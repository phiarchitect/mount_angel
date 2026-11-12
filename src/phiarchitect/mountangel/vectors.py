"""
Mount Angel Abbey Library — Constructive Geometry & Multi-Sheet Vector Overlay Engine.

Establishes a unified canonical 3D architectural coordinate system:
  - Origin O(0, 0, 0): Working Point #4 (convergence of Radial Axes B, C, D)
    on Level 3 Finished Floor (Main Fan Reading Room).
  - +X = East, +Y = North (Grid Line 6 runs along Y = 0), +Z = Upward.
  - Primary constructive units: architectural feet (converted cleanly to metres
    via FT_TO_M = 0.3048 for IngeTrazo 0.6.0).

Cross-registers 7 primary historical blueprint sheets (A & S series) to sub-pixel
accuracy and emits multi-layer College-Geometry-style SVG vector overlays.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

FT_TO_M = 0.3048


def ft(feet: float, inches: float = 0.0) -> float:
    """Return decimal feet from feet and inches."""
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


# =============================================================================
# 1. MASTER ARCHITECTURAL & CONSTRUCTIVE GEOMETRY CONSTANTS (FEET)
# =============================================================================

class AaltoGeometry:
    """Canonical constructive geometry of Alvar Aalto's Mount Angel Abbey Library."""

    # --- Vertical Elevations (Feet relative to Level 3 Main Reading Room = 0.0) ---
    Z_LOBBY_FT = ft(2, 0)           # +2'-0" (+0.61 m) South Entrance Wing & Lobby
    Z_L3_FT = 0.0                   #  0'-0" ( 0.00 m) Main Fan Reading Room & Control Desk
    Z_REF_GALLERY_FT = ft(-4, 6)    # -4'-6" (-1.37 m) Semicircular Intermediate Reference Gallery
    Z_L2_FT = ft(-12, 6)            # -12'-6" (-3.81 m) Level 2 Stacks, Carrels & Reading Well
    Z_L1_FT = ft(-26, 6)            # -26'-6" (-8.08 m) Level 1 Downhill Base Stacks
    Z_CRAWL_FT = ft(-34, 0)         # -34'-0" (-10.36 m) North Crawl Space & Footing Toe

    Z_CANOPY_FT = ft(10, 8)         # +10'-8" (+3.25 m) South Entry Portico Marquee
    Z_FAN_ROOF_LOW_FT = ft(12, 6)   # +12'-6" (+3.81 m) Fan Roof Deck outside Monitor
    Z_SOUTH_ROOF_FT = ft(16, 4)     # +16'-4" (+4.98 m) South Wing Built-up Roof & Parapet
    Z_FAN_PARAPET_N_FT = ft(17, 6)  # +17'-6" (+5.33 m) Tipped North Perimeter Light-Scoop Parapet
    Z_LANTERN_TOP_FT = ft(19, 6)    # +19'-6" (+5.94 m) Conical Roof Skylight Lanterns
    Z_SCOOP_RIDGE_FT = ft(21, 6)    # +21'-6" (+6.55 m) Curved Central Clerestory Light Scoop Peak

    # --- Polycentric Working Points (X_ft, Y_ft) ---
    WP4: tuple[float, float] = (0.0, 0.0)          # Convergence of Primary Structural Rays B, C, D
    WP3A: tuple[float, float] = (1.50, 2.60)       # Center of Mezzanine Well & Skylight Arcs
    WP_DESK: tuple[float, float] = (-1.20, 2.20)   # Center of Control Desk & Slatted Wood Drum
    WP_LOWER: tuple[float, float] = (5.20, -4.80)  # Lower Focus for Outer Boundary Axes A & E

    # --- Radial Axes (Degrees CCW from +X East) ---
    RAY_A_DEG = 168.00   # West Fan Throat Boundary (from WP_LOWER through West Jamb A)
    RAY_B_DEG = 136.80   # Structural Axis B (from WP4 through H-Pier B)
    RAY_C_DEG = 99.00    # Central Structural Axis C (from WP4 through H-Pier C)
    RAY_D_DEG = 63.62    # Structural Axis D (from WP4 through H-Pier D)
    RAY_E_DEG = 38.60    # East Diagonal Wall Boundary (from WP_LOWER through East Apex E)

    # --- Outer Fan Perimeter Vertices (Outer Face of Brick Wall along Bays A-B-C-D-E) ---
    PT_A: tuple[float, float] = (-86.5, 14.8)   # WP #6 West Jamb of Curtain Wall
    PT_B: tuple[float, float] = (-61.8, 56.8)   # WP #7 H-Pier B Outer Brick Line
    PT_C: tuple[float, float] = (-13.8, 85.4)   # WP #8 H-Pier C Outer Brick Line
    PT_D: tuple[float, float] = (40.8, 82.5)    # WP #9 H-Pier D Outer Brick Line
    PT_E: tuple[float, float] = (96.0, 66.5)    # WP #10 East Prow Apex

    # Inner West & East Junctions where Fan meets South Wing & Periodical Lounge
    PT_A_INNER_JUNC: tuple[float, float] = (-77.5, 12.8)  # West step down to Elevator/Grid 6
    PT_WEST_THROAT: tuple[float, float] = (-18.5, 0.2)    # West throat at Control Area
    PT_LOUNGE_JUNC: tuple[float, float] = (51.8, 32.8)    # East wall meets Periodical Lounge
    PT_EAST_THROAT: tuple[float, float] = (15.5, 3.6)     # East throat at Control Area

    # --- Orthogonal Survey Grid Lines 1..6 (Y_ft) ---
    GRID_Y = {
        "6": 0.0,      # Main Fan / South Wing Datum (WP #4)
        "5": -8.8,     # Rare Book Storage / Mechanical Datum
        "4": -21.0,    # Central Corridor / Auditorium North Wall
        "3": -28.0,    # West Cataloging Wing South Facade
        "2": -50.8,    # Main South Entrance Facade
        "1": -59.5,    # East Rare Book & Auditorium South Facade
    }

    # --- Concentric / Polycentric Radii around WP3A (1.50, 2.60) ---
    R_DESK_INNER = 11.0
    R_DESK_OUTER = 14.5
    R_WOOD_DRUM = 17.5
    R_GALLERY_RAIL = 22.8       # Semicircular Reading Level Gallery (Z = -4'-6")
    R_SCOOP_INNER = 24.0        # Inner curved white plaster light-scoop curb
    R_WELL_L2_WALL = ft(31, 10) # 31'-10" (31.833 ft) Curved L2 Reference Wall
    R_SCOOP_RIDGE = 34.8        # Peak ridge where curved copper/plaster scoop meets North glass
    R_SCOOP_OUTER = 41.8        # Outer curb of sloped North skylight glass
    R_MEZZ_OPENING = 43.8       # Level 3 Mezzanine Double-Height Well Opening
    R_MEZZ_DESK = 46.2          # Outer edge of continuous curved reading counter

    # --- Structural Round Columns (18" diameter = 0.75 ft radius) ---
    WELL_COLS_FT = {
        "Well_W_South": (-30.26, 1.60),
        "Well_1_WNW":   (-23.12, 21.72),
        "Well_2_NNW":   (-5.24, 32.97),
        "Well_3_NNE":   (15.23, 30.68),
        "Well_4_ENE":   (32.57, 18.93),
        "South_W1":     (-54.37, 6.87),
    }

    PAIRED_COLS_FT = {
        "Pair_B_L": (-42.30, 36.44),
        "Pair_B_R": (-39.01, 39.89),
        "Pair_C_L": (-11.31, 56.15),
        "Pair_C_R": (-6.65, 57.41),
        "Pair_D_L": (25.87, 57.53),
        "Pair_D_R": (30.47, 56.09),
    }

    SOUTH_WING_COLS_FT = [
        (-102.0, 0.0), (-91.5, 0.0), (-54.0, 0.0), (-34.5, 0.0), (-18.5, 0.0),
        (-91.5, -28.0), (-91.5, -50.8), (-71.5, -50.8), (-51.5, -50.8),
        (-22.5, -50.8), (4.5, -50.8), (16.5, -50.8),
        (51.8, 0.0), (51.8, 16.0), (51.8, 32.8),
    ]

    # --- 3 Perimeter H-Piers (Centers on Rays B, C, D just inside outer brick line) ---
    H_PIERS = [
        {"name": "HPier_B", "center": (-58.0, 53.1), "angle_deg": RAY_B_DEG, "depth": 6.2, "width": 5.2},
        {"name": "HPier_C", "center": (-13.1, 80.5), "angle_deg": RAY_C_DEG, "depth": 6.2, "width": 5.2},
        {"name": "HPier_D", "center": (38.7, 78.0),  "angle_deg": RAY_D_DEG, "depth": 6.2, "width": 5.2},
    ]

    # --- 12 Roof Conical Skylights (X_ft, Y_ft, radius_ft) measured from Drawing 07-a7 ---
    CONICAL_SKYLIGHTS = [
        # Control Desk Slatted Wood Drum Portholes (2)
        (-9.8, 11.8, 2.2),
        (6.2, 11.8, 2.2),
        # Public Catalog, Microfilm & Entry Area Row (4)
        (-39.5, -7.8, 2.2),
        (-27.2, -7.8, 2.2),
        (-11.2, -9.8, 2.2),
        (4.2, -9.8, 2.2),
        # West Wing & Corridor String (4)
        (-107.8, -22.2, 2.2),
        (-92.2, -22.2, 2.2),
        (-75.0, -22.2, 2.2),
        (-57.8, -22.2, 2.2),
        # Main Entrance Lobby Skylights (2)
        (-11.2, -21.2, 2.2),
        (4.2, -21.2, 2.2),
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

    def world_to_px(self, wx: float, wy: float) -> tuple[float, float]:
        """Map canonical world feet (X, Y) [or (S, Z) for section] to image pixels."""
        ang = math.radians(self.rot_deg)
        ca, sa = math.cos(ang), math.sin(ang)
        sx, sy = wx, -wy
        px = self.scale_px_per_ft * (ca * sx - sa * sy) + self.origin_px[0]
        py = self.scale_px_per_ft * (sa * sx + ca * sy) + self.origin_px[1]
        return (px, py)


CALIBRATED_SHEETS: dict[int, SheetCalibration] = {
    3: SheetCalibration(
        sheet_id=3,
        filename="03-a3_gm-1135x700.jpg",
        title="FLOOR PLAN LEVEL #1",
        width_px=1135,
        height_px=700,
        scale_px_per_ft=3.4115,
        rot_deg=-0.600,
        origin_px=(621.00, 418.80),
    ),
    4: SheetCalibration(
        sheet_id=4,
        filename="04-a4_gm-1144x700.jpg",
        title="FLOOR PLAN LEVEL TWO",
        width_px=1144,
        height_px=700,
        scale_px_per_ft=3.4534,
        rot_deg=-0.563,
        origin_px=(618.99, 420.14),
    ),
    5: SheetCalibration(
        sheet_id=5,
        filename="05-a5_gm-1145x700.jpg",
        title="FLOOR PLAN LEVEL #3",
        width_px=1145,
        height_px=700,
        scale_px_per_ft=3.4416,
        rot_deg=-0.741,
        origin_px=(620.25, 418.53),
    ),
    6: SheetCalibration(
        sheet_id=6,
        filename="06-a6_gm-1149x700.jpg",
        title="BASIC PLAN LAYOUT",
        width_px=1149,
        height_px=700,
        scale_px_per_ft=6.9100,
        rot_deg=-0.780,
        origin_px=(693.58, 691.15),
    ),
    7: SheetCalibration(
        sheet_id=7,
        filename="07-a7_gm-1145x700.jpg",
        title="ROOF PLAN & DETAILS",
        width_px=1145,
        height_px=700,
        scale_px_per_ft=3.4416,
        rot_deg=-0.741,
        origin_px=(619.25, 418.53),
    ),
    13: SheetCalibration(
        sheet_id=13,
        filename="13-a13_gm-1150x700.jpg",
        title="SECTION A-A & B-B",
        width_px=1150,
        height_px=700,
        scale_px_per_ft=3.4460,
        rot_deg=-0.250,
        origin_px=(423.10, 524.50),
        mode="section_aa",
    ),
    35: SheetCalibration(
        sheet_id=35,
        filename="35-s4_gm-1140x700.jpg",
        title="LEVEL THREE FRAMING & FOUNDATION PLAN",
        width_px=1140,
        height_px=700,
        scale_px_per_ft=3.4414,
        rot_deg=-0.761,
        origin_px=(618.45, 417.22),
    ),
}


# =============================================================================
# 3. CONSTRUCTIVE FLOORPLATE, STAIR, CARREL & STACK GENERATORS (FEET)
# =============================================================================

def get_level3_envelope_ft() -> list[tuple[float, float]]:
    """Complete exterior boundary polygon of Level 3 (Fan + Periodical Lounge + South Wing)."""
    G = AaltoGeometry
    return [
        G.PT_A,                  # (-86.5, 14.8) West Fan Jamb A
        G.PT_B,                  # (-61.8, 56.8) H-Pier B
        G.PT_C,                  # (-13.8, 85.4) H-Pier C
        G.PT_D,                  # (+40.8, 82.5) H-Pier D
        G.PT_E,                  # (+96.0, 66.5) East Prow Apex E
        G.PT_LOUNGE_JUNC,        # (+51.8, 32.8) SE Fan wall meets Periodical Lounge
        (51.8, -8.8),            # Periodical Lounge SE corner (Grid 5)
        (61.5, -8.8),            # Rare Book / East Stair NE corner
        (61.5, -59.5),           # Rare Book & Auditorium SE corner (Grid 1)
        (19.5, -59.5),           # Rare Book SW corner (Grid 1)
        (16.5, -50.8),           # Canted Lobby / Rare Book junction (Grid 2)
        (-91.5, -50.8),          # Main South Entrance Facade SW corner (Grid 2)
        (-91.5, -28.0),          # Step up to Grid 3
        (-126.5, -28.0),         # West Cataloging Wing SW corner (Grid 3)
        (-126.5, 1.5),           # West Cataloging Wing NW corner (Grid 6)
        (-77.5, 1.5),            # Elevator / West Wing step North
        G.PT_A_INNER_JUNC,       # (-77.5, 12.8) Junction with West Fan Throat
    ]


def get_level2_envelope_ft() -> list[tuple[float, float]]:
    """Complete boundary polygon of Level 2 (Fan + Seminar/Benedictina + Mechanical + West Wing)."""
    G = AaltoGeometry
    return [
        G.PT_A,
        G.PT_B,
        G.PT_C,
        G.PT_D,
        G.PT_E,
        G.PT_LOUNGE_JUNC,        # (+51.8, 32.8) Seminar Room NE corner
        (51.8, -8.8),            # Benedictina SE corner (Grid 5)
        (61.5, -8.8),            # Mechanical East step
        (61.5, -21.0),           # Mechanical SE corner (Grid 4)
        (-91.5, -21.0),          # Mechanical / Corridor SW line (Grid 4)
        (-91.5, -28.0),          # Bindery step
        (-126.5, -28.0),         # Receiving / Bindery SW corner (Grid 3)
        (-126.5, 1.5),           # Receiving / Bindery NW corner (Grid 6)
        (-77.5, 1.5),
        G.PT_A_INNER_JUNC,
    ]


def get_level1_envelope_ft() -> list[tuple[float, float]]:
    """Complete boundary polygon of Level 1 (Downhill Fan Stacks + Pentagonal Core + Elevator/Stair #4)."""
    G = AaltoGeometry
    return [
        (-77.5, 12.8),
        G.PT_A,
        G.PT_B,                  # H-Pier B
        G.PT_C,                  # H-Pier C
        G.PT_D,                  # H-Pier D
        (90.0, 68.2),            # L1 East corner near E
        (43.5, 24.5),            # SE wall step at Stair #2
        (32.57, 18.93),          # Well_4_ENE
        (10.5, 0.5),             # Electronics room SE corner (Grid 6)
        (-30.26, 1.60),          # Well_W_South
        (-67.5, 10.2),           # West corridor junction
        (-67.5, -21.0),          # Stair #4 SE corner
        (-83.5, -21.0),          # Stair #4 SW corner
        (-83.5, -8.5),           # Elevator pit
        (-91.5, -8.5),
        (-91.5, 1.5),
        (-77.5, 1.5),
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


def get_h_pier_polygons_ft() -> list[list[tuple[float, float]]]:
    """Return 12-vertex H-shaped polygons for Perimeter H-Piers B, C, D."""
    polys = []
    for hp in AaltoGeometry.H_PIERS:
        cx, cy = hp["center"]
        ang = math.radians(hp["angle_deg"] - 90.0)
        ca, sa = math.cos(ang), math.sin(ang)
        w, d = hp["width"], hp["depth"]
        tf, tw = 1.15, 1.15  # flange & web thickness in ft
        # Local H-shape centered at (0,0), Y along ray
        hw, hd, htw = w / 2.0, d / 2.0, tw / 2.0
        local = [
            (-hw, hd), (hw, hd), (hw, hd - tf), (htw, hd - tf),
            (htw, -hd + tf), (hw, -hd + tf), (hw, -hd), (-hw, -hd),
            (-hw, -hd + tf), (-htw, -hd + tf), (-htw, hd - tf), (-hw, hd - tf),
        ]
        polys.append([(cx + lx * ca - ly * sa, cy + lx * sa + ly * ca) for lx, ly in local])
    return polys


def get_carrel_alcoves_ft() -> list[list[tuple[float, float]]]:
    """Perimeter study carrel partitions along Faceted Bays A-B, B-C, C-D, D-E."""
    G = AaltoGeometry
    bays = [
        (G.PT_A, G.PT_B, 5),
        (G.PT_B, G.PT_C, 5),
        (G.PT_C, G.PT_D, 5),
        (G.PT_D, G.PT_E, 5),
    ]
    boxes = []
    for p0, p1, n_carrels in bays:
        vx, vy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(vx, vy)
        ux, uy = vx / L, vy / L
        # Inward normal (pointing South/toward fan center: rotate clockwise 90 deg -> (uy, -ux))
        nx, ny = uy, -ux
        margin = 5.2
        usable = L - 2 * margin
        cw = usable / n_carrels
        depth = 5.8
        for i in range(n_carrels):
            s0 = margin + i * cw + 0.6
            s1 = margin + (i + 1) * cw - 0.6
            q0 = (p0[0] + ux * s0 + nx * 1.2, p0[1] + uy * s0 + ny * 1.2)
            q1 = (p0[0] + ux * s1 + nx * 1.2, p0[1] + uy * s1 + ny * 1.2)
            q2 = (q1[0] + nx * depth, q1[1] + ny * depth)
            q3 = (q0[0] + nx * depth, q0[1] + ny * depth)
            boxes.append([q0, q1, q2, q3])
    return boxes


def get_radial_bookstacks_ft(r_start: float = 50.0, r_end: float = 69.5) -> list[list[tuple[float, float]]]:
    """Generate radiating double-faced Aalto bookstack ranges in the Fan reading room."""
    G = AaltoGeometry
    # Stack angles spanning cleanly between and flanking Rays B, C, D
    stack_angles = [
        156.0, 149.5, 143.0,
        130.5, 124.2, 118.0, 111.8, 105.5,
        92.5, 86.2, 80.0, 73.8,
        57.5, 51.2, 45.0,
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
    """West and East radial stairs connecting Level 3 Mezzanine, Reading Gallery, and Level 2."""
    G = AaltoGeometry
    stairs = []
    for ang_c in (155.5, 48.5):
        rad = math.radians(ang_c)
        ux, uy = math.cos(rad), math.sin(rad)
        nx, ny = -uy, ux
        hw = 3.2  # 6'-5" stair width
        r0, r1 = 22.8, 43.8
        cx, cy = G.WP3A
        stairs.append([
            (cx + r0 * ux - hw * nx, cy + r0 * uy - hw * ny),
            (cx + r1 * ux - hw * nx, cy + r1 * uy - hw * ny),
            (cx + r1 * ux + hw * nx, cy + r1 * uy + hw * ny),
            (cx + r0 * ux + hw * nx, cy + r0 * uy + hw * ny),
        ])
    # Also Stair #2 along SE diagonal wall (X=+65..+81, along Ray E)
    rad_e = math.radians(G.RAY_E_DEG)
    uxe, uye = math.cos(rad_e), math.sin(rad_e)
    nxe, nye = -uye, uxe
    bx, by = 64.5, 41.8
    stairs.append([
        (bx, by),
        (bx + 19.0 * uxe, by + 19.0 * uye),
        (bx + 19.0 * uxe + 6.5 * nxe, by + 19.0 * uye + 6.5 * nye),
        (bx + 6.5 * nxe, by + 6.5 * nye),
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
        svg.add_line("regulating", (-134.0, gy), (98.0, gy), "#38bdf8", width=1.1, dash="6,5")
        if cal.sheet_id != 6:
            svg.add_label("regulating", (-133.0, gy), f"GRID ({g_num}) Y={gy:+.0f}'", "#38bdf8", size=10, dx=2, dy=-4)

    # 2. Polycentric Radial Rays B, C, D from WP #4 (0, 0)
    for label, deg in [("AXIS B (136.8°)", G.RAY_B_DEG), ("AXIS C (99.0°)", G.RAY_C_DEG), ("AXIS D (63.6°)", G.RAY_D_DEG)]:
        p_end = polar_pt(G.WP4, 98.0, deg)
        svg.add_line("regulating", G.WP4, p_end, "#00e5ff", width=1.8, dash="8,4")
        svg.add_label("regulating", polar_pt(G.WP4, 92.5, deg), label, "#00e5ff", size=10)

    # 3. Outer Boundary Rays A & E from Lower Focus WP_LOWER
    svg.add_line("regulating", G.WP4, G.WP_LOWER, "#f59e0b", width=1.5, dash="3,3")
    for label, deg, r_max in [("AXIS A (168.0°)", G.RAY_A_DEG, 96.0), ("AXIS E (38.6°)", G.RAY_E_DEG, 118.0)]:
        p_end = polar_pt(G.WP_LOWER, r_max, deg)
        svg.add_line("regulating", G.WP_LOWER, p_end, "#fb923c", width=1.8, dash="7,4")
        svg.add_label("regulating", polar_pt(G.WP_LOWER, r_max - 8.0, deg), label, "#fb923c", size=10)

    # 4. Concentric Regulating Arcs (R = 31'-10" Well & R = 43.8' Mezzanine)
    svg.add_polyline("regulating", arc_pts(G.WP3A, G.R_WELL_L2_WALL, 36.0, 165.0, 44), "#a855f7", width=1.5, dash="5,4")
    svg.add_label("regulating", polar_pt(G.WP3A, G.R_WELL_L2_WALL, 80.0), "R = 31'-10\"", "#c084fc", size=10)

    # Working Point Markers
    for wp_name, wp_pt, col in [
        ("WP #4 (0,0)", G.WP4, "#00e5ff"),
        ("WP #3A", G.WP3A, "#c084fc"),
    ]:
        svg.add_circle_world("regulating", wp_pt, 10.0 / sc * 0.45, sc, col, width=2.0, fill=col, fill_opacity=0.35)
        svg.add_label("regulating", wp_pt, wp_name, col, size=10, dx=6, dy=-4)

    # 5. Structural Columns & Perimeter H-Piers
    for hp_poly in get_h_pier_polygons_ft():
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
        # Drawing 06: Basic Plan Layout (1/4" = 1'-0" master constructive key)
        _add_common_regulating_and_structure(svg, cal, include_south_cols=False)
        # Outer faceted brick bays A-B-C-D-E
        svg.add_polyline("walls", [G.PT_A_INNER_JUNC, G.PT_A, G.PT_B, G.PT_C, G.PT_D, G.PT_E, G.PT_LOUNGE_JUNC], "#10b981", width=2.8)
        # Level 1 pentagonal concrete retaining wall
        svg.add_polyline("walls", get_l1_inner_pentagon_ft(), "#22c55e", width=2.4)
        # Paired column callouts
        svg.add_label("structure", (-40.6, 38.2), "PAIRED 18\"Ø COLS (4'-10\" c/c)", "#fda4af", size=10, dx=8, dy=-8)

    elif sheet_id == 5:
        # Drawing 05: Floor Plan Level #3
        _add_common_regulating_and_structure(svg, cal)
        svg.add_polyline("walls", get_level3_envelope_ft(), "#10b981", width=2.5, closed=True, fill="#10b981", fill_opacity=0.05)
        # South Entry Canopy
        svg.add_polyline("roof_skylights", [(-22.5, -50.8), (4.5, -50.8), (4.5, -65.5), (-22.5, -65.5)], "#f59e0b", width=2.0, closed=True, dash="5,3")
        svg.add_label("roof_skylights", (-21.5, -64.5), "ENTRY CANOPY", "#fbbf24", size=9, dx=2, dy=11)
        # Mezzanine Opening & Continuous Reading Counter
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_MEZZ_OPENING, 51.0, 152.0, 40), "#facc15", width=2.2)
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_MEZZ_DESK, 51.0, 152.0, 40), "#eab308", width=1.6)
        svg.add_label("stairs_millwork", polar_pt(G.WP3A, G.R_MEZZ_DESK, 99.0), "MEZZANINE READING COUNTER", "#fde047", size=9, dx=-55, dy=-6)
        # Semicircular Reference Gallery below & Control Counter
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_GALLERY_RAIL, 45.0, 158.0, 32), "#38bdf8", width=1.6, dash="4,3")
        svg.add_polyline("stairs_millwork", arc_pts(G.WP_DESK, G.R_DESK_OUTER, 25.0, 165.0, 32), "#f97316", width=2.2)
        svg.add_polyline("stairs_millwork", arc_pts(G.WP_DESK, G.R_DESK_INNER, 25.0, 165.0, 32), "#f97316", width=1.6)
        # Carrels, Stairs & Radial Bookstacks
        for box in get_carrel_alcoves_ft():
            svg.add_polyline("walls", box, "#34d399", width=1.2, closed=True)
        for st in get_well_stairs_ft():
            svg.add_polyline("stairs_millwork", st, "#fbbf24", width=1.8, closed=True, fill="#fbbf24", fill_opacity=0.14)
        for stk in get_radial_bookstacks_ft(51.0, 69.0):
            svg.add_polyline("stairs_millwork", stk, "#a3e635", width=1.1, closed=True, fill="#a3e635", fill_opacity=0.12)
        svg.add_label("walls", (52.5, 16.0), "MT. HOOD PICTURE WINDOW", "#6ee7b7", size=9, dx=4, dy=0)

    elif sheet_id == 4:
        # Drawing 04: Floor Plan Level #2
        _add_common_regulating_and_structure(svg, cal)
        svg.add_polyline("walls", get_level2_envelope_ft(), "#10b981", width=2.5, closed=True, fill="#10b981", fill_opacity=0.05)
        # L2 Curved Reference Bookwall (R = 31'-10") & Semicircular Gallery above
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_WELL_L2_WALL, 48.0, 152.0, 36), "#facc15", width=2.2)
        svg.add_polyline("stairs_millwork", arc_pts(G.WP3A, G.R_GALLERY_RAIL, 45.0, 158.0, 32), "#f97316", width=1.8)
        for box in get_carrel_alcoves_ft():
            svg.add_polyline("walls", box, "#34d399", width=1.3, closed=True, fill="#34d399", fill_opacity=0.08)
        for st in get_well_stairs_ft():
            svg.add_polyline("stairs_millwork", st, "#fbbf24", width=1.8, closed=True, fill="#fbbf24", fill_opacity=0.14)
        for stk in get_radial_bookstacks_ft(46.0, 68.5):
            svg.add_polyline("stairs_millwork", stk, "#a3e635", width=1.0, closed=True, fill="#a3e635", fill_opacity=0.10)

    elif sheet_id == 3:
        # Drawing 03: Floor Plan Level #1
        _add_common_regulating_and_structure(svg, cal)
        svg.add_polyline("walls", get_level1_envelope_ft(), "#10b981", width=2.5, closed=True, fill="#10b981", fill_opacity=0.06)
        svg.add_polyline("walls", get_l1_inner_pentagon_ft(), "#22c55e", width=2.4)
        for stk in get_radial_bookstacks_ft(38.0, 71.0):
            svg.add_polyline("stairs_millwork", stk, "#a3e635", width=1.0, closed=True, fill="#a3e635", fill_opacity=0.10)

    elif sheet_id == 7:
        # Drawing 07: Roof Plan & Skylights
        _add_common_regulating_and_structure(svg, cal, include_south_cols=False)
        svg.add_polyline("walls", get_level3_envelope_ft(), "#10b981", width=2.2, closed=True)
        # Curved Copper/Plaster Scoop Band (R = 24.0..34.8 ft)
        scoop_in = arc_pts(G.WP3A, G.R_SCOOP_INNER, 46.0, 155.0, 40)
        scoop_ridge = arc_pts(G.WP3A, G.R_SCOOP_RIDGE, 46.0, 155.0, 40)
        scoop_out = arc_pts(G.WP3A, G.R_SCOOP_OUTER, 46.0, 155.0, 40)
        svg.add_polyline("roof_skylights", scoop_in + list(reversed(scoop_ridge)), "#f59e0b", width=2.0, closed=True, fill="#f59e0b", fill_opacity=0.16)
        # North-Facing Sloped Skylight Glazing Band (R = 34.8..41.8 ft)
        svg.add_polyline("roof_skylights", scoop_ridge + list(reversed(scoop_out)), "#38bdf8", width=2.2, closed=True, fill="#38bdf8", fill_opacity=0.22)
        # Skylight radial mullions across North glass
        for m_deg in range(48, 156, 8):
            svg.add_line("roof_skylights", polar_pt(G.WP3A, G.R_SCOOP_RIDGE, m_deg), polar_pt(G.WP3A, G.R_SCOOP_OUTER, m_deg), "#fde047", width=1.2)
        svg.add_label("roof_skylights", polar_pt(G.WP3A, G.R_SCOOP_OUTER + 2.5, 99.0), "CURVED NORTH DAYLIGHT SCOOP", "#fde047", size=10, dx=-70, dy=-4)
        # 12 Conical Roof Skylights
        for sx, sy, sr in G.CONICAL_SKYLIGHTS:
            svg.add_circle_world("roof_skylights", (sx, sy), sr, sc, "#facc15", width=2.2, fill="#fde047", fill_opacity=0.32)

    elif sheet_id == 35:
        # Drawing 35-s4: Level 3 Structural Framing Plan
        _add_common_regulating_and_structure(svg, cal)
        svg.add_polyline("walls", get_level3_envelope_ft(), "#10b981", width=1.8, closed=True)
        # Radial structural steel/concrete beams between R = 32' and outer perimeter
        for b_deg in range(44, 166, 6):
            svg.add_line("structure", polar_pt(G.WP4, 33.5, b_deg), polar_pt(G.WP4, 84.0, b_deg), "#fb7185", width=1.0, dash="3,2")
        svg.add_polyline("structure", arc_pts(G.WP3A, 57.5, 42.0, 162.0, 40), "#f43f5e", width=2.0)

    elif sheet_id == 13:
        # Drawing 13-a13: Section A-A (Horizontal = S_ft North of Grid 6; Vertical = Z_ft above L3)
        elevs = [
            ("UPPER LOBBY (+2'-0\")", G.Z_LOBBY_FT, -52.0, 0.0, "#38bdf8"),
            ("LEVEL #3 FAN (0'-0\")", G.Z_L3_FT, -2.0, 86.0, "#00e5ff"),
            ("REF. GALLERY (-4'-6\")", G.Z_REF_GALLERY_FT, 0.0, 26.0, "#a855f7"),
            ("LEVEL #2 (-12'-6\")", G.Z_L2_FT, -22.0, 86.0, "#22c55e"),
            ("LEVEL #1 (-26'-6\")", G.Z_L1_FT, 32.0, 86.0, "#10b981"),
        ]
        for lbl, zf, s0, s1, col in elevs:
            svg.add_line("regulating", (s0, zf), (88.0, zf), col, width=1.5, dash="6,4")
            svg.add_label("regulating", (89.0, zf), lbl, col, size=10, dx=4, dy=3)

        # Floor slabs & structural walls in Section A-A
        svg.add_polyline("walls", [(-72.5, G.Z_CANOPY_FT), (-50.8, G.Z_CANOPY_FT)], "#f59e0b", width=2.6)
        svg.add_polyline("walls", [(-50.8, G.Z_LOBBY_FT), (-3.0, G.Z_LOBBY_FT), (0.0, G.Z_L3_FT), (22.9, G.Z_L3_FT)], "#10b981", width=2.6)
        svg.add_polyline("walls", [(45.8, G.Z_L3_FT), (85.4, G.Z_L3_FT)], "#10b981", width=2.8)
        svg.add_polyline("stairs_millwork", [(45.8, G.Z_L3_FT), (45.8, G.Z_L3_FT + 3.1)], "#facc15", width=2.8)
        svg.add_polyline("stairs_millwork", [(22.9, G.Z_L3_FT), (22.9, G.Z_REF_GALLERY_FT), (33.0, G.Z_REF_GALLERY_FT)], "#c084fc", width=2.2)
        svg.add_polyline("walls", [(-21.0, G.Z_L2_FT), (85.4, G.Z_L2_FT)], "#10b981", width=2.6)
        svg.add_polyline("walls", [(33.0, G.Z_L1_FT), (85.4, G.Z_L1_FT)], "#10b981", width=2.6)
        svg.add_line("walls", (85.4, G.Z_CRAWL_FT), (85.4, G.Z_FAN_PARAPET_N_FT), "#10b981", width=2.8)
        svg.add_line("walls", (33.0, G.Z_CRAWL_FT), (33.0, G.Z_L2_FT), "#10b981", width=2.4)

        # Roof, Conical Lanterns, Curved Daylight Scoop & Tipped North Perimeter Roof!
        svg.add_polyline(
            "roof_skylights",
            [
                (-50.8, G.Z_SOUTH_ROOF_FT),
                (23.5, G.Z_SOUTH_ROOF_FT),
                # Exterior copper scoop roof slope up to ridge at S = +35.1 ft, Z = +21.5 ft
                (35.1, G.Z_SCOOP_RIDGE_FT),
                # Steep North-facing skylight glazing down to S = +40.9 ft, Z = +12.5 ft
                (40.9, G.Z_FAN_ROOF_LOW_FT),
                # Flat fan roof deck + Tipped North Perimeter Parapet (+17'-6")
                (75.5, G.Z_FAN_ROOF_LOW_FT),
                (85.4, G.Z_FAN_PARAPET_N_FT),
            ],
            "#facc15",
            width=2.6,
        )
        # Concave white plaster reflector vault inside the North Light Scoop + upward North soffit
        svg.add_polyline(
            "roof_skylights",
            [(28.2, 12.6), (29.5, 16.0), (31.8, 19.0), (35.1, G.Z_SCOOP_RIDGE_FT)],
            "#38bdf8",
            width=2.0,
            dash="4,2",
        )
        # Conical skylight throats visible in Section A-A
        for s_cone in (-27.0, -16.0, 6.9):
            svg.add_polyline(
                "roof_skylights",
                [(s_cone - 3.2, 10.5), (s_cone - 2.1, G.Z_LANTERN_TOP_FT), (s_cone + 2.1, G.Z_LANTERN_TOP_FT), (s_cone + 3.2, 10.5)],
                "#f59e0b",
                width=1.8,
            )
        # Abbey Hillside Grade Profile (sloping from South Plaza +2' down to North Toe -38')
        svg.add_polyline(
            "regulating",
            [(-75.0, 1.5), (-50.8, 1.8), (-44.0, 0.8), (-21.0, -13.0), (0.0, -16.5), (33.0, -27.5), (66.0, -33.5), (85.4, -30.5), (108.0, -39.0)],
            "#a3e635",
            width=2.0,
            dash="8,4",
        )
        svg.add_label("roof_skylights", (33.5, G.Z_SCOOP_RIDGE_FT + 1.5), "NORTH LIGHT SCOOP (+21'-6\")", "#fde047", size=10, dx=-25, dy=-4)

    return svg.to_svg()


def export_all_overlays(repo_root: Path, proof_dir: Path | None = None) -> dict:
    """Export all calibrated SVG overlays, manifest.json, and optional PNG bitmap+vector proof sheets."""
    overlays_dir = repo_root / "docs" / "overlays"
    overlays_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "origin_description": "Working Point #4 (convergence of Rays B, C, D) on Level 3 Finished Floor",
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
        # Tint ink pale slate-white over deep navy background (#0d1320)
        import numpy as np
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
    out_m = export_all_overlays(repo)
    print(f"Exported {len(out_m['sheets'])} calibrated SVG overlays to {repo / 'docs' / 'overlays'}")
