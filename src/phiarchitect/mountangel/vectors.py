"""
Mount Angel Abbey Library — Constructive Geometry & Multi-Sheet Vector Overlay Engine.

Establishes a unified canonical 3D architectural coordinate system verified directly
against Alvar Aalto & DeMars/Wells archival working drawings (Sheets A-3..A-22, S-4..S-17):
  - Origin O(0, 0, 0): Working Point #3 (convergence hub of Structural Rays B, C, D and
    all H-Column legs on Grid Line 6) at Level 3 Finished Floor (EL. +128'-6").
  - WP #2 (+2'-10", -5'-3"): Lower convergence hub of Outer Boundary Rays A & E.
  - WP #3A (+1'-7 3/8", +3'-4 5/8", 3'-9" along Ray D): Concentric center of the R = 31'-10"
    Mezzanine / Reading Well, R = 32'-0" Well-Column arc, and Daylight Scoop.
  - +X = East, +Y = North (Grid Line 6 along Y = 0), +Z = Upward.
  - Primary constructive units: exact architectural feet (converted to metres via
    FT_TO_M = 0.3048 for IngeTrazo 0.6.0).

Cross-registers 7 primary historical blueprint sheets (A & S series) to sub-pixel
accuracy and emits multi-layer College-Geometry-style SVG vector overlays.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

FT_TO_M = 0.3048


def ft(feet: float, inches: float = 0.0) -> float:
    """Return decimal feet from feet and inches (positive magnitude when feet < 0 subtracts inches)."""
    if feet < 0:
        return float(feet) - abs(float(inches)) / 12.0
    return float(feet) + float(inches) / 12.0


def ft_m(feet: float, inches: float = 0.0) -> float:
    """Return metres from feet and inches."""
    return ft(feet, inches) * FT_TO_M


def polar_pt(center: tuple[float, float], radius_ft: float, angle_deg: float) -> tuple[float, float]:
    """2D Cartesian point (X_ft, Y_ft) at polar offset from center."""
    rad = math.radians(angle_deg)
    return (center[0] + radius_ft * math.cos(rad), center[1] + radius_ft * math.sin(rad))


def arc_pts(
    center: tuple[float, float],
    radius_ft: float,
    start_deg: float,
    end_deg: float,
    steps: int = 36,
) -> list[tuple[float, float]]:
    """Sample polyline points along a circular arc from start_deg to end_deg."""
    return [
        polar_pt(center, radius_ft, start_deg + (end_deg - start_deg) * (i / steps))
        for i in range(steps + 1)
    ]


def _ray_offset_pt(origin: tuple[float, float], deg: float, r: float, t_off: float = 0.0) -> tuple[float, float]:
    """Point at radial distance r along ray `deg` from `origin` plus perpendicular clockwise offset `t_off`."""
    rad = math.radians(deg)
    urx, ury = math.cos(rad), math.sin(rad)
    utx, uty = math.sin(rad), -math.cos(rad)
    return (origin[0] + r * urx + t_off * utx, origin[1] + r * ury + t_off * uty)


def _ray_circle_intersect(
    origin: tuple[float, float],
    deg: float,
    center: tuple[float, float],
    radius_ft: float,
) -> tuple[float, float]:
    """Forward intersection of ray (`origin`, `deg`) with circle (`center`, `radius_ft`)."""
    rad = math.radians(deg)
    ux, uy = math.cos(rad), math.sin(rad)
    dx, dy = origin[0] - center[0], origin[1] - center[1]
    b = 2.0 * (dx * ux + dy * uy)
    c = dx * dx + dy * dy - radius_ft * radius_ft
    t = (-b + math.sqrt(max(0.0, b * b - 4.0 * c))) / 2.0
    return (origin[0] + t * ux, origin[1] + t * uy)


def _step_along(p0: tuple[float, float], p1: tuple[float, float], dist_ft: float) -> tuple[float, float]:
    """Point at `dist_ft` from `p0` toward `p1`."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    return (p0[0] + dist_ft * dx / L, p0[1] + dist_ft * dy / L)


def _line_intersect_2d(
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    p4: tuple[float, float],
) -> tuple[float, float]:
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return (px, py)


def _local_leg_pt(p: tuple[float, float], deg: float, s: float, t: float = 0.0) -> tuple[float, float]:
    rad = math.radians(deg)
    urx, ury = math.cos(rad), math.sin(rad)
    utx, uty = math.sin(rad), -math.cos(rad)
    return (p[0] + s * urx + t * utx, p[1] + s * ury + t * uty)


# =============================================================================
# 1. MASTER ARCHITECTURAL & CONSTRUCTIVE GEOMETRY CONSTANTS (FEET)
# =============================================================================

# Archival Working Points from W.P. DIMENSIONS (Sheets 05-a5, 06-a6, 35-s4)
_WP3: tuple[float, float] = (0.0, 0.0)                            # Origin on Grid 6: Hub of Rays B, C, D
_WP2: tuple[float, float] = (ft(2, 10), -ft(5, 3))                # (+2'-10", -5'-3"): Hub of Rays A & E
_WP1: tuple[float, float] = (ft(62, 5), -ft(61, 0))               # (+62'-5", -61'-0"): Auditorium SE corner (Grid 1)
_WP4: tuple[float, float] = (-ft(89, 0.5), ft(13, 9.75))          # (-89'-0 1/2", +13'-9 3/4"): West Jamb (Ray A)
_WP5: tuple[float, float] = (-ft(63, 7), ft(59, 4))               # (-63'-7", +59'-4"): H-Col B ref (Ray B)
_WP6: tuple[float, float] = (-ft(14, 9), ft(89, 5))               # (-14'-9", +89'-5"): H-Col C Bay-2 ref (Ray C)
_WP8: tuple[float, float] = (ft(42, 7), ft(89, 5))                # (+42'-7", +89'-5"): H-Col D Bay-3 ref (Ray D)
_WP10: tuple[float, float] = (ft(96, 4), ft(74, 0))               # (+96'-4", +74'-0"): East Prow Apex (Ray E)

_RAY_A_DEG = math.degrees(math.atan2(_WP4[1] - _WP2[1], _WP4[0] - _WP2[0]))   # 168.278°
_RAY_B_DEG = math.degrees(math.atan2(_WP5[1] - _WP3[1], _WP5[0] - _WP3[0]))   # 136.980°
_RAY_C_DEG = math.degrees(math.atan2(_WP6[1] - _WP3[1], _WP6[0] - _WP3[0]))   #  99.367°
_RAY_D_DEG = math.degrees(math.atan2(_WP8[1] - _WP3[1], _WP8[0] - _WP3[0]))   #  64.535°
_RAY_E_DEG = math.degrees(math.atan2(_WP10[1] - _WP2[1], _WP10[0] - _WP2[0])) #  40.284°

# Double Working Points stepping 1'-4 5/8" inward along Rays C & D (Sheet 06-a6)
_WP7: tuple[float, float] = polar_pt(_WP6, -ft(1, 4.625), _RAY_C_DEG)
_WP9: tuple[float, float] = polar_pt(_WP8, -ft(1, 4.625), _RAY_D_DEG)

# WP #3A lies directly on Ray D, 3'-9" NE of WP #3 (verified by Well_1/2/3 circumcircle)
_WP3A: tuple[float, float] = polar_pt(_WP3, ft(3, 9), _RAY_D_DEG)             # (+1.612, +3.386) ft

_R_WELL_COL_RING = ft(32, 0)  # Exact 32'-0" radius through Well_1, Well_2, Well_3 from WP #3A


