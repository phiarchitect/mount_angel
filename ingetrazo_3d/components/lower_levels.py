"""
Layers 2 & 3: Lower Hillside Tiers (`2_Level_1_Base` & `3_Level_2_Middle`).

  - Level 1 (-26'-6" / -8.08 m): Downhill fan stack floorplate, 5-sided interior
    reinforced-concrete core retaining wall, and radial archival bookstacks.
  - Level 2 (-12'-6" / -3.81 m): Main lower stack floorplate, curved R = 31'-10"
    interior core wall, perimeter study carrel alcoves, and two concentric rings
    of slatted-birch radial bookstacks with matte slate-grey steel canopy tops (`IMG_5143`).
  - Mezzanine / Reading Level (-4'-6" / -1.37 m): Slate-blue carpeted gallery deck,
    inner-arc 4-shelf curved Birch Reference Bookwall (`Angel-090508`), outer-arc
    cantilevered matte-black linoleum workbench (`R = 31'-10"`), 11 custom parapet-mounted
    angled-arm white mushroom lamps, 11 Aalto Artek 69 backrest reading chairs (`IMG_5143`),
    and West & East radial U-turn switchback stairs (`mezzaninestairsweb`).
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import (
    AaltoGeometry,
    get_carrel_alcoves_ft,
    get_l1_inner_pentagon_ft,
    get_level1_envelope_ft,
    get_level2_envelope_ft,
    get_radial_bookstacks_ft,
    polar_pt,
)

from .primitives import (
    MATERIALS,
    add_aalto_parapet_lamp,
    add_arc_band_ft,
    add_artek_chair_69,
    add_counter_wall_bracket,
    add_extruded_polygon_ft,
    add_oriented_box_ft,
    add_stepped_stair_ft,
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
)


def _lerp2(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _add_bookstack_range(
    mesh,
    quad_ft: list[tuple[float, float]],
    z_floor_m: float,
    height_m: float = 2.15,
    idx: int = 0,
    top_mat_key: str = "birch_wood",
):
    """
    Build an Aalto slatted-birch double-faced bookstack range with vertical birch end panels,
    canopy top (`stack_canopy_grey` on Level 2 per `IMG_5143`, `birch_wood` on Level 3), and recessed book tiers.
    """
    p0, p1, p2, p3 = quad_ft  # p0->p1 and p3->p2 are long radial edges; p0-p3 (inner) and p1-p2 (outer) are ends
    birch_side = {**MATERIALS["hemlock_slat"], "furniture": True}
    birch_end = {**MATERIALS["birch_wood"], "furniture": True}
    canopy_top = {**MATERIALS[top_mat_key], "furniture": True}

    # 1. Full-height slatted birch inner & outer end panels (t = 0.00..0.04 and 0.96..1.00 along length)
    end_in = [p0, _lerp2(p0, p1, 0.035), _lerp2(p3, p2, 0.035), p3]
    end_out = [_lerp2(p0, p1, 0.965), p1, p2, _lerp2(p3, p2, 0.965)]
    add_extruded_polygon_ft(mesh, end_in, z_floor_m, z_floor_m + height_m, birch_end, birch_side)
    add_extruded_polygon_ft(mesh, end_out, z_floor_m, z_floor_m + height_m, birch_end, birch_side)

    # 2. Central structural spine & base plinth
    spine = [
        _lerp2(_lerp2(p0, p3, 0.42), _lerp2(p1, p2, 0.42), 0.035),
        _lerp2(_lerp2(p0, p3, 0.42), _lerp2(p1, p2, 0.42), 0.965),
        _lerp2(_lerp2(p0, p3, 0.58), _lerp2(p1, p2, 0.58), 0.965),
        _lerp2(_lerp2(p0, p3, 0.58), _lerp2(p1, p2, 0.58), 0.035),
    ]
    add_extruded_polygon_ft(mesh, spine, z_floor_m + 0.10, z_floor_m + height_m - 0.05, birch_side)
    add_extruded_polygon_ft(mesh, quad_ft, z_floor_m, z_floor_m + 0.10, birch_end)

    # 3. Full-width top canopy (`stack_canopy_grey` on Level 2, `birch_wood` on Level 3/1)
    add_extruded_polygon_ft(mesh, quad_ft, z_floor_m + height_m - 0.05, z_floor_m + height_m, canopy_top, canopy_top)

    # 4. Recessed shelves + 4 tiers of colorful muted volumes visible along both sides
    shelf_quad = [
        _lerp2(_lerp2(p0, p3, 0.06), _lerp2(p1, p2, 0.06), 0.035),
        _lerp2(_lerp2(p0, p3, 0.06), _lerp2(p1, p2, 0.06), 0.965),
        _lerp2(_lerp2(p0, p3, 0.94), _lerp2(p1, p2, 0.94), 0.965),
        _lerp2(_lerp2(p0, p3, 0.94), _lerp2(p1, p2, 0.94), 0.035),
    ]
    book_quad = [
        _lerp2(_lerp2(p0, p3, 0.11), _lerp2(p1, p2, 0.11), 0.05),
        _lerp2(_lerp2(p0, p3, 0.11), _lerp2(p1, p2, 0.11), 0.95),
        _lerp2(_lerp2(p0, p3, 0.89), _lerp2(p1, p2, 0.89), 0.95),
        _lerp2(_lerp2(p0, p3, 0.89), _lerp2(p1, p2, 0.89), 0.05),
    ]
    book_mats = [
        MATERIALS["book_terracotta"],
        MATERIALS["book_slate"],
        MATERIALS["book_ochre"],
        MATERIALS["book_sage"],
    ]
    for tier in range(4):
        z_sh = z_floor_m + 0.12 + tier * 0.48
        add_extruded_polygon_ft(mesh, shelf_quad, z_sh, z_sh + 0.03, birch_end)
        bmat = {**book_mats[(idx + tier) % len(book_mats)], "furniture": True}
        add_extruded_polygon_ft(mesh, book_quad, z_sh + 0.03, z_sh + 0.36, bmat)


def build_lower_levels(scene):
    G = AaltoGeometry
    z_l1 = m_ft(G.Z_L1_FT)              # -8.08 m
    z_l2 = m_ft(G.Z_L2_FT)              # -3.81 m
    z_gal = m_ft(G.Z_REF_GALLERY_FT)    # -1.37 m (-4'-6" Mezzanine / Reading Level)
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
        _add_bookstack_range(m1, stk, z_l1, height_m=2.20, idx=idx, top_mat_key="stack_canopy_grey")

    # =========================================================================
    # LAYER 3: LEVEL 2 STACKS, MEZZANINE (-4'-6") & SWITCHBACK STAIRS
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

    # Curved White Plaster Wall at R = 31'-10" enclosing Level 2 Mechanical / Vertical File (`04-a4` & `Sheet 13`)
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_WELL_L2_WALL - 0.65,
        G.R_WELL_L2_WALL + 0.25,
        42.0,
        161.0,
        z_l2,
        z_gal - 0.22,
        MATERIALS["white_plaster"],
        steps=36,
    )

    # Level 2 Perimeter Study Carrel Partitions & Birch Desks (20 alcoves along Bays A-B..D-E)
    for c_box in get_carrel_alcoves_ft():
        add_wall_strip_ft(m2, [c_box[0], c_box[3]], 0.35, z_l2, z_l2 + 2.05, MATERIALS["white_plaster"])
        add_wall_strip_ft(m2, [c_box[1], c_box[2]], 0.35, z_l2, z_l2 + 2.05, MATERIALS["white_plaster"])
        desk_quad = [
            c_box[0],
            c_box[1],
            (0.55 * c_box[1][0] + 0.45 * c_box[2][0], 0.55 * c_box[1][1] + 0.45 * c_box[2][1]),
            (0.55 * c_box[0][0] + 0.45 * c_box[3][0], 0.55 * c_box[0][1] + 0.45 * c_box[3][1]),
        ]
        add_extruded_polygon_ft(m2, desk_quad, z_l2 + 0.70, z_l2 + 0.76, {**MATERIALS["birch_wood"], "furniture": True})

    # Level 2 Inner Ring of Radial Bookstacks (R = 34.4..47.4 ft, between well stairs; `Sheet 29-f1` & `IMG_5143`)
    inner_l2_stacks = get_radial_bookstacks_ft(34.4, 47.4)[2:13]
    for idx, stk in enumerate(inner_l2_stacks):
        _add_bookstack_range(m2, stk, z_l2, height_m=2.15, idx=idx, top_mat_key="stack_canopy_grey")

    # Level 2 Outer Ring of Radial Bookstacks (R = 51.4..68.5 ft; `Sheet 29-f1`)
    for idx, stk in enumerate(get_radial_bookstacks_ft(51.4, 68.5)):
        _add_bookstack_range(m2, stk, z_l2, height_m=2.15, idx=idx + 2, top_mat_key="stack_canopy_grey")

    # =========================================================================
    # MEZZANINE / READING LEVEL (-4'-6" / -1.37 m) (`Angel-090508`, `IMG_5143`)
    # =========================================================================
    # 1. Semicircular Mezzanine Structural Slab + Slate-Blue Wool Carpet Deck (R = 21.5..32.25 ft)
    add_arc_band_ft(
        m2,
        G.WP3A,
        21.5,
        G.R_WELL_L2_WALL + 0.42,
        41.8,
        161.5,
        z_gal - 0.22,
        z_gal - 0.02,
        MATERIALS["white_plaster"],
        steps=40,
    )
    add_arc_band_ft(
        m2,
        G.WP3A,
        21.5,
        G.R_WELL_L2_WALL + 0.42,
        41.8,
        161.5,
        z_gal - 0.02,
        z_gal,
        MATERIALS["carpet_blue"],
        steps=40,
    )

    # 2. Inner (-R) Arc: Curved 4-Shelf Birch Reference Bookwall tucked under Control Peninsula (`Angel-090508`)
    birch_furn = {**MATERIALS["birch_wood"], "furniture": True}
    add_arc_band_ft(m2, G.WP3A, 21.50, 21.85, 42.2, 161.1, z_gal, z_l3 - 0.28, birch_furn, steps=36)
    for z_sh in (0.04, 0.30, 0.56, 0.81, 1.05):
        add_arc_band_ft(
            m2,
            G.WP3A,
            21.85,
            G.R_GALLERY_RAIL + 0.15,
            42.2,
            161.1,
            z_gal + z_sh,
            z_gal + z_sh + 0.035,
            birch_furn,
            steps=36,
        )
    ref_book_mats = [
        {**MATERIALS["book_slate"], "furniture": True},
        {**MATERIALS["book_sage"], "furniture": True},
        {**MATERIALS["book_terracotta"], "furniture": True},
        {**MATERIALS["book_ochre"], "furniture": True},
    ]
    n_ref_bays = 18
    for b_idx in range(n_ref_bays):
        d0 = 42.6 + b_idx * (118.0 / n_ref_bays)
        d1 = d0 + (118.0 / n_ref_bays) - 0.6
        div_pt = polar_pt(G.WP3A, 22.40, d0 - 0.3)
        add_oriented_box_ft(m2, div_pt, 1.10, 0.12, d0 - 0.3, z_gal, z_l3 - 0.28, birch_furn)
        for s_tier, z_b0 in enumerate((0.08, 0.34, 0.60, 0.85)):
            add_arc_band_ft(
                m2,
                G.WP3A,
                21.88,
                G.R_GALLERY_RAIL + 0.02,
                d0 + 0.2,
                d1 - 0.2,
                z_gal + z_b0,
                z_gal + z_b0 + 0.19,
                ref_book_mats[(b_idx + s_tier) % len(ref_book_mats)],
                steps=2,
            )

    # Straight Radial 4-Shelf End Bookcases closing East (41.8°) & West (161.5°) Mezzanine Ends
    # (`Sheet 13-a13: EAST @ STAIR #2 / WEST @ STAIR #1` & visible behind columns in `mezzaninewithdictionaryweb2`!)
    for end_deg, in_sign in ((41.8, 1.0), (161.5, -1.0)):
        rad_e = math.radians(end_deg)
        urx, ury = math.cos(rad_e), math.sin(rad_e)
        itx, ity = in_sign * (-ury), in_sign * urx  # points inward onto Mezzanine carpet
        cx0, cy0 = G.WP3A
        # White plaster end backing wall under Level 3 stairwell edge
        back_quad = [
            (cx0 + 21.8 * urx - 0.28 * itx, cy0 + 21.8 * ury - 0.28 * ity),
            (cx0 + 32.1 * urx - 0.28 * itx, cy0 + 32.1 * ury - 0.28 * ity),
            (cx0 + 32.1 * urx + 0.05 * itx, cy0 + 32.1 * ury + 0.05 * ity),
            (cx0 + 21.8 * urx + 0.05 * itx, cy0 + 21.8 * ury + 0.05 * ity),
        ]
        add_extruded_polygon_ft(m2, back_quad, z_gal - 0.22, z_l3 - 0.28, MATERIALS["white_plaster"])
        # 4-shelf birch bookcase (R = 22.9..31.5 ft) under plaster spandrel beam
        sh_quad = [
            (cx0 + 22.95 * urx + 0.06 * itx, cy0 + 22.95 * ury + 0.06 * ity),
            (cx0 + 31.45 * urx + 0.06 * itx, cy0 + 31.45 * ury + 0.06 * ity),
            (cx0 + 31.45 * urx + 1.02 * itx, cy0 + 31.45 * ury + 1.02 * ity),
            (cx0 + 22.95 * urx + 1.02 * itx, cy0 + 22.95 * ury + 1.02 * ity),
        ]
        for z_sh in (0.04, 0.30, 0.56, 0.81, 1.04):
            add_extruded_polygon_ft(m2, sh_quad, z_gal + z_sh, z_gal + z_sh + 0.032, birch_furn)
        for eb_i in range(3):
            r_a = 23.05 + eb_i * 2.75
            r_b = r_a + 2.60
            bk_quad = [
                (cx0 + r_a * urx + 0.10 * itx, cy0 + r_a * ury + 0.10 * ity),
                (cx0 + r_b * urx + 0.10 * itx, cy0 + r_b * ury + 0.10 * ity),
                (cx0 + r_b * urx + 0.88 * itx, cy0 + r_b * ury + 0.88 * ity),
                (cx0 + r_a * urx + 0.88 * itx, cy0 + r_a * ury + 0.88 * ity),
            ]
            for s_tier, z_b0 in enumerate((0.08, 0.34, 0.60)):
                add_extruded_polygon_ft(
                    m2,
                    bk_quad,
                    z_gal + z_b0,
                    z_gal + z_b0 + 0.19,
                    ref_book_mats[(eb_i + s_tier) % len(ref_book_mats)],
                )

    # 3. Outer (+R) Arc: Mezzanine Parapet, Matte-Black Linoleum Workbench, Custom Lamps & Artek 69 Chairs (`IMG_5143`)
    mezz_deg0, mezz_deg1 = 55.8, 147.8
    r_mezz_in = G.R_WELL_L2_WALL - 0.18   # 31.65 ft (Mezzanine-facing plaster wall)
    r_mezz_out = G.R_WELL_L2_WALL + 0.42  # 32.25 ft (Well-facing plaster wall overlooking Level 2 stacks)

    # White plaster outer parapet wall + inner birch baseboard + raised birch book-stop curb
    add_arc_band_ft(m2, G.WP3A, r_mezz_in, r_mezz_out, mezz_deg0, mezz_deg1, z_gal - 0.22, z_gal + 0.89, MATERIALS["white_plaster"], steps=38)
    add_arc_band_ft(m2, G.WP3A, r_mezz_in - 0.10, r_mezz_in + 0.02, mezz_deg0, mezz_deg1, z_gal, z_gal + 0.09, birch_furn, steps=38)
    add_arc_band_ft(m2, G.WP3A, r_mezz_in - 0.05, r_mezz_out + 0.05, mezz_deg0, mezz_deg1, z_gal + 0.89, z_gal + 0.99, MATERIALS["birch_wood"], steps=38)

    # Cantilevered Matte-Black Linoleum Workbench + Birch Bullnose (R = 29.42..31.66 ft)
    lino_furn = {**MATERIALS["black_linoleum"], "furniture": True}
    add_arc_band_ft(m2, G.WP3A, 29.40, r_mezz_in + 0.02, mezz_deg0 + 0.2, mezz_deg1 - 0.2, z_gal + 0.70, z_gal + 0.745, birch_furn, steps=38)
    add_arc_band_ft(m2, G.WP3A, 29.52, r_mezz_in - 0.03, mezz_deg0 + 0.3, mezz_deg1 - 0.3, z_gal + 0.745, z_gal + 0.758, lino_furn, steps=38)

    # 12 White Painted Steel Wall T-Brackets under the Mezzanine Counter (`IMG_5143`)
    n_mezz_stations = 11
    mezz_step = (144.2 - 59.4) / (n_mezz_stations - 1)
    for b_i in range(n_mezz_stations + 1):
        b_deg = 59.4 - 0.5 * mezz_step + b_i * mezz_step
        b_deg = max(mezz_deg0 + 1.0, min(mezz_deg1 - 1.0, b_deg))
        add_counter_wall_bracket(m2, G.WP3A, r_mezz_in, b_deg, z_gal, seat_sign=-1)

    # 11 Custom Parapet-Mounted Angled-Arm White Mushroom Lamps + 11 Aalto Artek 69 Reading Chairs (`IMG_5143`)
    chair_swivels = (-5.0, 4.0, -3.0, 6.0, -4.0, 2.0, -6.0, 3.0, -2.0, 5.0, -4.0)
    for i in range(n_mezz_stations):
        st_deg = 59.4 + i * mezz_step
        # Lamp bracket bolted to +R well-facing side (r_mezz_out = 32.25 ft), arm angling -R inward over counter!
        add_aalto_parapet_lamp(m2, G.WP3A, r_well_face_ft=r_mezz_out, deg=st_deg, z_floor_m=z_gal, inward_sign=-1)
        # Aalto Artek 69 backrest chair on slate-blue carpet facing +R toward the workbench!
        chair_pt = polar_pt(G.WP3A, 28.35, st_deg)
        add_artek_chair_69(m2, chair_pt, facing_deg=st_deg + chair_swivels[i % len(chair_swivels)], z_floor_m=z_gal)

    # =========================================================================
    # WEST & EAST RADIAL SWITCHBACK (U-TURN) WELL STAIRS + SE STAIR #2
    # =========================================================================
    # Upper flight (outer lane) descends inward (-R) from Level 3 (R = 43.6) -> Mezzanine (R = 32.3, Z = -1.37 m)
    # alongside the Level 3 radial counter-height bookcase / plaster stairwell wall (`wall_side = +1` East, `-1` West).
    # Lower flight (inner lane) descends outward (+R) from Mezzanine (R = 32.4) -> Level 2 (R = 44.8, Z = -3.81 m).
    for ang_up, ang_dn, w_side in ((45.1, 52.0, 1), (158.2, 151.3, -1)):
        p_l3_top = polar_pt(G.WP3A, 43.6, ang_up)
        p_mezz_in = polar_pt(G.WP3A, 32.3, ang_up)
        add_stepped_stair_ft(
            m2,
            p_l3_top,
            p_mezz_in,
            width_ft=3.65,
            z_top_m=z_l3,
            z_bot_m=z_gal,
            n_steps=9,
            tread_attrs=MATERIALS["carpet_blue"],
            wall_side=w_side,
        )

        p_mezz_out = polar_pt(G.WP3A, 32.4, ang_dn)
        p_l2_bot = polar_pt(G.WP3A, 44.8, ang_dn)
        add_stepped_stair_ft(
            m2,
            p_mezz_out,
            p_l2_bot,
            width_ft=3.65,
            z_top_m=z_gal,
            z_bot_m=z_l2,
            n_steps=14,
            tread_attrs=MATERIALS["carpet_blue"],
        )

    # SE Stair #2 tucked inside Axis E diagonal brick wall (connecting L3 -> L2 -> L1)
    rad_e = math.radians(G.RAY_E_DEG)
    uxe, uye = math.cos(rad_e), math.sin(rad_e)
    nxe, nye = -uye, uxe
    st2_top = (65.0 + 3.2 * nxe, 42.2 + 3.2 * nye)
    st2_bot = (65.0 + 18.5 * uxe + 3.2 * nxe, 42.2 + 18.5 * uye + 3.2 * nye)
    add_stepped_stair_ft(m2, st2_top, st2_bot, width_ft=5.8, z_top_m=z_l3, z_bot_m=z_l2, n_steps=18)

    return grp_l1, grp_l2

