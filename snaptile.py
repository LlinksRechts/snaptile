#!/usr/bin/env python3

from __future__ import print_function

import sys, getopt

import signal
from Xlib import display, X

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from window import position, fill
from keyutil import get_posmap, initkeys
from pointer import pointer_position

import time

keymaps = {
    "qwerty":
    (['Q', 'W', 'E', 'R'],
     ['A', 'S', 'D', 'F'],
     ['Z', 'X', 'C', 'V']),
    "azerty":
    (['A', 'Z', 'E', 'R'],
     ['Q', 'S', 'D', 'F'],
     ['W', 'X', 'C', 'V']),
    "qwertz":
    (['Q', 'W', 'E', 'R'],
     ['A', 'S', 'D', 'F'],
     ['Y', 'X', 'C', 'V']),
    "colemak":
    (['Q', 'W', 'F', 'P'],
     ['A', 'R', 'S', 'T'],
     ['Z', 'X', 'C', 'V']),
    "dvorak":
    (['apostrophe', 'comma', 'period', 'P'],
     ['A', 'O', 'E', 'U'],
     ['semicolon', 'Q', 'J', 'K']),
}

dualMonitorKeymaps = {
    "qwerty":
    (['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I'],
     ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K'],
     ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'comma']),
    "azerty":
    (['A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I'],
     ['Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K'],
     ['W', 'X', 'C', 'V', 'B', 'N', 'comma', 'semicolon']),
    "qwertz":
    (['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I'],
     ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K'],
     ['Y', 'X', 'C', 'V', 'B', 'N', 'M', 'comma']),
    "colemak":
    (['Q', 'W', 'F', 'P', 'G', 'J', 'L', 'U'],
     ['A', 'R', 'S', 'T', 'D', 'H', 'N', 'E'],
     ['Z', 'X', 'C', 'V', 'B', 'K', 'M', 'comma']),
    "dvorak":
    (['apostrophe', 'comma', 'period', 'P', 'Y', 'F', 'G', 'C'],
     ['A', 'O', 'E', 'U', 'I', 'D', 'H', 'T'],
     ['semicolon', 'Q', 'J', 'K', 'X', 'B', 'M', 'W']),
}

# delay for double presses
fill_delay = 0.5



def autodetectKeyboard():
    try:
        import sdl2
        import sdl2.keyboard
        from sdl2 import keycode
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        keys = bytes(sdl2.keyboard.SDL_GetKeyFromScancode(sc) for sc in (keycode.SDL_SCANCODE_Q, keycode.SDL_SCANCODE_W, keycode.SDL_SCANCODE_Y))
        keyMap = {
            b'qwy': 'qwerty',
            b'azy': 'azerty',
            b'qwz': 'qwertz',
            b'qwj': 'colemak',
            b'\',f': 'dvorak',
        }
        if keys in keyMap:
            return keyMap.get(keys, 'unknown')
    except:
        print("Could not detect keyboard (is PySDL2 installed?). Falling back to qwerty.")
        return "qwerty"


def global_inital_states():
    displ = display.Display()
    rt = displ.screen().root
    rt.change_attributes(event_mask=X.KeyPressMask)

    return (
        displ,
        rt,
        {
            'code': 0,
            'pressed': False,
            'window': None,
        },
        get_posmap(keymap, displ)
    )

global disp, root, lastkey_state, posmap, isDualMonitor, fillEnabled, mouseEnabled;


def run():
    mask = None

    opts, args = getopt.getopt(sys.argv[1:], "hdWk:fm")
    keyboardLayout = autodetectKeyboard()

    global isDualMonitor, fillEnabled, mouseEnabled

    isDualMonitor = False

    fillEnabled = False
    mouseEnabled = False

    for opt in opts:
        if opt[0] == '-h':
            print ('Snaptile.py')
            print ('-d expanded dual-monitor keybinds')
            print ('-W use Windows key')
            print ('-h this help text')
            print ('-k <keymap> to specify a keyboard layout (eg. qwerty)')
            print ('-f enable filling available space on double press')
            print ('-m enable mouse move support')
            sys.exit()
        elif opt[0] == '-d':
            isDualMonitor = True
        elif opt[0] == '-W':
            mask = 'Windows'
        elif opt[0] == '-k':
            keyboardLayout = opt[1]
        elif opt[0] == '-f':
            fillEnabled = True
        elif opt[0] == '-m':
            mouseEnabled = True

    global keymap;
    keymapSource = keymaps
    if isDualMonitor:
        keymapSource = dualMonitorKeymaps
    if keyboardLayout in keymapSource:
        keymap = keymapSource[keyboardLayout]
    else:
        print("Unsupported keyboard layout. Falling back to qwerty.")
        keymap = keymapSource["qwerty"]

    global disp, root, lastkey_state, posmap
    disp, root, lastkey_state, posmap = global_inital_states()

    initkeys(keymap, disp, root, mask)
    if mouseEnabled:
        initkeys(keymap, disp, root, 'mouse')
    for _ in range(0, root.display.pending_events()):
        root.display.next_event()
    GLib.io_add_watch(root.display, GLib.IO_IN, checkevt)
    print('Snaptile running. Press CTRL+C to quit.')
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    Gtk.main()

# counter for how many keys are currently pressed to fix xlib 'bug'
keys_pressed = 0

def checkevt(_, __, handle=None):
    global lastkey_state, keys_pressed

    handle = handle or root.display
    for _ in range(0, handle.pending_events()):
        event = handle.next_event()

        if event.type == X.KeyPress:
            if mouseEnabled and event.state & X.Mod4Mask and event.state & X.ControlMask:
                handle_pointer_event(event.detail)
                continue
            keys_pressed += 1
            if event.detail not in posmap:
                break

            # prevent loosing double press release events
            root.grab_keyboard(1, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)

            win = None
            if not lastkey_state['pressed']:
                if fillEnabled and \
                   lastkey_state['code'] == event.detail and \
                   time.time() - lastkey_state['time'] < fill_delay:
                    win = handle_fill(
                        event.detail,
                        lastkey_state['window'],
                    )
                else:
                    win = handleevt(event.detail, event.detail)

            else:
                win = handleevt(
                    lastkey_state['code'],
                    event.detail,
                    lastkey_state['window'],
                )

            lastkey_state = {
                'code': event.detail,
                'pressed': True,
                'time': time.time(),
                'window': win,
            }

        if event.type == X.KeyRelease:
            # prevent going under 0 since we get
            # one last release event from the modifier key
            keys_pressed = max(keys_pressed-1, 0)
            if keys_pressed == 0:
                # no more keys pressed, so ungrab keyboard
                disp.flush()
                disp.ungrab_keyboard(X.CurrentTime)
            else:
                # grab keyboard to avoid losing KeyRelease event
                root.grab_keyboard(1, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)

            if event.detail == lastkey_state['code']:
                lastkey_state['pressed'] = False

    return True

def handleevt(startkey, endkey, window=None):
    return position(
        posmap[startkey],
        posmap[endkey],
        isDualMonitor,
        window,
    )

def handle_fill(key, window=None):
    return fill(posmap[key], isDualMonitor, window)

def handle_pointer_event(key):
    return pointer_position(
        posmap[key],
        isDualMonitor,
    )

if __name__ == '__main__':
    run()
