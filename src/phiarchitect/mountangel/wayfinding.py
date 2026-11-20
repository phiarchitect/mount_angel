"""Parametric CSS-variable-driven SVG wayfinding & print graphics for Mount Angel Abbey Library.

Derives visitor floor plans, longitudinal skylight & bluff cross-section, Abbey hilltop
campus locator map, constructive detail medallions, and polycentric signature diagrams
directly from ``phiarchitect.mountangel.vectors.AaltoGeometry``.

Every generated SVG uses semantic CSS classes and custom properties (``var(--paper)``,
``var(--ink)``, ``var(--poche)``, ``var(--accent)``, ``var(--birch)``, ``var(--sky)``,
``var(--gold)``) so interactive web layouts and print stylesheets can switch themes,
poché hatches, line weights, and graphic layers instantaneously without regenerating files.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from collections.abc import Callable

from .vectors import AaltoGeometry as G
from .vectors import (
    arc_pts,
    get_carrel_alcoves_ft,
    get_h_pier_polygons_ft,
    get_l1_inner_pentagon_ft,
    get_level1_envelope_ft,
    get_level2_envelope_ft,
    get_level3_envelope_ft,
    get_radial_bookstacks_ft,
    get_well_stairs_ft,
    polar_pt,
)


def _catmull_rom(
    ctrl: list[tuple[float, float]], n_sub: int = 4
) -> list[tuple[float, float]]:
    """Interpolate a smooth open Catmull-Rom spline through 2D control points."""
    pts: list[tuple[float, float]] = []
    m = len(ctrl)
    for i in range(m - 1):
        p0 = ctrl[max(0, i - 1)]
        p1 = ctrl[i]
        p2 = ctrl[i + 1]
        p3 = ctrl[min(m - 1, i + 2)]
        steps = n_sub if i < m - 2 else n_sub + 1
        for s in range(steps):
            t = s / n_sub
            t2, t3 = t * t, t * t * t
            x = 0.5 * (
                2 * p1[0]
                + (-p0[0] + p2[0]) * t
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                2 * p1[1]
                + (-p0[1] + p2[1]) * t
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            pts.append((x, y))
    return pts


def _rect_pts(
    cx: float, cy: float, length: float, width: float, deg: float
) -> list[tuple[float, float]]:
    """Return 4 oriented rectangle corners in canonical feet."""
    rad = math.radians(deg)
    ux, uy = math.cos(rad), math.sin(rad)
    vx, vy = -uy, ux
    hl, hw = 0.5 * length, 0.5 * width
    return [
        (cx - hl * ux - hw * vx, cy - hl * uy - hw * vy),
        (cx + hl * ux - hw * vx, cy + hl * uy - hw * vy),
        (cx + hl * ux + hw * vx, cy + hl * uy + hw * vy),
        (cx - hl * ux + hw * vx, cy - hl * uy + hw * vy),
    ]


def build_shared_svg_defs() -> str:
    """Return a hidden, always-mounted SVG holding shared gradients, hatches, and arrowheads."""
    return """<svg class="wf-shared-defs" aria-hidden="true" width="0" height="0" style="position:absolute;width:0;height:0;overflow:hidden;pointer-events:none">
  <defs>
    <pattern id="wfDiagHatch" width="6" height="6" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="6" class="wf-hatch-stroke"/>
    </pattern>
    <pattern id="wfEarthHatch" width="8" height="8" patternTransform="rotate(-30 0 0)" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="8" class="wf-earth-hatch-stroke"/>
    </pattern>
    <linearGradient id="wfSkyGlow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="var(--sky)" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="var(--sky)" stop-opacity="0.0"/>
    </linearGradient>
    <linearGradient id="wfSunGlow" x1="0" y1="0" x2="0.15" y2="1">
      <stop offset="0%" stop-color="var(--gold)" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="var(--gold)" stop-opacity="0.02"/>
    </linearGradient>
    <marker id="wfArrowSky" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="5" markerHeight="5" orient="auto">
      <path d="M0.5,1.2 L7,4 L0.5,6.8 Z" fill="var(--sky)"/>
    </marker>
    <marker id="wfArrowSun" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="5" markerHeight="5" orient="auto">
      <path d="M0.5,1.2 L7,4 L0.5,6.8 Z" fill="var(--gold)"/>
    </marker>
    <marker id="wfArrowVista" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="5.5" markerHeight="5.5" orient="auto">
      <path d="M0.5,1.2 L7,4 L0.5,6.8 Z" fill="var(--accent)"/>
    </marker>
  </defs>
