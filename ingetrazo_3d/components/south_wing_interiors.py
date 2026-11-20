"""
Alvar Aalto South Wing Interior Architecture (Mount Angel Abbey Library, 1970).
==============================================================================
Populates Layer 4 (`4_Level_3_Reading_Room`) with Alvar Aalto's South Entrance
Wing interior architecture derived from archival construction drawings:
  - Sheet 05-a5 (Main Level 3 Floor Plan)
  - Sheet 17-a17 (Wall Sections & Section 4 through Rare Book & Meeting Room)
  - Sheet 23-a23 (Stairs, Elevator & Auditorium Details)
  - Sheet 24-a24 (Glazed Airlock Screen, Wood Screens & Millwork Details)
  - Sheet 28-a27 (Restrooms 314 & 315 Layouts, Screen Elevations & Details)
  - Archival Photo `media_1794669876127_dee7257f.png` (South Wing Floor Plan)

Architectural Elements:
  1. Glazed Inner Lobby / Vestibule Airlock Screen (Y = -50.8 ft, X = -18.0..0.0 ft)
     with dark-bronze mullions framing 3 pairs of glazed entry doors + push bars.
  2. Restrooms (Men 314 & Women 315) with white-plaster partitions, recessed birch
     doors, and Alvar Aalto's signature freestanding 32-batten vertical birch privacy
     screen in bronze ceiling/floor channels.
  3. Chair Storage 341 & Rare Book Vault 342 with double doors into Auditorium,
     janitor/mech cross walls, heavy bronze/steel vault door, and single-sided Aalto
     birch rare-book shelving.
  4. Rare Book & Meeting Room (Auditorium 327):
     - Splayed west acoustic lobby-dividing wall with double birch doors.
     - Sweeping S-curved Audio Visual Control Booth 328 with raised platform and
       horizontal projection window slot.
     - Quarter-circle SE corner stage/dais with 2 curved steps, faceted hemlock
       batten acoustic backdrop screen, and birch lectern.
     - 6 concentric/angled rows of Aalto lecture seating (slate cushions, birch frames)
       with center aisle facing the SE stage.
     - Iconic 3-wave undulating suspended acoustic plaster ceiling (Z = +3.95..+4.55 m).

All elements are constructed as 100% watertight 2-manifold solids (`unpaired == 0`).
"""

from __future__ import annotations

import math

from phiarchitect.mountangel.vectors import (
    AaltoGeometry as G,
)
from phiarchitect.mountangel.vectors import (
    arc_pts,
)

from .aalto_bookcases import add_aalto_bookcase_ft
from .primitives import (
    MATERIALS,
    add_cylinder_ft,
    add_extruded_polygon_ft,
    add_oriented_box_ft,
    add_quad,
    add_wall_strip_ft,
    m_ft,
)


def _furn(mat_key: str, **kwargs) -> dict:
    """Return material dictionary with 'furniture': True for cutaway visibility."""
    base = MATERIALS.get(mat_key, {"color": (0.82, 0.63, 0.40), "roughness": 0.54, "metallic": 0.05})
    return {**base, "furniture": True, **kwargs}


# =============================================================================
# A. GLAZED INNER VESTIBULE AIRLOCK SCREEN (Sheet 24-a24)
# =============================================================================

