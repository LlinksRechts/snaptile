from gi.repository import Gdk
from window import get_target_monitor

def move_pointer_to(x, y):
    display = Gdk.Display.get_default()
    screen = Gdk.Screen.get_default()
    pointer = display.get_default_seat().get_pointer()
    pointer.warp(screen, x, y)
    # -> flush
    pointer.get_position()

def pointer_position(pos, dualMonitor):
    screen = Gdk.Screen.get_default()
    display = Gdk.Display.get_default()

    if dualMonitor:
        monitor = get_target_monitor(display, pos[1])
        workarea = monitor.get_workarea()

    w, h = (workarea.width / 4, workarea.height / 3)

    center = (
        (pos[1] % 4 + 0.5) * w + workarea.x,
        (pos[0] + 0.5) * h + workarea.y,
    )
    move_pointer_to(*center)