class AaltoGeometry:
    """Canonical constructive geometry of Alvar Aalto's Mount Angel Abbey Library."""

    # --- Vertical Elevations (Feet relative to Level 3 = EL. +128'-6" = 0'-0") ---
    # Verified identically across Sheets 13-a13, 17-a17, 18-a18, 22-a22, 46-s15 & 48-s17.
    Z_LOBBY_FT = ft(1, 4)               #  +1'-4"     (EL. +129'-10", +0.406 m) South Entrance Wing, Lobby & Auditorium (3R up from L3)
    Z_L3_FT = 0.0                       #   0'-0"     (EL. +128'-6",   0.000 m) Main Fan Reading Room, Control Desk & Periodical Lounge
    Z_REF_GALLERY_FT = -ft(5, 4)        #  -5'-4"     (EL. +123'-2",  -1.626 m) Semicircular Mezzanine / Reading Level (10R down from L3, 16R up from L2)
    Z_L2_FT = -ft(14, 0)                # -14'-0"     (EL. +114'-6",  -4.267 m) Level 2 Stacks, Carrels & Reading Well (14'-0" below L3)
    Z_L1_FT = -ft(28, 6)                # -28'-6"     (EL. +100'-0",  -8.687 m) Level 1 Downhill Base Stacks (14'-6" below L2; 26R)
    Z_CRAWL_FT = -ft(35, 0)             # -35'-0"     (EL.  +93'-6", -10.668 m) North Crawl Space & Footing Toe

    Z_CANOPY_FT = ft(10, 10)            # +10'-10"    (EL. +139'-4",  +3.302 m) South Entry Portico Marquee Top (soffit ~+10'-0", 8'-8" above Lobby)
    Z_SOUTH_CEIL_FT = ft(10, 5.5)       # +10'-5 1/2" (EL. +138'-11.5", +3.188 m) South Wing / Lobby Ceiling Soffit (9'-1 1/2" above Lobby; 17-a17 Sec. 3)
    Z_FAN_CEIL_FT = ft(11, 4)           # +11'-4"     (EL. +139'-10", +3.454 m) Fan Reading Room Flat Ceiling Soffit below 24WF68 Plenum (17-a17 Sec. 1)
    Z_HEADER_BEAM_BOT_FT = ft(12, 8)    # +12'-8"     (EL. +141'-2",  +3.861 m) Skylight Header Beam Plaster Soffit (48-s17 Det. B: 18WF50)
    Z_SOUTH_ROOF_FT = ft(13, 8)         # +13'-8"     (EL. +142'-2",  +4.166 m) Lower South Wing / Lobby / Lounge Roof Deck (EL. 141'-10" bottom of decking)
    Z_HEADER_BEAM_TOP_FT = ft(14, 7.375)# +14'-7 3/8" (EL. +143'-1 3/8", +4.455 m) Skylight Header Beam Top Cap / Flashing (48-s17 Det. B)
    Z_SOUTH_PARAPET_FT = ft(15, 0)      # +15'-0"     (EL. +143'-6",  +4.572 m) South Entrance & West Wing Parapet Coping (13'-8" above Lobby; 17-a17 Sec. 4)
    Z_FAN_ROOF_LOW_FT = ft(15, 3)       # +15'-3"     (EL. +143'-9",  +4.648 m) Main Fan Built-up Roof Deck (inner edge at skylight curb)
    Z_LOUNGE_PARAPET_FT = ft(15, 11.375)# +15'-11 3/8"(EL. +144'-5 3/8", +4.861 m) Periodical Lounge East Wall & North/West Parapet (17-a17 Sec. 2 & 3)
    Z_FAN_ROOF_HIGH_FT = ft(16, 2)      # +16'-2"     (EL. +144'-8",  +4.928 m) Outer North Perimeter Fan Roof Deck (tapering over clerestory soffit)
    Z_LANTERN_TOP_FT = ft(16, 4)        # +16'-4"     (EL. +144'-10", +4.978 m) Conical Roof Skylight Lantern Peaks above South Wing Roof
    Z_AUDITORIUM_ROOF_FT = ft(17, 10)   # +17'-10"    (EL. +146'-4",  +5.436 m) Taller SE Auditorium (Rm 327) Dark Membrane Roof Deck
    Z_FAN_PARAPET_N_FT = ft(17, 11.375) # +17'-11 3/8"(EL. +146'-5 3/8", +5.471 m) North Perimeter Brick & Copper Parapet Coping (17-a17 Sec. 1)
    Z_AUDITORIUM_PARAPET_FT = ft(19, 3.375)  # +19'-3 3/8" (EL. +147'-9 3/8", +5.877 m) SE Auditorium Parapet (17'-11 3/8" above Lobby; 17-a17)
    Z_SCOOP_RIDGE_FT = ft(21, 4)        # +21'-4"     (EL. +149'-10", +6.502 m) Curved Central Clerestory Light Scoop Peak (18-a18 Sec. 4 & 48-s17 Det. D)

    # --- Polycentric Working Points (Exact Archival Numbering, Feet relative to WP #3) ---
    WP1: tuple[float, float] = _WP1
    WP2: tuple[float, float] = _WP2
    WP3: tuple[float, float] = _WP3
    WP3A: tuple[float, float] = _WP3A
    WP4: tuple[float, float] = _WP4
    WP5: tuple[float, float] = _WP5
    WP6: tuple[float, float] = _WP6
    WP7: tuple[float, float] = _WP7
    WP8: tuple[float, float] = _WP8
    WP9: tuple[float, float] = _WP9
    WP10: tuple[float, float] = _WP10

    WP_LOWER: tuple[float, float] = _WP2         # Alias for WP #2 (Hub of Outer Boundary Rays A & E)
    WP_DESK: tuple[float, float] = (-1.10, 2.35) # Center of Control Desk & Slatted Wood Drum

    # --- Analytically Derived Radial Axes (Degrees CCW from +X East) ---
    RAY_A_DEG: float = _RAY_A_DEG   # 168.278° (WP #2 -> Well_W_South -> South_W1 -> WP #4)
    RAY_B_DEG: float = _RAY_B_DEG   # 136.980° (WP #3 -> Well_1 -> Pair_B -> WP #5)
    RAY_C_DEG: float = _RAY_C_DEG   #  99.367° (WP #3 -> Well_2 -> Pair_C -> WP #7 / WP #6)
    RAY_D_DEG: float = _RAY_D_DEG   #  64.535° (WP #3 -> WP #3A -> Well_3 -> Pair_D -> WP #9 / WP #8)
    RAY_E_DEG: float = _RAY_E_DEG   #  40.284° (WP #2 -> Well_4_ENE -> East Diagonal -> WP #10)

    # --- Outer Fan Perimeter Reference Working Point Aliases ---
    PT_A: tuple[float, float] = _WP4
    PT_B: tuple[float, float] = _WP5
    PT_C: tuple[float, float] = _WP6
    PT_D: tuple[float, float] = _WP8
    PT_E: tuple[float, float] = _WP10

    # --- Centralized South Wing Plan X-Coordinates (Feet relative to WP #3) ---
    X_WEST_WING: float = -ft(129, 5)    # -129'-5" West Cataloging Wing exterior brick face (total E-W width = 191'-10")
    X_SOUTH_STEP: float = -ft(91, 2)    #  -91'-2" Main South Entrance Wing West exterior wall (Grid 2 -> Grid 3 step)
    X_ELEV_E: float = -ft(80, 10)       #  -80'-10" Elevator / Stair #4 East line (steps North to Ray A)
    X_RESTROOM_E: float = -ft(35, 6)    #  -35'-6" Staff Restrooms / Vestibule-West concrete pier line
    X_LOBBY_W: float = -ft(21, 9)       #  -21'-9" Main Entry Lobby West wall
    X_LOBBY_E_G2: float = ft(17, 6)     #  +17'-6" Canted Lobby / Rare Book junction at Grid 2
    X_AUD_SW: float = ft(19, 2)         #  +19'-2" Rare Book & Auditorium SW corner at Grid 1
    X_LOUNGE_E: float = ft(52, 2)       #  +52'-2" Periodical Lounge East brick facade (Mt. Hood picture window)
    X_AUD_E: float = ft(62, 5)          #  +62'-5" Rare Book & Auditorium East exterior wall (WP #1)

    # --- Orthogonal Survey Grid Lines 1..6 (Y_ft) ---
    GRID_Y = {
        "6": 0.0,           #   0'-0" Main Fan / South Wing Datum (WP #3)
        "5": -ft(8, 10),    #  -8'-10" Rare Book Vault / East Stair North wall
        "4": -ft(21, 6),    # -21'-6" Central Corridor / Auditorium North wall
        "3": -ft(29, 0),    # -29'-0" West Cataloging Wing South facade
        "2": -ft(51, 8),    # -51'-8" Main South Entrance facade (-29'-0" - 22'-8")
        "1": -ft(61, 0),    # -61'-0" East Rare Book & Auditorium South facade (WP #1, -51'-8" - 9'-4")
    }

    # Inner West & East Junctions where Fan meets South Wing & Periodical Lounge
    # PT_A_INNER_JUNC sits directly on Ray A at X = X_ELEV_E (-80'-10")
    PT_A_INNER_JUNC: tuple[float, float] = (
        X_ELEV_E,
        _WP2[1] + (X_ELEV_E - _WP2[0]) * math.tan(math.radians(_RAY_A_DEG)),
    )  # (-80.833, +12.11) ft
    PT_WEST_THROAT: tuple[float, float] = (-19.0, 0.2)
    # PT_LOUNGE_JUNC sits where the East Diagonal Wall (Ray E) meets Periodical Lounge East wall (X = +52'-2")
    PT_LOUNGE_JUNC: tuple[float, float] = (
        X_LOUNGE_E,
        _WP2[1] + (X_LOUNGE_E - _WP2[0]) * math.tan(math.radians(_RAY_E_DEG)),
    )  # (+52.167, +36.56) ft — verify against 05-a5 / 06-a6 corner step!
    PT_EAST_THROAT: tuple[float, float] = (15.8, 3.6)

    # --- Concentric / Polycentric Radii around WP #3A (+1'-7 3/8", +3'-4 5/8") ---
    R_DESK_INNER = 11.0
    R_DESK_OUTER = 14.5
    R_WOOD_DRUM = 17.5
    R_GALLERY_RAIL = ft(22, 0)       # 22'-0" Mezzanine inner retaining wall (9'-10" inside 31'-10"; 46-s15 Det. N2)
    R_SCOOP_INNER = ft(25, 10)       # 25'-10" Inner daylight scoop reference line (18-a18 Sec. 4 & 48-s17 Det. D)
    R_WELL_L2_WALL = ft(31, 10)      # 31'-10" Curved L2 Reading Well Wall & Mezzanine Outer Parapet
    R_WELL_COL_RING = _R_WELL_COL_RING  # 32'-0" Exact circular arc through Well_1, Well_2, Well_3
    R_SCOOP_RIDGE = ft(34, 6)        # 34'-6" Peak ridge where curved copper/plaster scoop meets North glazing (18-a18 Sec. 4)
    R_SCOOP_OUTER = ft(41, 2)        # 41'-2" Outer curb of sloped North skylight glass (25'-10" + 15'-4"; 48-s17 Det. D)
    R_MEZZ_OPENING = ft(44, 0)       # 44'-0" Level 3 Double-Height Reading Well Opening
    R_MEZZ_DESK = ft(46, 4)          # 46'-4" Outer edge of continuous curved Level 3 reading workbench

    # --- Structural Round Columns (18" diameter = 0.75 ft radius; Sheet 06-a6) ---
    # Well_1/2/3 are exact analytical intersections of Rays B, C, D (from WP #3) with R = 32'-0" around WP #3A.
    # Well_W_South & South_W1 lie directly on Ray A (from WP #2); Well_4_ENE lies tangent to Ray E (from WP #2).
    WELL_COLS_FT = {
        "Well_W_South": polar_pt(_WP2, ft(34, 8.5), _RAY_A_DEG),
        "Well_1_WNW":   _ray_circle_intersect(_WP3, _RAY_B_DEG, _WP3A, _R_WELL_COL_RING),
        "Well_2_NNW":   _ray_circle_intersect(_WP3, _RAY_C_DEG, _WP3A, _R_WELL_COL_RING),
        "Well_3_NNE":   _ray_circle_intersect(_WP3, _RAY_D_DEG, _WP3A, _R_WELL_COL_RING),
        "Well_4_ENE":   _ray_offset_pt(_WP2, _RAY_E_DEG, ft(39, 6), +0.48),
        "South_W1":     polar_pt(_WP2, ft(60, 2.5), _RAY_A_DEG),
    }

    # 6 Paired Twin 18"Ø Columns symmetrically straddling WP #3 Rays B, C, D at ±2'-8" (5'-4" c/c; Sheet 06-a6)
    PAIRED_COLS_FT = {
        "Pair_B_L": _ray_offset_pt(_WP3, _RAY_B_DEG, ft(57, 7), -ft(2, 8)),
        "Pair_B_R": _ray_offset_pt(_WP3, _RAY_B_DEG, ft(57, 5), +ft(2, 8)),
        "Pair_C_L": _ray_offset_pt(_WP3, _RAY_C_DEG, ft(59, 2), -ft(2, 8)),
        "Pair_C_R": _ray_offset_pt(_WP3, _RAY_C_DEG, ft(59, 9), +ft(2, 8)),
        "Pair_D_L": _ray_offset_pt(_WP3, _RAY_D_DEG, ft(65, 3), -ft(2, 8)),
        "Pair_D_R": _ray_offset_pt(_WP3, _RAY_D_DEG, ft(66, 0), +ft(2, 8)),
    }

    SOUTH_WING_COLS_FT = [
        (-104.5, 0.0), (X_SOUTH_STEP, 0.0), (-55.0, 0.0), (-35.5, 0.0), (-19.0, 0.0),
        (X_SOUTH_STEP, GRID_Y["3"]), (X_SOUTH_STEP, GRID_Y["2"]), (-72.5, GRID_Y["2"]),
        (-52.5, GRID_Y["2"]), (X_LOBBY_W, GRID_Y["2"]), (5.0, GRID_Y["2"]), (X_LOBBY_E_G2, GRID_Y["2"]),
        (X_LOUNGE_E, 0.0), (X_LOUNGE_E, 16.5), (X_LOUNGE_E, 33.5),
    ]

    # --- 3 Distinct Irregular Perimeter H-Columns (Sheets 06-a6 & 45-s14) ---
    # Anchored analytically to WP #4..#10 and WP #3:
    # - Outer fin corners sit at exact jamb offsets from WP #5, WP #6/#7, WP #8/#9 along the 4 bays
    #   so glass openings equal exact printed 47'-0", 47'-0", 47'-0", and 50'-11".
    # - Both splayed legs point radially directly to WP #3 ("TO W.P. #3" on Sheet 45-s14).
    # - Recessed web sits 90° perpendicular to central Ray B/C/D at printed web_depth from WP_R.
    H_PIERS = [
        {
            "name": "HPier_B",
            "label": "H-COL B (WP #5)",
            "ray_deg": _RAY_B_DEG,
            "wp_L": _WP5, "bay_L_other": _WP4, "jamb_L": ft(4, 7.0),
            "wp_R": _WP5, "bay_R_other": _WP6, "jamb_R": ft(5, 2.13),
            "web_depth": ft(4, 0),
            "len_L": ft(7, 11),
            "len_R": ft(7, 11),
        },
        {
            "name": "HPier_C",
            "label": "H-COL C (WP #6/#7)",
            "ray_deg": _RAY_C_DEG,
            "wp_L": _WP6, "bay_L_other": _WP5, "jamb_L": ft(5, 2.13),
            "wp_R": _WP7, "bay_R_other": _WP8, "jamb_R": ft(4, 11.0),
            "web_depth": ft(3, 8),
            "len_L": ft(7, 10),
            "len_R": ft(7, 10),
        },
        {
            "name": "HPier_D",
            "label": "H-COL D (WP #8/#9)",
            "ray_deg": _RAY_D_DEG,
            "wp_L": _WP8, "bay_L_other": _WP7, "jamb_L": ft(5, 2.25),
            "wp_R": _WP9, "bay_R_other": _WP10, "jamb_R": ft(5, 2.75),
            "web_depth": ft(3, 8),
            "len_L": ft(8, 10),
            "len_R": ft(7, 6),
        },
    ]

    # --- 14 Roof Conical Dome Skylights (X_ft, Y_ft, radius_ft) exact from Drawing 07-a7 & 10-a10 ---
    CONICAL_SKYLIGHTS = [
        # Control Desk Slatted Wood Drum Portholes (2)
        (-10.8, 8.8, 2.2),
        (5.2, 8.8, 2.2),
        # West Staff / Elevator Corridor Vertical Pair (2)
        (-76.5, 2.0, 2.2),
        (-76.5, -12.0, 2.2),
        # Public Catalog, Microfilm & Entry Area Row (4)
        (-41.0, -12.0, 2.2),
        (-27.5, -12.0, 2.2),
        (-12.0, -14.5, 2.2),
        (4.0, -14.5, 2.2),
        # West Cataloging & Corridor String (4)
        (-112.0, -26.5, 2.2),
        (-94.2, -26.5, 2.2),
        (-76.5, -26.5, 2.2),
        (-58.8, -26.5, 2.2),
        # Main Entrance Lobby Skylights (2)
        (-12.0, -26.0, 2.2),
        (4.0, -26.0, 2.2),
    ]

    # --- 3 Outer-Fan Rooftop Exhaust Fans alongside Structural Rays B, C, D (Sheets 07-a7 & 36-s5) ---
    FAN_ROOF_EXHAUST_FANS = [
        (-54.5, 49.0, 1.8),   # Beside Ray B / H-Col B
        (-10.5, 75.0, 1.8),   # Beside Ray C / H-Col C
        (38.5, 75.0, 1.8),    # Beside Ray D / H-Col D
    ]


