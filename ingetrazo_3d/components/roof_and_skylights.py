"""
Layer 7: Dual-Scoop Daylight Roof, Copper Fascia & 12 Conical Lanterns (`7_Roof_And_Daylight_Scoop`).

Models Alvar Aalto's celebrated Mount Angel daylighting roof system:
  1. Curved Central North Daylight Monitor Scoop (R = 24.0..41.8 ft, peak +6.55 m):
     - Copper-clad curved exterior shell
     - Smooth concave white plaster interior reflector vault
     - Steep North-facing skylight glass with 15 radial aluminum mullions
     - Leaves R = 24.0..41.8 ft completely open below so north light pours straight
       into the double-height Reading Well!
  2. Tipped North Perimeter Fan Roof (+3.81 m sweeping upward to +5.25 m at the
     faceted North Curtain Wall): creates the upward-sweeping interior daylight
     soffit over the Level 3 bookstacks & carrels.
  3. South Wing Built-up Roof (+4.98 m) with weathered copper parapet coping,
     Suspended Slatted Birch Acoustic Ceiling Drum over the Control Desk, and
     all 12 Aalto Conical Roof Skylight Lanterns!
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import AaltoGeometry, get_north_perimeter_with_pockets_ft, polar_pt

from .primitives import (
    MATERIALS,
    add_arc_band_ft,
    add_cylinder_ft,
    add_extruded_polygon_ft,
    add_extruded_polygon_with_holes_ft,
    add_frustum_ft,
    add_oriented_box_ft,
    add_quad,
    add_tri,
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
    xy_m,
)


def _ray_segment_dist_ft(origin: tuple[float, float], deg: float, a: tuple[float, float], b: tuple[float, float]) -> float | None:
    """Intersect ray from `origin` at `deg` with line segment `a -> b`; return distance in ft."""
    rad = math.radians(deg)
    dx, dy = math.cos(rad), math.sin(rad)
    sx, sy = b[0] - a[0], b[1] - a[1]
    denom = dx * sy - dy * sx
    if abs(denom) < 1e-8:
        return None
    qpx, qpy = a[0] - origin[0], a[1] - origin[1]
    t = (qpx * sy - qpy * sx) / denom
    u = (qpx * dy - qpy * dx) / denom
    if t > 1.0 and -0.01 <= u <= 1.01:
        return t
    return None


def _fan_perimeter_chain_ft() -> list[tuple[float, float]]:
    G = AaltoGeometry
    return [
        (-77.5, 1.5),
        G.PT_A_INNER_JUNC,
        *get_north_perimeter_with_pockets_ft(level=3),
        G.PT_LOUNGE_JUNC,
        (19.0, 4.0),
    ]


def _fan_outer_radius_at_angle(deg: float, chain: list[tuple[float, float]]) -> float:
    """Distance from WP3A along `deg` to the pocketed North Fan boundary."""
    G = AaltoGeometry
    best = None
    for idx in range(len(chain) - 1):
        d = _ray_segment_dist_ft(G.WP3A, deg, chain[idx], chain[idx + 1])
        if d is not None and (best is None or d < best):
            best = d
    return best if best is not None else 82.0


def build_roof_and_skylights(scene):
    grp = create_scene_group(scene, "7_Roof_And_Daylight_Scoop")
    mesh = grp.mesh
    G = AaltoGeometry

    z_fan_low = m_ft(G.Z_FAN_ROOF_LOW_FT)   # +3.81 m
    z_south_rf = m_ft(G.Z_SOUTH_ROOF_FT)    # +4.98 m
    z_par_n = m_ft(G.Z_FAN_PARAPET_N_FT)    # +5.33 m
    z_ridge = m_ft(G.Z_SCOOP_RIDGE_FT)      # +6.55 m
    z_lantern = m_ft(G.Z_LANTERN_TOP_FT)    # +5.94 m

    # =========================================================================
    # 1. CURVED CENTRAL NORTH DAYLIGHT MONITOR SCOOP (46° .. 155° around WP3A)
    # =========================================================================
    n_scoop = 36
    deg0, deg1 = 45.0, 156.0
    angles = [deg0 + (deg1 - deg0) * (i / n_scoop) for i in range(n_scoop + 1)]

    # Concave white plaster reflector profile (radius_ft_from_WP3A, z_interior_m, z_exterior_m)
    vault_profile = [
        (G.R_SCOOP_INNER, 3.88, z_south_rf + 0.04),
        (26.8, 4.95, 5.42),
        (30.4, 5.88, 6.02),
        (G.R_SCOOP_RIDGE, z_ridge - 0.10, z_ridge),
    ]

    for i in range(n_scoop):
        a0, a1 = angles[i], angles[i + 1]
        for k in range(len(vault_profile) - 1):
            r_a, zi_a, ze_a = vault_profile[k]
            r_b, zi_b, ze_b = vault_profile[k + 1]
            p00_xy = xy_m(polar_pt(G.WP3A, r_a, a0))
            p10_xy = xy_m(polar_pt(G.WP3A, r_a, a1))
            p11_xy = xy_m(polar_pt(G.WP3A, r_b, a1))
            p01_xy = xy_m(polar_pt(G.WP3A, r_b, a0))

            # Exterior Copper Roof Slope (+Z/+South outward normal)
            add_quad(
                mesh,
                (*p00_xy, ze_a),
                (*p01_xy, ze_b),
                (*p11_xy, ze_b),
                (*p10_xy, ze_a),
                MATERIALS["copper_roof"],
            )
            # Interior Concave White Plaster Daylight Reflector Vault (facing North/Down into Well!)
            add_quad(
                mesh,
                (*p00_xy, zi_a),
                (*p10_xy, zi_a),
                (*p11_xy, zi_b),
                (*p01_xy, zi_b),
                MATERIALS["white_plaster"],
            )
            # Seal outer boundary rims of the curved scoop vault for watertight section capping
            if k == 0:
                add_quad(mesh, (*p00_xy, zi_a), (*p00_xy, ze_a), (*p10_xy, ze_a), (*p10_xy, zi_a), MATERIALS["copper_roof"])
            if k == len(vault_profile) - 2:
                add_quad(mesh, (*p01_xy, ze_b), (*p01_xy, zi_b), (*p11_xy, zi_b), (*p11_xy, ze_b), MATERIALS["copper_roof"])
            if i == 0:
                add_quad(mesh, (*p00_xy, zi_a), (*p01_xy, zi_b), (*p01_xy, ze_b), (*p00_xy, ze_a), MATERIALS["copper_roof"])
            if i == n_scoop - 1:
                add_quad(mesh, (*p10_xy, ze_a), (*p11_xy, ze_b), (*p11_xy, zi_b), (*p10_xy, zi_a), MATERIALS["copper_roof"])

        # Steep North-Facing Skylight Glazing (from Ridge R = 34.8 ft, Z = +6.55 m down to Curb R = 41.8 ft, Z = +3.92 m)
        pr0 = (*xy_m(polar_pt(G.WP3A, G.R_SCOOP_RIDGE, a0)), z_ridge - 0.04)
        pr1 = (*xy_m(polar_pt(G.WP3A, G.R_SCOOP_RIDGE, a1)), z_ridge - 0.04)
        pc1 = (*xy_m(polar_pt(G.WP3A, G.R_SCOOP_OUTER, a1)), z_fan_low + 0.12)
        pc0 = (*xy_m(polar_pt(G.WP3A, G.R_SCOOP_OUTER, a0)), z_fan_low + 0.12)
        add_quad(mesh, pr0, pc0, pc1, pr1, MATERIALS["glass_skylight"])
        add_quad(mesh, pr0, pr1, pc1, pc0, MATERIALS["glass_skylight"])

    # Radial Aluminum Skylight Mullions along North Scoop Glazing (closed 6-face bars)
    for i in range(0, n_scoop + 1, 2):
        ang = angles[i]
        m_top = xy_m(polar_pt(G.WP3A, G.R_SCOOP_RIDGE, ang))
        m_bot = xy_m(polar_pt(G.WP3A, G.R_SCOOP_OUTER, ang))
        rad = math.radians(ang + 90.0)
        ox, oy = 0.045 * math.cos(rad), 0.045 * math.sin(rad)
        zt0, zt1 = z_ridge - 0.04, z_ridge + 0.03
        zb0, zb1 = z_fan_low + 0.10, z_fan_low + 0.17
        t_l0, t_r0 = (m_top[0] - ox, m_top[1] - oy, zt0), (m_top[0] + ox, m_top[1] + oy, zt0)
        t_l1, t_r1 = (m_top[0] - ox, m_top[1] - oy, zt1), (m_top[0] + ox, m_top[1] + oy, zt1)
        b_l0, b_r0 = (m_bot[0] - ox, m_bot[1] - oy, zb0), (m_bot[0] + ox, m_bot[1] + oy, zb0)
        b_l1, b_r1 = (m_bot[0] - ox, m_bot[1] - oy, zb1), (m_bot[0] + ox, m_bot[1] + oy, zb1)
        add_quad(mesh, t_l1, b_l1, b_r1, t_r1, MATERIALS["mullion_alum"])  # top
        add_quad(mesh, t_r0, b_r0, b_l0, t_l0, MATERIALS["mullion_alum"])  # bottom
        add_quad(mesh, t_l0, b_l0, b_l1, t_l1, MATERIALS["mullion_alum"])  # left
        add_quad(mesh, t_r1, b_r1, b_r0, t_r0, MATERIALS["mullion_alum"])  # right
        add_quad(mesh, t_r0, t_l0, t_l1, t_r1, MATERIALS["mullion_alum"])  # ridge end
        add_quad(mesh, b_l0, b_r0, b_r1, b_l1, MATERIALS["mullion_alum"])  # curb end

    # Copper End-Cheek Gables closing East (45°) and West (156°) ends of the Daylight Scoop
    for end_ang, flip in ((deg0, False), (deg1, True)):
        p_in = (*xy_m(polar_pt(G.WP3A, G.R_SCOOP_INNER, end_ang)), z_fan_low)
        p_rg = (*xy_m(polar_pt(G.WP3A, G.R_SCOOP_RIDGE, end_ang)), z_ridge)
        p_ou = (*xy_m(polar_pt(G.WP3A, G.R_SCOOP_OUTER, end_ang)), z_fan_low)
        if not flip:
            add_tri(mesh, p_in, p_ou, p_rg, MATERIALS["copper_roof"])
            add_tri(mesh, p_in, p_rg, p_ou, MATERIALS["white_plaster"])
        else:
            add_tri(mesh, p_in, p_rg, p_ou, MATERIALS["copper_roof"])
            add_tri(mesh, p_in, p_ou, p_rg, MATERIALS["white_plaster"])

    # Outer Skylight Curb Beam at R = 41.8 ft
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_SCOOP_OUTER - 0.5,
        G.R_SCOOP_OUTER + 0.4,
        deg0,
        deg1,
        z_fan_low - 0.25,
        z_fan_low + 0.18,
        MATERIALS["white_plaster"],
        steps=36,
    )

    # =========================================================================
    # 2. TIPPED NORTH PERIMETER FAN ROOF & SWEEPING INTERIOR DAYLIGHT SOFFIT
    # =========================================================================
    chain = _fan_perimeter_chain_ft()
    f_deg0, f_deg1 = 31.0, 170.0
    raw_angles = [f_deg0 + (f_deg1 - f_deg0) * (i / 70) for i in range(71)]
    # Add exact corner angles of every H-column scupper pocket so roof notches cleanly!
    for vx, vy in chain[1:-1]:
        vang = math.degrees(math.atan2(vy - G.WP3A[1], vx - G.WP3A[0]))
        for eps in (-0.06, 0.0, 0.06):
            cand = vang + eps
            if f_deg0 <= cand <= f_deg1:
                raw_angles.append(cand)
    raw_angles.sort()
    f_angles: list[float] = []
    for a in raw_angles:
        if not f_angles or (a - f_angles[-1]) > 0.03:
            f_angles.append(a)

    raw_slices = []
    for i in range(len(f_angles) - 1):
        a0, a1 = f_angles[i], f_angles[i + 1]
        eps = min(0.015, 0.25 * (a1 - a0))
        r_out0 = _fan_outer_radius_at_angle(a0 + eps, chain) - 0.35
        r_out1 = _fan_outer_radius_at_angle(a1 - eps, chain) - 0.35
        a_mid = 0.5 * (a0 + a1)
        r_in = G.R_SCOOP_OUTER if (deg0 <= a_mid <= deg1) else G.R_SCOOP_INNER
        raw_slices.append([a0, a1, r_in, r_out0, r_out1])

    # Snap shared radial vertices across smooth joints so adjacent slices share bit-identical edges
    n_sl = len(raw_slices)
    for i in range(n_sl - 1):
        if raw_slices[i][2] == raw_slices[i + 1][2] and abs(raw_slices[i][4] - raw_slices[i + 1][3]) <= 0.12:
            shared_r = 0.5 * (raw_slices[i][4] + raw_slices[i + 1][3])
            raw_slices[i][4] = shared_r
            raw_slices[i + 1][3] = shared_r

    for i, (a0, a1, r_in, r_out0, r_out1) in enumerate(raw_slices):
        r_hinge0 = r_in + 0.72 * (r_out0 - r_in)
        r_hinge1 = r_in + 0.72 * (r_out1 - r_in)

        q_in0 = xy_m(polar_pt(G.WP3A, r_in, a0))
        q_in1 = xy_m(polar_pt(G.WP3A, r_in, a1))
        q_hg1 = xy_m(polar_pt(G.WP3A, r_hinge1, a1))
        q_hg0 = xy_m(polar_pt(G.WP3A, r_hinge0, a0))
        q_ou1 = xy_m(polar_pt(G.WP3A, r_out1, a1))
        q_ou0 = xy_m(polar_pt(G.WP3A, r_out0, a0))

        # Zone A: Flat Roof & Acoustic Soffit from r_in to r_hinge (Z = +3.81 m)
        add_quad(mesh, (*q_in0, z_fan_low), (*q_hg0, z_fan_low), (*q_hg1, z_fan_low), (*q_in1, z_fan_low), MATERIALS["builtup_roof"])
        add_quad(mesh, (*q_in0, z_fan_low - 0.22), (*q_in1, z_fan_low - 0.22), (*q_hg1, z_fan_low - 0.22), (*q_hg0, z_fan_low - 0.22), MATERIALS["white_soffit"])

        # Zone B: Upward-Sweeping Perimeter Daylight Scoop from r_hinge (+3.81 m) to North Curtain Wall (+5.25 m)
        add_quad(mesh, (*q_hg0, z_fan_low), (*q_ou0, z_par_n - 0.08), (*q_ou1, z_par_n - 0.08), (*q_hg1, z_fan_low), MATERIALS["copper_roof"])
        add_quad(mesh, (*q_hg0, z_fan_low - 0.22), (*q_hg1, z_fan_low - 0.22), (*q_ou1, z_par_n - 0.32), (*q_ou0, z_par_n - 0.32), MATERIALS["white_soffit"])

        # Seal inner (-r) and outer (+r) rims of the fan roof slab
        add_quad(mesh, (*q_in0, z_fan_low - 0.22), (*q_in0, z_fan_low), (*q_in1, z_fan_low), (*q_in1, z_fan_low - 0.22), MATERIALS["white_soffit"])
        add_quad(mesh, (*q_ou0, z_par_n - 0.08), (*q_ou0, z_par_n - 0.32), (*q_ou1, z_par_n - 0.32), (*q_ou1, z_par_n - 0.08), MATERIALS["copper_roof"])

        # Seal radial cheek rims at outer ends or H-pocket radial steps so the roof shell is watertight
        cap_east = (i == 0) or (raw_slices[i][2] != raw_slices[i - 1][2]) or (raw_slices[i][3] != raw_slices[i - 1][4])
        cap_west = (i == n_sl - 1) or (raw_slices[i][2] != raw_slices[i + 1][2]) or (raw_slices[i][4] != raw_slices[i + 1][3])
        if cap_east:
            add_quad(mesh, (*q_in0, z_fan_low - 0.22), (*q_hg0, z_fan_low - 0.22), (*q_hg0, z_fan_low), (*q_in0, z_fan_low), MATERIALS["copper_roof"])
            add_quad(mesh, (*q_hg0, z_fan_low - 0.22), (*q_ou0, z_par_n - 0.32), (*q_ou0, z_par_n - 0.08), (*q_hg0, z_fan_low), MATERIALS["copper_roof"])
        if cap_west:
            add_quad(mesh, (*q_in1, z_fan_low), (*q_hg1, z_fan_low), (*q_hg1, z_fan_low - 0.22), (*q_in1, z_fan_low - 0.22), MATERIALS["copper_roof"])
            add_quad(mesh, (*q_hg1, z_fan_low), (*q_ou1, z_par_n - 0.08), (*q_ou1, z_par_n - 0.32), (*q_hg1, z_fan_low - 0.22), MATERIALS["copper_roof"])

    # Clerestory Vertical Fascia closing height step between South Wing Roof (+4.98 m) and Lower Fan Deck (+3.81 m) on flanks
    add_arc_band_ft(mesh, G.WP3A, G.R_SCOOP_INNER - 0.6, G.R_SCOOP_INNER + 0.3, 31.0, 45.2, z_fan_low - 0.22, z_south_rf, MATERIALS["buff_brick"], steps=8)
    add_arc_band_ft(mesh, G.WP3A, G.R_SCOOP_INNER - 0.6, G.R_SCOOP_INNER + 0.3, 155.8, 170.0, z_fan_low - 0.22, z_south_rf, MATERIALS["buff_brick"], steps=8)

    # Weathered Copper Parapet Fascia Cap stepping around all 3 H-Column scupper pockets (offset_mode="right" = inward)
    add_wall_strip_ft(
        mesh,
        [G.PT_A_INNER_JUNC, *get_north_perimeter_with_pockets_ft(level=3), G.PT_LOUNGE_JUNC],
        1.05,
        z_par_n + 0.045,
        z_par_n + 0.18,
        MATERIALS["copper_roof"],
        offset_mode="right",
    )

    # =========================================================================
    # 3. SOUTH WING BUILT-UP ROOF (+4.98 m), COPPER COPING & WOOD CEILING DRUM
    # =========================================================================
    south_roof_arc = [polar_pt(G.WP3A, G.R_SCOOP_INNER, 170.0 - (170.0 - 31.0) * (k / 30)) for k in range(31)]
    south_roof_poly = [
        (-126.5, 1.5),
        (-77.5, 1.5),
        (-77.5, 12.8),
        *south_roof_arc,  # Seals seamlessly against fan roof & Central Daylight Scoop!
        (51.8, 32.8),
        (51.8, -8.8),
        (61.5, -8.8),
        (61.5, -59.5),
        (19.5, -59.5),
        (16.5, -50.8),
        (-91.5, -50.8),
        (-91.5, -28.0),
        (-126.5, -28.0),
    ]
    sides_sky = 20
    roof_skylight_holes = [
        [
            (
                sx + (sr - 0.10) * math.cos(2.0 * math.pi * k / sides_sky),
                sy + (sr - 0.10) * math.sin(2.0 * math.pi * k / sides_sky),
            )
            for k in range(sides_sky)
        ]
        for sx, sy, sr in G.CONICAL_SKYLIGHTS
    ]
    add_extruded_polygon_with_holes_ft(
        mesh,
        south_roof_poly,
        roof_skylight_holes,
        z_south_rf - 0.26,
        z_south_rf,
        MATERIALS["builtup_roof"],
        MATERIALS["buff_brick"],
        MATERIALS["white_plaster"],
        MATERIALS["white_soffit"],
    )

    # Copper Parapet Coping around South Wing & Periodical Lounge Perimeter
    add_wall_strip_ft(
        mesh,
        [
            (51.8, 32.8), (51.8, -8.8), (61.5, -8.8), (61.5, -59.5),
            (19.5, -59.5), (16.5, -50.8), (-91.5, -50.8), (-91.5, -28.0),
            (-126.5, -28.0), (-126.5, 1.5), (-77.5, 1.5),
        ],
        1.50,
        z_south_rf,
        z_south_rf + 0.22,
        MATERIALS["copper_roof"],
    )

    # Suspended Slatted Birch/Hemlock Acoustic Ceiling Drum above Control Desk (R = 17.5 ft, Z = +3.25..+3.65 m)
    # Perforated cleanly where the 2 Control Desk conical skylight throats pierce the wood drum!
    drum_outer = [
        (
            G.WP_DESK[0] + G.R_WOOD_DRUM * math.cos(2.0 * math.pi * k / 36),
            G.WP_DESK[1] + G.R_WOOD_DRUM * math.sin(2.0 * math.pi * k / 36),
        )
        for k in range(36)
    ]
    drum_holes = [
        [
            (
                sx + (sr + 1.15) * math.cos(2.0 * math.pi * k / sides_sky),
                sy + (sr + 1.15) * math.sin(2.0 * math.pi * k / sides_sky),
            )
            for k in range(sides_sky)
        ]
        for sx, sy, sr in G.CONICAL_SKYLIGHTS
        if math.hypot(sx - G.WP_DESK[0], sy - G.WP_DESK[1]) < G.R_WOOD_DRUM - sr - 1.2
    ]
    add_extruded_polygon_with_holes_ft(
        mesh,
        drum_outer,
        drum_holes,
        3.25,
        3.65,
        MATERIALS["hemlock_slat"],
        MATERIALS["hemlock_slat"],
        MATERIALS["hemlock_slat"],
        MATERIALS["hemlock_slat"],
    )

    # =========================================================================
    # 4. 12 SIGNATURE AALTO CONICAL ROOF SKYLIGHT LANTERNS (WATERTIGHT SHELLS)
    # =========================================================================
    for sx, sy, sr in G.CONICAL_SKYLIGHTS:
        # Hollow thick-walled Copper Skylight Drum above Roof (r_in = sr - 0.10, r_out = sr + 0.28)
        add_arc_band_ft(mesh, (sx, sy), sr - 0.10, sr + 0.28, 0.0, 360.0, z_south_rf, z_lantern - 0.22, MATERIALS["copper_roof"], steps=sides_sky)

        # Conical Translucent Skylight Dome Cap
        add_frustum_ft(
            mesh,
            (sx, sy),
            r0_ft=sr + 0.30,
            r1_ft=0.35,
            z0_m=z_lantern - 0.22,
            z1_m=z_lantern + 0.28,
            attrs=MATERIALS["glass_skylight"],
            sides=sides_sky,
            cap_top=True,
        )

        # Watertight Thick-Walled White Plaster Conical Light-Diffusing Throat (for Section A-A & B-B poché!)
        z_ceil = 3.22 if sy > 4.0 else 3.88
        z_throat_top = z_south_rf - 0.26
        cx_m, cy_m = xy_m((sx, sy))
        r0_in, r0_out = m_ft(sr + 0.78), m_ft(sr + 1.14)
        r1_in, r1_out = m_ft(sr - 0.10), m_ft(sr + 0.26)
        in0, out0, in1, out1 = [], [], [], []
        for s_i in range(sides_sky):
            ang = 2.0 * math.pi * s_i / sides_sky
            ca, sa = math.cos(ang), math.sin(ang)
            in0.append((cx_m + r0_in * ca, cy_m + r0_in * sa, z_ceil))
            out0.append((cx_m + r0_out * ca, cy_m + r0_out * sa, z_ceil))
            in1.append((cx_m + r1_in * ca, cy_m + r1_in * sa, z_throat_top))
            out1.append((cx_m + r1_out * ca, cy_m + r1_out * sa, z_throat_top))
        for s_i in range(sides_sky):
            s_j = (s_i + 1) % sides_sky
            add_quad(mesh, out0[s_i], out0[s_j], out1[s_j], out1[s_i], MATERIALS["white_plaster"])
            add_quad(mesh, in0[s_j], in0[s_i], in1[s_i], in1[s_j], MATERIALS["white_plaster"])
            add_quad(mesh, in0[s_j], out0[s_j], out0[s_i], in0[s_i], MATERIALS["white_plaster"])
            add_quad(mesh, in1[s_i], out1[s_i], out1[s_j], in1[s_j], MATERIALS["white_plaster"])

    return grp
