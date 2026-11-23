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

from .aalto_bookcases import add_aalto_bookcase_ft, add_aalto_curved_bookwall_ft
from .primitives import (
    MATERIALS,
    add_aalto_parapet_lamp,
    add_arc_band_ft,
    add_artek_chair_69,
    add_counter_wall_bracket,
    add_extruded_polygon_ft,
    add_stepped_stair_ft,
    add_wall_strip_ft,
    as_concrete,
    create_scene_group,
    m_ft,
    offset_polyline_right_ft,
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
    p0, p1, p2, p3 = quad_ft
    p_in = ((p0[0] + p3[0]) * 0.5, (p0[1] + p3[1]) * 0.5)
    p_out = ((p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5)
    vx = p_out[0] - p_in[0]
    vy = p_out[1] - p_in[1]
    length_ft = math.hypot(vx, vy)
    angle_deg = math.degrees(math.atan2(vy, vx))
    center_ft = ((p_in[0] + p_out[0]) * 0.5, (p_in[1] + p_out[1]) * 0.5)
    depth_ft = math.hypot(p3[0] - p0[0], p3[1] - p0[1])
    canopy_style = "slate_grey" if "grey" in top_mat_key else "birch"
    end_slats = "inner" if canopy_style == "birch" else "none"

    add_aalto_bookcase_ft(
        mesh,
        center_ft=center_ft,
        length_ft=length_ft,
        depth_ft=depth_ft,
        angle_deg=angle_deg,
        z_floor_m=z_floor_m,
        height_m=height_m,
        double_sided=True,
        n_shelf_tiers=6,
        canopy_style=canopy_style,
        end_slats=end_slats,
        populate_books=True,
        seed=idx * 19 + 7,
    )


def build_lower_levels(scene):
    G = AaltoGeometry
    z_l1 = m_ft(G.Z_L1_FT)              # -8.69 m (-28'-6" / EL. +100'-0")
    z_l2 = m_ft(G.Z_L2_FT)              # -4.27 m (-14'-0" / EL. +114'-6")
    z_gal = m_ft(G.Z_REF_GALLERY_FT)    # -1.63 m ( -5'-4" / EL. +123'-2" Mezzanine / Reading Level)
    z_l3 = m_ft(G.Z_L3_FT)              #  0.00 m (  0'-0" / EL. +128'-6")
    mezz_slab_m = m_ft(1.0)             #  0.305 m (1'-0" concrete slab per Sheet 46-s15 Detail N2)

    conc_mat = as_concrete(MATERIALS["concrete"])
    plaster_conc = as_concrete(MATERIALS["white_plaster"])

    # =========================================================================
    # LAYER 2: LEVEL 1 DOWNHILL BASE (-8.69 m / -28'-6")
    # =========================================================================
    grp_l1 = create_scene_group(scene, "2_Level_1_Base")
    m1 = grp_l1.mesh

    # Level 1 Structural Concrete Slab
    add_extruded_polygon_ft(
        m1,
        get_level1_envelope_ft(),
        z_l1 - 0.38,
        z_l1,
        as_concrete(MATERIALS["floor_lower"]),
        conc_mat,
    )

    # 5-Sided Interior Reinforced-Concrete Retaining Wall along Well Columns
    pent = get_l1_inner_pentagon_ft()
    add_wall_strip_ft(m1, pent, 1.25, z_l1, z_l2 - 0.28, conc_mat)
    # South retaining wall closing Level 1 core along Grid 6
    add_wall_strip_ft(
        m1,
        [(-69.5, 10.2), G.WELL_COLS_FT["Well_W_South"], (10.8, 0.5), G.WELL_COLS_FT["Well_4_ENE"], (44.5, 25.0)],
        1.20,
        z_l1,
        z_l2 - 0.28,
        conc_mat,
    )

    # Level 1 Archival Radial Bookstacks (6 open shelves, canopy_style="slate_grey", end_slats="none")
    for idx, stk in enumerate(get_radial_bookstacks_ft(38.5, 72.5)):
        p0, p1, p2, p3 = stk
        p_in = ((p0[0] + p3[0]) * 0.5, (p0[1] + p3[1]) * 0.5)
        p_out = ((p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5)
        vx = p_out[0] - p_in[0]
        vy = p_out[1] - p_in[1]
        length_ft = math.hypot(vx, vy)
        angle_deg = math.degrees(math.atan2(vy, vx))
        center_ft = ((p_in[0] + p_out[0]) * 0.5, (p_in[1] + p_out[1]) * 0.5)
        depth_ft = math.hypot(p3[0] - p0[0], p3[1] - p0[1])

        add_aalto_bookcase_ft(
            m1,
            center_ft=center_ft,
            length_ft=length_ft,
            depth_ft=depth_ft,
            angle_deg=angle_deg,
            z_floor_m=z_l1,
            height_m=2.15,
            double_sided=True,
            n_shelf_tiers=6,
            canopy_style="slate_grey",
            end_slats="none",
            populate_books=True,
            seed=idx * 17 + 101,
        )

    # =========================================================================
    # LAYER 3: LEVEL 2 STACKS (-14'-0"), MEZZANINE (-5'-4") & SWITCHBACK STAIRS
    # =========================================================================
    grp_l2 = create_scene_group(scene, "3_Level_2_Middle")
    m2 = grp_l2.mesh

    # Level 2 Concrete Floor Slab (-4.27 m, inset 0.52 ft inside exterior face brick veneer)
    add_extruded_polygon_ft(
        m2,
        offset_polyline_right_ft(get_level2_envelope_ft(), 0.52, closed=True),
        z_l2 - 0.30,
        z_l2,
        as_concrete(MATERIALS["floor_oatmeal"]),
        conc_mat,
    )

    # South Retaining Wall of Level 2 along Grid 4 & West Bindery
    add_wall_strip_ft(
        m2,
        [
            (G.X_AUD_E, G.GRID_Y["5"]),
            (G.X_AUD_E, G.GRID_Y["4"]),
            (G.X_SOUTH_STEP, G.GRID_Y["4"]),
            (G.X_SOUTH_STEP, G.GRID_Y["3"]),
            (G.X_WEST_WING, G.GRID_Y["3"]),
            (G.X_WEST_WING, G.GRID_Y["6"]),
        ],
        1.10,
        z_l2,
        z_l3 - 0.25,
        conc_mat,
    )

    # Curved Structural Concrete Core Wall at R = 31'-10" enclosing Level 2 Mechanical / Vertical File (`04-a4` & `46-s15`)
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_WELL_L2_WALL - 0.65,
        G.R_WELL_L2_WALL + 0.25,
        42.0,
        161.0,
        z_l2,
        z_gal - mezz_slab_m,
        plaster_conc,
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

    # Level 2 Inner Ring of Radial Bookstacks (R = 34.5..48.0 ft, between well stairs; `Sheet 29-f1` & `IMG_5143`)
    inner_l2_stacks = get_radial_bookstacks_ft(34.5, 48.0)[2:13]
    for idx, stk in enumerate(inner_l2_stacks):
        p0, p1, p2, p3 = stk
        p_in = ((p0[0] + p3[0]) * 0.5, (p0[1] + p3[1]) * 0.5)
        p_out = ((p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5)
        vx = p_out[0] - p_in[0]
        vy = p_out[1] - p_in[1]
        length_ft = math.hypot(vx, vy)
        angle_deg = math.degrees(math.atan2(vy, vx))
        center_ft = ((p_in[0] + p_out[0]) * 0.5, (p_in[1] + p_out[1]) * 0.5)
        depth_ft = math.hypot(p3[0] - p0[0], p3[1] - p0[1])

        add_aalto_bookcase_ft(
            m2,
            center_ft=center_ft,
            length_ft=length_ft,
            depth_ft=depth_ft,
            angle_deg=angle_deg,
            z_floor_m=z_l2,
            height_m=2.15,
            double_sided=True,
            n_shelf_tiers=6,
            canopy_style="slate_grey",
            end_slats="none",
            populate_books=True,
            seed=idx * 19 + 201,
        )

    # Level 2 Outer Ring of Radial Bookstacks (R = 51.8..70.0 ft; `Sheet 29-f1`)
    for idx, stk in enumerate(get_radial_bookstacks_ft(51.8, 70.0)):
        p0, p1, p2, p3 = stk
        p_in = ((p0[0] + p3[0]) * 0.5, (p0[1] + p3[1]) * 0.5)
        p_out = ((p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5)
        vx = p_out[0] - p_in[0]
        vy = p_out[1] - p_in[1]
        length_ft = math.hypot(vx, vy)
        angle_deg = math.degrees(math.atan2(vy, vx))
        center_ft = ((p_in[0] + p_out[0]) * 0.5, (p_in[1] + p_out[1]) * 0.5)
        depth_ft = math.hypot(p3[0] - p0[0], p3[1] - p0[1])

        add_aalto_bookcase_ft(
            m2,
            center_ft=center_ft,
            length_ft=length_ft,
            depth_ft=depth_ft,
            angle_deg=angle_deg,
            z_floor_m=z_l2,
            height_m=2.15,
            double_sided=True,
            n_shelf_tiers=6,
            canopy_style="slate_grey",
            end_slats="none",
            populate_books=True,
            seed=(idx + 2) * 23 + 301,
        )

    # =========================================================================
    # MEZZANINE / READING LEVEL (-5'-4" / -1.626 m / EL. +123'-2")
    # Sheet 46-s15 Detail N2: 1'-0" concrete slab spanning 9'-10" (R = 22'-0" .. 31'-10"),
    # 3-shelf reference bookcases (`1.24 m` tall) tucked cleanly beneath Level 3 4" plaster lip (`13-a13` Det. 9).
    # =========================================================================
    # 1. Semicircular Mezzanine Structural Slab (1'-0" thick) + Slate-Blue Wool Carpet Deck (R = 20.8..32.25 ft)
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_GALLERY_RAIL - 1.20,
        G.R_WELL_L2_WALL + 0.42,
        41.8,
        161.5,
        z_gal - mezz_slab_m,
        z_gal - 0.02,
        plaster_conc,
        steps=40,
    )
    add_arc_band_ft(
        m2,
        G.WP3A,
        G.R_GALLERY_RAIL - 1.20,
        G.R_WELL_L2_WALL + 0.42,
        41.8,
        161.5,
        z_gal - 0.02,
        z_gal,
        MATERIALS["carpet_blue"],
        steps=40,
    )

    # 2. Inner (-R) Arc: Curved 3-Shelf Birch Reference Bookwall tucked under Control Peninsula (`13-a13` Det. 9, `mezzaninewithdictionaryweb2`)
    # Bookcase height 1.24 m -> top at -1.626 + 1.24 = -0.386 m, flush under the -0.38 m Level 3 plaster soffit lip!
    mezz_bc_height_m = 1.24
    add_aalto_curved_bookwall_ft(
        m2,
        center_ft=G.WP3A,
        radius_ft=G.R_GALLERY_RAIL - 0.35,  # 21.65 ft centerline -> front book face at ~22.22 ft
        deg_start=42.2,
        deg_end=161.1,
        z_floor_m=z_gal,
        height_m=mezz_bc_height_m,
        depth_ft=1.15,
        n_shelf_tiers=3,
        face_inward=False,
        seed=42,
    )

    # Straight Radial 3-Shelf End Bookcases closing East (41.8°) & West (161.5°) Mezzanine Ends
    # (`Sheet 13-a13: EAST @ STAIR #2 / WEST @ STAIR #1` & visible behind columns in `mezzaninewithdictionaryweb2`!)
    for end_deg, in_sign, slat_side in ((41.8, 1.0, "start"), (161.5, -1.0, "end")):
        rad_e = math.radians(end_deg)
        urx, ury = math.cos(rad_e), math.sin(rad_e)
        itx, ity = in_sign * (-ury), in_sign * urx  # points inward onto Mezzanine carpet
        cx0, cy0 = G.WP3A
        # Structural concrete end wall under Level 3 stairwell edge
        back_quad = [
            (cx0 + (G.R_GALLERY_RAIL - 0.90) * urx - 0.28 * itx, cy0 + (G.R_GALLERY_RAIL - 0.90) * ury - 0.28 * ity),
            (cx0 + 32.1 * urx - 0.28 * itx, cy0 + 32.1 * ury - 0.28 * ity),
            (cx0 + 32.1 * urx + 0.05 * itx, cy0 + 32.1 * ury + 0.05 * ity),
            (cx0 + (G.R_GALLERY_RAIL - 0.90) * urx + 0.05 * itx, cy0 + (G.R_GALLERY_RAIL - 0.90) * ury + 0.05 * ity),
        ]
        add_extruded_polygon_ft(m2, back_quad, z_gal - mezz_slab_m, z_l3 - 0.28, plaster_conc)

        # 3-shelf birch bookcase (R = 22.35..31.45 ft, L = 9.10 ft, D = 1.05 ft, H = 1.24 m) under plaster spandrel beam
        r_mid = 26.90
        c_x = cx0 + r_mid * urx + 0.58 * itx
        c_y = cy0 + r_mid * ury + 0.58 * ity
        ang = end_deg if in_sign > 0 else (end_deg + 180.0) % 360.0

        add_aalto_bookcase_ft(
            m2,
            center_ft=(c_x, c_y),
            length_ft=9.10,
            depth_ft=1.05,
            angle_deg=ang,
            z_floor_m=z_gal,
            height_m=mezz_bc_height_m,
            double_sided=False,
            n_shelf_tiers=3,
            canopy_style="birch",
            end_slats=slat_side,
            populate_books=True,
            seed=int(end_deg * 10),
        )

    # 3. Outer (+R) Arc: Mezzanine Parapet (2'-9 1/2" per 46-s15 Det. N2), Matte-Black Workbench, Lamps & Artek 69 Chairs
    birch_furn = {**MATERIALS["birch_wood"], "furniture": True}
    mezz_deg0, mezz_deg1 = 55.8, 147.8
    r_mezz_in = G.R_WELL_L2_WALL - 0.18   # 31.65 ft (Mezzanine-facing plaster wall)
    r_mezz_out = G.R_WELL_L2_WALL + 0.42  # 32.25 ft (Well-facing plaster wall overlooking Level 2 stacks)

    # Structural upturned concrete parapet wall + inner birch baseboard + raised birch book-stop curb
    add_arc_band_ft(m2, G.WP3A, r_mezz_in, r_mezz_out, mezz_deg0, mezz_deg1, z_gal - mezz_slab_m, z_gal + 0.85, plaster_conc, steps=38)
    add_arc_band_ft(m2, G.WP3A, r_mezz_in - 0.10, r_mezz_in + 0.02, mezz_deg0, mezz_deg1, z_gal, z_gal + 0.09, birch_furn, steps=38)
    add_arc_band_ft(m2, G.WP3A, r_mezz_in - 0.05, r_mezz_out + 0.05, mezz_deg0, mezz_deg1, z_gal + 0.85, z_gal + 0.95, MATERIALS["birch_wood"], steps=38)

    # Cantilevered Matte-Black Linoleum Workbench + Birch Bullnose (R = 29.40..31.66 ft)
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
    # WEST & EAST RADIAL SWITCHBACK (U-TURN) WELL STAIRS + SE STAIR #2 (`22-a22`)
    # =========================================================================
    # Sheet 22-a22:
    #   - Upper flight (outer lane): 10 risers @ 6.40" = 5'-4" (Level 3 0'-0" -> Mezzanine -5'-4")
    #   - Lower flight (inner lane): 16 risers @ 6.50" = 8'-8" (Mezzanine -5'-4" -> Level 2 -14'-0")
    for ang_up, ang_dn, w_side in ((45.1, 52.0, 1), (158.2, 151.3, -1)):
        p_l3_top = polar_pt(G.WP3A, G.R_MEZZ_OPENING, ang_up)
        p_mezz_in = polar_pt(G.WP3A, 32.3, ang_up)
        add_stepped_stair_ft(
            m2,
            p_l3_top,
            p_mezz_in,
            width_ft=3.65,
            z_top_m=z_l3,
            z_bot_m=z_gal,
            n_steps=10,
            tread_attrs=MATERIALS["carpet_blue"],
            wall_side=w_side,
            concrete_struct=True,
        )

        p_mezz_out = polar_pt(G.WP3A, 32.4, ang_dn)
        p_l2_bot = polar_pt(G.WP3A, 45.2, ang_dn)
        add_stepped_stair_ft(
            m2,
            p_mezz_out,
            p_l2_bot,
            width_ft=3.65,
            z_top_m=z_gal,
            z_bot_m=z_l2,
            n_steps=16,
            tread_attrs=MATERIALS["carpet_blue"],
            concrete_struct=True,
        )

    # SE Stair #2 tucked inside Axis E diagonal brick wall (connecting Level 3 0'-0" -> Level 2 -14'-0")
    dx_e = G.PT_E[0] - G.PT_LOUNGE_JUNC[0]
    dy_e = G.PT_E[1] - G.PT_LOUNGE_JUNC[1]
    L_e = math.hypot(dx_e, dy_e)
    uxe_w, uye_w = dx_e / L_e, dy_e / L_e
    nxe_w, nye_w = -uye_w, uxe_w  # Inward normal into Reading Room
    c_dist = 4.05  # 1.12 ft wall + 0.15 ft clearance + 2.78 ft half-width = 4.05 ft
    st2_top = (G.PT_LOUNGE_JUNC[0] + 15.0 * uxe_w + c_dist * nxe_w, G.PT_LOUNGE_JUNC[1] + 15.0 * uye_w + c_dist * nye_w)
    st2_bot = (G.PT_LOUNGE_JUNC[0] + 34.5 * uxe_w + c_dist * nxe_w, G.PT_LOUNGE_JUNC[1] + 34.5 * uye_w + c_dist * nye_w)
    add_stepped_stair_ft(m2, st2_top, st2_bot, width_ft=5.8, z_top_m=z_l3, z_bot_m=z_l2, n_steps=22, wall_side=-1, concrete_struct=True)

    return grp_l1, grp_l2