def _add_glazed_vestibule_screen(mesh, z_lobby: float, z_head: float) -> None:
    """
    Inner glazed airlock screen along Grid 2 (`Y = -51'-8"`, `X = -18.5..0.0 ft`).
    Framed with dark-bronze tubular mullions housing 3 pairs of glazed entry doors.
    """
    bronze = MATERIALS["mullion_bronze"]
    glass = MATERIALS["glass_clear"]
    push_mat = _furn("railing_bronze")
    z_door_top = z_lobby + 2.13  # 7'-0" door opening head
    y_center = G.GRID_Y["2"]
    x_v0, x_v1 = -18.5, 0.0
    x_mid = 0.5 * (x_v0 + x_v1)
    span_w = x_v1 - x_v0
    bay_w = span_w / 3.0

    # 1. Continuous top head channel
    add_oriented_box_ft(
        mesh,
        center_ft=(x_mid, y_center),
        length_ft=span_w,
        width_ft=0.35,
        angle_deg=0.0,
        z0_m=z_head - 0.04,
        z1_m=z_head,
        attrs=bronze,
    )

    # 2. Continuous horizontal transom bar at door head
    add_oriented_box_ft(
        mesh,
        center_ft=(x_mid, y_center),
        length_ft=span_w,
        width_ft=0.35,
        angle_deg=0.0,
        z0_m=z_door_top,
        z1_m=z_door_top + 0.06,
        attrs=bronze,
    )

    # 3. Recessed floor threshold channel
    add_oriented_box_ft(
        mesh,
        center_ft=(x_mid, y_center),
        length_ft=span_w,
        width_ft=0.35,
        angle_deg=0.0,
        z0_m=z_lobby,
        z1_m=z_lobby + 0.035,
        attrs=bronze,
    )

    # 4. Main vertical bronze mullions dividing the 3 double-door bays
    for k in range(4):
        vx = x_v0 + k * bay_w
        add_oriented_box_ft(
            mesh,
            center_ft=(vx, y_center),
            length_ft=0.36,
            width_ft=0.36,
            angle_deg=0.0,
            z0_m=z_lobby,
            z1_m=z_head,
            attrs=bronze,
        )

    # 5. Transom clerestory glass panes above each bay
    bay_centers = [x_v0 + (k + 0.5) * bay_w for k in range(3)]
    for bx in bay_centers:
        add_oriented_box_ft(
            mesh,
            center_ft=(bx, y_center),
            length_ft=bay_w - 0.40,
            width_ft=0.06,
            angle_deg=0.0,
            z0_m=z_door_top + 0.06,
            z1_m=z_head - 0.04,
            attrs=glass,
        )

    # 6. Three pairs of glazed entry doors with dark-bronze perimeter stiles & push bars
    for bx in bay_centers:
        add_oriented_box_ft(
            mesh,
            center_ft=(bx, y_center),
            length_ft=0.14,
            width_ft=0.30,
            angle_deg=0.0,
            z0_m=z_lobby + 0.035,
            z1_m=z_door_top,
            attrs=bronze,
        )
        for offset_x in (-1.48, 1.48):
            leaf_cx = bx + offset_x
            leaf_len = 2.75
            add_oriented_box_ft(mesh, (leaf_cx, y_center), leaf_len, 0.22, 0.0, z_lobby + 0.035, z_lobby + 0.22, bronze)
            add_oriented_box_ft(mesh, (leaf_cx, y_center), leaf_len, 0.22, 0.0, z_door_top - 0.10, z_door_top, bronze)
            add_oriented_box_ft(mesh, (leaf_cx - leaf_len * 0.44, y_center), 0.20, 0.22, 0.0, z_lobby + 0.22, z_door_top - 0.10, bronze)
            add_oriented_box_ft(mesh, (leaf_cx + leaf_len * 0.44, y_center), 0.20, 0.22, 0.0, z_lobby + 0.22, z_door_top - 0.10, bronze)
            add_oriented_box_ft(mesh, (leaf_cx, y_center), leaf_len - 0.44, 0.04, 0.0, z_lobby + 0.22, z_door_top - 0.10, glass)
            add_oriented_box_ft(mesh, (leaf_cx, y_center), leaf_len - 0.10, 0.10, 0.0, z_lobby + 0.90, z_lobby + 0.96, push_mat)


# =============================================================================
# B. RESTROOMS 314 & 315 & FREESTANDING WOODEN SCREEN (Sheets 05-a5 & 28-a27)
# =============================================================================

