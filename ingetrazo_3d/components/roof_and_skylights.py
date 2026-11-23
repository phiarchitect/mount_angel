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
    as_concrete,
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

    z_fan_low = m_ft(G.Z_FAN_ROOF_LOW_FT)       # +4.65 m (+15'-3" Main Fan Roof Deck)
    z_fan_high = m_ft(G.Z_FAN_ROOF_HIGH_FT)     # +4.93 m (+16'-2" Outer North Perimeter Roof)
    z_fan_ceil = m_ft(G.Z_FAN_CEIL_FT)          # +3.45 m (+11'-4" Main Fan Reading Room Ceiling)
    z_s_ceil = m_ft(G.Z_SOUTH_CEIL_FT)          # +3.19 m (+10'-5 1/2" South Wing Interior Ceiling)
    z_south_rf = m_ft(G.Z_SOUTH_ROOF_FT)        # +4.17 m (+13'-8" Lower South Wing Roof Deck)
    z_s_par = m_ft(G.Z_SOUTH_PARAPET_FT)        # +4.57 m (+15'-0" South Wing Parapet Coping)
    z_aud_rf = m_ft(G.Z_AUDITORIUM_ROOF_FT)     # +5.44 m (+17'-10" Taller SE Auditorium Roof Deck)
    z_aud_par = m_ft(G.Z_AUDITORIUM_PARAPET_FT) # +5.88 m (+19'-3 3/8" Taller SE Auditorium Parapet Coping)
    z_par_n = m_ft(G.Z_FAN_PARAPET_N_FT)        # +5.47 m (+17'-11 3/8" North Fan Parapet Coping)
    z_ridge = m_ft(G.Z_SCOOP_RIDGE_FT)          # +6.50 m (+21'-4" Daylight Scoop Peak Ridge)
    z_lantern = m_ft(G.Z_LANTERN_TOP_FT)        # +4.98 m (+16'-4" Conical Skylight Lantern Peak)

    # =========================================================================
    # 1. CURVED CENTRAL NORTH DAYLIGHT MONITOR SCOOP (45° .. 156° around WP3A)
    #    Sheet 18-a18 Sec. 4 & Sheet 48-s17 Det. D: R_in = 25'-10", R_ridge = 34'-6",
    #    15'-4" total ceiling opening to R_out = 41'-2", peak EL. +149'-10" (+21'-4").
    # =========================================================================
    n_scoop = 36
    deg0, deg1 = 45.0, 156.0
    angles = [deg0 + (deg1 - deg0) * (i / n_scoop) for i in range(n_scoop + 1)]
    r_curb_top = G.R_SCOOP_OUTER - 0.75  # 40.42 ft glazing-to-curb contact (outer curb lip at 41'-2")
    z_curb = z_fan_low + 0.14            # +4.79 m concrete/plaster skylight curb top

    # Concave white plaster reflector profile (radius_ft_from_WP3A, z_interior_m, z_exterior_m)
    # Approximates the 7'-8" radius curved plaster vault springing from R = 25'-10" up to R = 34'-6"
    scoop_cop_conc = as_concrete(MATERIALS["copper_roof"])
    plaster_conc = as_concrete(MATERIALS["white_plaster"])
    soffit_conc = as_concrete(MATERIALS["white_soffit"])
    builtup_conc = as_concrete(MATERIALS["builtup_roof"])
    aud_rf_conc = as_concrete(MATERIALS["auditorium_roof"])
    brick_conc = as_concrete(MATERIALS["buff_brick"])
    vault_profile = [
        (G.R_SCOOP_INNER, z_s_ceil + 0.04, z_south_rf + 0.06),
        (28.2, 4.48, 4.98),
        (31.2, 5.65, 5.90),
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
                scoop_cop_conc,
            )
            # Interior Concave White Plaster Daylight Reflector Vault (facing North/Down into Well!)
            add_quad(
                mesh,
                (*p00_xy, zi_a),
                (*p10_xy, zi_a),
                (*p11_xy, zi_b),
                (*p01_xy, zi_b),
                plaster_conc,
            )
            # Seal outer boundary rims of the curved scoop vault for watertight section capping
            if k == 0:
                add_quad(mesh, (*p00_xy, zi_a), (*p00_xy, ze_a), (*p10_xy, ze_a), (*p10_xy, zi_a), scoop_cop_conc)
            if k == len(vault_profile) - 2:
                add_quad(mesh, (*p01_xy, ze_b), (*p01_xy, zi_b), (*p11_xy, zi_b), (*p11_xy, ze_b), scoop_cop_conc)
            if i == 0:
                add_quad(mesh, (*p00_xy, zi_a), (*p01_xy, zi_b), (*p01_xy, ze_b), (*p00_xy, ze_a), scoop_cop_conc)
            if i == n_scoop - 1:
                add_quad(mesh, (*p10_xy, ze_a), (*p11_xy, ze_b), (*p11_xy, zi_b), (*p10_xy, zi_a), scoop_cop_conc)

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

    # Outer Skylight Curb Beam & Copper Sill Flashing at R = 40.42 ft (`Sheet 07-a7 Detail 8: SILL DETAIL SKYLIGHT`)
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
        plaster_conc,
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

    # Radial Skylight Header Beams across the Daylight Scoop (`Sheet 48-s17: MAIN SKYLIGHT FRAME DETAILS`
    # & Detail B "HEADER BEAM TO CONC COLUMN"): plaster-cased 18WF50 beams running along true Radial Axes B, C, D
    # from WP #3 (0,0), emerging from the concave vault (R ≈ 26.8 ft from WP #3A) and crossing beneath the north
    # glazing to bury into the curb at R = 40.8 ft. Each bears dead-center on its well column (`Well_1/2/3`).
    beam_z0 = m_ft(G.Z_HEADER_BEAM_BOT_FT)  # +3.861 m (+12'-8")
    beam_z1 = m_ft(G.Z_HEADER_BEAM_TOP_FT)  # +4.455 m (+14'-7 3/8")
    beam_w_ft = 1.33
    for ray_deg in (G.RAY_B_DEG, G.RAY_C_DEG, G.RAY_D_DEG):
        ux, uy = math.cos(math.radians(ray_deg)), math.sin(math.radians(ray_deg))
        ox, oy = G.WP3[0] - G.WP3A[0], G.WP3[1] - G.WP3A[1]
        b = ox * ux + oy * uy
        c0 = ox * ox + oy * oy

        def _t_at_r(r_ft: float) -> float:
            # Distance along the ray from WP3 at which radius from WP3A equals r_ft
            return -b + math.sqrt(b * b - c0 + r_ft * r_ft)

        t0, t1 = _t_at_r(26.8), _t_at_r(r_curb_top + 0.40)
        t_mid = 0.5 * (t0 + t1)
        add_oriented_box_ft(
            mesh,
            (G.WP3[0] + t_mid * ux, G.WP3[1] + t_mid * uy),
            t1 - t0,
            beam_w_ft,
            ray_deg,
            beam_z0,
            beam_z1,
            plaster_conc,
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
        (m_ft(31.2),                   5.90),
        (m_ft(28.2),                   4.98),
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
        s0_attrs=plaster_conc,
        s1_attrs=scoop_cop_conc,
        rim_attrs=scoop_cop_conc,
    )
    # West End Cheek (`deg1 = 156.0°`): -n (+deg) faces outside (`copper_roof`), +n (-deg) faces inside (`white_plaster`)
    _add_scoop_end_cheek_solid(
        mesh,
        G.WP3A,
        deg1,
        cheek_rz_m,
        s0_m=-m_ft(0.16),
        s1_m=+m_ft(0.42),
        s0_attrs=scoop_cop_conc,
        s1_attrs=plaster_conc,
        rim_attrs=scoop_cop_conc,
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
    deg_e_ramp = deg_step_e_outer + 0.5
    f_deg0 = deg_step_e_outer
    f_deg1 = deg_step_w_outer

    raw_angles = [f_deg0 + (f_deg1 - f_deg0) * (i / 84) for i in range(85)]
    raw_angles.extend([deg0, deg1, deg_pt_e, deg_pt_a, deg_e_ramp])
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
          - Flat at `z_fan_low` (+4.65 m) where the fan meets the East Periodical Lounge step (`<= deg_e_ramp`),
            sweeping smoothly up to `z_fan_high` (+4.93 m) at the East Acute Prow (`deg_pt_e`),
          - Constant `z_fan_high` (+4.93 m, +4.62 m soffit) across all 4 North Bays (`deg_pt_e .. deg_pt_a`),
          - Smooth taper back down to `z_fan_low` (+4.65 m, +3.45 m soffit) across West Throat (`deg_pt_a .. f_deg1`).
        """
        if deg <= deg_e_ramp:
            return z_fan_low, z_fan_ceil
        if deg < deg_pt_e:
            t = (deg - deg_e_ramp) / max(1e-4, deg_pt_e - deg_e_ramp)
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
        r_bin = 43.8 if is_scoop else G.R_SCOOP_INNER
        raw_slices.append([a0, a1, r_tin, r_bin, r_out0, r_out1, is_scoop])

    # Snap shared radial vertices across smooth joints so adjacent slices share bit-identical edges
    n_sl = len(raw_slices)
    for i in range(n_sl - 1):
        if abs(raw_slices[i][5] - raw_slices[i + 1][4]) <= 0.18:
            shared_r = 0.5 * (raw_slices[i][5] + raw_slices[i + 1][4])
            raw_slices[i][5] = shared_r
            raw_slices[i + 1][4] = shared_r

    for i, (a0, a1, r_tin, r_bin, r_out0, r_out1, is_scoop) in enumerate(raw_slices):
        r_hinge0 = min(67.0, r_out0 - 1.2)
        r_hinge1 = min(67.0, r_out1 - 1.2)
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
        add_quad(mesh, (*q_tin0, z_fan_low), (*q_hg0, z_fan_low), (*q_hg1, z_fan_low), (*q_tin1, z_fan_low), builtup_conc)

        # Zone B: Upward-Sweeping Perimeter Built-Up Roof (`Sheet 07-a7`) & Daylight-Scoop Plaster Soffit
        zone_b_mat = builtup_conc
        if abs(zt_ou0 - zt_ou1) > 1e-5:
            add_tri(mesh, (*q_hg0, z_fan_low), (*q_ou0, zt_ou0), (*q_ou1, zt_ou1), zone_b_mat)
            add_tri(mesh, (*q_hg0, z_fan_low), (*q_ou1, zt_ou1), (*q_hg1, z_fan_low), zone_b_mat)
            add_tri(mesh, (*q_hg0, z_fan_ceil), (*q_hg1, z_fan_ceil), (*q_ou1, zb_ou1), soffit_conc)
            add_tri(mesh, (*q_hg0, z_fan_ceil), (*q_ou1, zb_ou1), (*q_ou0, zb_ou0), soffit_conc)
        else:
            add_quad(mesh, (*q_hg0, z_fan_low), (*q_ou0, zt_ou0), (*q_ou1, zt_ou1), (*q_hg1, z_fan_low), zone_b_mat)
            add_quad(mesh, (*q_hg0, z_fan_ceil), (*q_hg1, z_fan_ceil), (*q_ou1, zb_ou1), (*q_ou0, zb_ou0), soffit_conc)

        # Zone A: Bottom Horizontal Soffit from r_bin to r_hinge (Z = +3.45 m, 1.20 m plenum!)
        add_quad(mesh, (*q_bin0, z_fan_ceil), (*q_bin1, z_fan_ceil), (*q_hg1, z_fan_ceil), (*q_hg0, z_fan_ceil), soffit_conc)

        # Outer rim face at r_out (+r outward normal)
        add_quad(mesh, (*q_ou0, zt_ou0), (*q_ou0, zb_ou0), (*q_ou1, zb_ou1), (*q_ou1, zt_ou1), zone_b_mat)

        # Inner face: Diagonal Splayed Coffer (inside Scoop) or Vertical Rim (outside Scoop)
        if is_scoop:
            add_quad(mesh, (*q_tin0, z_fan_low), (*q_tin1, z_fan_low), (*q_bin1, z_fan_ceil), (*q_bin0, z_fan_ceil), plaster_conc)
        else:
            add_quad(mesh, (*q_tin0, z_fan_ceil), (*q_tin0, z_fan_low), (*q_tin1, z_fan_low), (*q_tin1, z_fan_ceil), soffit_conc)

        # Seal radial cheek rims at outer ends, sector transitions, or H-pocket radial steps
        cap_east = (i == 0) or (raw_slices[i][6] != raw_slices[i - 1][6]) or (raw_slices[i][4] != raw_slices[i - 1][5])
        cap_west = (i == n_sl - 1) or (raw_slices[i][6] != raw_slices[i + 1][6]) or (raw_slices[i][5] != raw_slices[i + 1][4])
        if cap_east:
            add_quad(mesh, (*q_bin0, z_fan_ceil), (*q_hg0, z_fan_ceil), (*q_hg0, z_fan_low), (*q_tin0, z_fan_low), scoop_cop_conc)
            add_quad(mesh, (*q_hg0, z_fan_ceil), (*q_ou0, zb_ou0), (*q_ou0, zt_ou0), (*q_hg0, z_fan_low), scoop_cop_conc)
        if cap_west:
            add_quad(mesh, (*q_tin1, z_fan_low), (*q_hg1, z_fan_low), (*q_hg1, z_fan_ceil), (*q_bin1, z_fan_ceil), scoop_cop_conc)
            add_quad(mesh, (*q_hg1, z_fan_low), (*q_ou1, zt_ou1), (*q_ou1, zb_ou1), (*q_hg1, z_fan_ceil), scoop_cop_conc)

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

    # 3 Outer-Fan Rooftop Exhaust Fan Hoods alongside Structural Rays B, C, D (`Sheets 07-a7 & 36-s5`)
    for fx, fy, fr in G.FAN_ROOF_EXHAUST_FANS:
        r_fan = math.hypot(fx - G.WP3A[0], fy - G.WP3A[1])
        u_slope = max(0.0, min(1.0, (r_fan - 67.0) / 18.0))
        z_rf_here = z_fan_low + u_slope * (z_fan_high - z_fan_low)
        # Curb base + brushed aluminum spun-hood exhaust cap
        add_arc_band_ft(mesh, (fx, fy), 0.10, fr * 0.72, 0.0, 360.0, z_rf_here - 0.04, z_rf_here + 0.36, MATERIALS["mullion_alum"], steps=16)
        add_frustum_ft(
            mesh,
            (fx, fy),
            r0_ft=fr * 1.05,
            r1_ft=fr * 0.62,
            z0_m=z_rf_here + 0.34,
            z1_m=z_rf_here + 0.62,
            attrs=MATERIALS["white_column"],
            sides=16,
            cap_top=True,
            cap_bottom=True,
        )

    # Centralized South Wing grid anchors
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

    # =========================================================================
    # 3. TALLER SE AUDITORIUM ROOF (+5.44 m) & COPPER-COPED BRICK PARAPET (+5.88 m)
    # =========================================================================
    auditorium_roof_poly = [
        (x_lob_e, y_g2),
        (x_aud_sw, y_g1),
        (x_aud_e, y_g1),
        (x_aud_e, y_g4),
        (36.8, y_g4),
        (36.8, -13.8),
        (18.5, -13.8),
        (18.5, y_g4),
    ]
    aud_wall_ft = 1.35
    aud_slab_poly = offset_polyline_right_ft(auditorium_roof_poly, -aud_wall_ft, closed=True)
    add_extruded_polygon_ft(
        mesh,
        aud_slab_poly,
        z_aud_rf - 0.64,
        z_aud_rf,
        aud_rf_conc,
        brick_conc,
        soffit_conc,
    )
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
    # 4. LOWER SOUTH WING BUILT-UP ROOF (+4.17 m, 0.98 m PLENUM!) & STEP WALLS
    # =========================================================================
    south_roof_arc = [
        polar_pt(G.WP3A, G.R_SCOOP_INNER, deg_step_w_outer - (deg_step_w_outer - deg_step_e_outer) * (k / 36))
        for k in range(37)
    ]
    south_roof_poly = [
        (x_w, y_g6),
        (x_elev, y_g6),
        G.PT_A_INNER_JUNC,
        *south_roof_arc,
        G.PT_LOUNGE_JUNC,
        (x_lng_e, y_g5),
        (x_aud_e, y_g5),
        (x_aud_e, y_g4),
        (36.8, y_g4),
        (36.8, -13.8),
        (18.5, -13.8),
        (18.5, y_g4),
        (x_lob_e, y_g2),
        (x_step, y_g2),
        (x_step, y_g3),
        (x_w, y_g3),
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
        builtup_conc,
        brick_conc,
        plaster_conc,
        soffit_conc,
    )

    # Continuous Watertight Buff-Brick + Copper-Capped Clerestory Step Parapet rising UP from the
    # Lower South Wing Roof (+4.17 m) to +4.83 m along R_SCOOP_INNER (25'-10").
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
        G.PT_LOUNGE_JUNC, (x_lng_e, y_g5), (x_aud_e, y_g5), (x_aud_e, y_g4),
    ]
    south_coping_chain_w = [
        (x_lob_e, y_g2), (x_step, y_g2), (x_step, y_g3),
        (x_w, y_g3), (x_w, y_g6), (x_elev, y_g6), G.PT_A_INNER_JUNC,
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
    drum_skylights = [G.CONICAL_SKYLIGHTS[0][:2], G.CONICAL_SKYLIGHTS[1][:2]]  # (-10.8, 8.8), (+5.2, 8.8)
    r_drum_in = 5.0
    r_drum_out = 19.2
    z_drum_bot = 2.92
    z_drum_top = z_s_ceil  # +3.188 m (flush under South Wing roof slab)

    # A. Recessed dark acoustic backing plenum (R = 5.0..19.2 ft, 26°..172°, Z = +3.01..z_drum_top)
    plenum_poly = [polar_pt(wp_desk, r_drum_out, 26.0 + (172.0 - 26.0) * i / 36) for i in range(37)]
    plenum_poly += [polar_pt(wp_desk, r_drum_in, 172.0 - (172.0 - 26.0) * i / 36) for i in range(37)]
    plenum_holes = []
    for sx, sy in drum_skylights:
        h = [(sx + 3.05 * math.cos(2.0 * math.pi * k / sides_sky), sy + 3.05 * math.sin(2.0 * math.pi * k / sides_sky)) for k in range(sides_sky)]
        plenum_holes.append(h)
    add_extruded_polygon_with_holes_ft(
        mesh,
        plenum_poly,
        plenum_holes,
        3.01,
        z_drum_top,
        MATERIALS["black_linoleum"],
    )

    # Circular White Plaster Oculus Trim Collars flush with Flared Conical Skylight Throats (Z = +2.92..+3.01 m)
    for sx, sy in drum_skylights:
        add_arc_band_ft(mesh, (sx, sy), 2.98, 3.36, 0.0, 360.0, z_drum_bot, 3.01, MATERIALS["white_plaster"], steps=20)

    # B. Curving Birch/Hemlock Vertical Fascia Bands (outer & inner, Z = +2.92..z_drum_top)
    add_arc_band_ft(mesh, wp_desk, r_drum_out - 0.05, r_drum_out + 0.25, 26.0, 172.0, z_drum_bot, z_drum_top, MATERIALS["birch_wood"], steps=36)
    add_arc_band_ft(mesh, wp_desk, r_drum_in - 0.15, r_drum_in + 0.15, 26.0, 172.0, z_drum_bot, z_drum_top, MATERIALS["birch_wood"], steps=36)
    for a_deg in (26.0, 172.0):
        rad = math.radians(a_deg)
        mid_r = 0.5 * (r_drum_in + 0.15 + r_drum_out - 0.05)
        c_pt = (wp_desk[0] + mid_r * math.cos(rad), wp_desk[1] + mid_r * math.sin(rad))
        add_oriented_box_ft(mesh, c_pt, (r_drum_out - 0.05) - (r_drum_in + 0.15), 0.30, a_deg, z_drum_bot, z_drum_top, MATERIALS["birch_wood"])

    # C. Dark Circumferential Joint Ring (R = 14.45..14.65 ft, Z = +2.93..+3.00 m), trimmed cleanly at both oculi
    for j_deg0, j_deg1, j_steps in ((26.2, 34.0, 6), (62.0, 134.0, 22), (160.0, 171.8, 6)):
        add_arc_band_ft(mesh, wp_desk, 14.45, 14.65, j_deg0, j_deg1, 2.93, 3.00, MATERIALS["black_linoleum"], steps=j_steps)

    # D. ~56 Radial Ceiling Battens (0.11 ft wide x 0.07 m tall, Z = +2.94..+3.01 m)
    n_slats = 56
    skylight_clearances = [(sx, sy, 3.42) for sx, sy in drum_skylights]
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

        for r_start, r_end in ((r_drum_in + 0.16, 14.44), (14.66, r_drum_out - 0.06)):
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
    entry_skylights = [(*G.CONICAL_SKYLIGHTS[6][:2], 3.38), (*G.CONICAL_SKYLIGHTS[7][:2], 3.38)]  # (-12.0, -14.5), (+4.0, -14.5)
    x_curr = -17.5
    while x_curr <= 15.5:
        blocked_y = []
        for sx, sy, r_clr in entry_skylights:
            if abs(x_curr - sx) < r_clr:
                dy = math.sqrt(r_clr * r_clr - (x_curr - sx) ** 2)
                blocked_y.append((sy - dy, sy + dy))
        y_segs = [(y_g4 + 0.5, -1.5)]
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
    # 6. 14 SIGNATURE AALTO CONICAL ROOF SKYLIGHT LANTERNS (WATERTIGHT SHELLS)
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
        z_ceil = 2.96 if sy > 4.0 else (z_s_ceil - 0.14)
        z_throat_top = z_s_ceil + 0.04  # strictly z_ceil < z_throat_top; embeds cleanly into South roof slab!
        cx_m, cy_m = xy_m((sx, sy))
        if sx < G.X_SOUTH_STEP and (sy - (sr + 1.14)) < (y_g3 + 0.25):
            r0_out_ft = max(sr + 0.05, sy - (y_g3 + 0.25))
            r0_in_ft = r0_out_ft - 0.30
            r1_in_ft, r1_out_ft = sr - 0.35, sr - 0.05
        else:
            r0_in_ft, r0_out_ft = sr + 0.78, sr + 1.14
            r1_in_ft, r1_out_ft = sr - 0.10, sr + 0.26
        r0_in, r0_out = m_ft(r0_in_ft), m_ft(r0_out_ft)
        r1_in, r1_out = m_ft(r1_in_ft), m_ft(r1_out_ft)
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
