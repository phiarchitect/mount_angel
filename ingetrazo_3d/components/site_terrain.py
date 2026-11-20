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

from phiarchitect.mountangel.vectors import (
    AaltoGeometry,
    arc_pts,
    get_level2_envelope_ft,
    get_level3_envelope_ft,
    get_north_perimeter_with_pockets_ft,
)

from .primitives import (
    MATERIALS,
    add_box_m,
    add_extruded_polygon_ft,
    add_quad,
    add_tri,
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
    # Aligned to true Lobby threshold (+1'-4" = +0.406 m) and Level 1 toe (-28'-6" = -8.687 m)
    if -140.0 <= x_ft <= 115.0 and -70.0 <= y_ft <= 110.0:
        if y_ft <= -42.0:
            return 0.32 - 0.002 * max(0.0, -42.0 - y_ft) - 0.0008 * max(0.0, abs(x_ft) - 70.0)
        if y_ft <= 88.0:
            t = (y_ft - (-42.0)) / (88.0 - (-42.0))
            s = t * t * (3.0 - 2.0 * t)
            z = 0.32 * (1.0 - s) + (-9.85) * s
        else:
            t2 = (y_ft - 88.0) / 54.0
            z = -9.85 - 2.35 * t2
        z -= 0.000045 * (x_ft * x_ft)
        return z

    # Broad Abbey Campus promontory & north bluff continuation
    if x_ft < -140.0:
        y_crest = 0.0
    elif x_ft > 115.0:
        y_crest = -20.0
    else:
        y_crest = -42.0

    if y_ft <= y_crest:
        z = 0.30 - 0.0012 * max(0.0, y_crest - y_ft) - 0.0004 * max(0.0, abs(x_ft) - 90.0)
        return max(-0.45, z)
    else:
        dy = y_ft - y_crest
        if dy <= 130.0:
            t = dy / 130.0
            s = t * t * (3.0 - 2.0 * t)
            z = 0.30 * (1.0 - s) + (-9.85) * s
        else:
            t2 = (dy - 130.0) / 54.0
            z = -9.85 - 2.35 * t2
        return z


def _add_hipped_roof_ft(
    mesh,
    x0_ft: float,
    y0_ft: float,
    x1_ft: float,
    y1_ft: float,
    z_eaves_m: float,
    z_ridge_m: float,
    attrs: dict,
    hip_x_ft: float = 0.0,
    hip_y_ft: float = 0.0,
    axis: str = "X",
):
    """Add a closed 2-manifold hipped/gabled roof solid with outward normals (`unpaired == 0`)."""
    if x0_ft > x1_ft:
        x0_ft, x1_ft = x1_ft, x0_ft
    if y0_ft > y1_ft:
        y0_ft, y1_ft = y1_ft, y0_ft
    p0 = (*xy_m((x0_ft, y0_ft)), z_eaves_m)
    p1 = (*xy_m((x1_ft, y0_ft)), z_eaves_m)
    p2 = (*xy_m((x1_ft, y1_ft)), z_eaves_m)
    p3 = (*xy_m((x0_ft, y1_ft)), z_eaves_m)

    add_quad(mesh, p0, p3, p2, p1, attrs)  # bottom (-Z)
    if axis == "X":
        ymid = 0.5 * (y0_ft + y1_ft)
        r0 = (*xy_m((x0_ft + hip_x_ft, ymid)), z_ridge_m)
        r1 = (*xy_m((x1_ft - hip_x_ft, ymid)), z_ridge_m)
        add_quad(mesh, p0, p1, r1, r0, attrs)  # south slope
        add_quad(mesh, p2, p3, r0, r1, attrs)  # north slope
        add_tri(mesh, p3, p0, r0, attrs)       # west gable/hip
        add_tri(mesh, p1, p2, r1, attrs)       # east gable/hip
    else:
        xmid = 0.5 * (x0_ft + x1_ft)
        r0 = (*xy_m((xmid, y0_ft + hip_y_ft)), z_ridge_m)
        r1 = (*xy_m((xmid, y1_ft - hip_y_ft)), z_ridge_m)
        add_quad(mesh, p0, r0, r1, p3, attrs)  # west slope
        add_quad(mesh, p1, p2, r1, r0, attrs)  # east slope
        add_tri(mesh, p0, p1, r0, attrs)       # south gable/hip
        add_tri(mesh, p2, p3, r1, attrs)       # north gable/hip


def _add_pyramidal_roof_ft(
    mesh,
    x0_ft: float,
    y0_ft: float,
    x1_ft: float,
    y1_ft: float,
    z_eaves_m: float,
    z_apex_m: float,
    attrs: dict,
):
    """Add a closed 2-manifold 4-sided pyramidal spire / roof (`unpaired == 0`)."""
    if x0_ft > x1_ft:
        x0_ft, x1_ft = x1_ft, x0_ft
    if y0_ft > y1_ft:
        y0_ft, y1_ft = y1_ft, y0_ft
    p0 = (*xy_m((x0_ft, y0_ft)), z_eaves_m)
    p1 = (*xy_m((x1_ft, y0_ft)), z_eaves_m)
    p2 = (*xy_m((x1_ft, y1_ft)), z_eaves_m)
    p3 = (*xy_m((x0_ft, y1_ft)), z_eaves_m)
    apex = (*xy_m((0.5 * (x0_ft + x1_ft), 0.5 * (y0_ft + y1_ft))), z_apex_m)

    add_quad(mesh, p0, p3, p2, p1, attrs)  # bottom (-Z)
    add_tri(mesh, p0, p1, apex, attrs)     # south
    add_tri(mesh, p1, p2, apex, attrs)     # east
    add_tri(mesh, p2, p3, apex, attrs)     # north
    add_tri(mesh, p3, p0, apex, attrs)     # west


def _add_road_ribbon_ft(mesh, pts_ft: list[tuple[float, float]], width_ft: float, road_attrs: dict):
    """Extrude a curving roadway as closed 2-manifold slab segments following natural grade."""
    half_w = width_ft * 0.5
    for i in range(len(pts_ft) - 1):
        x0, y0 = pts_ft[i]
        x1, y1 = pts_ft[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 1e-4:
            continue
        nx, ny = -dy / L * half_w, dx / L * half_w

        p0 = (x0 + nx, y0 + ny)
        p1 = (x0 - nx, y0 - ny)
        p2 = (x1 - nx, y1 - ny)
        p3 = (x1 + nx, y1 + ny)

        z0_ground = natural_hillside_z_m(x0, y0)
        z1_ground = natural_hillside_z_m(x1, y1)

        z0_top = z0_ground + 0.08
        z1_top = z1_ground + 0.08
        z0_bot = z0_ground - 0.25
        z1_bot = z1_ground - 0.25

        t0 = (*xy_m(p0), z0_top)
        t1 = (*xy_m(p1), z0_top)
        t2 = (*xy_m(p2), z1_top)
        t3 = (*xy_m(p3), z1_top)

        b0 = (*xy_m(p0), z0_bot)
        b1 = (*xy_m(p1), z0_bot)
        b2 = (*xy_m(p2), z1_bot)
        b3 = (*xy_m(p3), z1_bot)

        add_quad(mesh, t0, t1, t2, t3, road_attrs)  # top (+Z)
        add_quad(mesh, b0, b3, b2, b1, road_attrs)  # bottom (-Z)
        add_quad(mesh, t0, t3, b3, b0, road_attrs)  # left (+N)
        add_quad(mesh, t1, b1, b2, t2, road_attrs)  # right (-N)
        add_quad(mesh, t0, b0, b1, t1, road_attrs)  # start cap
        add_quad(mesh, t3, t2, b2, b3, road_attrs)  # end cap


def build_site_terrain(scene):
    grp = create_scene_group(scene, "1_Abbey_Hillside_Site")
    mesh = grp.mesh
    G = AaltoGeometry

    l2_env = get_level2_envelope_ft()
    l3_env = get_level3_envelope_ft()
    excav_z = m_ft(G.Z_L1_FT) - 0.45  # -8.53 m sub-slab footing datum inside building footprint

    # Expanded Campus Maquette Grid: -340..+420 ft in X, -360..+210 ft in Y
    # Dense ~10 ft spacing across Library footprint [-140..115] x [-70..110]
    xs_west = [-340.0, -310.0, -280.0, -250.0, -220.0, -195.0, -170.0, -150.0]
    xs_lib = [-140.0, -130.0, -120.0, -110.0, -100.0, -90.0, -80.0, -70.0, -60.0, -50.0, -40.0, -30.0, -20.0, -10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 115.0]
    xs_east = [135.0, 160.0, 190.0, 220.0, 250.0, 280.0, 310.0, 340.0, 370.0, 395.0, 420.0]
    xs = xs_west + xs_lib + xs_east

    ys_south = [-360.0, -330.0, -300.0, -270.0, -240.0, -210.0, -180.0, -150.0, -125.0, -100.0, -85.0]
    ys_lib = [-70.0, -60.0, -50.0, -40.0, -30.0, -20.0, -10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0]
    ys_north = [125.0, 142.0, 160.0, 180.0, 195.0, 210.0]
    ys = ys_south + ys_lib + ys_north

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

    # Thickened earthen plinth skirt around outer terrain perimeter (closed 2-manifold maquette block)
    base_z = -20.0
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
    # Bottom cap (-Z normal) sealing terrain maquette block with exact shared skirt edges (`unpaired == 0`)
    cx_b, cy_b = xy_m((0.5 * (xs[0] + xs[ie]), 0.5 * (ys[0] + ys[jn])))
    pc_b = (cx_b, cy_b, base_z)
    perim_b = (
        [(*xy_m((xs[i], ys[0])), base_z) for i in range(ie)]
        + [(*xy_m((xs[ie], ys[j])), base_z) for j in range(jn)]
        + [(*xy_m((xs[i], ys[jn])), base_z) for i in range(ie, 0, -1)]
        + [(*xy_m((xs[0], ys[j])), base_z) for j in range(jn, 0, -1)]
    )
    for k in range(len(perim_b)):
        p_curr = perim_b[k]
        p_next = perim_b[(k + 1) % len(perim_b)]
        add_tri(mesh, pc_b, p_next, p_curr, MATERIALS["hill_earth"])

    # Exposed-aggregate South Entrance Plaza & Abbey Approach Walk (flush just below +0.41 m Lobby)
    z_l1 = m_ft(G.Z_L1_FT)  # -8.69 m
    plaza_poly = [
        (-96.0, G.GRID_Y["2"]),
        (21.0, G.GRID_Y["2"]),
        (21.0, -82.0),
        (-96.0, -82.0),
    ]
    add_extruded_polygon_ft(mesh, plaza_poly, 0.15, 0.36, MATERIALS["plaza_paving"], MATERIALS["concrete"])

    # Broad Abbey South Promenade Walk extending toward Quad axis
    walk_poly = [
        (-26.0, -82.0),
        (8.0, -82.0),
        (8.0, -104.5),
        (-26.0, -104.5),
    ]
    add_extruded_polygon_ft(mesh, walk_poly, 0.08, 0.34, MATERIALS["plaza_paving"], MATERIALS["concrete"])

    # Low Buff-Brick Entry Forecourt Bench Wall along South Plaza
    add_wall_strip_ft(mesh, [(-92.0, -68.5), (-30.0, -68.5)], 1.4, 0.36, 0.95, MATERIALS["buff_brick"])

    # Subtle low concrete site curbs flanking the West & East upper plaza transitions
    add_wall_strip_ft(
        mesh,
        [(G.X_WEST_WING, G.GRID_Y["3"]), (G.X_WEST_WING - 7.5, G.GRID_Y["3"]), (G.X_WEST_WING - 7.5, G.GRID_Y["6"]), (G.X_WEST_WING, G.GRID_Y["6"])],
        1.1,
        -1.2,
        0.38,
        MATERIALS["concrete"],
    )
    add_wall_strip_ft(
        mesh,
        [(G.X_AUD_E, G.GRID_Y["1"]), (G.X_AUD_E + 6.5, G.GRID_Y["1"]), (G.X_AUD_E + 6.5, G.GRID_Y["5"]), (G.X_AUD_E, G.GRID_Y["5"])],
        1.1,
        -1.2,
        0.38,
        MATERIALS["concrete"],
    )

    # North & East Perimeter Concrete Maintenance Apron at Level 1 Toe (-28'-6" / -8.69 m)
    l1_chain = [G.PT_A_INNER_JUNC, *get_north_perimeter_with_pockets_ft(level=1), (44.5, 25.0)]
    apron_pts = [
        (-84.5, 13.5), (-92.5, 16.0), (-65.5, 62.5), (-15.0, 92.5), (44.0, 92.5), (99.5, 74.5), (49.0, 22.0),
        *reversed(l1_chain),
    ]
    add_extruded_polygon_ft(mesh, apron_pts, z_l1 - 1.50, z_l1 - 0.04, MATERIALS["plaza_paving"], MATERIALS["concrete"])

    # Local material definitions for contextual campus architecture
    buff_brick = MATERIALS["buff_brick"]
    terracotta_roof = {"color": (0.72, 0.36, 0.25), "roughness": 0.78, "metallic": 0.05}
    gravel_roof = {"color": (0.82, 0.80, 0.76), "roughness": 0.88, "metallic": 0.04}
    copper_roof = MATERIALS["copper_roof"]

    # =========================================================================
    # ABBEY DRIVE & CAMPUS QUAD WALKWAYS
    # =========================================================================
    drive_pts = [
        (-280.0, 40.0),
        (-220.0, 55.0),
        (-160.0, 80.0),
        (-100.0, 110.0),
        (-35.0, 128.0),
        (35.0, 126.0),
        (105.0, 110.0),
        (175.0, 85.0),
        (245.0, 52.0),
        (315.0, 15.0),
        (375.0, -25.0),
    ]
    _add_road_ribbon_ft(mesh, drive_pts, 20.0, MATERIALS["concrete_dark"])

    # Central E-W Quad Axial Walkway arriving at the Abbey Church Semicircular Forecourt
    add_extruded_polygon_ft(
        mesh,
        [(-135.0, -116.0), (238.0, -116.0), (238.0, -128.0), (-135.0, -128.0)],
        0.05, 0.32, MATERIALS["plaza_paving"], MATERIALS["concrete"]
    )
    # Connector Walkway linking Library Promenade south to Quad Axial Walk
    add_extruded_polygon_ft(
        mesh,
        [(-18.0, -104.5), (0.0, -104.5), (0.0, -116.0), (-18.0, -116.0)],
        0.05, 0.32, MATERIALS["plaza_paving"], MATERIALS["concrete"]
    )
    # West Quad Cross Walkway connecting Aquinas Hall south to Romanesque Hall
    add_extruded_polygon_ft(
        mesh,
        [(-162.0, -80.0), (-150.0, -80.0), (-150.0, -130.0), (-162.0, -130.0)],
        0.05, 0.30, MATERIALS["plaza_paving"], MATERIALS["concrete"]
    )
    # South Cross Walkway connecting Axial Walk south to Modern Seminary Pavilions
    add_extruded_polygon_ft(
        mesh,
        [(-32.0, -128.0), (-20.0, -128.0), (-20.0, -190.0), (-32.0, -190.0)],
        0.05, 0.28, MATERIALS["plaza_paving"], MATERIALS["concrete"]
    )
    # Semicircular Abbey Church Forecourt Plaza (center=(238.0, -122.0), R=46 ft, West half 90°..270°)
    forecourt_arc = arc_pts((238.0, -122.0), 46.0, 90.0, 270.0, steps=16)
    forecourt_poly = [(238.0, -76.0)] + forecourt_arc + [(238.0, -168.0)]
    add_extruded_polygon_ft(
        mesh,
        forecourt_poly,
        0.05, 0.38, MATERIALS["plaza_paving"], MATERIALS["concrete"]
    )

    # =========================================================================
    # SURROUNDING HILLTOP BUILDINGS (CLEAN 100% 2-MANIFOLD MAQUETTE MASSING)
    # =========================================================================

    # --- A) Minor Seminary / Aquinas Hall (Immediately West/SW of Library) ---
    # Main East-West 3-story wing along north lawn
    add_box_m(mesh, m_ft(-242.0), m_ft(-80.0), 0.20, m_ft(-148.0), m_ft(-42.0), 10.50, buff_brick)
    _add_hipped_roof_ft(mesh, -243.5, -81.5, -146.5, -40.5, 10.50, 14.50, terracotta_roof, hip_x_ft=18.0, axis="X")
    # North wing projecting toward the bluff
    add_box_m(mesh, m_ft(-242.0), m_ft(-42.0), -0.50, m_ft(-208.0), m_ft(14.0), 10.50, buff_brick)
    _add_hipped_roof_ft(mesh, -243.5, -42.0, -206.5, 15.5, 10.50, 14.50, terracotta_roof, hip_y_ft=16.0, axis="Y")
    # South entrance pavilion facing the quad lawn
    add_box_m(mesh, m_ft(-205.0), m_ft(-94.0), 0.30, m_ft(-175.0), m_ft(-80.0), 11.20, buff_brick)
    _add_hipped_roof_ft(mesh, -206.0, -95.0, -174.0, -79.0, 11.20, 14.00, terracotta_roof, hip_y_ft=0.0, axis="Y")
    # East connector porch
    add_box_m(mesh, m_ft(-148.0), m_ft(-70.0), 0.30, m_ft(-136.0), m_ft(-52.0), 4.20, buff_brick)
    _add_hipped_roof_ft(mesh, -148.5, -70.5, -135.5, -51.5, 4.20, 5.80, terracotta_roof, hip_x_ft=4.0, axis="X")

    # --- B) Downhill Rectangular Brick/Terracotta Annex (NW of Library on Terrace) ---
    add_box_m(mesh, m_ft(-195.0), m_ft(40.0), -4.50, m_ft(-135.0), m_ft(75.0), -0.50, buff_brick)
    _add_hipped_roof_ft(mesh, -196.5, 38.5, -133.5, 76.5, -0.50, 2.50, terracotta_roof, hip_x_ft=0.0, axis="X")
    # Twin roof skylights / monitors
    add_box_m(mesh, m_ft(-182.0), m_ft(52.0), 1.60, m_ft(-168.0), m_ft(63.0), 2.70, copper_roof)
    add_box_m(mesh, m_ft(-162.0), m_ft(52.0), 1.60, m_ft(-148.0), m_ft(63.0), 2.70, copper_roof)

    # --- C) East Monastery Range, Abbey Church, Bell Tower & West Arcaded Portico ---
    # Bluff-side East Monastery Wing SE of Library
    add_box_m(mesh, m_ft(125.0), m_ft(-58.0), 0.20, m_ft(210.0), m_ft(-18.0), 10.20, buff_brick)
    _add_hipped_roof_ft(mesh, 123.5, -59.5, 211.5, -16.5, 10.20, 14.00, terracotta_roof, hip_x_ft=16.0, axis="X")

    # Grand Symmetrical 3-Story N-S Monastery Building behind Abbey Church
    # Main continuous N-S wing spanning Y = -254.0 .. +10.0 ft
    add_box_m(mesh, m_ft(342.0), m_ft(-254.0), 0.30, m_ft(380.0), m_ft(10.0), 11.20, buff_brick)
    _add_hipped_roof_ft(mesh, 340.5, -255.5, 381.5, 11.5, 11.20, 15.00, terracotta_roof, hip_y_ft=16.0, axis="Y")
    # North West-Projecting End Pavilion (Y = -24.0 .. +10.0 ft)
    add_box_m(mesh, m_ft(316.0), m_ft(-24.0), 0.30, m_ft(342.0), m_ft(10.0), 11.20, buff_brick)
    _add_hipped_roof_ft(mesh, 314.5, -25.5, 342.0, 11.5, 11.20, 15.00, terracotta_roof, hip_x_ft=0.0, axis="X")
    # South West-Projecting End Pavilion (Y = -254.0 .. -220.0 ft)
    add_box_m(mesh, m_ft(316.0), m_ft(-254.0), 0.30, m_ft(342.0), m_ft(-220.0), 11.20, buff_brick)
    _add_hipped_roof_ft(mesh, 314.5, -255.5, 342.0, -218.5, 11.20, 15.00, terracotta_roof, hip_x_ft=0.0, axis="X")
    # Symmetrical West-Facing Cross-Gabled Entry Bays
    add_box_m(mesh, m_ft(336.0), m_ft(-66.0), 0.30, m_ft(342.0), m_ft(-48.0), 11.50, buff_brick)
    _add_hipped_roof_ft(mesh, 335.0, -67.0, 342.0, -47.0, 11.50, 13.50, terracotta_roof, hip_x_ft=0.0, axis="X")
    add_box_m(mesh, m_ft(336.0), m_ft(-196.0), 0.30, m_ft(342.0), m_ft(-178.0), 11.50, buff_brick)
    _add_hipped_roof_ft(mesh, 335.0, -197.0, 342.0, -177.0, 11.50, 13.50, terracotta_roof, hip_x_ft=0.0, axis="X")

    # Mount Angel Abbey Church Nave (projecting West from center of Monastery)
    add_box_m(mesh, m_ft(252.0), m_ft(-142.0), 0.40, m_ft(355.0), m_ft(-102.0), 13.50, buff_brick)
    _add_hipped_roof_ft(mesh, 250.5, -143.5, 356.5, -100.5, 13.50, 18.20, terracotta_roof, hip_x_ft=0.0, axis="X")
    # West Rose Window / Gable Relief on Church Nave
    add_box_m(mesh, m_ft(251.2), m_ft(-128.0), 8.50, m_ft(252.0), m_ft(-116.0), 12.50, MATERIALS["copper_roof"])

    # Lower Side Aisles flanking Church Nave
    add_box_m(mesh, m_ft(252.0), m_ft(-102.0), 0.40, m_ft(345.0), m_ft(-90.0), 7.50, buff_brick)
    _add_hipped_roof_ft(mesh, 251.0, -103.0, 346.0, -89.0, 7.50, 9.50, terracotta_roof, hip_x_ft=0.0, axis="X")
    add_box_m(mesh, m_ft(278.0), m_ft(-154.0), 0.40, m_ft(345.0), m_ft(-142.0), 7.50, buff_brick)
    _add_hipped_roof_ft(mesh, 277.5, -155.0, 346.0, -141.0, 7.50, 9.50, terracotta_roof, hip_x_ft=0.0, axis="X")

    # Iconic Abbey Bell Tower / Campanile (on SOUTH side of Nave, X = 260..278 ft, Y = -162..-144 ft)
    add_box_m(mesh, m_ft(260.0), m_ft(-162.0), 0.40, m_ft(278.0), m_ft(-144.0), 27.50, buff_brick)
    # Upper triple-louver band & collar
    add_box_m(mesh, m_ft(259.5), m_ft(-162.5), 27.50, m_ft(278.5), m_ft(-143.5), 29.50, buff_brick)
    add_box_m(mesh, m_ft(259.0), m_ft(-159.0), 27.80, m_ft(260.0), m_ft(-147.0), 29.20, MATERIALS["concrete_dark"])
    # Open 4-Pier Arched Belfry
    add_box_m(mesh, m_ft(260.0), m_ft(-148.0), 29.50, m_ft(264.0), m_ft(-144.0), 33.50, buff_brick)
    add_box_m(mesh, m_ft(274.0), m_ft(-148.0), 29.50, m_ft(278.0), m_ft(-144.0), 33.50, buff_brick)
    add_box_m(mesh, m_ft(260.0), m_ft(-162.0), 29.50, m_ft(264.0), m_ft(-158.0), 33.50, buff_brick)
    add_box_m(mesh, m_ft(274.0), m_ft(-162.0), 29.50, m_ft(278.0), m_ft(-158.0), 33.50, buff_brick)
    # Dark Belfry Bell Chamber Core
    add_box_m(mesh, m_ft(263.5), m_ft(-158.5), 29.50, m_ft(274.5), m_ft(-147.5), 33.50, MATERIALS["concrete_dark"])
    # Belfry Cornice & Pyramidal Terracotta Spire
    add_box_m(mesh, m_ft(259.0), m_ft(-163.0), 33.50, m_ft(279.0), m_ft(-143.0), 34.20, buff_brick)
    _add_pyramidal_roof_ft(mesh, 258.5, -163.5, 279.5, -142.5, 34.20, 38.50, terracotta_roof)

    # Wide 1-Story Romanesque Arcaded West Narthex / Cloister Portico (Y = -184.0 .. -60.0 ft)
    # Raised Central Triple-Arch Entry Vestibule with Flat Parapet
    add_box_m(mesh, m_ft(236.0), m_ft(-138.0), 0.40, m_ft(254.0), m_ft(-106.0), 5.60, buff_brick)
    add_box_m(mesh, m_ft(236.0), m_ft(-138.0), 5.60, m_ft(254.0), m_ft(-106.0), 6.00, buff_brick)
    add_box_m(mesh, m_ft(237.5), m_ft(-136.5), 5.60, m_ft(252.5), m_ft(-107.5), 5.75, gravel_roof)
    add_box_m(mesh, m_ft(235.2), m_ft(-132.0), 0.40, m_ft(236.0), m_ft(-112.0), 4.80, MATERIALS["concrete_dark"])
    # North Arcaded Portico Wing
    add_box_m(mesh, m_ft(240.0), m_ft(-106.0), 0.40, m_ft(254.0), m_ft(-60.0), 4.30, buff_brick)
    _add_hipped_roof_ft(mesh, 239.0, -107.0, 255.0, -59.0, 4.30, 5.40, terracotta_roof, hip_y_ft=6.0, axis="Y")
    add_box_m(mesh, m_ft(239.2), m_ft(-102.0), 0.40, m_ft(240.0), m_ft(-64.0), 3.80, MATERIALS["concrete_dark"])
    # South Arcaded Portico Wing
    add_box_m(mesh, m_ft(240.0), m_ft(-184.0), 0.40, m_ft(254.0), m_ft(-138.0), 4.30, buff_brick)
    _add_hipped_roof_ft(mesh, 239.0, -185.0, 255.0, -137.0, 4.30, 5.40, terracotta_roof, hip_y_ft=6.0, axis="Y")
    add_box_m(mesh, m_ft(239.2), m_ft(-180.0), 0.40, m_ft(240.0), m_ft(-142.0), 3.80, MATERIALS["concrete_dark"])

    # --- D) South-West Seminary Academic Halls ---
    # Romanesque Academic Hall (framing West end of axial lawn)
    add_box_m(mesh, m_ft(-235.0), m_ft(-185.0), 0.30, m_ft(-135.0), m_ft(-130.0), 8.50, buff_brick)
    _add_hipped_roof_ft(mesh, -236.5, -186.5, -133.5, -128.5, 8.50, 12.20, terracotta_roof, hip_x_ft=18.0, axis="X")
    # Central flat monitor deck
    add_box_m(mesh, m_ft(-200.0), m_ft(-168.0), 12.10, m_ft(-170.0), m_ft(-147.0), 12.45, gravel_roof)
    # Projecting central entrance pavilion
    add_box_m(mesh, m_ft(-195.0), m_ft(-130.0), 0.30, m_ft(-175.0), m_ft(-124.0), 9.20, buff_brick)
    _add_hipped_roof_ft(mesh, -196.0, -130.0, -174.0, -123.0, 9.20, 11.20, terracotta_roof, hip_y_ft=0.0, axis="Y")

    # Modern Seminary Academic Pavilions (Mount Angel Seminary)
    # North Pavilion (2 stories + parapet & roof monitors)
    add_box_m(mesh, m_ft(-65.0), m_ft(-235.0), 0.25, m_ft(15.0), m_ft(-190.0), 7.20, buff_brick)
    add_box_m(mesh, m_ft(-65.0), m_ft(-235.0), 7.20, m_ft(15.0), m_ft(-190.0), 7.80, buff_brick)
    add_box_m(mesh, m_ft(-63.5), m_ft(-233.5), 7.20, m_ft(13.5), m_ft(-191.5), 7.50, gravel_roof)
    add_box_m(mesh, m_ft(-52.0), m_ft(-222.0), 7.50, m_ft(-32.0), m_ft(-203.0), 8.35, copper_roof)
    add_box_m(mesh, m_ft(-18.0), m_ft(-222.0), 7.50, m_ft(2.0), m_ft(-203.0), 8.35, copper_roof)

    # South Pavilion (2 stories + parapet & roof monitors)
    add_box_m(mesh, m_ft(-50.0), m_ft(-290.0), 0.20, m_ft(25.0), m_ft(-245.0), 7.20, buff_brick)
    add_box_m(mesh, m_ft(-50.0), m_ft(-290.0), 7.20, m_ft(25.0), m_ft(-245.0), 7.80, buff_brick)
    add_box_m(mesh, m_ft(-48.5), m_ft(-288.5), 7.20, m_ft(23.5), m_ft(-246.5), 7.50, gravel_roof)
    add_box_m(mesh, m_ft(-35.0), m_ft(-278.0), 7.50, m_ft(-15.0), m_ft(-257.0), 8.35, copper_roof)
    add_box_m(mesh, m_ft(-5.0), m_ft(-278.0), 7.50, m_ft(15.0), m_ft(-257.0), 8.35, copper_roof)

    # Enclosed link corridor
    add_box_m(mesh, m_ft(-25.0), m_ft(-245.0), 0.22, m_ft(-10.0), m_ft(-235.0), 4.20, buff_brick)

    return grp
