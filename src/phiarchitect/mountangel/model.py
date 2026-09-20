"""
Mount Angel Library - Master Building Assembly Generator.
Assembles the complete 3D parametric building hierarchy in FreeCAD 1.1.
"""

import math
import FreeCAD
import Part
from phiarchitect.mountangel.params import LibraryDims, deg_to_rad, attach_varset, ft
from phiarchitect.mountangel.skeleton import build_skeleton, make_polar_point
from phiarchitect.mountangel.components.columns import make_round_column, make_h_pier
from phiarchitect.mountangel.components.skylights import make_curved_light_monitor, make_conical_skylight

def make_sector_polygon(r_inner, r_outer, start_deg, end_deg, z=0.0, n_divs=16):
    """
    Creates a planar polygon wire bounded by two concentric arcs and two radial rays.
    """
    step = (end_deg - start_deg) / float(n_divs)
    outer_pts = []
    inner_pts = []

    for i in range(n_divs + 1):
        deg = start_deg + i * step
        rad = deg_to_rad(deg)
        outer_pts.append(FreeCAD.Vector(r_outer * math.cos(rad), r_outer * math.sin(rad), z))
        inner_pts.append(FreeCAD.Vector(r_inner * math.cos(rad), r_inner * math.sin(rad), z))

    # Boundary order: outer arc forward, inner arc backward
    poly_pts = outer_pts + list(reversed(inner_pts)) + [outer_pts[0]]
    wire = Part.makePolygon(poly_pts)
    return Part.Face(wire)


def make_faceted_fan_slab(r_inner, chord_pts, start_deg, end_deg, z=0.0, thickness=LibraryDims.SLAB_THICKNESS, n_divs=16):
    """
    Creates a solid slab bounded by a faceted outer polygon and an inner arc.
    """
    step = (end_deg - start_deg) / float(n_divs)
    inner_pts = []
    for i in range(n_divs + 1):
        deg = start_deg + i * step
        rad = deg_to_rad(deg)
        inner_pts.append(FreeCAD.Vector(r_inner * math.cos(rad), r_inner * math.sin(rad), z))

    # Outer perimeter is formed by the faceted chord points
    outer_pts = [FreeCAD.Vector(p.x, p.y, z) for p in chord_pts]
    poly_pts = outer_pts + list(reversed(inner_pts)) + [outer_pts[0]]
    face = Part.Face(Part.makePolygon(poly_pts))
    # Extrude downward by thickness
    slab = face.extrude(FreeCAD.Vector(0, 0, -thickness))
    return slab


