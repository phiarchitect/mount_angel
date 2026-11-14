"""
Layers 5 & 6: Structural Columns/H-Piers (`5_Structural_Frame`) &
Buff-Brick Faceted Envelope, Curtain Walls & South Wing (`6_Envelope_And_South_Wing`).

  - 18"Ø round white concrete columns (including the 3 paired twin-column clusters
    on Rays B, C, D at 4'-10" c/c and the 5 multi-story Well columns rising into
    the North Daylight Scoop!)
  - 3 full-height Buff-Brick & Dark-Steel Perimeter H-Piers (B, C, D)
  - 3-Story Faceted North Buff-Brick Curtain Wall (Bays A-B, B-C, C-D, D-E) with
    ribbon window bands, bronze mullions, and exterior vertical wood sun louvers
  - Periodical Lounge East Mt. Hood floor-to-ceiling picture window & louvers
  - One-Story South Entrance Wing (Rare Book Auditorium, Glazed Entry Vestibule,
    West Cataloging Wing) & Slender Cantilevered South Entry Canopy!
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import (
    AaltoGeometry,
    get_faceted_curtain_bays_ft,
    get_h_pier_polygons_ft,
    get_north_perimeter_with_pockets_ft,
    polar_pt,
)

from .primitives import (
    MATERIALS,
    add_cylinder_ft,
    add_extruded_polygon_ft,
    add_louver_bank_ft,
    add_oriented_box_ft,
    add_quad,
    add_tri,
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
    triangulate_polygon_2d,
    xy_m,
)


def _lerp2(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _add_hpier_solid_ft(
    mesh_struct,
    mesh_env,
    hp_poly_ft: list[tuple[float, float]],
    z_bot_m: float,
    z_l3_m: float,
    z_fan_low_m: float,
    z_top_m: float,
    has_alcove_window: bool = False,
):
    """
    Build a 100% watertight 2-manifold H-Column pier (`5_Structural_Frame`), with:
      - Interior Level 3 alcove faces (`p10->p9`, `p9->p8`, `p8->p7` over `z_l3 .. z_fan_low`) finished
        in crisp `white_plaster` while exterior fins & scupper pocket are `buff_brick_dark`
      - Optional eye-level square punched window (`HPier_D` on Ray D = 65.72° ENE framing Mt. Hood on entry;
        Sheets 05-a5, 11-a11 & 12-a12) with closed dark-bronze frame and clear glazing in `6_Envelope_And_South_Wing`.
    """
    pts_m = [xy_m(p) for p in hp_poly_ft]
    # hp_poly_ft is 12 vertices in CW order:
    # 0:L_tip_out, 1:L_tip_in, 2:wL_out, 3:wR_out, 4:R_tip_in, 5:R_tip_out,
    # 6:R_bot_out, 7:R_bot_in, 8:wR_in,  9:wL_in,  10:L_bot_in, 11:L_bot_out
    brick_side = MATERIALS["buff_brick_dark"]
    brick_top = MATERIALS["buff_brick"]
    conc_bot = MATERIALS["concrete"]
    plaster = MATERIALS["white_plaster"]

    if not has_alcove_window:
        # CCW ring: reverse of CW pts_m
        ccw = list(reversed(pts_m))
        # In reversed indices: 0=p11, 1=p10, 2=p9, 3=p8, 4=p7, 5=p6, 6=p5, 7=p4, 8=p3, 9=p2, 10=p1, 11=p0
        # Inner alcove edges in CCW order: (1->2 = p10->p9), (2->3 = p9->p8), (3->4 = p8->p7)
        alcove_edges = {1, 2, 3}
        _, tris = triangulate_polygon_2d(ccw)
        for i0, i1, i2 in tris:
            a, b, c = ccw[i0], ccw[i1], ccw[i2]
            add_tri(mesh_struct, (*a, z_top_m), (*b, z_top_m), (*c, z_top_m), brick_top)
            add_tri(mesh_struct, (*a, z_bot_m), (*c, z_bot_m), (*b, z_bot_m), conc_bot)

        z_tiers = [z_bot_m, z_l3_m, z_fan_low_m, z_top_m]
        m = len(ccw)
        for ti in range(len(z_tiers) - 1):
            za, zb = z_tiers[ti], z_tiers[ti + 1]
            in_l3 = (ti == 1)
            for ei in range(m):
                p0 = ccw[ei]
                p1 = ccw[(ei + 1) % m]
                mat = plaster if (in_l3 and ei in alcove_edges) else brick_side
                add_quad(mesh_struct, (*p0, za), (*p1, za), (*p1, zb), (*p0, zb), mat)
        return

    # Genus-1 H-Pier (`HPier_D`) pierced by the eye-level square Mt. Hood alcove window:
    # Clear structural opening: u = 0.21..0.79 (~3'-8" wide) x z = +1.04..+2.14 m (+3'-5" sill to +7'-0" head)
    u0, u1 = 0.21, 0.79
    z_sill = z_l3_m + 1.04
    z_head = z_l3_m + 2.14

    wo0 = _lerp2(pts_m[2], pts_m[3], u0)
    wo1 = _lerp2(pts_m[2], pts_m[3], u1)
    wi0 = _lerp2(pts_m[9], pts_m[8], u0)
    wi1 = _lerp2(pts_m[9], pts_m[8], u1)

    poly_L = [pts_m[0], pts_m[11], pts_m[10], pts_m[9], wi0, wo0, pts_m[2], pts_m[1]]
    poly_C = [wo0, wi0, wi1, wo1]
    poly_R = [pts_m[5], pts_m[4], pts_m[3], wo1, wi1, pts_m[8], pts_m[7], pts_m[6]]

    for sub_ccw in (poly_L, poly_C, poly_R):
        _, tris = triangulate_polygon_2d(sub_ccw)
        for i0, i1, i2 in tris:
            a, b, c = sub_ccw[i0], sub_ccw[i1], sub_ccw[i2]
            add_tri(mesh_struct, (*a, z_top_m), (*b, z_top_m), (*c, z_top_m), brick_top)
            add_tri(mesh_struct, (*a, z_bot_m), (*c, z_bot_m), (*b, z_bot_m), conc_bot)

    z_tiers = [z_bot_m, z_l3_m, z_sill, z_head, z_fan_low_m, z_top_m]
    # Left leg + jamb outer perimeter (skipping internal seam index 4: wi0 -> wo0)
    for ti in range(len(z_tiers) - 1):
        za, zb = z_tiers[ti], z_tiers[ti + 1]
        in_l3 = (z_l3_m - 1e-4 <= za and zb <= z_fan_low_m + 1e-4)
        for ei in range(len(poly_L)):
            if ei == 4:
                continue
            p0, p1 = poly_L[ei], poly_L[(ei + 1) % len(poly_L)]
            mat = plaster if (in_l3 and ei in (2, 3)) else brick_side
            add_quad(mesh_struct, (*p0, za), (*p1, za), (*p1, zb), (*p0, zb), mat)

    # Right leg + jamb outer perimeter (skipping internal seam index 3: wo1 -> wi1)
    for ti in range(len(z_tiers) - 1):
        za, zb = z_tiers[ti], z_tiers[ti + 1]
        in_l3 = (z_l3_m - 1e-4 <= za and zb <= z_fan_low_m + 1e-4)
        for ei in range(len(poly_R)):
            if ei == 3:
                continue
            p0, p1 = poly_R[ei], poly_R[(ei + 1) % len(poly_R)]
            mat = plaster if (in_l3 and ei in (4, 5)) else brick_side
            add_quad(mesh_struct, (*p0, za), (*p1, za), (*p1, zb), (*p0, zb), mat)

    # Center web outer (wo1 -> wo0) and inner (wi0 -> wi1) walls for all tiers EXCEPT window tier (ti == 2)
    for ti in range(len(z_tiers) - 1):
        if ti == 2:
            continue
        za, zb = z_tiers[ti], z_tiers[ti + 1]
        in_l3 = (z_l3_m - 1e-4 <= za and zb <= z_fan_low_m + 1e-4)
        add_quad(mesh_struct, (*wo1, za), (*wo0, za), (*wo0, zb), (*wo1, zb), brick_side)
        add_quad(mesh_struct, (*wi0, za), (*wi1, za), (*wi1, zb), (*wi0, zb), plaster if in_l3 else brick_side)

    # Window tunnel reveals (z_sill .. z_head): sill (+Z), head (-Z), left jamb (+u), right jamb (-u)
    add_quad(mesh_struct, (*wo0, z_sill), (*wi0, z_sill), (*wi1, z_sill), (*wo1, z_sill), plaster)
    add_quad(mesh_struct, (*wo0, z_head), (*wo1, z_head), (*wi1, z_head), (*wi0, z_head), plaster)
    add_quad(mesh_struct, (*wi0, z_sill), (*wo0, z_sill), (*wo0, z_head), (*wi0, z_head), plaster)
    add_quad(mesh_struct, (*wo1, z_sill), (*wi1, z_sill), (*wi1, z_head), (*wo1, z_head), plaster)

    # Closed 2-manifold dark-bronze picture-window frame + clear square glazing in Layer 6 (`mesh_env`)
    f_out0 = _lerp2(_lerp2(wo0, wi0, 0.32), _lerp2(wo1, wi1, 0.32), 0.008)
    f_out1 = _lerp2(_lerp2(wo0, wi0, 0.32), _lerp2(wo1, wi1, 0.32), 0.992)
    b_out0 = _lerp2(_lerp2(wo0, wi0, 0.68), _lerp2(wo1, wi1, 0.68), 0.008)
    b_out1 = _lerp2(_lerp2(wo0, wi0, 0.68), _lerp2(wo1, wi1, 0.68), 0.992)

    f_in0 = _lerp2(_lerp2(wo0, wi0, 0.32), _lerp2(wo1, wi1, 0.32), 0.056)
    f_in1 = _lerp2(_lerp2(wo0, wi0, 0.32), _lerp2(wo1, wi1, 0.32), 0.944)
    b_in0 = _lerp2(_lerp2(wo0, wi0, 0.68), _lerp2(wo1, wi1, 0.68), 0.056)
    b_in1 = _lerp2(_lerp2(wo0, wi0, 0.68), _lerp2(wo1, wi1, 0.68), 0.944)

    zo0, zo1 = z_sill + 0.006, z_head - 0.006
    zi0, zi1 = z_sill + 0.056, z_head - 0.056
    f_mat = MATERIALS["mullion_bronze"]

    # Front (exterior pocket side, +r normal) & Back (interior alcove side, -r normal) 4-quad mitered rings
    O_f = [(*f_out0, zo0), (*f_out1, zo0), (*f_out1, zo1), (*f_out0, zo1)]
    I_f = [(*f_in0, zi0), (*f_in1, zi0), (*f_in1, zi1), (*f_in0, zi1)]
    O_b = [(*b_out0, zo0), (*b_out1, zo0), (*b_out1, zo1), (*b_out0, zo1)]
    I_b = [(*b_in0, zi0), (*b_in1, zi0), (*b_in1, zi1), (*b_in0, zi1)]
    for k in range(4):
        kn = (k + 1) % 4
        add_quad(mesh_env, O_f[k], O_f[kn], I_f[kn], I_f[k], f_mat)
        add_quad(mesh_env, O_b[kn], O_b[k], I_b[k], I_b[kn], f_mat)
        add_quad(mesh_env, O_b[k], O_b[kn], O_f[kn], O_f[k], f_mat)
        add_quad(mesh_env, I_f[k], I_f[kn], I_b[kn], I_b[k], f_mat)

    # Clear square glass pane centered in frame (`trans_pos`, allowing unobstructed sightline & solar beam!)
    g_f0 = _lerp2(_lerp2(wo0, wi0, 0.47), _lerp2(wo1, wi1, 0.47), 0.056)
    g_f1 = _lerp2(_lerp2(wo0, wi0, 0.47), _lerp2(wo1, wi1, 0.47), 0.944)
    g_b0 = _lerp2(_lerp2(wo0, wi0, 0.53), _lerp2(wo1, wi1, 0.53), 0.056)
    g_b1 = _lerp2(_lerp2(wo0, wi0, 0.53), _lerp2(wo1, wi1, 0.53), 0.944)
    g_mat = MATERIALS["glass_clear"]
    Gf = [(*g_f0, zi0), (*g_f1, zi0), (*g_f1, zi1), (*g_f0, zi1)]
    Gb = [(*g_b0, zi0), (*g_b1, zi0), (*g_b1, zi1), (*g_b0, zi1)]
    add_quad(mesh_env, Gf[0], Gf[1], Gf[2], Gf[3], g_mat)
    add_quad(mesh_env, Gb[1], Gb[0], Gb[3], Gb[2], g_mat)
    for k in range(4):
        kn = (k + 1) % 4
        add_quad(mesh_env, Gb[k], Gb[kn], Gf[kn], Gf[k], g_mat)


def _add_faceted_curtain_bay(
    mesh,
    p0_ft: tuple[float, float],
    p1_ft: tuple[float, float],
    z_l2_m: float,
    z_l3_m: float,
    z_parapet_m: float,
    trim_start_ft: float = 0.0,
    trim_end_ft: float = 0.0,
):
    """
    Build one cantilevered Level 2–3 faceted North bay (A-B, B-C, C-D, or D-E)
    terminating flush against the mitered outer fin tips of H-Columns B, C, D
    (Sheets 11-a11, 12-a12 & 17-a17 Section 1):
      - Level 2 carrel ribbon window (`+2'-8"` sill to `+9'-4"` head = `-3.00 .. -0.97 m`)
      - Monumental solid buff-brick outer wall + white-plaster interior reading-room wall rising
        to **above head height (`+7'-2"` / `+2.18 m`)** on Level 3 behind perimeter stacks & carrels
      - High Level 3 clerestory window band (`+2.18 .. +4.52 m`) screened by full-height exterior
        vertical wood sun-shading louvers (`+2.04 .. +5.23 m`, Detail 9 on Sheet 11-a11).
    """
    dx, dy = p1_ft[0] - p0_ft[0], p1_ft[1] - p0_ft[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    # Inward normal (Southward into fan: rotate clockwise 90 deg -> (uy, -ux))
    ix, iy = uy, -ux

    q0 = (p0_ft[0] + ux * trim_start_ft, p0_ft[1] + uy * trim_start_ft)
    q1 = (p1_ft[0] - ux * trim_end_ft, p1_ft[1] - uy * trim_end_ft)

    z_l2_sill = z_l2_m + 0.81        # -3.00 m (+2'-8" above L2 floor)
    z_l2_head = z_l2_m + 2.84        # -0.97 m (+9'-4" above L2 floor)
    z_l3_sill = z_l3_m + 2.18        # +2.18 m (+7'-2" above L3 floor — above head & stack height!)
    z_l3_head = z_parapet_m - 0.81   # +4.52 m (+14'-10" clerestory head below upper fascia)

    # Outer Mount Angel buff-brick wythe (`offset_mode="right"`, 0.72 ft thick)
    brick_bands = [
        (z_l2_m - 0.30, z_l2_sill),
        (z_l2_head, z_l3_sill),
        (z_l3_head, z_parapet_m),
    ]
    for zb, zt in brick_bands:
        add_wall_strip_ft(mesh, [q0, q1], 0.72, zb, zt, MATERIALS["buff_brick"], offset_mode="right")

    # Inner crisp white-plaster reading-room backing wythe (inset 0.75 ft, 0.37 ft thick -> total 1.12 ft wall)
    pl0 = (q0[0] + ix * 0.75, q0[1] + iy * 0.75)
    pl1 = (q1[0] + ix * 0.75, q1[1] + iy * 0.75)
    plaster_bands = [
        (z_l2_m + 0.01, z_l2_sill),
        (z_l2_head, z_l3_m - 0.30),
        (z_l3_m + 0.01, z_l3_sill),
        (z_l3_head, z_parapet_m - 0.36),
    ]
    for zb, zt in plaster_bands:
        add_wall_strip_ft(mesh, [pl0, pl1], 0.37, zb, zt, MATERIALS["white_plaster"], offset_mode="right")

    # Window Glazing, Bronze Mullions & Exterior Vertical Hemlock Sun-Louver Banks
    g0 = (q0[0] + ix * 0.48, q0[1] + iy * 0.48)
    g1 = (q1[0] + ix * 0.48, q1[1] + iy * 0.48)
    win_bands = [
        (z_l2_sill, z_l2_head, z_l2_sill + 0.06, z_l2_head - 0.06),
        (z_l3_sill, z_l3_head, z_l3_sill - 0.14, z_parapet_m - 0.10),
    ]

    ang_deg = math.degrees(math.atan2(dy, dx))
    eff_L = max(8.0, L - trim_start_ft - trim_end_ft)
    n_mull = max(4, int(eff_L / 5.2))
    for zb, zt, z_louv_b, z_louv_t in win_bands:
        add_wall_strip_ft(mesh, [g0, g1], 0.18, zb, zt, MATERIALS["glass_clear"], offset_mode="center")
        for k in range(n_mull + 1):
            t = k / n_mull
            mx = g0[0] + (g1[0] - g0[0]) * t
            my = g0[1] + (g1[1] - g0[1]) * t
            add_oriented_box_ft(mesh, (mx, my), 0.24, 0.52, ang_deg, zb, zt, MATERIALS["mullion_bronze"])
        add_louver_bank_ft(mesh, q0, q1, z_louv_b, z_louv_t, spacing_ft=2.35, blade_depth_ft=0.92, blade_thick_ft=0.19)


def _add_stepped_l1_concrete_bay(
    mesh,
    p0_ft: tuple[float, float],
    p1_ft: tuple[float, float],
    z_base_m: float,
    z_l1_m: float,
    z_l2_m: float,
):
    """
    Build the stepped-back Level 1 exposed-concrete foundation wall & high clerestory
    ribbon windows (`(M)` on North Elevation Sheet 12) flush with the H-column U-channels.
    """
    dx, dy = p1_ft[0] - p0_ft[0], p1_ft[1] - p0_ft[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    ix, iy = uy, -ux

    z_win_bot = z_l1_m + 2.15
    z_win_top = z_l2_m - 0.55
    add_wall_strip_ft(mesh, [p0_ft, p1_ft], 1.15, z_base_m, z_win_bot, MATERIALS["concrete"], offset_mode="right")
    add_wall_strip_ft(mesh, [p0_ft, p1_ft], 1.15, z_win_top, z_l2_m - 0.30, MATERIALS["concrete"], offset_mode="right")

    g0 = (p0_ft[0] + ix * 0.45, p0_ft[1] + iy * 0.45)
    g1 = (p1_ft[0] + ix * 0.45, p1_ft[1] + iy * 0.45)
    add_wall_strip_ft(mesh, [g0, g1], 0.18, z_win_bot, z_win_top, MATERIALS["glass_clear"], offset_mode="center")

    ang_deg = math.degrees(math.atan2(dy, dx))
    n_mull = max(4, int(L / 6.0))
    for k in range(n_mull + 1):
        t = k / n_mull
        mx = g0[0] + (g1[0] - g0[0]) * t
        my = g0[1] + (g1[1] - g0[1]) * t
        add_oriented_box_ft(mesh, (mx, my), 0.22, 0.48, ang_deg, z_win_bot, z_win_top, MATERIALS["mullion_bronze"])


def build_envelope_and_south_wing(scene):
    G = AaltoGeometry
    z_crawl = m_ft(G.Z_CRAWL_FT)            # -10.36 m
    z_l1 = m_ft(G.Z_L1_FT)                  #  -8.08 m
    z_l2 = m_ft(G.Z_L2_FT)                  #  -3.81 m
    z_l3 = m_ft(G.Z_L3_FT)                  #   0.00 m
    z_lobby = m_ft(G.Z_LOBBY_FT)            #  +0.61 m
    z_canopy = m_ft(G.Z_CANOPY_FT)          #  +3.25 m
    z_fan_low = m_ft(G.Z_FAN_ROOF_LOW_FT)   #  +3.81 m
    z_south_rf = m_ft(G.Z_SOUTH_ROOF_FT)    #  +4.98 m
    z_par_n = m_ft(G.Z_FAN_PARAPET_N_FT)    #  +5.33 m

    # =========================================================================
    # LAYER 5: STRUCTURAL COLUMNS, PAIRED COLUMNS & 3 IRREGULAR H-COLUMNS
    # =========================================================================
    grp_str = create_scene_group(scene, "5_Structural_Frame")
    ms = grp_str.mesh

    grp_env = create_scene_group(scene, "6_Envelope_And_South_Wing")
    me = grp_env.mesh

    # 5 Multi-Story Well Columns (rising from Level 1 all the way up to support the Daylight Scoop!)
    for cname, cpt in G.WELL_COLS_FT.items():
        z_top = z_south_rf - 0.15 if cname != "South_W1" else z_fan_low
        add_cylinder_ft(ms, cpt, 0.78, z_l1, z_top, MATERIALS["white_column"], sides=18)

    # 6 Paired Twin 18"Ø Columns straddling WP #3 Radial Axes B, C, D (5'-4" c/c, Sheet 06-a6)
    for _, cpt in G.PAIRED_COLS_FT.items():
        add_cylinder_ft(ms, cpt, 0.75, z_l1, z_fan_low + 0.15, MATERIALS["white_column"], sides=18)

    # South Wing & Periodical Lounge Structural Columns
    for cpt in G.SOUTH_WING_COLS_FT:
        z_bot = z_l2 if cpt[1] > -29.0 else z_lobby - 0.8
        add_cylinder_ft(ms, cpt, 0.68, z_bot, z_south_rf - 0.20, MATERIALS["white_column"], sides=14)

    # 3 Distinct Irregular Perimeter H-Columns (B @ WP #5, C @ WP #6/#7, D @ WP #8/#9; Sheets 06-a6 & 45-s14):
    #   (a) Level 1 Stepped-Back Concrete U-Channel Piers (+1'-6" inner leg extension)
    for u_poly in get_h_pier_polygons_ft(level=1):
        add_extruded_polygon_ft(ms, u_poly, z_crawl + 0.6, z_l2 - 0.30, MATERIALS["concrete"], MATERIALS["concrete"])

    #   (b) Levels 2–Roof Splayed Irregular Buff-Brick H-Columns (with eye-level square Mt. Hood window in HPier_D!)
    for hp_idx, hp_poly in enumerate(get_h_pier_polygons_ft(level=3)):
        _add_hpier_solid_ft(
            ms,
            me,
            hp_poly,
            z_bot_m=z_l2 - 0.30,
            z_l3_m=z_l3,
            z_fan_low_m=z_fan_low - 0.24,
            z_top_m=z_par_n + 0.04,
            has_alcove_window=(hp_idx == 2),  # HPier_D (Ray D = 65.72° ENE) frames Mt. Hood on entry!
        )
        # Exterior rainwater scupper leader pipe tucked into the left corner of the recessed H-pocket (Sheets 07-a7 & 11-a11)
        wx, wy = _lerp2(hp_poly[2], hp_poly[3], 0.12)
        tx = 0.5 * (hp_poly[1][0] + hp_poly[4][0]) - 0.5 * (hp_poly[2][0] + hp_poly[3][0])
        ty = 0.5 * (hp_poly[1][1] + hp_poly[4][1]) - 0.5 * (hp_poly[2][1] + hp_poly[3][1])
        tl = max(1e-4, math.hypot(tx, ty))
        scup_pt = (wx + (tx / tl) * 0.42, wy + (ty / tl) * 0.42)
        add_cylinder_ft(ms, scup_pt, 0.16, z_crawl + 0.6, z_par_n - 0.18, MATERIALS["copper_roof"], sides=12)

    # Radial Structural Ceiling Ribs radiating from WP #3 out to North Curtain Wall
    for b_deg in (152.0, G.RAY_B_DEG, 119.0, G.RAY_C_DEG, 83.0, G.RAY_D_DEG, 49.0):
        p_in = polar_pt(G.WP3, 45.0, b_deg)
        p_out = polar_pt(G.WP3, 83.0, b_deg)
        add_wall_strip_ft(ms, [p_in, p_out], 0.65, z_fan_low - 0.38, z_fan_low, MATERIALS["white_soffit"])

    # =========================================================================
    # LAYER 6: FACETED NORTH BRICK CURTAIN WALL, MT. HOOD WINDOW & SOUTH WING
    # =========================================================================
    # 4 Cantilevered Level 2–3 Faceted Curtain-Wall Bays (meeting H-Column fin miters cleanly)
    curtain_bays = get_faceted_curtain_bays_ft()
    for b_idx, (bp0, bp1) in enumerate(curtain_bays):
        t_s = 1.9 if b_idx == 0 else 0.0
        t_e = 2.1 if b_idx == len(curtain_bays) - 1 else 0.0
        _add_faceted_curtain_bay(me, bp0, bp1, z_l2, z_l3, z_par_n, trim_start_ft=t_s, trim_end_ft=t_e)

    # Stepped-Back Level 1 Exposed-Concrete Foundation Wall & Clerestory Windows (Sheet 12 & Sheet 45)
    l1_perim = get_north_perimeter_with_pockets_ft(level=1)
    l1_bays = [
        (l1_perim[0], l1_perim[1], z_crawl + 1.0),
        (l1_perim[2], l1_perim[3], z_crawl + 0.6),
        (l1_perim[4], l1_perim[5], z_crawl + 0.6),
        (l1_perim[6], l1_perim[7], z_crawl + 1.1),
    ]
    for lp0, lp1, zb_l1 in l1_bays:
        _add_stepped_l1_concrete_bay(me, lp0, lp1, zb_l1, z_l1, z_l2)

    # Concrete Cantilever Soffit Strip closing the step between Level 1 wall and cantilevered Level 2 facade
    cantilever_soffit_poly = [
        *get_north_perimeter_with_pockets_ft(level=3),
        *reversed(l1_perim),
    ]
    add_extruded_polygon_ft(me, cantilever_soffit_poly, z_l2 - 0.34, z_l2 - 0.28, MATERIALS["concrete"], MATERIALS["concrete"])

    # Corner Buff-Brick Piers at West Jamb A (WP #4/A) and East Prow Apex E (WP #10)
    add_oriented_box_ft(me, G.PT_A, 3.8, 3.6, G.RAY_A_DEG, z_l1 - 1.2, z_par_n + 0.04, MATERIALS["buff_brick"])
    add_oriented_box_ft(me, G.PT_E, 4.2, 3.8, G.RAY_E_DEG, z_l1 - 1.2, z_par_n + 0.04, MATERIALS["buff_brick"])

    # West Fan Throat Wall (PT_A -> PT_A_INNER_JUNC -> Grid 6) + Level 3 interior white-plaster liner
    add_wall_strip_ft(me, [G.PT_A, G.PT_A_INNER_JUNC, (-77.5, 1.5)], 1.25, z_l1 - 1.0, z_par_n - 0.4, MATERIALS["buff_brick"])
    add_wall_strip_ft(me, [(-84.2, 13.9), (-76.8, 12.3), (-76.8, 1.8)], 0.22, z_l3 + 0.01, z_fan_low - 0.25, MATERIALS["white_plaster"], offset_mode="left")

    # East Diagonal Fan Wall along Axis E (PT_E -> PT_LOUNGE_JUNC) + Level 3 interior white-plaster liner
    add_wall_strip_ft(me, [G.PT_E, G.PT_LOUNGE_JUNC], 1.30, z_l1 - 1.0, z_par_n - 0.4, MATERIALS["buff_brick"])
    rad_e = math.radians(G.RAY_E_DEG)
    nxe, nye = -math.sin(rad_e), math.cos(rad_e)
    add_wall_strip_ft(
        me,
        [(G.PT_E[0] + 0.72 * nxe, G.PT_E[1] + 0.72 * nye), (G.PT_LOUNGE_JUNC[0] + 0.72 * nxe, G.PT_LOUNGE_JUNC[1] + 0.72 * nye)],
        0.24,
        z_l3 + 0.01,
        z_fan_low - 0.25,
        MATERIALS["white_plaster"],
        offset_mode="left",
    )

    # Periodical Lounge East Wall featuring the Famous Mt. Hood Picture Window & Wood Louvers!
    # Solid brick corners + floor-to-ceiling glazing from Y = -4.0..+29.0 ft along X = +51.8 ft
    add_wall_strip_ft(me, [(51.8, 32.8), (51.8, 28.5)], 1.25, z_l2 - 0.8, z_south_rf, MATERIALS["buff_brick"])
    add_wall_strip_ft(me, [(51.8, -4.5), (51.8, -8.8)], 1.25, z_l2 - 0.8, z_south_rf, MATERIALS["buff_brick"])
    add_wall_strip_ft(me, [(51.8, 28.5), (51.8, -4.5)], 1.15, z_l2 - 0.8, z_l3 + 0.25, MATERIALS["buff_brick"])
    add_wall_strip_ft(me, [(51.8, 28.5), (51.8, -4.5)], 1.15, z_south_rf - 0.95, z_south_rf, MATERIALS["buff_brick"])
    # Tall Mt. Hood Picture Window (L3) & Seminar Ribbon Window (L2)
    add_wall_strip_ft(me, [(51.8, 28.5), (51.8, -4.5)], 0.20, z_l3 + 0.25, z_south_rf - 0.95, MATERIALS["glass_clear"])
    for wy in range(-4, 29, 4):
        add_oriented_box_ft(me, (51.8, float(wy)), 0.60, 0.24, 0.0, z_l3 + 0.25, z_south_rf - 0.95, MATERIALS["mullion_bronze"])
    add_louver_bank_ft(me, (52.2, 28.0), (52.2, -4.0), z_l3 + 2.1, z_south_rf - 1.0, spacing_ft=2.2, blade_depth_ft=1.0)

    # =========================================================================
    # ONE-STORY SOUTH ENTRANCE WING (RARE BOOK AUDITORIUM, LOBBY & WEST WING)
    # =========================================================================
    # East Rare Book & Windowless Brick Auditorium Volume (X = +16.5..+61.5, Y = -59.5..-8.8)
    add_wall_strip_ft(
        me,
        [(51.8, -8.8), (61.5, -8.8), (61.5, -59.5), (19.5, -59.5), (16.5, -50.8)],
        1.35,
        z_lobby - 0.55,
        z_south_rf,
        MATERIALS["buff_brick"],
    )

    # Main South Entrance Facade: Glazed Entry Vestibule (X = -22.5..+4.5) flanked by Buff-Brick Walls
    add_wall_strip_ft(me, [(16.5, -50.8), (4.5, -50.8)], 1.30, z_lobby - 0.4, z_south_rf, MATERIALS["buff_brick"])
    # Entry Vestibule Bronze & Glass Doors + Clerestory
    add_wall_strip_ft(me, [(4.5, -50.8), (-22.5, -50.8)], 0.22, z_lobby, z_canopy + 0.15, MATERIALS["glass_clear"])
    add_wall_strip_ft(me, [(4.5, -50.8), (-22.5, -50.8)], 1.25, z_canopy + 0.15, z_south_rf, MATERIALS["buff_brick"])
    for vx in (-22.5, -15.5, -9.0, -2.5, 4.5):
        add_oriented_box_ft(me, (vx, -50.8), 0.28, 0.65, 0.0, z_lobby, z_canopy + 0.15, MATERIALS["mullion_bronze"])

    # South-West Administration & Staff Offices Facade (X = -91.5..-22.5 along Grid 2, with high window strip)
    add_wall_strip_ft(me, [(-22.5, -50.8), (-91.5, -50.8)], 1.25, z_lobby - 0.4, z_lobby + 1.35, MATERIALS["buff_brick"])
    add_wall_strip_ft(me, [(-22.5, -50.8), (-91.5, -50.8)], 0.20, z_lobby + 1.35, z_lobby + 2.65, MATERIALS["glass_clear"])
    add_wall_strip_ft(me, [(-22.5, -50.8), (-91.5, -50.8)], 1.25, z_lobby + 2.65, z_south_rf, MATERIALS["buff_brick"])
    add_louver_bank_ft(me, (-24.0, -51.2), (-90.0, -51.2), z_lobby + 1.40, z_lobby + 2.60, spacing_ft=2.5, blade_depth_ft=0.85)

    # West Cataloging & Bindery Wing Perimeter (stepping along Grid 3 -> X = -126.5 -> Grid 6)
    add_wall_strip_ft(
        me,
        [(-91.5, -50.8), (-91.5, -28.0), (-126.5, -28.0), (-126.5, 1.5), (-77.5, 1.5)],
        1.25,
        z_l2 - 0.5,
        z_south_rf,
        MATERIALS["buff_brick"],
    )

    # Key Interior Architectural Partitions in South Wing (Lobby / Auditorium / Catalog)
    add_wall_strip_ft(me, [(18.0, -50.8), (18.0, -8.8)], 0.75, z_lobby, z_south_rf - 0.3, MATERIALS["white_plaster"])
    add_wall_strip_ft(me, [(-24.0, -50.8), (-24.0, -21.0)], 0.75, z_lobby, z_south_rf - 0.3, MATERIALS["white_plaster"])

    # Cantilevered South Entry Canopy / Portico Marquee (X = -23.5..+5.5, Y = -50.8..-66.0, Z = +3.25 m)
    canopy_poly = [(-23.5, -50.8), (5.5, -50.8), (5.5, -66.0), (-23.5, -66.0)]
    add_extruded_polygon_ft(me, canopy_poly, z_canopy - 0.16, z_canopy + 0.06, MATERIALS["copper_roof"], MATERIALS["copper_roof"], MATERIALS["hemlock_slat"])
    # Slender white steel portico columns supporting outer edge of Entry Canopy
    for cx_ft in (-21.5, -9.0, 3.5):
        add_cylinder_ft(me, (cx_ft, -64.5), 0.38, 0.54, z_canopy - 0.16, MATERIALS["white_column"], sides=14)

    return grp_str, grp_env
