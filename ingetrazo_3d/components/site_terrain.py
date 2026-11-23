"""
Layer 1: Mount Angel Abbey Bluff Terrain, Surveyed Campus Massing & Quad Walkways (`1_Abbey_Hillside_Site`).

Calibrated to zoom-19 Google satellite ortho-aerial (45.0576° N, -122.7748° W, Reference North
26.81° CW from True North), OpenStreetMap surveyed footprints, and Alvar Aalto's 1967–1970
archival Sheets 01-A1 (Location & Access Plan) and 02-A2 (Plot Plan) in Working Point #3 feet.

Models:
  - Expanded 2-manifold Abbey hilltop promontory (X = -560..+580 ft, Y = -480..+240 ft)
  - Dense 10-ft topography & Library excavation across [-140..+115] x [-70..+110] ft
  - Pre-construction unexcavated bare bluff restoration (`8_PreConstruction_Hill`)
  - Surveyed Quad formal walkways (Central E-W Axis at Y=-198 ft, Semicircular Abbey Church
    Forecourt, Curved Crescent Walk, West/East cross-walks, South Stair) & seamless Abbey Drive
  - Clean 2-manifold architectural maquette massing for all surrounding campus buildings:
    Post-Knox Boiler House, Anselm Hall, Damian Center, Aquinas Hall, Mount Angel Abbey
    Church / 118-ft Bell Tower / Grand Monastery, Annunciation Hall, Saint Benedict
    Guesthouse & Retreat Center, and Abbey Press Building.
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


def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def natural_hillside_z_m(x_ft: float, y_ft: float) -> float:
    """Smooth Mount Angel Abbey hilltop promontory elevation (metres) outside building excavation.

    Preserves the exact historical formula across the Library core [-140..115] x [-70..110] ft
    so every foundation wall, apron, and `8_PreConstruction_Hill` vertex remains locked, while
    blending smoothly outward across the entire hilltop Quad plateau (-560..+580 x -480..+240 ft).
    """
    # Exact locked Library core region (matches `library-3d.html` radial guide draping)
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

    # Continuous north bluff crest line across the full hilltop promontory
    if x_ft < -140.0:
        # Blend smoothly from Library crest (-42 ft) to Anselm/Damian bluff crest (+12 ft)
        w = _smoothstep(-140.0, -240.0, x_ft)
        y_crest = -42.0 * (1.0 - w) + 12.0 * w
    elif x_ft > 115.0:
        # Blend smoothly from Library crest (-42 ft) to Aquinas/Monastery bluff crest (+18 ft)
        w = _smoothstep(115.0, 195.0, x_ft)
        y_crest = -42.0 * (1.0 - w) + 18.0 * w
    else:
        y_crest = -42.0

    # Gently crown-level hilltop Quad plateau, rolling softly off the far South/West/East flanks
    if y_ft <= y_crest:
        z = 0.30 - 0.0003 * max(0.0, y_crest - y_ft)
        # Keep main hilltop Quad plateau (-495..+510 x -455..y_crest) comfortably level
        if y_ft < -455.0:
            z -= 0.065 * (-455.0 - y_ft)
        if x_ft < -500.0:
            z -= 0.030 * (-500.0 - x_ft)
        elif x_ft > 510.0:
            z -= 0.030 * (x_ft - 510.0)
        return z
    else:
        dy = y_ft - y_crest
        if dy <= 130.0:
            t = dy / 130.0
            s = t * t * (3.0 - 2.0 * t)
            z = 0.30 * (1.0 - s) + (-9.85) * s
        else:
            t2 = (dy - 130.0) / 54.0
            z = -9.85 - 2.35 * t2
        if x_ft < -500.0:
            z -= 0.020 * (-500.0 - x_ft)
        elif x_ft > 510.0:
            z -= 0.020 * (x_ft - 510.0)
        return z


def _rot_pt(x: float, y: float, cx: float, cy: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    c, s = math.cos(rad), math.sin(rad)
    dx, dy = x - cx, y - cy
    return cx + dx * c - dy * s, cy + dx * s + dy * c


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
    rot_deg: float = 0.0,
    pivot: tuple[float, float] | None = None,
):
    """Add a closed 2-manifold hipped/gabled roof solid with optional plan rotation (`unpaired == 0`)."""
    if x0_ft > x1_ft:
        x0_ft, x1_ft = x1_ft, x0_ft
    if y0_ft > y1_ft:
        y0_ft, y1_ft = y1_ft, y0_ft

    cx = 0.5 * (x0_ft + x1_ft) if pivot is None else pivot[0]
    cy = 0.5 * (y0_ft + y1_ft) if pivot is None else pivot[1]

    def _pt(x: float, y: float, z: float) -> tuple[float, float, float]:
        if abs(rot_deg) > 1e-6:
            x, y = _rot_pt(x, y, cx, cy, rot_deg)
        return (*xy_m((x, y)), z)

    p0 = _pt(x0_ft, y0_ft, z_eaves_m)
    p1 = _pt(x1_ft, y0_ft, z_eaves_m)
    p2 = _pt(x1_ft, y1_ft, z_eaves_m)
    p3 = _pt(x0_ft, y1_ft, z_eaves_m)

    add_quad(mesh, p0, p3, p2, p1, attrs)  # bottom (-Z)
    if axis == "X":
        ymid = 0.5 * (y0_ft + y1_ft)
        r0 = _pt(x0_ft + hip_x_ft, ymid, z_ridge_m)
        r1 = _pt(x1_ft - hip_x_ft, ymid, z_ridge_m)
        add_quad(mesh, p0, p1, r1, r0, attrs)  # south slope
        add_quad(mesh, p2, p3, r0, r1, attrs)  # north slope
        add_tri(mesh, p3, p0, r0, attrs)       # west gable/hip
        add_tri(mesh, p1, p2, r1, attrs)       # east gable/hip
    else:
        xmid = 0.5 * (x0_ft + x1_ft)
        r0 = _pt(xmid, y0_ft + hip_y_ft, z_ridge_m)
        r1 = _pt(xmid, y1_ft - hip_y_ft, z_ridge_m)
        add_quad(mesh, p0, r0, r1, p3, attrs)  # west slope
        add_quad(mesh, p1, p2, r1, r0, attrs)  # east slope
        add_tri(mesh, p0, p1, r0, attrs)       # south gable/hip
        add_tri(mesh, p2, p3, r1, attrs)       # north gable/hip


def _add_rotated_box_ft(
    mesh,
    x0_ft: float,
    y0_ft: float,
    x1_ft: float,
    y1_ft: float,
    z_bot_m: float,
    z_top_m: float,
    attrs: dict,
    rot_deg: float = 0.0,
    pivot: tuple[float, float] | None = None,
):
    """Add an oriented rectangular prism in local feet (`unpaired == 0`)."""
    if x0_ft > x1_ft:
        x0_ft, x1_ft = x1_ft, x0_ft
    if y0_ft > y1_ft:
        y0_ft, y1_ft = y1_ft, y0_ft
    cx = 0.5 * (x0_ft + x1_ft) if pivot is None else pivot[0]
    cy = 0.5 * (y0_ft + y1_ft) if pivot is None else pivot[1]
    corners = [(x0_ft, y0_ft), (x1_ft, y0_ft), (x1_ft, y1_ft), (x0_ft, y1_ft)]
    if abs(rot_deg) > 1e-6:
        corners = [_rot_pt(x, y, cx, cy, rot_deg) for x, y in corners]
    add_extruded_polygon_ft(mesh, corners, z_bot_m, z_top_m, attrs, attrs)


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


def _add_mitered_ribbon_ft(
    mesh,
    pts_ft: list[tuple[float, float]],
    width_ft: float,
    top_attrs: dict,
    side_attrs: dict | None = None,
    z_fixed_top_m: float | None = None,
    z_fixed_bot_m: float | None = None,
    z_lift_m: float = 0.08,
    thickness_m: float = 0.30,
):
    """Extrude a continuous, notch-free mitered 2-manifold roadway or walkway ribbon (`unpaired == 0`)."""
    if len(pts_ft) < 2:
        return
    if side_attrs is None:
        side_attrs = top_attrs

    # Filter duplicate consecutive points
    clean: list[tuple[float, float]] = [pts_ft[0]]
    for pt in pts_ft[1:]:
        if math.hypot(pt[0] - clean[-1][0], pt[1] - clean[-1][1]) > 1e-3:
            clean.append(pt)
    n = len(clean)
    if n < 2:
        return

    half_w = width_ft * 0.5
    seg_normals: list[tuple[float, float]] = []
    for i in range(n - 1):
        dx = clean[i + 1][0] - clean[i][0]
        dy = clean[i + 1][1] - clean[i][1]
        L = math.hypot(dx, dy)
        seg_normals.append((-dy / L, dx / L))  # left normal

    left_top: list[tuple[float, float, float]] = []
    right_top: list[tuple[float, float, float]] = []
    left_bot: list[tuple[float, float, float]] = []
    right_bot: list[tuple[float, float, float]] = []

    for i in range(n):
        x, y = clean[i]
        if i == 0:
            mx, my = seg_normals[0]
            scale = half_w
        elif i == n - 1:
            mx, my = seg_normals[-1]
            scale = half_w
        else:
            n0x, n0y = seg_normals[i - 1]
            n1x, n1y = seg_normals[i]
            bx, by = n0x + n1x, n0y + n1y
            bL = math.hypot(bx, by)
            if bL < 1e-4:
                mx, my, scale = n0x, n0y, half_w
            else:
                mx, my = bx / bL, by / bL
                dot = max(0.45, mx * n0x + my * n0y)
                scale = min(half_w * 2.0, half_w / dot)

        lx, ly = x + mx * scale, y + my * scale
        rx, ry = x - mx * scale, y - my * scale

        if z_fixed_top_m is not None:
            zt = z_fixed_top_m
            zb = z_fixed_bot_m if z_fixed_bot_m is not None else (zt - thickness_m)
        else:
            zg = natural_hillside_z_m(x, y)
            zt = zg + z_lift_m
            zb = zg - (thickness_m - z_lift_m)

        left_top.append((*xy_m((lx, ly)), zt))
        right_top.append((*xy_m((rx, ry)), zt))
        left_bot.append((*xy_m((lx, ly)), zb))
        right_bot.append((*xy_m((rx, ry)), zb))

    for i in range(n - 1):
        # CCW when viewed from outside (+Z top, -Z bottom, +left, +right)
        add_quad(mesh, right_top[i], right_top[i + 1], left_top[i + 1], left_top[i], top_attrs)
        add_quad(mesh, left_bot[i], left_bot[i + 1], right_bot[i + 1], right_bot[i], side_attrs)
        add_quad(mesh, left_top[i], left_top[i + 1], left_bot[i + 1], left_bot[i], side_attrs)
        add_quad(mesh, right_top[i], right_bot[i], right_bot[i + 1], right_top[i + 1], side_attrs)

    # Start & end caps
    add_quad(mesh, left_top[0], left_bot[0], right_bot[0], right_top[0], side_attrs)
    add_quad(mesh, right_top[-1], right_bot[-1], left_bot[-1], left_top[-1], side_attrs)


def build_site_terrain(scene):
    grp = create_scene_group(scene, "1_Abbey_Hillside_Site")
    mesh = grp.mesh
    G = AaltoGeometry

    l2_env = get_level2_envelope_ft()
    l3_env = get_level3_envelope_ft()
    excav_z = m_ft(G.Z_L1_FT) - 0.45  # -9.14 m sub-slab footing datum inside building footprint

    # Expanded Hilltop Promontory Maquette Grid: X = [-560..+580] ft, Y = [-480..+240] ft
    # Dense 10-ft spacing locked across Library footprint [-140..+115] x [-70..+110] ft
    xs_west = [-560.0, -520.0, -480.0, -440.0, -400.0, -360.0, -320.0, -280.0, -245.0, -210.0, -175.0, -155.0]
    xs_lib = [
        -140.0, -130.0, -120.0, -110.0, -100.0, -90.0, -80.0, -70.0, -60.0, -50.0,
        -40.0, -30.0, -20.0, -10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0,
        60.0, 70.0, 80.0, 90.0, 100.0, 115.0,
    ]
    xs_east = [135.0, 160.0, 190.0, 225.0, 260.0, 300.0, 340.0, 380.0, 420.0, 460.0, 500.0, 540.0, 580.0]
    xs = xs_west + xs_lib + xs_east

    ys_south = [-480.0, -455.0, -425.0, -395.0, -365.0, -330.0, -295.0, -260.0, -225.0, -195.0, -165.0, -135.0, -110.0, -88.0]
    ys_lib = [
        -70.0, -60.0, -50.0, -40.0, -30.0, -20.0, -10.0, 0.0, 10.0, 20.0,
        30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0,
    ]
    ys_north = [125.0, 145.0, 168.0, 192.0, 216.0, 240.0]
    ys = ys_south + ys_lib + ys_north

    grid_z: list[list[float]] = []
    nat_z: list[list[float]] = []
    for x in xs:
        col = []
        ncol = []
        for y in ys:
            nz = natural_hillside_z_m(x, y)
            hz = nz
            if _point_in_poly_2d((x, y), l2_env):
                hz = min(hz, excav_z)
            elif _point_in_poly_2d((x, y), l3_env):
                # Under South Wing crawl space: keep below South Wing slab (+0.41 m)
                hz = min(hz, m_ft(G.Z_LOBBY_FT) - 0.45)
            col.append(hz)
            ncol.append(nz)
        grid_z.append(col)
        nat_z.append(ncol)

    grp_bare = create_scene_group(scene, "8_PreConstruction_Hill")
    mesh_bare = grp_bare.mesh

    def _as_post(m: dict) -> dict:
        return {**m, "post_site": True}

    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            x0, x1 = xs[i], xs[i + 1]
            y0, y1 = ys[j], ys[j + 1]
            p00 = (*xy_m((x0, y0)), grid_z[i][j])
            p10 = (*xy_m((x1, y0)), grid_z[i + 1][j])
            p11 = (*xy_m((x1, y1)), grid_z[i + 1][j + 1])
            p01 = (*xy_m((x0, y1)), grid_z[i][j + 1])

            cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
            in_l2_pit = _point_in_poly_2d((cx, cy), l2_env)
            is_excav_cell = (
                in_l2_pit
                or abs(grid_z[i][j] - nat_z[i][j]) > 1e-4
                or abs(grid_z[i + 1][j] - nat_z[i + 1][j]) > 1e-4
                or abs(grid_z[i + 1][j + 1] - nat_z[i + 1][j + 1]) > 1e-4
                or abs(grid_z[i][j + 1] - nat_z[i][j + 1]) > 1e-4
            )
            mat = MATERIALS["concrete_dark"] if in_l2_pit else MATERIALS["hill_grass"]
            add_quad(mesh, p00, p10, p11, p01, _as_post(mat) if is_excav_cell else mat)

            if is_excav_cell:
                n00 = (*xy_m((x0, y0)), nat_z[i][j])
                n10 = (*xy_m((x1, y0)), nat_z[i + 1][j])
                n11 = (*xy_m((x1, y1)), nat_z[i + 1][j + 1])
                n01 = (*xy_m((x0, y1)), nat_z[i][j + 1])
                add_quad(mesh_bare, n00, n10, n11, n01, MATERIALS["hill_grass"])

    # Thickened earthen plinth skirt around outer terrain perimeter (closed 2-manifold maquette block)
    base_z = -22.0
    for i in range(len(xs) - 1):
        x0, y0 = xy_m((xs[i], ys[0]))
        x1, y1 = xy_m((xs[i + 1], ys[0]))
        add_quad(mesh, (x0, y0, base_z), (x1, y1, base_z), (x1, y1, grid_z[i + 1][0]), (x0, y0, grid_z[i][0]), MATERIALS["hill_earth"])
    jn = len(ys) - 1
    for i in range(len(xs) - 1):
        x0, y0 = xy_m((xs[i], ys[jn]))
        x1, y1 = xy_m((xs[i + 1], ys[jn]))
        add_quad(mesh, (x1, y1, base_z), (x0, y0, base_z), (x0, y0, grid_z[i][jn]), (x1, y1, grid_z[i + 1][jn]), MATERIALS["hill_earth"])
    ie = len(xs) - 1
    for j in range(len(ys) - 1):
        x0, y0 = xy_m((xs[ie], ys[j]))
        x1, y1 = xy_m((xs[ie], ys[j + 1]))
        add_quad(mesh, (x0, y0, base_z), (x1, y1, base_z), (x1, y1, grid_z[ie][j + 1]), (x0, y0, grid_z[ie][j]), MATERIALS["hill_earth"])
    for j in range(len(ys) - 1):
        x0, y0 = xy_m((xs[0], ys[j]))
        x1, y1 = xy_m((xs[0], ys[j + 1]))
        add_quad(mesh, (x1, y1, base_z), (x0, y0, base_z), (x0, y0, grid_z[0][j]), (x1, y1, grid_z[0][j + 1]), MATERIALS["hill_earth"])

    cx_b, cy_b = xy_m((0.5 * (xs[0] + xs[ie]), 0.5 * (ys[0] + ys[jn])))
    pc_b = (cx_b, cy_b, base_z)
    perim_b = (
        [(*xy_m((xs[i], ys[0])), base_z) for i in range(ie)]
        + [(*xy_m((xs[ie], ys[j])), base_z) for j in range(jn)]
        + [(*xy_m((xs[i], ys[jn])), base_z) for i in range(ie, 0, -1)]
        + [(*xy_m((xs[0], ys[j])), base_z) for j in range(jn, 0, -1)]
    )
    for k in range(len(perim_b)):
        add_tri(mesh, pc_b, perim_b[(k + 1) % len(perim_b)], perim_b[k], MATERIALS["hill_earth"])

    # =========================================================================
    # LIBRARY POST-CONSTRUCTION SITEWORK (HIDDEN IN `bareHill` MODE)
    # =========================================================================
    plaza_post = _as_post(MATERIALS["plaza_paving"])
    conc_post = _as_post(MATERIALS["concrete"])
    brick_post = _as_post(MATERIALS["buff_brick"])
    z_l1 = m_ft(G.Z_L1_FT)  # -8.69 m

    # Exposed-aggregate South Entrance Forecourt Plaza (flush just below +0.41 m Lobby)
    plaza_poly = [
        (-96.0, G.GRID_Y["2"]),
        (21.0, G.GRID_Y["2"]),
        (21.0, -72.0),
        (-96.0, -72.0),
    ]
    add_extruded_polygon_ft(mesh, plaza_poly, 0.12, 0.36, plaza_post, conc_post)

    # Connector Apron linking Library Portico South to North Perimeter Quad Walk (Y = -77 ft)
    add_extruded_polygon_ft(
        mesh,
        [(-45.0, -72.0), (-15.0, -72.0), (-15.0, -82.0), (-45.0, -82.0)],
        0.08, 0.34, plaza_post, conc_post,
    )

    # Low Buff-Brick Entry Forecourt Bench Wall along South Plaza
    add_wall_strip_ft(mesh, [(-92.0, -68.5), (-30.0, -68.5)], 1.4, 0.36, 0.95, brick_post)

    # Subtle low concrete site curbs flanking the West & East upper plaza transitions
    add_wall_strip_ft(
        mesh,
        [(G.X_WEST_WING, G.GRID_Y["3"]), (G.X_WEST_WING - 7.5, G.GRID_Y["3"]), (G.X_WEST_WING - 7.5, G.GRID_Y["6"]), (G.X_WEST_WING, G.GRID_Y["6"])],
        1.1, -1.2, 0.38, conc_post,
    )
    add_wall_strip_ft(
        mesh,
        [(G.X_AUD_E, G.GRID_Y["1"]), (G.X_AUD_E + 6.5, G.GRID_Y["1"]), (G.X_AUD_E + 6.5, G.GRID_Y["5"]), (G.X_AUD_E, G.GRID_Y["5"])],
        1.1, -1.2, 0.38, conc_post,
    )

    # North & East Perimeter Concrete Maintenance Apron at Level 1 Toe (-28'-6" / -8.69 m)
    l1_chain = [G.PT_A_INNER_JUNC, *get_north_perimeter_with_pockets_ft(level=1), (44.5, 25.0)]
    apron_pts = [
        (-84.5, 13.5), (-92.5, 16.0), (-65.5, 62.5), (-15.0, 92.5), (44.0, 92.5), (99.5, 74.5), (49.0, 22.0),
        *reversed(l1_chain),
    ]
    add_extruded_polygon_ft(mesh, apron_pts, z_l1 - 1.50, z_l1 - 0.04, plaza_post, conc_post)

    # Local material definitions for restrained contextual campus maquette architecture
    buff_brick = MATERIALS["buff_brick"]
    terracotta_roof = {"color": (0.72, 0.36, 0.25), "roughness": 0.78, "metallic": 0.05}
    gravel_roof = {"color": (0.85, 0.84, 0.80), "roughness": 0.88, "metallic": 0.04}
    slate_roof = {"color": (0.34, 0.37, 0.41), "roughness": 0.80, "metallic": 0.08}
    copper_roof = MATERIALS["copper_roof"]
    walk_paving = MATERIALS["plaza_paving"]
    walk_edge = MATERIALS["concrete"]
    road_asphalt = MATERIALS["concrete_dark"]

    # =========================================================================
    # SURVEYED ABBEY DRIVE, SERVICE ROADS & FORMAL QUAD WALKWAYS
    # =========================================================================

    # 1. North Bluff Abbey Drive (exact surveyed curve HWY 5496266, seamless mitered ribbon)
    north_drive_pts = [
        (-540.0, 118.0),
        (-485.0, 136.0),
        (-435.0, 158.0),
        (-410.0, 178.0),
        (-360.0, 168.0),
        (-295.0, 156.0),
        (-215.0, 148.0),
        (-135.0, 146.0),
        (-60.0, 150.0),
        (5.0, 149.0),
        (70.0, 139.0),
        (140.0, 126.0),
        (215.0, 117.0),
        (295.0, 96.0),
        (395.0, 75.0),
        (485.0, 65.0),
        (540.0, 48.0),
    ]
    _add_mitered_ribbon_ft(mesh, north_drive_pts, 22.0, road_asphalt, z_lift_m=0.16, thickness_m=0.45)

    # North Monastery Service Drive & Parking Apron East of Aquinas Hall (HWY 173105416)
    east_service_pts = [
        (165.0, 123.0),
        (195.0, 88.0),
        (228.0, 76.0),
        (260.0, 64.0),
        (299.0, 50.0),
        (338.0, 36.0),
        (356.0, 16.0),
        (372.0, -4.0),
        (430.0, -6.0),
        (495.0, -8.0),
        (535.0, -25.0),
    ]
    _add_mitered_ribbon_ft(mesh, east_service_pts, 18.0, road_asphalt, z_lift_m=0.25, thickness_m=0.55)

    # South Abbey Drive & South Campus Parking Strip (HWY 5496273 along south bluff edge)
    south_drive_pts = [
        (-520.0, -408.0),
        (-390.0, -420.0),
        (-240.0, -437.0),
        (-112.0, -448.0),
        (3.0, -454.0),
        (158.0, -462.0),
    ]
    _add_mitered_ribbon_ft(mesh, south_drive_pts, 22.0, road_asphalt, z_fixed_top_m=0.22, z_fixed_bot_m=-0.25)

    # 2. Central E-W Axial Quad Promenade (Y = -198 ft, 14 ft wide: Damian Center -> Abbey Church)
    _add_mitered_ribbon_ft(
        mesh,
        [(-372.0, -197.0), (-217.0, -197.0), (-116.0, -198.0), (228.0, -199.0)],
        14.0, walk_paving, walk_edge, z_fixed_top_m=0.33, z_fixed_bot_m=0.02,
    )

    # Damian Center East Entry Stone Plaza (framing west terminus of the Central Quad Axis)
    add_extruded_polygon_ft(
        mesh,
        [(-384.0, -172.0), (-332.0, -172.0), (-332.0, -224.0), (-384.0, -224.0)],
        0.02, 0.34, walk_paving, walk_edge,
    )

    # Semicircular Abbey Church Forecourt Plaza (center=(228.0, -199.0), R=54 ft, West semicircle)
    forecourt_arc = arc_pts((228.0, -199.0), 54.0, 90.0, 270.0, steps=20)
    forecourt_poly = [(228.0, -145.0)] + forecourt_arc + [(228.0, -253.0)]
    add_extruded_polygon_ft(mesh, forecourt_poly, 0.02, 0.36, walk_paving, walk_edge)

    # Square Crossing Node where the Curved Crescent Walk intersects the Central Axis (-116, -198)
    add_extruded_polygon_ft(
        mesh,
        [(-130.0, -184.0), (-102.0, -184.0), (-102.0, -212.0), (-130.0, -212.0)],
        0.02, 0.345, walk_paving, walk_edge,
    )

    # 3. Signature Sweeping Curved Crescent Walk (HWY 178571417: Library South -> Central Node -> South Walk)
    crescent_pts = [
        (-35.3, -77.2),
        (-52.0, -84.0),
        (-72.0, -95.0),
        (-89.0, -110.0),
        (-103.7, -127.3),
        (-112.5, -162.0),
        (-116.1, -198.1),
        (-112.3, -241.2),
        (-104.0, -280.9),
        (-92.0, -310.0),
        (-76.0, -337.0),
        (-61.2, -357.0),
    ]
    _add_mitered_ribbon_ft(mesh, crescent_pts, 8.5, walk_paving, walk_edge, z_fixed_top_m=0.32, z_fixed_bot_m=0.02)

    # 4. West Formal N-S Cross-Walk (HWY 177081403: Anselm Hall -> Central Axis -> Annunciation Hall)
    _add_mitered_ribbon_ft(
        mesh,
        [(-217.0, -96.0), (-217.0, -197.0), (-218.5, -281.0), (-219.5, -338.0)],
        9.0, walk_paving, walk_edge, z_fixed_top_m=0.32, z_fixed_bot_m=0.02,
    )

    # 5. Secondary West E-W Lawn Walk (HWY 178571422 at Y = -281 ft)
    _add_mitered_ribbon_ft(
        mesh,
        [(-346.0, -280.5), (-218.5, -281.0), (-104.0, -280.9)],
        7.5, walk_paving, walk_edge, z_fixed_top_m=0.315, z_fixed_bot_m=0.02,
    )

    # West Damian Center North/South Sweeping Perimeter Walks (HWY 177081404 & 177081406)
    _add_mitered_ribbon_ft(
        mesh,
        [(-332.0, -197.0), (-336.0, -155.0), (-346.0, -125.0), (-365.0, -104.0)],
        7.5, walk_paving, walk_edge, z_fixed_top_m=0.31, z_fixed_bot_m=0.02,
    )
    _add_mitered_ribbon_ft(
        mesh,
        [(-332.0, -197.0), (-344.0, -248.0), (-346.0, -281.0), (-356.0, -308.0)],
        7.5, walk_paving, walk_edge, z_fixed_top_m=0.31, z_fixed_bot_m=0.02,
    )

    # 6. North Perimeter Quad Walk (HWY 177081467: Anselm Hall -> Library Forecourt -> Aquinas Hall)
    _add_mitered_ribbon_ft(
        mesh,
        [(-162.0, -76.0), (-35.3, -77.2), (212.0, -78.0), (338.0, -80.0)],
        9.5, walk_paving, walk_edge, z_fixed_top_m=0.325, z_fixed_bot_m=0.02,
    )

    # 7. East Cloister N-S Walk (HWY 177081466 & 177081404: Aquinas Hall -> Church Forecourt -> Retreat Center)
    _add_mitered_ribbon_ft(
        mesh,
        [(212.0, -40.0), (212.0, -78.0), (212.0, -199.0), (209.0, -357.0), (209.0, -402.0)],
        10.0, walk_paving, walk_edge, z_fixed_top_m=0.325, z_fixed_bot_m=0.02,
    )

    # 8. South Perimeter Quad Walk (Y = -357 ft: Annunciation East -> South Stair -> East Cloister Walk)
    _add_mitered_ribbon_ft(
        mesh,
        [(-142.0, -357.0), (-61.2, -357.0), (0.4, -357.1), (209.0, -357.0)],
        9.5, walk_paving, walk_edge, z_fixed_top_m=0.32, z_fixed_bot_m=0.02,
    )
    # South Quad Grand Approach Steps & Walk down to South Abbey Drive (HWY 177081803)
    _add_mitered_ribbon_ft(
        mesh,
        [(0.4, -357.1), (3.0, -454.0)],
        12.0, walk_paving, walk_edge, z_fixed_top_m=0.30, z_fixed_bot_m=0.00,
    )
    # East Cloister South Spur to Monastery South Wing & Retreat Center (HWY 177081405)
    _add_mitered_ribbon_ft(
        mesh,
        [(209.0, -339.0), (250.0, -339.0), (374.0, -339.0)],
        8.5, walk_paving, walk_edge, z_fixed_top_m=0.315, z_fixed_bot_m=0.02,
    )
    _add_mitered_ribbon_ft(
        mesh,
        [(250.0, -339.0), (248.0, -392.0)],
        9.0, walk_paving, walk_edge, z_fixed_top_m=0.315, z_fixed_bot_m=0.02,
    )

    # =========================================================================
    # SURVEYED CAMPUS ARCHITECTURE (CLEAN 2-MANIFOLD MAQUETTE MASSING)
    # =========================================================================

    # --- 1) Post-Knox / Boiler House (NW Downhill Terrace behind Library, Pre-1970) ---
    # Exact surveyed orientation ~ -8.3 deg CCW, X=[-212..-120], Y=[+20..+71]
    pk_cx, pk_cy, pk_rot = -167.0, 45.0, -8.3
    _add_rotated_box_ft(mesh, -210.0, 25.0, -142.0, 64.0, -4.60, -0.35, buff_brick, pk_rot, (pk_cx, pk_cy))
    _add_hipped_roof_ft(mesh, -211.5, 23.5, -140.5, 65.5, -0.35, 2.45, terracotta_roof, hip_x_ft=0.0, axis="X", rot_deg=pk_rot, pivot=(pk_cx, pk_cy))
    # East mechanical bump-out toward Library West Wing
    _add_rotated_box_ft(mesh, -142.0, 44.0, -120.5, 64.0, -4.60, -0.60, buff_brick, pk_rot, (pk_cx, pk_cy))
    _add_hipped_roof_ft(mesh, -142.0, 43.0, -119.5, 65.0, -0.60, 1.40, terracotta_roof, hip_x_ft=0.0, axis="X", rot_deg=pk_rot, pivot=(pk_cx, pk_cy))
    # Twin roof skylight monitors visible in aerial
    _add_rotated_box_ft(mesh, -196.0, 38.0, -180.0, 50.0, 1.50, 2.65, gravel_roof, pk_rot, (pk_cx, pk_cy))
    _add_rotated_box_ft(mesh, -172.0, 38.0, -156.0, 50.0, 1.50, 2.65, gravel_roof, pk_rot, (pk_cx, pk_cy))

    # --- 2) Anselm Hall (formerly Minor Seminary, immediately West of Library, Pre-1970) ---
    # Surveyed multi-wing U/H footprint rotated +5.0 deg CCW, centered around (-240, -75)
    an_cx, an_cy, an_rot = -240.0, -75.0, 5.0
    # Main E-W 3-story spine
    _add_rotated_box_ft(mesh, -310.0, -96.0, -162.0, -52.0, 0.05, 10.60, buff_brick, an_rot, (an_cx, an_cy))
    _add_hipped_roof_ft(mesh, -311.5, -97.5, -160.5, -50.5, 10.60, 14.60, terracotta_roof, hip_x_ft=18.0, axis="X", rot_deg=an_rot, pivot=(an_cx, an_cy))
    # Projecting South-West Wing (X ~ -308..-264, Y ~ -140..-96)
    _add_rotated_box_ft(mesh, -308.0, -140.0, -264.0, -96.0, 0.05, 10.60, buff_brick, an_rot, (an_cx, an_cy))
    _add_hipped_roof_ft(mesh, -309.5, -141.5, -262.5, -94.0, 10.60, 14.60, terracotta_roof, hip_y_ft=16.0, axis="Y", rot_deg=an_rot, pivot=(an_cx, an_cy))
    # Projecting North-East Wing toward Library West courtyard (X ~ -202..-162, Y ~ -52..-12)
    _add_rotated_box_ft(mesh, -202.0, -52.0, -162.0, -12.0, -0.40, 10.60, buff_brick, an_rot, (an_cx, an_cy))
    _add_hipped_roof_ft(mesh, -203.5, -53.0, -160.5, -10.5, 10.60, 14.60, terracotta_roof, hip_y_ft=15.0, axis="Y", rot_deg=an_rot, pivot=(an_cx, an_cy))
    # Projecting South-East Pavilion facing Quad lawn (X ~ -202..-158, Y ~ -112..-96)
    _add_rotated_box_ft(mesh, -202.0, -112.0, -158.0, -96.0, 0.05, 10.60, buff_brick, an_rot, (an_cx, an_cy))
    _add_hipped_roof_ft(mesh, -203.5, -113.5, -156.5, -94.5, 10.60, 14.20, terracotta_roof, hip_x_ft=12.0, axis="X", rot_deg=an_rot, pivot=(an_cx, an_cy))
    # West projecting entry bay
    _add_rotated_box_ft(mesh, -323.0, -92.0, -310.0, -56.0, 0.05, 9.60, buff_brick, an_rot, (an_cx, an_cy))
    _add_hipped_roof_ft(mesh, -324.0, -93.0, -309.0, -55.0, 9.60, 12.60, terracotta_roof, hip_x_ft=0.0, axis="X", rot_deg=an_rot, pivot=(an_cx, an_cy))

    # --- 3) Damian Center (West End Hall / Gym closing West Quad Axis, Pre-1970) ---
    # Exact N-S orientation (-2.1 deg), X=[-480..-373], Y=[-305..-142], centered on Y=-224
    dm_cx, dm_cy, dm_rot = -426.0, -224.0, -2.1
    # Main 2.5-story rectangular Romanesque block
    _add_rotated_box_ft(mesh, -464.0, -303.0, -384.0, -144.0, 0.05, 8.80, buff_brick, dm_rot, (dm_cx, dm_cy))
    _add_hipped_roof_ft(mesh, -465.5, -304.5, -382.5, -142.5, 8.80, 12.50, terracotta_roof, hip_y_ft=24.0, axis="Y", rot_deg=dm_rot, pivot=(dm_cx, dm_cy))
    # Signature white/gravel flat cruciform center monitor deck (clearly visible in aerial)
    _add_rotated_box_ft(mesh, -442.0, -276.0, -406.0, -172.0, 12.00, 12.55, gravel_roof, dm_rot, (dm_cx, dm_cy))
    _add_rotated_box_ft(mesh, -456.0, -238.0, -392.0, -206.0, 12.00, 12.55, gravel_roof, dm_rot, (dm_cx, dm_cy))
    # Lower East & West perimeter wing bays
    _add_rotated_box_ft(mesh, -478.0, -276.0, -464.0, -172.0, 0.05, 5.20, buff_brick, dm_rot, (dm_cx, dm_cy))
    _add_hipped_roof_ft(mesh, -479.0, -277.0, -463.0, -171.0, 5.20, 6.80, terracotta_roof, hip_y_ft=10.0, axis="Y", rot_deg=dm_rot, pivot=(dm_cx, dm_cy))
    # East Entry Pavilion facing straight down Central Quad Axis (Y=-197 ft)
    _add_rotated_box_ft(mesh, -384.0, -219.0, -373.0, -169.0, 0.05, 9.40, buff_brick, dm_rot, (dm_cx, dm_cy))
    _add_hipped_roof_ft(mesh, -385.0, -220.0, -372.0, -168.0, 9.40, 11.80, terracotta_roof, hip_x_ft=0.0, axis="X", rot_deg=dm_rot, pivot=(dm_cx, dm_cy))

    # --- 4) Aquinas Hall (formerly Major Seminary, immediately East of Library, Pre-1970) ---
    # Exact surveyed 166 x 51 ft 3-story E-W brick bar at X=[+155.5..+321.5], Y=[-41.0..+10.0]
    add_box_m(mesh, m_ft(155.5), m_ft(-41.0), 0.05, m_ft(321.5), m_ft(10.0), 10.40, buff_brick)
    _add_hipped_roof_ft(mesh, 154.0, -42.5, 323.0, 11.5, 10.40, 14.40, terracotta_roof, hip_x_ft=22.0, axis="X")
    # Modern low dark-slate north rear service annex tucked behind Aquinas Hall along bluff
    aq_rear = [(175.0, 10.0), (298.0, 10.0), (298.0, 32.0), (192.0, 54.0), (175.0, 54.0)]
    add_extruded_polygon_ft(mesh, aq_rear, -3.20, 4.80, buff_brick, buff_brick)
    add_extruded_polygon_ft(mesh, aq_rear, 4.80, 5.40, slate_roof, slate_roof)

    # --- 5) Mount Angel Abbey Church, 118-ft Bell Tower & Grand Monastery (Pre-1970) ---
    # Centered dead-on Central Quad Axis Y = -199.0 ft; X = [+226..+490], Y = [-356..-38]

    # Grand 3-Story Monastery N-S Spine (318 ft long: X=416..456, Y=-356..-38)
    add_box_m(mesh, m_ft(416.0), m_ft(-356.0), 0.05, m_ft(456.0), m_ft(-38.0), 11.20, buff_brick)
    _add_hipped_roof_ft(mesh, 414.5, -357.5, 457.5, -36.5, 11.20, 15.20, terracotta_roof, hip_y_ft=20.0, axis="Y")

    # North West-Projecting Monastery Wing (X=370..416, Y=-82..-38)
    add_box_m(mesh, m_ft(370.0), m_ft(-82.0), 0.05, m_ft(416.0), m_ft(-38.0), 11.20, buff_brick)
    _add_hipped_roof_ft(mesh, 368.5, -83.5, 418.0, -36.5, 11.20, 15.20, terracotta_roof, hip_x_ft=18.0, axis="X")
    # North-East Monastery Service Deck / Terrace Return (X=456..490, Y=-80..-38)
    add_box_m(mesh, m_ft(456.0), m_ft(-80.0), 0.05, m_ft(490.0), m_ft(-38.0), 6.20, buff_brick)
    add_box_m(mesh, m_ft(457.5), m_ft(-78.5), 6.20, m_ft(488.5), m_ft(-39.5), 6.45, gravel_roof)

    # South West-Projecting Monastery Wing (X=372..416, Y=-356..-314)
    add_box_m(mesh, m_ft(372.0), m_ft(-356.0), 0.05, m_ft(416.0), m_ft(-314.0), 11.20, buff_brick)
    _add_hipped_roof_ft(mesh, 370.5, -357.5, 418.0, -312.5, 11.20, 15.20, terracotta_roof, hip_x_ft=18.0, axis="X")

    # East Choir / Apse Wing projecting East behind Church Nave (X=456..472, Y=-220..-180)
    add_box_m(mesh, m_ft(456.0), m_ft(-220.0), 0.05, m_ft(472.0), m_ft(-180.0), 10.00, buff_brick)
    _add_hipped_roof_ft(mesh, 455.0, -221.0, 473.0, -179.0, 10.00, 12.80, terracotta_roof, hip_x_ft=6.0, axis="X")

    # Abbey Church Nave (X=252..436, Y=-217..-181, centered on Y=-199 ft)
    add_box_m(mesh, m_ft(252.0), m_ft(-217.0), 0.05, m_ft(436.0), m_ft(-181.0), 13.60, buff_brick)
    _add_hipped_roof_ft(mesh, 250.5, -218.5, 437.5, -179.5, 13.60, 18.40, terracotta_roof, hip_x_ft=0.0, axis="X")
    # West Rose Window / Arched Gable Relief on Church Nave facade
    add_box_m(mesh, m_ft(251.2), m_ft(-205.5), 8.20, m_ft(252.0), m_ft(-192.5), 12.60, copper_roof)

    # Low Side Aisles flanking Church Nave
    add_box_m(mesh, m_ft(252.0), m_ft(-181.0), 0.05, m_ft(416.0), m_ft(-168.0), 7.50, buff_brick)
    _add_hipped_roof_ft(mesh, 251.0, -182.0, 417.0, -167.0, 7.50, 9.50, terracotta_roof, hip_x_ft=0.0, axis="X")
    add_box_m(mesh, m_ft(280.0), m_ft(-230.0), 0.05, m_ft(416.0), m_ft(-217.0), 7.50, buff_brick)
    _add_hipped_roof_ft(mesh, 279.0, -231.0, 417.0, -216.0, 7.50, 9.50, terracotta_roof, hip_x_ft=0.0, axis="X")

    # North & South Transept Chapels (X=310..344)
    add_box_m(mesh, m_ft(310.0), m_ft(-181.0), 0.05, m_ft(344.0), m_ft(-150.0), 10.80, buff_brick)
    _add_hipped_roof_ft(mesh, 309.0, -182.0, 345.0, -149.0, 10.80, 14.40, terracotta_roof, hip_y_ft=0.0, axis="Y")
    add_box_m(mesh, m_ft(310.0), m_ft(-244.0), 0.05, m_ft(344.0), m_ft(-217.0), 10.80, buff_brick)
    _add_hipped_roof_ft(mesh, 309.0, -245.0, 345.0, -216.0, 10.80, 14.40, terracotta_roof, hip_y_ft=0.0, axis="Y")

    # Iconic 118-ft Abbey Bell Tower / Campanile (South-West flank of Nave: X=260..280, Y=-239..-219)
    add_box_m(mesh, m_ft(260.0), m_ft(-239.0), 0.05, m_ft(280.0), m_ft(-219.0), 27.50, buff_brick)
    add_box_m(mesh, m_ft(259.4), m_ft(-239.6), 27.50, m_ft(280.6), m_ft(-218.4), 29.50, buff_brick)
    add_box_m(mesh, m_ft(258.9), m_ft(-236.0), 27.80, m_ft(259.6), m_ft(-222.0), 29.20, road_asphalt)
    # Open 4-Pier Arched Belfry
    add_box_m(mesh, m_ft(260.0), m_ft(-223.5), 29.50, m_ft(264.2), m_ft(-219.0), 33.60, buff_brick)
    add_box_m(mesh, m_ft(275.8), m_ft(-223.5), 29.50, m_ft(280.0), m_ft(-219.0), 33.60, buff_brick)
    add_box_m(mesh, m_ft(260.0), m_ft(-239.0), 29.50, m_ft(264.2), m_ft(-234.5), 33.60, buff_brick)
    add_box_m(mesh, m_ft(275.8), m_ft(-239.0), 29.50, m_ft(280.0), m_ft(-234.5), 33.60, buff_brick)
    add_box_m(mesh, m_ft(263.8), m_ft(-235.0), 29.50, m_ft(276.2), m_ft(-223.0), 33.60, road_asphalt)
    # Belfry Cornice & Pyramidal Terracotta Spire (apex 38.6 m / ~126 ft)
    add_box_m(mesh, m_ft(259.0), m_ft(-240.0), 33.60, m_ft(281.0), m_ft(-218.0), 34.30, buff_brick)
    _add_pyramidal_roof_ft(mesh, 258.4, -240.6, 281.6, -217.4, 34.30, 38.60, terracotta_roof)

    # Wide 1-Story Romanesque Arcaded West Narthex / Cloister Portico (X=226..252, Y=-260..-144)
    # Central Raised Triple-Arch Entry Vestibule (flat parapet roof)
    add_box_m(mesh, m_ft(226.5), m_ft(-219.0), 0.05, m_ft(252.0), m_ft(-179.0), 5.60, buff_brick)
    add_box_m(mesh, m_ft(226.5), m_ft(-219.0), 5.60, m_ft(252.0), m_ft(-179.0), 6.05, buff_brick)
    add_box_m(mesh, m_ft(228.0), m_ft(-217.5), 5.60, m_ft(250.5), m_ft(-180.5), 5.80, gravel_roof)
    add_box_m(mesh, m_ft(225.7), m_ft(-211.0), 0.05, m_ft(226.5), m_ft(-187.0), 4.70, road_asphalt)
    # North Arcaded Portico Wing
    add_box_m(mesh, m_ft(234.0), m_ft(-179.0), 0.05, m_ft(252.0), m_ft(-144.0), 4.30, buff_brick)
    _add_hipped_roof_ft(mesh, 233.0, -180.0, 253.0, -143.0, 4.30, 5.50, terracotta_roof, hip_y_ft=6.0, axis="Y")
    add_box_m(mesh, m_ft(233.3), m_ft(-175.0), 0.05, m_ft(234.0), m_ft(-148.0), 3.70, road_asphalt)
    # South Arcaded Portico Wing
    add_box_m(mesh, m_ft(234.0), m_ft(-260.0), 0.05, m_ft(252.0), m_ft(-219.0), 4.30, buff_brick)
    _add_hipped_roof_ft(mesh, 233.0, -261.0, 253.0, -218.0, 4.30, 5.50, terracotta_roof, hip_y_ft=6.0, axis="Y")
    add_box_m(mesh, m_ft(233.3), m_ft(-256.0), 0.05, m_ft(234.0), m_ft(-223.0), 3.70, road_asphalt)

    # --- 6) Annunciation Hall (SW Quad Seminary Classrooms & Admin, Post-1970) ---
    # Exact surveyed twin linked pavilions rotated +1.8 deg CCW at X=[-364..-138], Y=[-404..-315]
    ann_cx, ann_cy, ann_rot = -250.0, -360.0, 1.8
    # West larger 2-story pavilion (110 x 86 ft)
    _add_rotated_box_ft(mesh, -360.0, -402.0, -252.0, -316.0, 0.05, 7.20, buff_brick, ann_rot, (ann_cx, ann_cy))
    _add_rotated_box_ft(mesh, -360.0, -402.0, -252.0, -316.0, 7.20, 7.80, buff_brick, ann_rot, (ann_cx, ann_cy))
    _add_rotated_box_ft(mesh, -358.0, -400.0, -254.0, -318.0, 7.20, 7.55, gravel_roof, ann_rot, (ann_cx, ann_cy))
    # Subtle roof monitors matching campus_quad_aerial.jpg
    _add_rotated_box_ft(mesh, -342.0, -354.0, -274.0, -334.0, 7.55, 8.65, gravel_roof, ann_rot, (ann_cx, ann_cy))
    _add_rotated_box_ft(mesh, -342.0, -388.0, -296.0, -372.0, 7.55, 8.45, gravel_roof, ann_rot, (ann_cx, ann_cy))
    # Link gallery between West & East pavilions
    _add_rotated_box_ft(mesh, -252.0, -396.0, -224.0, -338.0, 0.05, 6.20, buff_brick, ann_rot, (ann_cx, ann_cy))
    _add_rotated_box_ft(mesh, -251.0, -395.0, -225.0, -339.0, 6.20, 6.50, gravel_roof, ann_rot, (ann_cx, ann_cy))
    # East stepped L-pavilion
    _add_rotated_box_ft(mesh, -224.0, -386.0, -142.0, -350.0, 0.05, 6.80, buff_brick, ann_rot, (ann_cx, ann_cy))
    _add_rotated_box_ft(mesh, -222.5, -384.5, -143.5, -351.5, 6.80, 7.15, gravel_roof, ann_rot, (ann_cx, ann_cy))
    _add_rotated_box_ft(mesh, -172.0, -350.0, -138.0, -318.0, 0.05, 6.80, buff_brick, ann_rot, (ann_cx, ann_cy))
    _add_rotated_box_ft(mesh, -170.5, -350.0, -139.5, -319.5, 6.80, 7.15, gravel_roof, ann_rot, (ann_cx, ann_cy))

    # --- 7) Saint Benedict Guesthouse & Retreat Center (SE Quad, Post-1970) ---
    # Exact surveyed footprint X=[+195..+354], Y=[-446..-391] + West entry plaza
    add_box_m(mesh, m_ft(195.0), m_ft(-445.5), 0.05, m_ft(353.5), m_ft(-404.0), 8.20, buff_brick)
    _add_hipped_roof_ft(mesh, 193.5, -447.0, 355.0, -402.5, 8.20, 10.60, terracotta_roof, hip_x_ft=14.0, axis="X")
    # North projecting entry lobby pavilion facing Quad
    add_box_m(mesh, m_ft(230.0), m_ft(-404.0), 0.05, m_ft(256.5), m_ft(-391.0), 6.20, buff_brick)
    add_box_m(mesh, m_ft(231.0), m_ft(-403.5), 6.20, m_ft(255.5), m_ft(-392.0), 6.50, gravel_roof)
    # Terraced West arrival plaza flanking Retreat Center
    add_extruded_polygon_ft(
        mesh,
        [(138.0, -408.0), (195.0, -408.0), (195.0, -444.0), (138.0, -444.0)],
        0.02, 0.34, walk_paving, walk_edge,
    )

    # --- 8) Abbey Press Building (Far NW Bluff Context, Pre-1970) ---
    # Surveyed bar X=[-556..-396], Y=[+6..+63] trimmed cleanly inside West terrain edge
    add_box_m(mesh, m_ft(-554.0), m_ft(6.5), -1.20, m_ft(-396.5), m_ft(63.0), 4.60, buff_brick)
    _add_hipped_roof_ft(mesh, -555.0, 5.5, -395.5, 64.0, 4.60, 7.60, terracotta_roof, hip_x_ft=12.0, axis="X")

    return grp
