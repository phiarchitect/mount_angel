"""
Layer 0: Constructive Regulating Grid & Working Points (`0_Regulating_Grid`).
Renders Alvar Aalto's polycentric regulating geometry directly in 3D space
at Level 3 datum (Z = +0.025 m) so it can be toggled on/off in IngeTrazo.
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

    # Primary Structural Rays B, C, D from WP #3 (2.60, -1.80) through Twin Columns & H-Columns
    for deg in (G.RAY_B_DEG, G.RAY_C_DEG, G.RAY_D_DEG):
        add_wall_strip_ft(mesh, [G.WP3, polar_pt(G.WP3, 98.0, deg)], 0.28, z0, z1, MATERIALS["reg_cyan"])

    # Outer Boundary Rays A & E from Lower Focus WP_LOWER
    add_wall_strip_ft(mesh, [G.WP4, G.WP_LOWER], 0.24, z0, z1, MATERIALS["reg_amber"])
    add_wall_strip_ft(mesh, [G.WP_LOWER, polar_pt(G.WP_LOWER, 96.0, G.RAY_A_DEG)], 0.28, z0, z1, MATERIALS["reg_amber"])
    add_wall_strip_ft(mesh, [G.WP_LOWER, polar_pt(G.WP_LOWER, 116.0, G.RAY_E_DEG)], 0.28, z0, z1, MATERIALS["reg_amber"])

    # R = 31'-10" Well Arc & Grid Line 6 Datum
    add_wall_strip_ft(mesh, arc_pts(G.WP3A, G.R_WELL_L2_WALL, 38.0, 162.0, 40), 0.24, z0, z1, MATERIALS["reg_purple"])
    add_wall_strip_ft(mesh, [(-132.0, 0.0), (80.0, 0.0)], 0.22, z0, z1, MATERIALS["reg_cyan"])

    # Working Point Cylinders (#4, #3, and #3A)
    add_cylinder_ft(mesh, G.WP4, 0.85, 0.0, 0.14, MATERIALS["reg_cyan"], sides=16)
    add_cylinder_ft(mesh, G.WP3, 0.75, 0.0, 0.14, MATERIALS["reg_cyan"], sides=16)
    add_cylinder_ft(mesh, G.WP3A, 0.75, 0.0, 0.14, MATERIALS["reg_purple"], sides=16)
    return grp
