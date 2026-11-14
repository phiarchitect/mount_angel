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
    add_wall_strip_ft,
    create_scene_group,
    m_ft,
)


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
    terminating flush against the mitered outer fin tips of H-Columns B, C, D:
      - Solid buff-brick spandrel bands (`offset_mode="right"` so outer brick face is exact)
      - Recessed ribbon glazing bands at L2 and L3 high clerestory
      - Vertical bronze mullions & exterior vertical wood sun-shading louvers
    """
    dx, dy = p1_ft[0] - p0_ft[0], p1_ft[1] - p0_ft[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    # Inward normal (Southward into fan: rotate clockwise 90 deg -> (uy, -ux))
    ix, iy = uy, -ux

    q0 = (p0_ft[0] + ux * trim_start_ft, p0_ft[1] + uy * trim_start_ft)
    q1 = (p1_ft[0] - ux * trim_end_ft, p1_ft[1] - uy * trim_end_ft)

    spandrels = [
        (z_l2_m - 0.30, z_l2_m + 0.85),       # Cantilevered L2 slab edge to L2 window sill
        (z_l2_m + 2.75, z_l3_m + 0.90),       # L2 window head to L3 carrel sill buff-brick spandrel
        (z_parapet_m - 0.95, z_parapet_m),    # Upper North brick parapet fascia
    ]
    for zb, zt in spandrels:
        add_wall_strip_ft(mesh, [q0, q1], 1.12, zb, zt, MATERIALS["buff_brick"], offset_mode="right")

    # Window Glazing Bands (L2 ribbon and tall L3 Clerestory rising into the Tipped North Roof)
    g0 = (q0[0] + ix * 0.48, q0[1] + iy * 0.48)
    g1 = (q1[0] + ix * 0.48, q1[1] + iy * 0.48)
    win_bands = [
        (z_l2_m + 0.85, z_l2_m + 2.75, True),
        (z_l3_m + 0.90, z_parapet_m - 0.95, True),
    ]

    ang_deg = math.degrees(math.atan2(dy, dx))
    eff_L = max(8.0, L - trim_start_ft - trim_end_ft)
    n_mull = max(4, int(eff_L / 5.2))
    for zb, zt, has_louvers in win_bands:
        add_wall_strip_ft(mesh, [g0, g1], 0.18, zb, zt, MATERIALS["glass_clear"], offset_mode="center")
        for k in range(n_mull + 1):
            t = k / n_mull
            mx = g0[0] + (g1[0] - g0[0]) * t
            my = g0[1] + (g1[1] - g0[1]) * t
            add_oriented_box_ft(mesh, (mx, my), 0.24, 0.52, ang_deg, zb, zt, MATERIALS["mullion_bronze"])
        if has_louvers:
            add_louver_bank_ft(mesh, q0, q1, zb + 0.08, zt - 0.08, spacing_ft=2.35, blade_depth_ft=0.92, blade_thick_ft=0.19)


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

    #   (b) Levels 2–Roof Splayed Irregular Buff-Brick H-Columns (cantilevering forward at Level 2)
    for hp_poly in get_h_pier_polygons_ft(level=3):
        add_extruded_polygon_ft(
            ms,
            hp_poly,
            z_l2 - 0.30,
            z_par_n + 0.04,
            MATERIALS["buff_brick_dark"],
            MATERIALS["buff_brick"],
            MATERIALS["concrete"],
        )
        # Exterior rainwater scupper leader pipe descending inside the recessed H-pocket (Sheet 07-a7)
        wx = 0.5 * (hp_poly[2][0] + hp_poly[3][0])
        wy = 0.5 * (hp_poly[2][1] + hp_poly[3][1])
        tx = 0.5 * (hp_poly[1][0] + hp_poly[4][0]) - wx
        ty = 0.5 * (hp_poly[1][1] + hp_poly[4][1]) - wy
        tl = max(1e-4, math.hypot(tx, ty))
        scup_pt = (wx + (tx / tl) * 0.42, wy + (ty / tl) * 0.42)
        add_cylinder_ft(ms, scup_pt, 0.18, z_crawl + 0.6, z_par_n - 0.18, MATERIALS["copper_roof"], sides=12)

    # Radial Structural Ceiling Ribs radiating from WP #3 out to North Curtain Wall
    for b_deg in (152.0, G.RAY_B_DEG, 119.0, G.RAY_C_DEG, 83.0, G.RAY_D_DEG, 49.0):
        p_in = polar_pt(G.WP3, 45.0, b_deg)
        p_out = polar_pt(G.WP3, 83.0, b_deg)
        add_wall_strip_ft(ms, [p_in, p_out], 0.65, z_fan_low - 0.38, z_fan_low, MATERIALS["white_soffit"])

    # =========================================================================
    # LAYER 6: FACETED NORTH BRICK CURTAIN WALL, MT. HOOD WINDOW & SOUTH WING
    # =========================================================================
    grp_env = create_scene_group(scene, "6_Envelope_And_South_Wing")
    me = grp_env.mesh

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

    # West Fan Throat Wall (PT_A -> PT_A_INNER_JUNC -> Grid 6)
    add_wall_strip_ft(me, [G.PT_A, G.PT_A_INNER_JUNC, (-77.5, 1.5)], 1.25, z_l1 - 1.0, z_par_n - 0.4, MATERIALS["buff_brick"])

    # East Diagonal Fan Wall along Axis E (PT_E -> PT_LOUNGE_JUNC, enclosing Stair #2)
    add_wall_strip_ft(me, [G.PT_E, G.PT_LOUNGE_JUNC], 1.30, z_l1 - 1.0, z_par_n - 0.4, MATERIALS["buff_brick"])

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
