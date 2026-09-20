"""
Mount Angel Library - Master 2D/3D Skeleton & Datum Wireframe.
Generates constructive geometric guides: polar rays, concentric arcs, facet chords, and level planes.
"""

import math
import FreeCAD
import Part
from phiarchitect.mountangel.params import LibraryDims, deg_to_rad

def make_polar_point(radius, angle_deg, z=0.0):
    """Calculates 3D Cartesian coordinates from polar (r, theta, z)."""
    rad = deg_to_rad(angle_deg)
    x = radius * math.cos(rad)
    y = radius * math.sin(rad)
    return FreeCAD.Vector(x, y, z)


def build_skeleton(doc):
    """
    Constructs the master parametric wireframe skeleton in `doc`.
    """
    grp = doc.addObject("App::DocumentObjectGroup", "MasterSkeleton")
    grp.Label = "1. Master Skeleton & Datums"

    # 1. Radial Rays (A, B, C, D, E)
    ray_labels = ["Ray_A_136deg", "Ray_B_113deg", "Ray_C_090deg", "Ray_D_067deg", "Ray_E_044deg"]
    ray_r_max = LibraryDims.R_OUTER_FACET + 4000.0  # Extend slightly past outer wall

    for label, deg in zip(ray_labels, LibraryDims.PRIMARY_RAYS):
        pt_start = FreeCAD.Vector(0, 0, LibraryDims.Z_L3)
        pt_end = make_polar_point(ray_r_max, deg, LibraryDims.Z_L3)
        line = Part.makeLine(pt_start, pt_end)

        feat = doc.addObject("Part::Feature", label)
        feat.Label = label
        feat.Shape = line
        grp.addObject(feat)

    # 2. Concentric Guide Arcs on Level 3
    arc_configs = [
        ("Arc_SunkenWell_31ft10in", LibraryDims.R_WELL),
        ("Arc_Mezzanine_44ft", LibraryDims.R_MEZZ),
        ("Arc_ColumnRing_62ft", LibraryDims.R_COL_INTERMEDIATE),
        ("Arc_OuterPerimeter_92ft5in", LibraryDims.R_OUTER_FACET),
    ]

    for label, radius in arc_configs:
        # Arc from Ray E (44 deg) to Ray A (136 deg)
        p1 = make_polar_point(radius, LibraryDims.RAY_E_DEG, LibraryDims.Z_L3)
        p_mid = make_polar_point(radius, LibraryDims.RAY_C_DEG, LibraryDims.Z_L3)
        p2 = make_polar_point(radius, LibraryDims.RAY_A_DEG, LibraryDims.Z_L3)

        arc = Part.Arc(p1, p_mid, p2)
        feat = doc.addObject("Part::Feature", label)
        feat.Label = label
        feat.Shape = arc.toShape()
        grp.addObject(feat)

    # 3. Outer Faceted Chords (The polygon of straight wall segments)
    chord_pts = [
        make_polar_point(LibraryDims.R_OUTER_FACET, deg, LibraryDims.Z_L3)
        for deg in LibraryDims.PRIMARY_RAYS
    ]
    chord_wires = []
    for i in range(len(chord_pts) - 1):
        p_a = chord_pts[i]
        p_b = chord_pts[i+1]
        line = Part.makeLine(p_a, p_b)
        chord_wires.append(line)
        feat = doc.addObject("Part::Feature", f"FacetChord_Bay_{i+1}")
        feat.Label = f"Facet Chord Bay {i+1}"
        feat.Shape = line
        grp.addObject(feat)

    # 4. South Wing Cartesian Boundary Skeleton
    sw_corners = [
        FreeCAD.Vector(LibraryDims.SOUTH_WING_WEST_X, 0, LibraryDims.Z_L3),
        FreeCAD.Vector(LibraryDims.SOUTH_WING_WEST_X, LibraryDims.SOUTH_WALL_Y, LibraryDims.Z_L3),
        FreeCAD.Vector(LibraryDims.SOUTH_WING_EAST_X, LibraryDims.SOUTH_WALL_Y, LibraryDims.Z_L3),
        FreeCAD.Vector(LibraryDims.SOUTH_WING_EAST_X, 0, LibraryDims.Z_L3),
    ]
    sw_poly = Part.makePolygon(sw_corners + [sw_corners[0]])
    feat_sw = doc.addObject("Part::Feature", "SouthWing_Footprint")
    feat_sw.Label = "South Wing Footprint Wire"
    feat_sw.Shape = sw_poly
    grp.addObject(feat_sw)

    return grp
