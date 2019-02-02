#!/usr/bin/env python3

# by TheTechromancer

import os
import sys
import random
import argparse
from jpeg import *
from time import sleep
import subprocess as sp
from pathlib import Path



class GlitchWallpaper:

    def __init__(self, directory, cache_dir=None, frames=3, delay=.65, shuffle=True):

        if cache_dir is None:
            self.cache_dir = Path.home() / '.cache/glitch-wallpaper'
        else:
            self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.shuffle = shuffle
        self.position = 0
        self.delay = delay

        self.wallpapers = []

        self.directory = Path(directory)
        assert directory.is_dir(), 'Problem accessing wallpaper directory: {}'.format(str(directory))

        self.gen_cache()
        if self.shuffle:
            random.shuffle(self.wallpapers)


    def transition(self):

        gsettings_command = ['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri']

        old_position = (self.position % len(self.wallpapers))

        # glitch current wallpaper
        cur_wallpaper, cur_glitch_frames = self.wallpapers[old_position]
        random.shuffle(cur_glitch_frames)
        for frame in cur_glitch_frames:
            sp.run(gsettings_command + ['file://{}'.format(frame)])
            sleep(self.delay)


        new_position = ((old_position+1) % len(self.wallpapers))

        # glitch new wallpaper
        new_wallpaper, new_glitch_frames = self.wallpapers[new_position]
        random.shuffle(new_glitch_frames)
        for frame in new_glitch_frames:
            sp.run(gsettings_command + ['file://{}'.format(frame)])
            sleep(self.delay)

        # set new wallpaper
        sp.run(gsettings_command + ['file://{}'.format(new_wallpaper)])

        # increment counter
        self.position += 1


    def gen_cache(self):

        for image in self.find_images():

            glitched_frames = []
            image_bytes = bytearray(image.read_bytes())
            jpeg = Jpeg(image_bytes)

            for i in range(options.frames):

                frame_filename = self.cache_dir / '{}___{}.png'.format(image.name, i)

                # checked for cached files
                if self.is_cached(frame_filename):
                    sys.stderr.write('\r[+] Found cached frame #{} for {}     '.format(i+1, image.name))

                else:
                    while 1:
                        try:
                            jpeg.amount      = random.randint(0,99)
                            jpeg.seed        = random.randint(0,99)
                            jpeg.iterations  = random.randint(0,115)

                            sys.stderr.write('\r[+] Generating frame #{} for {}     '.format(i+1, image.name))

                            # create a new image if not cached
                            jpeg.save_image(frame_filename)
                            break

                        except JpegError as e:
                            sys.stderr.write('[!] {}'.format(str(e)))
                            continue

                glitched_frames.append(frame_filename)


            self.wallpapers.append((image, glitched_frames))
            sys.stderr.write('\r[+] Generated frames for {}     \n'.format(image.name))

        sys.stderr.write('\r[+] All frames generated.              ')


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
                    except sp.CalledProcessError:
                        sys.stderr.write('[!] Unsupported file: {}\n'.format(filename.name))
                        sys.stderr.write('[!]  - please install imagemagick in order to use {} files\n'.format(filename.suffix))
                        sys.stderr.write('[!]  - e.g. "apt install imagemagick"')



    def is_cached(self, filename):

        if (self.cache_dir / filename).is_file():
            return True
        return False




def main(options):

    g = GlitchWallpaper(options.directory, cache_dir=options.cache_dir, frames=options.frames, shuffle=(not options.dont_shuffle))
    sp.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-options', options.placement])

    while 1:
        g.transition()
        sleep(options.transition_time)



if __name__ == '__main__':

    valid_placements = ['centered', 'none', 'scaled', 'spanned', 'stretched', 'wallpaper', 'zoom']

    parser = argparse.ArgumentParser()

    parser.add_argument('directory',                type=Path,                      help='folder containing wallpapers')
    parser.add_argument('-d', '--dont-shuffle',     action='store_true',            help='disable shuffling of images')
    parser.add_argument('-t', '--transition-time',  type=int,   default=60,         help='time in seconds between transitions')
    parser.add_argument('-f', '--frames',           type=int,   default=3,          help='number of frames per transition')
    parser.add_argument('-p', '--placement',                    default='scaled',   help=', '.join(valid_placements))
    parser.add_argument('-c', '--cache-dir',                                        help='directory to hold glitch resources')

    try:

        options = parser.parse_args()

        options.placement = options.placement.lower()
        assert options.placement in valid_placements, 'Invalid placement'

        main(options)


    except AssertionError as e:
        sys.stderr.write('[!] {}'.format(str(e)))

    except KeyboardInterrupt:
        sys.stderr.write('[!] Interrupted')

    except argparse.ArgumentError as e:
        sys.stderr.write('\n\n[!] {}\n[!] Check your syntax'.format(str(e)))
        exit(2)