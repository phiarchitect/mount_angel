"""
Layer 4: Level 3 Main Fan Reading Room, Mezzanine Counter, Control Desk & Stacks (`4_Level_3_Reading_Room`).

Constructs Aalto's iconic main reading room at Z = 0.00 m:
  - C-shaped asymmetric fan mezzanine deck framing the open double-height Reading Well
  - Control Area semicircular peninsula (R = 22.8 ft) with open 3-rail dark-bronze tubular
    guardrail (`Angel-090508`) + curved slatted-birch Circulation Control Desk
  - Continuous curved white plaster parapet + raised birch curb + cantilevered matte-black
    linoleum workbench (R = 44.1..46.6 ft) on white steel wall T-brackets, equipped with
    custom parapet-mounted angled-arm white mushroom reading lamps & backless Artek 60 stools
  - 15 radiating double-faced slatted-birch bookstack ranges
  - 20 perimeter study carrel alcoves along North Curtain Wall Bays A-B, B-C, C-D, D-E
  - Periodical Lounge reading group facing the East Mt. Hood Picture Window
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import (
    AaltoGeometry,
    arc_pts,
    get_carrel_alcoves_ft,
    get_h_pier_polygons_ft,
    get_north_perimeter_with_pockets_ft,
    get_radial_bookstacks_ft,
    polar_pt,
)

from .lower_levels import _add_bookstack_range
from .primitives import (
    MATERIALS,
    _clean_ring_2d,
    add_aalto_linear_parapet_lamp,
    add_aalto_parapet_lamp,
    add_arc_band_ft,
    add_artek_stool_60,
    add_counter_wall_bracket,
    add_cylinder_ft,
    add_extruded_polygon_ft,
    add_extruded_polygon_with_holes_ft,
    add_quad,
    add_stepped_stair_ft,
    add_tubular_arc_railing_ft,
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
    xy_m,
)


def _add_sloped_bottom_wall_ft(
    mesh,
    p_in_a: tuple[float, float],
    p_out_a: tuple[float, float],
    p_out_b: tuple[float, float],
    p_in_b: tuple[float, float],
    z_top_m: float,
    z_bot_in_m: float,
    z_bot_out_m: float,
    attrs: dict,
):
    """Build a 100% closed 2-manifold 6-face wall wedge with horizontal top `z_top_m` and sloped bottom."""
    pts_raw = [xy_m(p_in_a), xy_m(p_out_a), xy_m(p_out_b), xy_m(p_in_b)]
    area = 0.0
    for i in range(4):
        x0, y0 = pts_raw[i]
        x1, y1 = pts_raw[(i + 1) % 4]
        area += x0 * y1 - x1 * y0
    if area < 0.0:
        # Swap a <-> b so ring is strictly CCW while preserving in=(0,3) and out=(1,2)
        pts = [pts_raw[3], pts_raw[2], pts_raw[1], pts_raw[0]]
    else:
        pts = pts_raw

    zb = [z_bot_in_m, z_bot_out_m, z_bot_out_m, z_bot_in_m]
    add_quad(mesh, (*pts[0], z_top_m), (*pts[1], z_top_m), (*pts[2], z_top_m), (*pts[3], z_top_m), attrs)
    add_quad(mesh, (*pts[0], zb[0]), (*pts[3], zb[3]), (*pts[2], zb[2]), (*pts[1], zb[1]), attrs)
    for k in range(4):
        kn = (k + 1) % 4
        add_quad(
            mesh,
            (*pts[k], zb[k]),
            (*pts[kn], zb[kn]),
            (*pts[kn], z_top_m),
            (*pts[k], z_top_m),
            attrs,
        )


def _add_l3_stair_bookcase(
    mesh,
    deg: float,
    room_sign: float,
    z_l3: float,
    z_gal: float,
):
    """
    Build Alvar Aalto's counter-height stairwell bookcase & white-plaster stair parapet along
    the radial edge where the Mezzanine stairs descend from Level 3 (`0'-0"`) to the Mezzanine (`-4'-6"`)
    (`mezzaninewithdictionaryweb2`, `Angel-090508`, `Sheet 22-a22 Section B`, `Sheet 30-f2`):
      - Stairwell-facing side: smooth white-plaster parapet + sloped stair-cheek wall + continuous birch cap
      - Level 3 top-floor side: 6-bay, 3-shelf counter-height birch bookcase (`+3'-1"` flat birch counter top
        replacing an open guardrail!)
      - 4 custom parapet-mounted white angled-arm mushroom reading lamps illuminating the bookcase counter.
    """
    G = AaltoGeometry
    rad = math.radians(deg)
    urx, ury = math.cos(rad), math.sin(rad)
    # Unit vector pointing perpendicular to the radial stairwell edge INTO the Level 3 room
    tx, ty = room_sign * (-ury), room_sign * urx
    arm_dir_deg = deg + room_sign * 90.0
    cx, cy = G.WP3A

    def rpt(r_ft: float, t_ft: float) -> tuple[float, float]:
        return (cx + r_ft * urx + t_ft * tx, cy + r_ft * ury + t_ft * ty)

    birch_furn = {**MATERIALS["birch_wood"], "furniture": True}
    book_mats = [
        {**MATERIALS["book_slate"], "furniture": True},
        {**MATERIALS["book_terracotta"], "furniture": True},
        {**MATERIALS["book_ochre"], "furniture": True},
        {**MATERIALS["book_sage"], "furniture": True},
    ]

    r_in = G.R_GALLERY_RAIL          # 22.80 ft (meets curved Control Peninsula bronze guardrail)
    r_out = G.R_MEZZ_OPENING + 0.30  # 44.10 ft (meets outer curved Level 3 workbench parapet)

    # 1. Stairwell-facing white-plaster guardrail backing wall (z = -0.28 .. +0.89 m)
    wall_quad = _clean_ring_2d([rpt(r_in, -0.10), rpt(r_out, -0.10), rpt(r_out, 0.32), rpt(r_in, 0.32)], ccw=True)
    add_extruded_polygon_ft(mesh, wall_quad, z_l3 - 0.28, z_l3 + 0.89, MATERIALS["white_plaster"])

    # Plaster spandrel fascia over Mezzanine end bookcase (R = 22.80..32.25 ft) + sloped stair-cheek infill (R = 32.30..43.75 ft)
    spandrel_quad = _clean_ring_2d([rpt(r_in, -0.10), rpt(32.25, -0.10), rpt(32.25, 0.30), rpt(r_in, 0.30)], ccw=True)
    add_extruded_polygon_ft(mesh, spandrel_quad, z_l3 - 0.42, z_l3 - 0.285, MATERIALS["white_plaster"])
    _add_sloped_bottom_wall_ft(
        mesh,
        rpt(32.30, -0.10),
        rpt(43.75, -0.10),
        rpt(43.75, 0.30),
        rpt(32.30, 0.30),
        z_top_m=z_l3 - 0.285,
        z_bot_in_m=z_gal - 0.20,
        z_bot_out_m=z_l3 - 0.34,
        attrs=MATERIALS["white_plaster"],
    )

    # Continuous raised Birch Curb / Rail Cap matching the curved Level 3 workbench parapet (+0.895 .. +0.99 m)
    cap_quad = _clean_ring_2d([rpt(r_in - 0.15, -0.15), rpt(r_out, -0.15), rpt(r_out, 0.36), rpt(r_in - 0.15, 0.36)], ccw=True)
    add_extruded_polygon_ft(mesh, cap_quad, z_l3 + 0.895, z_l3 + 0.99, MATERIALS["birch_wood"])

    # 2. 6-Bay, 3-Shelf Counter-Height Birch Bookcase facing Level 3 (t = +0.33 .. +1.62 ft, height +0.94 m)
    plinth_quad = _clean_ring_2d([rpt(r_in + 0.05, 0.33), rpt(r_out - 0.05, 0.33), rpt(r_out - 0.05, 1.52), rpt(r_in + 0.05, 1.52)], ccw=True)
    add_extruded_polygon_ft(mesh, plinth_quad, z_l3 + 0.005, z_l3 + 0.09, birch_furn)

    counter_top = _clean_ring_2d([rpt(r_in - 0.05, 0.33), rpt(r_out, 0.33), rpt(r_out, 1.64), rpt(r_in - 0.05, 1.64)], ccw=True)
    add_extruded_polygon_ft(mesh, counter_top, z_l3 + 0.885, z_l3 + 0.94, birch_furn)

    shelf_quad = _clean_ring_2d([rpt(r_in + 0.17, 0.34), rpt(r_out - 0.17, 0.34), rpt(r_out - 0.17, 1.50), rpt(r_in + 0.17, 1.50)], ccw=True)
    for z_sh in (0.35, 0.61):
        add_extruded_polygon_ft(mesh, shelf_quad, z_l3 + z_sh, z_l3 + z_sh + 0.032, birch_furn)

    n_bays = 6
    bay_len = (r_out - 0.10 - (r_in + 0.05)) / n_bays
    for b_i in range(n_bays + 1):
        r_div = (r_in + 0.05) + b_i * bay_len
        div_q = _clean_ring_2d([rpt(r_div, 0.33), rpt(r_div + 0.12, 0.33), rpt(r_div + 0.12, 1.54), rpt(r_div, 1.54)], ccw=True)
        add_extruded_polygon_ft(mesh, div_q, z_l3 + 0.092, z_l3 + 0.883, birch_furn)

    for b_i in range(n_bays):
        ra = (r_in + 0.05) + b_i * bay_len + 0.16
        rb = (r_in + 0.05) + (b_i + 1) * bay_len - 0.04
        bk_q = _clean_ring_2d([rpt(ra, 0.38), rpt(rb, 0.38), rpt(rb, 1.38), rpt(ra, 1.38)], ccw=True)
        for s_tier, (zb0, zb1) in enumerate(((0.095, 0.31), (0.385, 0.58), (0.645, 0.84))):
            add_extruded_polygon_ft(mesh, bk_q, z_l3 + zb0, z_l3 + zb1, book_mats[(b_i + s_tier) % len(book_mats)])

    # 3. 4 Parapet-Mounted Angled-Arm White Mushroom Lamps along the stairwell bookcase cap (`mezzaninewithdictionaryweb2`)
    for r_lamp in (25.4, 30.7, 36.0, 41.3):
        add_aalto_linear_parapet_lamp(mesh, rpt(r_lamp, -0.10), arm_dir_deg=arm_dir_deg, z_floor_m=z_l3)


def _add_wall_mounted_bookcase_ft(
    mesh,
    p0_ft: tuple[float, float],
    p1_ft: tuple[float, float],
    z_floor_m: float,
    height_m: float = 2.12,
):
    """Single-faced 7'-0" birch wall bookcase (`Sheet 30-f2: 10\" x 3'-0\" LIBRARY STACK UNITS MOUNTED AT WALL`)."""
    dx, dy = p1_ft[0] - p0_ft[0], p1_ft[1] - p0_ft[1]
    L = math.hypot(dx, dy)
    if L < 2.0:
        return
    ux, uy = dx / L, dy / L
    # Left normal pointing into reading room when p0 -> p1 runs from PT_LOUNGE_JUNC toward PT_E
    nx, ny = -uy, ux
    birch_furn = {**MATERIALS["birch_wood"], "furniture": True}
    book_mats = [
        {**MATERIALS["book_terracotta"], "furniture": True},
        {**MATERIALS["book_slate"], "furniture": True},
        {**MATERIALS["book_ochre"], "furniture": True},
        {**MATERIALS["book_sage"], "furniture": True},
    ]

    def wpt(s: float, d: float) -> tuple[float, float]:
        return (p0_ft[0] + s * ux + d * nx, p0_ft[1] + s * uy + d * ny)

    # Plinth, canopy top & 5 shelves
    body_q = _clean_ring_2d([wpt(0.0, 0.02), wpt(L, 0.02), wpt(L, 1.02), wpt(0.0, 1.02)], ccw=True)
    add_extruded_polygon_ft(mesh, body_q, z_floor_m + 0.005, z_floor_m + 0.10, birch_furn)
    add_extruded_polygon_ft(mesh, body_q, z_floor_m + height_m - 0.05, z_floor_m + height_m, birch_furn)
    for tier in range(4):
        z_sh = z_floor_m + 0.12 + tier * 0.48
        sh_q = _clean_ring_2d([wpt(0.12, 0.04), wpt(L - 0.12, 0.04), wpt(L - 0.12, 0.98), wpt(0.12, 0.98)], ccw=True)
        add_extruded_polygon_ft(mesh, sh_q, z_sh, z_sh + 0.03, birch_furn)

    n_units = max(2, int(L / 3.2))
    u_len = L / n_units
    for u_i in range(n_units + 1):
        s_d = min(L - 0.12, u_i * u_len)
        st_q = _clean_ring_2d([wpt(s_d, 0.02), wpt(s_d + 0.12, 0.02), wpt(s_d + 0.12, 1.02), wpt(s_d, 1.02)], ccw=True)
        add_extruded_polygon_ft(mesh, st_q, z_floor_m + 0.102, z_floor_m + height_m - 0.052, birch_furn)

    for u_i in range(n_units):
        sa = u_i * u_len + 0.16
        sb = (u_i + 1) * u_len - 0.06
        bk_q = _clean_ring_2d([wpt(sa, 0.06), wpt(sb, 0.06), wpt(sb, 0.88), wpt(sa, 0.88)], ccw=True)
        for tier in range(4):
            z_sh = z_floor_m + 0.155 + tier * 0.48
            add_extruded_polygon_ft(mesh, bk_q, z_sh, z_sh + 0.34, book_mats[(u_i + tier) % len(book_mats)])


