"""
Layer 7: Dual-Scoop Daylight Roof, Copper Fascia & 12 Conical Lanterns (`7_Roof_And_Daylight_Scoop`).

Models Alvar Aalto's celebrated Mount Angel daylighting roof system:
  1. Curved Central North Daylight Monitor Scoop (R = 24.0..39.6 ft, peak +6.55 m):
     - Copper-clad curved exterior shell + copper ridge & sill flashings
     - Smooth concave white plaster interior reflector vault
     - Closed 2-manifold steep North-facing skylight glazing with 19 radial aluminum mullions
     - Watertight 8-vertex copper/plaster end-cheek gable walls (`Sheet 18-a18 Detail 4`)
       sealing flush against the curved vault, glazing, curb, fan roof, and step parapet!
  2. High North Perimeter Fan Roof (+4.65 m with 1.20 m / 3'-11" plenum, sweeping upward
     to +4.95 m along the 4 faceted North Curtain-Wall Bays): mitered cleanly into the acute
     East & West prows, with upward daylight-scoop ceiling soffit (+4.62 m).
  3. Lower South Wing Built-up Roof (+3.86 m, 0.56 m structural thickness!), continuous Buff-Brick +
     Copper-Capped Clerestory Step Walls rising up to +4.83 m, Taller SE Auditorium Dark-Membrane
     Roof (+5.69 m, 0.64 m slab!), Authentic Radial Wood-Slatted Sector Ceiling with circumferential
     joint ring, and 12 Conical Roof Skylight Lanterns!
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import (
    AaltoGeometry,
    get_north_perimeter_with_pockets_ft,
    polar_pt,
)

from .primitives import (
    MATERIALS,
    add_arc_band_ft,
    add_extruded_polygon_ft,
    add_extruded_polygon_with_holes_ft,
    add_frustum_ft,
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


def _ray_segment_dist_ft(
    origin: tuple[float, float],
    deg: float,
    a: tuple[float, float],
    b: tuple[float, float],
) -> float | None:
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
    if t > 1.0 and -0.005 <= u <= 1.005:
        return t
    return None


def _fan_outer_radius_at_angle(deg: float, chain: list[tuple[float, float]]) -> float:
    """Distance from WP3A along `deg` to the inward-offset Fan Roof centerline boundary."""
    G = AaltoGeometry
    best = None
    for idx in range(len(chain) - 1):
        d = _ray_segment_dist_ft(G.WP3A, deg, chain[idx], chain[idx + 1])
        if d is not None and (best is None or d < best):
            best = d
    return best if best is not None else 82.0


def _add_scoop_end_cheek_solid(
    mesh,
    center_ft: tuple[float, float],
    end_deg: float,
    cheek_rz_m: list[tuple[float, float]],
    s0_m: float,
    s1_m: float,
    s0_attrs: dict,
    s1_attrs: dict,
    rim_attrs: dict,
):
    """
    Extrude a closed 2D `(r_m, z_m)` profile along tangential normal `n = (sin(deg), -cos(deg), 0)`
    from `s0_m` to `s1_m` as a 100% watertight 2-manifold solid (`unpaired = 0`).
    """
    cx_m, cy_m = xy_m(center_ft)
    rad = math.radians(end_deg)
    urx, ury = math.cos(rad), math.sin(rad)
    nx, ny = ury, -urx  # +n = u_r x +Z (points in -deg tangential direction)

    ccw_rz, tris = triangulate_polygon_2d(cheek_rz_m)
    if len(ccw_rz) < 3:
        return

    def pt3(r_m: float, z_m: float, s_m: float) -> tuple[float, float, float]:
        return (cx_m + r_m * urx + s_m * nx, cy_m + r_m * ury + s_m * ny, z_m)

    # +n cap at s1_m and -n cap at s0_m
    for i0, i1, i2 in tris:
        r0, z0 = ccw_rz[i0]
        r1, z1 = ccw_rz[i1]
        r2, z2 = ccw_rz[i2]
        add_tri(mesh, pt3(r0, z0, s1_m), pt3(r1, z1, s1_m), pt3(r2, z2, s1_m), s1_attrs)
        add_tri(mesh, pt3(r0, z0, s0_m), pt3(r2, z2, s0_m), pt3(r1, z1, s0_m), s0_attrs)

    # Outward-normal perimeter rim quads around CCW `(r_m, z_m)` loop
    m = len(ccw_rz)
    for i in range(m):
        r0, z0 = ccw_rz[i]
        r1, z1 = ccw_rz[(i + 1) % m]
        add_quad(mesh, pt3(r0, z0, s0_m), pt3(r1, z1, s0_m), pt3(r1, z1, s1_m), pt3(r0, z0, s1_m), rim_attrs)


def build_roof_and_skylights(scene):
    grp = create_scene_group(scene, "7_Roof_And_Daylight_Scoop")
    mesh = grp.mesh
    G = AaltoGeometry

    z_fan_low = m_ft(G.Z_FAN_ROOF_LOW_FT)       # +4.65 m (Main Fan Roof Deck)
    z_fan_high = m_ft(G.Z_FAN_ROOF_HIGH_FT)     # +4.95 m (Outer North Perimeter Roof)
    z_fan_ceil = m_ft(G.Z_FAN_CEIL_FT)         # +3.45 m (Main Fan Reading Room Ceiling)
    z_s_ceil = m_ft(G.Z_SOUTH_CEIL_FT)          # +3.30 m (South Wing Interior Ceiling)
    z_south_rf = m_ft(G.Z_SOUTH_ROOF_FT)        # +3.86 m (Lower South Wing Roof Deck)
    z_s_par = m_ft(G.Z_SOUTH_PARAPET_FT)        # +4.22 m (South Wing Parapet Coping)
    z_aud_rf = m_ft(G.Z_AUDITORIUM_ROOF_FT)     # +5.69 m (Taller SE Auditorium Roof Deck)
    z_aud_par = m_ft(G.Z_AUDITORIUM_PARAPET_FT) # +6.15 m (Taller SE Auditorium Parapet Coping)
    z_par_n = m_ft(G.Z_FAN_PARAPET_N_FT)        # +5.44 m (North Fan Parapet Coping)
    z_ridge = m_ft(G.Z_SCOOP_RIDGE_FT)          # +6.55 m (Daylight Scoop Peak Ridge)
    z_lantern = m_ft(G.Z_LANTERN_TOP_FT)        # +4.83 m (Conical Skylight Lantern Peak)

    # =========================================================================
    # 1. CURVED CENTRAL NORTH DAYLIGHT MONITOR SCOOP (45° .. 156° around WP3A)
    # =========================================================================
    n_scoop = 36
    deg0, deg1 = 45.0, 156.0
    angles = [deg0 + (deg1 - deg0) * (i / n_scoop) for i in range(n_scoop + 1)]
    r_curb_top = 39.6          # Radius where North Skylight Glazing meets Fan Roof
    z_curb = z_fan_low + 0.14  # +4.79 m concrete/plaster skylight curb top

    # Concave white plaster reflector profile (radius_ft_from_WP3A, z_interior_m, z_exterior_m)
    vault_profile = [
        (G.R_SCOOP_INNER, 3.32, 3.94),
        (26.8, 4.55, 4.98),
        (30.4, 5.68, 5.92),
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

        # Closed 2-manifold Steep North-Facing Skylight Glazing Shell (thickness = 24 mm)
        rg0_xy = xy_m(polar_pt(G.WP3A, G.R_SCOOP_RIDGE, a0))
        rg1_xy = xy_m(polar_pt(G.WP3A, G.R_SCOOP_RIDGE, a1))
        cb0_xy = xy_m(polar_pt(G.WP3A, r_curb_top, a0))
        cb1_xy = xy_m(polar_pt(G.WP3A, r_curb_top, a1))
        zr_t, zr_b = z_ridge - 0.030, z_ridge - 0.054
        zc_t, zc_b = z_curb + 0.030, z_curb + 0.006
        add_quad(mesh, (*rg0_xy, zr_t), (*cb0_xy, zc_t), (*cb1_xy, zc_t), (*rg1_xy, zr_t), MATERIALS["glass_skylight"])
        add_quad(mesh, (*rg0_xy, zr_b), (*rg1_xy, zr_b), (*cb1_xy, zc_b), (*cb0_xy, zc_b), MATERIALS["glass_skylight"])
        add_quad(mesh, (*rg0_xy, zr_b), (*rg0_xy, zr_t), (*rg1_xy, zr_t), (*rg1_xy, zr_b), MATERIALS["glass_skylight"])
        add_quad(mesh, (*cb0_xy, zc_t), (*cb0_xy, zc_b), (*cb1_xy, zc_b), (*cb1_xy, zc_t), MATERIALS["glass_skylight"])
        if i == 0:
            add_quad(mesh, (*rg0_xy, zr_b), (*cb0_xy, zc_b), (*cb0_xy, zc_t), (*rg0_xy, zr_t), MATERIALS["glass_skylight"])
        if i == n_scoop - 1:
            add_quad(mesh, (*rg1_xy, zr_t), (*cb1_xy, zc_t), (*cb1_xy, zc_b), (*rg1_xy, zr_b), MATERIALS["glass_skylight"])

    # Radial Aluminum Skylight Mullions along North Scoop Glazing (19 closed 6-face bars)
    for i in range(0, n_scoop + 1, 2):
        ang = angles[i] + (0.42 if i == 0 else (-0.42 if i == n_scoop else 0.0))
        m_top = xy_m(polar_pt(G.WP3A, G.R_SCOOP_RIDGE, ang))
        m_bot = xy_m(polar_pt(G.WP3A, r_curb_top, ang))
        rad = math.radians(ang + 90.0)
        ox, oy = 0.045 * math.cos(rad), 0.045 * math.sin(rad)
        zt0, zt1 = z_ridge - 0.055, z_ridge + 0.025
        zb0, zb1 = z_curb + 0.005, z_curb + 0.075
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

    # Weathered Copper Ridge Flashing Cap sealing the Ridge Apex (`Sheet 07-a7 Detail 9: HEAD DETAIL SKYLIGHT`)
    add_arc_band_ft(
        mesh,
        G.WP3A,
        G.R_SCOOP_RIDGE - 0.35,
        G.R_SCOOP_RIDGE + 0.28,
        deg0 - 0.12,
        deg1 + 0.12,
        z_ridge - 0.035,
        z_ridge + 0.042,
        MATERIALS["copper_roof"],
        steps=36,
    )

    # Outer Skylight Curb Beam & Copper Sill Flashing at R = 39.6 ft (`Sheet 07-a7 Detail 8: SILL DETAIL SKYLIGHT`)
    r_curb_in = r_curb_top - 0.48
    r_curb_out = r_curb_top + 0.36
    add_arc_band_ft(
        mesh,
        G.WP3A,
        r_curb_in,
        r_curb_out,
        deg0,
        deg1,
        z_fan_low - 0.22,
        z_curb,
        MATERIALS["white_plaster"],
        steps=36,
    )
    add_arc_band_ft(
        mesh,
        G.WP3A,
        r_curb_top - 0.12,
        r_curb_out + 0.04,
        deg0 - 0.12,
        deg1 + 0.12,
        z_curb,
        z_curb + 0.032,
        MATERIALS["copper_roof"],
        steps=36,
    )

    # Watertight Copper/Plaster End-Cheek Gables closing East (45°) & West (156°) Scoop Ends
    # (`Sheet 18-a18 Detail 4: 16 OZ COPPER FASCIA & WALL` — matches every exact vertex of `vault_profile`,
    # glazing slope, curb sill, lower fan roof slab, and upper step parapet with ZERO gaps!)
    cheek_rz_m = [
        (m_ft(G.R_SCOOP_INNER - 0.55), z_south_rf),
        (m_ft(r_curb_out + 0.04),      z_fan_low),
        (m_ft(r_curb_out + 0.04),      z_curb + 0.032),
        (m_ft(r_curb_top),             z_curb + 0.032),
        (m_ft(G.R_SCOOP_RIDGE),        z_ridge + 0.038),
        (m_ft(30.4),                   5.92),
        (m_ft(26.8),                   4.98),
        (m_ft(G.R_SCOOP_INNER - 0.55), z_south_rf + 0.08),
    ]
    # East End Cheek (`deg0 = 45.0°`): +n (-deg) faces outside (`copper_roof`), -n (+deg) faces inside (`white_plaster`)
    _add_scoop_end_cheek_solid(
        mesh,
        G.WP3A,
        deg0,
        cheek_rz_m,
        s0_m=-m_ft(0.42),
        s1_m=+m_ft(0.16),
        s0_attrs=MATERIALS["white_plaster"],
        s1_attrs=MATERIALS["copper_roof"],
        rim_attrs=MATERIALS["copper_roof"],
    )
    # West End Cheek (`deg1 = 156.0°`): -n (+deg) faces outside (`copper_roof`), +n (-deg) faces inside (`white_plaster`)
    _add_scoop_end_cheek_solid(
        mesh,
        G.WP3A,
        deg1,
        cheek_rz_m,
        s0_m=-m_ft(0.16),
        s1_m=+m_ft(0.42),
        s0_attrs=MATERIALS["copper_roof"],
        s1_attrs=MATERIALS["white_plaster"],
        rim_attrs=MATERIALS["copper_roof"],
    )

    # =========================================================================
    # 2. MAIN FAN ROOF PLENUM (1.20 m / 3'-11" DEEP) & TAPERED CLERESTORY SOFFIT
    # =========================================================================
    perim_outer = [G.PT_A_INNER_JUNC, *get_north_perimeter_with_pockets_ft(level=3), G.PT_LOUNGE_JUNC]
    ext_w = (
        G.PT_A_INNER_JUNC[0] + 1.40 * (G.PT_A_INNER_JUNC[0] - G.PT_A[0]),
        G.PT_A_INNER_JUNC[1] + 1.40 * (G.PT_A_INNER_JUNC[1] - G.PT_A[1]),
    )
    ext_e = (
        G.PT_LOUNGE_JUNC[0] + 0.30 * (G.PT_LOUNGE_JUNC[0] - G.PT_E[0]),
        G.PT_LOUNGE_JUNC[1] + 0.30 * (G.PT_LOUNGE_JUNC[1] - G.PT_E[1]),
    )
    perim_outer_ext = [ext_w, *perim_outer[1:-1], ext_e]
    roof_inner_chain = offset_polyline_right_ft(perim_outer_ext, 0.55)

    pt_e_mid = roof_inner_chain[-2]   # Mitered centerline inside East Acute Prow `PT_E`
    pt_a_mid = roof_inner_chain[1]    # Mitered centerline inside West Acute Corner `PT_A`
    deg_pt_e = math.degrees(math.atan2(pt_e_mid[1] - G.WP3A[1], pt_e_mid[0] - G.WP3A[0]))
    deg_pt_a = math.degrees(math.atan2(pt_a_mid[1] - G.WP3A[1], pt_a_mid[0] - G.WP3A[0]))

    deg_step_w_outer = math.degrees(math.atan2(G.PT_A_INNER_JUNC[1] - G.WP3A[1], G.PT_A_INNER_JUNC[0] - G.WP3A[0]))
    deg_step_e_outer = math.degrees(math.atan2(G.PT_LOUNGE_JUNC[1] - G.WP3A[1], G.PT_LOUNGE_JUNC[0] - G.WP3A[0]))
    f_deg0 = deg_step_e_outer
    f_deg1 = deg_step_w_outer

    raw_angles = [f_deg0 + (f_deg1 - f_deg0) * (i / 84) for i in range(85)]
    raw_angles.extend([deg0, deg1, deg_pt_e, deg_pt_a, 32.80])
    # Include exact vertex angles of every H-column scupper pocket & prow corner in `roof_inner_chain`
    for vx, vy in roof_inner_chain[1:-1]:
        vang = math.degrees(math.atan2(vy - G.WP3A[1], vx - G.WP3A[0]))
        for eps in (-0.05, 0.0, 0.05):
            cand = vang + eps
            if f_deg0 <= cand <= f_deg1:
                raw_angles.append(cand)
    raw_angles.sort()
    f_angles: list[float] = []
    for a in raw_angles:
        if not f_angles or (a - f_angles[-1]) > 0.025:
            f_angles.append(a)

    def _z_outer_roof_and_soffit(deg: float) -> tuple[float, float]:
        """
        Outer perimeter built-up roof & interior daylight-scoop soffit Z at polar angle `deg`
        (`Sheet 07-a7 Detail 1: PARAPET DETAIL NORTH WALL` & `Sheet 13-a13 Section A-A`):
          - Flat at `z_fan_low` (+4.65 m) where the fan meets the East Periodical Lounge step (`<= 32.80°`),
            sweeping smoothly up to `z_fan_high` (+4.95 m) at the East Acute Prow (`deg_pt_e`),
          - Constant `z_fan_high` (+4.95 m, +4.62 m soffit) across all 4 North Bays (`deg_pt_e .. deg_pt_a`),
          - Smooth taper back down to `z_fan_low` (+4.65 m, +3.45 m soffit) across West Throat (`deg_pt_a .. f_deg1`).
        """
        if deg <= 32.80:
            return z_fan_low, z_fan_ceil
        if deg < deg_pt_e:
            t = (deg - 32.80) / max(1e-4, deg_pt_e - 32.80)
            s = t * t * (3.0 - 2.0 * t)
            zt = z_fan_low + s * (z_fan_high - z_fan_low)
            zb = z_fan_ceil + s * (4.62 - z_fan_ceil)
            return zt, zb
        if deg <= deg_pt_a:
            return z_fan_high, 4.62
        t_w = (deg - deg_pt_a) / max(1e-4, f_deg1 - deg_pt_a)
        s_w = min(1.0, max(0.0, t_w))
        zt = z_fan_high + s_w * (z_fan_low - z_fan_high)
        zb = 4.62 + s_w * (z_fan_ceil - 4.62)
        return zt, zb

    raw_slices = []
    for i in range(len(f_angles) - 1):
        a0, a1 = f_angles[i], f_angles[i + 1]
        eps = min(0.012, 0.25 * (a1 - a0))
        r_out0 = _fan_outer_radius_at_angle(a0 + eps, roof_inner_chain)
        r_out1 = _fan_outer_radius_at_angle(a1 - eps, roof_inner_chain)
        a_mid = 0.5 * (a0 + a1)
        is_scoop = (deg0 <= a_mid <= deg1)
        r_tin = r_curb_top if is_scoop else G.R_SCOOP_INNER
        r_bin = 43.2 if is_scoop else G.R_SCOOP_INNER
        raw_slices.append([a0, a1, r_tin, r_bin, r_out0, r_out1, is_scoop])

    # Snap shared radial vertices across smooth joints so adjacent slices share bit-identical edges
    n_sl = len(raw_slices)
    for i in range(n_sl - 1):
        if abs(raw_slices[i][5] - raw_slices[i + 1][4]) <= 0.18:
            shared_r = 0.5 * (raw_slices[i][5] + raw_slices[i + 1][4])
            raw_slices[i][5] = shared_r
            raw_slices[i + 1][4] = shared_r

    for i, (a0, a1, r_tin, r_bin, r_out0, r_out1, is_scoop) in enumerate(raw_slices):
        r_hinge0 = min(65.5, r_out0 - 1.2)
        r_hinge1 = min(65.5, r_out1 - 1.2)
        zt_ou0, zb_ou0 = _z_outer_roof_and_soffit(a0)
        zt_ou1, zb_ou1 = _z_outer_roof_and_soffit(a1)

        q_tin0 = xy_m(polar_pt(G.WP3A, r_tin, a0))
        q_tin1 = xy_m(polar_pt(G.WP3A, r_tin, a1))
        q_bin0 = xy_m(polar_pt(G.WP3A, r_bin, a0))
        q_bin1 = xy_m(polar_pt(G.WP3A, r_bin, a1))
        q_hg0 = xy_m(polar_pt(G.WP3A, r_hinge0, a0))
        q_hg1 = xy_m(polar_pt(G.WP3A, r_hinge1, a1))
        q_ou0 = xy_m(polar_pt(G.WP3A, r_out0, a0))
        q_ou1 = xy_m(polar_pt(G.WP3A, r_out1, a1))

        # Zone A: Top Built-Up Roof from r_tin to r_hinge (Z = +4.65 m)
        add_quad(mesh, (*q_tin0, z_fan_low), (*q_hg0, z_fan_low), (*q_hg1, z_fan_low), (*q_tin1, z_fan_low), MATERIALS["builtup_roof"])

        # Zone B: Upward-Sweeping Perimeter Built-Up Roof (`Sheet 07-a7`) & Daylight-Scoop Plaster Soffit
        zone_b_mat = MATERIALS["builtup_roof"]
        if abs(zt_ou0 - zt_ou1) > 1e-5:
            add_tri(mesh, (*q_hg0, z_fan_low), (*q_ou0, zt_ou0), (*q_ou1, zt_ou1), zone_b_mat)
            add_tri(mesh, (*q_hg0, z_fan_low), (*q_ou1, zt_ou1), (*q_hg1, z_fan_low), zone_b_mat)
            add_tri(mesh, (*q_hg0, z_fan_ceil), (*q_hg1, z_fan_ceil), (*q_ou1, zb_ou1), MATERIALS["white_soffit"])
            add_tri(mesh, (*q_hg0, z_fan_ceil), (*q_ou1, zb_ou1), (*q_ou0, zb_ou0), MATERIALS["white_soffit"])
        else:
            add_quad(mesh, (*q_hg0, z_fan_low), (*q_ou0, zt_ou0), (*q_ou1, zt_ou1), (*q_hg1, z_fan_low), zone_b_mat)
            add_quad(mesh, (*q_hg0, z_fan_ceil), (*q_hg1, z_fan_ceil), (*q_ou1, zb_ou1), (*q_ou0, zb_ou0), MATERIALS["white_soffit"])

        # Zone A: Bottom Horizontal Soffit from r_bin to r_hinge (Z = +3.45 m, 1.20 m plenum!)
        add_quad(mesh, (*q_bin0, z_fan_ceil), (*q_bin1, z_fan_ceil), (*q_hg1, z_fan_ceil), (*q_hg0, z_fan_ceil), MATERIALS["white_soffit"])

        # Outer rim face at r_out (+r outward normal)
        add_quad(mesh, (*q_ou0, zt_ou0), (*q_ou0, zb_ou0), (*q_ou1, zb_ou1), (*q_ou1, zt_ou1), zone_b_mat)

        # Inner face: Diagonal Splayed Coffer (inside Scoop) or Vertical Rim (outside Scoop)
        if is_scoop:
            add_quad(mesh, (*q_tin0, z_fan_low), (*q_tin1, z_fan_low), (*q_bin1, z_fan_ceil), (*q_bin0, z_fan_ceil), MATERIALS["white_plaster"])
        else:
            add_quad(mesh, (*q_tin0, z_fan_ceil), (*q_tin0, z_fan_low), (*q_tin1, z_fan_low), (*q_tin1, z_fan_ceil), MATERIALS["white_soffit"])

        # Seal radial cheek rims at outer ends, sector transitions, or H-pocket radial steps
        cap_east = (i == 0) or (raw_slices[i][6] != raw_slices[i - 1][6]) or (raw_slices[i][4] != raw_slices[i - 1][5])
        cap_west = (i == n_sl - 1) or (raw_slices[i][6] != raw_slices[i + 1][6]) or (raw_slices[i][5] != raw_slices[i + 1][4])
        if cap_east:
            add_quad(mesh, (*q_bin0, z_fan_ceil), (*q_hg0, z_fan_ceil), (*q_hg0, z_fan_low), (*q_tin0, z_fan_low), MATERIALS["copper_roof"])
            add_quad(mesh, (*q_hg0, z_fan_ceil), (*q_ou0, zb_ou0), (*q_ou0, zt_ou0), (*q_hg0, z_fan_low), MATERIALS["copper_roof"])
        if cap_west:
            add_quad(mesh, (*q_tin1, z_fan_low), (*q_hg1, z_fan_low), (*q_hg1, z_fan_ceil), (*q_bin1, z_fan_ceil), MATERIALS["copper_roof"])
            add_quad(mesh, (*q_hg1, z_fan_low), (*q_ou1, zt_ou1), (*q_ou1, zb_ou1), (*q_hg1, z_fan_ceil), MATERIALS["copper_roof"])

    # Weathered Copper Parapet Fascia Cap mitering razor-sharp around ALL 3 H-Pockets & BOTH Acute Prows!
    add_wall_strip_ft(
        mesh,
        perim_outer,
        1.26,
        z_par_n,
        z_par_n + 0.14,
        MATERIALS["copper_roof"],
        offset_mode="right",
        overhang_left_ft=0.08,
    )

    # =========================================================================
    # 3. TALLER SE AUDITORIUM ROOF (+5.69 m) & COPPER-COPED BRICK PARAPET (+6.15 m)
    # =========================================================================
    # SE Auditorium + NW Intake Housing projection from Sheet 13-a13 Section B-B & media_1794671241974_4b7a0b79.jpg
    auditorium_roof_poly = [
        (16.5, -50.8),
        (19.5, -59.5),
        (61.5, -59.5),
        (61.5, -21.0),
        (36.0, -21.0),
        (36.0, -13.5),
        (18.0, -13.5),
        (18.0, -21.0),
    ]
    # Envelope wall (Layer 6) is 1.35 ft thick and runs INWARD from this footprint line.
    aud_wall_ft = 1.35
    # Extrude 0.64 m structural slab (+5.05 .. +5.69 m) with dark slate-charcoal membrane,
    # inset to the inner face of the envelope wall so slab and wall never share coplanar faces.
    aud_slab_poly = offset_polyline_right_ft(auditorium_roof_poly, -aud_wall_ft, closed=True)
    add_extruded_polygon_ft(
        mesh,
        aud_slab_poly,
        z_aud_rf - 0.64,
        z_aud_rf,
        MATERIALS["auditorium_roof"],
        MATERIALS["buff_brick"],
        MATERIALS["white_soffit"],
    )
    # Copper Coping capping the Auditorium parapet. The buff-brick parapet itself is the
    # Layer 6 auditorium envelope wall (rising to z_aud_par), so no second brick strip is
    # added here (it would be coplanar and z-fight). Loop is wound clockwise like the
    # envelope wall so "right" = inward; the coping overhangs both wall faces by 0.08 ft.
    aud_coping_loop = [*reversed(auditorium_roof_poly), auditorium_roof_poly[-1]]
    add_wall_strip_ft(
        mesh,
        aud_coping_loop,
        aud_wall_ft + 0.16,
        z_aud_par,
        z_aud_par + 0.14,
        MATERIALS["copper_roof"],
        offset_mode="right",
        overhang_left_ft=0.08,
    )

    # =========================================================================
    # 4. LOWER SOUTH WING BUILT-UP ROOF (+3.86 m, 0.56 m THICK!) & STEP WALLS
    # =========================================================================
    deg_step_w_outer = math.degrees(math.atan2(G.PT_A_INNER_JUNC[1] - G.WP3A[1], G.PT_A_INNER_JUNC[0] - G.WP3A[0]))
    deg_step_e_outer = math.degrees(math.atan2(G.PT_LOUNGE_JUNC[1] - G.WP3A[1], G.PT_LOUNGE_JUNC[0] - G.WP3A[0]))
    south_roof_arc = [
        polar_pt(G.WP3A, G.R_SCOOP_INNER, deg_step_w_outer - (deg_step_w_outer - deg_step_e_outer) * (k / 36))
        for k in range(37)
    ]
    south_roof_poly = [
        (-126.5, 1.5),
        (-77.5, 1.5),
        G.PT_A_INNER_JUNC,
        *south_roof_arc,
        G.PT_LOUNGE_JUNC,
        (51.8, -8.8),
        (61.5, -8.8),
        (61.5, -21.0),
        (36.0, -21.0),
        (36.0, -13.5),
        (18.0, -13.5),
        (18.0, -21.0),
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
        z_s_ceil,
        z_south_rf,
        MATERIALS["builtup_roof"],
        MATERIALS["buff_brick"],
        MATERIALS["white_plaster"],
        MATERIALS["white_soffit"],
    )

    # Continuous Watertight Buff-Brick + Copper-Capped Clerestory Step Parapet rising UP from the
    # Lower South Wing Roof (+3.74 m) to +4.83 m. It runs unbroken from the West flank (PT_A junction)
    # along R_SCOOP_INNER — passing BEHIND the springing of the curved Daylight Scoop (45°..156°),
    # exactly as the parapet + coping at the low end of `Sheet 18-a18 Detail 4` and the continuous
    # white cap seen in the aerial photograph — to the East flank (Periodical Lounge junction).
    n_step_arc = 48
    step_pts = [
        G.PT_A_INNER_JUNC,
        *[
            polar_pt(G.WP3A, G.R_SCOOP_INNER, deg_step_w_outer - (deg_step_w_outer - deg_step_e_outer) * (k / n_step_arc))
            for k in range(n_step_arc + 1)
        ],
        G.PT_LOUNGE_JUNC,
    ]
    step_ov_l, step_th = 0.95, 1.55
    add_wall_strip_ft(
        mesh,
        step_pts,
        step_th,
        z_south_rf - 0.12,
        z_fan_low + 0.18,
        MATERIALS["buff_brick"],
        offset_mode="right",
        overhang_left_ft=step_ov_l,
    )
    add_wall_strip_ft(
        mesh,
        step_pts,
        step_th + 0.16,
        z_fan_low + 0.18,
        z_fan_low + 0.32,
        MATERIALS["copper_roof"],
        offset_mode="right",
        overhang_left_ft=step_ov_l + 0.08,
    )

    # Copper Parapet Coping around Lower South Wing & Periodical Lounge Perimeter
    south_coping_chain_e = [
        G.PT_LOUNGE_JUNC, (51.8, -8.8), (61.5, -8.8), (61.5, -21.0),
    ]
    south_coping_chain_w = [
        (16.5, -50.8), (-91.5, -50.8), (-91.5, -28.0),
        (-126.5, -28.0), (-126.5, 1.5), (-77.5, 1.5), G.PT_A_INNER_JUNC,
    ]
    for c_chain in (south_coping_chain_e, south_coping_chain_w):
        add_wall_strip_ft(
            mesh,
            c_chain,
            1.45,
            z_s_par,
            z_s_par + 0.14,
            MATERIALS["copper_roof"],
            offset_mode="right",
            overhang_left_ft=0.08,
        )

    # =========================================================================
    # 5. AUTHENTIC RADIAL WOOD-SLATTED CEILING SECTOR & ENTRY SLATS (`10-a10`)
    # =========================================================================
    wp_desk = G.WP_DESK
    # A. Recessed dark acoustic backing plenum (R = 8.6..19.2 ft, 26°..172°, Z = +3.02..+3.28 m)
    plenum_poly = [polar_pt(wp_desk, 19.2, 26.0 + (172.0 - 26.0) * i / 36) for i in range(37)]
    plenum_poly += [polar_pt(wp_desk, 8.6, 172.0 - (172.0 - 26.0) * i / 36) for i in range(37)]
    plenum_holes = []
    for sx, sy in ((-9.8, 11.8), (6.2, 11.8)):
        h = [(sx + 3.05 * math.cos(2.0 * math.pi * k / sides_sky), sy + 3.05 * math.sin(2.0 * math.pi * k / sides_sky)) for k in range(sides_sky)]
        plenum_holes.append(h)
    add_extruded_polygon_with_holes_ft(
        mesh,
        plenum_poly,
        plenum_holes,
        3.02,
        3.28,
        MATERIALS["black_linoleum"],
    )

    # Circular White Plaster Oculus Trim Collars flush with Flared Conical Skylight Throats (Z = +2.92..+3.02 m)
    for sx, sy in ((-9.8, 11.8), (6.2, 11.8)):
        add_arc_band_ft(mesh, (sx, sy), 2.98, 3.36, 0.0, 360.0, 2.92, 3.02, MATERIALS["white_plaster"], steps=20)

    # B. Curving Birch/Hemlock Vertical Fascia Bands (outer & inner, Z = +2.92..+3.30 m)
    add_arc_band_ft(mesh, wp_desk, 19.15, 19.45, 26.0, 172.0, 2.92, 3.30, MATERIALS["birch_wood"], steps=36)
    add_arc_band_ft(mesh, wp_desk, 8.45, 8.75, 26.0, 172.0, 2.92, 3.30, MATERIALS["birch_wood"], steps=36)
    for a_deg in (26.0, 172.0):
        rad = math.radians(a_deg)
        mid_r = 0.5 * (8.75 + 19.15)
        c_pt = (wp_desk[0] + mid_r * math.cos(rad), wp_desk[1] + mid_r * math.sin(rad))
        add_oriented_box_ft(mesh, c_pt, 19.15 - 8.75, 0.30, a_deg, 2.92, 3.30, MATERIALS["birch_wood"])

    # C. Dark Circumferential Joint Ring (R = 14.45..14.65 ft, Z = +2.93..+3.01 m), trimmed cleanly at both skylight oculi
    for j_deg0, j_deg1, j_steps in ((26.2, 41.0, 8), (63.8, 118.5, 18), (145.2, 171.8, 10)):
        add_arc_band_ft(mesh, wp_desk, 14.45, 14.65, j_deg0, j_deg1, 2.93, 3.01, MATERIALS["black_linoleum"], steps=j_steps)

    # D. ~56 Radial Ceiling Battens (0.11 ft wide x 0.07 m tall, Z = +2.94..+3.01 m)
    n_slats = 56
    skylight_clearances = [(-9.8, 11.8, 3.42), (6.2, 11.8, 3.42)]
    for k in range(n_slats):
        ang_deg = 27.0 + (171.0 - 27.0) * (k / (n_slats - 1))
        rad = math.radians(ang_deg)
        ux, uy = math.cos(rad), math.sin(rad)

        blocked_intervals = []
        for sx, sy, r_clr in skylight_clearances:
            vx, vy = sx - wp_desk[0], sy - wp_desk[1]
            t_proj = vx * ux + vy * uy
            d_sq = (vx * vx + vy * vy) - t_proj * t_proj
            if d_sq < r_clr * r_clr:
                h = math.sqrt(r_clr * r_clr - d_sq)
                blocked_intervals.append((t_proj - h, t_proj + h))

        for r_start, r_end in ((8.76, 14.44), (14.66, 19.14)):
            segs = [(r_start, r_end)]
            for b0, b1 in blocked_intervals:
                new_segs = []
                for s0, s1 in segs:
                    if b1 <= s0 or b0 >= s1:
                        new_segs.append((s0, s1))
                    else:
                        if s0 < b0:
                            new_segs.append((s0, b0))
                        if b1 < s1:
                            new_segs.append((b1, s1))
                segs = new_segs
            for s0, s1 in segs:
                if s1 - s0 > 0.25:
                    mid_r = 0.5 * (s0 + s1)
                    c_pt = (wp_desk[0] + mid_r * ux, wp_desk[1] + mid_r * uy)
                    add_oriented_box_ft(mesh, c_pt, s1 - s0, 0.11, ang_deg, 2.94, 3.01, MATERIALS["hemlock_slat"])

    # E. Parallel N–S Wood Ceiling Slats over ENTRY AREA 318 (Z = +2.94..+3.01 m)
    entry_skylights = [(-11.2, -9.8, 3.38), (4.2, -9.8, 3.38)]
    x_curr = -16.8
    while x_curr <= 15.0:
        blocked_y = []
        for sx, sy, r_clr in entry_skylights:
            if abs(x_curr - sx) < r_clr:
                dy = math.sqrt(r_clr * r_clr - (x_curr - sx) ** 2)
                blocked_y.append((sy - dy, sy + dy))
        y_segs = [(-20.5, -1.5)]
        for b0, b1 in blocked_y:
            new_ysegs = []
            for s0, s1 in y_segs:
                if b1 <= s0 or b0 >= s1:
                    new_ysegs.append((s0, s1))
                else:
                    if s0 < b0:
                        new_ysegs.append((s0, b0))
                    if b1 < s1:
                        new_ysegs.append((b1, s1))
            y_segs = new_ysegs
        for y0, y1 in y_segs:
            if y1 - y0 > 0.3:
                c_y = 0.5 * (y0 + y1)
                add_oriented_box_ft(mesh, (x_curr, c_y), 0.11, y1 - y0, 0.0, 2.94, 3.01, MATERIALS["hemlock_slat"])
        x_curr += 0.58

    # =========================================================================
    # 6. 12 SIGNATURE AALTO CONICAL ROOF SKYLIGHT LANTERNS (WATERTIGHT SHELLS)
    # =========================================================================
    for sx, sy, sr in G.CONICAL_SKYLIGHTS:
        add_arc_band_ft(mesh, (sx, sy), sr - 0.10, sr + 0.28, 0.0, 360.0, z_south_rf, z_lantern - 0.22, MATERIALS["copper_roof"], steps=sides_sky)

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
            cap_bottom=True,
        )

        # Watertight Thick-Walled White Plaster Conical Light-Diffusing Throat (for Section A-A & B-B poché!)
        z_ceil = 2.98 if sy > 4.0 else 3.28
        z_throat_top = z_south_rf - 0.56  # 3.8608 - 0.56 = 3.3008 m -> strictly z_ceil < z_throat_top!
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