# =============================================================================
# 2. SHEET CALIBRATION TRANSFORMS
# =============================================================================

@dataclass(frozen=True)
class SheetCalibration:
    sheet_id: int
    filename: str
    title: str
    width_px: int
    height_px: int
    scale_px_per_ft: float
    rot_deg: float
    origin_px: tuple[float, float]
    mode: str = "plan"  # "plan" (X, Y) or "section_aa" (S_north, Z)
    scale_y_px_per_ft: float | None = None  # Optional blueline paper-stretch Y scale

    def world_to_px(self, wx: float, wy: float) -> tuple[float, float]:
        """Map canonical world feet (X, Y) [or (S, Z) for section] to image pixels."""
        ang = math.radians(self.rot_deg)
        ca, sa = math.cos(ang), math.sin(ang)
        sx = wx * self.scale_px_per_ft
        sy = -wy * (self.scale_y_px_per_ft if self.scale_y_px_per_ft is not None else self.scale_px_per_ft)
        px = (ca * sx - sa * sy) + self.origin_px[0]
        py = (sa * sx + ca * sy) + self.origin_px[1]
        return (px, py)


CALIBRATED_SHEETS: dict[int, SheetCalibration] = {
    3: SheetCalibration(
        sheet_id=3,
        filename="03-a3_gm-1135x700.jpg",
        title="FLOOR PLAN LEVEL #1",
        width_px=1135,
        height_px=700,
        scale_px_per_ft=3.3680,
        scale_y_px_per_ft=3.3450,
        rot_deg=-0.120,
        origin_px=(621.80, 419.50),
    ),
    4: SheetCalibration(
        sheet_id=4,
        filename="04-a4_gm-1144x700.jpg",
        title="FLOOR PLAN LEVEL TWO",
        width_px=1144,
        height_px=700,
        scale_px_per_ft=3.3800,
        scale_y_px_per_ft=3.3450,
        rot_deg=-0.100,
        origin_px=(622.20, 420.50),
    ),
    5: SheetCalibration(
        sheet_id=5,
        filename="05-a5_gm-1145x700.jpg",
        title="FLOOR PLAN LEVEL #3",
        width_px=1145,
        height_px=700,
        scale_px_per_ft=3.3800,
        scale_y_px_per_ft=3.3380,
        rot_deg=+0.020,
        origin_px=(623.00, 419.50),
    ),
    6: SheetCalibration(
        sheet_id=6,
        filename="06-a6_gm-1149x700.jpg",
        title="BASIC PLAN LAYOUT",
        width_px=1149,
        height_px=700,
        scale_px_per_ft=6.7271,
        rot_deg=-0.321,
        origin_px=(692.86, 693.37),
    ),
    7: SheetCalibration(
        sheet_id=7,
        filename="07-a7_gm-1145x700.jpg",
        title="ROOF PLAN & DETAILS",
        width_px=1145,
        height_px=700,
        scale_px_per_ft=3.3850,
        scale_y_px_per_ft=3.3450,
        rot_deg=+0.050,
        origin_px=(623.00, 419.20),
    ),
    13: SheetCalibration(
        sheet_id=13,
        filename="13-a13_gm-1150x700.jpg",
        title="SECTION A-A & B-B",
        width_px=1150,
        height_px=700,
        scale_px_per_ft=3.3950,
        scale_y_px_per_ft=3.3780,
        rot_deg=-0.100,
        origin_px=(425.50, 523.75),
        mode="section_aa",
    ),
    35: SheetCalibration(
        sheet_id=35,
        filename="35-s4_gm-1140x700.jpg",
        title="LEVEL THREE FRAMING & FOUNDATION PLAN",
        width_px=1140,
        height_px=700,
        scale_px_per_ft=3.3683,
        scale_y_px_per_ft=3.3560,
        rot_deg=-0.095,
        origin_px=(622.50, 419.50),
    ),
}


# =============================================================================
# 3. CONSTRUCTIVE FLOORPLATE, STAIR, CARREL & STACK GENERATORS (FEET)
# =============================================================================