</svg>"""


def build_emblem_svg() -> str:
    """Compact geometric masthead emblem of Aalto's polycentric fan & daylight scoop."""
    ox, oy, sc = 44.0, 56.0, 0.46

    def xy(pt: tuple[float, float]) -> tuple[float, float]:
        return (ox + pt[0] * sc, oy - pt[1] * sc)

    def pts_s(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{xy(p)[0]:.1f},{xy(p)[1]:.1f}" for p in pts)

    env = get_level3_envelope_ft()
    scoop = arc_pts(G.WP3A, G.R_SCOOP_RIDGE, 45.0, 156.0, 24)
    well = arc_pts(G.WP3A, G.R_MEZZ_OPENING, 42.0, 161.0, 24)
    rays = []
    for orig, deg in (
        (G.WP2, G.RAY_A_DEG),
        (G.WP3, G.RAY_B_DEG),
        (G.WP3, G.RAY_C_DEG),
        (G.WP3, G.RAY_D_DEG),
        (G.WP2, G.RAY_E_DEG),
    ):
        pa, pb = xy(orig), xy(polar_pt(orig, 86.0, deg))
        rays.append(
            f'  <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-emblem-ray"/>'
        )
    wp = xy(G.WP3)
    return "\n".join(
        [
            '<svg viewBox="0 0 96 78" class="wf-svg wf-emblem-svg" role="img" aria-label="Mount Angel Library Polycentric Fan Emblem">',
            f'  <polygon points="{pts_s(env)}" class="wf-emblem-fill"/>',
            *rays,
            f'  <polyline points="{pts_s(well)}" class="wf-emblem-arc"/>',
            f'  <polyline points="{pts_s(scoop)}" class="wf-emblem-scoop"/>',
            f'  <polygon points="{pts_s(env)}" class="wf-emblem-outline"/>',
            f'  <circle cx="{wp[0]:.1f}" cy="{wp[1]:.1f}" r="2.2" class="wf-wp-dot"/>',
            "</svg>",
        ]
    )


def build_level3_wayfinding_svg(compact: bool = False) -> str:
    """Generate CSS-themed Main Entrance & Fan Reading Room (Level 3 + Mezzanine Well) SVG.

    North (+Y) is UP so a visitor standing in the South Lobby facing North into the
    Library reads Left = West, Right = East, Straight Ahead = Sunken Reading Well & Fan.
    """
    w_vb, h_vb = (760, 535) if compact else (920, 648)
    sc = w_vb / 252.0
    ox = 141.0 * sc
    oy = 102.5 * sc

    def xy(pt: tuple[float, float]) -> tuple[float, float]:
        return (ox + pt[0] * sc, oy - pt[1] * sc)

    def pts_s(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{xy(p)[0]:.1f},{xy(p)[1]:.1f}" for p in pts)

    x_w = G.X_WEST_WING
    x_step = G.X_SOUTH_STEP
    x_elev = G.X_ELEV_E
    x_rest = G.X_RESTROOM_E
    x_lob_e = G.X_LOBBY_E_G2
    x_aud_sw = G.X_AUD_SW
    x_lng_e = G.X_LOUNGE_E
    x_aud_e = G.X_AUD_E
    y_g6 = G.GRID_Y["6"]
    y_g5 = G.GRID_Y["5"]
    y_g4 = G.GRID_Y["4"]
    y_g3 = G.GRID_Y["3"]
    y_g2 = G.GRID_Y["2"]
    y_g1 = G.GRID_Y["1"]
    y_vest_s = y_g2 - 6.8

    out: list[str] = [
        f'<svg viewBox="0 0 {w_vb} {h_vb}" class="wf-svg wf-plan-l3" role="img" aria-label="Level 3 Main Reading Room &amp; Entrance Wayfinding Plan">',
    ]

    # 1. Zone Tints (toggleable via .layer-zones)
    env_l3 = get_level3_envelope_ft()
    well_outer = arc_pts(G.WP3A, G.R_MEZZ_OPENING, 41.8, 161.5, 44)
    well_inner = list(reversed(arc_pts(G.WP3A, G.R_GALLERY_RAIL, 41.8, 161.5, 32)))
    well_ring = well_outer + well_inner

    aud_poly = [(x_lob_e, y_g2), (x_aud_sw, y_g1), (x_aud_e, y_g1), (x_aud_e, y_g4), (18.5, y_g4)]
    lounge_poly = [G.PT_EAST_THROAT, G.PT_LOUNGE_JUNC, (x_lng_e, y_g5), (19.0, y_g5), (19.0, -4.8)]
    staff_west = [
        (x_w, y_g6),
        (x_elev, y_g6),
        (x_elev, y_g4),
        (-44.0, y_g4),
        (-44.0, y_g2),
        (x_step, y_g2),
        (x_step, y_g3),
        (x_w, y_g3),
    ]

    out.append('  <g class="layer-zones">')
    out.append(f'    <polygon points="{pts_s(env_l3)}" class="zone-quiet"/>')
    out.append(f'    <polygon points="{pts_s(staff_west)}" class="zone-staff"/>')
    out.append(
        f'    <polygon points="{pts_s([(18.5, y_g4), (x_aud_e, y_g4), (x_aud_e, y_g5), (18.5, y_g5)])}" class="zone-staff"/>'
    )
    out.append(f'    <polygon points="{pts_s(lounge_poly)}" class="zone-lounge"/>')
    out.append(f'    <polygon points="{pts_s(aud_poly)}" class="zone-auditorium"/>')
    out.append(
        f'    <polygon points="{pts_s([(x_rest, y_g2), (x_lob_e, y_g2), (18.5, y_g4), G.PT_EAST_THROAT, G.PT_WEST_THROAT, (-17.5, y_g4), (x_rest, y_g3)])}" class="zone-public"/>'
    )
    out.append(
        f'    <polygon points="{pts_s([(-18.5, y_vest_s), (0.0, y_vest_s), (0.0, y_g2), (-18.5, y_g2)])}" class="zone-public"/>'
    )
    out.append(f'    <polygon points="{pts_s(well_ring)}" class="zone-well"/>')
    out.append("  </g>")

    # 2. Entry Plaza & Pergola Trellises (South Portico)
    out.append('  <g class="layer-site-plaza">')
    out.append(
        f'    <polygon points="{pts_s([(-36.5, -69.5), (18.5, -69.5), (18.5, y_g2), (-36.5, y_g2)])}" class="wf-plaza"/>'
    )
    for x0, x1 in ((-35.5, -19.0), (0.5, 16.5)):
        out.append(
            f'    <polygon points="{pts_s([(x0, -65.5), (x1, -65.5), (x1, y_g2), (x0, y_g2)])}" class="wf-pergola"/>'
        )
        for gx in range(int(x0) + 4, int(x1), 4):
            p_a, p_b = xy((gx, -65.5)), xy((gx, y_g2))
            out.append(
                f'    <line x1="{p_a[0]:.1f}" y1="{p_a[1]:.1f}" x2="{p_b[0]:.1f}" y2="{p_b[1]:.1f}" class="wf-pergola-grid"/>'
            )
    out.append(
        f'    <polygon points="{pts_s([(-19.0, -67.0), (0.5, -67.0), (0.5, y_g2), (-19.0, y_g2)])}" class="wf-canopy-marquee"/>'
    )
    if not compact:
        ep = xy((-9.0, -63.5))
        out.append(
            f'    <text x="{ep[0]:.1f}" y="{ep[1]:.1f}" text-anchor="middle" class="wf-tech-lbl">SOUTH ENTRY PORTICO &amp; PERGOLAS ↑</text>'
        )
    out.append("  </g>")

    # 3. Regulating Compass Lines & Rays (toggleable via .layer-reg)
    out.append('  <g class="layer-reg">')
    for deg in (G.RAY_B_DEG, G.RAY_C_DEG, G.RAY_D_DEG):
        pa, pb = xy(G.WP3), xy(polar_pt(G.WP3, 98.0, deg))
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-reg-ray"/>'
        )
    for deg, r_m in ((G.RAY_A_DEG, 100.0), (G.RAY_E_DEG, 114.0)):
        pa, pb = xy(G.WP2), xy(polar_pt(G.WP2, r_m, deg))
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-reg-ray-alt"/>'
        )
    out.append(
        f'    <polyline points="{pts_s(arc_pts(G.WP3A, G.R_WELL_L2_WALL, 38.0, 164.0, 40))}" class="wf-reg-arc"/>'
    )
    wp_px = xy(G.WP3)
    out.append(
        f'    <circle cx="{wp_px[0]:.1f}" cy="{wp_px[1]:.1f}" r="3.2" class="wf-wp-dot"/>'
    )
    if not compact:
        out.append(
            f'    <text x="{wp_px[0] + 6:.1f}" y="{wp_px[1] + 9:.1f}" class="wf-tech-lbl">WP #3 (0,0)</text>'
        )
    out.append("  </g>")

    # 4. Millwork, Bookcases, Stairs, Workbench & Auditorium Seating
    out.append('  <g class="layer-millwork">')
    out.append(f'    <polygon points="{pts_s(well_ring)}" class="wf-well-void"/>')
    out.append(
        f'    <polyline points="{pts_s(arc_pts(G.WP3A, G.R_WELL_L2_WALL, 55.8, 147.8, 36))}" class="wf-mezz-curve"/>'
    )
    out.append(
        f'    <polyline points="{pts_s(arc_pts(G.WP3A, 29.42, 55.8, 147.8, 36))}" class="wf-mezz-desk"/>'
    )

    for st in get_well_stairs_ft():
        out.append(f'    <polygon points="{pts_s(st)}" class="wf-stair"/>')
    # 3-riser (+1'-4" -> 0'-0") Lobby-to-Entry steps per Sheet 13-a13 Det. 15
    for sy in (y_g4, y_g4 + 1.05, y_g4 + 2.10):
        pa, pb = xy((-16.5, sy)), xy((16.0, sy))
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-stair-tread"/>'
        )

    wb_band = arc_pts(G.WP3A, G.R_MEZZ_OPENING, 47.9, 155.4, 40) + list(
        reversed(arc_pts(G.WP3A, G.R_MEZZ_DESK, 47.9, 155.4, 40))
    )
    out.append(f'    <polygon points="{pts_s(wb_band)}" class="wf-workbench"/>')
    for i in range(16):
        lp = xy(polar_pt(G.WP3A, G.R_MEZZ_OPENING + 0.8, 51.2 + i * (101.0 / 15.0)))
        out.append(
            f'    <circle cx="{lp[0]:.1f}" cy="{lp[1]:.1f}" r="1.5" class="wf-lamp-dot"/>'
        )

    for st_deg, r_sgn in ((41.8, -1.0), (161.5, +1.0)):
        s_rad = math.radians(st_deg)
        urx, ury = math.cos(s_rad), math.sin(s_rad)
        tx, ty = r_sgn * (-ury), r_sgn * urx
        cx0, cy0 = G.WP3A
        bk = [
            (cx0 + G.R_GALLERY_RAIL * urx, cy0 + G.R_GALLERY_RAIL * ury),
            (cx0 + G.R_MEZZ_OPENING * urx, cy0 + G.R_MEZZ_OPENING * ury),
            (cx0 + G.R_MEZZ_OPENING * urx + 1.8 * tx, cy0 + G.R_MEZZ_OPENING * ury + 1.8 * ty),
            (cx0 + G.R_GALLERY_RAIL * urx + 1.8 * tx, cy0 + G.R_GALLERY_RAIL * ury + 1.8 * ty),
        ]
        out.append(f'    <polygon points="{pts_s(bk)}" class="wf-bookcase"/>')

    desk_band = arc_pts(G.WP_DESK, G.R_DESK_INNER, 28.0, 162.0, 30) + list(
        reversed(arc_pts(G.WP_DESK, G.R_DESK_OUTER, 28.0, 162.0, 30))
    )
    out.append(f'    <polygon points="{pts_s(desk_band)}" class="wf-control-desk"/>')
    slat_halo = arc_pts(G.WP_DESK, 19.2, 26.0, 172.0, 32)
    out.append(f'    <polyline points="{pts_s(slat_halo)}" class="wf-ceiling-halo"/>')

    r_start = 51.2
    r_ends = [
        67.8,
        69.4,
        71.0,
        68.2,
        70.4,
        71.2,
        69.8,
        68.0,
        68.5,
        70.8,
        71.2,
        69.2,
        67.5,
        69.8,
        70.5,
    ]
    stack_angles = [
        159.0,
        153.2,
        147.8,
        132.5,
        126.6,
        120.8,
        115.0,
        109.2,
        93.4,
        86.4,
        79.4,
        72.4,
        56.5,
        50.5,
        44.5,
    ]
    for deg, r_end in zip(stack_angles, r_ends):
        rad = math.radians(deg)
        l_stk = r_end - r_start
        r_mid = 0.5 * (r_start + r_end)
        cx_s = G.WP3A[0] + r_mid * math.cos(rad)
        cy_s = G.WP3A[1] + r_mid * math.sin(rad)
        out.append(
            f'    <polygon points="{pts_s(_rect_pts(cx_s, cy_s, l_stk, 2.75, deg))}" class="wf-bookcase"/>'
        )

    for box in get_carrel_alcoves_ft():
        out.append(
            f'    <polyline points="{pts_s([box[3], box[0], box[1], box[2]])}" class="wf-carrel"/>'
        )
    for py_ft in (4.0, 15.0, 25.0):
        tc = xy((38.5, py_ft))
        out.append(
            f'    <circle cx="{tc[0]:.1f}" cy="{tc[1]:.1f}" r="{2.4 * sc:.1f}" class="wf-table"/>'
        )

    for cx_c, cy_c in ((-33.5, -8.0), (-26.0, -8.0), (-30.0, -14.5)):
        out.append(
            f'    <polygon points="{pts_s(_rect_pts(cx_c, cy_c, 5.8, 2.3, 0.0))}" class="wf-bookcase"/>'
        )

    stage_c = (x_aud_e - 1.3, y_g1 + 1.3)
    stage_poly = [stage_c] + arc_pts(stage_c, 15.8, 90.0, 180.0, 18)
    out.append(f'    <polygon points="{pts_s(stage_poly)}" class="wf-stage"/>')
    out.append(
        f'    <polyline points="{pts_s(arc_pts(stage_c, 18.0, 90.0, 180.0, 18))}" class="wf-stair-tread"/>'
    )
    for r_seat in (22.5, 26.2, 29.9, 33.6, 37.3):
        out.append(
            f'    <polyline points="{pts_s(arc_pts(stage_c, r_seat, 98.0, 172.0, 16))}" class="wf-seat-arc"/>'
        )

    pa_scr, pb_scr = xy((-30.0, -45.5)), xy((-30.0, -32.2))
    out.append(
        f'    <line x1="{pa_scr[0]:.1f}" y1="{pa_scr[1]:.1f}" x2="{pb_scr[0]:.1f}" y2="{pb_scr[1]:.1f}" class="wf-wood-screen"/>'
    )

    for j in range(14):
        f_t = (j + 0.5) / 14.0
        fx = -17.5 + f_t * (-19.0 - (-17.5))
        fy = -18.0 + f_t * (0.2 - (-18.0))
        out.append(
            f'    <polygon points="{pts_s(_rect_pts(fx, fy, 1.3, 0.35, 94.2 + 28.0))}" class="wf-wood-fin"/>'
        )

    scoop_band = arc_pts(G.WP3A, G.R_SCOOP_RIDGE, 46.0, 155.0, 32) + list(
        reversed(arc_pts(G.WP3A, G.R_SCOOP_OUTER, 46.0, 155.0, 32))
    )
    out.append(
        f'    <polygon points="{pts_s(scoop_band)}" class="wf-skylight-overhead"/>'
    )
    for sx, sy, sr in G.CONICAL_SKYLIGHTS:
        sp = xy((sx, sy))
        out.append(
            f'    <circle cx="{sp[0]:.1f}" cy="{sp[1]:.1f}" r="{sr * sc:.1f}" class="wf-skylight-circle"/>'
        )
    out.append("  </g>")

    # 5. Interior Partitions, Glazed Wall & Heavy Structural Envelope Walls
    out.append('  <g class="layer-walls">')
    for seg in (
        [(-54.0, y_g3), (x_rest, y_g3)],
        [(-54.0, -40.0), (x_rest, -40.0)],
        [(-54.0, y_g2), (-54.0, y_g3)],
        [(x_rest, y_g2), (x_rest, -46.2)],
        [(x_rest, -43.2), (x_rest, -36.2)],
        [(x_rest, -33.2), (x_rest, y_g3)],
    ):
        out.append(f'    <polyline points="{pts_s(seg)}" class="wf-wall-int"/>')

    serp = _catmull_rom(
        [
            (-44.0, y_g4 + 0.4),
            (-44.0, -11.0),
            (-41.8, -5.2),
            (-38.5, -1.2),
            (-36.8, -0.5),
            (-33.3, 1.0),
            (-30.5, 1.6),
        ]
    )
    out.append(f'    <polyline points="{pts_s(serp)}" class="wf-wall-int-bold"/>')

    for seg in (
        [(x_elev, y_g6), (x_elev, y_g4), (-44.0, y_g4)],
        [(x_elev, y_g4), (x_elev, y_g2)],
    ):
        out.append(f'    <polyline points="{pts_s(seg)}" class="wf-wall-int"/>')

    out.append(
        f'    <line x1="{xy(G.PT_EAST_THROAT)[0]:.1f}" y1="{xy(G.PT_EAST_THROAT)[1]:.1f}" x2="{xy(G.PT_LOUNGE_JUNC)[0]:.1f}" y2="{xy(G.PT_LOUNGE_JUNC)[1]:.1f}" class="wf-glass-wall"/>'
    )
    for k in range(15):
        t = k / 14.0
        mx, my = xy((
            G.PT_EAST_THROAT[0] + t * (G.PT_LOUNGE_JUNC[0] - G.PT_EAST_THROAT[0]),
            G.PT_EAST_THROAT[1] + t * (G.PT_LOUNGE_JUNC[1] - G.PT_EAST_THROAT[1]),
        ))
        out.append(
            f'    <circle cx="{mx:.1f}" cy="{my:.1f}" r="1.2" class="wf-mullion-dot"/>'
        )
    for seg in (
        [(26.2, 12.1), (39.6, -4.8)],
        [G.PT_EAST_THROAT, (17.2, -0.8), (19.0, -4.8), (x_lng_e - 0.5, -4.8)],
        [(18.5, y_g5), (x_lng_e, y_g5)],
        [(18.5, y_g4), (42.0, y_g4)],
        [(47.0, y_g4), (x_aud_e, y_g4)],
        [(26.0, y_g4), (26.0, y_g5)],
        [(37.0, y_g4), (37.0, y_g5)],
        [(x_lob_e, y_g2 + 0.5), (17.8, -43.5)],
        [(18.0, -38.0), (18.5, y_g4)],
        [(18.8, -27.2), (21.5, -27.7), (25.0, -27.5), (29.0, -25.3), (32.0, y_g4 - 0.3)],
    ):
        out.append(f'    <polyline points="{pts_s(seg)}" class="wf-wall-int"/>')

    out.append(
        f'    <polygon points="{pts_s([(-18.5, y_vest_s), (0.0, y_vest_s), (0.0, y_g2), (-18.5, y_g2)])}" class="wf-glass-vestibule"/>'
    )

    out.append(f'    <polygon points="{pts_s(env_l3)}" class="wf-wall-ext"/>')
    for hp_poly in get_h_pier_polygons_ft(level=3):
        out.append(f'    <polygon points="{pts_s(hp_poly)}" class="wf-poche-solid"/>')
    for cpt in [
        *G.WELL_COLS_FT.values(),
        *G.PAIRED_COLS_FT.values(),
        *G.SOUTH_WING_COLS_FT,
    ]:
        cx_p, cy_p = xy(cpt)
        out.append(
            f'    <circle cx="{cx_p:.1f}" cy="{cy_p:.1f}" r="{max(1.8, 0.85 * sc):.1f}" class="wf-col-dot"/>'
        )

    hp_d = get_h_pier_polygons_ft(level=3)[2]
    mh_orig = ((hp_d[2][0] + hp_d[3][0]) * 0.5, (hp_d[2][1] + hp_d[3][1]) * 0.5)
    mh_tip = (
        mh_orig[0] + 19.0 * math.cos(math.radians(G.RAY_D_DEG)),
        mh_orig[1] + 19.0 * math.sin(math.radians(G.RAY_D_DEG)),
    )
    p_mh0, p_mh1 = xy(mh_orig), xy(mh_tip)
    out.append(
        f'    <line x1="{p_mh0[0]:.1f}" y1="{p_mh0[1]:.1f}" x2="{p_mh1[0]:.1f}" y2="{p_mh1[1]:.1f}" class="wf-vista-arrow" marker-end="url(#wfArrowVista)"/>'
    )
    out.append(
        f'    <text x="{p_mh1[0] - 10:.1f}" y="{p_mh1[1] - 6:.1f}" class="wf-vista-lbl">MT. HOOD VISTA ({G.RAY_D_DEG:.1f}°) ↗</text>'
    )
    out.append("  </g>")

    # Subtle room tags on large Poster plan
    if not compact:
        out.append('  <g class="layer-room-tags">')
        for rx, ry, rtxt in (
            (-36.0, 56.0, "MAIN FAN READING ROOM (0'-0\")"),
            (-2.0, 33.5, "SUNKEN WELL"),
            (37.5, -50.5, "AUDITORIUM"),
            (-104.0, -14.0, "CATALOGING"),
            (38.0, -15.2, "RARE BOOK VAULT"),
        ):
            rp = xy((rx, ry))
            out.append(
                f'    <text x="{rp[0]:.1f}" y="{rp[1]:.1f}" text-anchor="middle" class="wf-room-tag">{rtxt}</text>'
            )
        out.append("  </g>")

    # 6. YOU ARE HERE Beacon + Numbered Visitor Pins (1..9 on Level 3)
    yah = xy((-9.0, -38.5))
    out.append('  <g class="layer-pins">')
    out.append(
        f'    <circle cx="{yah[0]:.1f}" cy="{yah[1]:.1f}" r="{12.5 if not compact else 9.8}" class="wf-yah-pulse"/>'
    )
    out.append(
        f'    <circle cx="{yah[0]:.1f}" cy="{yah[1]:.1f}" r="{7.4 if not compact else 6.2}" class="wf-yah-core"/>'
    )
    out.append(
        f'    <text x="{yah[0]:.1f}" y="{yah[1] + 3.2:.1f}" text-anchor="middle" class="wf-yah-star">★</text>'
    )
    out.append(
        f'    <text x="{yah[0]:.1f}" y="{yah[1] + (21 if not compact else 17):.1f}" text-anchor="middle" class="wf-yah-lbl">YOU ARE HERE</text>'
    )

    pins_l3 = [
        ("1", (-38.5, -39.0), "Restrooms & Wood Screen"),
        ("2", (39.0, -37.5), "Rare Book Auditorium"),
        ("3", (-29.5, -8.5), "Public Catalogue & Squiggle Walls"),
        ("4", (-1.5, 11.5), "Control Desk & Slatted Ceiling"),
        ("5", (34.5, 12.0), "Glazed Offices & Media Lounge"),
        ("6", (-12.0, 45.8), "Mezzanine Reading Counter"),
        ("7", (14.5, 61.5), "Radiating Birch Bookstacks"),
        ("8", (31.5, 73.5), "H-Col D Mt. Hood Window"),
        ("9", (-86.0, -34.0), "Cataloging & Technical Services"),
    ]
    r_pin = 8.4 if not compact else 6.9
    for num, pt_w, title in pins_l3:
        px, py = xy(pt_w)
        safe_t = title.replace("&", "&amp;")
        out.append(
            f'    <g class="wf-pin" data-pin="{num}" tabindex="0" role="button" aria-label="{num}. {safe_t}">'
        )
        out.append(
            f'      <circle cx="{px:.1f}" cy="{py:.1f}" r="{r_pin:.1f}" class="wf-pin-bg"/>'
        )
        out.append(
            f'      <text x="{px:.1f}" y="{py + (3.2 if not compact else 2.7):.1f}" text-anchor="middle" class="wf-pin-txt">{num}</text>'
        )
        out.append("    </g>")

    cx_n, cy_n = 34, 38
    out.append(f'    <g transform="translate({cx_n},{cy_n})" class="wf-compass">')
    out.append('      <circle cx="0" cy="0" r="14" class="wf-compass-ring"/>')
    out.append('      <polygon points="0,-12 3.5,2 0,-1 -3.5,2" class="wf-compass-needle"/>')
    out.append('      <text x="0" y="-17" text-anchor="middle" class="wf-compass-lbl">N</text>')
    out.append("    </g>")

    sb_x, sb_y = 24, h_vb - 18
    w_40ft = 40.0 * sc
    out.append(f'    <g transform="translate({sb_x},{sb_y})" class="wf-scalebar">')
    out.append(
        f'      <line x1="0" y1="0" x2="{w_40ft:.1f}" y2="0" class="wf-scale-line"/>'
    )
    out.append('      <line x1="0" y1="-4" x2="0" y2="4" class="wf-scale-line"/>')
    out.append(
        f'      <line x1="{w_40ft * 0.5:.1f}" y1="-3" x2="{w_40ft * 0.5:.1f}" y2="3" class="wf-scale-line"/>'
    )
    out.append(
        f'      <line x1="{w_40ft:.1f}" y1="-4" x2="{w_40ft:.1f}" y2="4" class="wf-scale-line"/>'
    )
    out.append(
        f'      <text x="{w_40ft + 6:.1f}" y="3" class="wf-scale-lbl">0   20   40 FT</text>'
    )
    out.append("    </g>")
    out.append("  </g>")

    out.append("</svg>")
    return "\n".join(out)


