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
    for deg in (G.RAY_A_DEG, G.RAY_B_DEG, G.RAY_C_DEG, G.RAY_D_DEG, G.RAY_E_DEG):
        pa, pb = xy(G.WP3), xy(polar_pt(G.WP3, 84.0, deg))
        rays.append(
            f'  <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-emblem-ray"/>'
        )
    wp = xy(G.WP4)
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
    sc = w_vb / 246.0
    ox = 138.0 * sc
    oy = 100.5 * sc

    def xy(pt: tuple[float, float]) -> tuple[float, float]:
        return (ox + pt[0] * sc, oy - pt[1] * sc)

    def pts_s(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{xy(p)[0]:.1f},{xy(p)[1]:.1f}" for p in pts)

    out: list[str] = [
        f'<svg viewBox="0 0 {w_vb} {h_vb}" class="wf-svg wf-plan-l3" role="img" aria-label="Level 3 Main Reading Room &amp; Entrance Wayfinding Plan">',
    ]

    # 1. Zone Tints (toggleable via .layer-zones)
    env_l3 = get_level3_envelope_ft()
    well_outer = arc_pts(G.WP3A, G.R_MEZZ_OPENING, 41.8, 161.5, 44)
    well_inner = list(reversed(arc_pts(G.WP3A, G.R_GALLERY_RAIL, 41.8, 161.5, 32)))
    well_ring = well_outer + well_inner

    aud_poly = [(16.8, -50.8), (19.5, -59.5), (61.5, -59.5), (61.5, -21.0), (18.2, -21.0)]
    lounge_poly = [(15.5, 3.6), (51.8, 32.8), (51.8, -8.8), (19.0, -8.8), (19.0, -4.8)]
    staff_west = [
        (-126.5, 1.5),
        (-77.5, 1.5),
        (-77.5, -21.0),
        (-43.0, -21.0),
        (-43.0, -50.8),
        (-91.5, -50.8),
        (-91.5, -28.0),
        (-126.5, -28.0),
    ]

    out.append('  <g class="layer-zones">')
    out.append(f'    <polygon points="{pts_s(env_l3)}" class="zone-quiet"/>')
    out.append(f'    <polygon points="{pts_s(staff_west)}" class="zone-staff"/>')
    out.append(
        f'    <polygon points="{pts_s([(18.2, -21.0), (61.5, -21.0), (61.5, -8.8), (18.2, -8.8)])}" class="zone-staff"/>'
    )
    out.append(f'    <polygon points="{pts_s(lounge_poly)}" class="zone-lounge"/>')
    out.append(f'    <polygon points="{pts_s(aud_poly)}" class="zone-auditorium"/>')
    out.append(
        f'    <polygon points="{pts_s([(-33.5, -50.8), (16.8, -50.8), (18.2, -21.0), (15.5, 3.6), (-18.5, 0.2), (-17.2, -21.0), (-33.5, -28.0)])}" class="zone-public"/>'
    )
    out.append(
        f'    <polygon points="{pts_s([(-18.0, -57.5), (0.0, -57.5), (0.0, -50.8), (-18.0, -50.8)])}" class="zone-public"/>'
    )
    out.append(f'    <polygon points="{pts_s(well_ring)}" class="zone-well"/>')
    out.append("  </g>")

    # 2. Entry Plaza & Pergola Trellises (South Portico)
    out.append('  <g class="layer-site-plaza">')
    out.append(
        f'    <polygon points="{pts_s([(-36.0, -68.0), (18.0, -68.0), (18.0, -50.8), (-36.0, -50.8)])}" class="wf-plaza"/>'
    )
    for x0, x1 in ((-35.0, -19.0), (1.0, 16.5)):
        out.append(
            f'    <polygon points="{pts_s([(x0, -64.5), (x1, -64.5), (x1, -50.8), (x0, -50.8)])}" class="wf-pergola"/>'
        )
        for gx in range(int(x0) + 4, int(x1), 4):
            p_a, p_b = xy((gx, -64.5)), xy((gx, -50.8))
            out.append(
                f'    <line x1="{p_a[0]:.1f}" y1="{p_a[1]:.1f}" x2="{p_b[0]:.1f}" y2="{p_b[1]:.1f}" class="wf-pergola-grid"/>'
            )
    out.append(
        f'    <polygon points="{pts_s([(-19.0, -66.0), (1.0, -66.0), (1.0, -50.8), (-19.0, -50.8)])}" class="wf-canopy-marquee"/>'
    )
    if not compact:
        ep = xy((-9.0, -62.5))
        out.append(
            f'    <text x="{ep[0]:.1f}" y="{ep[1]:.1f}" text-anchor="middle" class="wf-tech-lbl">SOUTH ENTRY PORTICO &amp; PERGOLAS ↑</text>'
        )
    out.append("  </g>")

    # 3. Regulating Compass Lines & Rays (toggleable via .layer-reg)
    out.append('  <g class="layer-reg">')
    for deg in (G.RAY_B_DEG, G.RAY_C_DEG, G.RAY_D_DEG):
        pa, pb = xy(G.WP3), xy(polar_pt(G.WP3, 96.0, deg))
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-reg-ray"/>'
        )
    for deg, r_m in ((G.RAY_A_DEG, 94.0), (G.RAY_E_DEG, 114.0)):
        pa, pb = xy(G.WP_LOWER), xy(polar_pt(G.WP_LOWER, r_m, deg))
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-reg-ray-alt"/>'
        )
    out.append(
        f'    <polyline points="{pts_s(arc_pts(G.WP3A, G.R_WELL_L2_WALL, 38.0, 164.0, 40))}" class="wf-reg-arc"/>'
    )
    wp_px = xy(G.WP4)
    out.append(
        f'    <circle cx="{wp_px[0]:.1f}" cy="{wp_px[1]:.1f}" r="3.2" class="wf-wp-dot"/>'
    )
    if not compact:
        out.append(
            f'    <text x="{wp_px[0] + 6:.1f}" y="{wp_px[1] + 9:.1f}" class="wf-tech-lbl">WP #4 (0,0)</text>'
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
    for sy in (-21.0, -20.05, -19.1, -18.15, -17.2):
        pa, pb = xy((-16.2, sy)), xy((15.8, sy))
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
            (cx0 + 22.8 * urx, cy0 + 22.8 * ury),
            (cx0 + 44.1 * urx, cy0 + 44.1 * ury),
            (cx0 + 44.1 * urx + 1.8 * tx, cy0 + 44.1 * ury + 1.8 * ty),
            (cx0 + 22.8 * urx + 1.8 * tx, cy0 + 22.8 * ury + 1.8 * ty),
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
        156.0,
        149.5,
        143.0,
        130.5,
        124.2,
        118.0,
        111.8,
        105.5,
        92.5,
        86.2,
        80.0,
        73.8,
        57.5,
        51.2,
        45.0,
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

    stage_c = (60.2, -58.2)
    stage_poly = [stage_c] + arc_pts(stage_c, 15.8, 90.0, 180.0, 18)
    out.append(f'    <polygon points="{pts_s(stage_poly)}" class="wf-stage"/>')
    out.append(
        f'    <polyline points="{pts_s(arc_pts(stage_c, 18.0, 90.0, 180.0, 18))}" class="wf-stair-tread"/>'
    )
    for r_seat in (22.5, 26.2, 29.9, 33.6, 37.3):
        out.append(
            f'    <polyline points="{pts_s(arc_pts(stage_c, r_seat, 98.0, 172.0, 16))}" class="wf-seat-arc"/>'
        )

    pa_scr, pb_scr = xy((-29.08, -44.8)), xy((-29.08, -31.8))
    out.append(
        f'    <line x1="{pa_scr[0]:.1f}" y1="{pa_scr[1]:.1f}" x2="{pb_scr[0]:.1f}" y2="{pb_scr[1]:.1f}" class="wf-wood-screen"/>'
    )

    for j in range(14):
        f_t = (j + 0.5) / 14.0
        fx = -17.2 + f_t * (-18.5 - (-17.2))
        fy = -17.5 + f_t * (0.2 - (-17.5))
        out.append(
            f'    <polygon points="{pts_s(_rect_pts(fx, fy, 1.3, 0.35, 94.2 + 28.0))}" class="wf-wood-fin"/>'
        )

    scoop_band = arc_pts(G.WP3A, G.R_SCOOP_RIDGE, 46.0, 155.0, 32) + list(
        reversed(arc_pts(G.WP3A, 39.6, 46.0, 155.0, 32))
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
        [(-53.0, -28.0), (-33.5, -28.0)],
        [(-53.0, -39.0), (-33.5, -39.0)],
        [(-53.0, -50.8), (-53.0, -28.0)],
        [(-33.5, -50.8), (-33.5, -45.5)],
        [(-33.5, -42.5), (-33.5, -35.5)],
        [(-33.5, -32.5), (-33.5, -28.0)],
    ):
        out.append(f'    <polyline points="{pts_s(seg)}" class="wf-wall-int"/>')

    serp = _catmull_rom(
        [
            (-43.0, -20.6),
            (-43.0, -11.0),
            (-41.2, -5.2),
            (-38.2, -1.2),
            (-36.5, -0.5),
            (-33.0, 1.0),
            (-30.3, 1.6),
        ]
    )
    out.append(f'    <polyline points="{pts_s(serp)}" class="wf-wall-int-bold"/>')

    for seg in (
        [(-77.5, 1.5), (-77.5, -21.0), (-43.0, -21.0)],
        [(-77.5, -21.0), (-77.5, -50.8)],
    ):
        out.append(f'    <polyline points="{pts_s(seg)}" class="wf-wall-int"/>')

    out.append(
        f'    <line x1="{xy((15.5, 3.6))[0]:.1f}" y1="{xy((15.5, 3.6))[1]:.1f}" x2="{xy((51.8, 32.8))[0]:.1f}" y2="{xy((51.8, 32.8))[1]:.1f}" class="wf-glass-wall"/>'
    )
    for k in range(15):
        t = k / 14.0
        mx, my = xy((15.5 + t * (51.8 - 15.5), 3.6 + t * (32.8 - 3.6)))
        out.append(
            f'    <circle cx="{mx:.1f}" cy="{my:.1f}" r="1.2" class="wf-mullion-dot"/>'
        )
    for seg in (
        [(25.87, 11.94), (39.34, -4.80)],
        [(15.50, 3.60), (16.9, -0.8), (19.0, -4.8), (51.2, -4.8)],
        [(18.5, -8.8), (51.8, -8.8)],
        [(18.2, -21.0), (41.5, -21.0)],
        [(46.5, -21.0), (61.5, -21.0)],
        [(25.5, -21.0), (25.5, -8.8)],
        [(36.5, -21.0), (36.5, -8.8)],
        [(16.8, -50.2), (17.15, -43.0)],
        [(17.41, -37.5), (18.2, -21.0)],
        [(18.4, -26.8), (21.0, -27.3), (24.5, -27.2), (28.5, -25.0), (31.5, -21.3)],
    ):
        out.append(f'    <polyline points="{pts_s(seg)}" class="wf-wall-int"/>')

    out.append(
        f'    <polygon points="{pts_s([(-18.0, -57.5), (0.0, -57.5), (0.0, -50.8), (-18.0, -50.8)])}" class="wf-glass-vestibule"/>'
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
        mh_orig[0] + 19.0 * math.cos(math.radians(65.7)),
        mh_orig[1] + 19.0 * math.sin(math.radians(65.7)),
    )
    p_mh0, p_mh1 = xy(mh_orig), xy(mh_tip)
    out.append(
        f'    <line x1="{p_mh0[0]:.1f}" y1="{p_mh0[1]:.1f}" x2="{p_mh1[0]:.1f}" y2="{p_mh1[1]:.1f}" class="wf-vista-arrow" marker-end="url(#wfArrowVista)"/>'
    )
    out.append(
        f'    <text x="{p_mh1[0] - 10:.1f}" y="{p_mh1[1] - 6:.1f}" class="wf-vista-lbl">MT. HOOD VISTA (65.7°) ↗</text>'
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
    """Side-by-side Mezzanine (-4'-6") / Level 2 (-12'-6") and Level 1 (-26'-6") plans."""
    w_vb, h_vb = 900, 360
    sc = 2.05

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
        '    <text x="18" y="24" class="wf-subplan-kicker">MEZZANINE (-4\'-6") &amp; LEVEL 2 (-12\'-6")</text>'
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
        pa, pb = xy_l2(G.WP3), xy_l2(polar_pt(G.WP3, 92.0, deg))
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
        ("10", (-16.0, 27.5), "Mezzanine Study Counter (-4 ft 6 in)"),
        ("11", (10.0, 41.5), "Level 2 Reference &amp; Stacks (-12 ft 6 in)"),
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
        '    <text x="482" y="24" class="wf-subplan-kicker">LEVEL 1 BASE DECK (-26\'-6")</text>'
    )
    out.append(
        '    <text x="482" y="40" class="wf-subplan-sub">Pentagonal Retaining Wall &amp; Archival Collections</text>'
    )
    out.append(
        f'    <polygon points="{pts_fn(env_l1, xy_l1)}" class="zone-staff layer-zones"/>'
    )

    out.append('    <g class="layer-reg">')
    for deg in (G.RAY_B_DEG, G.RAY_C_DEG, G.RAY_D_DEG):
        pa, pb = xy_l1(G.WP3), xy_l1(polar_pt(G.WP3, 92.0, deg))
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
        '      <g class="wf-pin" data-pin="12" tabindex="0" role="button" aria-label="12. Lower Archival Stacks (-26 ft 6 in)">'
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
    w_vb, h_vb = (820, 355) if compact else (1080, 468)
    sc = (w_vb - 96.0) / 180.0
    ox = 48.0 + 74.0 * sc
    oy = 38.0 + 30.0 * sc

    def sz(s_ft: float, z_ft: float) -> tuple[float, float]:
        return (ox + s_ft * sc, oy - z_ft * sc)

    def pts_s(pts: list[tuple[float, float]]) -> str:
        return " ".join(f"{sz(s, z)[0]:.1f},{sz(s, z)[1]:.1f}" for s, z in pts)

    out: list[str] = [
        f'<svg viewBox="0 0 {w_vb} {h_vb}" class="wf-svg wf-section-aa" role="img" aria-label="Longitudinal Architectural Cross-Section Through Skylights and Hillside">',
    ]

    # 1. Earth Hillside Bluff Poché
    earth_poly = [
        (-74.0, 1.8),
        (-50.8, 1.8),
        (-50.8, 0.9),
        (-21.0, 0.9),
        (-21.0, -13.6),
        (33.0, -13.6),
        (33.0, -27.7),
        (85.8, -27.7),
        (86.4, -28.2),
        (104.0, -34.5),
        (104.0, -36.5),
        (-74.0, -36.5),
    ]
    out.append(f'  <polygon points="{pts_s(earth_poly)}" class="wf-earth"/>')
    out.append(
        f'  <polygon points="{pts_s(earth_poly)}" fill="url(#wfEarthHatch)" class="wf-earth-hatch"/>'
    )
    out.append(
        f'  <polyline points="{pts_s([(-74.0, 1.8), (-50.8, 1.8)])}" class="wf-grade-line"/>'
    )
    out.append(
        f'  <polyline points="{pts_s([(85.8, -28.0), (104.0, -34.5)])}" class="wf-grade-line"/>'
    )

    aud_ghost = [(-50.8, 13.8), (-50.8, 20.2), (-21.0, 20.2), (-21.0, 13.8)]
    out.append(f'  <polygon points="{pts_s(aud_ghost)}" class="wf-aud-ghost"/>')
    if not compact:
        pa_lbl = sz(-36.0, 18.0)
        out.append(
            f'  <text x="{pa_lbl[0]:.1f}" y="{pa_lbl[1]:.1f}" text-anchor="middle" class="wf-ghost-lbl">AUDITORIUM ROOF (+20\'-2" BEYOND)</text>'
        )

    # 2. Interior Daylight & Solar Ray-Tracing Cones (toggleable via .layer-solar)
    out.append('  <g class="layer-solar">')
    scoop_wash = [
        (35.2, 21.3),
        (39.6, 15.3),
        (43.2, 11.33),
        (45.8, 0.0),
        (32.0, -4.5),
        (31.8, -12.5),
        (22.8, -12.5),
        (22.8, 0.0),
        (28.5, 13.2),
        (31.8, 19.0),
    ]
    out.append(f'    <polygon points="{pts_s(scoop_wash)}" fill="url(#wfSkyGlow)"/>')
    for sc_x, z_flr, half_w in ((-21.2, 2.0, 9.5), (10.2, 0.0, 10.5)):
        cone = [
            (sc_x - 2.1, 15.6),
            (sc_x + 2.1, 15.6),
            (sc_x + half_w, z_flr),
            (sc_x - half_w, z_flr),
        ]
        out.append(f'    <polygon points="{pts_s(cone)}" fill="url(#wfSunGlow)"/>')

    ray_paths = [
        (
            [(43.5, 25.5), (37.2, 18.2), (30.8, 16.8), (36.5, -2.5)],
            "wf-ray-sky",
            "wfArrowSky",
        ),
        (
            [(41.0, 26.2), (36.0, 19.8), (29.5, 14.5), (26.5, -4.2)],
            "wf-ray-sky",
            "wfArrowSky",
        ),
        (
            [(94.0, 15.8), (85.0, 11.8), (74.5, 13.2), (61.0, 2.5)],
            "wf-ray-sky",
            "wfArrowSky",
        ),
        (
            [(14.8, 26.8), (10.5, 15.8), (8.6, 12.2), (10.8, 3.6)],
            "wf-ray-sun",
            "wfArrowSun",
        ),
        (
            [(-16.6, 26.8), (-20.9, 15.8), (-22.6, 12.2), (-20.2, 2.2)],
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
        ("+21'-6\" SCOOP RIDGE", 21.5, 34.0),
        ("+16'-3\" FAN ROOF", 16.25, 40.0),
        ("+2'-0\" LOBBY", 2.0, -52.0),
        ("0'-0\" READING LEVEL", 0.0, -16.0),
        ("-4'-6\" MEZZANINE", -4.5, 22.0),
        ("-12'-6\" LEVEL 2", -12.5, -21.0),
        ("-26'-6\" LEVEL 1", -26.5, 33.0),
    ]:
        pa, pb = sz(s_start, zf), sz(103.5, zf)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-datum-line"/>'
        )
        out.append(
            f'    <text x="{pb[0] - 2:.1f}" y="{pb[1] - 3:.1f}" text-anchor="end" class="wf-datum-lbl">{lbl}</text>'
        )
    out.append("  </g>")

    # 4. Architectural Interior Elements in Elevation
    out.append('  <g class="layer-interior-elev">')
    for vx in (-57.5, -50.8):
        pa, pb = sz(vx, 1.8), sz(vx, 10.2)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-glass-elev"/>'
        )
    for bx in range(-44, -31, 2):
        pa, pb = sz(bx, 2.0), sz(bx, 10.8)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-batten-line"/>'
        )

    for s0, s1 in ((0.5, 6.9), (13.5, 18.8)):
        pa, pb = sz(s0, 9.75), sz(s1, 9.75)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-slat-ceiling"/>'
        )

    out.append(
        f'    <polygon points="{pts_s([(8.2, 0.0), (12.6, 0.0), (12.6, 3.5), (8.2, 3.5)])}" class="wf-bookcase"/>'
    )
    for rz in (1.1, 2.1, 3.1):
        pa, pb = sz(19.5, rz), sz(22.7, rz)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-rail-line"/>'
        )
    out.append(
        f'    <polygon points="{pts_s([(31.1, -12.5), (32.4, -12.5), (32.4, 18.6), (31.1, 18.0)])}" class="wf-col-elev"/>'
    )
    out.append(
        f'    <polygon points="{pts_s([(56.6, -26.5), (57.9, -26.5), (57.9, 11.33), (56.6, 11.33)])}" class="wf-col-elev"/>'
    )

    out.append(
        f'    <polygon points="{pts_s([(22.9, -4.5), (24.1, -4.5), (24.1, -0.8), (22.9, -0.8)])}" class="wf-bookcase"/>'
    )
    for s0, s1, z_flr, h_ft in [
        (51.2, 70.4, 0.0, 6.85),
        (35.2, 47.0, -12.5, 6.85),
        (52.0, 68.2, -12.5, 6.85),
        (39.0, 54.5, -26.5, 6.85),
        (59.0, 71.0, -26.5, 6.85),
    ]:
        out.append(
            f'    <polygon points="{pts_s([(s0, z_flr), (s1, z_flr), (s1, z_flr + h_ft), (s0, z_flr + h_ft)])}" class="wf-bookcase"/>'
        )
        for tier in range(1, 5):
            zt = z_flr + tier * (h_ft / 5.0)
            pa, pb = sz(s0, zt), sz(s1, zt)
            out.append(
                f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-shelf-line"/>'
            )

    for s_par, z_flr in ((31.8, -4.5), (43.8, 0.0)):
        dir_s = -1.0 if z_flr < 0 else 1.0
        out.append(
            f'    <polygon points="{pts_s([(s_par - 0.35, z_flr), (s_par + 0.35, z_flr), (s_par + 0.35, z_flr + 3.2), (s_par - 0.35, z_flr + 3.2)])}" class="wf-poche-cut"/>'
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
        f'    <polygon points="{pts_s([(80.8, 2.35), (84.6, 2.35), (84.6, 2.60), (80.8, 2.60)])}" class="wf-workbench"/>'
    )
    for gz0, gz1 in ((7.2, 15.0), (-9.2, -1.2), (-23.5, -15.5)):
        pa, pb = sz(85.1, gz0), sz(85.1, gz1)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-glass-elev"/>'
        )
    for lz in [7.6 + k * 1.05 for k in range(8)] + [-8.8 + k * 1.05 for k in range(8)]:
        pa, pb = sz(86.0, lz), sz(87.3, lz - 0.35)
        out.append(
            f'    <line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" class="wf-louver-tick"/>'
        )

    out.append(
        f'    <line x1="{sz(35.1, 21.5)[0]:.1f}" y1="{sz(35.1, 21.5)[1]:.1f}" x2="{sz(39.6, 15.3)[0]:.1f}" y2="{sz(39.6, 15.3)[1]:.1f}" class="wf-skylight-glass"/>'
    )
    for sc_x in (-21.2, 10.2):
        lantern = [
            (sc_x - 2.3, 12.67),
            (sc_x - 1.3, 15.83),
            (sc_x + 1.3, 15.83),
            (sc_x + 2.3, 12.67),
        ]
        out.append(f'    <polygon points="{pts_s(lantern)}" class="wf-lantern-cap"/>')
        out.append(
            f'    <polyline points="{pts_s([(sc_x - 3.1, 10.8), (sc_x - 2.1, 12.67)])}" class="wf-throat-line"/>'
        )
        out.append(
            f'    <polyline points="{pts_s([(sc_x + 3.1, 10.8), (sc_x + 2.1, 12.67)])}" class="wf-throat-line"/>'
        )

    truss_pts = [
        (43.5, 11.5),
        (48.0, 15.1),
        (52.5, 11.5),
        (57.0, 15.3),
        (61.5, 11.5),
        (65.5, 15.5),
        (71.0, 12.8),
        (76.5, 15.8),
    ]
    out.append(f'    <polyline points="{pts_s(truss_pts)}" class="wf-truss-web"/>')
    out.append("  </g>")

    # 5. Cut Structural Concrete & Roof Section Poché Solids
    out.append('  <g class="layer-poche">')
    poche_polys = [
        [(-66.0, 10.2), (-50.2, 10.2), (-50.2, 10.8), (-66.0, 10.8)],
        [(-64.4, 1.8), (-63.7, 1.8), (-63.7, 10.2), (-64.4, 10.2)],
        [
            (-51.6, 10.8),
            (-24.3, 10.8),
            (-23.3, 12.67),
            (-50.2, 12.67),
            (-50.2, 13.85),
            (-51.6, 13.85),
        ],
        [(-18.1, 10.8), (7.1, 10.8), (8.1, 12.67), (-19.1, 12.67)],
        [
            (13.3, 10.8),
            (24.2, 10.8),
            (26.8, 13.2),
            (29.8, 16.8),
            (32.4, 19.6),
            (35.1, 21.5),
            (34.2, 22.1),
            (30.8, 19.8),
            (27.4, 16.2),
            (23.8, 12.67),
            (12.3, 12.67),
        ],
        [
            (39.6, 15.25),
            (84.6, 16.25),
            (84.6, 17.85),
            (85.8, 17.85),
            (85.8, 15.0),
            (84.4, 15.0),
            (65.5, 11.33),
            (43.2, 11.33),
        ],
        [(84.6, 0.0), (85.8, 0.0), (85.8, 7.2), (84.6, 7.2)],
        [(84.6, -1.2), (85.8, -1.2), (85.8, 0.0), (84.6, 0.0)],
        [(84.6, -13.6), (85.8, -13.6), (85.8, -9.2), (84.6, -9.2)],
        [(84.6, -28.0), (85.8, -28.0), (85.8, -23.5), (84.6, -23.5)],
        [
            (-51.6, 0.9),
            (-19.5, 0.9),
            (-16.0, -0.9),
            (22.0, -0.9),
            (22.0, -5.4),
            (32.0, -5.4),
            (32.0, -4.5),
            (22.9, -4.5),
            (22.9, 0.0),
            (-16.0, 0.0),
            (-19.5, 2.0),
            (-51.6, 2.0),
        ],
        [(43.5, -0.95), (85.8, -0.95), (85.8, 0.0), (43.5, 0.0)],
        [
            (-21.8, -13.6),
            (85.8, -13.6),
            (85.8, -12.5),
            (-20.8, -12.5),
            (-20.8, 0.9),
            (-21.8, 0.9),
        ],
        [
            (32.2, -27.7),
            (85.8, -27.7),
            (85.8, -26.5),
            (33.2, -26.5),
            (33.2, -13.6),
            (32.2, -13.6),
        ],
    ]
    for poly in poche_polys:
        out.append(f'    <polygon points="{pts_s(poly)}" class="wf-poche-cut"/>')
    out.append("  </g>")

    # 6. Human Scale Silhouettes
    out.append('  <g class="layer-figures">')
    for fx, fz in ((-47.0, 2.0), (5.2, 0.0), (47.2, 0.0), (28.0, -4.5), (49.5, -12.5)):
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
        ((-59.0, 10.8), (-58.0, 18.5), "SOUTH PORTICO"),
        ((-21.2, 15.9), (-18.5, 24.0), "CONICAL SKYLIGHTS (12)"),
        ((35.1, 21.8), (20.5, 27.8), "NORTH DAYLIGHT SCOOP (+21'-6\")"),
        ((57.0, 14.2), (54.5, 23.6), "3'-11\" TRUSS ROOF PLENUM"),
        ((85.8, 11.5), (80.0, 27.8), "+7'-2\" CLERESTORY &amp; LOUVERS"),
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
        (-36.0, 5.5, "ENTRANCE LOBBY"),
        (10.0, 5.8, "CONTROL DESK"),
        (33.5, 4.2, "READING WELL"),
        (61.0, 8.5, "MAIN FAN STACKS"),
        (27.5, -8.5, "MEZZANINE"),
        (60.0, -8.5, "LEVEL 2 STACKS"),
        (55.0, -21.5, "LEVEL 1 ARCHIVAL DECK"),
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
  <text x="180" y="21" class="wf-vista-lbl">65.7° MT. HOOD ↗</text>
  <text x="130" y="180" text-anchor="middle" class="wf-callout-lbl">IRREGULAR H-COLUMN D ALCOVE</text>