def get_h_pier_polygons_ft(level: int = 3) -> list[list[tuple[float, float]]]:
    """
    Construct the 3 distinct irregular Perimeter H-Columns (`B` @ WP #5, `C` @ WP #6/#7, `D` @ WP #8/#9):
      - `level >= 2` (Levels 2, 3 & Roof): 12-vertex irregular H-polygon with radial splayed legs
        pointing directly to WP #3 ("TO W.P. #3" on Sheet 45-s14), stepped leg thickness (8" outer fin
        -> 1'-0" inner column leg), mitered outer tips flush with adjacent 47'-0" / 50'-11" faceted bays,
        and recessed 10" web strictly 90° perpendicular to the central structural Ray (B, C, D).
      - `level == 1` (Level 1 Foundation Base, Sheet 45-s14 bottom row): 8-vertex U-channel polygon
        flush with the recessed Level 1 concrete wall and +1'-6" inner leg extensions.
    """
    G = AaltoGeometry
    t_web = ft(0, 10)   # 10" recessed structural web
    t_out = ft(0, 9.5)  # 8" concrete fin + exterior veneer (~9.5" overall fin thickness)
    t_in = ft(1, 0)     # 1'-0" inner structural column leg
    polys: list[list[tuple[float, float]]] = []

    for hp in G.H_PIERS:
        wp_L, bay_L_other = hp["wp_L"], hp["bay_L_other"]
        wp_R, bay_R_other = hp["wp_R"], hp["bay_R_other"]

        # Exact outer leg tip corners along Left & Right bay facade lines
        p_L_tip_out = _step_along(wp_L, bay_L_other, hp["jamb_L"])
        p_R_tip_out = _step_along(wp_R, bay_R_other, hp["jamb_R"])

        # Each leg's outer face points radially straight to WP #3 (Sheet 45-s14)
        deg_L = math.degrees(math.atan2(p_L_tip_out[1] - G.WP3[1], p_L_tip_out[0] - G.WP3[0]))
        deg_R = math.degrees(math.atan2(p_R_tip_out[1] - G.WP3[1], p_R_tip_out[0] - G.WP3[0]))

        # Inner face of outer fins intersected with adjacent bay facade lines
        # For Left leg, inward toward H-Col web is clockwise (+t); for Right leg, inward is CCW (-t).
        p_L_tip_in = _line_intersect_2d(
            _local_leg_pt(p_L_tip_out, deg_L, -25.0, +t_out),
            _local_leg_pt(p_L_tip_out, deg_L, +10.0, +t_out),
            wp_L, bay_L_other,
        )
        p_R_tip_in = _line_intersect_2d(
            _local_leg_pt(p_R_tip_out, deg_R, -25.0, -t_out),
            _local_leg_pt(p_R_tip_out, deg_R, +10.0, -t_out),
            wp_R, bay_R_other,
        )

        # Recessed web: strictly 90° perpendicular to central Ray B/C/D at `web_depth` inward from wp_R
        ray_deg = hp["ray_deg"]
        w_out_ctr = polar_pt(wp_R, -hp["web_depth"], ray_deg)
        w_out_a = _local_leg_pt(w_out_ctr, ray_deg, 0.0, -15.0)
        w_out_b = _local_leg_pt(w_out_ctr, ray_deg, 0.0, +15.0)

        w_in_ctr = polar_pt(wp_R, -(hp["web_depth"] + t_web), ray_deg)
        w_in_a = _local_leg_pt(w_in_ctr, ray_deg, 0.0, -15.0)
        w_in_b = _local_leg_pt(w_in_ctr, ray_deg, 0.0, +15.0)

        p_wL_out = _line_intersect_2d(
            _local_leg_pt(p_L_tip_out, deg_L, -25.0, +t_out),
            _local_leg_pt(p_L_tip_out, deg_L, +10.0, +t_out),
            w_out_a, w_out_b,
        )
        p_wR_out = _line_intersect_2d(
            _local_leg_pt(p_R_tip_out, deg_R, -25.0, -t_out),
            _local_leg_pt(p_R_tip_out, deg_R, +10.0, -t_out),
            w_out_a, w_out_b,
        )
        p_wL_in = _line_intersect_2d(
            _local_leg_pt(p_L_tip_out, deg_L, -25.0, +t_in),
            _local_leg_pt(p_L_tip_out, deg_L, +10.0, +t_in),
            w_in_a, w_in_b,
        )
        p_wR_in = _line_intersect_2d(
            _local_leg_pt(p_R_tip_out, deg_R, -25.0, -t_in),
            _local_leg_pt(p_R_tip_out, deg_R, +10.0, -t_in),
            w_in_a, w_in_b,
        )

        extra_in = ft(1, 6) if level == 1 else 0.0
        len_L = hp["len_L"] + extra_in
        len_R = hp["len_R"] + extra_in
        p_L_bot_out = _local_leg_pt(p_L_tip_out, deg_L, -len_L, 0.0)
        p_L_bot_in = _local_leg_pt(p_L_tip_out, deg_L, -len_L, +t_in)
        p_R_bot_out = _local_leg_pt(p_R_tip_out, deg_R, -len_R, 0.0)
        p_R_bot_in = _local_leg_pt(p_R_tip_out, deg_R, -len_R, -t_in)

        if level == 1:
            p_uL_out = _line_intersect_2d(
                _local_leg_pt(p_L_tip_out, deg_L, -25.0, 0.0),
                _local_leg_pt(p_L_tip_out, deg_L, +10.0, 0.0),
                w_out_a, w_out_b,
            )
            p_uR_out = _line_intersect_2d(
                _local_leg_pt(p_R_tip_out, deg_R, -25.0, 0.0),
                _local_leg_pt(p_R_tip_out, deg_R, +10.0, 0.0),
                w_out_a, w_out_b,
            )
            polys.append([
                p_uL_out, p_uR_out,
                p_R_bot_out, p_R_bot_in, p_wR_in,
                p_wL_in, p_L_bot_in, p_L_bot_out,
            ])
        else:
            polys.append([
                p_L_tip_out, p_L_tip_in, p_wL_out,
                p_wR_out, p_R_tip_in, p_R_tip_out,
                p_R_bot_out, p_R_bot_in, p_wR_in,
                p_wL_in, p_L_bot_in, p_L_bot_out,
            ])
    return polys


