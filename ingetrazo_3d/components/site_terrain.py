"""
Layer 1: Mount Angel Abbey Bluff Terrain, Entry Forecourt & Retaining Walls (`1_Abbey_Hillside_Site`).

Models the dramatic topography of the Abbey hilltop:
  - Level upper approach plaza along the South Entrance (+0.52 m / +1'-8")
  - Steep natural downhill drop toward the North orchard (-9.2 m to -11.8 m),
    revealing all three stories of Aalto's faceted buff-brick fan on the North
    while presenting a serene one-story brick-and-copper pavilion on the South.
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import AaltoGeometry, get_level2_envelope_ft, get_level3_envelope_ft

from .primitives import (
    MATERIALS,
    add_box_m,
    add_extruded_polygon_ft,
    add_quad,
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
    xy_m,
)


def _point_in_poly_2d(pt: tuple[float, float], poly: list[tuple[float, float]]) -> bool:
    x, y = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def natural_hillside_z_m(x_ft: float, y_ft: float) -> float:
    """Smooth Mount Angel Abbey bluff elevation (metres) outside the building excavation."""
    # South hilltop plateau (Y <= -42 ft): gently crowned around +0.52 m
    if y_ft <= -42.0:
        gentle = 0.52 - 0.002 * max(0.0, -42.0 - y_ft) - 0.0008 * max(0.0, abs(x_ft) - 70.0)
        return gentle
    # Hillside slope from Y = -42 ft (+0.52 m) down to Y = +86 ft (-9.35 m), continuing to -11.6 m at Y = +135 ft
    if y_ft <= 86.0:
        t = (y_ft - (-42.0)) / (86.0 - (-42.0))
        # Smooth S-curve drop matching Section A-A grade line
        s = t * t * (3.0 - 2.0 * t)
        z = 0.52 * (1.0 - s) + (-9.35) * s
    else:
        t2 = (y_ft - 86.0) / 54.0
        z = -9.35 - 2.35 * t2
    # Subtle natural East-West crown of the abbey promontory
    z -= 0.000045 * (x_ft * x_ft)
    return z


def build_site_terrain(scene):
    grp = create_scene_group(scene, "1_Abbey_Hillside_Site")
    mesh = grp.mesh
    G = AaltoGeometry

    l2_env = get_level2_envelope_ft()
    l3_env = get_level3_envelope_ft()
    excav_z = m_ft(G.Z_L1_FT) - 0.45  # -8.53 m sub-slab footing datum inside building footprint

    xs = [ -175.0 + i * 10.0 for i in range(32) ]   # -175 .. +135 ft
    ys = [ -105.0 + j * 8.0 for j in range(32) ]    # -105 .. +143 ft

    grid_z: list[list[float]] = []
    for x in xs:
        col = []
        for y in ys:
            hz = natural_hillside_z_m(x, y)
            if _point_in_poly_2d((x, y), l2_env):
                hz = min(hz, excav_z)
            elif _point_in_poly_2d((x, y), l3_env):
                # Under South Wing crawl space: keep below South Wing slab (+0.61 m)
                hz = min(hz, m_ft(G.Z_LOBBY_FT) - 0.45)
            col.append(hz)
        grid_z.append(col)

    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            x0, x1 = xs[i], xs[i + 1]
            y0, y1 = ys[j], ys[j + 1]
            p00 = (*xy_m((x0, y0)), grid_z[i][j])
            p10 = (*xy_m((x1, y0)), grid_z[i + 1][j])
            p11 = (*xy_m((x1, y1)), grid_z[i + 1][j + 1])
            p01 = (*xy_m((x0, y1)), grid_z[i][j + 1])

            cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
            if _point_in_poly_2d((cx, cy), l2_env):
                mat = MATERIALS["concrete_dark"]
            else:
                mat = MATERIALS["hill_grass"]
            add_quad(mesh, p00, p10, p11, p01, mat)

    # Thickened earthen plinth skirt around outer terrain perimeter so model reads as an architectural site maquette
    base_z = -12.6
    # South edge (j = 0)
    for i in range(len(xs) - 1):
        x0, y0 = xy_m((xs[i], ys[0]))
        x1, y1 = xy_m((xs[i + 1], ys[0]))
        add_quad(mesh, (x0, y0, base_z), (x1, y1, base_z), (x1, y1, grid_z[i + 1][0]), (x0, y0, grid_z[i][0]), MATERIALS["hill_earth"])
    # North edge (j = last)
    jn = len(ys) - 1
    for i in range(len(xs) - 1):
        x0, y0 = xy_m((xs[i], ys[jn]))
        x1, y1 = xy_m((xs[i + 1], ys[jn]))
        add_quad(mesh, (x1, y1, base_z), (x0, y0, base_z), (x0, y0, grid_z[i][jn]), (x1, y1, grid_z[i + 1][jn]), MATERIALS["hill_earth"])
    # East edge (i = last)
    ie = len(xs) - 1
    for j in range(len(ys) - 1):
        x0, y0 = xy_m((xs[ie], ys[j]))
        x1, y1 = xy_m((xs[ie], ys[j + 1]))
        add_quad(mesh, (x0, y0, base_z), (x1, y1, base_z), (x1, y1, grid_z[ie][j + 1]), (x0, y0, grid_z[ie][j]), MATERIALS["hill_earth"])
    # West edge (i = 0)
    for j in range(len(ys) - 1):
        x0, y0 = xy_m((xs[0], ys[j]))
        x1, y1 = xy_m((xs[0], ys[j + 1]))
        add_quad(mesh, (x1, y1, base_z), (x0, y0, base_z), (x0, y0, grid_z[0][j]), (x1, y1, grid_z[0][j + 1]), MATERIALS["hill_earth"])

    # Exposed-aggregate South Entrance Plaza & Abbey Approach Walk
    plaza_poly = [
        (-96.0, -50.8),
        (20.0, -50.8),
        (20.0, -82.0),
        (-96.0, -82.0),
    ]
    add_extruded_polygon_ft(mesh, plaza_poly, 0.35, 0.56, MATERIALS["plaza_paving"], MATERIALS["concrete"])

    # Broad Abbey South Promenade Walk extending to edge of site
    walk_poly = [
        (-26.0, -82.0),
        (8.0, -82.0),
        (8.0, -104.5),
        (-26.0, -104.5),
    ]
    add_extruded_polygon_ft(mesh, walk_poly, 0.25, 0.54, MATERIALS["plaza_paving"], MATERIALS["concrete"])

    # Low Buff-Brick Entry Forecourt Bench Wall along South Plaza
    add_wall_strip_ft(mesh, [(-92.0, -68.0), (-30.0, -68.0)], 1.4, 0.56, 1.15, MATERIALS["buff_brick"])

    # Subtle low concrete site curbs flanking the West & East upper plaza transitions
    add_wall_strip_ft(mesh, [(-126.5, -28.0), (-134.0, -28.0), (-134.0, 1.5), (-126.5, 1.5)], 1.1, -1.2, 0.58, MATERIALS["concrete"])
    add_wall_strip_ft(mesh, [(61.5, -59.5), (68.0, -59.5), (68.0, -8.8), (61.5, -8.8)], 1.1, -1.2, 0.58, MATERIALS["concrete"])

    # North Perimeter Concrete Maintenance Apron at Level 1 Toe
    apron_pts = [
        (-89.0, 16.0), (-63.8, 59.0), (-14.2, 88.2), (42.0, 85.2), (98.5, 68.5),
        (96.0, 66.5), (40.8, 82.5), (-13.8, 85.4), (-61.8, 56.8), (-86.5, 14.8),
    ]
    add_extruded_polygon_ft(mesh, apron_pts, -9.60, -8.25, MATERIALS["plaza_paving"], MATERIALS["concrete"])

    return grp
