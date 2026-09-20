"""
Mount Angel Library - Column Components.
Implements reusable interior round columns and exterior perimeter H-piers.
"""

import math
import FreeCAD
import Part
from phiarchitect.mountangel.params import LibraryDims

def make_round_column(doc, radius=None, height=None, name="RoundColumn", origin=None):
    """
    Creates an interior circular concrete column with base centered at `origin`.
    """
    if radius is None:
        radius = LibraryDims.ROUND_COL_DIAMETER / 2.0
    if height is None:
        height = LibraryDims.Z_ROOF_EAVE - LibraryDims.Z_L3
    if origin is None:
        origin = FreeCAD.Vector(0, 0, 0)

    # Create cylinder aligned along Z
    cyl = Part.makeCylinder(radius, height, origin, FreeCAD.Vector(0, 0, 1))

    feat = doc.addObject("Part::Feature", name)
    feat.Label = name
    feat.Shape = cyl
    return feat


def make_h_pier(doc, depth=None, width=None, height=None, name="HPier", origin=None, rotation_deg=0.0):
    """
    Creates Aalto's signature H-shaped perimeter masonry/structural pier.
    Base centered at `origin`, rotated by `rotation_deg` around Z so its web
    aligns with the radial ray.
    """
    if depth is None:
        depth = LibraryDims.H_PIER_DEPTH      # Length along radial ray (~42")
    if width is None:
        width = LibraryDims.H_PIER_WIDTH      # Width across facet chords (~28")
    if height is None:
        height = LibraryDims.Z_ROOF_EAVE - LibraryDims.Z_L3
    if origin is None:
        origin = FreeCAD.Vector(0, 0, 0)

    t_flange = width * 0.35
    t_web = depth * 0.25

    # Build 2D H-profile in XY plane centered at (0, 0)
    # Flange 1 (outer)
    f1 = Part.makeBox(width, t_flange, height, FreeCAD.Vector(-width/2.0, depth/2.0 - t_flange, 0))
    # Flange 2 (inner)
    f2 = Part.makeBox(width, t_flange, height, FreeCAD.Vector(-width/2.0, -depth/2.0, 0))
    # Web (central connecting bar)
    web = Part.makeBox(t_web, depth - 2 * t_flange, height, FreeCAD.Vector(-t_web/2.0, -depth/2.0 + t_flange, 0))

    pier_shape = f1.fuse(f2).fuse(web)

    # Apply rotation around Z axis, then translation to origin
    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), rotation_deg)
    placement = FreeCAD.Placement(origin, rot)
    pier_shape.Placement = placement

    feat = doc.addObject("Part::Feature", name)
    feat.Label = name
    feat.Shape = pier_shape
    return feat