def get_faceted_curtain_bays_ft() -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Return the 4 exact North Curtain-Wall segments (47'-0", 47'-0", 47'-0", 50'-11") terminating at H-Column fin tips."""
    G = AaltoGeometry
    pB, pC, pD = get_h_pier_polygons_ft(level=3)
    return [
        (G.PT_A, pB[0]),
        (pB[5], pC[0]),
        (pC[5], pD[0]),
        (pD[5], G.PT_E),
    ]


def get_north_perimeter_with_pockets_ft(level: int = 3) -> list[tuple[float, float]]:
    """
    Trace the exact North Faceted Perimeter from PT_A (WP #4) to PT_E (WP #10):
      - `level >= 2`: steps cleanly INWARD around each of the 3 H-Column exterior scupper pockets (B, C, D).
      - `level == 1`: traces the stepped-back Level 1 concrete foundation wall ("Outside face of concrete at level 1").
    """
    G = AaltoGeometry
    if level == 1:
        uB, uC, uD = get_h_pier_polygons_ft(level=1)
        bays_l3 = get_faceted_curtain_bays_ft()

        def _off_seg_right(a: tuple[float, float], b: tuple[float, float], d: float) -> tuple[tuple[float, float], tuple[float, float]]:
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            ix, iy = dy / L, -dx / L
            return (a[0] + d * ix, a[1] + d * iy), (b[0] + d * ix, b[1] + d * iy)

        def _dist_right(a: tuple[float, float], b: tuple[float, float], pt: tuple[float, float]) -> float:
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            ix, iy = dy / L, -dx / L
            return (pt[0] - a[0]) * ix + (pt[1] - a[1]) * iy

        d_b0 = _dist_right(bays_l3[0][0], bays_l3[0][1], uB[0])
        d_b3 = _dist_right(bays_l3[3][0], bays_l3[3][1], uD[1])
        w_a, w_b = _off_seg_right(G.PT_A_INNER_JUNC, G.PT_A, 2.80)
        b0_a, b0_b = _off_seg_right(bays_l3[0][0], bays_l3[0][1], d_b0)
        l1_pt_a = _line_intersect_2d(w_a, w_b, b0_a, b0_b)

        e_a, e_b = _off_seg_right(G.PT_E, G.PT_LOUNGE_JUNC, 3.20)
        b3_a, b3_b = _off_seg_right(bays_l3[3][0], bays_l3[3][1], d_b3)
        l1_pt_e = _line_intersect_2d(b3_a, b3_b, e_a, e_b)
        return [
            l1_pt_a,
            uB[0], uB[1],
            uC[0], uC[1],
            uD[0], uD[1],
            l1_pt_e,
        ]
    pB, pC, pD = get_h_pier_polygons_ft(level=3)
    return [
        G.PT_A,
        *pB[0:6],
        *pC[0:6],
        *pD[0:6],
        G.PT_E,
    ]


def get_level3_envelope_ft() -> list[tuple[float, float]]:
    """Complete exterior boundary polygon of Level 3 (with recessed North H-Column pockets)."""
    G = AaltoGeometry
    return [
        *get_north_perimeter_with_pockets_ft(level=3),
        G.PT_LOUNGE_JUNC,
        (G.X_LOUNGE_E, G.GRID_Y["5"]),   # Periodical Lounge SE corner (Grid 5)
        (G.X_AUD_E, G.GRID_Y["5"]),      # Rare Book / East Stair NE corner
        (G.X_AUD_E, G.GRID_Y["1"]),      # Rare Book & Auditorium SE corner (WP #1, Grid 1)
        (G.X_AUD_SW, G.GRID_Y["1"]),     # Rare Book SW corner (Grid 1)
        (G.X_LOBBY_E_G2, G.GRID_Y["2"]), # Canted Lobby / Rare Book junction (Grid 2)
        (G.X_SOUTH_STEP, G.GRID_Y["2"]), # Main South Entrance Facade SW corner (Grid 2)
        (G.X_SOUTH_STEP, G.GRID_Y["3"]), # Step up to Grid 3
        (G.X_WEST_WING, G.GRID_Y["3"]),  # West Cataloging Wing SW corner (Grid 3)
        (G.X_WEST_WING, G.GRID_Y["6"]),  # West Cataloging Wing NW corner (Grid 6)
        (G.X_ELEV_E, G.GRID_Y["6"]),     # Elevator / West Wing step North
        G.PT_A_INNER_JUNC,               # Junction with West Fan Throat on Ray A
    ]


def get_level2_envelope_ft() -> list[tuple[float, float]]:
    """Complete boundary polygon of Level 2 (with recessed North H-Column pockets)."""
    G = AaltoGeometry
    return [
        *get_north_perimeter_with_pockets_ft(level=2),
        G.PT_LOUNGE_JUNC,
        (G.X_LOUNGE_E, G.GRID_Y["5"]),   # Benedictina SE corner (Grid 5)
        (G.X_AUD_E, G.GRID_Y["5"]),      # Mechanical East step
        (G.X_AUD_E, G.GRID_Y["4"]),      # Mechanical SE corner (Grid 4)
        (G.X_SOUTH_STEP, G.GRID_Y["4"]), # Mechanical / Corridor SW line (Grid 4)
        (G.X_SOUTH_STEP, G.GRID_Y["3"]), # Bindery step
        (G.X_WEST_WING, G.GRID_Y["3"]),  # Receiving / Bindery SW corner (Grid 3)
        (G.X_WEST_WING, G.GRID_Y["6"]),  # Receiving / Bindery NW corner (Grid 6)
        (G.X_ELEV_E, G.GRID_Y["6"]),
        G.PT_A_INNER_JUNC,
    ]


def get_level1_envelope_ft() -> list[tuple[float, float]]:
    """Complete boundary polygon of Level 1 (stepped-back L1 concrete face + Pentagonal Core + Elevator/Stair #4)."""
    G = AaltoGeometry
    return [
        G.PT_A_INNER_JUNC,
        *get_north_perimeter_with_pockets_ft(level=1),
        (44.5, 25.0),                    # SE wall step at Stair #2
        G.WELL_COLS_FT["Well_4_ENE"],
        (10.8, 0.5),                     # Electronics room SE corner (Grid 6)
        G.WELL_COLS_FT["Well_W_South"],
        (-69.5, 10.2),                   # West corridor junction
        (-69.5, G.GRID_Y["4"]),          # Stair #4 SE corner
        (-85.5, G.GRID_Y["4"]),          # Stair #4 SW corner
        (-85.5, G.GRID_Y["5"]),          # Elevator pit
        (G.X_SOUTH_STEP, G.GRID_Y["5"]),
        (G.X_SOUTH_STEP, G.GRID_Y["6"]),
        (G.X_ELEV_E, G.GRID_Y["6"]),
    ]


def get_l1_inner_pentagon_ft() -> list[tuple[float, float]]:
    """Level 1 interior pentagonal reinforced-concrete retaining wall dividing stacks from electronics core."""
    G = AaltoGeometry
    return [
        G.WELL_COLS_FT["Well_W_South"],
        G.WELL_COLS_FT["Well_1_WNW"],
        G.WELL_COLS_FT["Well_2_NNW"],
        G.WELL_COLS_FT["Well_3_NNE"],
        G.WELL_COLS_FT["Well_4_ENE"],
    ]


def get_carrel_alcoves_ft() -> list[list[tuple[float, float]]]:
    """Perimeter study carrel partitions along the 4 Faceted Bays A-B, B-C, C-D, D-E."""
    boxes = []
    bays = get_faceted_curtain_bays_ft()
    for b_idx, (p0, p1) in enumerate(bays):
        n_carrels = 5
        vx, vy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(vx, vy)
        ux, uy = vx / L, vy / L
        # Inward normal (pointing South/toward fan center: rotate clockwise 90 deg -> (uy, -ux))
        nx, ny = uy, -ux
        margin_s = 4.8 if b_idx == 0 else 1.8
        margin_e = 6.6 if b_idx == len(bays) - 1 else 1.8
        usable = L - margin_s - margin_e
        cw = usable / n_carrels
        depth = 5.6
        for i in range(n_carrels):
            s0 = margin_s + i * cw + 0.55
            s1 = margin_s + (i + 1) * cw - 0.55
            q0 = (p0[0] + ux * s0 + nx * 1.15, p0[1] + uy * s0 + ny * 1.15)
            q1 = (p0[0] + ux * s1 + nx * 1.15, p0[1] + uy * s1 + ny * 1.15)
            q2 = (q1[0] + nx * depth, q1[1] + ny * depth)
            q3 = (q0[0] + nx * depth, q0[1] + ny * depth)
            boxes.append([q0, q1, q2, q3])
    return boxes


def get_radial_bookstacks_ft(r_start: float = 50.5, r_end: float = 70.5) -> list[list[tuple[float, float]]]:
    """Generate radiating double-faced Aalto bookstack ranges flanking true Rays B (137.0°), C (99.4°), D (64.5°)."""
    G = AaltoGeometry
    # Angles from WP #3A chosen to sit cleanly between paired columns & rays with >=2.5 ft clearance
    stack_angles = [
        159.0, 153.2, 147.8,
        132.5, 126.6, 120.8, 115.0, 109.2,
        93.4, 86.4, 79.4, 72.4,
        56.5, 50.5, 44.5,
    ]
    half_thick = 1.35  # 32" double-faced stack width
    stacks = []
    for deg in stack_angles:
        rad = math.radians(deg)
        ux, uy = math.cos(rad), math.sin(rad)
        px, py = -uy * half_thick, ux * half_thick
        cx, cy = G.WP3A
        p0 = (cx + r_start * ux - px, cy + r_start * uy - py)
        p1 = (cx + r_end * ux - px, cy + r_end * uy - py)
        p2 = (cx + r_end * ux + px, cy + r_end * uy + py)
        p3 = (cx + r_start * ux + px, cy + r_start * uy + py)
        stacks.append([p0, p1, p2, p3])
    return stacks


def get_well_stairs_ft() -> list[list[tuple[float, float]]]:
    """West and East radial U-turn switchback stairs connecting Level 3, -5'-4" Mezzanine (10R), and Level 2 (16R)."""
    G = AaltoGeometry
    stairs = []
    for ang_up, ang_dn in ((45.4, 52.2), (158.1, 151.3)):
        for ang_c, r0, r1 in ((ang_up, 32.2, 44.0), (ang_dn, 32.2, 45.2)):
            rad = math.radians(ang_c)
            ux, uy = math.cos(rad), math.sin(rad)
            nx, ny = -uy, ux
            hw = 1.82
            cx, cy = G.WP3A
            stairs.append([
                (cx + r0 * ux - hw * nx, cy + r0 * uy - hw * ny),
                (cx + r1 * ux - hw * nx, cy + r1 * uy - hw * ny),
                (cx + r1 * ux + hw * nx, cy + r1 * uy + hw * ny),
                (cx + r0 * ux + hw * nx, cy + r0 * uy + hw * ny),
            ])
    # Also Stair #2 along SE diagonal wall (parallel to PT_LOUNGE_JUNC -> PT_E inside exterior wall)
    dx_e = G.PT_E[0] - G.PT_LOUNGE_JUNC[0]
    dy_e = G.PT_E[1] - G.PT_LOUNGE_JUNC[1]
    L_e = math.hypot(dx_e, dy_e)
    uxe, uye = dx_e / L_e, dy_e / L_e
    nxe, nye = -uye, uxe
    bx = G.PT_LOUNGE_JUNC[0] + 15.0 * uxe + 1.25 * nxe
    by = G.PT_LOUNGE_JUNC[1] + 15.0 * uye + 1.25 * nye
    stairs.append([
        (bx, by),
        (bx + 19.5 * uxe, by + 19.5 * uye),
        (bx + 19.5 * uxe + 5.8 * nxe, by + 19.5 * uye + 5.8 * nye),
        (bx + 5.8 * nxe, by + 5.8 * nye),
    ])
    return stairs


# =============================================================================
# 4. MULTI-LAYER SVG BUILDER (COLLEGE GEOMETRY STYLE)
# =============================================================================

class SvgOverlayBuilder:
    """Builds clean, semantic-layered SVG vector overlays matching exact bitmap dimensions."""

    def __init__(self, width: int, height: int, w2p: Callable[[float, float], tuple[float, float]]):
        self.width = width
        self.height = height
        self.w2p = w2p
        self.layers: dict[str, list[str]] = {
            "regulating": [],
            "structure": [],
            "walls": [],
            "stairs_millwork": [],
            "roof_skylights": [],
        }

    def add_line(self, layer: str, p0: tuple[float, float], p1: tuple[float, float], stroke: str, width: float = 1.6, dash: str = ""):
        x0, y0 = self.w2p(*p0)
        x1, y1 = self.w2p(*p1)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.layers[layer].append(
            f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{stroke}" stroke-width="{width}"{da} stroke-linecap="round"/>'
        )

    def add_polyline(self, layer: str, pts: list[tuple[float, float]], stroke: str, width: float = 1.8, closed: bool = False, fill: str = "none", fill_opacity: float = 0.0, dash: str = ""):
        p_px = [self.w2p(x, y) for x, y in pts]
        pts_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in p_px)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        fo = f' fill-opacity="{fill_opacity:.2f}"' if fill != "none" else ""
        tag = "polygon" if closed else "polyline"
        self.layers[layer].append(
            f'<{tag} points="{pts_str}" fill="{fill}"{fo} stroke="{stroke}" stroke-width="{width}"{da} stroke-linejoin="round"/>'
        )

    def add_circle_world(self, layer: str, center: tuple[float, float], r_ft: float, scale_px: float, stroke: str, width: float = 1.8, fill: str = "none", fill_opacity: float = 0.0, dash: str = ""):
        cx, cy = self.w2p(*center)
        r_px = r_ft * scale_px
        da = f' stroke-dasharray="{dash}"' if dash else ""
        fo = f' fill-opacity="{fill_opacity:.2f}"' if fill != "none" else ""
        self.layers[layer].append(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_px:.2f}" fill="{fill}"{fo} stroke="{stroke}" stroke-width="{width}"{da}/>'
        )

    def add_label(self, layer: str, pt: tuple[float, float], text: str, color: str = "#00e5ff", size: int = 11, dx: float = 5.0, dy: float = -5.0):
        px, py = self.w2p(*pt)
        esc = text.replace("&", "&amp;").replace("<", "&lt;")
        self.layers[layer].append(
            f'<text x="{px + dx:.2f}" y="{py + dy:.2f}" fill="{color}" font-family="Inter, monospace, sans-serif" font-size="{size}" font-weight="700" paint-order="stroke" stroke="#0b0f17" stroke-width="3" stroke-linejoin="round">{esc}</text>'
        )

    def to_svg(self) -> str:
        out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}" class="aalto-vector-svg">',
        ]
        for layer_name, elems in self.layers.items():
            if elems:
                out.append(f'  <g class="vec-layer" data-layer="{layer_name}">')
                for el in elems:
                    out.append(f"    {el}")
                out.append("  </g>")
        out.append("</svg>")
        return "\n".join(out)


