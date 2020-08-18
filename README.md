# Snaptile

Versatile, mouse-free window tiling for X11.

![lol](https://user-images.githubusercontent.com/5866348/26905369-089db4d4-4bb5-11e7-90a8-96e39f278f1c.gif)

## Grid System

The grid system divides your screen into 12 sections

<kbd>ctl</kbd> + <kbd>alt</kbd> +


| <kbd>Q</kbd>| <kbd>W</kbd>| <kbd>E</kbd>| <kbd>R</kbd>|
|--|--|--|--|
| <kbd>A</kbd>| <kbd>S</kbd>| <kbd>D</kbd>| <kbd>F</kbd>|
| <kbd>Z</kbd>| <kbd>X</kbd>| <kbd>C</kbd>| <kbd>V</kbd>|

or, in dual screen mode (`-d` switch), into 12 sections each, with extended keybindings for the second screen:

| <kbd>T</kbd>| <kbd>Y</kbd>| <kbd>U</kbd>| <kbd>I</kbd>|
|--|--|--|--|
| <kbd>G</kbd>| <kbd>H</kbd>| <kbd>J</kbd>| <kbd>K</kbd>|
| <kbd>B</kbd>| <kbd>N</kbd>| <kbd>M</kbd>| <kbd>,</kbd>|

You can snap your window to any rectangle, of any arbitrary size, on this grid by specifying 2 corners. For example:

<kbd>ctl</kbd> + <kbd>alt</kbd> + <kbd>E</kbd> + <kbd>D</kbd>

| x | x | <kbd>E</kbd>| x |
|--|--|--|--|
| x | x | <kbd>D</kbd>| x |
| x | x |      x      | x |


Which looks like

![screenshot from 2017-06-07 18-50-28](https://user-images.githubusercontent.com/5866348/26905371-0b657a26-4bb5-11e7-9e0f-b3a56f5802a5.png)

The two keys only needs to "span" a rectangle. For example:

<kbd>ctl</kbd> + <kbd>alt</kbd> + <kbd>X</kbd> + <kbd>D</kbd>

| x | x |x | x |
|--|--|--|--|
| x | + | <kbd>D</kbd>| x |
| x | <kbd>X</kbd> |      +      | x |

which looks like

![screenshot from 2017-06-07 22-55-56](https://user-images.githubusercontent.com/5866348/26910417-b381baca-4bd4-11e7-9ff7-fff9262743e8.png)

### Fill
With the `-f` switch, filling is activated. On double press of any of the shortcuts, snaptile will try to find as many sections
around the specified one as possible without intersecting with other windows, and fill the largest match. This will still align to the 4x3 grid.
Windows which obstruct the initial section are excluded from intersection, so they might be partially or even completely occluded.

For example, if there is a window between tiles <kbd>Q</kbd> and <kbd>S</kbd>, double pressing <kbd>ctl</kbd> + <kbd>alt</kbd> + <kbd>X</kbd>
will have the same outcome as <kbd>Z</kbd> and <kbd>V</kbd>. Double <kbd>C</kbd>, on the other hand, will result in <kbd>E</kbd> and <kbd>V</kbd>.


## Requirements
* Python3
* X11-based desktop
* python3-gi
* python3-xlib
* PySQL2 (not required, for automatically detecting keyboard layout)

## Installation Guides

### Install on Ubuntu

Go to a directory you want to store snaptile:
```bash
cd <place-you-want-to-store-snaptile>
```

Install and run:
```bash
sudo apt-get install git python3-gi python3-xlib
git clone https://github.com/jakebian/snaptile.git
cd snaptile && ./snaptile.py
```

### Install on Arch / Manjaro

The snaptile-git arch linux packaged is created & maintained by [@madnight](https://github.com/madnight).

Install and run:
```bash
yaourt snaptile-git
snaptile
```

### Install on Fedora
Go to a directory you want to store snaptile:
```bash
cd <place-you-want-to-store-snaptile>
```

Install and run:
```bash
sudo dnf install git python3-gobject python3-xlib
git clone https://github.com/jakebian/snaptile.git
cd snaptile && ./snaptile.py
```

## Options
```bash
./snaptile.py -h
Snaptile.py
-d expanded dual-monitor keybinds
-W use Windows key
-h this help text
```
## Start at boot

To start at boot, just add a script to *Startup Applications* invoking the python script
```bash
/usr/bin/python3 <full-path>/snaptile/snaptile.py
```

## Credits
Snaptile is a rewrite of [PyGrid](https://github.com/pkkid/pygrid), supporting the more powerful shortcuts system.
