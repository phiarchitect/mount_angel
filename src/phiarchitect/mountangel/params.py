"""
Mount Angel Abbey Library - Central Parametric Definitions & Dimensions.
Standardizes all dimensions, datums, and geometric constraints.
"""

import math

# --- Dimensional Unit Conversion Constants ---
MM = 1.0
INCH = 25.4 * MM
FT = 12.0 * INCH

def ft(feet, inches=0.0):
    """Converts feet and inches into millimeters."""
    return float(feet) * FT + float(inches) * INCH

def deg_to_rad(d):
    """Converts degrees to radians."""
    return math.radians(d)

class LibraryDims:
    """Master dimensional container for Mount Angel Abbey Library."""

    # --- Origin & System Datum ---
    # Global (0, 0, 0) is at Level 3 Finished Floor at the Fan Focus Point.
    # +X = East, +Y = North (along central Ray C), +Z = Upward

    # --- Vertical Elevations (Relative to L3 Finished Floor = 0) ---
    Z_L3 = 0.0 * FT
    Z_L2 = -10.0 * FT               # Floor-to-floor = 10'-0"
    Z_L1 = -20.0 * FT               # Floor-to-floor = 10'-0"
    Z_ROOF_EAVE = ft(11, 4)         # 11'-4" above Level 3
    Z_ROOF_HIGH = ft(14, 0)         # High roof plane
    Z_MONITOR_RIDGE = ft(19, 6)     # Peak of curved light monitor scoop
    
    SLAB_THICKNESS = ft(0, 10)       # 10" structural reinforced slab
    WALL_THICKNESS = ft(1, 0)        # 12" structural concrete / brick wall
    FACET_WALL_THICKNESS = ft(1, 2)  # 14" insulated brick curtain wall

    # --- Radial Fan Geometry (The North Wing) ---
    # Central Ray C is oriented along +Y (90 degrees).
    # 4 major bays of 23.0 degrees each = 92.0 degrees total sweep.
    RAY_C_DEG = 90.0
    BAY_ANGLE_DEG = 23.0
    NUM_BAYS = 4
    TOTAL_SWEEP_DEG = NUM_BAYS * BAY_ANGLE_DEG  # 92.0 deg

    RAY_A_DEG = RAY_C_DEG + 2 * BAY_ANGLE_DEG   # 136.0 deg (West edge)
    RAY_B_DEG = RAY_C_DEG + 1 * BAY_ANGLE_DEG   # 113.0 deg
    # RAY_C_DEG = 90.0 deg                      # 90.0 deg (Center)
    RAY_D_DEG = RAY_C_DEG - 1 * BAY_ANGLE_DEG   # 67.0 deg
    RAY_E_DEG = RAY_C_DEG - 2 * BAY_ANGLE_DEG   # 44.0 deg (East edge)

    PRIMARY_RAYS = [RAY_A_DEG, RAY_B_DEG, RAY_C_DEG, RAY_D_DEG, RAY_E_DEG]

    # 16 Window Spaces (4 per bay)
    NUM_WINDOW_SPACES = 16
    WINDOW_SPACE_DEG = TOTAL_SWEEP_DEG / NUM_WINDOW_SPACES  # 5.75 deg per window
    CHORD_PER_WINDOW = ft(9, 3)     # 9'-3" chord per drawing 12-a12 schedule

    # --- Concentric Radii ---
    R_DESK_INNER = ft(12, 0)        # Inner curve of circulation counter
    R_DESK_OUTER = ft(15, 6)        # Outer counter working face
    R_WELL = ft(31, 10)             # 31'-10" edge of sunken reading well
    R_MEZZ = ft(44, 0)              # Edge of Level 3 mezzanine overhang
    R_COL_INTERMEDIATE = ft(62, 0)  # Ring of interior circular concrete columns
    R_OUTER_FACET = ft(92, 5.25)    # 92'-5 1/4" to perimeter H-column center

    # --- Columns & Piers ---
    ROUND_COL_DIAMETER = ft(1, 6)   # 18" round concrete columns
    H_PIER_DEPTH = ft(3, 6)         # 42" depth of H-shaped brick/steel pier
    H_PIER_WIDTH = ft(2, 4)         # 28" width of H-pier flanges
    H_STEEL_COL_D = ft(1, 0)        # 12" structural wide flange inside pier

    # --- South Wing (Rectilinear Block) ---
    SOUTH_WALL_Y = ft(-48, 0)       # Main south facade
    SOUTH_WING_EAST_X = ft(72, 0)   # East edge of building
    SOUTH_WING_WEST_X = ft(-84, 0)  # West edge of building
    SOUTH_WING_DEPTH = ft(48, 0)    # Extends from Y=0 to Y=-48'
    
    # Entry Portico / Canopy
    CANOPY_SOUTH_Y = ft(-62, 0)
    CANOPY_WEST_X = ft(-14, 0)
    CANOPY_EAST_X = ft(14, 0)
    CANOPY_ROOF_Z = ft(9, 6)


def attach_varset(doc, name="dims"):
    """
    Attaches an App::VarSet container to the FreeCAD document,
    registering primary architectural parameters for GUI inspection.
    """
    varset = doc.addObject("App::VarSet", name)
    varset.Label = "Library Datums & Dimensions"

    # Register Float / Length properties
    params = [
        ("Z_L3", LibraryDims.Z_L3, "Level 3 Floor Elevation (mm)"),
        ("Z_L2", LibraryDims.Z_L2, "Level 2 Floor Elevation (mm)"),
        ("Z_L1", LibraryDims.Z_L1, "Level 1 Floor Elevation (mm)"),
        ("Z_RoofEave", LibraryDims.Z_ROOF_EAVE, "Roof Eave Elevation (mm)"),
        ("Z_MonitorRidge", LibraryDims.Z_MONITOR_RIDGE, "Light Monitor Ridge Elevation (mm)"),
        ("R_Well", LibraryDims.R_WELL, "Sunken Reading Well Radius (mm)"),
        ("R_ColRing", LibraryDims.R_COL_INTERMEDIATE, "Intermediate Column Ring Radius (mm)"),
        ("R_OuterFacet", LibraryDims.R_OUTER_FACET, "Outer Curtain Wall Radius (mm)"),
        ("FanSweepDeg", LibraryDims.TOTAL_SWEEP_DEG, "Total Fan Sweep (Degrees)"),
        ("BayAngleDeg", LibraryDims.BAY_ANGLE_DEG, "Radial Bay Angle (Degrees)"),
    ]

    for prop_name, val, desc in params:
        try:
            varset.addProperty("App::PropertyFloat", prop_name, "ArchitecturalDimensions", desc)
            setattr(varset, prop_name, float(val))
        except Exception:
            pass

    return varset
