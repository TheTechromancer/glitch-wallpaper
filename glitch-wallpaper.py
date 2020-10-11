#!/usr/bin/env python3

# by TheTechromancer

import os
import sys
import random
import hashlib
import argparse
import datetime
from jpeg import *
from time import sleep
import subprocess as sp
from pathlib import Path



class GlitchWallpaper:

    def __init__(self, directory, cache_dir=None, frames=3, delay=(0, .5), shuffle=True):

        if cache_dir is None:
            self.cache_dir = Path.home() / '.cache/glitch-wallpaper'
        else:
            self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.shuffle = shuffle
        self.position = 0
        self.delay = delay
        self.frames = frames

        self.wallpapers = []

        self.directory = Path(directory)
        assert directory.is_dir(), f'Problem accessing wallpaper directory: {directory}'

        self._gen_cache()
        if self.shuffle:
            random.shuffle(self.wallpapers)


    def transition(self):

        nitrogen_success = False

        # nitrogen
        try:
            for screen_num in range(10):
                for frame in self._make_transition_frames(offset=screen_num):
                    nitrogen_command = ['nitrogen', f'--head={screen_num}', '--set-zoom', str(frame)]

                    start_time = datetime.datetime.now()
                    nitrogen_process = sp.run(nitrogen_command, stderr=sp.PIPE, check=True)
                    end_time = datetime.datetime.now()
                    time_diff = end_time - start_time

                    if not 'Could not find' in nitrogen_process.stderr.decode():
                        self._sleep(time_diff)

                nitrogen_success = True

        except (sp.CalledProcessError, FileNotFoundError) as e:
            sys.stderr.write(f'[!] Error with nitrogen: {e}\n')

            if not nitrogen_success:
                sys.stderr.write(f'[!] Falling back to feh: {e}\n')

                for frame in self._make_transition_frames():

                    # feh
                    try:
                        feh_command = ['feh', '--bg-max', frame]
                        start_time = datetime.datetime.now()
                        sp.run(feh_command, check=True)
                        end_time = datetime.datetime.now()
                        time_diff = end_time - start_time
                        self._sleep(time_diff)

                    except sp.CalledProcessError as e:
                        sys.stderr.write(f'[!] Error with feh: {e}\n')
                        continue

                    except FileNotFoundError as e:
                        sys.stderr.write(f'[!] Error with feh: {e}\n')
                        sys.stderr.write(f'[!] Falling back to gsettings: {e}\n')

                        # gsettings
                        try:
                            gsettings_command = ['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri']
                            sp.run(gsettings_command + [f'file://{frame}'], check=True)
                            sleep(max(sleep_time, .4))
                        except (sp.CalledProcessError, FileNotFoundError) as e:
                            sys.stderr.write(f'[!] Error with gsettings: {e}')

        # increment counter
        self.position += 1



    def _make_transition_frames(self, offset=0):

        old_position = ((self.position + offset) % len(self.wallpapers))

        # glitch current wallpaper
        cur_wallpaper, cur_glitch_frames = self.wallpapers[old_position]
        random.shuffle(cur_glitch_frames)
        for frame in cur_glitch_frames[:-1]:
            yield frame

        new_position = ((old_position+1) % len(self.wallpapers))

        # shuffle the whole deck if we're back to zero
        if new_position == 0 and self.shuffle:
            random.shuffle(self.wallpapers)

        # glitch new wallpaper
        new_wallpaper, new_glitch_frames = self.wallpapers[new_position]
        random.shuffle(new_glitch_frames)
        yield new_glitch_frames[0]
        yield cur_glitch_frames[-1]
        for frame in new_glitch_frames[1:]:
            yield frame

        yield new_wallpaper


    def _sleep(self, d):
        '''
        takes time delta to subtract
        sleeps based on min, max value of self.delay
        '''
        floor,ceiling = self.delay
        floor = int(floor *1000)
        ceiling = int(ceiling * 1000)
        delay = random.randint(floor,ceiling)
        delay = random.randint(floor, delay)

        sleep_time = datetime.timedelta(seconds=delay/1000)
        sleep_time = sleep_time - d
        if not sleep_time.days < 0:
            sleep(sleep_time.seconds + (sleep_time.microseconds / 1000000))


    def _gen_cache(self):

        for image in self.find_images():

            glitched_frames = []
            image_bytes = bytearray(image.read_bytes())
            image_hash = hashlib.md5(image_bytes).hexdigest()
            jpeg = Jpeg(image_bytes)

            for i in range(self.frames):

                frame_filename = self.cache_dir / f'{image_hash}___{i}.png'

                # checked for cached files
                if self.is_cached(frame_filename):
                    sys.stderr.write(f'[+] Found cached frame #{i+1} for {image.name}')

                else:
                    while 1:
                        try:
                            jpeg.amount      = random.randint(0,99)
                            jpeg.seed        = random.randint(0,99)
                            jpeg.iterations  = random.randint(0,115)

                            sys.stderr.write(f'[+] Generating frame #{i+1} for {image.name}')

                            # create a new image if not cached
                            jpeg.save_image(frame_filename)
                            break

                        except JpegError as e:
                            sys.stderr.write(f'[!] {e}')
                            continue

                glitched_frames.append(frame_filename)


            self.wallpapers.append((image, glitched_frames))
            sys.stderr.write(f'[+] Generated frames for {image.name}')

        sys.stderr.write('[+] All frames generated.')


    def find_images(self):

        valid_suffixes = ['.jpg', '.jpeg']
        convert_suffixes = ['.png']

        for root,dirs,files in os.walk(self.directory):
            for file in files:
                filename = Path(root) / file

                # if image is a JPEG
                if any([filename.suffix.lower().endswith(s) for s in valid_suffixes]):
                    yield filename

                # if image is an unsupported image type
                elif any([filename.suffix.lower().endswith(s) for s in convert_suffixes]):
                    # try to convert it with imagemagick
                    try:
                        new_filename = self.cache_dir / (filename.stem + '.jpg')
                        sp.run(['convert', str(filename), str(new_filename)], check=True)
                        yield new_filename
                    except (FileNotFoundError, sp.CalledProcessError) as e:
                        sys.stderr.write(f'[!] Unsupported file: {filename.name}\n')
                        sys.stderr.write(f'[!]  - please install imagemagick in order to use {filename.suffix} files\n')
                        sys.stderr.write('[!]  - e.g. "apt install imagemagick"\n')



    def is_cached(self, filename):

        if (self.cache_dir / filename).is_file():
            return True
        return False