def build_lower_levels_svg() -> str:
    """Side-by-side Mezzanine (-5'-4") / Level 2 (-14'-0") and Level 1 (-28'-6") plans."""
    w_vb, h_vb = 900, 360
    sc = 2.02

    def xy_l2(pt: tuple[float, float]) -> tuple[float, float]:
        return (235.0 + pt[0] * sc, 212.0 - pt[1] * sc)

    def xy_l1(pt: tuple[float, float]) -> tuple[float, float]:
        return (685.0 + pt[0] * sc, 224.0 - pt[1] * sc)

    def pts_fn(
        pts: list[tuple[float, float]],
        fn: Callable[[tuple[float, float]], tuple[float, float]],
    ) -> str:
        return " ".join(f"{fn(p)[0]:.1f},{fn(p)[1]:.1f}" for p in pts)

    out: list[str] = [
        f'<svg viewBox="0 0 {w_vb} {h_vb}" class="wf-svg wf-plan-lower" role="img" aria-label="Mezzanine, Level 2, and Level 1 Lower Floor Plans">',
        '  <line x1="462" y1="16" x2="462" y2="344" class="wf-panel-divider"/>',
    ]

    # Left Panel: Mezzanine & Level 2
    env_l2 = get_level2_envelope_ft()
    out.append('  <g class="panel-l2">')
    out.append(
        '    <text x="18" y="24" class="wf-subplan-kicker">MEZZANINE (-5\'-4") &amp; LEVEL 2 (-14\'-0")</text>'
    )
    out.append(
        '    <text x="18" y="40" class="wf-subplan-sub">Reference Gallery, Well Core &amp; Study Carrels</text>'
    )
    out.append(
        f'    <polygon points="{pts_fn(env_l2, xy_l2)}" class="zone-quiet layer-zones"/>'
    )
    mezz_cres = arc_pts(G.WP3A, G.R_WELL_L2_WALL, 42.0, 161.0, 32) + list(
        reversed(arc_pts(G.WP3A, G.R_GALLERY_RAIL, 42.0, 161.0, 28))
    )
    out.append(
        f'    <polygon points="{pts_fn(mezz_cres, xy_l2)}" class="zone-lounge layer-zones"/>'
    )

    out.append('    <g class="layer-reg">')
    for deg in (G.RAY_B_DEG, G.RAY_C_DEG, G.RAY_D_DEG):
        pa, pb = xy_l2(G.WP3), xy_l2(polar_pt(G.WP3, 94.0, deg))
        out.append(
            f'      <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-reg-ray"/>'
        )
    out.append("    </g>")

    for stk in get_radial_bookstacks_ft(34.4, 47.4)[2:13]:
        out.append(
            f'    <polygon points="{pts_fn(stk, xy_l2)}" class="wf-bookcase"/>'
        )
    for stk in get_radial_bookstacks_ft(51.4, 68.5):
        out.append(
            f'    <polygon points="{pts_fn(stk, xy_l2)}" class="wf-bookcase"/>'
        )
    for st in get_well_stairs_ft():
        out.append(f'    <polygon points="{pts_fn(st, xy_l2)}" class="wf-stair"/>')
    for box in get_carrel_alcoves_ft():
        out.append(
            f'    <polyline points="{pts_fn([box[3], box[0], box[1], box[2]], xy_l2)}" class="wf-carrel"/>'
        )

    wb_m = arc_pts(G.WP3A, 29.4, 55.8, 147.8, 30) + list(
        reversed(arc_pts(G.WP3A, G.R_WELL_L2_WALL, 55.8, 147.8, 30))
    )
    out.append(f'    <polygon points="{pts_fn(wb_m, xy_l2)}" class="wf-workbench"/>')
    out.append(
        f'    <polyline points="{pts_fn(arc_pts(G.WP3A, G.R_GALLERY_RAIL, 45.0, 158.0, 28), xy_l2)}" class="wf-control-desk-line"/>'
    )
    out.append(
        f'    <polyline points="{pts_fn(arc_pts(G.WP3A, G.R_WELL_L2_WALL, 42.0, 161.0, 34), xy_l2)}" class="wf-wall-int-bold"/>'
    )

    out.append(f'    <polygon points="{pts_fn(env_l2, xy_l2)}" class="wf-wall-ext"/>')
    for hp_poly in get_h_pier_polygons_ft(level=3):
        out.append(
            f'    <polygon points="{pts_fn(hp_poly, xy_l2)}" class="wf-poche-solid"/>'
        )
    for cpt in [*G.WELL_COLS_FT.values(), *G.PAIRED_COLS_FT.values()]:
        cx_p, cy_p = xy_l2(cpt)
        out.append(
            f'    <circle cx="{cx_p:.1f}" cy="{cy_p:.1f}" r="1.9" class="wf-col-dot"/>'
        )

    out.append('    <g class="layer-pins">')
    for num, pt_w, title in [
        ("10", (-16.0, 27.5), "Mezzanine Study Counter (-5 ft 4 in)"),
        ("11", (10.0, 41.5), "Level 2 Reference &amp; Stacks (-14 ft 0 in)"),
    ]:
        px, py = xy_l2(pt_w)
        out.append(
            f'      <g class="wf-pin" data-pin="{num}" tabindex="0" role="button" aria-label="{num}. {title}">'
        )
        out.append(
            f'        <circle cx="{px:.1f}" cy="{py:.1f}" r="7.2" class="wf-pin-bg"/>'
        )
        out.append(
            f'        <text x="{px:.1f}" y="{py + 2.8:.1f}" text-anchor="middle" class="wf-pin-txt">{num}</text>'
        )
        out.append("      </g>")
    out.append("    </g>")
    out.append("  </g>")

    # Right Panel: Level 1 Base Deck
    env_l1 = get_level1_envelope_ft()
    out.append('  <g class="panel-l1">')
    out.append(
        '    <text x="482" y="24" class="wf-subplan-kicker">LEVEL 1 BASE DECK (-28\'-6")</text>'
    )
    out.append(
        '    <text x="482" y="40" class="wf-subplan-sub">Pentagonal Retaining Wall &amp; Archival Collections</text>'
    )
    out.append(
        f'    <polygon points="{pts_fn(env_l1, xy_l1)}" class="zone-staff layer-zones"/>'
    )

    out.append('    <g class="layer-reg">')
    for deg in (G.RAY_B_DEG, G.RAY_C_DEG, G.RAY_D_DEG):
        pa, pb = xy_l1(G.WP3), xy_l1(polar_pt(G.WP3, 94.0, deg))
        out.append(
            f'      <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-reg-ray"/>'
        )
    out.append("    </g>")

    for stk in get_radial_bookstacks_ft(38.0, 71.0):
        out.append(
            f'    <polygon points="{pts_fn(stk, xy_l1)}" class="wf-bookcase"/>'
        )
    out.append(
        f'    <polyline points="{pts_fn(get_l1_inner_pentagon_ft(), xy_l1)}" class="wf-wall-int-bold"/>'
    )
    out.append(f'    <polygon points="{pts_fn(env_l1, xy_l1)}" class="wf-wall-ext"/>')
    for hp_poly in get_h_pier_polygons_ft(level=1):
        out.append(
            f'    <polygon points="{pts_fn(hp_poly, xy_l1)}" class="wf-poche-solid"/>'
        )
    for cpt in G.PAIRED_COLS_FT.values():
        cx_p, cy_p = xy_l1(cpt)
        out.append(
            f'    <circle cx="{cx_p:.1f}" cy="{cy_p:.1f}" r="1.9" class="wf-col-dot"/>'
        )

    out.append('    <g class="layer-pins">')
    px12, py12 = xy_l1((-4.0, 54.0))
    out.append(
        '      <g class="wf-pin" data-pin="12" tabindex="0" role="button" aria-label="12. Lower Archival Stacks (-28 ft 6 in)">'
    )
    out.append(
        f'        <circle cx="{px12:.1f}" cy="{py12:.1f}" r="7.2" class="wf-pin-bg"/>'
    )
    out.append(
        f'        <text x="{px12:.1f}" y="{py12 + 2.8:.1f}" text-anchor="middle" class="wf-pin-txt">12</text>'
    )
    out.append("      </g>")
    out.append("    </g>")
    out.append("  </g>")

    out.append("</svg>")
    return "\n".join(out)