def _add_restrooms_and_screen(mesh, z_lobby: float, z_s_ceil: float) -> None:
    """
    Restroom enclosure walls for Men 314 and Women 315 west of Lobby 317,
    recessed birch doors, and Aalto's signature 32-batten vertical privacy screen.
    """
    plaster = MATERIALS["white_plaster"]
    bronze = MATERIALS["railing_bronze"]
    birch_furn = _furn("birch_wood")

    z_bot = z_lobby + 0.005
    z_top = z_s_ceil - 0.02
    z_lintel_bot = z_lobby + 2.13
    w_th = 0.45
    y_n = G.GRID_Y["3"]          # -29'-0"
    y_s = G.GRID_Y["2"] + 0.80   # -50.87 ft
    y_mid = 0.5 * (y_n + y_s)    # -39.93 ft
    x_w, x_e = -54.0, -34.5

    # 1. North corridor wall
    add_wall_strip_ft(mesh, [(x_w, y_n), (x_e, y_n)], w_th, z_bot, z_top, plaster)
    # 2. Central dividing wall between Men 314 and Women 315
    add_wall_strip_ft(mesh, [(x_w, y_mid), (x_e, y_mid)], w_th, z_bot, z_top, plaster)
    # 3. West boundary wall
    add_wall_strip_ft(mesh, [(x_w, y_s), (x_w, y_n)], w_th, z_bot, z_top, plaster)
    # 4. South wall
    add_wall_strip_ft(mesh, [(x_w, y_s), (x_e, y_s)], w_th, z_bot, z_top, plaster)

    # 5. East wall facing the screen alcove (solid segments + 2 doorway lintels)
    add_wall_strip_ft(mesh, [(x_e, y_s), (x_e, -46.2)], w_th, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(x_e, -43.2), (x_e, -36.5)], w_th, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(x_e, -33.5), (x_e, y_n)], w_th, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(x_e, -46.2), (x_e, -43.2)], w_th, z_lintel_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(x_e, -36.5), (x_e, -33.5)], w_th, z_lintel_bot, z_top, plaster)

    # 6. Recessed birch restroom doors
    for y_d in (-44.7, -35.0):
        add_oriented_box_ft(mesh, (x_e, y_d), 2.90, 0.16, 90.0, z_lobby + 0.01, z_lintel_bot, birch_furn)

    # 7. Signature Freestanding Wood Batten Privacy Screen (SCREEN on Sheet 05-a5 & 28-a27)
    x_scr = -30.0
    add_oriented_box_ft(mesh, (x_scr, -39.2), 13.4, 0.34, 90.0, z_lobby, z_lobby + 0.06, bronze)
    add_oriented_box_ft(mesh, (x_scr, -39.2), 13.4, 0.34, 90.0, z_s_ceil - 0.08, z_s_ceil - 0.02, bronze)

    y_start, y_end = -45.7, -32.7
    n_battens = 32
    step_y = (y_end - y_start) / (n_battens - 1)
    for i in range(n_battens):
        yk = y_start + i * step_y
        add_oriented_box_ft(mesh, (x_scr, yk), 0.22, 0.16, 90.0, z_lobby + 0.06, z_s_ceil - 0.08, birch_furn)


# =============================================================================
# C. CHAIR STORAGE 341 & RARE BOOK VAULT 342 (Sheets 05-a5 & 23-a23)
# =============================================================================