def _add_common_regulating_and_structure(svg: SvgOverlayBuilder, cal: SheetCalibration, include_south_cols: bool = True):
    G = AaltoGeometry
    sc = cal.scale_px_per_ft

    # 1. Orthogonal Grid Lines 1..6
    for g_num, gy in G.GRID_Y.items():
        if cal.sheet_id == 6 and gy < -2.0:
            continue
        svg.add_line("regulating", (-136.0, gy), (100.0, gy), "#38bdf8", width=1.1, dash="6,5")
        if cal.sheet_id != 6:
            svg.add_label("regulating", (-135.0, gy), f"GRID ({g_num}) Y={gy:+.1f}'", "#38bdf8", size=10, dx=2, dy=-4)

    # 2. Polycentric Structural Rays B, C, D from WP #3 (0'-0", 0'-0")
    for label, deg, r_max in [
        (f"AXIS B ({G.RAY_B_DEG:.1f}°)", G.RAY_B_DEG, 94.0),
        (f"AXIS C ({G.RAY_C_DEG:.1f}°)", G.RAY_C_DEG, 96.0),
        (f"AXIS D ({G.RAY_D_DEG:.1f}°)", G.RAY_D_DEG, 105.0),
    ]:
        p_end = polar_pt(G.WP3, r_max, deg)
        svg.add_line("regulating", G.WP3, p_end, "#00e5ff", width=1.8, dash="8,4")
        svg.add_label("regulating", polar_pt(G.WP3, r_max - 5.0, deg), label, "#00e5ff", size=10)

    # 3. Outer Boundary Rays A & E from Lower Hub WP #2 (+2'-10", -5'-3")
    svg.add_line("regulating", G.WP3, G.WP2, "#f59e0b", width=1.5, dash="3,3")
    for label, deg, r_max in [
        (f"AXIS A ({G.RAY_A_DEG:.1f}°)", G.RAY_A_DEG, 98.0),
        (f"AXIS E ({G.RAY_E_DEG:.1f}°)", G.RAY_E_DEG, 126.0),
    ]:
        p_end = polar_pt(G.WP2, r_max, deg)
        svg.add_line("regulating", G.WP2, p_end, "#fb923c", width=1.8, dash="7,4")
        svg.add_label("regulating", polar_pt(G.WP2, r_max - 9.0, deg), label, "#fb923c", size=10)

    # 4. Concentric Regulating Arcs (R = 31'-10" Well Wall centered at WP #3A on Ray D)
    svg.add_polyline("regulating", arc_pts(G.WP3A, G.R_WELL_L2_WALL, 36.0, 165.0, 44), "#a855f7", width=1.5, dash="5,4")
    svg.add_label("regulating", polar_pt(G.WP3A, G.R_WELL_L2_WALL, 80.0), "R = 31'-10\"", "#c084fc", size=10)

    # Working Point Markers
    for wp_name, wp_pt, col in [
        ("WP #3 (0,0)", G.WP3, "#00e5ff"),
        ("WP #2", G.WP2, "#fb923c"),
        ("WP #3A", G.WP3A, "#c084fc"),
    ]:
        svg.add_circle_world("regulating", wp_pt, 10.0 / sc * 0.42, sc, col, width=2.0, fill=col, fill_opacity=0.35)
        svg.add_label("regulating", wp_pt, wp_name, col, size=10, dx=6, dy=-4)

    # 5. Structural Columns & Distinct Irregular Perimeter H-Columns (U-channels at Level 1)
    hp_level = 1 if cal.sheet_id == 3 else 3
    for hp_poly in get_h_pier_polygons_ft(level=hp_level):
        svg.add_polyline("structure", hp_poly, "#ef4444", width=2.0, closed=True, fill="#ef4444", fill_opacity=0.32)

    for c_name, cpt in {**G.WELL_COLS_FT, **G.PAIRED_COLS_FT}.items():
        if cal.sheet_id == 3 and c_name in ("South_W1",):
            continue
        svg.add_circle_world("structure", cpt, 0.85, sc, "#f43f5e", width=2.0, fill="#f43f5e", fill_opacity=0.45)

    if include_south_cols and cal.sheet_id != 6:
        for cpt in G.SOUTH_WING_COLS_FT:
            if cal.sheet_id == 3 and cpt[1] < -22.0:
                continue
            svg.add_circle_world("structure", cpt, 0.70, sc, "#fb7185", width=1.6, fill="#fb7185", fill_opacity=0.35)


