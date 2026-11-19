"""
Layers 5 & 6: Structural Columns/H-Piers (`5_Structural_Frame`) &
Buff-Brick Faceted Envelope, Curtain Walls & South Wing (`6_Envelope_And_South_Wing`).

  - 18"Ø round white concrete columns (including the 3 paired twin-column clusters
    on Rays B, C, D at 5'-4" c/c and the multi-story Well columns rising cleanly
    into the concave plaster reflector vault and below the 1.20 m Fan Roof plenum!)
  - 3 full-height Buff-Brick & Dark-Steel Perimeter H-Piers (B, C, D)
  - 3-Story Faceted North Buff-Brick Curtain Wall (Bays A-B, B-C, C-D, D-E) with
    ribbon window bands, bronze mullions, and exterior vertical wood sun louvers
  - Periodical Lounge East Mt. Hood floor-to-ceiling picture window & louvers
  - One-Story South Entrance Wing (Taller SE Brick Auditorium volume, Glazed Projecting
    Vestibule 316, West Cataloging Wing) & South Entry Canopy with Open Pergola Trellises!
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
    offset_polyline_right_ft,
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

    # Collar split points `cL` (on L_tip_out->L_bot_out) and `cR` (on R_tip_out->R_bot_out)
    # plus mid-leg spine vertices `bL`, `bR` opposite `wL_out`, `wR_out` so `collar_ccw` never
    # grazes the tapered pocket corners `pts_m[2]` / `pts_m[3]`.
    cL = _lerp2(pts_m[0], pts_m[11], 0.13)
    cR = _lerp2(pts_m[5], pts_m[6], 0.13)
    bL = (
        pts_m[2][0] + 0.5 * (pts_m[0][0] - pts_m[1][0]),
        pts_m[2][1] + 0.5 * (pts_m[0][1] - pts_m[1][1]),
    )
    bR = (
        pts_m[3][0] + 0.5 * (pts_m[5][0] - pts_m[4][0]),
        pts_m[3][1] + 0.5 * (pts_m[5][1] - pts_m[4][1]),
    )

    # Sloped roof-plenum cap height `_z_leg_m(pt)` so interior reading-room alcove legs (`p6..p11`)
    # rise cleanly above the sloped ceiling soffit (+Z) while staying strictly buried below the built-up roof!
    wp3a_m = xy_m(AaltoGeometry.WP3A)
    r_hinge_m = m_ft(65.5)
    r_outer_ref_m = max(
        r_hinge_m + 1.0,
        min(
            math.hypot(pts_m[2][0] - wp3a_m[0], pts_m[2][1] - wp3a_m[1]),
            math.hypot(pts_m[3][0] - wp3a_m[0], pts_m[3][1] - wp3a_m[1]),
        )
        + m_ft(0.8),
    )

    def _z_leg_m(pt_xy: tuple[float, float]) -> float:
        r_m = math.hypot(pt_xy[0] - wp3a_m[0], pt_xy[1] - wp3a_m[1])
        u = max(0.0, min(1.0, (r_m - r_hinge_m) / (r_outer_ref_m - r_hinge_m)))
        return (z_fan_low_m + 0.08) + u * ((z_top_m - 0.67) - (z_fan_low_m + 0.08))

    leg_L_ccw = [cL, pts_m[11], pts_m[10], pts_m[9], bL]
    leg_R_ccw = [pts_m[8], pts_m[7], pts_m[6], cR, bR]
    collar_ccw = [pts_m[0], cL, bL, pts_m[9], pts_m[8], bR, cR, pts_m[5], pts_m[4], pts_m[3], pts_m[2], pts_m[1]]

    if not has_alcove_window:
        for sub_ccw, is_collar in ((leg_L_ccw, False), (leg_R_ccw, False), (collar_ccw, True)):
            _, tris = triangulate_polygon_2d(sub_ccw)
            for i0, i1, i2 in tris:
                a, b, c = sub_ccw[i0], sub_ccw[i1], sub_ccw[i2]
                za = z_top_m if is_collar else _z_leg_m(a)
                zb = z_top_m if is_collar else _z_leg_m(b)
                zc = z_top_m if is_collar else _z_leg_m(c)
                add_tri(mesh_struct, (*a, za), (*b, zb), (*c, zc), brick_top)
                add_tri(mesh_struct, (*a, z_bot_m), (*c, z_bot_m), (*b, z_bot_m), conc_bot)

        full_ccw = [pts_m[0], cL, pts_m[11], pts_m[10], pts_m[9], pts_m[8], pts_m[7], pts_m[6], cR, pts_m[5], pts_m[4], pts_m[3], pts_m[2], pts_m[1]]
        alcove_edges = {3, 4, 5}  # p10->p9, p9->p8, p8->p7
        m = len(full_ccw)
        for ei in range(m):
            p0, p1 = full_ccw[ei], full_ccw[(ei + 1) % m]
            add_quad(mesh_struct, (*p0, z_bot_m), (*p1, z_bot_m), (*p1, z_l3_m), (*p0, z_l3_m), brick_side)
            mat_l3 = plaster if ei in alcove_edges else brick_side
            add_quad(mesh_struct, (*p0, z_l3_m), (*p1, z_l3_m), (*p1, _z_leg_m(p1)), (*p0, _z_leg_m(p0)), mat_l3)

        mc = len(collar_ccw)
        for ei in range(mc):
            p0, p1 = collar_ccw[ei], collar_ccw[(ei + 1) % mc]
            add_quad(mesh_struct, (*p0, _z_leg_m(p0)), (*p1, _z_leg_m(p1)), (*p1, z_top_m), (*p0, z_top_m), brick_side)
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

    collar_L = [pts_m[0], cL, bL, pts_m[9], wi0, wo0, pts_m[2], pts_m[1]]
    collar_C = [wo0, wi0, wi1, wo1]
    collar_R = [pts_m[5], pts_m[4], pts_m[3], wo1, wi1, pts_m[8], bR, cR]

    for sub_ccw, is_collar in (
        (leg_L_ccw, False),
        (leg_R_ccw, False),
        (collar_L, True),
        (collar_C, True),
        (collar_R, True),
    ):
        _, tris = triangulate_polygon_2d(sub_ccw)
        for i0, i1, i2 in tris:
            a, b, c = sub_ccw[i0], sub_ccw[i1], sub_ccw[i2]
            za = z_top_m if is_collar else _z_leg_m(a)
            zb = z_top_m if is_collar else _z_leg_m(b)
            zc = z_top_m if is_collar else _z_leg_m(c)
            add_tri(mesh_struct, (*a, za), (*b, zb), (*c, zc), brick_top)
            add_tri(mesh_struct, (*a, z_bot_m), (*c, z_bot_m), (*b, z_bot_m), conc_bot)

    z_low_tiers = [z_bot_m, z_l3_m, z_sill, z_head, None]
    low_L = [pts_m[0], cL, pts_m[11], pts_m[10], pts_m[9], wi0, wo0, pts_m[2], pts_m[1]]
    low_R = [pts_m[5], pts_m[4], pts_m[3], wo1, wi1, pts_m[8], pts_m[7], pts_m[6], cR]

    for ti in range(len(z_low_tiers) - 1):
        za_fixed, zb_fixed = z_low_tiers[ti], z_low_tiers[ti + 1]
        in_l3 = ti >= 1
        for ei in range(len(low_L)):
            if ei == 5:
                continue
            p0, p1 = low_L[ei], low_L[(ei + 1) % len(low_L)]
            zb0 = _z_leg_m(p0) if zb_fixed is None else zb_fixed
            zb1 = _z_leg_m(p1) if zb_fixed is None else zb_fixed
            mat = plaster if (in_l3 and ei in (3, 4)) else brick_side
            add_quad(mesh_struct, (*p0, za_fixed), (*p1, za_fixed), (*p1, zb1), (*p0, zb0), mat)
        for ei in range(len(low_R)):
            if ei == 3:
                continue
            p0, p1 = low_R[ei], low_R[(ei + 1) % len(low_R)]
            zb0 = _z_leg_m(p0) if zb_fixed is None else zb_fixed
            zb1 = _z_leg_m(p1) if zb_fixed is None else zb_fixed
            mat = plaster if (in_l3 and ei in (4, 5)) else brick_side
            add_quad(mesh_struct, (*p0, za_fixed), (*p1, za_fixed), (*p1, zb1), (*p0, zb0), mat)
        if ti != 2:
            zbo0 = _z_leg_m(wo0) if zb_fixed is None else zb_fixed
            zbo1 = _z_leg_m(wo1) if zb_fixed is None else zb_fixed
            zbi0 = _z_leg_m(wi0) if zb_fixed is None else zb_fixed
            zbi1 = _z_leg_m(wi1) if zb_fixed is None else zb_fixed
            add_quad(mesh_struct, (*wo1, za_fixed), (*wo0, za_fixed), (*wo0, zbo0), (*wo1, zbo1), brick_side)
            add_quad(mesh_struct, (*wi0, za_fixed), (*wi1, za_fixed), (*wi1, zbi1), (*wi0, zbi0), plaster if in_l3 else brick_side)

    collar_sub_ccw = [pts_m[0], cL, bL, pts_m[9], wi0, wi1, pts_m[8], bR, cR, pts_m[5], pts_m[4], pts_m[3], wo1, wo0, pts_m[2], pts_m[1]]
    for ei in range(len(collar_sub_ccw)):
        p0, p1 = collar_sub_ccw[ei], collar_sub_ccw[(ei + 1) % len(collar_sub_ccw)]
        add_quad(mesh_struct, (*p0, _z_leg_m(p0)), (*p1, _z_leg_m(p1)), (*p1, z_top_m), (*p0, z_top_m), brick_side)

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
      - High Level 3 clerestory window band (`+2.18 .. +4.56 m`) screened by full-height exterior
        vertical wood sun-shading louvers (`+2.04 .. +5.34 m`, Detail 9 on Sheet 11-a11).
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
    z_l3_head = 4.56                 # +4.56 m (just below the +4.62 m upward-sweeping ceiling soffit!)

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
        (z_l3_head, 4.61),
    ]
    for zb, zt in plaster_bands:
        add_wall_strip_ft(mesh, [pl0, pl1], 0.37, zb, zt, MATERIALS["white_plaster"], offset_mode="right")
    # Inner brick parapet band above the +4.95 m outer roof deck
    add_wall_strip_ft(mesh, [pl0, pl1], 0.37, 4.96, z_parapet_m, MATERIALS["buff_brick"], offset_mode="right")

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
    trim_start_ft: float = 0.0,
    trim_end_ft: float = 0.0,
):
    """
    Build the stepped-back Level 1 exposed-concrete foundation wall & high clerestory
    ribbon windows (`(M)` on North Elevation Sheet 12) flush with the H-column U-channels.
    """
    dx, dy = p1_ft[0] - p0_ft[0], p1_ft[1] - p0_ft[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    ix, iy = uy, -ux

    q0 = (p0_ft[0] + ux * trim_start_ft, p0_ft[1] + uy * trim_start_ft)
    q1 = (p1_ft[0] - ux * trim_end_ft, p1_ft[1] - uy * trim_end_ft)

    z_win_bot = z_l1_m + 2.15
    z_win_top = z_l2_m - 0.55
    add_wall_strip_ft(mesh, [q0, q1], 1.15, z_base_m, z_win_bot, MATERIALS["concrete"], offset_mode="right")
    add_wall_strip_ft(mesh, [q0, q1], 1.15, z_win_top, z_l2_m - 0.30, MATERIALS["concrete"], offset_mode="right")

    g0 = (q0[0] + ix * 0.45, q0[1] + iy * 0.45)
    g1 = (q1[0] + ix * 0.45, q1[1] + iy * 0.45)
    add_wall_strip_ft(mesh, [g0, g1], 0.18, z_win_bot, z_win_top, MATERIALS["glass_clear"], offset_mode="center")

    ang_deg = math.degrees(math.atan2(dy, dx))
    eff_L = max(8.0, L - trim_start_ft - trim_end_ft)
    n_mull = max(4, int(eff_L / 6.0))
    for k in range(n_mull + 1):
        t = k / n_mull
        mx = g0[0] + (g1[0] - g0[0]) * t
        my = g0[1] + (g1[1] - g0[1]) * t
        add_oriented_box_ft(mesh, (mx, my), 0.22, 0.48, ang_deg, z_win_bot, z_win_top, MATERIALS["mullion_bronze"])


def _add_mitered_strip_between_offsets_ft(
    mesh,
    pts_ft: list[tuple[float, float]],
    d_outer_ft: float,
    d_inner_ft: float,
    z0_m: float,
    z1_m: float,
    attrs: dict,
    side_attrs: dict | None = None,
):
    """Extrude an exact mitered wall wythe bounded by inward offsets `d_outer_ft` and `d_inner_ft`."""
    outer_chain = offset_polyline_right_ft(pts_ft, d_outer_ft)
    inner_chain = offset_polyline_right_ft(pts_ft, d_inner_ft)
    poly_ft = [*outer_chain, *reversed(inner_chain)]
    add_extruded_polygon_ft(mesh, poly_ft, z0_m, z1_m, attrs, side_attrs or attrs)


def build_envelope_and_south_wing(scene):
    G = AaltoGeometry
    z_crawl = m_ft(G.Z_CRAWL_FT)            # -10.36 m
    z_l1 = m_ft(G.Z_L1_FT)                  #  -8.08 m
    z_l2 = m_ft(G.Z_L2_FT)                  #  -3.81 m
    z_l3 = m_ft(G.Z_L3_FT)                  #   0.00 m
    z_lobby = m_ft(G.Z_LOBBY_FT)            #  +0.61 m
    z_canopy = m_ft(G.Z_CANOPY_FT)          #  +3.25 m
    z_s_ceil = m_ft(G.Z_SOUTH_CEIL_FT)      #  +3.30 m
    z_fan_ceil = m_ft(G.Z_FAN_CEIL_FT)      #  +3.45 m
    z_s_par = m_ft(G.Z_SOUTH_PARAPET_FT)    #  +4.22 m
    z_fan_high = m_ft(G.Z_FAN_ROOF_HIGH_FT) #  +4.95 m
    z_aud_par = m_ft(G.Z_AUDITORIUM_PARAPET_FT)  # +6.15 m
    z_par_n = m_ft(G.Z_FAN_PARAPET_N_FT)    #  +5.44 m

    # =========================================================================
    # LAYER 5: STRUCTURAL COLUMNS, PAIRED COLUMNS & 3 IRREGULAR H-COLUMNS
    # =========================================================================
    grp_str = create_scene_group(scene, "5_Structural_Frame")
    ms = grp_str.mesh

    grp_env = create_scene_group(scene, "6_Envelope_And_South_Wing")
    me = grp_env.mesh

    # 6 Multi-Story Well & Throat Columns:
    #   - `Well_1_WNW`, `Well_2_NNW`, `Well_3_NNE` rise inside the Curved North Daylight Scoop on Radial
    #     Axes B, C, D and stop at the soffit of the radial skylight header beams (`+3.85 m`,
    #     Sheet 48-s17 Detail B: "HEADER BEAM TO CONC COLUMN"; beams built in `roof_and_skylights`).
    #   - `Well_W_South`, `Well_4_ENE`, `South_W1` terminate at the South interior ceiling soffit (`z_s_ceil = +3.30 m`).
    scoop_well_cols = {"Well_1_WNW", "Well_2_NNW", "Well_3_NNE"}
    for cname, cpt in G.WELL_COLS_FT.items():
        z_top = 3.85 if cname in scoop_well_cols else z_s_ceil
        add_cylinder_ft(ms, cpt, 0.78, z_l1, z_top, MATERIALS["white_column"], sides=18)

    # 6 Paired Twin 18"Ø Columns straddling WP #3 Radial Axes B, C, D (5'-4" c/c, Sheet 06-a6 & Sheet 47-s16 Detail D):
    # Terminate cleanly at the flat fan ceiling soffit (`z_fan_ceil = +3.45 m`), below the 1.20 m 24WF68 roof plenum!
    for cpt in G.PAIRED_COLS_FT.values():
        add_cylinder_ft(ms, cpt, 0.75, z_l1, z_fan_ceil, MATERIALS["white_column"], sides=18)

    # South Wing & Periodical Lounge Structural Columns (terminating cleanly at interior ceiling soffit `z_s_ceil = +3.30 m`)
    for cpt in G.SOUTH_WING_COLS_FT:
        z_bot = z_l2 if cpt[1] > -29.0 else z_lobby - 0.8
        add_cylinder_ft(ms, cpt, 0.68, z_bot, z_s_ceil, MATERIALS["white_column"], sides=14)

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
            z_fan_low_m=z_fan_ceil,
            z_top_m=z_par_n + 0.01,
            has_alcove_window=(hp_idx == 2),  # HPier_D (Ray D = 65.72° ENE) frames Mt. Hood on entry!
        )
        # Exterior rainwater scupper leader pipe tucked into the left corner of the recessed H-pocket (Sheets 07-a7 & 11-a11)
        wx, wy = _lerp2(hp_poly[2], hp_poly[3], 0.12)
        tx = 0.5 * (hp_poly[1][0] + hp_poly[4][0]) - 0.5 * (hp_poly[2][0] + hp_poly[3][0])
        ty = 0.5 * (hp_poly[1][1] + hp_poly[4][1]) - 0.5 * (hp_poly[2][1] + hp_poly[3][1])
        tl = max(1e-4, math.hypot(tx, ty))
        scup_pt = (wx + (tx / tl) * 0.42, wy + (ty / tl) * 0.42)
        add_cylinder_ft(ms, scup_pt, 0.16, z_crawl + 0.6, z_par_n - 0.18, MATERIALS["copper_roof"], sides=12)

    # Radial Structural Ceiling Ribs below the flat acoustic soffit (`z_fan_ceil - 0.14 .. z_fan_ceil`)
    for b_deg in (152.0, G.RAY_B_DEG, 119.0, G.RAY_C_DEG, 83.0, G.RAY_D_DEG, 49.0):
        p_in = polar_pt(G.WP3A, 42.2, b_deg)
        p_out = polar_pt(G.WP3A, 65.2, b_deg)
        add_wall_strip_ft(ms, [p_in, p_out], 0.65, z_fan_ceil - 0.14, z_fan_ceil, MATERIALS["white_soffit"])

    # =========================================================================
    # LAYER 6: FACETED NORTH BRICK CURTAIN WALL, ACUTE PROWS & SOUTH WING
    # =========================================================================
    # 4 Cantilevered Level 2–3 Faceted Curtain-Wall Bays:
    #   - Bay 0 (West) trims 3.85 ft (`3'-10"`) from `PT_A` for the solid mitered West Jamb (`Sheet 06-a6 Detail 1`)
    #   - Bay 3 (East) trims 4.10 ft (`4'-1"`) from `PT_E` for the solid mitered East Prow Jamb (`Sheet 06-a6 Detail 2`)
    curtain_bays = get_faceted_curtain_bays_ft()
    west_jamb_trim = 3.85
    east_jamb_trim = 4.10
    for b_idx, (bp0, bp1) in enumerate(curtain_bays):
        t_s = west_jamb_trim if b_idx == 0 else 0.0
        t_e = east_jamb_trim if b_idx == len(curtain_bays) - 1 else 0.0
        _add_faceted_curtain_bay(me, bp0, bp1, z_l2, z_l3, z_par_n + 0.01, trim_start_ft=t_s, trim_end_ft=t_e)

    # Stepped-Back Level 1 Exposed-Concrete Foundation Wall, Clerestory Windows & Mitered L1 Flank Corners
    l1_perim = get_north_perimeter_with_pockets_ft(level=1)
    l1_west_trim = 2.80
    l1_east_trim = 3.10
    l1_bays = [
        (l1_perim[0], l1_perim[1], z_crawl + 1.0, l1_west_trim, 0.0),
        (l1_perim[2], l1_perim[3], z_crawl + 0.6, 0.0, 0.0),
        (l1_perim[4], l1_perim[5], z_crawl + 0.6, 0.0, 0.0),
        (l1_perim[6], l1_perim[7], z_crawl + 1.1, 0.0, l1_east_trim),
    ]
    for lp0, lp1, zb_l1, ts1, te1 in l1_bays:
        _add_stepped_l1_concrete_bay(me, lp0, lp1, zb_l1, z_l1, z_l2, trim_start_ft=ts1, trim_end_ft=te1)

    # Mitered Level 1 Exposed-Concrete West & East Acute Corner / Flank Retaining Walls (Sheets 03-a3 & 11-a11)
    l1_b0_len = math.hypot(l1_perim[1][0] - l1_perim[0][0], l1_perim[1][1] - l1_perim[0][1])
    l1_b3_len = math.hypot(l1_perim[7][0] - l1_perim[6][0], l1_perim[7][1] - l1_perim[6][1])
    l1_jamb_a = _lerp2(l1_perim[0], l1_perim[1], l1_west_trim / l1_b0_len)
    l1_jamb_e = _lerp2(l1_perim[6], l1_perim[7], 1.0 - l1_east_trim / l1_b3_len)
    _add_mitered_strip_between_offsets_ft(
        me,
        [(-77.5, 1.5), G.PT_A_INNER_JUNC, l1_perim[0], l1_jamb_a],
        0.0,
        1.15,
        z_crawl + 1.0,
        z_l2 - 0.30,
        MATERIALS["concrete"],
    )
    _add_mitered_strip_between_offsets_ft(
        me,
        [l1_jamb_e, l1_perim[7], (43.5, 24.5), G.WELL_COLS_FT["Well_4_ENE"]],
        0.0,
        1.15,
        z_crawl + 1.1,
        z_l2 - 0.30,
        MATERIALS["concrete"],
    )

    # Continuous Concrete Cantilever Soffit wrapping seamlessly around North Curtain Wall & BOTH Acute Prows!
    soffit_outer = offset_polyline_right_ft([G.PT_A_INNER_JUNC, *get_north_perimeter_with_pockets_ft(level=3), G.PT_LOUNGE_JUNC], 0.42)
    soffit_inner = offset_polyline_right_ft([G.PT_A_INNER_JUNC, *l1_perim, (43.5, 24.5)], 0.85)
    cantilever_soffit_poly = [*soffit_outer, *reversed(soffit_inner)]
    add_extruded_polygon_ft(me, cantilever_soffit_poly, z_l2 - 0.34, z_l2 - 0.28, MATERIALS["concrete"], MATERIALS["concrete"])

    # Exact Acute Mitered Buff-Brick Veneer Corners & Flank Walls (`Sheet 06-a6 Details 1 & 2`, `Sheet 11-a11`):
    b0_p0, b0_p1 = curtain_bays[0]
    b3_p0, b3_p1 = curtain_bays[-1]
    jamb_A_pt = _lerp2(b0_p0, b0_p1, west_jamb_trim / math.hypot(b0_p1[0] - b0_p0[0], b0_p1[1] - b0_p0[1]))
    jamb_E_pt = _lerp2(b3_p0, b3_p1, 1.0 - east_jamb_trim / math.hypot(b3_p1[0] - b3_p0[0], b3_p1[1] - b3_p0[1]))

    # 1. West Acute Corner (`PT_A`, 73.3° interior wedge):
    #    - Outer `0.72 ft` Mount Angel buff-brick veneer wythe rising unbroken from cantilevered soffit (`z_l2 - 0.34`)
    #      to parapet coping (`z_par_n + 0.01`), plus throat return `(-77.5, 1.5) -> PT_A_INNER_JUNC` up to `z_s_par`
    _add_mitered_strip_between_offsets_ft(
        me,
        [G.PT_A_INNER_JUNC, G.PT_A, jamb_A_pt],
        0.0,
        0.72,
        z_l2 - 0.34,
        z_par_n + 0.01,
        MATERIALS["buff_brick"],
    )
    #    - Inner `0.40 ft` (`0.72 .. 1.12 ft` inward) brick parapet backing above outer roof deck (`z_fan_high - 0.02 .. z_par_n + 0.01`)
    _add_mitered_strip_between_offsets_ft(
        me,
        [_lerp2(G.PT_A, G.PT_A_INNER_JUNC, 0.94), G.PT_A, jamb_A_pt],
        0.72,
        1.12,
        z_fan_high - 0.02,
        z_par_n + 0.01,
        MATERIALS["buff_brick"],
    )
    _add_mitered_strip_between_offsets_ft(
        me,
        [(-77.5, 1.5), G.PT_A_INNER_JUNC],
        0.0,
        1.12,
        z_l2 - 0.34,
        z_s_par,
        MATERIALS["buff_brick"],
    )
    #    - Inner `0.37 ft` (`0.75 .. 1.12 ft` inward) white-plaster reading-room / stack backing wythe across L2 & L3
    for zb_pl, zt_pl in ((z_l2 + 0.01, z_l3 - 0.30), (z_l3 + 0.01, z_fan_ceil - 0.02)):
        _add_mitered_strip_between_offsets_ft(
            me,
            [_lerp2(G.PT_A, G.PT_A_INNER_JUNC, 0.94), G.PT_A, jamb_A_pt],
            0.75,
            1.12,
            zb_pl,
            zt_pl,
            MATERIALS["white_plaster"],
        )

    # 2. East Acute Prow (`PT_E`, 56.5° interior wedge, `Sheet 06-a6 Detail 2 EAST JAMB`):
    #    - Outer `0.72 ft` Mount Angel buff-brick veneer wythe mitering cleanly to a sharp knife-edge at `PT_E`
    #      from Level 2 cantilevered soffit (`z_l2 - 0.34`) up to copper coping underside (`z_par_n + 0.01`)!
    _add_mitered_strip_between_offsets_ft(
        me,
        [jamb_E_pt, G.PT_E, G.PT_LOUNGE_JUNC],
        0.0,
        0.72,
        z_l2 - 0.34,
        z_par_n + 0.01,
        MATERIALS["buff_brick"],
    )
    #    - Inner `0.40 ft` (`0.72 .. 1.12 ft` inward) brick parapet backing above outer roof deck (`z_fan_high - 0.02 .. z_par_n + 0.01`)
    _add_mitered_strip_between_offsets_ft(
        me,
        [jamb_E_pt, G.PT_E, _lerp2(G.PT_E, G.PT_LOUNGE_JUNC, 0.965)],
        0.72,
        1.12,
        z_fan_high - 0.02,
        z_par_n + 0.01,
        MATERIALS["buff_brick"],
    )
    #    - Inner `0.37 ft` (`0.75 .. 1.12 ft` inward) white-plaster reading-room / stack backing wythe across L2 & L3
    for zb_pl, zt_pl in ((z_l2 + 0.01, z_l3 - 0.30), (z_l3 + 0.01, z_fan_ceil - 0.02)):
        _add_mitered_strip_between_offsets_ft(
            me,
            [jamb_E_pt, G.PT_E, _lerp2(G.PT_E, G.PT_LOUNGE_JUNC, 0.965)],
            0.75,
            1.12,
            zb_pl,
            zt_pl,
            MATERIALS["white_plaster"],
        )

    # Periodical Lounge East Wall featuring Mt. Hood Picture Window & Wood Louvers!
    # Solid brick corners + floor-to-ceiling glazing from Y = -4.0..+29.0 ft along X = +51.8 ft
    add_wall_strip_ft(me, [(51.8, 32.8), (51.8, 28.5)], 1.25, z_l2 - 0.8, z_s_par, MATERIALS["buff_brick"], offset_mode="right")
    add_wall_strip_ft(me, [(51.8, -4.5), (51.8, -8.8)], 1.25, z_l2 - 0.8, z_s_par, MATERIALS["buff_brick"], offset_mode="right")
    add_wall_strip_ft(me, [(51.8, 28.5), (51.8, -4.5)], 1.15, z_l2 - 0.8, z_l3 + 0.25, MATERIALS["buff_brick"], offset_mode="right")
    add_wall_strip_ft(me, [(51.8, 28.5), (51.8, -4.5)], 1.15, z_s_ceil - 0.05, z_s_par, MATERIALS["buff_brick"], offset_mode="right")
    # Tall Mt. Hood Picture Window (L3) & Seminar Ribbon Window (L2)
    add_wall_strip_ft(me, [(51.8, 28.5), (51.8, -4.5)], 0.20, z_l3 + 0.25, z_s_ceil - 0.05, MATERIALS["glass_clear"])
    for wy in range(-4, 29, 4):
        add_oriented_box_ft(me, (51.8, float(wy)), 0.60, 0.24, 0.0, z_l3 + 0.25, z_s_ceil - 0.05, MATERIALS["mullion_bronze"])
    add_louver_bank_ft(me, (52.2, 28.0), (52.2, -4.0), z_l3 + 2.1, z_s_ceil - 0.10, spacing_ft=2.2, blade_depth_ft=1.0)

    # =========================================================================
    # ONE-STORY SOUTH ENTRANCE WING (TALLER AUDITORIUM, LOBBY & WEST WING)
    # =========================================================================
    # Rare Book Vault East Wall (rising to z_s_par = +4.22 m)
    add_wall_strip_ft(
        me,
        [(51.8, -8.8), (61.5, -8.8), (61.5, -21.0)],
        1.35,
        z_lobby - 0.55,
        z_s_par,
        MATERIALS["buff_brick"],
        offset_mode="right",
    )

    # Taller SE Auditorium Windowless Buff-Brick Envelope (rising up to z_aud_par = +6.15 m!)
    aud_envelope_pts = [
        (18.0, -21.0),
        (18.0, -13.5),
        (36.0, -13.5),
        (36.0, -21.0),
        (61.5, -21.0),
        (61.5, -59.5),
        (19.5, -59.5),
        (16.5, -50.8),
        (18.0, -21.0),
    ]
    add_wall_strip_ft(
        me,
        aud_envelope_pts,
        1.35,
        z_lobby - 0.55,
        z_aud_par,
        MATERIALS["buff_brick"],
        offset_mode="right",
    )

    # Main South Entrance Facade: Flanking Buff-Brick Walls & Projecting Glazed Vestibule 316
    add_wall_strip_ft(me, [(16.5, -50.8), (0.0, -50.8)], 1.30, z_lobby - 0.4, z_s_par, MATERIALS["buff_brick"])
    add_wall_strip_ft(me, [(0.0, -50.8), (-18.0, -50.8)], 1.25, z_canopy - 0.16, z_s_par, MATERIALS["buff_brick"])

    # Projecting Glazed VESTIBULE 316 (X = -18.0..0.0, Y = -57.5..-50.8, Z = z_lobby .. z_canopy - 0.16)
    add_wall_strip_ft(me, [(-18.0, -50.8), (-18.0, -57.5)], 0.20, z_lobby, z_canopy - 0.16, MATERIALS["glass_clear"])
    add_wall_strip_ft(me, [(-18.0, -57.5), (0.0, -57.5)], 0.20, z_lobby, z_canopy - 0.16, MATERIALS["glass_clear"])
    add_wall_strip_ft(me, [(0.0, -57.5), (0.0, -50.8)], 0.20, z_lobby, z_canopy - 0.16, MATERIALS["glass_clear"])
    add_oriented_box_ft(me, (-18.0, -57.5), 0.35, 0.35, 0.0, z_lobby, z_canopy - 0.16, MATERIALS["mullion_bronze"])
    add_oriented_box_ft(me, (0.0, -57.5), 0.35, 0.35, 0.0, z_lobby, z_canopy - 0.16, MATERIALS["mullion_bronze"])
    for vx in (-14.0, -12.0, -9.0, -6.0, -4.0):
        add_oriented_box_ft(me, (vx, -57.5), 0.28, 0.55, 0.0, z_lobby, z_canopy - 0.16, MATERIALS["mullion_bronze"])
    add_wall_strip_ft(me, [(-12.0, -57.5), (-6.0, -57.5)], 0.28, z_lobby + 2.10, z_lobby + 2.20, MATERIALS["mullion_bronze"])
    for vy in (-53.0, -55.2):
        add_oriented_box_ft(me, (-18.0, vy), 0.55, 0.28, 0.0, z_lobby, z_canopy - 0.16, MATERIALS["mullion_bronze"])
        add_oriented_box_ft(me, (0.0, vy), 0.55, 0.28, 0.0, z_lobby, z_canopy - 0.16, MATERIALS["mullion_bronze"])

    # South-West Administration & Staff Offices Facade (X = -91.5..-18.0 along Grid 2, with high window strip)
    add_wall_strip_ft(me, [(-18.0, -50.8), (-91.5, -50.8)], 1.25, z_lobby - 0.4, z_lobby + 1.35, MATERIALS["buff_brick"])
    add_wall_strip_ft(me, [(-18.0, -50.8), (-91.5, -50.8)], 0.20, z_lobby + 1.35, z_lobby + 2.65, MATERIALS["glass_clear"])
    add_wall_strip_ft(me, [(-18.0, -50.8), (-91.5, -50.8)], 1.25, z_lobby + 2.65, z_s_par, MATERIALS["buff_brick"])
    add_louver_bank_ft(me, (-19.0, -51.2), (-90.0, -51.2), z_lobby + 1.40, z_lobby + 2.60, spacing_ft=2.5, blade_depth_ft=0.85)

    # West Cataloging & Bindery Wing Perimeter (stepping along Grid 3 -> X = -126.5 -> Grid 6)
    add_wall_strip_ft(
        me,
        [(-91.5, -50.8), (-91.5, -28.0), (-126.5, -28.0), (-126.5, 1.5), (-77.5, 1.5)],
        1.25,
        z_l2 - 0.5,
        z_s_par,
        MATERIALS["buff_brick"],
    )

    # Central Solid Copper/White-Fascia + Hemlock-Soffit Portico Marquee (X = -19.0..+1.0, Y = -50.8..-66.0)
    canopy_poly = [(-19.0, -50.8), (1.0, -50.8), (1.0, -66.0), (-19.0, -66.0)]
    add_extruded_polygon_ft(
        me,
        canopy_poly,
        z_canopy - 0.16,
        z_canopy + 0.08,
        MATERIALS["copper_roof"],
        MATERIALS["white_soffit"],
        MATERIALS["hemlock_slat"],
    )
    for cx_ft in (-17.5, -9.0, -0.5):
        add_cylinder_ft(me, (cx_ft, -65.0), 0.38, 0.54, z_canopy - 0.16, MATERIALS["white_column"], sides=14)

    # Flanking Open White Pergola Trellises (West: X = -35.0..-19.0; East: X = +1.0..+16.5; Sheet 12-a12)
    z_tr_b = z_canopy - 0.14
    z_tr_t = z_canopy + 0.04
    y_trellis_lines = [-50.8, -55.37, -59.93, -64.5]

    # West Pergola Trellis
    for y_b in y_trellis_lines:
        add_oriented_box_ft(me, (-27.0, y_b), 16.0, 0.36, 0.0, z_tr_b, z_tr_t, MATERIALS["white_column"])
    for x_b in (-35.0, -29.67, -24.33, -19.0):
        for k in range(len(y_trellis_lines) - 1):
            y_mid = 0.5 * (y_trellis_lines[k] + y_trellis_lines[k + 1])
            y_span = (y_trellis_lines[k] - 0.18) - (y_trellis_lines[k + 1] + 0.18)
            add_oriented_box_ft(me, (x_b, y_mid), 0.36, y_span, 0.0, z_tr_b, z_tr_t, MATERIALS["white_column"])
    for c_pt in ((-35.0, -64.5), (-24.33, -64.5), (-35.0, -57.5)):
        add_cylinder_ft(me, c_pt, 0.35, 0.54, z_tr_b, MATERIALS["white_column"], sides=14)

    # East Pergola Trellis
    for y_b in y_trellis_lines:
        add_oriented_box_ft(me, (8.75, y_b), 15.5, 0.36, 0.0, z_tr_b, z_tr_t, MATERIALS["white_column"])
    for x_b in (1.0, 6.17, 11.33, 16.5):
        for k in range(len(y_trellis_lines) - 1):
            y_mid = 0.5 * (y_trellis_lines[k] + y_trellis_lines[k + 1])
            y_span = (y_trellis_lines[k] - 0.18) - (y_trellis_lines[k + 1] + 0.18)
            add_oriented_box_ft(me, (x_b, y_mid), 0.36, y_span, 0.0, z_tr_b, z_tr_t, MATERIALS["white_column"])
    for c_pt in ((16.5, -64.5), (6.17, -64.5), (16.5, -57.5)):
        add_cylinder_ft(me, c_pt, 0.35, 0.54, z_tr_b, MATERIALS["white_column"], sides=14)

    return grp_str, grp_env
