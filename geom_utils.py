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