def _add_vault_and_storage(mesh, z_lobby: float, z_s_ceil: float) -> None:
    """
    Constructs Chair Storage 341, Rare Book Vault 342, dividing cross-walls,
    vault security door, and Aalto single-sided rare-book shelving.
    """
    plaster = MATERIALS["white_plaster"]
    steel = _furn("steel_pier")
    brass = _furn("brass")
    birch_furn = _furn("birch_wood")

    z_bot = z_lobby + 0.005
    z_top = z_s_ceil - 0.02
    z_head = z_lobby + 2.13
    z_vdoor = z_lobby + 2.00
    y_g5 = G.GRID_Y["5"]
    y_g4 = G.GRID_Y["4"]
    x_v_east = G.X_AUD_E - 1.5  # +60.92 ft

    # 1. Corridor / Vault North wall along Grid 5
    add_wall_strip_ft(mesh, [(18.8, y_g5), (G.X_LOUNGE_E - 0.6, y_g5)], 0.55, z_bot, z_top, plaster)

    # 2. Auditorium / Vault dividing wall along Grid 4 with double-door opening at X = 42.0..47.0 ft
    add_wall_strip_ft(mesh, [(18.5, y_g4), (42.0, y_g4)], 0.65, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(47.0, y_g4), (x_v_east, y_g4)], 0.65, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(42.0, y_g4), (47.0, y_g4)], 0.65, z_head, z_top, plaster)
    add_oriented_box_ft(mesh, (44.5, y_g4), 4.90, 0.18, 0.0, z_lobby + 0.01, z_head, birch_furn)

    # 3. Janitor / Mechanical cross-wall at X = 26.0 ft
    add_wall_strip_ft(mesh, [(26.0, y_g4), (26.0, y_g5)], 0.45, z_bot, z_top, plaster)

    # 4. Storage 341 / Vault 342 dividing wall at X = 37.0 ft with security vault door
    add_wall_strip_ft(mesh, [(37.0, y_g4), (37.0, -16.8)], 0.55, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(37.0, -13.8), (37.0, y_g5)], 0.55, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(37.0, -16.8), (37.0, -13.8)], 0.55, z_vdoor, z_top, plaster)
    add_oriented_box_ft(mesh, (37.0, -15.3), 2.90, 0.32, 90.0, z_lobby + 0.01, z_vdoor, steel)
    add_cylinder_ft(mesh, (37.22, -15.3), 0.52, z_lobby + 1.20, z_lobby + 1.25, brass, sides=16)

    # 5. Aalto single-sided rare-book shelving inside Rare Book Vault 342 (6 open shelves)
    add_aalto_bookcase_ft(
        mesh,
        center_ft=(44.2, y_g5 - 0.80),
        length_ft=12.4,
        depth_ft=1.15,
        angle_deg=180.0,
        z_floor_m=z_lobby,
        height_m=2.15,
        double_sided=False,
        n_shelf_tiers=6,
        canopy_style="birch",
        end_slats="none",
        populate_books=True,
        seed=3421,
    )
    add_aalto_bookcase_ft(
        mesh,
        center_ft=(50.8, 0.5 * (y_g5 + y_g4)),
        length_ft=8.8,
        depth_ft=1.15,
        angle_deg=90.0,
        z_floor_m=z_lobby,
        height_m=2.15,
        double_sided=False,
        n_shelf_tiers=6,
        canopy_style="birch",
        end_slats="none",
        populate_books=True,
        seed=3422,
    )


# =============================================================================
# D. AUDITORIUM 327 (RARE BOOK & MEETING ROOM) (Sheets 17-a17 & 23-a23)
# =============================================================================