def build_skylight_cross_section_svg(compact: bool = False) -> str:
    """Constructive Longitudinal Cross-Section (Section A-A) through Skylights & Bluff."""
    w_vb, h_vb = (820, 365) if compact else (1080, 480)
    sc = (w_vb - 96.0) / 182.0
    ox = 48.0 + 74.0 * sc
    oy = 36.0 + 29.0 * sc

    def sz(s_ft: float, z_ft: float) -> tuple[float, float]:
        return (ox + s_ft * sc, oy - z_ft * sc)

    def pts_s(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{sz(s, z)[0]:.1f},{sz(s, z)[1]:.1f}" for s, z in pts)

    z_lob = G.Z_LOBBY_FT              # +1.333 ft (+1'-4")
    z_mezz = G.Z_REF_GALLERY_FT       # -5.333 ft (-5'-4")
    z_l2 = G.Z_L2_FT                  # -14.0 ft (-14'-0")
    z_l1 = G.Z_L1_FT                  # -28.5 ft (-28'-6")
    z_sc = G.Z_SOUTH_CEIL_FT          # +10.458 ft (+10'-5 1/2")
    z_sr = G.Z_SOUTH_ROOF_FT          # +13.667 ft (+13'-8")
    z_sp = G.Z_SOUTH_PARAPET_FT       # +15.0 ft (+15'-0")
    z_fc = G.Z_FAN_CEIL_FT            # +11.333 ft (+11'-4")
    z_fr = G.Z_FAN_ROOF_HIGH_FT       # +16.167 ft (+16'-2")
    z_fp = G.Z_FAN_PARAPET_N_FT       # +17.95 ft (+17'-11 3/8")
    z_ap = G.Z_AUDITORIUM_PARAPET_FT  # +19.28 ft (+19'-3 3/8")
    z_sk = G.Z_SCOOP_RIDGE_FT         # +21.333 ft (+21'-4")

    out: list[str] = [
        f'<svg viewBox="0 0 {w_vb} {h_vb}" class="wf-svg wf-section-aa" role="img" aria-label="Longitudinal Architectural Cross-Section Through Skylights and Hillside">',
    ]

    # 1. Earth Hillside Bluff Poché
    earth_poly = [
        (-74.0, 1.15),
        (-51.7, 1.15),
        (-51.7, 0.35),
        (-21.5, 0.35),
        (-21.5, z_l2 - 1.1),
        (33.0, z_l2 - 1.1),
        (33.0, z_l1 - 1.2),
        (87.0, z_l1 - 1.2),
        (87.6, z_l1 - 1.6),
        (106.0, z_l1 - 8.2),
        (106.0, z_l1 - 10.2),
        (-74.0, z_l1 - 10.2),
    ]
    out.append(f'  <polygon points="{pts_s(earth_poly)}" class="wf-earth"/>')
    out.append(
        f'  <polygon points="{pts_s(earth_poly)}" fill="url(#wfEarthHatch)" class="wf-earth-hatch"/>'
    )
    out.append(
        f'  <polyline points="{pts_s([(-74.0, 1.15), (-51.7, 1.15)])}" class="wf-grade-line"/>'
    )
    out.append(
        f'  <polyline points="{pts_s([(87.0, z_l1 - 1.4), (106.0, z_l1 - 8.2)])}" class="wf-grade-line"/>'
    )

    aud_ghost = [(-51.7, z_sp), (-51.7, z_ap), (-21.5, z_ap), (-21.5, z_sp)]
    out.append(f'  <polygon points="{pts_s(aud_ghost)}" class="wf-aud-ghost"/>')
    if not compact:
        pa_lbl = sz(-36.6, z_ap - 1.8)
        out.append(
            f'  <text x="{pa_lbl[0]:.1f}" y="{pa_lbl[1]:.1f}" text-anchor="middle" class="wf-ghost-lbl">AUDITORIUM PARAPET (+19\'-3" BEYOND)</text>'
        )

    # 2. Interior Daylight & Solar Ray-Tracing Cones (toggleable via .layer-solar)
    out.append('  <g class="layer-solar">')
    scoop_wash = [
        (35.0, z_sk),
        (41.2, 15.1),
        (44.0, z_fc),
        (46.0, 0.0),
        (32.0, z_mezz),
        (31.8, z_l2),
        (22.0, z_l2),
        (22.0, 0.0),
        (28.0, 13.0),
        (31.5, 18.8),
    ]
    out.append(f'    <polygon points="{pts_s(scoop_wash)}" fill="url(#wfSkyGlow)"/>')
    for sc_x, z_flr, half_w in ((-26.0, z_lob, 9.2), (8.8, 0.0, 10.2)):
        cone = [
            (sc_x - 2.1, z_sr + 2.4),
            (sc_x + 2.1, z_sr + 2.4),
            (sc_x + half_w, z_flr),
            (sc_x - half_w, z_flr),
        ]
        out.append(f'    <polygon points="{pts_s(cone)}" fill="url(#wfSunGlow)"/>')

    ray_paths = [
        (
            [(44.5, 25.5), (37.8, 18.2), (31.0, 16.6), (36.5, -2.5)],
            "wf-ray-sky",
            "wfArrowSky",
        ),
        (
            [(42.0, 26.2), (36.4, 19.6), (29.5, 14.3), (26.5, -4.5)],
            "wf-ray-sky",
            "wfArrowSky",
        ),
        (
            [(95.0, 15.8), (86.0, 11.8), (75.5, 13.2), (61.5, 2.5)],
            "wf-ray-sky",
            "wfArrowSky",
        ),
        (
            [(13.4, 26.8), (9.1, 16.0), (7.2, 12.2), (9.4, 3.6)],
            "wf-ray-sun",
            "wfArrowSun",
        ),
        (
            [(-21.4, 26.8), (-25.7, 16.0), (-27.4, 12.2), (-25.0, 2.0)],
            "wf-ray-sun",
            "wfArrowSun",
        ),
    ]
    for r_pts, cls, mk in ray_paths:
        out.append(
            f'    <polyline points="{pts_s(r_pts)}" class="{cls}" marker-end="url(#{mk})"/>'
        )
    out.append("  </g>")

    # 3. Elevation Datum Lines (.layer-reg)
    out.append('  <g class="layer-reg">')
    for lbl, zf, s_start in [
        ("+21'-4\" SCOOP RIDGE", z_sk, 34.0),
        ("+16'-2\" FAN ROOF", z_fr, 41.0),
        ("+1'-4\" LOBBY", z_lob, -52.0),
        ("0'-0\" READING LEVEL", 0.0, -17.0),
        ("-5'-4\" MEZZANINE", z_mezz, 22.0),
        ("-14'-0\" LEVEL 2", z_l2, -21.5),
        ("-28'-6\" LEVEL 1", z_l1, 33.0),
    ]:
        pa, pb = sz(s_start, zf), sz(105.0, zf)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-datum-line"/>'
        )
        out.append(
            f'    <text x="{pb[0] - 2:.1f}" y="{pb[1] - 3:.1f}" text-anchor="end" class="wf-datum-lbl">{lbl}</text>'
        )
    out.append("  </g>")

    # 4. Architectural Interior Elements in Elevation
    out.append('  <g class="layer-interior-elev">')
    for vx in (-58.5, -51.7):
        pa, pb = sz(vx, z_lob), sz(vx, 9.8)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-glass-elev"/>'
        )
    for bx in range(-45, -31, 2):
        pa, pb = sz(bx, z_lob), sz(bx, z_sc)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-batten-line"/>'
        )

    for s0, s1 in ((0.0, 5.5), (12.1, 18.2)):
        pa, pb = sz(s0, 9.75), sz(s1, 9.75)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-slat-ceiling"/>'
        )

    out.append(
        f'    <polygon points="{pts_s([(8.2, 0.0), (12.6, 0.0), (12.6, 3.5), (8.2, 3.5)])}" class="wf-bookcase"/>'
    )
    for rz in (1.1, 2.1, 3.1):
        pa, pb = sz(19.0, rz), sz(22.0, rz)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-rail-line"/>'
        )
    out.append(
        f'    <polygon points="{pts_s([(31.2, z_l2), (32.5, z_l2), (32.5, 12.67), (31.2, 12.67)])}" class="wf-col-elev"/>'
    )
    out.append(
        f'    <polygon points="{pts_s([(57.2, z_l1), (58.5, z_l1), (58.5, z_fc), (57.2, z_fc)])}" class="wf-col-elev"/>'
    )

    # 3-shelf curved Mezzanine bookcase tucked flush under Level 3 4" soffit lip
    out.append(
        f'    <polygon points="{pts_s([(22.0, z_mezz), (23.3, z_mezz), (23.3, -1.25), (22.0, -1.25)])}" class="wf-bookcase"/>'
    )
    for m_tier in (1, 2):
        zt = z_mezz + m_tier * ((-1.25 - z_mezz) / 3.0)
        pa, pb = sz(22.0, zt), sz(23.3, zt)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-shelf-line"/>'
        )

    # 6-shelf full-height radial stacks across Level 3, Level 2, and Level 1
    for s0, s1, z_flr, h_ft in [
        (51.2, 70.4, 0.0, 6.85),
        (35.2, 47.0, z_l2, 6.85),
        (52.0, 68.2, z_l2, 6.85),
        (39.0, 54.5, z_l1, 6.85),
        (59.5, 72.0, z_l1, 6.85),
    ]:
        out.append(
            f'    <polygon points="{pts_s([(s0, z_flr), (s1, z_flr), (s1, z_flr + h_ft), (s0, z_flr + h_ft)])}" class="wf-bookcase"/>'
        )
        for tier in range(1, 6):
            zt = z_flr + tier * (h_ft / 6.0)
            pa, pb = sz(s0, zt), sz(s1, zt)
            out.append(
                f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-shelf-line"/>'
            )

    for s_par, z_flr in ((31.8, z_mezz), (44.0, 0.0)):
        dir_s = -1.0 if z_flr < 0 else 1.0
        out.append(
            f'    <polygon points="{pts_s([(s_par - 0.35, z_flr), (s_par + 0.35, z_flr), (s_par + 0.35, z_flr + 2.8), (s_par - 0.35, z_flr + 2.8)])}" class="wf-poche-cut"/>'
        )
        d0, d1 = (s_par, s_par + dir_s * 2.5)
        out.append(
            f'    <polygon points="{pts_s([(d0, z_flr + 2.35), (d1, z_flr + 2.35), (d1, z_flr + 2.55), (d0, z_flr + 2.55)])}" class="wf-workbench"/>'
        )
        lp0 = sz(s_par - dir_s * 0.25, z_flr + 2.5)
        lp1 = sz(s_par + dir_s * 1.15, z_flr + 4.35)
        out.append(
            f'    <line x1="{lp0[0]:.1f}" y1="{lp0[1]:.1f}" x2="{lp1[0]:.1f}" y2="{lp1[1]:.1f}" class="wf-lamp-stem"/>'
        )
        out.append(
            f'    <ellipse cx="{lp1[0]:.1f}" cy="{lp1[1]:.1f}" rx="{1.1 * sc:.1f}" ry="{0.42 * sc:.1f}" class="wf-lamp-dome"/>'
        )

    out.append(
        f'    <polygon points="{pts_s([(82.0, 2.35), (85.8, 2.35), (85.8, 2.60), (82.0, 2.60)])}" class="wf-workbench"/>'
    )
    for gz0, gz1 in ((7.2, 15.0), (z_l2 + 3.4, -1.6), (z_l1 + 6.7, z_l2 - 2.2)):
        pa, pb = sz(86.4, gz0), sz(86.4, gz1)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-glass-elev"/>'
        )
    for lz in [7.6 + k * 1.05 for k in range(8)] + [z_l2 + 3.8 + k * 1.05 for k in range(9)]:
        pa, pb = sz(87.3, lz), sz(88.6, lz - 0.35)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-louver-tick"/>'
        )

    out.append(
        f'    <line x1="{sz(34.8, z_sk)[0]:.1f}" y1="{sz(34.8, z_sk)[1]:.1f}" x2="{sz(41.2, 15.1)[0]:.1f}" y2="{sz(41.2, 15.1)[1]:.1f}" class="wf-skylight-glass"/>'
    )
    for sc_x in (-26.0, 8.8):
        lantern = [
            (sc_x - 2.3, z_sr),
            (sc_x - 1.3, z_sr + 3.0),
            (sc_x + 1.3, z_sr + 3.0),
            (sc_x + 2.3, z_sr),
        ]
        out.append(f'    <polygon points="{pts_s(lantern)}" class="wf-lantern-cap"/>')
        out.append(
            f'    <polyline points="{pts_s([(sc_x - 3.1, z_sc), (sc_x - 2.1, z_sr)])}" class="wf-throat-line"/>'
        )
        out.append(
            f'    <polyline points="{pts_s([(sc_x + 3.1, z_sc), (sc_x + 2.1, z_sr)])}" class="wf-throat-line"/>'
        )

    truss_pts = [
        (44.0, z_fc + 0.2),
        (48.5, 15.2),
        (53.0, z_fc + 0.2),
        (57.5, 15.4),
        (62.0, z_fc + 0.2),
        (66.5, 15.7),
        (72.0, 12.8),
        (77.5, 16.0),
    ]
    out.append(f'    <polyline points="{pts_s(truss_pts)}" class="wf-truss-web"/>')
    out.append("  </g>")

    # 5. Cut Structural Concrete & Roof Section Poché Solids
    out.append('  <g class="layer-poche">')
    poche_polys = [
        [(-67.0, 9.6), (-51.0, 9.6), (-51.0, 10.2), (-67.0, 10.2)],
        [(-65.4, 1.15), (-64.7, 1.15), (-64.7, 9.6), (-65.4, 9.6)],
        [
            (-52.4, z_sc),
            (-29.1, z_sc),
            (-28.1, z_sr),
            (-51.1, z_sr),
            (-51.1, z_sp),
            (-52.4, z_sp),
        ],
        [(-22.9, z_sc), (5.7, z_sc), (6.7, z_sr), (-23.9, z_sr)],
        [
            (11.9, z_sc),
            (25.2, z_sc),
            (27.5, 13.0),
            (30.2, 16.6),
            (32.4, 19.4),
            (34.8, z_sk),
            (33.9, z_sk + 0.6),
            (30.6, 19.6),
            (27.4, 16.0),
            (24.6, z_sr),
            (10.9, z_sr),
        ],
        [
            (41.2, 15.1),
            (85.8, z_fr),
            (85.8, z_fp),
            (87.0, z_fp),
            (87.0, 15.0),
            (85.6, 15.0),
            (67.0, z_fc),
            (44.0, z_fc),
        ],
        [(85.8, 0.0), (87.0, 0.0), (87.0, 7.2), (85.8, 7.2)],
        [(85.8, -1.6), (87.0, -1.6), (87.0, 0.0), (85.8, 0.0)],
        [(85.8, z_l2 - 1.1), (87.0, z_l2 - 1.1), (87.0, z_l2 + 3.4), (85.8, z_l2 + 3.4)],
        [(85.8, z_l1 - 1.4), (87.0, z_l1 - 1.4), (87.0, z_l1 + 6.7), (85.8, z_l1 + 6.7)],
        [
            (-52.4, 0.35),
            (-20.0, 0.35),
            (-16.5, -1.0),
            (21.2, -1.0),
            (21.2, z_mezz - 1.0),
            (32.0, z_mezz - 1.0),
            (32.0, z_mezz),
            (22.0, z_mezz),
            (22.0, 0.0),
            (-16.5, 0.0),
            (-20.0, z_lob),
            (-52.4, z_lob),
        ],
        [(43.8, -1.0), (87.0, -1.0), (87.0, 0.0), (43.8, 0.0)],
        [
            (-22.3, z_l2 - 1.1),
            (87.0, z_l2 - 1.1),
            (87.0, z_l2),
            (-21.3, z_l2),
            (-21.3, 0.35),
            (-22.3, 0.35),
        ],
        [
            (32.2, z_l1 - 1.2),
            (87.0, z_l1 - 1.2),
            (87.0, z_l1),
            (33.2, z_l1),
            (33.2, z_l2 - 1.1),
            (32.2, z_l2 - 1.1),
        ],
    ]
    for poly in poche_polys:
        out.append(f'    <polygon points="{pts_s(poly)}" class="wf-poche-cut"/>')
    out.append("  </g>")

    # 6. Human Scale Silhouettes
    out.append('  <g class="layer-figures">')
    for fx, fz in ((-47.5, z_lob), (4.8, 0.0), (47.5, 0.0), (28.0, z_mezz), (49.5, z_l2)):
        head = sz(fx, fz + 5.25)
        body_pts = [
            (fx - 0.55, fz),
            (fx - 0.7, fz + 3.1),
            (fx - 0.95, fz + 4.4),
            (fx + 0.95, fz + 4.4),
            (fx + 0.7, fz + 3.1),
            (fx + 0.55, fz),
        ]
        out.append(
            f'    <circle cx="{head[0]:.1f}" cy="{head[1]:.1f}" r="{0.52 * sc:.1f}" class="wf-figure"/>'
        )
        out.append(f'    <polygon points="{pts_s(body_pts)}" class="wf-figure"/>')
    out.append("  </g>")

    # 7. Callout Leaders
    callouts = [
        ((-60.0, 10.2), (-59.0, 18.2), "SOUTH PORTICO"),
        ((-26.0, z_sr + 3.0), (-22.0, 23.8), "CONICAL SKYLIGHTS (14)"),
        ((34.8, z_sk + 0.3), (20.5, 27.2), "NORTH DAYLIGHT SCOOP (+21'-4\")"),
        ((57.5, 14.2), (55.0, 23.4), "3'-11\" TRUSS ROOF PLENUM"),
        ((87.0, 11.5), (81.0, 27.2), "+7'-2\" CLERESTORY &amp; LOUVERS"),
    ]
    out.append('  <g class="layer-callouts">')
    for p_src, p_txt, label in callouts:
        ps, pt = sz(*p_src), sz(*p_txt)
        out.append(
            f'    <line x1="{ps[0]:.1f}" y1="{ps[1]:.1f}" x2="{pt[0]:.1f}" y2="{pt[1] + 3:.1f}" class="wf-leader"/>'
        )
        out.append(
            f'    <circle cx="{ps[0]:.1f}" cy="{ps[1]:.1f}" r="2.0" class="wf-leader-dot"/>'
        )
        out.append(
            f'    <text x="{pt[0]:.1f}" y="{pt[1]:.1f}" text-anchor="middle" class="wf-callout-lbl">{label}</text>'
        )

    room_tags = [
        (-36.5, 5.2, "ENTRANCE LOBBY"),
        (9.5, 5.6, "CONTROL DESK"),
        (33.5, 4.0, "READING WELL"),
        (61.5, 8.5, "MAIN FAN STACKS"),
        (27.5, -9.8, "MEZZANINE"),
        (60.5, -9.8, "LEVEL 2 STACKS"),
        (55.5, -23.5, "LEVEL 1 ARCHIVAL DECK"),
    ]
    if not compact:
        for rs, rz, rlbl in room_tags:
            rp = sz(rs, rz)
            out.append(
                f'    <text x="{rp[0]:.1f}" y="{rp[1]:.1f}" text-anchor="middle" class="wf-room-tag">{rlbl}</text>'
            )
    out.append("  </g>")

    out.append("</svg>")
    return "\n".join(out)


