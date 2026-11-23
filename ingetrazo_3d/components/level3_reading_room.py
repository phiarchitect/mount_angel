"""
Layer 4: Level 3 Main Fan Reading Room, Mezzanine Counter, Control Desk & Stacks (`4_Level_3_Reading_Room`).

Constructs Aalto's iconic main reading room at Z = 0.00 m:
  - C-shaped asymmetric fan mezzanine deck framing the open double-height Reading Well
  - Control Area semicircular peninsula (R = 22.8 ft) with open 3-rail dark-bronze tubular
    guardrail (`Angel-090508`) + curved slatted-birch Circulation Control Desk
  - Continuous curved white plaster parapet + raised birch curb + cantilevered matte-black
    linoleum workbench (R = 44.1..46.6 ft) on white steel wall T-brackets, equipped with
    custom parapet-mounted angled-arm white mushroom reading lamps & backless Artek 60 stools
  - 15 radiating double-faced slatted-birch bookstack ranges with variable lengths & directory stanchions
  - 20 perimeter study carrel alcoves along North Curtain Wall Bays A-B, B-C, C-D, D-E
  - Periodical Lounge reading group facing the East Mt. Hood Picture Window
  - 14-bay glazed partition wall dividing Reading Room from Director's Office 344 & Periodical Room 346
  - West Squiggle Walls: 28°-canted wood-fin screen wall & serpentine Public Catalogue wall with card catalogs
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import (
    AaltoGeometry,
    arc_pts,
    get_carrel_alcoves_ft,
    get_h_pier_polygons_ft,
    get_north_perimeter_with_pockets_ft,
    polar_pt,
)

from .aalto_bookcases import add_aalto_bookcase_ft
from .primitives import (
    MATERIALS,
    _clean_ring_2d,
    add_aalto_linear_parapet_lamp,
    add_aalto_parapet_lamp,
    add_arc_band_ft,
    add_artek_chair_69,
    add_artek_stool_60,
    add_counter_wall_bracket,
    add_cylinder_ft,
    add_extruded_polygon_ft,
    add_extruded_polygon_with_holes_ft,
    add_oriented_box_ft,
    add_quad,
    add_stepped_stair_ft,
    add_tubular_arc_railing_ft,
    add_wall_strip_ft,
    as_concrete,
    create_scene_group,
    m_ft,
    offset_polyline_right_ft,
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
      - Level 3 top-floor side: counter-height birch bookcase (`+3'-1"` flat birch counter top replacing open guardrail)
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

    r_in = G.R_GALLERY_RAIL          # 22'-0" (meets curved Control Peninsula bronze guardrail)
    r_out = G.R_MEZZ_OPENING + 0.30  # 44'-3.6" (meets outer curved Level 3 workbench parapet)

    # 1. Stairwell-facing structural concrete guardrail backing wall (z = -0.28 .. +0.89 m)
    plaster_conc = as_concrete(MATERIALS["white_plaster"])
    wall_quad = _clean_ring_2d([rpt(r_in, -0.10), rpt(r_out, -0.10), rpt(r_out, 0.32), rpt(r_in, 0.32)], ccw=True)
    add_extruded_polygon_ft(mesh, wall_quad, z_l3 - 0.28, z_l3 + 0.89, plaster_conc)

    # Structural spandrel fascia over 3-shelf Mezzanine end bookcase (z = -0.38 .. -0.285 m) + sloped stair-cheek infill
    spandrel_quad = _clean_ring_2d([rpt(r_in, -0.10), rpt(32.25, -0.10), rpt(32.25, 0.30), rpt(r_in, 0.30)], ccw=True)
    add_extruded_polygon_ft(mesh, spandrel_quad, z_l3 - 0.38, z_l3 - 0.285, plaster_conc)
    _add_sloped_bottom_wall_ft(
        mesh,
        rpt(32.30, -0.10),
        rpt(G.R_MEZZ_OPENING, -0.10),
        rpt(G.R_MEZZ_OPENING, 0.30),
        rpt(32.30, 0.30),
        z_top_m=z_l3 - 0.285,
        z_bot_in_m=z_gal - 0.305,
        z_bot_out_m=z_l3 - 0.34,
        attrs=plaster_conc,
    )

    # Continuous raised Birch Curb / Rail Cap matching the curved Level 3 workbench parapet (+0.895 .. +0.99 m)
    cap_quad = _clean_ring_2d([rpt(r_in - 0.15, -0.15), rpt(r_out, -0.15), rpt(r_out, 0.36), rpt(r_in - 0.15, 0.36)], ccw=True)
    add_extruded_polygon_ft(mesh, cap_quad, z_l3 + 0.895, z_l3 + 0.99, MATERIALS["birch_wood"])

    # 2. Counter-Height Birch Bookcase facing Level 3 using add_aalto_bookcase_ft (3 open shelves)
    depth_ft = 1.20
    length_ft = r_out - r_in - 0.20
    r_mid = 0.5 * (r_in + 0.10 + r_out - 0.10)
    t_mid = 0.33 + 0.5 * depth_ft
    c_bookcase = rpt(r_mid, t_mid)
    ang_bc = (deg + 180.0) % 360.0 if room_sign < 0.0 else deg

    add_aalto_bookcase_ft(
        mesh,
        center_ft=c_bookcase,
        length_ft=length_ft,
        depth_ft=depth_ft,
        angle_deg=ang_bc,
        z_floor_m=z_l3,
        height_m=0.935,
        double_sided=False,
        n_shelf_tiers=3,
        canopy_style="counter",
        end_slats="none",
        populate_books=True,
        seed=int(deg * 10),
    )

    # 3. 4 Parapet-Mounted Angled-Arm White Mushroom Lamps along the stairwell bookcase cap (`mezzaninewithdictionaryweb2`)
    for r_lamp in (25.4, 30.7, 36.0, 41.3):
        add_aalto_linear_parapet_lamp(mesh, rpt(r_lamp, -0.10), arm_dir_deg=arm_dir_deg, z_floor_m=z_l3)


def _add_wall_mounted_bookcase_ft(
    mesh,
    z_floor_m: float,
    height_m: float = 2.08,
):
    """Single-faced birch wall bookcase along East Flank wall (`Sheet 30-f2`)."""
    G = AaltoGeometry
    rad_e = math.radians(G.RAY_E_DEG)
    uxe, uye = math.cos(rad_e), math.sin(rad_e)
    nxe, nye = -uye, uxe
    s_start = 1.50
    s_end = 15.00
    length_ft = s_end - s_start  # 13.50 ft
    s_mid = 0.5 * (s_start + s_end)
    depth_ft = 1.15
    # Inset 1.18 ft from wall line so it clears the inner wall face cleanly
    d_mid = 1.18
    c_x = G.PT_LOUNGE_JUNC[0] + s_mid * uxe + d_mid * nxe
    c_y = G.PT_LOUNGE_JUNC[1] + s_mid * uye + d_mid * nye

    add_aalto_bookcase_ft(
        mesh,
        center_ft=(c_x, c_y),
        length_ft=length_ft,
        depth_ft=depth_ft,
        angle_deg=G.RAY_E_DEG,
        z_floor_m=z_floor_m,
        height_m=height_m,
        double_sided=False,
        n_shelf_tiers=6,
        canopy_style="birch",
        end_slats="start",
        populate_books=True,
        seed=42,
    )


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

    # Structural concrete well parapet wall + room-side birch baseboard + raised birch book-stop curb
    add_arc_band_ft(mesh, G.WP3A, r_well_face, r_room_face, deg0, deg1, z_l3 - 0.28, z_l3 + 0.89, as_concrete(MATERIALS["white_plaster"]), steps=steps)
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


def _catmull_rom_chain(ctrl_pts: list[tuple[float, float]], n_sub: int = 3) -> list[tuple[float, float]]:
    """Generate smooth Catmull-Rom spline chain through control points."""
    pts: list[tuple[float, float]] = []
    m = len(ctrl_pts)
    for i in range(m - 1):
        p0 = ctrl_pts[max(0, i - 1)]
        p1 = ctrl_pts[i]
        p2 = ctrl_pts[i + 1]
        p3 = ctrl_pts[min(m - 1, i + 2)]
        for s in range(n_sub if i < m - 2 else n_sub + 1):
            t = s / n_sub
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                (2.0 * p1[0])
                + (-p0[0] + p2[0]) * t
                + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2.0 * p1[1])
                + (-p0[1] + p2[1]) * t
                + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
            )
            pts.append((round(x, 3), round(y, 3)))
    return pts


def build_level3_reading_room(scene):
    grp = create_scene_group(scene, "4_Level_3_Reading_Room")
    mesh = grp.mesh
    G = AaltoGeometry
    z_l3 = m_ft(G.Z_L3_FT)              #  0.00 m (0'-0" / EL. +128'-6")
    z_gal = m_ft(G.Z_REF_GALLERY_FT)    # -1.63 m (-5'-4" / EL. +123'-2" Mezzanine)
    z_lobby = m_ft(G.Z_LOBBY_FT)        # +0.41 m (+1'-4" / EL. +129'-10" Lobby)
    z_s_ceil = m_ft(G.Z_SOUTH_CEIL_FT)  # +3.19 m (+10'-5 1/2" South Wing Ceiling)
    z_wall_top = z_s_ceil - 0.01        # +3.18 m (cleanly flush under South roof slab)

    x_w = G.X_WEST_WING        # -129'-5"
    x_step = G.X_SOUTH_STEP    #  -91'-2"
    x_elev = G.X_ELEV_E        #  -80'-10"
    x_lob_e = G.X_LOBBY_E_G2   #  +17'-6"
    x_aud_sw = G.X_AUD_SW      #  +19'-2"
    x_lng_e = G.X_LOUNGE_E     #  +52'-2"
    x_aud_e = G.X_AUD_E        #  +62'-5"
    y_g6 = G.GRID_Y["6"]       #    0'-0"
    y_g5 = G.GRID_Y["5"]       #   -8'-10"
    y_g4 = G.GRID_Y["4"]       #  -21'-6"
    y_g3 = G.GRID_Y["3"]       #  -29'-0"
    y_g2 = G.GRID_Y["2"]       #  -51'-8"
    y_g1 = G.GRID_Y["1"]       #  -61'-0"

    birch_furn = {**MATERIALS["birch_wood"], "furniture": True}
    lino_furn = {**MATERIALS["black_linoleum"], "furniture": True}
    slat_furn = {**MATERIALS["hemlock_slat"], "furniture": True}
    brass_furn = {**MATERIALS["brass"], "furniture": True}
    plaster_mat = MATERIALS["white_plaster"]
    plaster_conc = as_concrete(MATERIALS["white_plaster"])
    conc_mat = as_concrete(MATERIALS["concrete"])
    glass_mat = MATERIALS["glass_clear"]
    col_mat = MATERIALS["white_column"]

    # 1. Unified Watertight Level 3 Floorplate (`0'-0"`) pierced by the Annular-Sector Reading Well
    deg_well_e, deg_well_w = 41.8, 161.5
    ext_l3_chain = offset_polyline_right_ft(
        [(x_elev, y_g6), G.PT_A_INNER_JUNC, *get_north_perimeter_with_pockets_ft(level=3), G.PT_LOUNGE_JUNC, (x_lng_e, y_g5)],
        0.52,
    )
    x_elev_in = x_elev + 0.52
    l3_outer_poly = [
        *ext_l3_chain[1:-1],
        (x_lng_e - 0.52, y_g5),     # Periodical Lounge SE corner (inset inside East brick wall)
        (18.5, y_g5),
        (18.5, y_g4),               # Extended southward to Grid 4 across Entry Area & Public Catalog
        (x_elev_in, y_g4),
        (x_elev_in, y_g6),
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
        as_concrete(MATERIALS["floor_oatmeal"]),
        conc_mat,
        plaster_conc,
        plaster_conc,
    )

    # Control Peninsula 4" Structural Soffit Lip (`Sheet 13-a13 Detail 9`): drops from -0.28 to -0.38 m
    # right over the top of the 3-shelf curved Mezzanine Reference Bookwall (`top = -0.386 m`)!
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_GALLERY_RAIL - 0.35,
        G.R_GALLERY_RAIL + 0.02,
        deg_well_e,
        deg_well_w,
        z_l3 - 0.38,
        z_l3 - 0.28,
        plaster_conc,
        steps=36,
    )

    # 2. Upper South Entrance Lobby & West Cataloging Floorplate (Z = +0.41 m / +1'-4" / EL. +129'-10")
    y_vest_s = y_g2 - 6.8
    south_upper_poly = [
        (x_elev_in, y_g4),
        (18.5, y_g4),
        (18.5, y_g5),
        (x_aud_e, y_g5),
        (x_aud_e, y_g1),
        (x_aud_sw, y_g1),
        (x_lob_e, y_g2 + 0.5),
        (0.0, y_g2 + 0.5),
        (0.0, y_vest_s),            # South Vestibule 316 projecting pad
        (-18.5, y_vest_s),
        (-18.5, y_g2 + 0.5),
        (x_step, y_g2 + 0.5),
        (x_step, y_g3),
        (x_w, y_g3),
        (x_w, y_g6),
        (x_elev_in, y_g6),
    ]
    add_extruded_polygon_ft(
        mesh,
        south_upper_poly,
        z_lobby - 0.32,
        z_lobby,
        as_concrete(MATERIALS["floor_lobby"]),
        conc_mat,
    )

    # 0.50 ft Concrete riser apron spanning z_l3 .. z_lobby - 0.32 (+0.086 m) to seal floor step
    add_wall_strip_ft(
        mesh,
        [(x_elev_in, y_g4), (18.5, y_g4), (18.5, y_g5)],
        0.50,
        z_l3,
        z_lobby - 0.32,
        conc_mat,
    )

    # Wide Lobby -> Entry Area threshold steps (`Sheet 13-a13 Detail 15`: 3 risers = 1'-4"!)
    add_stepped_stair_ft(
        mesh,
        (-0.25, y_g4),
        (-0.25, y_g4 + 3.2),
        width_ft=33.0,
        z_top_m=z_lobby,
        z_bot_m=z_l3,
        n_steps=3,
        tread_attrs=birch_furn,
        concrete_struct=True,
    )

    # Aalto curved central brass threshold arc band at Entry Area
    add_arc_band_ft(
        mesh,
        (-0.25, y_g3),
        9.8,
        10.2,
        70.0,
        110.0,
        z_l3,
        z_l3 + 0.015,
        brass_furn,
        steps=16,
    )

    # 3. Iconic Level 3 Curved Parapet, Matte-Black Linoleum Workbench, Mushroom Lamps & Artek 60 Stools
    #    Sweeping continuously (`47.9°..155.4°`) between the East & West Mezzanine stair entries
    main_lamp_degs = [51.2 + i * (101.0 / 15.0) for i in range(16)]
    _add_l3_workbench_segment(mesh, 47.9, 155.4, z_l3, main_lamp_degs, steps=44)

    # 4. Counter-Height Birch Bookcases & Plaster Stair Parapets along East (`41.8°`) & West (`161.5°`) Mezzanine Stairs
    _add_l3_stair_bookcase(mesh, deg=deg_well_e, room_sign=-1.0, z_l3=z_l3, z_gal=z_gal)
    _add_l3_stair_bookcase(mesh, deg=deg_well_w, room_sign=+1.0, z_l3=z_l3, z_gal=z_gal)

    # 5. Open 3-Rail Dark-Bronze Tubular Guardrail around the Control Peninsula (`Angel-090508`, `13-a13` Det. 9)
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

    # 7. 15 Radiating Double-Faced Birch Bookstack Ranges on Level 3 (6 open shelves per `obs_04_bookcase_photo.jpg`)
    #    Angles synced to vectors.py so every stack cleanly flanks true Rays B (137.0°), C (99.4°), D (64.5°)
    r_start = 51.5
    r_ends = [69.0, 70.6, 72.2, 69.5, 71.8, 72.6, 71.2, 69.4, 70.0, 72.2, 72.6, 70.6, 68.8, 71.2, 72.0]
    stack_angles = [
        159.0, 153.2, 147.8,
        132.5, 126.6, 120.8, 115.0, 109.2,
        93.4, 86.4, 79.4, 72.4,
        56.5, 50.5, 44.5,
    ]
    for idx, (deg, r_end) in enumerate(zip(stack_angles, r_ends)):
        rad = math.radians(deg)
        ux, uy = math.cos(rad), math.sin(rad)
        l_stack = r_end - r_start
        r_mid = 0.5 * (r_start + r_end)
        c_stk = (G.WP3A[0] + r_mid * ux, G.WP3A[1] + r_mid * uy)
        add_aalto_bookcase_ft(
            mesh,
            center_ft=c_stk,
            length_ft=l_stack,
            depth_ft=2.70,
            angle_deg=deg,
            z_floor_m=z_l3,
            height_m=2.08,
            double_sided=True,
            n_shelf_tiers=6,
            canopy_style="birch",
            end_slats="start",
            populate_books=True,
            seed=idx,
        )

    # East Flank Wall-Mounted Birch Stack Units (`Sheet 30-f2`)
    _add_wall_mounted_bookcase_ft(mesh, z_l3, height_m=2.08)

    # 8. Level 3 Perimeter Study Carrel Partitions & Built-in Birch Desks (tucked cleanly under the +8'-4" clerestory sill!)
    for c_box in get_carrel_alcoves_ft():
        add_wall_strip_ft(mesh, [c_box[0], c_box[3]], 0.35, z_l3 + 0.01, z_l3 + 2.10, plaster_mat)
        add_wall_strip_ft(mesh, [c_box[1], c_box[2]], 0.35, z_l3 + 0.01, z_l3 + 2.10, plaster_mat)
        desk_quad = [
            c_box[0],
            c_box[1],
            (0.55 * c_box[1][0] + 0.45 * c_box[2][0], 0.55 * c_box[1][1] + 0.45 * c_box[2][1]),
            (0.55 * c_box[0][0] + 0.45 * c_box[3][0], 0.55 * c_box[0][1] + 0.45 * c_box[3][1]),
        ]
        add_extruded_polygon_ft(mesh, desk_quad, z_l3 + 0.72, z_l3 + 0.78, birch_furn)

    # Built-in Birch Counters tucked inside the 3 interior H-Column reading alcoves (under HPier_D's eye-level Mt. Hood window!)
    for hp_poly in get_h_pier_polygons_ft(level=3):
        alcove_desk = [
            hp_poly[9],
            hp_poly[8],
            (0.42 * hp_poly[8][0] + 0.58 * hp_poly[7][0], 0.42 * hp_poly[8][1] + 0.58 * hp_poly[7][1]),
            (0.42 * hp_poly[9][0] + 0.58 * hp_poly[10][0], 0.42 * hp_poly[9][1] + 0.58 * hp_poly[10][1]),
        ]
        add_extruded_polygon_ft(mesh, alcove_desk, z_l3 + 0.72, z_l3 + 0.78, birch_furn)

    # 9. Periodical Lounge Reading Tables (East Flank facing Mt. Hood Picture Window)
    for py_ft in (4.0, 15.0, 26.0):
        add_cylinder_ft(mesh, (39.0, py_ft), 2.4, z_l3 + 0.66, z_l3 + 0.72, birch_furn, sides=18)
        add_cylinder_ft(mesh, (39.0, py_ft), 0.35, z_l3, z_l3 + 0.66, birch_furn, sides=10)
        for c_ang in (0, 90, 180, 270):
            sx = 39.0 + 3.4 * math.cos(math.radians(c_ang))
            sy = py_ft + 3.4 * math.sin(math.radians(c_ang))
            add_artek_stool_60(mesh, (sx, sy), z_l3, rot_deg=float(c_ang))

    # 10. 14-Bay Repeating Birch-Framed Glazed Partition Wall (PT_EAST_THROAT -> PT_LOUNGE_JUNC)
    p_gl0 = G.PT_EAST_THROAT
    p_gl1 = G.PT_LOUNGE_JUNC
    dx_gl = p_gl1[0] - p_gl0[0]
    dy_gl = p_gl1[1] - p_gl0[1]
    l_gl = math.hypot(dx_gl, dy_gl)
    ux_gl, uy_gl = dx_gl / l_gl, dy_gl / l_gl
    ang_gl = math.degrees(math.atan2(dy_gl, dx_gl))

    # Continuous head rail & upper plaster spandrel bulkhead (flush under South ceiling `z_wall_top`)
    c_mid_gl = (p_gl0[0] + 0.5 * dx_gl, p_gl0[1] + 0.5 * dy_gl)
    add_oriented_box_ft(mesh, c_mid_gl, l_gl, 0.38, ang_gl, 2.58, 2.70, birch_furn)
    add_oriented_box_ft(mesh, c_mid_gl, l_gl, 0.42, ang_gl, 2.70, z_wall_top, plaster_mat)

    n_bays_gl = 14
    w_bay_gl = l_gl / n_bays_gl
    t_mul = 0.16
    d_mul = 0.38

    for k in range(n_bays_gl + 1):
        s_k = max(t_mul * 0.5, min(l_gl - t_mul * 0.5, k * w_bay_gl))
        pt_k = (p_gl0[0] + s_k * ux_gl, p_gl0[1] + s_k * uy_gl)
        z_bot = 0.00 if k in (1, 2, 5, 6) else 0.86
        add_oriented_box_ft(mesh, pt_k, t_mul, d_mul, ang_gl, z_bot, 2.58, birch_furn)

    for i in range(n_bays_gl):
        s_a = i * w_bay_gl + t_mul * 0.5
        s_b = (i + 1) * w_bay_gl - t_mul * 0.5
        w_open = s_b - s_a
        s_c = (s_a + s_b) * 0.5
        pt_c = (p_gl0[0] + s_c * ux_gl, p_gl0[1] + s_c * uy_gl)

        if i in (1, 5):
            w_stile = 0.38
            pt_s0 = (p_gl0[0] + (s_a + w_stile * 0.5) * ux_gl, p_gl0[1] + (s_a + w_stile * 0.5) * uy_gl)
            pt_s1 = (p_gl0[0] + (s_b - w_stile * 0.5) * ux_gl, p_gl0[1] + (s_b - w_stile * 0.5) * uy_gl)
            add_oriented_box_ft(mesh, pt_s0, w_stile, 0.14, ang_gl, 0.00, 2.13, birch_furn)
            add_oriented_box_ft(mesh, pt_s1, w_stile, 0.14, ang_gl, 0.00, 2.13, birch_furn)
            w_mid = w_open - 2.0 * w_stile
            add_oriented_box_ft(mesh, pt_c, w_mid, 0.14, ang_gl, 0.00, 0.30, birch_furn)
            add_oriented_box_ft(mesh, pt_c, w_mid, 0.14, ang_gl, 1.98, 2.13, birch_furn)
            add_oriented_box_ft(mesh, pt_c, w_mid, 0.06, ang_gl, 0.30, 1.98, glass_mat)
            add_oriented_box_ft(mesh, pt_c, w_open, 0.22, ang_gl, 2.13, 2.20, birch_furn)
            add_oriented_box_ft(mesh, pt_c, w_open, 0.06, ang_gl, 2.20, 2.58, glass_mat)
        else:
            add_oriented_box_ft(mesh, pt_c, w_open, 0.38, ang_gl, 0.00, 0.10, lino_furn)
            add_oriented_box_ft(mesh, pt_c, w_open, 0.38, ang_gl, 0.10, 0.81, plaster_mat)
            add_oriented_box_ft(mesh, pt_c, w_open, 0.44, ang_gl, 0.81, 0.86, lino_furn)
            add_oriented_box_ft(mesh, pt_c, w_open, 0.08, ang_gl, 0.86, 2.58, glass_mat)

    # Interior walls of Director's Office 344 and Periodical Room 346
    add_wall_strip_ft(mesh, [(26.2, 12.6), (39.8, -5.0)], 0.42, 0.00, z_wall_top, plaster_mat)
    add_wall_strip_ft(
        mesh,
        [G.PT_EAST_THROAT, (16.4, 1.4), (17.2, -0.8), (18.2, -2.8), (19.2, -5.0)],
        0.45,
        0.00,
        z_wall_top,
        plaster_mat,
    )
    add_wall_strip_ft(mesh, [(19.2, -5.0), (42.8, -5.0)], 0.45, 0.00, z_wall_top, plaster_mat)
    add_wall_strip_ft(mesh, [(46.3, -5.0), (x_lng_e - 0.6, -5.0)], 0.45, 0.00, z_wall_top, plaster_mat)
    add_wall_strip_ft(mesh, [(42.8, -5.0), (46.3, -5.0)], 0.45, 2.15, z_wall_top, plaster_mat)

    # Executive desk & Artek 69 chairs inside Director's Office 344
    desk_center = (23.6, 1.2)
    add_oriented_box_ft(mesh, desk_center, 5.5, 3.0, ang_gl, 0.72, 0.76, birch_furn)
    add_oriented_box_ft(mesh, desk_center, 5.1, 2.6, ang_gl, 0.76, 0.765, lino_furn)
    for d_s in (-2.0, 2.0):
        ped_pt = (desk_center[0] + d_s * ux_gl, desk_center[1] + d_s * uy_gl)
        add_oriented_box_ft(mesh, ped_pt, 1.2, 2.6, ang_gl, 0.00, 0.72, birch_furn)
    add_artek_chair_69(mesh, (desk_center[0] - 2.8 * (-uy_gl), desk_center[1] - 2.8 * ux_gl), ang_gl + 90.0, 0.00)
    add_artek_chair_69(mesh, (desk_center[0] + 2.8 * (-uy_gl), desk_center[1] + 2.8 * ux_gl), ang_gl - 90.0, 0.00)

    # 11. West Squiggle Walls: 28-deg Canted Wood-Fin Screen Wall
    p_sc0 = (-17.6, y_g4 + 3.5)
    p_sc1 = G.PT_WEST_THROAT
    dx_sc = p_sc1[0] - p_sc0[0]
    dy_sc = p_sc1[1] - p_sc0[1]
    l_sc = math.hypot(dx_sc, dy_sc)
    ux_sc, uy_sc = dx_sc / l_sc, dy_sc / l_sc
    wall_ang_sc = math.degrees(math.atan2(dy_sc, dx_sc))
    c_sc = (0.5 * (p_sc0[0] + p_sc1[0]), 0.5 * (p_sc0[1] + p_sc1[1]))

    add_oriented_box_ft(mesh, c_sc, l_sc, 0.22, wall_ang_sc, 0.00, 2.82, MATERIALS["railing_bronze"])
    add_oriented_box_ft(mesh, c_sc, l_sc, 0.35, wall_ang_sc, 2.82, z_wall_top, plaster_mat)

    n_fins = 18
    fin_step = l_sc / n_fins
    for j in range(n_fins):
        s_j = (j + 0.5) * fin_step
        pt_j = (p_sc0[0] + s_j * ux_sc, p_sc0[1] + s_j * uy_sc)
        add_oriented_box_ft(mesh, pt_j, 0.75, 0.12, wall_ang_sc + 28.0, 0.05, 2.82, slat_furn)

    # 12. Serpentine S-Curved Public Catalogue Plaster Wall terminating at Well_W_South
    ctrl_pts = [
        (-44.0, y_g4 + 0.4),
        (-44.0, -11.2),
        (-42.2, -5.2),
        (-39.0, -1.2),
        (-37.2, -0.4),
        (-33.8, 1.0),
        G.WELL_COLS_FT["Well_W_South"],
    ]
    spline_pts = _catmull_rom_chain(ctrl_pts, n_sub=3)
    add_wall_strip_ft(mesh, spline_pts, 0.42, 0.00, z_wall_top, plaster_mat)

    # White steel pipe column along serpentine curve
    add_cylinder_ft(mesh, (-37.2, -0.4), 0.18, 0.00, z_wall_top, col_mat, sides=14)

    # Card-Catalog Cabinets on Tapered Legs inside PUBLIC CATALOGUE 320
    catalog_islands = [
        (-34.2, -8.2, 0.0),
        (-26.5, -8.2, 0.0),
        (-30.5, -14.8, 0.0),
    ]
    for cx_c, cy_c, rot_c in catalog_islands:
        c_pt = (cx_c, cy_c)
        for dx_leg in (-2.4, 2.4):
            for dy_leg in (-0.85, 0.85):
                add_cylinder_ft(mesh, (cx_c + dx_leg, cy_c + dy_leg), 0.10, 0.00, 0.42, birch_furn, sides=8)
        add_oriented_box_ft(mesh, c_pt, 5.2, 1.9, rot_c, 0.35, 0.42, birch_furn)
        add_oriented_box_ft(mesh, c_pt, 5.8, 2.3, rot_c, 0.42, 1.22, birch_furn)
        add_oriented_box_ft(mesh, c_pt, 6.0, 2.45, rot_c, 1.22, 1.25, birch_furn)

    # 13. Hook for south_wing_interiors.py
    try:
        from .south_wing_interiors import populate_south_wing_interiors
        populate_south_wing_interiors(mesh)
    except (ImportError, ModuleNotFoundError):
        pass

    return grp
