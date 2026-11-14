"""
Layer 4: Level 3 Main Fan Reading Room, Mezzanine Counter, Control Desk & Stacks (`4_Level_3_Reading_Room`).

Constructs Aalto's iconic main reading room at Z = 0.00 m:
  - C-shaped asymmetric fan mezzanine deck cleanly framing the open double-height
    semicircular Reading Well (R = 22.8..43.8 ft)
  - Control Area semicircular peninsula (R = 22.8 ft) + curved slatted-birch Control Desk
  - Continuous curved white plaster mezzanine parapet + birch & matte-black-linoleum
    reading counter (R = 43.8..46.5 ft) with 16 white Aalto dome lamps & Artek stools
  - 15 radiating double-faced birch bookstack ranges
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
    add_arc_band_ft,
    add_cylinder_ft,
    add_extruded_polygon_ft,
    add_frustum_ft,
    add_oriented_box_ft,
    add_stepped_stair_ft,
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
)


def _add_aalto_dome_lamp(mesh, pt_ft: tuple[float, float], z_desk_m: float):
    """Signature white spun-aluminum Aalto reading lamp with brass stem & warm glow."""
    add_cylinder_ft(mesh, pt_ft, 0.22, z_desk_m, z_desk_m + 0.03, MATERIALS["brass"], sides=10)
    add_cylinder_ft(mesh, pt_ft, 0.07, z_desk_m + 0.03, z_desk_m + 0.42, MATERIALS["brass"], sides=8)
    add_frustum_ft(
        mesh,
        pt_ft,
        r0_ft=0.72,
        r1_ft=0.26,
        z0_m=z_desk_m + 0.34,
        z1_m=z_desk_m + 0.50,
        attrs=MATERIALS["lamp_shade"],
        sides=14,
        cap_top=True,
        cap_bottom=True,
    )
    add_cylinder_ft(mesh, pt_ft, 0.48, z_desk_m + 0.33, z_desk_m + 0.35, MATERIALS["lamp_glow"], sides=12)


def _add_artek_stool(mesh, pt_ft: tuple[float, float], z_floor_m: float):
    """Aalto Artek 60 3-legged birch reading stool."""
    add_cylinder_ft(mesh, pt_ft, 0.58, z_floor_m + 0.42, z_floor_m + 0.46, MATERIALS["birch_wood"], sides=12)
    add_cylinder_ft(mesh, pt_ft, 0.52, z_floor_m + 0.46, z_floor_m + 0.475, MATERIALS["black_linoleum"], sides=12)
    for k in range(3):
        ang = 2.0 * math.pi * k / 3.0
        lx = pt_ft[0] + 0.42 * math.cos(ang)
        ly = pt_ft[1] + 0.42 * math.sin(ang)
        add_cylinder_ft(mesh, (lx, ly), 0.08, z_floor_m, z_floor_m + 0.42, MATERIALS["birch_wood"], sides=6)


def build_level3_reading_room(scene):
    grp = create_scene_group(scene, "4_Level_3_Reading_Room")
    mesh = grp.mesh
    G = AaltoGeometry
    z_l3 = m_ft(G.Z_L3_FT)          #  0.00 m
    z_lobby = m_ft(G.Z_LOBBY_FT)    # +0.61 m

    # 1. Outer C-Shaped Fan Mezzanine Floorplate (leaving R = 22.8..43.8 ft Well 100% open!)
    well_outer_arc = arc_pts(G.WP3A, G.R_MEZZ_OPENING, 42.0, 161.0, 38)  # East -> West
    fan_mezz_poly = [
        G.PT_A_INNER_JUNC,          # (-77.5, 12.8)
        *get_north_perimeter_with_pockets_ft(level=3),
        G.PT_LOUNGE_JUNC,           # (+51.8, 32.8)
        (51.8, -8.8),               # Periodical Lounge SE corner
        (19.0, -8.8),
        (19.0, 4.0),
        *well_outer_arc,            # Curves around Mezzanine Well opening from East (42°) to West (161°)
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

    # 4. Iconic Mezzanine Parapet & Continuous Curved Reading Counter (sparing West 155.5° & East 48.5° Stair Openings!)
    # Main central sweep between East Stair (53.5°) and West Stair (150.0°)
    # White plaster vertical parapet wall rising 0.92 m above L3 floor (and extending -0.28 m down slab edge)
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_MEZZ_OPENING - 0.35,
        G.R_MEZZ_OPENING + 0.35,
        53.5,
        150.0,
        z_l3 - 0.28,
        z_l3 + 0.92,
        MATERIALS["white_plaster"],
        steps=42,
    )
    # Birch wood bullnose cap & fascia along top of parapet
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_MEZZ_OPENING - 0.42,
        G.R_MEZZ_OPENING + 0.45,
        53.5,
        150.0,
        z_l3 + 0.92,
        z_l3 + 0.98,
        MATERIALS["birch_wood"],
        steps=42,
    )
    # Continuous cantilevered Birch & Matte-Black-Linoleum Reading Counter (R = 44.1..46.5 ft, Z = +0.73 m)
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_MEZZ_OPENING + 0.30,
        G.R_MEZZ_DESK + 0.35,
        53.8,
        149.7,
        z_l3 + 0.68,
        z_l3 + 0.74,
        MATERIALS["birch_wood"],
        steps=42,
    )
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_MEZZ_OPENING + 0.40,
        G.R_MEZZ_DESK + 0.25,
        54.0,
        149.5,
        z_l3 + 0.74,
        z_l3 + 0.76,
        MATERIALS["black_linoleum"],
        steps=42,
    )

    # 16 Signature Aalto White Dome Lamps & Birch Reading Stools along the Mezzanine Counter
    for i in range(16):
        deg = 57.0 + i * (90.0 / 15.0)
        lamp_pt = polar_pt(G.WP3A, G.R_MEZZ_OPENING + 1.15, deg)
        stool_pt = polar_pt(G.WP3A, G.R_MEZZ_DESK + 1.45, deg)
        _add_aalto_dome_lamp(mesh, lamp_pt, z_l3 + 0.76)
        _add_artek_stool(mesh, stool_pt, z_l3)

    # Guardrails around the Control Peninsula overlooking the Reference Gallery (between 54° and 150°)
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_GALLERY_RAIL - 0.30,
        G.R_GALLERY_RAIL + 0.25,
        54.0,
        150.0,
        z_l3,
        z_l3 + 0.92,
        MATERIALS["white_plaster"],
        steps=32,
    )
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_GALLERY_RAIL - 0.35,
        G.R_GALLERY_RAIL + 0.30,
        54.0,
        150.0,
        z_l3 + 0.92,
        z_l3 + 0.97,
        MATERIALS["birch_wood"],
        steps=32,
    )

    # 5. Curved Slatted-Birch Circulation Control Desk (under the Slatted Wood Ceiling Drum)
    add_arc_band_ft(
        mesh,
        G.WP_DESK,
        G.R_DESK_INNER,
        G.R_DESK_OUTER,
        28.0,
        162.0,
        z_l3,
        z_l3 + 1.02,
        MATERIALS["hemlock_slat"],
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
        MATERIALS["black_linoleum"],
        steps=32,
    )

    # 6. 15 Radiating Double-Faced Birch Bookstack Ranges on Level 3
    for idx, stk in enumerate(get_radial_bookstacks_ft(51.2, 69.0)):
        _add_bookstack_range(mesh, stk, z_l3, height_m=2.12, idx=idx)

    # 7. Level 3 Perimeter Study Carrel Partitions & Built-in Birch Desks
    for c_box in get_carrel_alcoves_ft():
        add_wall_strip_ft(mesh, [c_box[0], c_box[3]], 0.35, z_l3, z_l3 + 2.10, MATERIALS["white_plaster"])
        add_wall_strip_ft(mesh, [c_box[1], c_box[2]], 0.35, z_l3, z_l3 + 2.10, MATERIALS["white_plaster"])
        desk_quad = [
            c_box[0],
            c_box[1],
            (0.55 * c_box[1][0] + 0.45 * c_box[2][0], 0.55 * c_box[1][1] + 0.45 * c_box[2][1]),
            (0.55 * c_box[0][0] + 0.45 * c_box[3][0], 0.55 * c_box[0][1] + 0.45 * c_box[3][1]),
        ]
        add_extruded_polygon_ft(mesh, desk_quad, z_l3 + 0.72, z_l3 + 0.78, MATERIALS["birch_wood"])

    # Built-in Birch Counters tucked inside the 3 interior H-Column reading alcoves (Sheet 05-a5)
    for hp_poly in get_h_pier_polygons_ft(level=3):
        alcove_desk = [
            hp_poly[9],
            hp_poly[8],
            (0.42 * hp_poly[8][0] + 0.58 * hp_poly[7][0], 0.42 * hp_poly[8][1] + 0.58 * hp_poly[7][1]),
            (0.42 * hp_poly[9][0] + 0.58 * hp_poly[10][0], 0.42 * hp_poly[9][1] + 0.58 * hp_poly[10][1]),
        ]
        add_extruded_polygon_ft(mesh, alcove_desk, z_l3 + 0.72, z_l3 + 0.78, MATERIALS["birch_wood"])

    # 8. Periodical Lounge Reading Tables (East Flank facing Mt. Hood Picture Window)
    for py_ft in (4.0, 15.0, 25.0):
        add_cylinder_ft(mesh, (38.5, py_ft), 2.4, z_l3 + 0.66, z_l3 + 0.72, MATERIALS["birch_wood"], sides=18)
        add_cylinder_ft(mesh, (38.5, py_ft), 0.35, z_l3, z_l3 + 0.66, MATERIALS["birch_wood"], sides=10)
        for c_ang in (0, 90, 180, 270):
            sx = 38.5 + 3.4 * math.cos(math.radians(c_ang))
            sy = py_ft + 3.4 * math.sin(math.radians(c_ang))
            _add_artek_stool(mesh, (sx, sy), z_l3)

    return grp