def install(options):

    script_name = Path(__file__).resolve()
    script_dir_name = script_name.parent

    options_str = []
    if options.dont_shuffle:
        options_str.append('--dont-shuffle')
    if options.cache_dir is not None:
        options_str.append(f'--cache-dir {options.cache_dir}')
    options_str.append(f'--transition-time {options.transition_time}')
    options_str.append(f'--frames {options.frames}')
    options_str.append(str(options.directory))

    try:
        display_var = str(os.environ['DISPLAY'])
    except KeyError:
        display_var = ':0'

    service_content = f'''
[Unit]
Description=Glitch Wallpaper

[Service]
Type=exec
WorkingDirectory={script_dir_name}
ExecStart=/usr/bin/env python3 {script_name} {" ".join(options_str)}
User={os.getlogin()}
Environment=DISPLAY={display_env}

[Install]
WantedBy=multi-user.target
'''

    with open('/tmp/glitch-wallpaper.service', 'w') as f:
        f.write(service_content)

    print('[+] Installing service')
    print('[+] Please provide password if prompted')
    sp.run(['sudo', 'mv', '/tmp/glitch-wallpaper.service', '/etc/systemd/system/'])

    print('[+] Starting service')
    sp.run(['sudo', 'systemctl', 'enable', 'glitch-wallpaper.service'])
    sp.run(['sudo', 'systemctl', 'start', 'glitch-wallpaper.service'])

    print('[+] Done')
    print('[+] Type the following command to check status of service:')
    print('     - systemctl status glitch-wallpaper.service')





def main(options):

    options.directory = options.directory.resolve()

    g = GlitchWallpaper(options.directory, cache_dir=options.cache_dir, frames=options.frames, shuffle=(not options.dont_shuffle))
    sp.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-options', 'scaled'])

    while 1:
        g.transition()
        sleep(options.transition_time)



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('directory',                type=Path,                      help='folder containing wallpapers')
    parser.add_argument('-d', '--dont-shuffle',     action='store_true',            help='disable shuffling of images')
    parser.add_argument('-t', '--transition-time',  type=int,   default=60,         help='time in seconds between transitions')
    parser.add_argument('-f', '--frames',           type=int,   default=3,          help='number of frames per transition')
    parser.add_argument('-c', '--cache-dir',                                        help='directory to hold glitch resources')
    parser.add_argument('-i', '--install',          action='store_true',            help='install and start systemd service with current options')

    try:

        options = parser.parse_args()

        if options.install:
            install(options)
        else:
            main(options)


    except AssertionError as e:
        sys.stderr.write(f'\n[!] {e}\n')

    except KeyboardInterrupt:
        sys.stderr.write('\n\n[!] Interrupted\n')

    except argparse.ArgumentError as e:
        sys.stderr.write(f'\n\n[!] {e}\n[!] Check your syntax')
        exit(2)