def _add_auditorium(mesh, z_lobby: float, z_s_ceil: float) -> None:
    """
    Constructs Alvar Aalto's iconic Rare Book & Meeting Room 327:
      - Splayed west acoustic lobby wall with double birch entry doors.
      - Sweeping S-curved Audio Visual Control Booth 328 with raised platform
        and horizontal projection window slot.
      - Quarter-circle SE corner stage platform with 2 curved steps, hemlock batten
        acoustic backdrop screen, and birch lectern.
      - 6 concentric/angled rows of lecture seating facing the stage.
      - 3-wave undulating suspended acoustic ceiling.
    """
    plaster = MATERIALS["white_plaster"]
    glass = MATERIALS["glass_clear"]
    bronze = MATERIALS["mullion_bronze"]
    birch_furn = _furn("birch_wood")
    slate_furn = _furn("book_slate")
    hemlock_furn = _furn("hemlock_slat")
    floor_booth = MATERIALS["floor_lobby"]

    z_aud_wall_top = m_ft(G.Z_AUDITORIUM_ROOF_FT) - 0.68  # +4.76 m (strictly below +4.80 m roof slab soffit!)
    z_door_top = z_lobby + 2.13
    y_g4 = G.GRID_Y["4"]
    y_g2 = G.GRID_Y["2"]
    y_g1 = G.GRID_Y["1"]

    # 1. Splayed West Acoustic Lobby-Dividing Wall: (X_LOBBY_E_G2 + 0.3, Grid 2 + 0.6) -> (18.5, Grid 4)
    x_s0, y_s0 = G.X_LOBBY_E_G2 + 0.3, y_g2 + 0.6
    x_s1, y_s1 = 18.5, y_g4
    y_d0, y_d1 = -43.8, -38.2
    x_d_south = x_s0 + ((y_d0 - y_s0) / (y_s1 - y_s0)) * (x_s1 - x_s0)
    x_d_north = x_s0 + ((y_d1 - y_s0) / (y_s1 - y_s0)) * (x_s1 - x_s0)
    w_splay = 0.70

    add_wall_strip_ft(mesh, [(x_s0, y_s0), (x_d_south, y_d0)], w_splay, z_lobby + 0.005, z_aud_wall_top, plaster)
    add_wall_strip_ft(mesh, [(x_d_north, y_d1), (x_s1, y_s1)], w_splay, z_lobby + 0.005, z_aud_wall_top, plaster)
    add_wall_strip_ft(mesh, [(x_d_south, y_d0), (x_d_north, y_d1)], w_splay, z_door_top, z_aud_wall_top, plaster)
    splay_deg = math.degrees(math.atan2(y_s1 - y_s0, x_s1 - x_s0))
    add_oriented_box_ft(
        mesh,
        center_ft=((x_d_south + x_d_north) * 0.5, 0.5 * (y_d0 + y_d1)),
        length_ft=5.50,
        width_ft=0.20,
        angle_deg=splay_deg,
        z0_m=z_lobby + 0.01,
        z1_m=z_door_top,
        attrs=birch_furn,
    )

    # 2. Sweeping Curved Audio Visual Control Booth 328 (Sheet 23-a23)
    booth_curve_pts = [
        (18.8, -27.4),
        (21.4, -27.9),
        (25.0, -27.8),
        (27.5, -26.9),
        (29.0, -25.6),
        (30.8, -23.8),
        (32.1, y_g4 - 0.3),
    ]
    booth_floor_poly = [(18.6, y_g4 - 0.3), (18.6, -27.4)] + booth_curve_pts + [(32.1, y_g4 - 0.3)]
    add_extruded_polygon_ft(mesh, booth_floor_poly, z_lobby, z_lobby + 0.76, floor_booth)

    z_booth_top = 4.10
    add_wall_strip_ft(mesh, booth_curve_pts, 0.50, z_lobby + 0.01, z_lobby + 1.10, plaster)
    slot_curve = booth_curve_pts[1:5]
    add_wall_strip_ft(mesh, slot_curve, 0.08, z_lobby + 1.10, z_lobby + 1.60, glass)
    add_wall_strip_ft(mesh, slot_curve, 0.28, z_lobby + 1.08, z_lobby + 1.10, bronze)
    add_wall_strip_ft(mesh, slot_curve, 0.28, z_lobby + 1.60, z_lobby + 1.62, bronze)
    add_wall_strip_ft(mesh, booth_curve_pts[0:2], 0.50, z_lobby + 1.10, z_lobby + 1.60, plaster)
    add_wall_strip_ft(mesh, booth_curve_pts[4:7], 0.50, z_lobby + 1.10, z_lobby + 1.60, plaster)
    add_wall_strip_ft(mesh, booth_curve_pts, 0.50, z_lobby + 1.60, z_booth_top, plaster)

    # 3. Quarter-Circle SE Corner Stage / Dais anchored to WP #1 (`X_AUD_E`, `Grid 1`)
    stage_center = (G.X_AUD_E - 1.35, y_g1 + 1.35)  # (+61.07, -59.65)
    poly_stage = [stage_center] + [p for p in arc_pts(stage_center, 15.8, 90.0, 180.0, 20)]
    add_extruded_polygon_ft(mesh, poly_stage, z_lobby + 0.005, z_lobby + 0.52, birch_furn)

    poly_step1 = [p for p in arc_pts(stage_center, 17.6, 90.0, 180.0, 20)] + [
        p for p in arc_pts(stage_center, 16.7, 180.0, 90.0, 20)
    ]
    add_extruded_polygon_ft(mesh, poly_step1, z_lobby + 0.005, z_lobby + 0.17, birch_furn)

    poly_step2 = [p for p in arc_pts(stage_center, 16.7, 90.0, 180.0, 20)] + [
        p for p in arc_pts(stage_center, 15.8, 180.0, 90.0, 20)
    ]
    add_extruded_polygon_ft(mesh, poly_step2, z_lobby + 0.005, z_lobby + 0.35, birch_furn)

    # Acoustic Vertical Hemlock Batten Backdrop Screen behind stage
    x_scr_e = G.X_AUD_E - 1.65
    y_scr_s = y_g1 + 1.65
    for i in range(36):
        yk = y_scr_s + i * (16.5 / 35.0)
        add_oriented_box_ft(mesh, (x_scr_e, yk), 0.20, 0.12, 90.0, z_lobby + 0.52, z_booth_top, hemlock_furn)
    for i in range(36):
        xk = (x_scr_e - 16.2) + i * (16.2 / 35.0)
        add_oriented_box_ft(mesh, (xk, y_scr_s), 0.20, 0.12, 0.0, z_lobby + 0.52, z_booth_top, hemlock_furn)

    # Aalto Birch Lectern on the Stage
    add_oriented_box_ft(mesh, (stage_center[0] - 7.7, stage_center[1] + 7.7), 1.80, 1.40, 135.0, z_lobby + 0.52, z_lobby + 1.45, birch_furn)
    add_oriented_box_ft(mesh, (stage_center[0] - 7.9, stage_center[1] + 7.9), 2.00, 1.50, 135.0, z_lobby + 1.45, z_lobby + 1.62, birch_furn)

    # 4. Concentric / Angled Auditorium Seating Rows (6 rows, ~8 seats per row with center aisle)
    row_radii = (22.0, 25.5, 29.0, 32.5, 36.0, 39.5)
    chair_angles = (106.5, 113.5, 120.5, 127.5, 142.5, 149.5, 156.5, 163.5)

    for r_seat in row_radii:
        for ang_deg in chair_angles:
            ang_rad = math.radians(ang_deg)
            cx = stage_center[0] + r_seat * math.cos(ang_rad)
            cy = stage_center[1] + r_seat * math.sin(ang_rad)
            rot_deg = (ang_deg + 180.0) % 360.0
            rot_rad = math.radians(rot_deg)
            ux, uy = math.cos(rot_rad), math.sin(rot_rad)

            add_oriented_box_ft(mesh, (cx, cy), 1.65, 1.55, rot_deg + 90.0, z_lobby + 0.38, z_lobby + 0.46, slate_furn)
            back_cx = cx - 0.65 * ux
            back_cy = cy - 0.65 * uy
            add_oriented_box_ft(mesh, (back_cx, back_cy), 1.65, 0.20, rot_deg + 90.0, z_lobby + 0.46, z_lobby + 0.82, slate_furn)
            nx, ny = -uy, ux
            for arm_sign in (-1.0, 1.0):
                arm_cx = cx + arm_sign * 0.78 * nx
                arm_cy = cy + arm_sign * 0.78 * ny
                add_oriented_box_ft(mesh, (arm_cx, arm_cy), 1.50, 0.10, rot_deg, z_lobby, z_lobby + 0.60, birch_furn)
                add_oriented_box_ft(mesh, (arm_cx, arm_cy), 1.35, 0.16, rot_deg, z_lobby + 0.58, z_lobby + 0.63, birch_furn)

    # 5. Iconic 3-Wave Undulating Suspended Acoustic Plaster Ceiling (Sheet 17-a17 Section 4)
    _add_auditorium_acoustic_ceiling(mesh)


