from gi.repository import Gdk

def position(startpos, endpos, dualMonitor):
    window, screen = active_window()
    if window is None:
        return
    window.unmaximize()
    window.set_shadow_width(0, 0, 0, 0)
    workarea = screen.get_monitor_workarea(screen.get_monitor_at_window(window))
    display = Gdk.Display.get_default()

    offx, offy = offsets(window)
    w, h = (workarea.width / 4, workarea.height / 3)

    pos = (
        min(startpos[0], endpos[0]),
        min(startpos[1], endpos[1])
    )
    dims = (
        max(abs(endpos[0] - startpos[0]) + 1, 1),
        max(abs(endpos[1] - startpos[1]) + 1, 1)
    )


    if dualMonitor:
        multiscreen_offset = 0
    else:
        multiscreen_offset = get_multi_screen_offset(screen, window)

    if dualMonitor:
        screen_y_offset = [
            monitor_y_offset(display, min(startpos, endpos, key=lambda x: x[0]*10 + x[1])[1]),
            monitor_y_offset(display, max(startpos, endpos, key=lambda x: x[0]*10 + x[1])[1]),
        ]
    else:
        screen_y_offset = [0, 0]

    window.move_resize(
        pos[1] * w + multiscreen_offset,
        pos[0] * h + screen_y_offset[0],
        w * dims[1] - (offx * 2),
        h * dims[0]- (offx + offy) + screen_y_offset[1] - screen_y_offset[0]
    )

def active_window():
    screen = Gdk.Screen.get_default()
    window = screen.get_active_window()

    if no_window(screen, window):
        return None, None

    return (window, screen)

def get_multi_screen_offset(screen,window):
    monitor = screen.get_monitor_at_window(window)
    monitor_geometry = screen.get_monitor_geometry(monitor)
    return monitor_geometry.x

def offsets(window):
    origin = window.get_origin()
    root = window.get_root_origin()
    return (origin.x - root.x, origin.y - root.y)


def no_window(screen, window):
    return (
        not screen.supports_net_wm_hint(
            Gdk.atom_intern('_NET_ACTIVE_WINDOW', True)
        ) or
        not screen.supports_net_wm_hint(
            Gdk.atom_intern('_NET_WM_WINDOW_TYPE', True)
        ) or
        window.get_type_hint().value_name == 'GDK_WINDOW_TYPE_HINT_DESKTOP'
    )


def monitor_y_offset(display, x):
    left_monitor = display.get_monitor_at_point(0, 0)
    right_monitor = display.get_monitor(1) \
                    if left_monitor == display.get_monitor(0) \
                       else display.get_monitor(0)
    return [left_monitor, right_monitor][x // 4].get_workarea().y