def build_sheet_svg(sheet_id: int) -> str:
    """Generate the complete multi-layer SVG vector overlay for `sheet_id`."""
    cal = CALIBRATED_SHEETS[sheet_id]
    G = AaltoGeometry
    svg = SvgOverlayBuilder(cal.width_px, cal.height_px, cal.world_to_px)
    sc = cal.scale_px_per_ft

    if sheet_id == 6:
        # Drawing 06: Basic Plan Layout (1/8" = 1'-0" master constructive H-Column & Twin-Column key)
        _add_common_regulating_and_structure(svg, cal, include_south_cols=False)
        # Dashed Level 1 U-channel inner leg extensions (+1'-6") & stepped-back Level 1 concrete line
        for u_poly in get_h_pier_polygons_ft(level=1):
            svg.add_polyline("structure", u_poly, "#fda4af", width=1.4, closed=True, dash="4,3")
        svg.add_polyline("walls", get_north_perimeter_with_pockets_ft(level=1), "#34d399", width=1.5, dash="6,4")
        # Outer faceted brick bays A-B, B-C, C-D, D-E stepping into H-Column scupper pockets
        svg.add_polyline("walls", [G.PT_A_INNER_JUNC, *get_north_perimeter_with_pockets_ft(level=3), G.PT_LOUNGE_JUNC], "#10b981", width=2.6)
        # Level 1 pentagonal concrete retaining wall
        svg.add_polyline("walls", get_l1_inner_pentagon_ft(), "#22c55e", width=2.4)
        # Perimeter WP markers (#4..#9 visible on Sheet 06)
        for wp_lbl, wp_pt in [("WP #4", G.WP4), ("WP #5", G.WP5), ("WP #6", G.WP6), ("WP #7", G.WP7), ("WP #8", G.WP8), ("WP #9", G.WP9)]:
            svg.add_circle_world("regulating", wp_pt, 0.55, sc, "#fde047", width=1.8, fill="#fde047", fill_opacity=0.4)
            svg.add_label("regulating", wp_pt, wp_lbl, "#fde047", size=9, dx=6, dy=-4)
        # Callouts for Paired Twin Columns & the 3 distinct irregular H-Columns
        svg.add_label("structure", G.PAIRED_COLS_FT["Pair_B_R"], "PAIRED 18\"Ø COLS (5'-4\" c/c)", "#fda4af", size=10, dx=8, dy=-6)
        for hp, hp_poly in zip(G.H_PIERS, get_h_pier_polygons_ft(level=3)):
            svg.add_label("structure", hp_poly[5], hp["label"], "#fecdd3", size=10, dx=6, dy=-6)

    elif sheet_id == 5:
        # Drawing 05: Floor Plan Level #3
        _add_common_regulating_and_structure(svg, cal)
        svg.add_polyline("walls", get_level3_envelope_ft(), "#10b981", width=2.5, closed=True, fill="#10b981", fill_opacity=0.05)
        # South Entry Canopy
        svg.add_polyline("roof_skylights", [(-18.5, G.GRID_Y["2"]), (8.5, G.GRID_Y["2"]), (8.5, -66.5), (-18.5, -66.5)], "#f59e0b", width=2.0, closed=True, dash="5,3")
        svg.add_label("roof_skylights", (-17.5, -65.5), "ENTRY CANOPY", "#fbbf24", size=9, dx=2, dy=11)
        # Level 3 Mezzanine Opening, Continuous Reading Counter & Radial Stairwell Bookcases
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_MEZZ_OPENING, 47.9, 155.4, 40), "#facc15", width=2.2)
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_MEZZ_DESK, 47.9, 155.4, 40), "#eab308", width=1.6)
        svg.add_label("stairs_millwork", polar_pt(G.WP3A, G.R_MEZZ_DESK, 99.0), "L3 WORKBENCH (STOOLS + LAMPS)", "#fde047", size=9, dx=-64, dy=-6)
        for st_deg, r_sgn in ((41.8, -1.0), (161.5, +1.0)):
            s_rad = math.radians(st_deg)
            urx, ury = math.cos(s_rad), math.sin(s_rad)
            tx, ty = r_sgn * (-ury), r_sgn * urx
            cx0, cy0 = G.WP3A
            bk_poly = [
                (cx0 + G.R_GALLERY_RAIL * urx, cy0 + G.R_GALLERY_RAIL * ury),
                (cx0 + G.R_MEZZ_OPENING * urx, cy0 + G.R_MEZZ_OPENING * ury),
                (cx0 + G.R_MEZZ_OPENING * urx + 1.55 * tx, cy0 + G.R_MEZZ_OPENING * ury + 1.55 * ty),
                (cx0 + G.R_GALLERY_RAIL * urx + 1.55 * tx, cy0 + G.R_GALLERY_RAIL * ury + 1.55 * ty),
            ]
            svg.add_polyline("stairs_millwork", bk_poly, "#fde047", width=2.0, closed=True, fill="#facc15", fill_opacity=0.28)
        svg.add_label("stairs_millwork", polar_pt(G.WP3A, 34.0, 39.0), "COUNTER-HT. BOOKCASE", "#fde047", size=8, dx=4, dy=4)
        # -5'-4" Mezzanine below: Outer-Arc Workbench (R = 29.4..31.83') & Inner Reference Bookwall (R = 22'-0")
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_WELL_L2_WALL, 55.8, 147.8, 36), "#fde047", width=1.9)
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, 29.42, 55.8, 147.8, 36), "#fbbf24", width=1.4, dash="4,2")
        svg.add_label("stairs_millwork", polar_pt(G.WP3A, 29.42, 100.0), "MEZZ. WORKBENCH (-5'-4\")", "#fde047", size=8, dx=-68, dy=11)
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_GALLERY_RAIL, 42.1, 161.2, 32), "#38bdf8", width=1.6, dash="4,3")
        svg.add_polyline("stairs_millwork", arc_pts(G.WP_DESK, G.R_DESK_OUTER, 25.0, 165.0, 32), "#f97316", width=2.2)
        svg.add_polyline("stairs_millwork", arc_pts(G.WP_DESK, G.R_DESK_INNER, 25.0, 165.0, 32), "#f97316", width=1.6)
        # Carrels, Stairs & Radial Bookstacks
        for box in get_carrel_alcoves_ft():
            svg.add_polyline("walls", box, "#34d399", width=1.2, closed=True)
        for st in get_well_stairs_ft():
            svg.add_polyline("stairs_millwork", st, "#fbbf24", width=1.8, closed=True, fill="#fbbf24", fill_opacity=0.14)
        for stk in get_radial_bookstacks_ft(51.5, 70.5):
            svg.add_polyline("stairs_millwork", stk, "#a3e635", width=1.1, closed=True, fill="#a3e635", fill_opacity=0.12)
        # Eye-Level Square Mt. Hood Window in H-Column D Alcove (Ray D = 64.5° ENE)
        hp_d = get_h_pier_polygons_ft(level=3)[2]
        w_a = (hp_d[2][0] + 0.21 * (hp_d[3][0] - hp_d[2][0]), hp_d[2][1] + 0.21 * (hp_d[3][1] - hp_d[2][1]))
        w_b = (hp_d[2][0] + 0.79 * (hp_d[3][0] - hp_d[2][0]), hp_d[2][1] + 0.79 * (hp_d[3][1] - hp_d[2][1]))
        svg.add_line("walls", w_a, w_b, "#38bdf8", width=3.2)
        svg.add_label("walls", hp_d[3], "EYE-LEVEL MT. HOOD WINDOW", "#7dd3fc", size=8, dx=6, dy=-4)
        svg.add_label("walls", (G.X_LOUNGE_E + 0.8, 16.0), "MT. HOOD PICTURE WINDOW", "#6ee7b7", size=9, dx=4, dy=0)

    elif sheet_id == 4:
        # Drawing 04: Floor Plan Level #2
        _add_common_regulating_and_structure(svg, cal)
        svg.add_polyline("walls", get_level2_envelope_ft(), "#10b981", width=2.5, closed=True, fill="#10b981", fill_opacity=0.05)
        # L2 Curved Core Wall (R = 31'-10") & Mezzanine inner wall above (R = 22'-0")
        svg.add_polyline("walls", arc_pts(G.WP3A, G.R_WELL_L2_WALL, 42.0, 161.0, 38), "#10b981", width=2.2)
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_GALLERY_RAIL, 45.0, 158.0, 32), "#f97316", width=1.6, dash="4,3")
        for box in get_carrel_alcoves_ft():
            svg.add_polyline("walls", box, "#34d399", width=1.3, closed=True, fill="#34d399", fill_opacity=0.08)
        for st in get_well_stairs_ft():
            svg.add_polyline("stairs_millwork", st, "#fbbf24", width=1.8, closed=True, fill="#fbbf24", fill_opacity=0.14)
        for stk in get_radial_bookstacks_ft(34.5, 48.0)[2:13]:
            svg.add_polyline("stairs_millwork", stk, "#a3e635", width=1.0, closed=True, fill="#a3e635", fill_opacity=0.12)
        for stk in get_radial_bookstacks_ft(51.8, 70.0):
            svg.add_polyline("stairs_millwork", stk, "#a3e635", width=1.0, closed=True, fill="#a3e635", fill_opacity=0.10)

    elif sheet_id == 3:
        # Drawing 03: Floor Plan Level #1
        _add_common_regulating_and_structure(svg, cal)
        svg.add_polyline("walls", get_level1_envelope_ft(), "#10b981", width=2.5, closed=True, fill="#10b981", fill_opacity=0.06)
        svg.add_polyline("walls", get_l1_inner_pentagon_ft(), "#22c55e", width=2.4)
        for stk in get_radial_bookstacks_ft(38.0, 72.5):
            svg.add_polyline("stairs_millwork", stk, "#a3e635", width=1.0, closed=True, fill="#a3e635", fill_opacity=0.10)

    elif sheet_id == 7:
        # Drawing 07: Roof Plan & Skylights
        _add_common_regulating_and_structure(svg, cal, include_south_cols=False)
        svg.add_polyline("walls", get_level3_envelope_ft(), "#10b981", width=2.2, closed=True)
        # Curved Copper/Plaster Scoop Band (R = 25'-10"..34'-6")
        scoop_in = arc_pts(G.WP3A, G.R_SCOOP_INNER, 46.0, 155.0, 40)
        scoop_ridge = arc_pts(G.WP3A, G.R_SCOOP_RIDGE, 46.0, 155.0, 40)
        scoop_out = arc_pts(G.WP3A, G.R_SCOOP_OUTER, 46.0, 155.0, 40)
        svg.add_polyline("roof_skylights", scoop_in + list(reversed(scoop_ridge)), "#f59e0b", width=2.0, closed=True, fill="#f59e0b", fill_opacity=0.16)
        # North-Facing Sloped Skylight Glazing Band (R = 34'-6"..41'-2")
        svg.add_polyline("roof_skylights", scoop_ridge + list(reversed(scoop_out)), "#38bdf8", width=2.2, closed=True, fill="#38bdf8", fill_opacity=0.22)
        # Skylight radial mullions across North glass
        for m_deg in range(48, 156, 8):
            svg.add_line("roof_skylights", polar_pt(G.WP3A, G.R_SCOOP_RIDGE, m_deg), polar_pt(G.WP3A, G.R_SCOOP_OUTER, m_deg), "#fde047", width=1.2)
        svg.add_label("roof_skylights", polar_pt(G.WP3A, G.R_SCOOP_OUTER + 2.5, 99.0), "CURVED NORTH DAYLIGHT SCOOP", "#fde047", size=10, dx=-70, dy=-4)
        # 14 Conical Dome Skylights on Lower South Wing Roof (Sheets 07-a7 & 10-a10)
        for sx, sy, sr in G.CONICAL_SKYLIGHTS:
            svg.add_circle_world("roof_skylights", (sx, sy), sr, sc, "#facc15", width=2.2, fill="#fde047", fill_opacity=0.32)
        # 3 Outer-Fan Rooftop Exhaust Fans alongside Radial Beams B, C, D (Sheets 07-a7 & 36-s5)
        for fx, fy, fr in G.FAN_ROOF_EXHAUST_FANS:
            svg.add_circle_world("roof_skylights", (fx, fy), fr, sc, "#38bdf8", width=2.0, fill="#38bdf8", fill_opacity=0.28)
        svg.add_label("roof_skylights", G.FAN_ROOF_EXHAUST_FANS[1][:2], "EXHAUST FANS (3x)", "#7dd3fc", size=9, dx=10, dy=-2)

    elif sheet_id == 35:
        # Drawing 35-s4: Level 3 Structural Framing Plan
        _add_common_regulating_and_structure(svg, cal)
        svg.add_polyline("walls", get_level3_envelope_ft(), "#10b981", width=1.8, closed=True)
        # Radial structural steel/concrete beams between R = 32' and outer perimeter from WP #3
        for b_deg in range(44, 166, 6):
            svg.add_line("structure", polar_pt(G.WP3, 33.5, b_deg), polar_pt(G.WP3, 86.0, b_deg), "#fb7185", width=1.0, dash="3,2")
        svg.add_polyline("structure", arc_pts(G.WP3A, 59.0, 42.0, 162.0, 40), "#f43f5e", width=2.0)

    elif sheet_id == 13:
        # Drawing 13-a13: Section A-A (Horizontal = S_ft North of Grid 6; Vertical = Z_ft above Level 3)
        # Section A-A cuts N-S at X ≈ -8' (through Lobby Vestibule, Control Area, Mezzanine, and Bay 3 North Wall at S = +88'-2")
        s_north = 88.2
        s_south = G.GRID_Y["2"]  # -51'-8"
        elevs = [
            ("UPPER LOBBY (+1'-4\" / EL. 129'-10\")", G.Z_LOBBY_FT, s_south, 0.0, "#38bdf8", -6.0),
            ("LEVEL #3 FAN (0'-0\" / EL. 128'-6\")", G.Z_L3_FT, -2.0, s_north, "#00e5ff", +7.0),
            ("MEZZANINE (-5'-4\" / EL. 123'-2\")", G.Z_REF_GALLERY_FT, 0.0, 35.5, "#a855f7", +3.0),
            ("LEVEL #2 (-14'-0\" / EL. 114'-6\")", G.Z_L2_FT, G.GRID_Y["4"], s_north, "#22c55e", +3.0),
            ("LEVEL #1 (-28'-6\" / EL. 100'-0\")", G.Z_L1_FT, 35.0, s_north, "#10b981", +3.0),
        ]
        for lbl, zf, s0, s1, col, dy_off in elevs:
            svg.add_line("regulating", (s0, zf), (s_north + 4.0, zf), col, width=1.5, dash="6,4")
            svg.add_label("regulating", (s_north + 5.0, zf), lbl, col, size=10, dx=4, dy=dy_off)

        # Floor slabs & structural walls in Section A-A (WP3A is +3.39' N of Grid 6 along cut)
        s_gal_in = G.WP3A[1] + G.R_GALLERY_RAIL      # ~+25.4' N of Grid 6
        s_gal_out = G.WP3A[1] + G.R_WELL_L2_WALL     # ~+35.2' N of Grid 6
        s_well_open = G.WP3A[1] + G.R_MEZZ_OPENING   # ~+47.4' N of Grid 6
        svg.add_polyline("walls", [(-74.0, G.Z_CANOPY_FT), (s_south, G.Z_CANOPY_FT)], "#f59e0b", width=2.6)
        svg.add_polyline("walls", [(s_south, G.Z_LOBBY_FT), (-3.0, G.Z_LOBBY_FT), (0.0, G.Z_L3_FT), (s_gal_in, G.Z_L3_FT)], "#10b981", width=2.6)
        svg.add_polyline("walls", [(s_well_open, G.Z_L3_FT), (s_north, G.Z_L3_FT)], "#10b981", width=2.8)
        svg.add_polyline("stairs_millwork", [(s_well_open, G.Z_L3_FT), (s_well_open, G.Z_L3_FT + 3.0)], "#facc15", width=2.8)
        svg.add_polyline("stairs_millwork", [(s_gal_in, G.Z_L3_FT), (s_gal_in, G.Z_REF_GALLERY_FT), (s_gal_out, G.Z_REF_GALLERY_FT), (s_gal_out, G.Z_REF_GALLERY_FT + 2.8)], "#c084fc", width=2.4)
        svg.add_polyline("walls", [(G.GRID_Y["4"], G.Z_L2_FT), (s_north, G.Z_L2_FT)], "#10b981", width=2.6)
        svg.add_polyline("walls", [(s_gal_out, G.Z_L1_FT), (s_north, G.Z_L1_FT)], "#10b981", width=2.6)
        svg.add_line("walls", (s_north, G.Z_CRAWL_FT), (s_north, G.Z_FAN_PARAPET_N_FT), "#10b981", width=2.8)
        svg.add_line("walls", (s_gal_out, G.Z_CRAWL_FT), (s_gal_out, G.Z_L2_FT), "#10b981", width=2.4)

        # Roof, Conical Lanterns, Curved Daylight Scoop & Thick 24WF68 Fan Roof Plenum
        s_scoop_in = G.WP3A[1] + G.R_SCOOP_INNER     # ~+29.2'
        s_scoop_ridge = G.WP3A[1] + G.R_SCOOP_RIDGE  # ~+37.9'
        s_scoop_out = G.WP3A[1] + G.R_SCOOP_OUTER    # ~+44.5'
        svg.add_polyline(
            "roof_skylights",
            [
                (s_south, G.Z_SOUTH_ROOF_FT),
                (s_gal_in, G.Z_SOUTH_ROOF_FT),
                (s_scoop_ridge, G.Z_SCOOP_RIDGE_FT),
                (s_scoop_out, G.Z_FAN_ROOF_LOW_FT),
                (s_north, G.Z_FAN_ROOF_HIGH_FT),
                (s_north, G.Z_FAN_PARAPET_N_FT),
            ],
            "#facc15",
            width=2.6,
        )
        # Deep Fan Roof Structural Soffit (+11'-4" over stacks, splayed skylight coffer & upward North soffit)
        svg.add_polyline(
            "roof_skylights",
            [
                (s_scoop_out, G.Z_FAN_ROOF_LOW_FT),
                (s_scoop_out + 3.0, G.Z_FAN_CEIL_FT),
                (67.5, G.Z_FAN_CEIL_FT),
                (s_north - 0.8, 16.2),
            ],
            "#38bdf8",
            width=2.0,
            dash="5,3",
        )
        # Concave white plaster reflector vault (R = 7'-8") inside the North Light Scoop
        svg.add_polyline(
            "roof_skylights",
            [(s_scoop_in, G.Z_FAN_CEIL_FT), (s_scoop_in + 1.8, 16.0), (s_scoop_in + 4.8, 19.2), (s_scoop_ridge, G.Z_SCOOP_RIDGE_FT)],
            "#38bdf8",
            width=2.0,
            dash="4,2",
        )
        # Conical skylight throats visible in Section A-A
        for s_cone in (-22.5, -10.8, 11.8):
            svg.add_polyline(
                "roof_skylights",
                [(s_cone - 3.2, G.Z_SOUTH_CEIL_FT), (s_cone - 2.1, G.Z_LANTERN_TOP_FT), (s_cone + 2.1, G.Z_LANTERN_TOP_FT), (s_cone + 3.2, G.Z_SOUTH_CEIL_FT)],
                "#f59e0b",
                width=1.8,
            )
        # Abbey Hillside Grade Profile (sloping from South Plaza +1.3' down to North Toe -38')
        svg.add_polyline(
            "regulating",
            [(-76.0, 1.0), (s_south, 1.2), (-44.0, 0.4), (G.GRID_Y["4"], -14.5), (0.0, -17.5), (s_gal_out, -29.0), (68.0, -34.5), (s_north, -32.0), (108.0, -40.0)],
            "#a3e635",
            width=2.0,
            dash="8,4",
        )
        svg.add_label("roof_skylights", (s_scoop_ridge - 2.0, G.Z_SCOOP_RIDGE_FT + 1.5), "NORTH LIGHT SCOOP (+21'-4\")", "#fde047", size=10, dx=-25, dy=-4)

    return svg.to_svg()


