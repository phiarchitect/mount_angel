"""
Layers 2 & 3: Lower Hillside Tiers (`2_Level_1_Base` & `3_Level_2_Middle`).

  - Level 1 (-26'-6" / -8.08 m): Downhill fan stack floorplate, 5-sided interior
    reinforced-concrete core retaining wall, and radial archival bookstacks.
  - Level 2 (-12'-6" / -3.81 m): Main lower reading & stack floorplate, curved
    R = 31'-10" birch reference bookwall, perimeter study carrel alcoves & desks,
    radial bookstacks, Semicircular Reference Gallery (-4'-6" / -1.37 m) with
    pipe railing, and West & East stepped radial flanking well stairs!
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import (
    AaltoGeometry,
    arc_pts,
    get_carrel_alcoves_ft,
    get_l1_inner_pentagon_ft,
    get_level1_envelope_ft,
    get_level2_envelope_ft,
    get_radial_bookstacks_ft,
    polar_pt,
)

from .primitives import (
    MATERIALS,
    add_arc_band_ft,
    add_cylinder_ft,
    add_extruded_polygon_ft,
    add_oriented_box_ft,
    add_stepped_stair_ft,
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
)


def _add_bookstack_range(mesh, quad_ft: list[tuple[float, float]], z_floor_m: float, height_m: float = 2.15, idx: int = 0):
    """Build an Aalto birch-slat double-faced bookstack range with shelves and book blocks."""
    wood_side = {**MATERIALS["birch_wood"], "furniture": True}
    wood_top = {**MATERIALS["hemlock_slat"], "furniture": True}
    add_extruded_polygon_ft(mesh, quad_ft, z_floor_m, z_floor_m + height_m, wood_side, wood_top)
    # Colorful muted book band inset slightly at mid-height
    cx = sum(p[0] for p in quad_ft) * 0.25
    cy = sum(p[1] for p in quad_ft) * 0.25
    inset = [(cx + (p[0] - cx) * 0.92, cy + (p[1] - cy) * 0.92) for p in quad_ft]
    book_mats = [
        MATERIALS["book_terracotta"],
        MATERIALS["book_slate"],
        MATERIALS["book_ochre"],
        MATERIALS["book_sage"],
    ]
    bmat = {**book_mats[idx % len(book_mats)], "furniture": True}
    for tier in range(3):
        zb = z_floor_m + 0.32 + tier * 0.58
        add_extruded_polygon_ft(mesh, inset, zb, zb + 0.36, bmat)


def build_lower_levels(scene):
    G = AaltoGeometry
    z_l1 = m_ft(G.Z_L1_FT)              # -8.08 m
    z_l2 = m_ft(G.Z_L2_FT)              # -3.81 m
    z_gal = m_ft(G.Z_REF_GALLERY_FT)    # -1.37 m
    z_l3 = m_ft(G.Z_L3_FT)              #  0.00 m

    # =========================================================================
    # LAYER 2: LEVEL 1 DOWNHILL BASE (-8.08 m)
    # =========================================================================
    grp_l1 = create_scene_group(scene, "2_Level_1_Base")
    m1 = grp_l1.mesh

    # Level 1 Structural Concrete Slab
    add_extruded_polygon_ft(
        m1,
        get_level1_envelope_ft(),
        z_l1 - 0.38,
        z_l1,
        MATERIALS["floor_lower"],
        MATERIALS["concrete"],
    )

    # 5-Sided Interior Reinforced-Concrete Retaining Wall along Well Columns
    pent = get_l1_inner_pentagon_ft()
    add_wall_strip_ft(m1, pent, 1.25, z_l1, z_l2 - 0.28, MATERIALS["concrete"])
    # South retaining wall closing Level 1 core along Grid 6
    add_wall_strip_ft(
        m1,
        [(-67.5, 10.2), G.WELL_COLS_FT["Well_W_South"], (10.5, 0.5), G.WELL_COLS_FT["Well_4_ENE"], (43.5, 24.5)],
        1.20,
        z_l1,
        z_l2 - 0.28,
        MATERIALS["concrete"],
    )

    # Level 1 Archival Radial Bookstacks
    for idx, stk in enumerate(get_radial_bookstacks_ft(38.5, 70.5)):
        _add_bookstack_range(m1, stk, z_l1, height_m=2.20, idx=idx)

    # =========================================================================
    # LAYER 3: LEVEL 2 STACKS, WELL, GALLERY & STAIRS (-3.81 m & -1.37 m)
    # =========================================================================
    grp_l2 = create_scene_group(scene, "3_Level_2_Middle")
    m2 = grp_l2.mesh

    # Level 2 Concrete Floor Slab (-3.81 m)
    add_extruded_polygon_ft(
        m2,
        get_level2_envelope_ft(),
        z_l2 - 0.30,
        z_l2,
        MATERIALS["floor_oatmeal"],
        MATERIALS["concrete"],
    )

    # South Retaining Wall of Level 2 along Grid 4 (Y = -21.0) & West Bindery
    add_wall_strip_ft(
        m2,
        [(61.5, -8.8), (61.5, -21.0), (-91.5, -21.0), (-91.5, -28.0), (-126.5, -28.0), (-126.5, 1.5)],
        1.10,
        z_l2,
        z_l3 - 0.25,
        MATERIALS["concrete"],
    )

    # Curved R = 31'-10" Birch Reference Bookwall tucked beneath the Semicircular Gallery
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_WELL_L2_WALL - 1.4,
        G.R_WELL_L2_WALL + 0.2,
        52.0,
        151.0,
        z_l2,
        z_gal - 0.22,
        MATERIALS["birch_wood"],
        steps=32,
    )
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_WELL_L2_WALL - 1.6,
        G.R_WELL_L2_WALL - 1.25,
        53.0,
        150.0,
        z_l2 + 0.35,
        z_l2 + 1.85,
        MATERIALS["book_slate"],
        steps=32,
    )

    # Level 2 Reading Tables in the Sunken Well (radial birch study tables)
    for t_deg in (68.0, 90.0, 112.0, 134.0):
        pt_t = polar_pt(G.WP3A, 22.0, t_deg)
        add_oriented_box_ft(m2, pt_t, 7.5, 3.6, t_deg, z_l2 + 0.68, z_l2 + 0.76, MATERIALS["birch_wood"])
        add_oriented_box_ft(m2, pt_t, 7.1, 3.2, t_deg, z_l2 + 0.76, z_l2 + 0.78, MATERIALS["black_linoleum"])
        for s_off in (-2.4, 2.4):
            leg = polar_pt(G.WP3A, 22.0 + s_off, t_deg)
            add_cylinder_ft(m2, leg, 0.25, z_l2, z_l2 + 0.68, MATERIALS["birch_wood"], sides=10)

    # Level 2 Perimeter Study Carrel Partitions & Birch Desks (20 alcoves along Bays A-B..D-E)
    for c_box in get_carrel_alcoves_ft():
        # Partition side dividers & built-in birch desk surface
        add_wall_strip_ft(m2, [c_box[0], c_box[3]], 0.35, z_l2, z_l2 + 2.05, MATERIALS["white_plaster"])
        add_wall_strip_ft(m2, [c_box[1], c_box[2]], 0.35, z_l2, z_l2 + 2.05, MATERIALS["white_plaster"])
        desk_quad = [
            c_box[0],
            c_box[1],
            (0.55 * c_box[1][0] + 0.45 * c_box[2][0], 0.55 * c_box[1][1] + 0.45 * c_box[2][1]),
            (0.55 * c_box[0][0] + 0.45 * c_box[3][0], 0.55 * c_box[0][1] + 0.45 * c_box[3][1]),
        ]
        add_extruded_polygon_ft(m2, desk_quad, z_l2 + 0.70, z_l2 + 0.76, MATERIALS["birch_wood"])

    # Level 2 Radial Bookstack Ranges
    for idx, stk in enumerate(get_radial_bookstacks_ft(46.0, 68.5)):
        _add_bookstack_range(m2, stk, z_l2, height_m=2.15, idx=idx + 1)

    # =========================================================================
    # INTERMEDIATE SEMICIRCULAR REFERENCE GALLERY (-4'-6" / -1.37 m)
    # =========================================================================
    # Semicircular floor deck spanning R = 22.8..32.5 ft from Control Core out to R = 31'-10" wall
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_GALLERY_RAIL,
        G.R_WELL_L2_WALL + 0.8,
        46.0,
        158.0,
        z_gal - 0.22,
        z_gal,
        MATERIALS["floor_oatmeal"],
        steps=36,
    )
    # Crisp white plaster gallery fascia + Aalto brass/white pipe handrail at R = 22.8 ft
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_GALLERY_RAIL - 0.35,
        G.R_GALLERY_RAIL + 0.15,
        52.0,
        152.0,
        z_gal - 0.24,
        z_gal + 0.42,
        MATERIALS["white_plaster"],
        steps=32,
    )
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_GALLERY_RAIL - 0.25,
        G.R_GALLERY_RAIL,
        52.0,
        152.0,
        z_gal + 0.88,
        z_gal + 0.94,
        MATERIALS["brass"],
        steps=32,
    )
    for post_deg in range(55, 152, 12):
        add_cylinder_ft(m2, polar_pt(G.WP3A, G.R_GALLERY_RAIL - 0.12, post_deg), 0.10, z_gal + 0.40, z_gal + 0.90, MATERIALS["brass"], sides=8)

    # =========================================================================
    # WEST (155.5°) & EAST (48.5°) STEPPED RADIAL WELL STAIRS + SE STAIR #2
    # =========================================================================
    for ang_c in (155.5, 48.5):
        # Upper flight: Level 3 Mezzanine (R = 43.8, Z = 0.0) -> Mid Landing (R = 33.2, Z = -1.37 m)
        p_top = polar_pt(G.WP3A, 43.6, ang_c)
        p_mid = polar_pt(G.WP3A, 33.4, ang_c)
        add_stepped_stair_ft(m2, p_top, p_mid, width_ft=6.2, z_top_m=z_l3, z_bot_m=z_gal, n_steps=9)

        # Mid landing connecting into the Semicircular Reference Gallery
        p_land_c = polar_pt(G.WP3A, 31.4, ang_c)
        add_oriented_box_ft(m2, p_land_c, 4.4, 6.4, ang_c, z_gal - 0.22, z_gal, MATERIALS["birch_wood"])

        # Lower flight: Mid Landing (R = 29.4, Z = -1.37 m) -> Level 2 Well Floor (R = 16.5, Z = -3.81 m)
        p_mid2 = polar_pt(G.WP3A, 29.2, ang_c)
        p_bot = polar_pt(G.WP3A, 16.8, ang_c)
        add_stepped_stair_ft(m2, p_mid2, p_bot, width_ft=6.2, z_top_m=z_gal, z_bot_m=z_l2, n_steps=14)

    # SE Stair #2 tucked inside Axis E diagonal brick wall (connecting L3 -> L2 -> L1)
    rad_e = math.radians(G.RAY_E_DEG)
    uxe, uye = math.cos(rad_e), math.sin(rad_e)
    nxe, nye = -uye, uxe
    st2_top = (65.0 + 3.2 * nxe, 42.2 + 3.2 * nye)
    st2_bot = (65.0 + 18.5 * uxe + 3.2 * nxe, 42.2 + 18.5 * uye + 3.2 * nye)
    add_stepped_stair_ft(m2, st2_top, st2_bot, width_ft=5.8, z_top_m=z_l3, z_bot_m=z_l2, n_steps=18)

    return grp_l1, grp_l2