# =============================================================================
# E. ICONIC UNDULATING ACOUSTIC PLASTER CEILING (Sheet 17-a17 Section 4)
# =============================================================================

def _add_auditorium_acoustic_ceiling(mesh) -> None:
    """
    Spanning cleanly inside the Auditorium walls at Z ≈ +3.78..+4.44 m
    (well below the +4.80 m Auditorium roof slab soffit).
    """
    soffit_attrs = MATERIALS["white_soffit"]
    top_attrs = MATERIALS["white_plaster"]

    x_min, x_max = 19.5, G.X_AUD_E - 1.65
    y_min, y_max = G.GRID_Y["1"] + 1.65, G.GRID_Y["4"] - 0.80
    steps = 24
    t_thick = 0.18

    xs = [x_min + (x_max - x_min) * (i / steps) for i in range(steps + 1)]
    us = [i / steps for i in range(steps + 1)]
    zs_bot = [4.02 + 0.24 * math.sin(3.0 * math.pi * u) - 0.12 * u for u in us]
    zs_top = [zb + t_thick for zb in zs_bot]

    xs_m = [m_ft(x) for x in xs]
    y0_m = m_ft(y_min)
    y1_m = m_ft(y_max)

    for i in range(steps):
        x0, x1 = xs_m[i], xs_m[i + 1]
        z0, z1 = zs_bot[i], zs_bot[i + 1]
        add_quad(mesh, (x0, y0_m, z0), (x0, y1_m, z0), (x1, y1_m, z1), (x1, y0_m, z1), soffit_attrs)

    for i in range(steps):
        x0, x1 = xs_m[i], xs_m[i + 1]
        z0, z1 = zs_top[i], zs_top[i + 1]
        add_quad(mesh, (x0, y0_m, z0), (x1, y0_m, z1), (x1, y1_m, z1), (x0, y1_m, z0), top_attrs)

    for i in range(steps):
        x0, x1 = xs_m[i], xs_m[i + 1]
        zb0, zb1 = zs_bot[i], zs_bot[i + 1]
        zt0, zt1 = zs_top[i], zs_top[i + 1]
        add_quad(mesh, (x0, y0_m, zb0), (x1, y0_m, zb1), (x1, y0_m, zt1), (x0, y0_m, zt0), top_attrs)

    for i in range(steps):
        x0, x1 = xs_m[i], xs_m[i + 1]
        zb0, zb1 = zs_bot[i], zs_bot[i + 1]
        zt0, zt1 = zs_top[i], zs_top[i + 1]
        add_quad(mesh, (x1, y1_m, zb1), (x0, y1_m, zb0), (x0, y1_m, zt0), (x1, y1_m, zt1), top_attrs)

    add_quad(mesh, (xs_m[0], y1_m, zs_bot[0]), (xs_m[0], y0_m, zs_bot[0]), (xs_m[0], y0_m, zs_top[0]), (xs_m[0], y1_m, zs_top[0]), top_attrs)
    add_quad(mesh, (xs_m[-1], y0_m, zs_bot[-1]), (xs_m[-1], y1_m, zs_bot[-1]), (xs_m[-1], y1_m, zs_top[-1]), (xs_m[-1], y0_m, zs_top[-1]), top_attrs)


# =============================================================================
# MASTER PUBLIC EXPORT
# =============================================================================

def populate_south_wing_interiors(mesh) -> None:
    """
    Populate Layer 4 (`4_Level_3_Reading_Room`) with Alvar Aalto's South Wing
    interior architecture from Sheets 05-a5, 17-a17, 23-a23, 24-a24, and 28-a27.
    """
    z_lobby = m_ft(G.Z_LOBBY_FT)        # +1'-4"      = +0.4064 m
    z_s_ceil = m_ft(G.Z_SOUTH_CEIL_FT)  # +10'-5 1/2" = +3.1877 m

    _add_glazed_vestibule_screen(mesh, z_lobby=z_lobby, z_head=z_s_ceil - 0.04)
    _add_restrooms_and_screen(mesh, z_lobby=z_lobby, z_s_ceil=z_s_ceil)
    _add_vault_and_storage(mesh, z_lobby=z_lobby, z_s_ceil=z_s_ceil)
    _add_auditorium(mesh, z_lobby=z_lobby, z_s_ceil=z_s_ceil)
