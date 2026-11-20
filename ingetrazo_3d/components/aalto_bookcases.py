"""
Alvar Aalto Parametric Millwork & Bookcase Module (Mount Angel Abbey Library).
=============================================================================
Constructive, 100% 2-manifold (`unpaired == 0`), parametric millwork builder
for Aalto's iconic birch bookcases, radial stacks, curved reference bookwalls,
and stairwell counter bookcases.

Archival Sources & Details:
  - Sheet 13-a13 (Reading Level Elevations & Details 9–14):
      * Detail 9: SECTION — Base plinth, intermediate shelves, top canopy, central spine.
      * Detail 10: BASE DETAIL — Recessed kick plinth inset 1.5" from face and 0.8" from ends.
      * Detail 11: SHELF DETAIL — Solid birch shelves (~0.85" thick) with rounded front lip.
      * Detail 12: DIVIDER DETAIL — Vertical birch panels (~1" thick) separating 3'-0" bays.
      * Detail 13: CORNER DETAIL & Detail 14: EDGE DETAIL.
  - Sheet 29-f1 / 30-f2 / 31-f3 (Stack & Furniture Layouts):
      * Standard ~3'-0" to 3'-3" bay modules dynamically subdivided across arbitrary lengths.
  - Archival Photographs:
      * `media_1794672224799_48025ce8.jpg` & `mezzaninewithdictionaryweb2`:
        Iconic vertical slatted birch screen (4–5 battens) rising ~3" above the canopy
        at the aisle end of Level 3 radial stacks, acting as call-number directory stanchions.
      * `IMG_5143`: Levels 1 & 2 stack canopies in slate-grey laminate (`stack_canopy_grey`)
        with birch edge lip.
"""

from __future__ import annotations

import math

from .primitives import (
    MATERIALS,
    add_extruded_polygon_ft,
)

# -----------------------------------------------------------------------------
# Architectural Constants & Tolerances
# -----------------------------------------------------------------------------
BAY_MODULE_FT = 3.10       # Canonical Aalto stack bay width (~3'-0" to 3'-3")
DIVIDER_THICK_FT = 0.085   # ~1.0" solid birch cheek / intermediate bay divider
SPINE_THICK_FT = 0.065     # ~0.78" central longitudinal spine / back panel
PLINTH_HEIGHT_M = 0.100    # ~3.9" (10 cm) recessed base plinth
SHELF_THICK_M = 0.022      # ~0.85" solid birch shelf
CANOPY_THICK_M = 0.032     # ~1.25" top canopy board
COUNTER_CANOPY_M = 0.040   # ~1.6" heavy solid birch counter-top slab

# Millwork Tolerances to prevent coplanar Z-fighting across 3D renderers
TOL_FT = 0.008             # ~2.4 mm clearance along horizontal axes
TOL_M = 0.0025             # 2.5 mm clearance along vertical Z axis

BOOK_PALETTE = (
    "book_terracotta",
    "book_slate",
    "book_ochre",
    "book_sage",
)


def _furn_mat(key: str, **overrides) -> dict:
    """Return material dictionary guaranteed to have 'furniture': True."""
    base = MATERIALS.get(key, {"color": (0.82, 0.63, 0.40), "roughness": 0.54, "metallic": 0.05})
    return {**base, "furniture": True, **overrides}


def _pseudo_rand(seed: int, *args: int) -> float:
    """
    Deterministic, fast integer hash returning a float in [0.0, 1.0).
    Guarantees reproducible book clustering across platforms without touching global state.
    """
    h = (seed & 0xFFFFFFFF) ^ 0x9E3779B9
    for a in args:
        h = ((h * 1664525) + (a & 0xFFFFFFFF) + 1013904223) & 0xFFFFFFFF
    return ((h >> 8) & 0x00FFFFFF) / 16777216.0