</svg>"""

    return {"cone": d_cone, "lamp": d_lamp, "hpier": d_hpier}


def build_polycentric_diagram_svg() -> str:
    """Analytical Constructive Diagram of Aalto's 4 Working Points, Radial Fan, and 4-Origin Inset."""
    w_vb, h_vb = 920, 446
    sc = 3.05
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
        (G.R_GALLERY_RAIL, "R = 23'-6\" GALLERY"),
        (G.R_WELL_L2_WALL, "R = 31'-10\" WELL CORE"),
        (G.R_MEZZ_OPENING, "R = 44'-2\" MEZZANINE"),
        (85.5, "R = 85'-6\" NORTH WALL"),
    ):
        apts = arc_pts(G.WP3A, r_arc, 40.0, 162.0, 44)
        out.append(f'  <polyline points="{pts_s(apts)}" class="wf-reg-arc"/>')
        lp = xy(polar_pt(G.WP3A, r_arc, 159.0))
        out.append(
            f'  <text x="{lp[0] - 4:.1f}" y="{lp[1] - 3:.1f}" text-anchor="end" class="wf-datum-lbl">{lbl_arc}</text>'
        )

    for deg, name, orig in (
        (G.RAY_A_DEG, "AXIS A (136.5°)", G.WP_LOWER),
        (G.RAY_B_DEG, "AXIS B (112.9°)", G.WP3),
        (G.RAY_C_DEG, "AXIS C (89.3°)", G.WP3),
        (G.RAY_D_DEG, "AXIS D (65.7° MT. HOOD)", G.WP3),
        (G.RAY_E_DEG, "AXIS E (42.1°)", G.WP_LOWER),
    ):
        pa, pb = xy(orig), xy(polar_pt(orig, 93.0, deg))
        cls = "wf-vista-arrow" if "65.7" in name else "wf-reg-ray"
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
        156.0,
        149.5,
        143.0,
        130.5,
        124.2,
        118.0,
        111.8,
        105.5,
        92.5,
        86.2,
        80.0,
        73.8,
        57.5,
        51.2,
        45.0,
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

    for wp_pt in (G.WP4, G.WP3, G.WP3A, G.WP_DESK):
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

    # Right Top: 16x Magnified 4-Origin Cluster Inset
    ix, iy, isc = 774.0, 178.0, 28.0
    out.append(
        '  <text x="648" y="24" class="wf-subplan-kicker">MAGNIFIED 4-ORIGIN CLUSTER (16×)</text>'
    )
    out.append(
        '  <text x="648" y="40" class="wf-subplan-sub">Subtle eccentricities prevent rigid symmetry</text>'
    )
    out.append(
        f'  <line x1="652" y1="{iy:.1f}" x2="898" y2="{iy:.1f}" class="wf-datum-line"/>'
    )
    out.append(
        f'  <line x1="{ix:.1f}" y1="64" x2="{ix:.1f}" y2="222" class="wf-datum-line"/>'
    )
    origins = [
        (G.WP4, "WP #4 (0, 0)", "Survey Grid 6 Datum", 8, 13),
        (G.WP3, "WP #3 (0, +1.0')", "Primary Rays B, C, D", 8, -5),
        (G.WP3A, "WP #3A (+1.5', +2.6')", "Well, Scoop &amp; Stacks", 8, -6),
        (G.WP_DESK, "WP_DESK (-1.2', +2.2')", "Desk &amp; Slatted Ceiling", -8, -8),
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
        '  <text x="648" y="278" class="wf-subplan-sub">Heights above Level 3 Reading Deck (0\'-0")</text>'
    )
    y_base = 410.0
    z_sc = 4.8
    bars = [
        (654, 52, 12.67, "zone-public", "+12'-8\"", "SOUTH / LOBBY"),
        (714, 58, 16.25, "zone-quiet", "+16'-3\"", "MAIN FAN"),
        (780, 56, 18.67, "zone-auditorium", "+18'-8\"", "AUDITORIUM"),
        (844, 54, 21.50, "zone-well", "+21'-6\"", "SCOOP RIDGE"),
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