def build_library_model(doc):
    """
    Generates the complete Mount Angel Library 3D assembly.
    """
    # 0. Attach Central VarSet
    attach_varset(doc)

    # 1. Master Wireframe Skeleton
    build_skeleton(doc)

    # Calculate perimeter chord points
    chord_pts = [
        make_polar_point(LibraryDims.R_OUTER_FACET, deg, 0.0)
        for deg in LibraryDims.PRIMARY_RAYS
    ]

    # ---------------------------------------------------------
    # 2. Level 1 Structure (Base & Downhill Retaining Box)
    # ---------------------------------------------------------
    grp_l1 = doc.addObject("App::DocumentObjectGroup", "Level_1_Structure")
    grp_l1.Label = "2. Level 1 Structure (Downhill Base)"

    # L1 Fan Slab (from intermediate ring out to perimeter)
    l1_slab = make_faceted_fan_slab(
        r_inner=LibraryDims.R_COL_INTERMEDIATE,
        chord_pts=chord_pts,
        start_deg=LibraryDims.RAY_E_DEG,
        end_deg=LibraryDims.RAY_A_DEG,
        z=LibraryDims.Z_L1,
        thickness=LibraryDims.SLAB_THICKNESS
    )
    feat_l1 = doc.addObject("Part::Feature", "L1_Floor_Slab")
    feat_l1.Label = "Level 1 Floor Slab"
    feat_l1.Shape = l1_slab
    grp_l1.addObject(feat_l1)

    # ---------------------------------------------------------
    # 3. Level 2 Structure (Middle Tier & Sunken Well)
    # ---------------------------------------------------------
    grp_l2 = doc.addObject("App::DocumentObjectGroup", "Level_2_Structure")
    grp_l2.Label = "3. Level 2 Structure (Middle Tier)"

    # L2 Slab (from well boundary R_WELL out to perimeter)
    l2_slab = make_faceted_fan_slab(
        r_inner=LibraryDims.R_WELL,
        chord_pts=chord_pts,
        start_deg=LibraryDims.RAY_E_DEG,
        end_deg=LibraryDims.RAY_A_DEG,
        z=LibraryDims.Z_L2,
        thickness=LibraryDims.SLAB_THICKNESS
    )
    feat_l2 = doc.addObject("Part::Feature", "L2_Floor_Slab")
    feat_l2.Label = "Level 2 Floor Slab"
    feat_l2.Shape = l2_slab
    grp_l2.addObject(feat_l2)

    # Sunken Reading Pit Slab at Level 2 Base
    well_face = make_sector_polygon(
        r_inner=LibraryDims.R_DESK_INNER,
        r_outer=LibraryDims.R_WELL,
        start_deg=LibraryDims.RAY_E_DEG,
        end_deg=LibraryDims.RAY_A_DEG,
        z=LibraryDims.Z_L2
    )
    well_slab = well_face.extrude(FreeCAD.Vector(0, 0, -LibraryDims.SLAB_THICKNESS))
    feat_well = doc.addObject("Part::Feature", "L2_SunkenWell_Slab")
    feat_well.Label = "Level 2 Sunken Well Floor"
    feat_well.Shape = well_slab
    grp_l2.addObject(feat_well)

    # ---------------------------------------------------------
    # 4. Level 3 Structure (Main Deck & South Wing)
    # ---------------------------------------------------------
    grp_l3 = doc.addObject("App::DocumentObjectGroup", "Level_3_Structure")
    grp_l3.Label = "4. Level 3 Structure (Main Floor & Mezzanine)"

    # L3 Fan Slab (Mezzanine overhang from R_MEZZ to outer wall)
    l3_fan_slab = make_faceted_fan_slab(
        r_inner=LibraryDims.R_MEZZ,
        chord_pts=chord_pts,
        start_deg=LibraryDims.RAY_E_DEG,
        end_deg=LibraryDims.RAY_A_DEG,
        z=LibraryDims.Z_L3,
        thickness=LibraryDims.SLAB_THICKNESS
    )
    feat_l3_fan = doc.addObject("Part::Feature", "L3_Mezzanine_Slab")
    feat_l3_fan.Label = "Level 3 Mezzanine Deck"
    feat_l3_fan.Shape = l3_fan_slab
    grp_l3.addObject(feat_l3_fan)

    # L3 Connecting Lobby Floor (Spanning from South Wing to Sunken Well Edge)
    # Fills the floor between Y=0 and the well radius R_WELL
    lobby_wedge = make_sector_polygon(
        r_inner=LibraryDims.R_WELL,
        r_outer=LibraryDims.R_MEZZ,
        start_deg=LibraryDims.RAY_E_DEG,
        end_deg=LibraryDims.RAY_A_DEG,
        z=LibraryDims.Z_L3
    )
    lobby_slab = lobby_wedge.extrude(FreeCAD.Vector(0, 0, -LibraryDims.SLAB_THICKNESS))
    feat_lobby = doc.addObject("Part::Feature", "L3_Lobby_Mezzanine_Fill")
    feat_lobby.Label = "Level 3 Mezzanine Inner Ring"
    feat_lobby.Shape = lobby_slab
    grp_l3.addObject(feat_lobby)

    # L3 South Wing Slab (Rectilinear Entrance Block extending to Y=0)
    sw_w = LibraryDims.SOUTH_WING_EAST_X - LibraryDims.SOUTH_WING_WEST_X
    sw_d = abs(LibraryDims.SOUTH_WALL_Y)
    sw_box = Part.makeBox(
        sw_w, sw_d, LibraryDims.SLAB_THICKNESS,
        FreeCAD.Vector(LibraryDims.SOUTH_WING_WEST_X, LibraryDims.SOUTH_WALL_Y, LibraryDims.Z_L3 - LibraryDims.SLAB_THICKNESS)
    )
    feat_sw_slab = doc.addObject("Part::Feature", "L3_SouthWing_Slab")
    feat_sw_slab.Label = "Level 3 South Wing Slab"
    feat_sw_slab.Shape = sw_box
    grp_l3.addObject(feat_sw_slab)

    # Sunken Reading Well Stepped Terraces (Level 2 to Level 3)
    # Creates 3 stepped concentric tiers around the well
    n_tiers = 3
    dr = (LibraryDims.R_WELL - LibraryDims.R_DESK_INNER) / float(n_tiers + 1)
    dz = (LibraryDims.Z_L3 - LibraryDims.Z_L2) / float(n_tiers + 1)
    for t_idx in range(n_tiers):
        r_tier_inner = LibraryDims.R_DESK_INNER + (t_idx + 1) * dr
        r_tier_outer = LibraryDims.R_WELL
        z_tier = LibraryDims.Z_L2 + (t_idx + 1) * dz
        tier_face = make_sector_polygon(
            r_inner=r_tier_inner,
            r_outer=r_tier_outer,
            start_deg=LibraryDims.RAY_E_DEG,
            end_deg=LibraryDims.RAY_A_DEG,
            z=z_tier
        )
        tier_solid = tier_face.extrude(FreeCAD.Vector(0, 0, -dz))
        feat_tier = doc.addObject("Part::Feature", f"SunkenWell_Tier_{t_idx+1}")
        feat_tier.Label = f"Sunken Well Reading Tier #{t_idx+1}"
        feat_tier.Shape = tier_solid
        grp_l2.addObject(feat_tier)

    # ---------------------------------------------------------
    # 5. Columns & Structural Grid
    # ---------------------------------------------------------
    grp_col = doc.addObject("App::DocumentObjectGroup", "Structural_Columns")
    grp_col.Label = "5. Columns & Vertical Framing"

    # Intermediate Ring Round Concrete Columns
    # Located along primary rays at R_COL_INTERMEDIATE
    for i, deg in enumerate(LibraryDims.PRIMARY_RAYS):
        pt_col = make_polar_point(LibraryDims.R_COL_INTERMEDIATE, deg, LibraryDims.Z_L2)
        # Height from L2 to roof eave
        h_col = LibraryDims.Z_ROOF_EAVE - LibraryDims.Z_L2
        col_obj = make_round_column(
            doc,
            radius=LibraryDims.ROUND_COL_DIAMETER / 2.0,
            height=h_col,
            name=f"RoundColumn_Ray_{chr(ord('A') + i)}",
            origin=pt_col
        )
        col_obj.Label = f"Round Column Ray {chr(ord('A') + i)}"
        grp_col.addObject(col_obj)

    # Perimeter H-Piers at Facet Vertices
    for i, deg in enumerate(LibraryDims.PRIMARY_RAYS):
        pt_pier = make_polar_point(LibraryDims.R_OUTER_FACET, deg, LibraryDims.Z_L1)
        h_pier_total = LibraryDims.Z_ROOF_EAVE - LibraryDims.Z_L1
        pier_obj = make_h_pier(
            doc,
            depth=LibraryDims.H_PIER_DEPTH,
            width=LibraryDims.H_PIER_WIDTH,
            height=h_pier_total,
            name=f"HPier_Ray_{chr(ord('A') + i)}",
            origin=pt_pier,
            rotation_deg=deg - 90.0  # Align web with radial ray
        )
        pier_obj.Label = f"Perimeter H-Pier Ray {chr(ord('A') + i)}"
        grp_col.addObject(pier_obj)

    # ---------------------------------------------------------
    # 6. Exterior Envelope & Curtain Walls
    # ---------------------------------------------------------
    grp_env = doc.addObject("App::DocumentObjectGroup", "Exterior_Envelope")
    grp_env.Label = "6. Exterior Envelope & Facades"

    # Faceted Curtain Wall Panels (Between H-Piers)
    t_wall = LibraryDims.FACET_WALL_THICKNESS
    h_wall = LibraryDims.Z_ROOF_EAVE - LibraryDims.Z_L1

    for i in range(len(chord_pts) - 1):
        p1 = chord_pts[i]
        p2 = chord_pts[i+1]
        
        # Direction vector along chord
        v_chord = p2 - p1
        chord_len = v_chord.Length
        chord_dir = v_chord.normalize()
        # Normal vector pointing outward
        v_norm = FreeCAD.Vector(-chord_dir.y, chord_dir.x, 0)

        # Base corner
        base_corner = FreeCAD.Vector(p1.x, p1.y, LibraryDims.Z_L1)
        # Create solid wall segment along chord
        wall_box = Part.makeBox(chord_len, t_wall, h_wall)
        
        # Rotate wall to align with chord
        angle_chord = math.degrees(math.atan2(chord_dir.y, chord_dir.x))
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle_chord)
        wall_box.Placement = FreeCAD.Placement(base_corner, rot)

        # Create window ribbon opening cutout at Level 3
        win_h = ft(6, 0)
        win_sill = LibraryDims.Z_L3 + ft(2, 8)
        win_cutout = Part.makeBox(chord_len - ft(4, 0), t_wall * 2.0, win_h)
        win_pos = base_corner + chord_dir * ft(2, 0) - v_norm * (t_wall * 0.5)
        win_pos.z = win_sill
        win_cutout.Placement = FreeCAD.Placement(win_pos, rot)

        wall_solid = wall_box.cut(win_cutout)

        feat_wall = doc.addObject("Part::Feature", f"PerimeterWall_Bay_{i+1}")
        feat_wall.Label = f"Curtain Wall Bay {i+1} (Rays {chr(ord('A') + i)}-{chr(ord('A') + i + 1)})"
        feat_wall.Shape = wall_solid
        grp_env.addObject(feat_wall)

    # South Wing Solid Walls
    # South main facade wall
    s_wall_len = sw_w
    s_wall_h = LibraryDims.Z_ROOF_HIGH - LibraryDims.Z_L3
    s_wall = Part.makeBox(
        s_wall_len, LibraryDims.WALL_THICKNESS, s_wall_h,
        FreeCAD.Vector(LibraryDims.SOUTH_WING_WEST_X, LibraryDims.SOUTH_WALL_Y, LibraryDims.Z_L3)
    )
    feat_swall = doc.addObject("Part::Feature", "South_Facade_Wall")
    feat_swall.Label = "South Entrance Facade Wall"
    feat_swall.Shape = s_wall
    grp_env.addObject(feat_swall)

    # East and West end walls of South wing
    w_end_wall = Part.makeBox(
        LibraryDims.WALL_THICKNESS, sw_d, s_wall_h,
        FreeCAD.Vector(LibraryDims.SOUTH_WING_WEST_X, LibraryDims.SOUTH_WALL_Y, LibraryDims.Z_L3)
    )
    feat_wwall = doc.addObject("Part::Feature", "West_End_Wall")
    feat_wwall.Label = "South Wing West End Wall"
    feat_wwall.Shape = w_end_wall
    grp_env.addObject(feat_wwall)

    e_end_wall = Part.makeBox(
        LibraryDims.WALL_THICKNESS, sw_d, s_wall_h,
        FreeCAD.Vector(LibraryDims.SOUTH_WING_EAST_X - LibraryDims.WALL_THICKNESS, LibraryDims.SOUTH_WALL_Y, LibraryDims.Z_L3)
    )
    feat_ewall = doc.addObject("Part::Feature", "East_End_Wall")
    feat_ewall.Label = "South Wing East End Wall"
    feat_ewall.Shape = e_end_wall
    grp_env.addObject(feat_ewall)

    # South Entrance Canopy & Portico (Drawing 28-a27)
    c_w = LibraryDims.CANOPY_EAST_X - LibraryDims.CANOPY_WEST_X
    c_d = abs(LibraryDims.CANOPY_SOUTH_Y - LibraryDims.SOUTH_WALL_Y)
    canopy_slab = Part.makeBox(
        c_w, c_d, ft(0, 8),
        FreeCAD.Vector(LibraryDims.CANOPY_WEST_X, LibraryDims.CANOPY_SOUTH_Y, LibraryDims.CANOPY_ROOF_Z)
    )
    feat_canopy = doc.addObject("Part::Feature", "Entrance_Canopy_Roof")
    feat_canopy.Label = "South Entrance Canopy Roof"
    feat_canopy.Shape = canopy_slab
    grp_env.addObject(feat_canopy)

    # Canopy Slender Steel Posts
    post_radius = ft(0, 2)  # 4" pipe columns
    post_positions = [
        FreeCAD.Vector(LibraryDims.CANOPY_WEST_X + ft(1, 6), LibraryDims.CANOPY_SOUTH_Y + ft(1, 6), LibraryDims.Z_L3),
        FreeCAD.Vector(LibraryDims.CANOPY_EAST_X - ft(1, 6), LibraryDims.CANOPY_SOUTH_Y + ft(1, 6), LibraryDims.Z_L3),
    ]
    for p_idx, p_pos in enumerate(post_positions):
        post = Part.makeCylinder(post_radius, LibraryDims.CANOPY_ROOF_Z - LibraryDims.Z_L3, p_pos, FreeCAD.Vector(0, 0, 1))
        feat_post = doc.addObject("Part::Feature", f"Canopy_Post_{p_idx+1}")
        feat_post.Label = f"Canopy Column #{p_idx+1}"
        feat_post.Shape = post
        grp_env.addObject(feat_post)

    # ---------------------------------------------------------
    # 7. Roof & Signature Light Monitor Scoop
    # ---------------------------------------------------------
    grp_roof = doc.addObject("App::DocumentObjectGroup", "Roof_And_Skylights")
    grp_roof.Label = "7. Roof & Daylight Monitor"

    # Radial Roof over the Fan Bays
    fan_roof_slab = make_faceted_fan_slab(
        r_inner=LibraryDims.R_WELL + 1500.0,
        chord_pts=chord_pts,
        start_deg=LibraryDims.RAY_E_DEG,
        end_deg=LibraryDims.RAY_A_DEG,
        z=LibraryDims.Z_ROOF_EAVE,
        thickness=LibraryDims.SLAB_THICKNESS
    )
    feat_fan_roof = doc.addObject("Part::Feature", "Fan_Roof_Slab")
    feat_fan_roof.Label = "Fan Radial Roof Slab"
    feat_fan_roof.Shape = fan_roof_slab
    grp_roof.addObject(feat_fan_roof)

    # South Wing Roof
    sw_roof = Part.makeBox(
        sw_w, sw_d, LibraryDims.SLAB_THICKNESS,
        FreeCAD.Vector(LibraryDims.SOUTH_WING_WEST_X, LibraryDims.SOUTH_WALL_Y, LibraryDims.Z_ROOF_HIGH - LibraryDims.SLAB_THICKNESS)
    )
    feat_sw_roof = doc.addObject("Part::Feature", "SouthWing_Roof_Slab")
    feat_sw_roof.Label = "South Wing Roof Deck"
    feat_sw_roof.Shape = sw_roof
    grp_roof.addObject(feat_sw_roof)

    # Signature Curved Light Monitor Scoop over Central Well
    monitor_scoop = make_curved_light_monitor(
        doc,
        r_inner=LibraryDims.R_DESK_INNER,
        r_outer=LibraryDims.R_WELL + 1800.0,
        z_base=LibraryDims.Z_ROOF_EAVE,
        z_ridge=LibraryDims.Z_MONITOR_RIDGE,
        start_deg=LibraryDims.RAY_E_DEG,
        end_deg=LibraryDims.RAY_A_DEG,
        name="Aalto_Daylight_Monitor"
    )
    grp_roof.addObject(monitor_scoop)

    # Conical Skylights across South Wing & Mezzanine
    skylight_locs = [
        FreeCAD.Vector(-ft(30), -ft(24), LibraryDims.Z_ROOF_HIGH),
        FreeCAD.Vector(-ft(10), -ft(24), LibraryDims.Z_ROOF_HIGH),
        FreeCAD.Vector(ft(10), -ft(24), LibraryDims.Z_ROOF_HIGH),
        FreeCAD.Vector(ft(30), -ft(24), LibraryDims.Z_ROOF_HIGH),
    ]
    for idx, pos in enumerate(skylight_locs):
        sky = make_conical_skylight(doc, r_bottom=500.0, r_top=650.0, height=800.0, origin=pos, name=f"ConicalSkylight_{idx+1}")
        sky.Label = f"Conical Roof Lantern #{idx+1}"
        grp_roof.addObject(sky)

    return doc