def _add_box_local_ft(
    mesh,
    cx: float,
    cy: float,
    ux: float,
    uy: float,
    nx: float,
    ny: float,
    s0: float,
    s1: float,
    t0: float,
    t1: float,
    z0_m: float,
    z1_m: float,
    top_attrs: dict,
    side_attrs: dict | None = None,
    bottom_attrs: dict | None = None,
):
    """
    Emit a 100% closed 2-manifold 6-face solid box oriented in the local (u, n) frame.
    s spans along longitudinal unit vector u; t spans along transverse unit vector n.
    Normals are strictly CCW outward-facing.
    """
    if s0 > s1:
        s0, s1 = s1, s0
    if t0 > t1:
        t0, t1 = t1, t0
    if z0_m > z1_m:
        z0_m, z1_m = z1_m, z0_m

    # Vertices ordered strictly counter-clockwise (+Z normal)
    p0 = (cx + s0 * ux + t0 * nx, cy + s0 * uy + t0 * ny)
    p1 = (cx + s1 * ux + t0 * nx, cy + s1 * uy + t0 * ny)
    p2 = (cx + s1 * ux + t1 * nx, cy + s1 * uy + t1 * ny)
    p3 = (cx + s0 * ux + t1 * nx, cy + s0 * uy + t1 * ny)

    add_extruded_polygon_ft(mesh, [p0, p1, p2, p3], z0_m, z1_m, top_attrs, side_attrs, bottom_attrs)