def _add_l3_workbench_segment(
    mesh,
    deg0: float,
    deg1: float,
    z_l3: float,
    lamp_degs: list[float],
    steps: int,
):
    """Build a segment of the Level 3 well parapet, birch curb, black linoleum workbench, lamps & stools."""
    G = AaltoGeometry
    r_well_face = G.R_MEZZ_OPENING - 0.35   # 43.45 ft (well-facing plaster face)
    r_room_face = G.R_MEZZ_OPENING + 0.30   # 44.10 ft (reading-room-facing plaster face)
    birch_furn = {**MATERIALS["birch_wood"], "furniture": True}
    lino_furn = {**MATERIALS["black_linoleum"], "furniture": True}

    # White plaster vertical parapet wall + room-side birch baseboard + raised birch book-stop curb
    add_arc_band_ft(mesh, G.WP3A, r_well_face, r_room_face, deg0, deg1, z_l3 - 0.28, z_l3 + 0.89, MATERIALS["white_plaster"], steps=steps)
    add_arc_band_ft(mesh, G.WP3A, r_room_face - 0.02, r_room_face + 0.09, deg0, deg1, z_l3, z_l3 + 0.09, birch_furn, steps=steps)
    add_arc_band_ft(mesh, G.WP3A, r_well_face - 0.05, r_room_face + 0.06, deg0, deg1, z_l3 + 0.89, z_l3 + 0.99, MATERIALS["birch_wood"], steps=steps)

    # Cantilevered Matte-Black Linoleum Workbench + Birch Front Bullnose (R = 44.08..46.65 ft)
    add_arc_band_ft(mesh, G.WP3A, r_room_face - 0.02, G.R_MEZZ_DESK + 0.18, deg0 + 0.15, deg1 - 0.15, z_l3 + 0.70, z_l3 + 0.745, birch_furn, steps=steps)
    add_arc_band_ft(mesh, G.WP3A, r_room_face + 0.03, G.R_MEZZ_DESK + 0.06, deg0 + 0.25, deg1 - 0.25, z_l3 + 0.745, z_l3 + 0.758, lino_furn, steps=steps)

    # Custom parapet-mounted angled-arm white mushroom lamps + under-counter steel T-brackets + Artek 60 stools
    for idx, l_deg in enumerate(lamp_degs):
        add_aalto_parapet_lamp(mesh, G.WP3A, r_well_face_ft=r_well_face, deg=l_deg, z_floor_m=z_l3, inward_sign=1)
        stool_pt = polar_pt(G.WP3A, G.R_MEZZ_DESK + 1.05, l_deg)
        add_artek_stool_60(mesh, stool_pt, z_l3, rot_deg=l_deg + (15.0 if idx % 2 == 0 else -12.0))

    if len(lamp_degs) >= 2:
        step_d = lamp_degs[1] - lamp_degs[0]
        for k in range(len(lamp_degs) + 1):
            b_deg = max(deg0 + 0.8, min(deg1 - 0.8, lamp_degs[0] - 0.5 * step_d + k * step_d))
            add_counter_wall_bracket(mesh, G.WP3A, r_room_face, b_deg, z_l3, seat_sign=1)
    elif len(lamp_degs) == 1:
        add_counter_wall_bracket(mesh, G.WP3A, r_room_face, lamp_degs[0], z_l3, seat_sign=1)