def build_campus_locator_svg() -> str:
    """Mount Angel Abbey Hilltop Campus Orientation Map (with South-Side Bell Tower)."""
    w_vb, h_vb = 520, 310
    sc = 0.72
    ox = 212.0
    oy = 104.0

    def xy(pt: tuple[float, float]) -> tuple[float, float]:
        return (ox + pt[0] * sc, oy - pt[1] * sc)

    def pts_s(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{xy(p)[0]:.1f},{xy(p)[1]:.1f}" for p in pts)

    bt_c = xy((269, -162))
    bt_lbl = xy((269, -196))

    out: list[str] = [
        f'<svg viewBox="0 0 {w_vb} {h_vb}" class="wf-svg wf-campus-map" role="img" aria-label="Mount Angel Abbey Hilltop Campus Locator Map">',
        f'  <polygon points="{pts_s([(-260, -255), (385, -255), (385, 25), (175, 86), (45, 108), (-110, 102), (-210, 58), (-260, -20)])}" class="wf-quad-lawn"/>',
        f'  <polyline points="{pts_s([(-265, -20), (-210, 65), (-110, 108), (45, 115), (175, 92), (385, 35)])}" class="wf-bluff-contour"/>',
        f'  <polyline points="{pts_s([(-265, -45), (-220, 48), (-120, 96), (35, 104), (185, 76), (310, 22)])}" class="wf-abbey-drive"/>',
        f'  <polygon points="{pts_s([(-145, -127), (238, -127), (238, -117), (-145, -117)])}" class="wf-plaza"/>',
        f'  <polygon points="{pts_s([(-18, -122), (2, -122), (2, -55), (-18, -55)])}" class="wf-plaza"/>',
        f'  <polygon points="{pts_s([(238, -122)] + arc_pts((238, -122), 46.0, 90.0, 270.0, 18))}" class="wf-plaza"/>',
        f'  <polygon points="{pts_s([(-250, -165), (-140, -165), (-140, -115), (-195, -115), (-195, -10), (-250, -10)])}" class="wf-ctx-bldg"/>',
        f'  <polygon points="{pts_s([(-195, 35), (-118, 35), (-118, 82), (-195, 82)])}" class="wf-ctx-bldg"/>',
        f'  <polygon points="{pts_s([(-125, -245), (-35, -245), (-35, -168), (-125, -168)])}" class="wf-ctx-bldg"/>',
        f'  <polygon points="{pts_s([(45, -238), (118, -238), (118, -165), (45, -165)])}" class="wf-ctx-bldg"/>',
        f'  <polygon points="{pts_s([(132, -238), (205, -238), (205, -165), (132, -165)])}" class="wf-ctx-bldg"/>',
        f'  <polygon points="{pts_s([(125, -52), (205, -52), (205, -12), (125, -12)])}" class="wf-ctx-bldg"/>',
        f'  <polygon points="{pts_s([(316, 10), (380, 10), (380, -254), (316, -254), (316, -220), (342, -220), (342, -24), (316, -24)])}" class="wf-ctx-bldg"/>',
        f'  <polygon points="{pts_s([(238, -184), (254, -184), (254, -60), (238, -60)])}" class="wf-ctx-bldg"/>',
        f'  <polygon points="{pts_s([(254, -154), (355, -154), (355, -90), (254, -90)])}" class="wf-ctx-bldg-bold"/>',
        # Landmark 126-ft Bell Tower on the SOUTH side of the Abbey Church
        f'  <polygon points="{pts_s([(260, -162), (278, -162), (278, -144), (260, -144)])}" class="wf-bell-tower"/>',
        f'  <line x1="{bt_c[0]:.1f}" y1="{bt_c[1]:.1f}" x2="{bt_lbl[0]:.1f}" y2="{bt_lbl[1] - 9:.1f}" class="wf-leader"/>',
        f'  <polygon points="{pts_s(get_level3_envelope_ft())}" class="wf-library-hero"/>',
        f'  <line x1="{xy((48, 55))[0]:.1f}" y1="{xy((48, 55))[1]:.1f}" x2="{xy((142, 98))[0]:.1f}" y2="{xy((142, 98))[1]:.1f}" class="wf-vista-arrow" marker-end="url(#wfArrowVista)"/>',
        f'  <text x="{xy((-18, 28))[0]:.1f}" y="{xy((-18, 28))[1]:.1f}" text-anchor="middle" class="wf-map-hero-lbl">AALTO LIBRARY</text>',
        f'  <text x="{xy((-215, -85))[0]:.1f}" y="{xy((-215, -85))[1]:.1f}" text-anchor="middle" class="wf-map-lbl">AQUINAS HALL</text>',
        f'  <text x="{xy((85, -122))[0]:.1f}" y="{xy((85, -122))[1] - 6:.1f}" text-anchor="middle" class="wf-map-lbl">ABBEY QUAD</text>',
        f'  <text x="{xy((305, -118))[0]:.1f}" y="{xy((305, -118))[1]:.1f}" text-anchor="middle" class="wf-map-lbl">ABBEY CHURCH</text>',
        f'  <text x="{bt_lbl[0]:.1f}" y="{bt_lbl[1]:.1f}" text-anchor="middle" class="wf-map-accent-lbl">BELL TOWER (SOUTH)</text>',
        f'  <text x="{xy((361, -122))[0]:.1f}" y="{xy((361, -122))[1]:.1f}" text-anchor="middle" transform="rotate(90 {xy((361, -122))[0]:.1f} {xy((361, -122))[1]:.1f})" class="wf-map-lbl">MONASTERY</text>',
        f'  <text x="{xy((-35, 108))[0]:.1f}" y="{xy((-35, 108))[1] - 5:.1f}" text-anchor="middle" class="wf-map-lbl">ABBEY DRIVE &amp; NORTH BLUFF</text>',
        f'  <text x="{xy((148, 102))[0]:.1f}" y="{xy((148, 102))[1]:.1f}" class="wf-vista-lbl">MT. HOOD ↗</text>',
        "</svg>",
    ]
    return "\n".join(out)


def build_detail_medallions_svg() -> dict[str, str]:
    """Return 3 enlarged constructive detail SVGs: Conical Skylight, Mushroom Lamp, H-Column D."""
    d_cone = """<svg viewBox="0 0 260 190" class="wf-svg wf-detail-svg" role="img" aria-label="Detail A: Perforated Conical Skylight Diffuser">
  <polygon points="82,42 104,16 156,16 178,42" class="wf-lantern-cap"/>
  <polygon points="74,42 186,42 198,128 62,128" fill="url(#wfSunGlow)" class="layer-solar"/>
  <polyline points="118,6 130,36 104,88 126,150" class="wf-ray-sun layer-solar" marker-end="url(#wfArrowSun)"/>
  <polyline points="148,6 136,36 156,88 134,150" class="wf-ray-sun layer-solar" marker-end="url(#wfArrowSun)"/>
  <polygon points="18,42 78,42 62,118 18,118" class="wf-poche-cut"/>
  <polygon points="182,42 242,42 242,118 198,118" class="wf-poche-cut"/>
  <line x1="78" y1="42" x2="62" y2="118" class="wf-throat-line"/>
  <line x1="182" y1="42" x2="198" y2="118" class="wf-throat-line"/>
  <line x1="88" y1="50" x2="76" y2="108" class="wf-datum-line"/>
  <line x1="172" y1="50" x2="184" y2="108" class="wf-datum-line"/>
  <line x1="14" y1="128" x2="58" y2="128" class="wf-slat-ceiling"/>
  <line x1="202" y1="128" x2="246" y2="128" class="wf-slat-ceiling"/>
  <rect x="56" y="122" width="8" height="10" class="wf-poche-cut"/>
  <rect x="196" y="122" width="8" height="10" class="wf-poche-cut"/>
  <text x="130" y="166" text-anchor="middle" class="wf-callout-lbl">DOUBLE-CONE DIFFUSER + OCULUS</text>
  <text x="130" y="180" text-anchor="middle" class="wf-datum-lbl">1&quot;×1&quot; RADIAL HEMLOCK CEILING SLATS</text>
</svg>"""

    d_lamp = """<svg viewBox="0 0 260 190" class="wf-svg wf-detail-svg" role="img" aria-label="Detail B: Parapet Mushroom Reading Lamp and Workbench">
  <polygon points="78,74 102,74 102,162 78,162" class="wf-poche-cut"/>
  <polygon points="75,64 105,64 105,74 75,74" class="wf-bookcase"/>
  <polygon points="102,94 184,94 184,103 102,103" class="wf-workbench"/>
  <polyline points="102,126 146,103" class="wf-wall-int-bold"/>
  <line x1="72" y1="86" x2="132" y2="38" class="wf-lamp-stem"/>
  <line x1="72" y1="82" x2="78" y2="82" class="wf-lamp-stem"/>
  <ellipse cx="136" cy="36" rx="34" ry="11" class="wf-lamp-dome"/>
  <polygon points="106,44 166,44 186,94 98,94" fill="url(#wfSunGlow)" class="layer-solar"/>
  <rect x="164" y="122" width="38" height="6" class="wf-workbench"/>
  <line x1="170" y1="128" x2="166" y2="162" class="wf-batten-line"/>
  <line x1="196" y1="128" x2="200" y2="162" class="wf-batten-line"/>
  <line x1="78" y1="162" x2="236" y2="162" class="wf-wall-int-bold"/>
  <text x="44" y="118" text-anchor="middle" class="wf-datum-lbl">WELL</text>
  <text x="44" y="130" text-anchor="middle" class="wf-datum-lbl">VOID</text>
  <text x="148" y="180" text-anchor="middle" class="wf-callout-lbl">ANGLED LAMP + LINOLEUM COUNTER</text>
</svg>"""

    hp_d = get_h_pier_polygons_ft(level=3)[2]
    cx_h = sum(p[0] for p in hp_d) / len(hp_d)
    cy_h = sum(p[1] for p in hp_d) / len(hp_d)
    sc_h = 11.0

    def hxy(p: tuple[float, float]) -> str:
        return f"{130.0 + (p[0] - cx_h) * sc_h:.1f},{94.0 - (p[1] - cy_h) * sc_h:.1f}"

    hp_pts = " ".join(hxy(p) for p in hp_d)
    w0 = (
        hp_d[2][0] + 0.22 * (hp_d[3][0] - hp_d[2][0]),
        hp_d[2][1] + 0.22 * (hp_d[3][1] - hp_d[2][1]),
    )
    w1 = (
        hp_d[2][0] + 0.78 * (hp_d[3][0] - hp_d[2][0]),
        hp_d[2][1] + 0.78 * (hp_d[3][1] - hp_d[2][1]),
    )
    desk_h = " ".join(
        hxy(p)
        for p in [
            hp_d[9],
            hp_d[8],
            (
                0.45 * hp_d[8][0] + 0.55 * hp_d[7][0],
                0.45 * hp_d[8][1] + 0.55 * hp_d[7][1],
            ),
            (
                0.45 * hp_d[9][0] + 0.55 * hp_d[10][0],
                0.45 * hp_d[9][1] + 0.55 * hp_d[10][1],
            ),
        ]
    )
    d_hpier = f"""<svg viewBox="0 0 260 190" class="wf-svg wf-detail-svg" role="img" aria-label="Detail C: Irregular H-Column D and Mt. Hood Window">
  <polygon points="{desk_h}" class="wf-bookcase"/>
  <polygon points="{hp_pts}" class="wf-poche-solid"/>
  <line x1="{hxy(w0).split(',')[0]}" y1="{hxy(w0).split(',')[1]}" x2="{hxy(w1).split(',')[0]}" y2="{hxy(w1).split(',')[1]}" class="wf-skylight-glass"/>
  <line x1="118" y1="106" x2="174" y2="24" class="wf-vista-arrow" marker-end="url(#wfArrowVista)"/>
  <text x="180" y="21" class="wf-vista-lbl">{G.RAY_D_DEG:.1f}° MT. HOOD ↗</text>
  <text x="130" y="180" text-anchor="middle" class="wf-callout-lbl">IRREGULAR H-COLUMN D ALCOVE</text>
</svg>"""

    return {"cone": d_cone, "lamp": d_lamp, "hpier": d_hpier}


def build_polycentric_diagram_svg() -> str:
    """Analytical Constructive Diagram of Aalto's 4 Working Points, Radial Fan, and 4-Origin Inset."""
    w_vb, h_vb = 920, 446
    sc = 2.95
    ox, oy = 328.0, 358.0

    def xy(pt: tuple[float, float]) -> tuple[float, float]:
        return (ox + pt[0] * sc, oy - pt[1] * sc)

    def pts_s(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{xy(p)[0]:.1f},{xy(p)[1]:.1f}" for p in pts)

    out: list[str] = [
        f'<svg viewBox="0 0 {w_vb} {h_vb}" class="wf-svg wf-polycentric-svg" role="img" aria-label="Alvar Aalto Polycentric 4-Origin Regulating Diagram">',
        '  <line x1="628" y1="18" x2="628" y2="428" class="wf-panel-divider"/>',
    ]

    # Left: Fan Regulating Arcs, 5 Primary Axes, Variable Stacks & Rotated H-Columns
    env = get_level3_envelope_ft()
    out.append(f'  <polygon points="{pts_s(env)}" class="zone-quiet"/>')
    for r_arc, lbl_arc in (
        (G.R_GALLERY_RAIL, "R = 22'-0\" GALLERY"),
        (G.R_WELL_L2_WALL, "R = 31'-10\" WELL CORE"),
        (G.R_MEZZ_OPENING, "R = 44'-0\" MEZZANINE"),
        (87.0, "R = 87'-0\" NORTH WALL"),
    ):
        apts = arc_pts(G.WP3A, r_arc, 40.0, 162.0, 44)
        out.append(f'  <polyline points="{pts_s(apts)}" class="wf-reg-arc"/>')
        lp = xy(polar_pt(G.WP3A, r_arc, 159.0))
        out.append(
            f'  <text x="{lp[0] - 4:.1f}" y="{lp[1] - 3:.1f}" text-anchor="end" class="wf-datum-lbl">{lbl_arc}</text>'
        )

    for deg, name, orig in (
        (G.RAY_A_DEG, f"AXIS A ({G.RAY_A_DEG:.1f}°)", G.WP2),
        (G.RAY_B_DEG, f"AXIS B ({G.RAY_B_DEG:.1f}°)", G.WP3),
        (G.RAY_C_DEG, f"AXIS C ({G.RAY_C_DEG:.1f}°)", G.WP3),
        (G.RAY_D_DEG, f"AXIS D ({G.RAY_D_DEG:.1f}° MT. HOOD)", G.WP3),
        (G.RAY_E_DEG, f"AXIS E ({G.RAY_E_DEG:.1f}°)", G.WP2),
    ):
        pa, pb = xy(orig), xy(polar_pt(orig, 95.0, deg))
        cls = "wf-vista-arrow" if "MT. HOOD" in name else "wf-reg-ray"
        out.append(
            f'  <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="{cls}"/>'
        )
        out.append(
            f'  <text x="{pb[0]:.1f}" y="{pb[1] - 5:.1f}" text-anchor="middle" class="wf-callout-lbl">{name}</text>'
        )

    # Variable-length radial bookcases highlighted in warm birch
    r_start = 51.2
    r_ends = [
        67.8,
        69.4,
        71.0,
        68.2,
        70.4,
        71.2,
        69.8,
        68.0,
        68.5,
        70.8,
        71.2,
        69.2,
        67.5,
        69.8,
        70.5,
    ]
    stack_angles = [
        159.0,
        153.2,
        147.8,
        132.5,
        126.6,
        120.8,
        115.0,
        109.2,
        93.4,
        86.4,
        79.4,
        72.4,
        56.5,
        50.5,
        44.5,
    ]
    for deg, r_end in zip(stack_angles, r_ends):
        rad = math.radians(deg)
        l_stk = r_end - r_start
        r_mid = 0.5 * (r_start + r_end)
        cx_s = G.WP3A[0] + r_mid * math.cos(rad)
        cy_s = G.WP3A[1] + r_mid * math.sin(rad)
        out.append(
            f'  <polygon points="{pts_s(_rect_pts(cx_s, cy_s, l_stk, 2.6, deg))}" class="wf-bookcase"/>'
        )

    for hp_poly in get_h_pier_polygons_ft(level=3):
        out.append(f'  <polygon points="{pts_s(hp_poly)}" class="wf-poche-solid"/>')
    out.append(f'  <polygon points="{pts_s(env)}" class="wf-wall-ext"/>')

    for wp_pt in (G.WP3, G.WP2, G.WP3A, G.WP_DESK):
        p = xy(wp_pt)
        out.append(
            f'  <circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3.4" class="wf-wp-dot"/>'
        )
    out.append(
        '  <text x="20" y="24" class="wf-subplan-kicker">POLYCENTRIC RADIAL FAN &amp; VARIABLE STACK MODULES</text>'
    )
    out.append(
        '  <text x="20" y="40" class="wf-subplan-sub">Every bookcase length (16.3\'–20.0\'), H-column rotation, and skylight arc springs from shifted origins</text>'
    )

    # Right Top: 8x Magnified 4-Origin Cluster Inset
    ix, iy, isc = 762.0, 142.0, 13.5
    out.append(
        '  <text x="648" y="24" class="wf-subplan-kicker">MAGNIFIED 4-ORIGIN CLUSTER (8×)</text>'
    )
    out.append(
        '  <text x="648" y="40" class="wf-subplan-sub">Archival W.P. offsets prevent rigid symmetry</text>'
    )
    out.append(
        f'  <line x1="652" y1="{iy:.1f}" x2="898" y2="{iy:.1f}" class="wf-datum-line"/>'
    )
    out.append(
        f'  <line x1="{ix:.1f}" y1="64" x2="{ix:.1f}" y2="226" class="wf-datum-line"/>'
    )
    origins = [
        (G.WP3, "WP #3 (0, 0)", "Rays B, C, D &amp; Grid 6", -8, 12),
        (G.WP2, "WP #2 (+2'-10\", -5'-3\")", "Flanks A &amp; E", -8, 12),
        (G.WP3A, "WP #3A (+1'-7\", +3'-5\")", "Well, Scoop &amp; Stacks", 8, -4),
        (G.WP_DESK, "WP_DESK (-1'-2\", +2'-2\")", "Desk &amp; Slatted Ceiling", -8, -8),
    ]
    for pt_o, lbl_o, sub_o, dx, dy in origins:
        px = ix + pt_o[0] * isc
        py = iy - pt_o[1] * isc
        anc = "end" if dx < 0 else "start"
        out.append(
            f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" class="wf-wp-dot"/>'
        )
        out.append(
            f'  <text x="{px + dx:.1f}" y="{py + dy:.1f}" text-anchor="{anc}" class="wf-callout-lbl">{lbl_o}</text>'
        )
        out.append(
            f'  <text x="{px + dx:.1f}" y="{py + dy + 11:.1f}" text-anchor="{anc}" class="wf-datum-lbl">{sub_o}</text>'
        )

    # Right Bottom: 3-Tier Roof Elevation Hierarchy Schematic
    out.append('  <line x1="648" y1="240" x2="904" y2="240" class="wf-panel-divider"/>')
    out.append(
        '  <text x="648" y="262" class="wf-subplan-kicker">THREE-TIER ROOF STEP HIERARCHY</text>'
    )
    out.append(
        '  <text x="648" y="278" class="wf-subplan-sub">Roof deck heights above Level 3 (0\'-0")</text>'
    )
    y_base = 410.0
    z_sc = 4.8
    bars = [
        (654, 52, G.Z_SOUTH_ROOF_FT, "zone-public", "+13'-8\"", "SOUTH / LOBBY"),
        (714, 58, G.Z_FAN_ROOF_HIGH_FT, "zone-quiet", "+16'-2\"", "MAIN FAN"),
        (780, 56, G.Z_AUDITORIUM_ROOF_FT, "zone-auditorium", "+17'-10\"", "AUDITORIUM"),
        (844, 54, G.Z_SCOOP_RIDGE_FT, "zone-well", "+21'-4\"", "SCOOP RIDGE"),
    ]
    out.append(
        f'  <line x1="648" y1="{y_base:.1f}" x2="906" y2="{y_base:.1f}" class="wf-wall-int-bold"/>'
    )
    for bx, bw, z_ft, z_cls, z_txt, b_lbl in bars:
        bh = z_ft * z_sc
        by = y_base - bh
        out.append(
            f'  <rect x="{bx}" y="{by:.1f}" width="{bw}" height="{bh:.1f}" class="{z_cls}"/>'
        )
        out.append(
            f'  <rect x="{bx}" y="{by:.1f}" width="{bw}" height="{bh:.1f}" class="wf-wall-ext"/>'
        )
        out.append(
            f'  <text x="{bx + bw / 2:.1f}" y="{by - 5:.1f}" text-anchor="middle" class="wf-callout-lbl">{z_txt}</text>'
        )
        out.append(
            f'  <text x="{bx + bw / 2:.1f}" y="{y_base + 13:.1f}" text-anchor="middle" class="wf-datum-lbl">{b_lbl}</text>'
        )

    out.append("</svg>")
    return "\n".join(out)


def build_all_wayfinding_svgs() -> dict[str, str]:
    """Build and XML-validate all wayfinding & poster SVG diagrams."""
    svgs = {
        "shared_defs": build_shared_svg_defs(),
        "emblem": build_emblem_svg(),
        "l3_poster": build_level3_wayfinding_svg(compact=False),
        "l3_rack": build_level3_wayfinding_svg(compact=True),
        "lower": build_lower_levels_svg(),
        "sec_poster": build_skylight_cross_section_svg(compact=False),
        "sec_rack": build_skylight_cross_section_svg(compact=True),
        "campus": build_campus_locator_svg(),
        "polycentric": build_polycentric_diagram_svg(),
        **build_detail_medallions_svg(),
    }
    for svg_str in svgs.values():
        ET.fromstring(svg_str)
    return svgs