def add_aalto_bookcase_ft(
    mesh,
    center_ft: tuple[float, float],
    length_ft: float,
    depth_ft: float,
    angle_deg: float,
    z_floor_m: float,
    height_m: float = 2.06,
    *,
    double_sided: bool = True,
    n_shelf_tiers: int = 5,
    canopy_style: str = "birch",
    end_slats: str = "inner",
    populate_books: bool = True,
    seed: int = 0,
):
    """
    Construct a parametric, 100% 2-manifold Alvar Aalto bookcase / radial bookstack range.

    Parameters:
      mesh: IngeTrazo Mesh container
      center_ft: (cx, cy) center of bookcase footprint in feet
      length_ft: Total length along longitudinal axis in feet (e.g. 3.0 ft to 30.0+ ft)
      depth_ft: Total depth across shelf faces in feet (e.g. 2.7 ft double-faced, 1.15 ft single-faced)
      angle_deg: Rotation angle in degrees along the length (0 = East, 90 = North)
      z_floor_m: Floor elevation in metres
      height_m: Total top-of-canopy height in metres (default 2.06 m ~ 6'-9")
      double_sided: True for freestanding double-faced stacks; False for wall/counter units
      n_shelf_tiers: Number of horizontal shelf tiers (default 5 for 2.06m; 3 for counter-height)
      canopy_style: 'birch' (Level 3 / Mezzanine), 'slate_grey' (Levels 1 & 2), or 'counter' (L3 stairwell)
      end_slats: Signature vertical birch batten screen stanchions: 'inner'/'start', 'outer'/'end', 'both', 'none'
      populate_books: Whether to generate curated, varied-height book clusters
      seed: Deterministic integer seed for book clustering
    """
    cx, cy = float(center_ft[0]), float(center_ft[1])
    L = max(1.5, float(length_ft))
    D = max(0.8, float(depth_ft))
    H = max(0.6, float(height_m))
    z_fl = float(z_floor_m)
    z_top = z_fl + H

    rad = math.radians(angle_deg)
    ux, uy = math.cos(rad), math.sin(rad)
    nx, ny = -uy, ux  # +n is +90 deg CCW from u

    birch_mat = _furn_mat("birch_wood")
    lino_mat = _furn_mat("black_linoleum")
    canopy_grey_mat = _furn_mat("stack_canopy_grey")

    t_canopy = COUNTER_CANOPY_M if canopy_style == "counter" else CANOPY_THICK_M
    h_plinth = PLINTH_HEIGHT_M

    # -------------------------------------------------------------------------
    # 1. Bay Subdivisions & Divider Geometry (Detail 12)
    # -------------------------------------------------------------------------
    n_bays = max(1, round(L / BAY_MODULE_FT))
    t_end = min(DIVIDER_THICK_FT, L * 0.15)
    t_div = min(DIVIDER_THICK_FT, L * 0.12)
    t_sp = min(SPINE_THICK_FT, D * 0.20)

    # Compute bay boundary coordinates along s [-L/2 .. +L/2]
    bay_bounds: list[tuple[float, float]] = []
    if n_bays == 1:
        bay_bounds.append((-L * 0.5 + t_end, L * 0.5 - t_end))
    else:
        bay_step = L / n_bays
        for b in range(n_bays):
            s_a = -L * 0.5 + t_end if b == 0 else (-L * 0.5 + b * bay_step + t_div * 0.5)
            s_b = L * 0.5 - t_end if b == n_bays - 1 else (-L * 0.5 + (b + 1) * bay_step - t_div * 0.5)
            bay_bounds.append((s_a, s_b))

    # -------------------------------------------------------------------------
    # 2. Recessed Base Plinth (Detail 10)
    # -------------------------------------------------------------------------
    # Inset 1.5" (0.125 ft) from shelf front/back and 0.8" (0.067 ft) from ends
    plinth_s0 = -L * 0.5 + min(0.067, t_end * 0.8)
    plinth_s1 = L * 0.5 - min(0.067, t_end * 0.8)
    if double_sided:
        plinth_t0 = -D * 0.5 + 0.125
        plinth_t1 = D * 0.5 - 0.125
    else:
        plinth_t0 = -D * 0.5 + 0.020  # slight setback from rear wall
        plinth_t1 = D * 0.5 - 0.125   # front kick recess
    _add_box_local_ft(
        mesh, cx, cy, ux, uy, nx, ny,
        plinth_s0, plinth_s1, plinth_t0, plinth_t1,
        z_fl + 0.001, z_fl + h_plinth,
        lino_mat,
    )

    # -------------------------------------------------------------------------
    # 3. Solid Birch End Cheeks & Intermediate Bay Dividers (Details 12–14)
    # -------------------------------------------------------------------------
    z_div_bot = z_fl + h_plinth + TOL_M
    z_div_top = z_top - t_canopy - TOL_M

    # Outer End Cheeks rise from floor up to canopy underside
    _add_box_local_ft(
        mesh, cx, cy, ux, uy, nx, ny,
        -L * 0.5, -L * 0.5 + t_end,
        -D * 0.5, D * 0.5,
        z_fl + 0.002, z_div_top,
        birch_mat,
    )
    _add_box_local_ft(
        mesh, cx, cy, ux, uy, nx, ny,
        L * 0.5 - t_end, L * 0.5,
        -D * 0.5, D * 0.5,
        z_fl + 0.002, z_div_top,
        birch_mat,
    )

    # Intermediate Bay Dividers
    if n_bays > 1:
        bay_step = L / n_bays
        for b in range(1, n_bays):
            div_s_mid = -L * 0.5 + b * bay_step
            _add_box_local_ft(
                mesh, cx, cy, ux, uy, nx, ny,
                div_s_mid - t_div * 0.5, div_s_mid + t_div * 0.5,
                -D * 0.5 + TOL_FT, D * 0.5 - TOL_FT,
                z_div_bot, z_div_top,
                birch_mat,
            )

    # -------------------------------------------------------------------------
    # 4. Longitudinal Center Spine / Back Panel (Detail 9)
    # -------------------------------------------------------------------------
    for s_a, s_b in bay_bounds:
        sp_s0 = s_a + TOL_FT
        sp_s1 = s_b - TOL_FT
        if sp_s1 <= sp_s0:
            continue
        if double_sided:
            sp_t0 = -t_sp * 0.5
            sp_t1 = t_sp * 0.5
        else:
            sp_t0 = -D * 0.5 + TOL_FT
            sp_t1 = -D * 0.5 + t_sp
        _add_box_local_ft(
            mesh, cx, cy, ux, uy, nx, ny,
            sp_s0, sp_s1, sp_t0, sp_t1,
            z_div_bot, z_div_top,
            birch_mat,
        )

    # -------------------------------------------------------------------------
    # 5. Top Canopy Board (Detail 9)
    # -------------------------------------------------------------------------
    z_can_bot = z_top - t_canopy
    z_can_top = z_top

    if canopy_style == "counter":
        # Overhanging birch counter slab for Level 3 stairwell bookcases
        c_s0 = -L * 0.5 - 0.12
        c_s1 = L * 0.5 + 0.12
        c_t0 = -D * 0.5 if not double_sided else (-D * 0.5 - 0.15)
        c_t1 = D * 0.5 + 0.15
        _add_box_local_ft(
            mesh, cx, cy, ux, uy, nx, ny,
            c_s0, c_s1, c_t0, c_t1,
            z_can_bot, z_can_top,
            birch_mat,
        )
    elif canopy_style == "slate_grey":
        # Levels 1 & 2: Slate-grey laminate top with birch perimeter edge lip
        _add_box_local_ft(
            mesh, cx, cy, ux, uy, nx, ny,
            -L * 0.5, L * 0.5, -D * 0.5, D * 0.5,
            z_can_bot, z_can_top,
            top_attrs=canopy_grey_mat,
            side_attrs=birch_mat,
            bottom_attrs=birch_mat,
        )
    else:
        # Standard Level 3 / Mezzanine solid birch canopy
        _add_box_local_ft(
            mesh, cx, cy, ux, uy, nx, ny,
            -L * 0.5, L * 0.5, -D * 0.5, D * 0.5,
            z_can_bot, z_can_top,
            birch_mat,
        )

    # -------------------------------------------------------------------------
    # 6. Horizontal Birch Shelves (Detail 11)
    # -------------------------------------------------------------------------
    # Distribute n_tiers evenly so every tier (including the top tier beneath the canopy)
    # forms a full open book compartment (`n_shelf_tiers=3` -> 3 open rows of books).
    n_tiers = max(1, int(n_shelf_tiers))
    z_sh_bot = z_fl + h_plinth + TOL_M
    z_sh_max = z_top - t_canopy - TOL_M
    z_span = z_sh_max - z_sh_bot
    dz_tier = z_span / n_tiers

    shelf_z_levels: list[float] = [z_sh_bot + k * dz_tier for k in range(n_tiers)]

    for z_k0 in shelf_z_levels:
        z_k1 = z_k0 + SHELF_THICK_M
        for s_a, s_b in bay_bounds:
            sh_s0 = s_a + TOL_FT
            sh_s1 = s_b - TOL_FT
            if sh_s1 <= sh_s0:
                continue
            if double_sided:
                # Side - (South/Aisle side)
                _add_box_local_ft(
                    mesh, cx, cy, ux, uy, nx, ny,
                    sh_s0, sh_s1,
                    -D * 0.5 + 0.015, -t_sp * 0.5 - TOL_FT,
                    z_k0, z_k1,
                    birch_mat,
                )
                # Side + (North/Aisle side)
                _add_box_local_ft(
                    mesh, cx, cy, ux, uy, nx, ny,
                    sh_s0, sh_s1,
                    t_sp * 0.5 + TOL_FT, D * 0.5 - 0.015,
                    z_k0, z_k1,
                    birch_mat,
                )
            else:
                _add_box_local_ft(
                    mesh, cx, cy, ux, uy, nx, ny,
                    sh_s0, sh_s1,
                    -D * 0.5 + t_sp + TOL_FT, D * 0.5 - 0.015,
                    z_k0, z_k1,
                    birch_mat,
                )

    # -------------------------------------------------------------------------
    # 7. Signature Aalto Vertical Birch End-Batten Screen
    # -------------------------------------------------------------------------
    # Iconic 4–5 battens spaced across the inner aisle end face (media_1794672224799_48025ce8)
    slats_mode = str(end_slats).lower().strip()
    add_start_slats = slats_mode in ("inner", "start", "both")
    add_end_slats = slats_mode in ("outer", "end", "both")

    if add_start_slats or add_end_slats:
        w_slat = 0.125   # ~1.5" wide batten
        th_slat = 0.100  # ~1.2" thick batten projecting outward
        n_slats = 5 if D >= 2.0 else 3
        z_slat_bot = z_fl + 0.005
        z_slat_top = z_top + 0.075  # rises ~3" above top canopy / directory stanchion

        t_margin = 0.16
        t_span = D - 2.0 * t_margin
        step_t = t_span / (n_slats - 1) if n_slats > 1 else 0.0

        for j in range(n_slats):
            tj_mid = -D * 0.5 + t_margin + j * step_t
            slat_t0 = tj_mid - w_slat * 0.5
            slat_t1 = tj_mid + w_slat * 0.5

            if add_start_slats:
                # Placed at s = -L/2, projecting outward into the aisle
                _add_box_local_ft(
                    mesh, cx, cy, ux, uy, nx, ny,
                    -L * 0.5 - th_slat, -L * 0.5 - TOL_FT,
                    slat_t0, slat_t1,
                    z_slat_bot, z_slat_top,
                    birch_mat,
                )
            if add_end_slats:
                # Placed at s = +L/2, projecting outward
                _add_box_local_ft(
                    mesh, cx, cy, ux, uy, nx, ny,
                    L * 0.5 + TOL_FT, L * 0.5 + th_slat,
                    slat_t0, slat_t1,
                    z_slat_bot, z_slat_top,
                    birch_mat,
                )

    # -------------------------------------------------------------------------
    # 8. Varied Parametric Book Clusters (Detail 11 & Photographs)
    # -------------------------------------------------------------------------
    if populate_books:
        sides_config = (
            ((-1, -D * 0.5, -t_sp * 0.5), (1, t_sp * 0.5, D * 0.5))
            if double_sided
            else ((1, -D * 0.5 + t_sp, D * 0.5),)
        )

        for tier_idx, z_sh in enumerate(shelf_z_levels):
            z_bk_bot = z_sh + SHELF_THICK_M + TOL_M
            z_ceil = (
                z_top - t_canopy - TOL_M
                if tier_idx == n_tiers - 1
                else (shelf_z_levels[tier_idx + 1] - TOL_M)
            )
            h_open = z_ceil - z_bk_bot
            if h_open < 0.12:
                continue

            for bay_idx, (s_a, s_b) in enumerate(bay_bounds):
                bay_avail_s = (s_b - TOL_FT) - (s_a + TOL_FT)
                if bay_avail_s < 0.6:
                    continue

                for side_sign, t_back_limit, t_front_limit in sides_config:
                    n_clusters = 3 if bay_avail_s >= 2.4 else 2
                    m_end = 0.04
                    gap = 0.06
                    net_len = bay_avail_s - 2.0 * m_end - (n_clusters - 1) * gap
                    if net_len < 0.3:
                        continue
                    base_cluster_len = net_len / n_clusters

                    curr_s = s_a + TOL_FT + m_end
                    for c_idx in range(n_clusters):
                        r_len = _pseudo_rand(seed, bay_idx, tier_idx, side_sign, c_idx, 1)
                        r_h = _pseudo_rand(seed, bay_idx, tier_idx, side_sign, c_idx, 2)
                        r_d = _pseudo_rand(seed, bay_idx, tier_idx, side_sign, c_idx, 3)
                        r_mat = _pseudo_rand(seed, bay_idx, tier_idx, side_sign, c_idx, 4)

                        len_factor = 0.82 + 0.36 * r_len
                        c_len = base_cluster_len * len_factor
                        max_remain = (s_b - TOL_FT - m_end) - curr_s
                        if c_idx == n_clusters - 1 or c_len > max_remain:
                            c_len = max(0.20, max_remain)

                        b_s0 = curr_s
                        b_s1 = curr_s + c_len
                        curr_s = b_s1 + gap

                        # Varied authentic octavo/quarto volume heights (68% to 88% of bay opening)
                        h_factor = 0.68 + 0.20 * r_h
                        z_bk_top = z_bk_bot + min(h_open - 0.018, max(0.16, h_open * h_factor))

                        # Realistic spine setback from outer shelf face
                        setback = 0.08 + 0.04 * r_d
                        if side_sign > 0:
                            b_t0 = t_back_limit + 0.05
                            b_t1 = t_front_limit - setback
                        else:
                            b_t0 = t_front_limit + setback
                            b_t1 = t_back_limit - 0.05

                        if b_t1 <= b_t0 or b_s1 <= b_s0:
                            continue

                        book_key = BOOK_PALETTE[int(r_mat * len(BOOK_PALETTE)) % len(BOOK_PALETTE)]
                        book_mat = _furn_mat(book_key)

                        _add_box_local_ft(
                            mesh, cx, cy, ux, uy, nx, ny,
                            b_s0, b_s1, b_t0, b_t1,
                            z_bk_bot, z_bk_top,
                            book_mat,
                        )


