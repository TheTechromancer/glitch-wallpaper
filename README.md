# Glitch Wallpaper
### Automatic glitch transition animations for Linux desktop backgrounds / wallpapers

![glitch_wallpaper](https://orig00.deviantart.net/ef8c/f/2019/034/d/c/glitch_gif_2_by_thetechromancer-dcytyaw.gif "Glitch Wallpaper Demo")
Artist Credit:
<br>
["Ghost in the shell - Kuze fanart" by YUANYUE CHANG](https://www.artstation.com/artwork/JYDyd)
["Walk in the Rain" by MuYoung Kim](https://www.artstation.com/artwork/w86knL)
<br>

### Features:
- Recursively searches directory for images
- JPEGs and PNGs are supported
- Customize duration, transition time, etc.

<br>

### Installation
- Clone repo
~~~
$ git clone https://github.com/thetechromancer/glitch-wallpaper
$ cd glitch-wallpaper
~~~
- Install dependencies (required)
~~~
$ python3 -m pip install --user Pillow
~~~
- Install feh or nitrogen (highly recommended)
~~~
$ sudo apt install nitrogen
$ sudo apt install feh
~~~
- Install imagemagick (required for PNG support)
~~~
$ sudo apt install imagemagick
~~~

<br>

### Usage
~~~
$ ./glitch-wallpaper.py --help
usage: glitch-wallpaper.py [-h] [-d] [-t TRANSITION_TIME] [-f FRAMES]
                           [-c CACHE_DIR]
                           directory

positional arguments:
  directory             folder containing wallpapers

optional arguments:
  -h, --help            show this help message and exit
  -d, --dont-shuffle    disable shuffling of images
  -t TRANSITION_TIME, --transition-time TRANSITION_TIME
                        time in seconds between transitions
  -f FRAMES, --frames FRAMES
                        number of frames per transition
  -c CACHE_DIR, --cache-dir CACHE_DIR
                        directory to hold glitch resources
~~~

<br>

### Example #1
Start from the command line.  Just give it a folder containing pictures.
~~~
$ ./glitch-wallpaper.py ~/Pictures
[+] Generated frames for muyoung-kim-walk-in-the-rain-lr-myk.jpg          
[+] Generated frames for yuanyue-chang-img-6883.jpg          
[+] Generated frames for yuanyue-chang-img-6725.jpg          
[+] All frames generated.
~~~

### Example #2
Run in the background as a Systemd service (will start automatically on boot).
~~~
$ ./glitch-wallpaper.py --install ~/Pictures
[+] Installing service
[+] Please provide password if prompted
[sudo] password for user: 
[+] Starting service
Created symlink /etc/systemd/system/multi-user.target.wants/glitch-wallpaper.service → /etc/systemd/system/glitch-wallpaper.service.
[+] Done
[+] Type the following command to check status of service:
     - systemctl status glitch-wallpaper.service
~~~
