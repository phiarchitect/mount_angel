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
    add_aalto_parapet_lamp,
    add_arc_band_ft,
    add_artek_stool_60,
    add_counter_wall_bracket,
    add_cylinder_ft,
    add_extruded_polygon_ft,
    add_stepped_stair_ft,
    add_tubular_arc_railing_ft,
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
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
    z_l3 = m_ft(G.Z_L3_FT)          #  0.00 m
    z_lobby = m_ft(G.Z_LOBBY_FT)    # +0.61 m
    birch_furn = {**MATERIALS["birch_wood"], "furniture": True}
    lino_furn = {**MATERIALS["black_linoleum"], "furniture": True}
    slat_furn = {**MATERIALS["hemlock_slat"], "furniture": True}

    # 1. Outer C-Shaped Fan Mezzanine Floorplate (leaving R = 22.8..43.8 ft Well 100% open!)
    well_outer_arc = arc_pts(G.WP3A, G.R_MEZZ_OPENING, 37.5, 164.2, 44)  # East -> West
    fan_mezz_poly = [
        G.PT_A_INNER_JUNC,          # (-77.5, 12.8)
        *get_north_perimeter_with_pockets_ft(level=3),
        G.PT_LOUNGE_JUNC,           # (+51.8, 32.8)
        (51.8, -8.8),               # Periodical Lounge SE corner
        (19.0, -8.8),
        (19.0, 4.0),
        *well_outer_arc,            # Curves around Mezzanine Well opening from East (37.5°) to West (164.2°)
        (-45.0, 4.5),
        (-77.5, 1.5),
    ]
    add_extruded_polygon_ft(
        mesh,
        fan_mezz_poly,
        z_l3 - 0.28,
        z_l3,
        MATERIALS["floor_oatmeal"],
        MATERIALS["white_plaster"],
    )

    # 2. Control Area Peninsula (Z = 0.00 m) projecting out to Semicircular Gallery Edge (R = 22.8 ft)
    peninsula_arc = list(reversed(arc_pts(G.WP3A, G.R_GALLERY_RAIL, 35.0, 166.0, 28)))
    control_poly = [
        (-77.5, -8.8),
        (-77.5, 1.5),
        (-45.0, 4.5),
        *peninsula_arc,
        (19.0, 4.0),
        (19.0, -8.8),
    ]
    add_extruded_polygon_ft(
        mesh,
        control_poly,
        z_l3 - 0.28,
        z_l3,
        MATERIALS["floor_oatmeal"],
        MATERIALS["white_plaster"],
    )

    # 3. Upper South Entrance Lobby & West Cataloging Floorplate (Z = +0.61 m / +2'-0")
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

    # 4. Iconic Level 3 Parapet, Matte-Black Linoleum Workbench, Custom Mushroom Lamps & Artek 60 Stools
    #    - Main central sweep (48.2°..155.3°) between East & West upper stair openings: 16 lamps & 16 stools
    main_lamp_degs = [51.4 + i * (100.6 / 15.0) for i in range(16)]
    _add_l3_workbench_segment(mesh, 48.2, 155.3, z_l3, main_lamp_degs, steps=44)

    #    - Flanking East segment beyond East stair opening (37.5°..42.6°, `Angel-090508` background)
    _add_l3_workbench_segment(mesh, 37.5, 42.6, z_l3, [39.0, 41.4], steps=6)

    #    - Flanking West segment beyond West stair opening (160.8°..164.2°)
    _add_l3_workbench_segment(mesh, 160.8, 164.2, z_l3, [162.5], steps=5)

    # 5. Open 3-Rail Dark-Bronze Tubular Guardrail around the Control Peninsula (`Angel-090508`, `mezzaninestairsweb`)
    add_tubular_arc_railing_ft(
        mesh,
        G.WP3A,
        G.R_GALLERY_RAIL - 0.18,
        41.0,
        162.0,
        z_l3,
        post_step_deg=9.3,
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

    # 7. 15 Radiating Double-Faced Birch Bookstack Ranges on Level 3
    for idx, stk in enumerate(get_radial_bookstacks_ft(51.2, 69.0)):
        _add_bookstack_range(mesh, stk, z_l3, height_m=2.12, idx=idx, top_mat_key="birch_wood")

    # 8. Level 3 Perimeter Study Carrel Partitions & Built-in Birch Desks
    for c_box in get_carrel_alcoves_ft():
        add_wall_strip_ft(mesh, [c_box[0], c_box[3]], 0.35, z_l3, z_l3 + 2.10, MATERIALS["white_plaster"])
        add_wall_strip_ft(mesh, [c_box[1], c_box[2]], 0.35, z_l3, z_l3 + 2.10, MATERIALS["white_plaster"])
        desk_quad = [
            c_box[0],
            c_box[1],
            (0.55 * c_box[1][0] + 0.45 * c_box[2][0], 0.55 * c_box[1][1] + 0.45 * c_box[2][1]),
            (0.55 * c_box[0][0] + 0.45 * c_box[3][0], 0.55 * c_box[0][1] + 0.45 * c_box[3][1]),
        ]
        add_extruded_polygon_ft(mesh, desk_quad, z_l3 + 0.72, z_l3 + 0.78, birch_furn)

    # Built-in Birch Counters tucked inside the 3 interior H-Column reading alcoves (Sheet 05-a5)
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

