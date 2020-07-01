from gi.repository import Gdk
from itertools import product

def position(startpos, endpos, dualMonitor):
    window, screen = active_window()
    if window is None:
        return
    window.unmaximize()
    window.set_shadow_width(0, 0, 0, 0)

    display = Gdk.Display.get_default()
    if dualMonitor:
        monitor = get_target_monitor(display, startpos[1])
        workarea = monitor.get_workarea()
        end_monitor = get_target_monitor(display, endpos[1])
        end_workarea = end_monitor.get_workarea()
    else:
        monitor = screen.get_monitor_at_window(window)
        workarea = screen.get_monitor_workarea(monitor)
        # same screen -> same workarea on both corners
        end_workarea = workarea

    w, h = (workarea.width / 4, workarea.height / 3)
    end_w, end_h = (end_workarea.width / 4, end_workarea.height / 3)

    # each contain top left and bottom right position of the respective cell
    first_corner = (
        (startpos[1] % 4) * w + workarea.x,
        startpos[0] * h + workarea.y,
        (startpos[1] % 4 + 1) * w + workarea.x,
        (startpos[0] + 1) * h + workarea.y,
    )
    second_corner = (
        (endpos[1] % 4) * end_w + end_workarea.x,
        endpos[0] * end_h + end_workarea.y,
        (endpos[1] % 4 + 1) * end_w + end_workarea.x,
        (endpos[0] + 1) * end_h + end_workarea.y,
    )

    top_left, bottom_right = (
        # use top left corner of cells (0 & 1)
        (min(first_corner[0], second_corner[0]), min(first_corner[1], second_corner[1])),
        # use bottom right corner of cells (2 & 3)
        (max(first_corner[2], second_corner[2]), max(first_corner[3], second_corner[3])),
    )

    dims = (
        bottom_right[0] - top_left[0],
        bottom_right[1] - top_left[1],
    )

    window.move_resize(
        *top_left,
        *dims,
    )


def fill(pos, dualMonitor):
    screen = Gdk.Screen.get_default()
    display = Gdk.Display.get_default()
    window = screen.get_active_window()
    if dualMonitor:
        monitor = get_target_monitor(display, pos[1])
    else:
        monitor = display.get_monitor_at_window(window)
    other_wins = [
        win for win in screen.get_window_stack()
        if win.get_desktop() == window.get_desktop()
        and win != window
    ]
    win_geometries = [win.get_frame_extents() for win in other_wins]
    initial = grid_to_xywh(pos, monitor)
    # filter out windows which overlap no matter what
    win_geometries = [win for win in win_geometries if not overlaps(initial, geom_to_tuple(win))]
    max_tiles = 0
    best_pos = ()
    # try all possibilities and choose the one with the most tiles
    # at least one is valid (the single tile), since we filter out windows
    # which conflict this tile above
    for ylow, yhigh, xlow, xhigh in product(
            range(0, pos[0] + 1),
            range(pos[0], 3),
            range(0, (pos[1] % 4) + 1),
            range((pos[1] % 4), 4),
    ):
        tiles = (xhigh-xlow+1) * (yhigh-ylow+1)
        if tiles < max_tiles:
            continue
        top_left = (ylow, xlow)
        bot_right = (yhigh, xhigh)
        abs_top_left = grid_to_coords(top_left, monitor)[:2]
        abs_bot_right = grid_to_coords(bot_right, monitor)[2:]
        abs_pos = (
            *abs_top_left,
            abs_bot_right[0] - abs_top_left[0],
            abs_bot_right[1] - abs_top_left[1],
        )
        if not any(overlaps(abs_pos, geom_to_tuple(geom)) for geom in win_geometries):
            max_tiles = tiles
            best_pos = abs_pos

    window.unmaximize()
    window.set_shadow_width(0, 0, 0, 0)
    window.move_resize(*best_pos)


def grid_to_coords(pos, monitor):
    geom = monitor.get_geometry()
    x = geom.x + (pos[1] % 4) * geom.width // 4
    y = geom.y + (pos[0] % 3) * geom.height // 3
    return (x, y, x + geom.width // 4, y + geom.height // 3)


def grid_to_xywh(pos, monitor):
    coords = grid_to_coords(pos, monitor)
    return (
        coords[0],
        coords[1],
        coords[2] - coords[0],
        coords[3] - coords[1],
    )


def geom_to_tuple(geom):
    return (geom.x, geom.y, geom.width, geom.height)


def overlaps(geom1, geom2):
    return not (
        geom1[0] >= geom2[0] + geom2[2] or
        geom1[0] + geom1[2] <= geom2[0] or
        geom1[1] >= geom2[1] + geom2[3] or
        geom1[1] + geom1[3] <= geom2[1]
    )


def active_window():
    screen = Gdk.Screen.get_default()
    window = screen.get_active_window()

    if no_window(screen, window):
        return None, None

    return (window, screen)


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


def get_target_monitor(display, x):
    # NOTE: only works for up to 2 monitors!!
    left_monitor = display.get_monitor_at_point(0, 0)
    right_monitor = display.get_monitor(1) \
                    if left_monitor == display.get_monitor(0) \
                       else display.get_monitor(0)
    return [left_monitor, right_monitor][x // 4]