def export_all_overlays(repo_root: Path, proof_dir: Path | None = None) -> dict:
    """Export all calibrated SVG overlays, manifest.json, and optional PNG bitmap+vector proof sheets."""
    overlays_dir = repo_root / "docs" / "overlays"
    overlays_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "origin_description": "Working Point #3 (convergence of Rays B, C, D on Grid Line 6) at Level 3 Finished Floor (EL. +128'-6\")",
        "units": "feet (canonical) / metres (IngeTrazo 3D)",
        "layers": [
            {"id": "regulating", "label": "Regulating Grid & Rays", "color": "#00e5ff"},
            {"id": "structure", "label": "Columns & H-Piers", "color": "#f43f5e"},
            {"id": "walls", "label": "Walls, Slabs & Carrels", "color": "#10b981"},
            {"id": "stairs_millwork", "label": "Well, Stairs & Bookstacks", "color": "#facc15"},
            {"id": "roof_skylights", "label": "Roof, Scoop & Skylights", "color": "#f59e0b"},
        ],
        "sheets": {},
    }

    for sid, cal in CALIBRATED_SHEETS.items():
        svg_text = build_sheet_svg(sid)
        svg_name = f"sheet_{sid:02d}.svg"
        (overlays_dir / svg_name).write_text(svg_text, encoding="utf-8")
        manifest["sheets"][str(sid)] = {
            "sheet_id": sid,
            "filename": cal.filename,
            "title": cal.title,
            "svg": f"overlays/{svg_name}",
            "scale_px_per_ft": cal.scale_px_per_ft,
            "scale_y_px_per_ft": cal.scale_y_px_per_ft,
            "rot_deg": cal.rot_deg,
            "origin_px": list(cal.origin_px),
            "mode": cal.mode,
        }

    (overlays_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if proof_dir is not None:
        _render_proof_composites(repo_root, proof_dir)

    return manifest


def _render_proof_composites(repo_root: Path, proof_dir: Path):
    """Render crisp darkened-blueprint + bright-vector PNG composites for visual verification."""
    import xml.etree.ElementTree as ET
    import numpy as np
    from PIL import Image, ImageDraw, ImageOps

    proof_dir.mkdir(parents=True, exist_ok=True)
    drawings_dir = repo_root / "docs" / "drawings"
    overlays_dir = repo_root / "docs" / "overlays"

    def hex_rgba(h: str, alpha: int = 235) -> tuple[int, int, int, int]:
        h = h.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)

    for sid, cal in CALIBRATED_SHEETS.items():
        # Dark-mode blueprint background (inverted dark slate blueprint so neon vectors pop!)
        raw = Image.open(drawings_dir / cal.filename).convert("L")
        raw = ImageOps.autocontrast(raw, cutoff=1)
        inv = ImageOps.invert(raw)
        arr = np.asarray(inv, dtype=np.float32) / 255.0
        rgb = np.zeros((cal.height_px, cal.width_px, 3), dtype=np.uint8)
        rgb[..., 0] = np.clip(14 + arr * 165, 0, 255).astype(np.uint8)
        rgb[..., 1] = np.clip(20 + arr * 175, 0, 255).astype(np.uint8)
        rgb[..., 2] = np.clip(34 + arr * 190, 0, 255).astype(np.uint8)
        canvas = Image.fromarray(rgb, "RGB")
        draw = ImageDraw.Draw(canvas, "RGBA")

        root = ET.fromstring((overlays_dir / f"sheet_{sid:02d}.svg").read_text(encoding="utf-8"))
        for elem in root.iter():
            tag = elem.tag.split("}")[-1]
            if tag == "line":
                p0 = (float(elem.attrib["x1"]), float(elem.attrib["y1"]))
                p1 = (float(elem.attrib["x2"]), float(elem.attrib["y2"]))
                col = hex_rgba(elem.attrib.get("stroke", "#00e5ff"), 220)
                w = max(1, int(round(float(elem.attrib.get("stroke-width", "1.5")))))
                draw.line([p0, p1], fill=col, width=w)
            elif tag in ("polyline", "polygon"):
                pts = [tuple(map(float, pair.split(","))) for pair in elem.attrib["points"].split()]
                fill_s = elem.attrib.get("fill", "none")
                if fill_s != "none" and tag == "polygon":
                    fop = int(float(elem.attrib.get("fill-opacity", "0.2")) * 255)
                    draw.polygon(pts, fill=hex_rgba(fill_s, fop))
                col = hex_rgba(elem.attrib.get("stroke", "#10b981"), 240)
                w = max(1, int(round(float(elem.attrib.get("stroke-width", "2.0")))))
                if tag == "polygon":
                    pts = pts + [pts[0]]
                draw.line(pts, fill=col, width=w)
            elif tag == "circle":
                cx, cy, r = float(elem.attrib["cx"]), float(elem.attrib["cy"]), float(elem.attrib["r"])
                fill_s = elem.attrib.get("fill", "none")
                fill_c = hex_rgba(fill_s, int(float(elem.attrib.get("fill-opacity", "0.35")) * 255)) if fill_s != "none" else None
                col = hex_rgba(elem.attrib.get("stroke", "#f43f5e"), 245)
                draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill_c, outline=col, width=2)
            elif tag == "text":
                tx, ty = float(elem.attrib["x"]), float(elem.attrib["y"]) - 8
                col = hex_rgba(elem.attrib.get("fill", "#00e5ff"), 255)
                draw.text((tx, ty), elem.text or "", fill=col)

        canvas.save(proof_dir / f"proof_sheet_{sid:02d}.png")


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[3]
    pdir = (repo / "docs" / "overlays" / "proofs") if "--proofs" in sys.argv else None
    out_m = export_all_overlays(repo, proof_dir=pdir)
    print(f"Exported {len(out_m['sheets'])} calibrated SVG overlays to {repo / 'docs' / 'overlays'}")