def build_level3_reading_room(scene):
    grp = create_scene_group(scene, "4_Level_3_Reading_Room")
    mesh = grp.mesh
    G = AaltoGeometry
    z_l3 = m_ft(G.Z_L3_FT)              #  0.00 m
    z_gal = m_ft(G.Z_REF_GALLERY_FT)    # -1.37 m (-4'-6" Mezzanine)
    z_lobby = m_ft(G.Z_LOBBY_FT)        # +0.61 m
    birch_furn = {**MATERIALS["birch_wood"], "furniture": True}
    lino_furn = {**MATERIALS["black_linoleum"], "furniture": True}
    slat_furn = {**MATERIALS["hemlock_slat"], "furniture": True}

    # 1. Unified Watertight Level 3 Floorplate (`0'-0"`) pierced by the Annular-Sector Reading Well & Stairwells
    #    (`R = 22.80..43.80 ft`, `41.8°..161.5°`; Sheets 05-a5 & 30-f2)
    deg_well_e, deg_well_w = 41.8, 161.5
    l3_outer_poly = [
        G.PT_A_INNER_JUNC,          # (-77.5, 12.8)
        *get_north_perimeter_with_pockets_ft(level=3),
        G.PT_LOUNGE_JUNC,           # (+51.8, 32.8)
        (51.8, -8.8),               # Periodical Lounge SE corner
        (19.0, -8.8),
        (19.0, -4.5),               # East side of Lobby threshold steps
        (-18.5, -4.5),              # West side of Lobby threshold steps
        (-18.5, -8.8),
        (-77.5, -8.8),
        (-77.5, 1.5),
    ]
    well_hole_poly = [
        *arc_pts(G.WP3A, G.R_MEZZ_OPENING, deg_well_e, deg_well_w, 48),
        *reversed(arc_pts(G.WP3A, G.R_GALLERY_RAIL, deg_well_e, deg_well_w, 32)),
    ]
    add_extruded_polygon_with_holes_ft(
        mesh,
        l3_outer_poly,
        [well_hole_poly],
        z_l3 - 0.28,
        z_l3,
        MATERIALS["floor_oatmeal"],
        MATERIALS["concrete"],
        MATERIALS["white_plaster"],
        MATERIALS["white_plaster"],
    )

    # 2. Upper South Entrance Lobby & West Cataloging Floorplate (Z = +0.61 m / +2'-0")
    south_upper_poly = [
        (-126.5, 1.5),
        (-77.5, 1.5),
        (-77.5, -8.8),
        (-18.5, -8.8),
        (-18.5, -4.5),
        (19.0, -4.5),
        (19.0, -8.8),
        (61.5, -8.8),
        (61.5, -59.5),
        (19.5, -59.5),
        (16.5, -50.8),
        (-91.5, -50.8),
        (-91.5, -28.0),
        (-126.5, -28.0),
    ]
    add_extruded_polygon_ft(
        mesh,
        south_upper_poly,
        z_lobby - 0.32,
        z_lobby,
        MATERIALS["floor_lobby"],
        MATERIALS["concrete"],
    )

    # 3 Wide Entrance Threshold Steps descending from Lobby (+0.61 m) to Control Area (0.00 m)
    add_stepped_stair_ft(mesh, (0.0, -4.5), (0.0, -0.5), width_ft=24.0, z_top_m=z_lobby, z_bot_m=z_l3, n_steps=4)

    # 3. Iconic Level 3 Curved Parapet, Matte-Black Linoleum Workbench, Mushroom Lamps & Artek 60 Stools
    #    Sweeping continuously (`47.9°..155.4°`) between the East & West Mezzanine stair entries (`41.8°..47.9°` & `155.4°..161.5°`)
    main_lamp_degs = [51.2 + i * (101.0 / 15.0) for i in range(16)]
    _add_l3_workbench_segment(mesh, 47.9, 155.4, z_l3, main_lamp_degs, steps=44)

    # 4. Counter-Height Birch Bookcases & Plaster Stair Parapets along East (`41.8°`) & West (`161.5°`) Mezzanine Stairs
    #    (Replacing open railings along both radial stairwell edges; `mezzaninewithdictionaryweb2`, `22-a22`, `30-f2`)
    _add_l3_stair_bookcase(mesh, deg=deg_well_e, room_sign=-1.0, z_l3=z_l3, z_gal=z_gal)
    _add_l3_stair_bookcase(mesh, deg=deg_well_w, room_sign=+1.0, z_l3=z_l3, z_gal=z_gal)

    # 5. Open 3-Rail Dark-Bronze Tubular Guardrail around the Control Peninsula (`Angel-090508`, `mezzaninestairsweb`)
    add_tubular_arc_railing_ft(
        mesh,
        G.WP3A,
        G.R_GALLERY_RAIL - 0.18,
        deg_well_e + 0.3,
        deg_well_w - 0.3,
        z_l3,
        post_step_deg=9.15,
    )

    # 6. Curved Slatted-Birch Circulation Control Desk (under the Slatted Wood Ceiling Drum)
    add_arc_band_ft(
        mesh,
        G.WP_DESK,
        G.R_DESK_INNER,
        G.R_DESK_OUTER,
        28.0,
        162.0,
        z_l3,
        z_l3 + 1.02,
        slat_furn,
        steps=32,
    )
    add_arc_band_ft(
        mesh,
        G.WP_DESK,
        G.R_DESK_INNER - 0.2,
        G.R_DESK_OUTER + 0.25,
        28.0,
        162.0,
        z_l3 + 1.02,
        z_l3 + 1.07,
        lino_furn,
        steps=32,
    )

    # 7. 15 Radiating Double-Faced Birch Bookstack Ranges on Level 3 + SE Wall-Mounted Birch Stack Units (`Sheet 30-f2`)
    for idx, stk in enumerate(get_radial_bookstacks_ft(51.2, 69.0)):
        _add_bookstack_range(mesh, stk, z_l3, height_m=2.12, idx=idx, top_mat_key="birch_wood")

    rad_e = math.radians(G.RAY_E_DEG)
    uxe, uye = math.cos(rad_e), math.sin(rad_e)
    nxe, nye = -uye, uxe
    _add_wall_mounted_bookcase_ft(
        mesh,
        (G.PT_LOUNGE_JUNC[0] + 1.5 * uxe + 0.98 * nxe, G.PT_LOUNGE_JUNC[1] + 1.5 * uye + 0.98 * nye),
        (G.PT_LOUNGE_JUNC[0] + 15.2 * uxe + 0.98 * nxe, G.PT_LOUNGE_JUNC[1] + 15.2 * uye + 0.98 * nye),
        z_l3,
        height_m=2.12,
    )

    # 8. Level 3 Perimeter Study Carrel Partitions & Built-in Birch Desks (tucked cleanly under the +7'-2" clerestory sill!)
    for c_box in get_carrel_alcoves_ft():
        add_wall_strip_ft(mesh, [c_box[0], c_box[3]], 0.35, z_l3 + 0.01, z_l3 + 2.10, MATERIALS["white_plaster"])
        add_wall_strip_ft(mesh, [c_box[1], c_box[2]], 0.35, z_l3 + 0.01, z_l3 + 2.10, MATERIALS["white_plaster"])
        desk_quad = [
            c_box[0],
            c_box[1],
            (0.55 * c_box[1][0] + 0.45 * c_box[2][0], 0.55 * c_box[1][1] + 0.45 * c_box[2][1]),
            (0.55 * c_box[0][0] + 0.45 * c_box[3][0], 0.55 * c_box[0][1] + 0.45 * c_box[3][1]),
        ]
        add_extruded_polygon_ft(mesh, desk_quad, z_l3 + 0.72, z_l3 + 0.78, birch_furn)

    # Built-in Birch Counters tucked inside the 3 interior H-Column reading alcoves (Sheet 05-a5; under HPier_D's eye-level Mt. Hood window!)
    for hp_poly in get_h_pier_polygons_ft(level=3):
        alcove_desk = [
            hp_poly[9],
            hp_poly[8],
            (0.42 * hp_poly[8][0] + 0.58 * hp_poly[7][0], 0.42 * hp_poly[8][1] + 0.58 * hp_poly[7][1]),
            (0.42 * hp_poly[9][0] + 0.58 * hp_poly[10][0], 0.42 * hp_poly[9][1] + 0.58 * hp_poly[10][1]),
        ]
        add_extruded_polygon_ft(mesh, alcove_desk, z_l3 + 0.72, z_l3 + 0.78, birch_furn)

    # 9. Periodical Lounge Reading Tables (East Flank facing Mt. Hood Picture Window)
    for py_ft in (4.0, 15.0, 25.0):
        add_cylinder_ft(mesh, (38.5, py_ft), 2.4, z_l3 + 0.66, z_l3 + 0.72, birch_furn, sides=18)
        add_cylinder_ft(mesh, (38.5, py_ft), 0.35, z_l3, z_l3 + 0.66, birch_furn, sides=10)
        for c_ang in (0, 90, 180, 270):
            sx = 38.5 + 3.4 * math.cos(math.radians(c_ang))
            sy = py_ft + 3.4 * math.sin(math.radians(c_ang))
            add_artek_stool_60(mesh, (sx, sy), z_l3, rot_deg=float(c_ang))

    return grp

