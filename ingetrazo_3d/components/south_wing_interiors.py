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

def _add_glazed_vestibule_screen(mesh, z_lobby: float, z_head: float = 3.24) -> None:
    """
    Inner glazed airlock screen along Y = -50.8 ft (X = -18.0..0.0 ft, z_lobby..+3.24 m).
    Framed with dark-bronze tubular mullions housing 3 pairs of glazed entry doors.
    """
    bronze = MATERIALS["mullion_bronze"]
    glass = MATERIALS["glass_clear"]
    push_mat = _furn("railing_bronze")
    z_door_top = z_lobby + 2.14  # ~7'-0" door opening head (~2.75 m)
    y_center = -50.8

    # 1. Continuous top head channel (Z = 3.20..3.24 m)
    add_oriented_box_ft(
        mesh,
        center_ft=(-9.0, y_center),
        length_ft=18.0,
        width_ft=0.35,
        angle_deg=0.0,
        z0_m=3.20,
        z1_m=z_head,
        attrs=bronze,
    )

    # 2. Continuous horizontal transom bar at door head (Z = z_door_top..z_door_top + 0.06 m)
    add_oriented_box_ft(
        mesh,
        center_ft=(-9.0, y_center),
        length_ft=18.0,
        width_ft=0.35,
        angle_deg=0.0,
        z0_m=z_door_top,
        z1_m=z_door_top + 0.06,
        attrs=bronze,
    )

    # 3. Recessed floor threshold channel (Z = z_lobby..z_lobby + 0.035 m)
    add_oriented_box_ft(
        mesh,
        center_ft=(-9.0, y_center),
        length_ft=18.0,
        width_ft=0.35,
        angle_deg=0.0,
        z0_m=z_lobby,
        z1_m=z_lobby + 0.035,
        attrs=bronze,
    )

    # 4. Main vertical bronze mullions dividing the 3 double-door bays
    for vx in (-18.0, -12.0, -6.0, 0.0):
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

    # 5. Transom clerestory glass panes above each bay (Z = z_door_top + 0.06..3.20 m)
    for bx in (-15.0, -9.0, -3.0):
        add_oriented_box_ft(
            mesh,
            center_ft=(bx, y_center),
            length_ft=5.60,
            width_ft=0.06,
            angle_deg=0.0,
            z0_m=z_door_top + 0.06,
            z1_m=3.20,
            attrs=glass,
        )

    # 6. Three pairs of glazed entry doors with dark-bronze perimeter stiles & push bars
    for bx in (-15.0, -9.0, -3.0):
        # Intermediate center meeting mullion
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
        for offset_x in (-1.44, 1.44):
            leaf_cx = bx + offset_x
            leaf_len = 2.68
            # Bottom kick rail
            add_oriented_box_ft(
                mesh,
                center_ft=(leaf_cx, y_center),
                length_ft=leaf_len,
                width_ft=0.22,
                angle_deg=0.0,
                z0_m=z_lobby + 0.035,
                z1_m=z_lobby + 0.22,
                attrs=bronze,
            )
            # Top door rail
            add_oriented_box_ft(
                mesh,
                center_ft=(leaf_cx, y_center),
                length_ft=leaf_len,
                width_ft=0.22,
                angle_deg=0.0,
                z0_m=z_door_top - 0.10,
                z1_m=z_door_top,
                attrs=bronze,
            )
            # Vertical outer stiles
            add_oriented_box_ft(
                mesh,
                center_ft=(leaf_cx - leaf_len * 0.44, y_center),
                length_ft=0.20,
                width_ft=0.22,
                angle_deg=0.0,
                z0_m=z_lobby + 0.22,
                z1_m=z_door_top - 0.10,
                attrs=bronze,
            )
            add_oriented_box_ft(
                mesh,
                center_ft=(leaf_cx + leaf_len * 0.44, y_center),
                length_ft=0.20,
                width_ft=0.22,
                angle_deg=0.0,
                z0_m=z_lobby + 0.22,
                z1_m=z_door_top - 0.10,
                attrs=bronze,
            )
            # Clear glass door pane
            add_oriented_box_ft(
                mesh,
                center_ft=(leaf_cx, y_center),
                length_ft=leaf_len - 0.44,
                width_ft=0.04,
                angle_deg=0.0,
                z0_m=z_lobby + 0.22,
                z1_m=z_door_top - 0.10,
                attrs=glass,
            )
            # Horizontal bronze push bar across leaf
            add_oriented_box_ft(
                mesh,
                center_ft=(leaf_cx, y_center),
                length_ft=leaf_len - 0.10,
                width_ft=0.10,
                angle_deg=0.0,
                z0_m=z_lobby + 0.90,
                z1_m=z_lobby + 0.96,
                attrs=push_mat,
            )


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
    z_lintel_bot = 2.74
    w_th = 0.45

    # 1. North corridor wall: (-53.0, -28.0) -> (-33.5, -28.0)
    add_wall_strip_ft(mesh, [(-53.0, -28.0), (-33.5, -28.0)], w_th, z_bot, z_top, plaster)

    # 2. Central dividing wall between Men 314 and Women 315: (-53.0, -39.0) -> (-33.5, -39.0)
    add_wall_strip_ft(mesh, [(-53.0, -39.0), (-33.5, -39.0)], w_th, z_bot, z_top, plaster)

    # 3. West boundary wall: (-53.0, -50.0) -> (-53.0, -28.0)
    add_wall_strip_ft(mesh, [(-53.0, -50.0), (-53.0, -28.0)], w_th, z_bot, z_top, plaster)

    # 4. South wall: (-53.0, -50.0) -> (-33.5, -50.0)
    add_wall_strip_ft(mesh, [(-53.0, -50.0), (-33.5, -50.0)], w_th, z_bot, z_top, plaster)

    # 5. East wall facing the screen alcove (solid segments):
    # Segment 1 (South): (-33.5, -50.0) -> (-33.5, -45.5)
    add_wall_strip_ft(mesh, [(-33.5, -50.0), (-33.5, -45.5)], w_th, z_bot, z_top, plaster)
    # Segment 2 (Center): (-33.5, -42.5) -> (-33.5, -35.5)
    add_wall_strip_ft(mesh, [(-33.5, -42.5), (-33.5, -35.5)], w_th, z_bot, z_top, plaster)
    # Segment 3 (North): (-33.5, -32.5) -> (-33.5, -28.0)
    add_wall_strip_ft(mesh, [(-33.5, -32.5), (-33.5, -28.0)], w_th, z_bot, z_top, plaster)

    # 6. Lintel headers above the two restroom doorways (Z = 2.74..z_top m)
    # Men 314 doorway opening: Y = -45.5..-42.5
    add_wall_strip_ft(mesh, [(-33.5, -45.5), (-33.5, -42.5)], w_th, z_lintel_bot, z_top, plaster)
    # Women 315 doorway opening: Y = -35.5..-32.5
    add_wall_strip_ft(mesh, [(-33.5, -35.5), (-33.5, -32.5)], w_th, z_lintel_bot, z_top, plaster)

    # 7. Recessed birch restroom doors (furniture: True)
    add_oriented_box_ft(
        mesh,
        center_ft=(-33.5, -44.0),
        length_ft=2.90,
        width_ft=0.16,
        angle_deg=90.0,
        z0_m=z_lobby + 0.01,
        z1_m=z_lintel_bot,
        attrs=birch_furn,
    )
    add_oriented_box_ft(
        mesh,
        center_ft=(-33.5, -34.0),
        length_ft=2.90,
        width_ft=0.16,
        angle_deg=90.0,
        z0_m=z_lobby + 0.01,
        z1_m=z_lintel_bot,
        attrs=birch_furn,
    )

    # 8. Signature Freestanding Wood Batten Privacy Screen (SCREEN on Sheet 05-a5 & 28-a27)
    # Recessed matte-bronze floor & ceiling mounting channels along X = -29.08 ft (Y = -44.8..-31.8 ft)
    add_oriented_box_ft(
        mesh,
        center_ft=(-29.08, -38.3),
        length_ft=13.0,
        width_ft=0.34,
        angle_deg=90.0,
        z0_m=z_lobby,
        z1_m=z_lobby + 0.06,
        attrs=bronze,
    )
    add_oriented_box_ft(
        mesh,
        center_ft=(-29.08, -38.3),
        length_ft=13.0,
        width_ft=0.34,
        angle_deg=90.0,
        z0_m=z_s_ceil - 0.08,
        z1_m=z_s_ceil - 0.02,
        attrs=bronze,
    )

    # Exactly 32 vertical birch / hemlock battens (0.16 ft x 0.22 ft section @ 0.40 ft o.c.)
    y_start = -44.6
    y_end = -32.0
    n_battens = 32
    step_y = (y_end - y_start) / (n_battens - 1)
    for i in range(n_battens):
        yk = y_start + i * step_y
        add_oriented_box_ft(
            mesh,
            center_ft=(-29.08, yk),
            length_ft=0.22,
            width_ft=0.16,
            angle_deg=90.0,
            z0_m=z_lobby + 0.06,
            z1_m=z_s_ceil - 0.08,
            attrs=birch_furn,
        )


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
    z_head = 2.74

    # 1. Corridor / Vault North wall along Y = -8.8 ft: (18.5, -8.8) -> (51.0, -8.8)
    add_wall_strip_ft(mesh, [(18.5, -8.8), (51.0, -8.8)], 0.55, z_bot, z_top, plaster)

    # 2. Auditorium / Vault dividing wall along Y = -21.0 ft: (18.2, -21.0) -> (59.8, -21.0)
    # Double-door opening into Auditorium at X = 41.5..46.5 ft
    add_wall_strip_ft(mesh, [(18.2, -21.0), (41.5, -21.0)], 0.65, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(46.5, -21.0), (59.8, -21.0)], 0.65, z_bot, z_top, plaster)
    # Lintel header over Auditorium double-door
    add_wall_strip_ft(mesh, [(41.5, -21.0), (46.5, -21.0)], 0.65, z_head, z_top, plaster)
    # Double birch doors into Auditorium
    add_oriented_box_ft(
        mesh,
        center_ft=(44.0, -21.0),
        length_ft=4.90,
        width_ft=0.18,
        angle_deg=0.0,
        z0_m=z_lobby + 0.01,
        z1_m=z_head,
        attrs=birch_furn,
    )

    # 3. Janitor / Mechanical cross-wall at X = 25.5 ft: (25.5, -21.0) -> (25.5, -8.8)
    add_wall_strip_ft(mesh, [(25.5, -21.0), (25.5, -8.8)], 0.45, z_bot, z_top, plaster)

    # 4. Storage 341 / Vault 342 dividing wall at X = 36.5 ft with security vault door opening (Y = -16.5..-13.5 ft)
    add_wall_strip_ft(mesh, [(36.5, -21.0), (36.5, -16.5)], 0.55, z_bot, z_top, plaster)
    add_wall_strip_ft(mesh, [(36.5, -13.5), (36.5, -8.8)], 0.55, z_bot, z_top, plaster)
    # Lintel header over vault door opening
    add_wall_strip_ft(mesh, [(36.5, -16.5), (36.5, -13.5)], 0.55, 2.60, z_top, plaster)
    # Heavy bronze/steel vault door
    add_oriented_box_ft(
        mesh,
        center_ft=(36.5, -15.0),
        length_ft=2.90,
        width_ft=0.32,
        angle_deg=90.0,
        z0_m=z_lobby + 0.01,
        z1_m=2.60,
        attrs=steel,
    )
    # Brass combination wheel & spindle on Vault Door
    add_cylinder_ft(
        mesh,
        center_ft=(36.72, -15.0),
        radius_ft=0.52,
        z0_m=z_lobby + 1.25,
        z1_m=z_lobby + 1.30,
        attrs=brass,
        sides=16,
    )

    # 5. Aalto single-sided rare-book shelving inside Rare Book Vault 342
    # North wall unit: X = 37.5..49.8 ft, Y = -9.55 ft (facing South into Vault)
    add_aalto_bookcase_ft(
        mesh,
        center_ft=(43.65, -9.55),
        length_ft=12.2,
        depth_ft=1.15,
        angle_deg=180.0,
        z_floor_m=z_lobby,
        height_m=2.15,
        double_sided=False,
        n_shelf_tiers=5,
        canopy_style="birch",
        end_slats="none",
        populate_books=True,
        seed=3421,
    )
    # East wall unit: X = 50.15 ft, Y = -11.0..-19.5 ft (facing West into Vault)
    add_aalto_bookcase_ft(
        mesh,
        center_ft=(50.15, -15.25),
        length_ft=8.4,
        depth_ft=1.15,
        angle_deg=90.0,
        z_floor_m=z_lobby,
        height_m=2.15,
        double_sided=False,
        n_shelf_tiers=5,
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
      - Sweeping S-curved Audio Visual Control Booth 328 with raised concrete platform
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

    # 1. Splayed West Acoustic Lobby-Dividing Wall: (16.8, -50.2) -> (18.2, -21.0)
    # Double birch entry doors from Lobby 317 at Y = -43.0..-37.5 ft
    # Parametric interpolation along the splayed wall line:
    # X(y) = 16.8 + (y - (-50.2)) / 29.2 * 1.4
    x_d_south = 16.8 + (7.2 / 29.2) * 1.4    # ~17.145 ft
    x_d_north = 16.8 + (12.7 / 29.2) * 1.4   # ~17.409 ft
    w_splay = 0.70

    # South segment: (16.8, -50.2) -> (x_d_south, -43.0)
    add_wall_strip_ft(mesh, [(16.8, -50.2), (x_d_south, -43.0)], w_splay, z_lobby + 0.005, 4.95, plaster)
    # North segment: (x_d_north, -37.5) -> (18.2, -21.0)
    add_wall_strip_ft(mesh, [(x_d_north, -37.5), (18.2, -21.0)], w_splay, z_lobby + 0.005, 4.95, plaster)
    # Lintel header over entry opening (Z = 2.74..4.95 m)
    add_wall_strip_ft(mesh, [(x_d_south, -43.0), (x_d_north, -37.5)], w_splay, 2.74, 4.95, plaster)
    # Double birch entry doors
    splay_deg = math.degrees(math.atan2(-21.0 - (-50.2), 18.2 - 16.8))
    add_oriented_box_ft(
        mesh,
        center_ft=((x_d_south + x_d_north) * 0.5, -40.25),
        length_ft=5.40,
        width_ft=0.20,
        angle_deg=splay_deg,
        z0_m=z_lobby + 0.01,
        z1_m=2.74,
        attrs=birch_furn,
    )

    # 2. Sweeping Curved Audio Visual Control Booth 328 (Sheet 23-a23)
    # Booth floor platform (Z = z_lobby..z_lobby + 0.76 m)
    booth_curve_pts = [
        (18.4, -26.8),
        (21.0, -27.3),
        (24.5, -27.2),
        (27.0, -26.3),
        (28.5, -25.0),
        (30.2, -23.3),
        (31.5, -21.3),
    ]
    booth_floor_poly = [(18.2, -21.3), (18.2, -26.8)] + booth_curve_pts + [(31.5, -21.3)]
    add_extruded_polygon_ft(mesh, booth_floor_poly, z_lobby, z_lobby + 0.76, floor_booth)

    # Sweeping S-curved plaster wall with horizontal projection window slot:
    # A. Solid base wall: Z = z_lobby + 0.01..z_lobby + 1.10 m
    add_wall_strip_ft(mesh, booth_curve_pts, 0.50, z_lobby + 0.01, z_lobby + 1.10, plaster)
    # B. Mid level: window slot between (21.0, -27.3) and (28.5, -25.0)
    slot_curve = booth_curve_pts[1:5]
    add_wall_strip_ft(mesh, slot_curve, 0.08, z_lobby + 1.10, z_lobby + 1.60, glass)
    add_wall_strip_ft(mesh, slot_curve, 0.28, z_lobby + 1.08, z_lobby + 1.10, bronze)
    add_wall_strip_ft(mesh, slot_curve, 0.28, z_lobby + 1.60, z_lobby + 1.62, bronze)
    # Flanking solid sections at mid level
    add_wall_strip_ft(mesh, booth_curve_pts[0:2], 0.50, z_lobby + 1.10, z_lobby + 1.60, plaster)
    add_wall_strip_ft(mesh, booth_curve_pts[4:7], 0.50, z_lobby + 1.10, z_lobby + 1.60, plaster)
    # C. Solid upper wall above slot: Z = z_lobby + 1.60..4.35 m
    add_wall_strip_ft(mesh, booth_curve_pts, 0.50, z_lobby + 1.60, 4.35, plaster)

    # 3. Quarter-Circle SE Corner Stage / Dais (center = (60.2, -58.2), R = 15.8 ft, 90°..180°)
    stage_center = (60.2, -58.2)
    poly_stage = [stage_center] + [p for p in arc_pts(stage_center, 15.8, 90.0, 180.0, 20)]
    add_extruded_polygon_ft(mesh, poly_stage, z_lobby + 0.005, z_lobby + 0.52, birch_furn)

    # Two curved corner steps leading up to the stage
    poly_step1 = [p for p in arc_pts(stage_center, 17.6, 90.0, 180.0, 20)] + [
        p for p in arc_pts(stage_center, 16.7, 180.0, 90.0, 20)
    ]
    add_extruded_polygon_ft(mesh, poly_step1, z_lobby + 0.005, z_lobby + 0.17, birch_furn)

    poly_step2 = [p for p in arc_pts(stage_center, 16.7, 90.0, 180.0, 20)] + [
        p for p in arc_pts(stage_center, 15.8, 180.0, 90.0, 20)
    ]
    add_extruded_polygon_ft(mesh, poly_step2, z_lobby + 0.005, z_lobby + 0.35, birch_furn)

    # Curved / Faceted Acoustic Vertical Hemlock Batten Backdrop Screen behind stage
    # East wall screen: X = 59.8 ft, Y = -58.2..-41.5 ft (36 battens)
    for i in range(36):
        yk = -58.0 + i * (16.2 / 35.0)
        add_oriented_box_ft(
            mesh,
            center_ft=(59.8, yk),
            length_ft=0.20,
            width_ft=0.12,
            angle_deg=90.0,
            z0_m=z_lobby + 0.52,
            z1_m=4.35,
            attrs=hemlock_furn,
        )
    # South wall screen: Y = -57.8 ft, X = 43.5..59.8 ft (36 battens)
    for i in range(36):
        xk = 43.8 + i * (15.8 / 35.0)
        add_oriented_box_ft(
            mesh,
            center_ft=(xk, -57.8),
            length_ft=0.20,
            width_ft=0.12,
            angle_deg=0.0,
            z0_m=z_lobby + 0.52,
            z1_m=4.35,
            attrs=hemlock_furn,
        )

    # Aalto Birch Lectern on the Stage (located at radius ~10.9 ft at 135°)
    add_oriented_box_ft(
        mesh,
        center_ft=(52.5, -50.5),
        length_ft=1.80,
        width_ft=1.40,
        angle_deg=135.0,
        z0_m=z_lobby + 0.52,
        z1_m=z_lobby + 1.45,
        attrs=birch_furn,
    )
    add_oriented_box_ft(
        mesh,
        center_ft=(52.3, -50.3),
        length_ft=2.00,
        width_ft=1.50,
        angle_deg=135.0,
        z0_m=z_lobby + 1.45,
        z1_m=z_lobby + 1.62,
        attrs=birch_furn,
    )

    # 4. Concentric / Angled Auditorium Seating Rows (6 rows, ~8 seats per row with center aisle)
    row_radii = (22.0, 25.5, 29.0, 32.5, 36.0, 39.5)
    chair_angles = (106.5, 113.5, 120.5, 127.5, 142.5, 149.5, 156.5, 163.5)

    for r_seat in row_radii:
        for ang_deg in chair_angles:
            ang_rad = math.radians(ang_deg)
            cx = stage_center[0] + r_seat * math.cos(ang_rad)
            cy = stage_center[1] + r_seat * math.sin(ang_rad)
            # Chair faces towards stage center: rot_deg = ang_deg + 180°
            rot_deg = (ang_deg + 180.0) % 360.0
            rot_rad = math.radians(rot_deg)
            ux, uy = math.cos(rot_rad), math.sin(rot_rad)

            # Seat cushion (slate blue upholstered box)
            add_oriented_box_ft(
                mesh,
                center_ft=(cx, cy),
                length_ft=1.65,
                width_ft=1.55,
                angle_deg=rot_deg + 90.0,
                z0_m=z_lobby + 0.38,
                z1_m=z_lobby + 0.46,
                attrs=slate_furn,
            )
            # Curved backrest
            back_cx = cx - 0.65 * ux
            back_cy = cy - 0.65 * uy
            add_oriented_box_ft(
                mesh,
                center_ft=(back_cx, back_cy),
                length_ft=1.65,
                width_ft=0.20,
                angle_deg=rot_deg + 90.0,
                z0_m=z_lobby + 0.46,
                z1_m=z_lobby + 0.82,
                attrs=slate_furn,
            )
            # Birch side leg frames & armrests
            nx, ny = -uy, ux
            for arm_sign in (-1.0, 1.0):
                arm_cx = cx + arm_sign * 0.78 * nx
                arm_cy = cy + arm_sign * 0.78 * ny
                # Vertical leg post
                add_oriented_box_ft(
                    mesh,
                    center_ft=(arm_cx, arm_cy),
                    length_ft=1.50,
                    width_ft=0.10,
                    angle_deg=rot_deg,
                    z0_m=z_lobby,
                    z1_m=z_lobby + 0.60,
                    attrs=birch_furn,
                )
                # Curved armrest cap
                add_oriented_box_ft(
                    mesh,
                    center_ft=(arm_cx, arm_cy),
                    length_ft=1.35,
                    width_ft=0.16,
                    angle_deg=rot_deg,
                    z0_m=z_lobby + 0.58,
                    z1_m=z_lobby + 0.63,
                    attrs=birch_furn,
                )

    # 5. Iconic 3-Wave Undulating Suspended Acoustic Plaster Ceiling (Sheet 17-a17 Section 4)
    _add_auditorium_acoustic_ceiling(mesh)


# =============================================================================
# E. ICONIC UNDULATING ACOUSTIC PLASTER CEILING (Sheet 17-a17 Section 4)
# =============================================================================

def _add_auditorium_acoustic_ceiling(mesh) -> None:
    """
    Spanning X = 19.0..59.8 ft, Y = -57.8..-22.0 ft, stopping cleanly inside
    the Auditorium walls at Z ≈ +3.95..+4.55 m (well below the +5.05 m roof slab).
    Constructed as a 100% closed, watertight 2-manifold acoustic shell (0.18 m thick,
    white_soffit bottom, white_plaster top and perimeter rims) across 24 steps along
    the East-West axis with 3 graceful Aalto acoustic waves:
        z(u) = 4.22 + 0.26 * sin(3 * pi * u) - 0.12 * u
    """
    soffit_attrs = MATERIALS["white_soffit"]
    top_attrs = MATERIALS["white_plaster"]

    x_min, x_max = 19.0, 59.8
    y_min, y_max = -57.8, -22.0
    steps = 24
    t_thick = 0.18

    # Calculate coordinates along E-W axis
    xs = [x_min + (x_max - x_min) * (i / steps) for i in range(steps + 1)]
    us = [i / steps for i in range(steps + 1)]
    zs_bot = [4.22 + 0.26 * math.sin(3.0 * math.pi * u) - 0.12 * u for u in us]
    zs_top = [zb + t_thick for zb in zs_bot]

    xs_m = [m_ft(x) for x in xs]
    y0_m = m_ft(y_min)
    y1_m = m_ft(y_max)

    # 1. Bottom undulating soffit quads (-Z outward normal)
    for i in range(steps):
        x0, x1 = xs_m[i], xs_m[i + 1]
        z0, z1 = zs_bot[i], zs_bot[i + 1]
        add_quad(mesh, (x0, y0_m, z0), (x0, y1_m, z0), (x1, y1_m, z1), (x1, y0_m, z1), soffit_attrs)

    # 2. Top undulating ceiling quads (+Z outward normal)
    for i in range(steps):
        x0, x1 = xs_m[i], xs_m[i + 1]
        z0, z1 = zs_top[i], zs_top[i + 1]
        add_quad(mesh, (x0, y0_m, z0), (x1, y0_m, z1), (x1, y1_m, z1), (x0, y1_m, z0), top_attrs)

    # 3. South rim quads along y = y0 (-Y outward normal)
    for i in range(steps):
        x0, x1 = xs_m[i], xs_m[i + 1]
        zb0, zb1 = zs_bot[i], zs_bot[i + 1]
        zt0, zt1 = zs_top[i], zs_top[i + 1]
        add_quad(mesh, (x0, y0_m, zb0), (x1, y0_m, zb1), (x1, y0_m, zt1), (x0, y0_m, zt0), top_attrs)

    # 4. North rim quads along y = y1 (+Y outward normal)
    for i in range(steps):
        x0, x1 = xs_m[i], xs_m[i + 1]
        zb0, zb1 = zs_bot[i], zs_bot[i + 1]
        zt0, zt1 = zs_top[i], zs_top[i + 1]
        add_quad(mesh, (x1, y1_m, zb1), (x0, y1_m, zb0), (x0, y1_m, zt0), (x1, y1_m, zt1), top_attrs)

    # 5. West end cap quad at x = x0 (-X outward normal)
    add_quad(
        mesh,
        (xs_m[0], y1_m, zs_bot[0]),
        (xs_m[0], y0_m, zs_bot[0]),
        (xs_m[0], y0_m, zs_top[0]),
        (xs_m[0], y1_m, zs_top[0]),
        top_attrs,
    )

    # 6. East end cap quad at x = xN (+X outward normal)
    add_quad(
        mesh,
        (xs_m[-1], y0_m, zs_bot[-1]),
        (xs_m[-1], y1_m, zs_bot[-1]),
        (xs_m[-1], y1_m, zs_top[-1]),
        (xs_m[-1], y0_m, zs_top[-1]),
        top_attrs,
    )


# =============================================================================
# MASTER PUBLIC EXPORT
# =============================================================================

def populate_south_wing_interiors(mesh) -> None:
    """
    Populate Layer 4 (`4_Level_3_Reading_Room`) with Alvar Aalto's South Wing
    interior architecture from Sheets 05-a5, 17-a17, 23-a23, 24-a24, and 28-a27:
      - Glazed Inner Lobby Airlock Screen along Y = -50.8 ft
      - Restrooms Men 314 & Women 315 + 32-Batten Vertical Privacy Screen
      - Chair Storage 341 & Rare Book Vault 342 with Vault Door & Rare Book Stacks
      - Rare Book & Meeting Room (Auditorium 327) with Control Booth 328,
        Quarter-Circle Stage, Acoustic Batten Screen, Lectern, 6 Seating Rows,
        and Iconic 3-Wave Undulating Acoustic Plaster Ceiling.
    """
    z_lobby = m_ft(G.Z_LOBBY_FT)        # +2.0 ft  = +0.6096 m
    z_s_ceil = m_ft(G.Z_SOUTH_CEIL_FT)  # +10'-10" = +3.3020 m

    _add_glazed_vestibule_screen(mesh, z_lobby=z_lobby)
    _add_restrooms_and_screen(mesh, z_lobby=z_lobby, z_s_ceil=z_s_ceil)
    _add_vault_and_storage(mesh, z_lobby=z_lobby, z_s_ceil=z_s_ceil)
    _add_auditorium(mesh, z_lobby=z_lobby, z_s_ceil=z_s_ceil)