def add_aalto_curved_bookwall_ft(
    mesh,
    center_ft: tuple[float, float],
    radius_ft: float,
    deg_start: float,
    deg_end: float,
    z_floor_m: float,
    height_m: float = 1.12,
    depth_ft: float = 1.15,
    n_shelf_tiers: int = 3,
    face_inward: bool = True,
    seed: int = 0,
):
    """
    Construct Alvar Aalto's faceted curved Reference Bookwall / Reading Well parapet bookcase
    (`Sheet 13-a13`, `Angel-090508`, `mezzaninewithdictionaryweb2`).

    Faceted along the arc into ~3.0 ft chord bays using `add_aalto_bookcase_ft(..., double_sided=False)`
    so the curved Mezzanine Reference Bookwall receives identical Aalto bay dividers, recessed kick
    plinths, solid birch shelves, top canopy, and curated book clusters.

    Parameters:
      mesh: IngeTrazo Mesh container
      center_ft: Working point center of the arc in feet (e.g. WP3A)
      radius_ft: Radius to centerline of bookcase in feet (e.g. 22.4 ft Mezzanine Reference Bookwall)
      deg_start: Start polar angle of the arc in degrees
      deg_end: End polar angle of the arc in degrees
      z_floor_m: Floor elevation in metres (e.g. Z_REF_GALLERY_FT)
      height_m: Height of curved bookcase in metres (default 1.12 m ~ 3'-8")
      depth_ft: Single-sided shelf depth in feet (default 1.15 ft ~ 14")
      n_shelf_tiers: Number of shelf tiers (default 3 tiers)
      face_inward: True if open shelves face toward the arc center (Reading Well); False for outer facing
      seed: Integer seed for book variation
    """
    cx, cy = float(center_ft[0]), float(center_ft[1])
    r = float(radius_ft)
    d_span = abs(deg_end - deg_start)
    arc_len = r * math.radians(d_span)
    n_facets = max(2, round(arc_len / BAY_MODULE_FT))
    d_step = (deg_end - deg_start) / n_facets

    for i in range(n_facets):
        d0 = deg_start + i * d_step
        d1 = d0 + d_step
        rad0 = math.radians(d0)
        rad1 = math.radians(d1)

        p0 = (cx + r * math.cos(rad0), cy + r * math.sin(rad0))
        p1 = (cx + r * math.cos(rad1), cy + r * math.sin(rad1))

        vx = p1[0] - p0[0]
        vy = p1[1] - p0[1]
        chord_len = math.hypot(vx, vy)
        if chord_len < 0.1:
            continue

        mid_x = (p0[0] + p1[0]) * 0.5
        mid_y = (p0[1] + p1[1]) * 0.5
        chord_deg = math.degrees(math.atan2(vy, vx))

        # Test normal direction relative to arc center
        chord_rad = math.radians(chord_deg)
        nx = -math.sin(chord_rad)
        ny = math.cos(chord_rad)
        to_center_x = cx - mid_x
        to_center_y = cy - mid_y
        dot_inward = nx * to_center_x + ny * to_center_y

        # Align +n with desired facing direction (inward or outward)
        if face_inward:
            if dot_inward < 0.0:
                chord_deg = (chord_deg + 180.0) % 360.0
        else:
            if dot_inward > 0.0:
                chord_deg = (chord_deg + 180.0) % 360.0

        add_aalto_bookcase_ft(
            mesh,
            center_ft=(mid_x, mid_y),
            length_ft=chord_len,
            depth_ft=depth_ft,
            angle_deg=chord_deg,
            z_floor_m=z_floor_m,
            height_m=height_m,
            double_sided=False,
            n_shelf_tiers=n_shelf_tiers,
            canopy_style="birch",
            end_slats="none",
            populate_books=True,
            seed=seed + i * 19,
        )
