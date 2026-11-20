"""
Layer 0: Constructive Regulating Grid & Working Points (`0_Regulating_Grid`).
Renders Alvar Aalto's polycentric regulating geometry directly in 3D space
at Level 3 datum (Z = +0.025 m) so it can be toggled on/off in IngeTrazo:
  - WP #3 (0, 0): Structural convergence hub of Rays B (137.0°), C (99.4°), D (64.5°)
  - WP #2 (+2'-10", -5'-3"): Lower convergence hub of Outer Boundary Rays A (168.3°) & E (40.3°)
  - WP #3A (+1'-7 3/8", +3'-4 5/8" on Ray D): Center of the R = 31'-10" Reading Well & Daylight Scoop
"""

from __future__ import annotations

from phiarchitect.mountangel.vectors import AaltoGeometry, arc_pts, polar_pt

from .primitives import (
    MATERIALS,
    add_cylinder_ft,
    add_wall_strip_ft,
    create_scene_group,
)


def build_regulating_lines(scene):
    grp = create_scene_group(scene, "0_Regulating_Grid")
    mesh = grp.mesh
    G = AaltoGeometry
    z0, z1 = 0.018, 0.045

    # Primary Structural Rays B, C, D from WP #3 (0, 0) through Well Columns, Twin Columns & H-Columns
    for deg, r_max in ((G.RAY_B_DEG, 92.0), (G.RAY_C_DEG, 95.0), (G.RAY_D_DEG, 103.0)):
        add_wall_strip_ft(mesh, [G.WP3, polar_pt(G.WP3, r_max, deg)], 0.28, z0, z1, MATERIALS["reg_cyan"])

    # Outer Boundary Rays A & E from Lower Hub WP #2 (+2'-10", -5'-3")
    add_wall_strip_ft(mesh, [G.WP3, G.WP2], 0.24, z0, z1, MATERIALS["reg_amber"])
    add_wall_strip_ft(mesh, [G.WP2, polar_pt(G.WP2, 96.0, G.RAY_A_DEG)], 0.28, z0, z1, MATERIALS["reg_amber"])
    add_wall_strip_ft(mesh, [G.WP2, polar_pt(G.WP2, 125.0, G.RAY_E_DEG)], 0.28, z0, z1, MATERIALS["reg_amber"])

    # R = 31'-10" Well Arc (centered at WP #3A) & Grid Line 6 Datum
    add_wall_strip_ft(mesh, arc_pts(G.WP3A, G.R_WELL_L2_WALL, 38.0, 162.0, 40), 0.24, z0, z1, MATERIALS["reg_purple"])
    add_wall_strip_ft(mesh, [(-134.0, 0.0), (80.0, 0.0)], 0.22, z0, z1, MATERIALS["reg_cyan"])

    # Working Point Cylinders (#3, #2, and #3A)
    add_cylinder_ft(mesh, G.WP3, 0.85, 0.0, 0.14, MATERIALS["reg_cyan"], sides=16)
    add_cylinder_ft(mesh, G.WP2, 0.75, 0.0, 0.14, MATERIALS["reg_amber"], sides=16)
    add_cylinder_ft(mesh, G.WP3A, 0.75, 0.0, 0.14, MATERIALS["reg_purple"], sides=16)
    return grp
