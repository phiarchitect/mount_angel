"""
Mount Angel Library - Skylights and Light Scoop Components.
Implements the signature Alvar Aalto daylight monitor scoop and circular conical skylights.
"""

import math
import FreeCAD
import Part
from phiarchitect.mountangel.params import LibraryDims, deg_to_rad

def make_conical_skylight(doc, r_bottom=500.0, r_top=650.0, height=800.0, origin=None, name="ConicalSkylight"):
    """
    Creates Aalto's classic conical ceiling/roof daylight lantern.
    """
    if origin is None:
        origin = FreeCAD.Vector(0, 0, 0)

    cone = Part.makeCone(r_bottom, r_top, height, origin, FreeCAD.Vector(0, 0, 1))
    feat = doc.addObject("Part::Feature", name)
    feat.Label = name
    feat.Shape = cone
    return feat


def make_curved_light_monitor(doc, r_inner=None, r_outer=None, z_base=None, z_ridge=None,
                               start_deg=44.0, end_deg=136.0, name="DaylightMonitorScoop"):
    """
    Creates the iconic curved daylight monitor scoop over the central sunken well.
    Profiles along Section A-A swept across the angular arc above the circulation desk.
    """
    if r_inner is None:
        r_inner = LibraryDims.R_DESK_INNER
    if r_outer is None:
        r_outer = LibraryDims.R_WELL + 2000.0
    if z_base is None:
        z_base = LibraryDims.Z_ROOF_EAVE
    if z_ridge is None:
        z_ridge = LibraryDims.Z_MONITOR_RIDGE

    # Generate an arc shell spanning from start_deg to end_deg
    # The monitor has a sloping/curved profile rising to z_ridge
    n_steps = 16
    angle_step = (end_deg - start_deg) / float(n_steps)

    # We construct a curved volumetric wedge representing the monitor scoop
    pts_lower = []
    pts_upper = []
    for i in range(n_steps + 1):
        deg = start_deg + i * angle_step
        rad = deg_to_rad(deg)
        # Inner curve at roof level
        pts_lower.append(FreeCAD.Vector(r_inner * math.cos(rad), r_inner * math.sin(rad), z_base))
        # Outer high ridge curve at monitor peak
        pts_upper.append(FreeCAD.Vector(r_outer * math.cos(rad), r_outer * math.sin(rad), z_ridge))

    # Build loft between lower and upper arcs
    wire_lower = Part.makePolygon(pts_lower)
    wire_upper = Part.makePolygon(pts_upper)
    
    # Create ruled surface and thicken into shell
    surf = Part.makeRuledSurface(wire_lower, wire_upper)
    # Thicken downward by 200 mm
    solid = surf.makeOffsetShape(200.0, 0.01, fill=True)

    feat = doc.addObject("Part::Feature", name)
    feat.Label = name
    feat.Shape = solid
    return feat
