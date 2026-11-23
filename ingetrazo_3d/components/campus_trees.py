"""
Mount Angel Abbey Hilltop Monumental Campus Trees (Layer 9: `9_Campus_Trees`).

Sculptural architectural-maquette tree library calibrated directly to the
Reference-North zoom-19 satellite ortho-aerial (`mount_angel_abbey_ortho_z19.png`),
archival Sheet 02-A2 ("Preserve Existing Trees"), and `campus_quad_aerial.jpg`.

Design philosophy (Museum Architectural Maquette — Non-Kludgy):
  - 100% closed, outward-oriented 2-manifold faceted polyhedra with zero
    self-intersecting tier artifacts (so both Solid and Ghost translucent-veil
    modes read like carved basswood / frosted-acrylic museum models).
  - Distinct botanical silhouettes recognizable from aerial & eye-level views:
      1. `cedar_lebanon` (*Cedrus libani*): Iconic 65–88 ft asymmetrical
         cantilevered tabular cloud canopies supported by spreading dark-umber
         boughs in muted glaucous blue-sage.
      2. `giant_sequoia` (*Sequoiadendron giganteum* / Cathedral PNW Conifers):
         90–114 ft continuous single-envelope fluted multi-tiered spire crowned
         by a mature rounded dome apex in deep PNW forest evergreen over a
         buttressed cinnamon-redwood trunk (zero internal discs in Ghost mode).
      3. `copper_beech` (*Fagus sylvatica* 'Purpurea') & `oak` (Specimen Quad
         Deciduous): Tapered Y-branched trunk supporting interlocking 80-facet
         geodesic icosphere canopies in deep smoky plum-bronze or olive-sage.
  - All trunks root solidly below `natural_hillside_z_m(x_ft, y_ft)` while
    leaving Aalto's Library North bluff corridor and South entry unobstructed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .primitives import add_face, add_quad, add_tri, create_scene_group, m_ft, xy_m
from .site_terrain import natural_hillside_z_m


@dataclass(frozen=True)
class TreeSpec:
    x_ft: float
    y_ft: float
    height_ft: float
    radius_ft: float
    species: str  # "cedar_lebanon" | "giant_sequoia" | "copper_beech" | "oak"
    note: str = ""


# =============================================================================
# MUTED ARCHITECTURAL MAQUETTE FOLIAGE & BARK PALETTES
# =============================================================================
# Tuned for the WebGL2 Reinhard tone-mapper so canopies sit harmoniously against
# `hill_grass` (0.37, 0.49, 0.31) and Mount Angel `buff_brick` (0.80, 0.68, 0.50).

BARK_CEDAR = {"color": (0.28, 0.23, 0.19), "roughness": 0.92, "metallic": 0.02}
BARK_SEQUOIA = {"color": (0.38, 0.22, 0.16), "roughness": 0.90, "metallic": 0.02}
BARK_DECIDUOUS = {"color": (0.31, 0.26, 0.22), "roughness": 0.92, "metallic": 0.02}

# Cedar of Lebanon: restrained dusty blue-sage (glaucous evergreen, never icy cyan)
CEDAR_TONES = (
    {"color": (0.21, 0.31, 0.27), "roughness": 0.92, "metallic": 0.02},
    {"color": (0.26, 0.37, 0.32), "roughness": 0.90, "metallic": 0.02},
    {"color": (0.31, 0.42, 0.37), "roughness": 0.88, "metallic": 0.02},
    {"color": (0.35, 0.46, 0.41), "roughness": 0.86, "metallic": 0.02},
)

# Giant Sequoia / Cathedral PNW Conifers: deep, rich Oregon evergreen
SEQUOIA_TONES = (
    {"color": (0.11, 0.20, 0.14), "roughness": 0.93, "metallic": 0.02},
    {"color": (0.14, 0.24, 0.17), "roughness": 0.91, "metallic": 0.02},
    {"color": (0.17, 0.28, 0.20), "roughness": 0.90, "metallic": 0.02},
    {"color": (0.21, 0.32, 0.23), "roughness": 0.88, "metallic": 0.02},
)

# Quad Specimen Copper Beeches: deep aristocratic smoky plum-bronze
BEECH_TONES = (
    {"color": (0.20, 0.13, 0.16), "roughness": 0.92, "metallic": 0.02},
    {"color": (0.25, 0.16, 0.19), "roughness": 0.90, "metallic": 0.02},
    {"color": (0.30, 0.20, 0.23), "roughness": 0.88, "metallic": 0.02},
)

# Quad Specimen Oaks / Maples: calm muted Willamette olive-sage
OAK_TONES = (
    {"color": (0.25, 0.34, 0.21), "roughness": 0.92, "metallic": 0.02},
    {"color": (0.30, 0.40, 0.25), "roughness": 0.90, "metallic": 0.02},
    {"color": (0.35, 0.45, 0.29), "roughness": 0.88, "metallic": 0.02},
)


def _hash_seed(x_ft: float, y_ft: float) -> float:
    """Deterministic pseudo-random phase in [0, 2*pi) from trunk coordinates."""
    v = math.sin(x_ft * 12.9898 + y_ft * 78.233) * 43758.5453
    return (v - math.floor(v)) * 2.0 * math.pi


def _organic_scale(angle_rad: float, seed: float, amp: float) -> float:
    """Smooth low-frequency radial modulation for calm sculptural asymmetry."""
    return 1.0 + amp * (
        0.58 * math.sin(2.0 * angle_rad + seed)
        + 0.42 * math.cos(3.0 * angle_rad - 1.7 * seed)
    )


# =============================================================================
# 100% CLOSED 2-MANIFOLD ARCHITECTURAL TREE PRIMITIVES
# =============================================================================

def _add_tapered_limb_m(
    mesh,
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    r0: float,
    r1: float,
    sides: int,
    mat: dict,
) -> None:
    """Closed 2-manifold tapered polygonal strut from `p0` (r0) to `p1` (r1)."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-4:
        return
    ux, uy, uz = dx / length, dy / length, dz / length
    ax, ay, az = (1.0, 0.0, 0.0) if abs(uz) > 0.85 else (0.0, 0.0, 1.0)
    tx = ay * uz - az * uy
    ty = az * ux - ax * uz
    tz = ax * uy - ay * ux
    tl = math.sqrt(tx * tx + ty * ty + tz * tz)
    tx, ty, tz = tx / tl, ty / tl, tz / tl
    bx = uy * tz - uz * ty
    by = uz * tx - ux * tz
    bz = ux * ty - uy * tx

    ring0: list[tuple[float, float, float]] = []
    ring1: list[tuple[float, float, float]] = []
    for i in range(sides):
        ang = (2.0 * math.pi * i) / sides
        ca, sa = math.cos(ang), math.sin(ang)
        rx = tx * ca + bx * sa
        ry = ty * ca + by * sa
        rz = tz * ca + bz * sa
        ring0.append((p0[0] + r0 * rx, p0[1] + r0 * ry, p0[2] + r0 * rz))
        ring1.append((p1[0] + r1 * rx, p1[1] + r1 * ry, p1[2] + r1 * rz))

    add_face(mesh, list(reversed(ring0)), mat)
    add_face(mesh, ring1, mat)
    for i in range(sides):
        j = (i + 1) % sides
        add_quad(mesh, ring0[i], ring0[j], ring1[j], ring1[i], mat)


def _add_layered_ring_solid_m(
    mesh,
    cx: float,
    cy: float,
    rings: list[tuple[float, float, float]],
    sides: int,
    rot_rad: float,
    seed: float,
    wobble: float,
    ring_mats: list[dict],
    cap_bot_mat: dict,
    cap_top_mat: dict,
    flute_amp: float = 0.0,
) -> None:
    """
    Closed 2-manifold continuous multi-ring sculpted canopy volume.

    `rings` is a bottom-to-top list of `(z_m, radius_m, twist_rad)`.
    Zero internal horizontal caps — renders crisply in both Solid & Ghost modes.
    """
    n_rings = len(rings)
    pts_rings: list[list[tuple[float, float, float]]] = []
    for z_m, rad, tw in rings:
        if rad <= 1e-4:
            pts_rings.append([(cx, cy, z_m)])
        else:
            rpts = []
            for i in range(sides):
                ang = rot_rad + tw + (2.0 * math.pi * i) / sides
                sc = _organic_scale(ang, seed, wobble)
                if flute_amp > 0.0:
                    sc *= 1.0 + flute_amp * (1.0 if (i % 2 == 0) else -1.0)
                rr = rad * sc
                rpts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang), z_m))
            pts_rings.append(rpts)

    if len(pts_rings[0]) == sides:
        add_face(mesh, list(reversed(pts_rings[0])), cap_bot_mat)

    for k in range(n_rings - 1):
        low = pts_rings[k]
        high = pts_rings[k + 1]
        mat = ring_mats[min(k, len(ring_mats) - 1)]
        if len(low) == sides and len(high) == sides:
            for i in range(sides):
                j = (i + 1) % sides
                add_quad(mesh, low[i], low[j], high[j], high[i], mat)
        elif len(low) == sides and len(high) == 1:
            apex = high[0]
            for i in range(sides):
                j = (i + 1) % sides
                add_tri(mesh, low[i], low[j], apex, mat)
        elif len(low) == 1 and len(high) == sides:
            apex = low[0]
            for i in range(sides):
                j = (i + 1) % sides
                add_tri(mesh, apex, high[j], high[i], mat)

    if len(pts_rings[-1]) == sides:
        add_face(mesh, pts_rings[-1], cap_top_mat)


# Cached unit 1-subdivided icosahedron (42 vertices, 80 outward-oriented triangular faces)
def _build_unit_geodesic_ico() -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    phi = (1.0 + math.sqrt(5.0)) * 0.5
    raw_verts = [
        (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
        (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
        (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1),
    ]
    verts: list[tuple[float, float, float]] = []
    for vx, vy, vz in raw_verts:
        l = math.sqrt(vx * vx + vy * vy + vz * vz)
        verts.append((vx / l, vy / l, vz / l))

    base_faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
    ]

    mid_cache: dict[tuple[int, int], int] = {}

    def midpoint(i0: int, i1: int) -> int:
        key = (i0, i1) if i0 < i1 else (i1, i0)
        if key in mid_cache:
            return mid_cache[key]
        a, b = verts[i0], verts[i1]
        mx, my, mz = 0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1]), 0.5 * (a[2] + b[2])
        ml = math.sqrt(mx * mx + my * my + mz * mz)
        idx = len(verts)
        verts.append((mx / ml, my / ml, mz / ml))
        mid_cache[key] = idx
        return idx

    faces: list[tuple[int, int, int]] = []
    for a, b, c in base_faces:
        ab = midpoint(a, b)
        bc = midpoint(b, c)
        ca = midpoint(c, a)
        for tri in ((a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)):
            p0, p1, p2 = verts[tri[0]], verts[tri[1]], verts[tri[2]]
            e1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
            e2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
            nx = e1[1] * e2[2] - e1[2] * e2[1]
            ny = e1[2] * e2[0] - e1[0] * e2[2]
            nz = e1[0] * e2[1] - e1[1] * e2[0]
            cx = p0[0] + p1[0] + p2[0]
            cy = p0[1] + p1[1] + p2[1]
            cz = p0[2] + p1[2] + p2[2]
            if nx * cx + ny * cy + nz * cz < 0.0:
                faces.append((tri[0], tri[2], tri[1]))
            else:
                faces.append(tri)
    return verts, faces


_ICO_VERTS, _ICO_FACES = _build_unit_geodesic_ico()


def _add_geodesic_lobe_m(
    mesh,
    cx: float,
    cy: float,
    cz: float,
    rx: float,
    ry: float,
    rz: float,
    rot_rad: float,
    seed: float,
    mat: dict,
    flat_top: float = 1.0,
) -> None:
    """Closed 80-facet sculptural geodesic canopy lobe (flat-faceted museum maquette)."""
    cr, sr = math.cos(rot_rad), math.sin(rot_rad)
    pts: list[tuple[float, float, float]] = []
    for vx, vy, vz in _ICO_VERTS:
        mod = 1.0 + 0.075 * math.sin(3.0 * vx + seed) * math.cos(2.5 * vy - seed)
        if vz < 0.0:
            z_mod = vz * 0.78
        else:
            z_mod = vz * flat_top
        lx = vx * rx * mod
        ly = vy * ry * mod
        wx = cx + lx * cr - ly * sr
        wy = cy + lx * sr + ly * cr
        wz = cz + z_mod * rz * mod
        pts.append((wx, wy, wz))
    for i0, i1, i2 in _ICO_FACES:
        add_tri(mesh, pts[i0], pts[i1], pts[i2], mat)


# =============================================================================
# BOTANICAL SPECIES BUILDERS
# =============================================================================

def add_cedar_of_lebanon(mesh, spec: TreeSpec) -> None:
    """
    Build an heirloom Mount Angel Cedar of Lebanon (*Cedrus libani*).

    Asymmetrical cantilevered flat-topped cloud tables branching gracefully
    outward from a heavy spreading dark-umber trunk & structural arms —
    avoiding symmetric pancake stacking while capturing the unmistakable
    horizontal glaucous silhouette of *Cedrus libani*.
    """
    cx, cy = xy_m((spec.x_ft, spec.y_ft))
    z0 = natural_hillside_z_m(spec.x_ft, spec.y_ft)
    h = m_ft(spec.height_ft)
    r = m_ft(spec.radius_ft)
    seed = _hash_seed(spec.x_ft, spec.y_ft)

    # 1. Massive slightly leaning dark-umber trunk rooted 1.8 m into hillside
    trunk_r0 = max(0.36, r * 0.088)
    trunk_r1 = max(0.16, r * 0.036)
    lean_x = math.cos(seed + 0.6) * r * 0.08
    lean_y = math.sin(seed + 0.6) * r * 0.08
    _add_tapered_limb_m(
        mesh,
        (cx, cy, z0 - 1.8),
        (cx + lean_x, cy + lean_y, z0 + h * 0.78),
        trunk_r0,
        trunk_r1,
        sides=7,
        mat=BARK_CEDAR,
    )

    # 2. Five asymmetrical cantilevered horizontal bough clouds (broad flat-topped geodesic slabs)
    # Tuple: (z_center_frac, r_horiz_frac, r_vert_frac, xy_offset_frac, azimuth_offset, tone_idx, has_limb)
    bough_clouds = (
        (0.30, 0.64, 0.135, 0.38, 0.00, 0, True),
        (0.41, 0.62, 0.130, 0.42, 2.25, 1, True),
        (0.55, 0.60, 0.125, 0.34, 4.35, 1, True),
        (0.71, 0.56, 0.120, 0.24, 1.15, 2, True),
        (0.86, 0.54, 0.115, 0.08, 3.60, 3, False),
    )

    for idx, (zcf, rhf, rvf, off_f, az_off, t_idx, has_limb) in enumerate(bough_clouds):
        ang = seed + az_off
        ox = cx + lean_x * zcf + math.cos(ang) * r * off_f
        oy = cy + lean_y * zcf + math.sin(ang) * r * off_f
        cz = z0 + h * zcf

        if has_limb:
            fork_z = z0 + h * max(0.18, zcf - 0.11)
            fork_t = max(0.18, zcf - 0.11)
            _add_tapered_limb_m(
                mesh,
                (cx + lean_x * fork_t, cy + lean_y * fork_t, fork_z),
                (ox, oy, cz - h * 0.03),
                trunk_r0 * (0.48 - 0.05 * idx),
                trunk_r1 * 0.75,
                sides=5,
                mat=BARK_CEDAR,
            )

        # Wide flattened geodesic cloud table (flat_top=0.58 produces authentic flat-topped Cedar silhouette!)
        _add_geodesic_lobe_m(
            mesh,
            ox,
            oy,
            cz,
            rx=r * rhf,
            ry=r * rhf * 0.86,
            rz=h * rvf,
            rot_rad=ang + 0.4,
            seed=seed + idx * 2.13,
            mat=CEDAR_TONES[t_idx],
            flat_top=0.58,
        )

    # Secondary lower sweeping shelf on wide heirloom specimens (R >= 24 ft)
    if spec.radius_ft >= 24.0:
        ang_w = seed + 5.30
        wx = cx + math.cos(ang_w) * r * 0.46
        wy = cy + math.sin(ang_w) * r * 0.46
        wz = z0 + h * 0.36
        _add_tapered_limb_m(
            mesh,
            (cx + lean_x * 0.24, cy + lean_y * 0.24, z0 + h * 0.24),
            (wx, wy, wz - h * 0.03),
            trunk_r0 * 0.44,
            trunk_r1 * 0.70,
            sides=5,
            mat=BARK_CEDAR,
        )
        _add_geodesic_lobe_m(
            mesh,
            wx,
            wy,
            wz,
            rx=r * 0.52,
            ry=r * 0.46,
            rz=h * 0.11,
            rot_rad=ang_w,
            seed=seed + 9.4,
            mat=CEDAR_TONES[0],
            flat_top=0.56,
        )


def add_giant_sequoia(mesh, spec: TreeSpec) -> None:
    """
    Build a 90–114 ft Mount Angel Giant Sequoia / Cathedral PNW Conifer.

    Built as ONE continuous, non-self-intersecting 2-manifold sculpted fluted
    envelope with rhythmic bough ledges and a mature domed apex over a
    buttressed cinnamon-redwood trunk — zero jagged overlaps in Solid mode and
    zero internal horizontal discs in Ghost translucent-veil mode!
    """
    cx, cy = xy_m((spec.x_ft, spec.y_ft))
    z0 = natural_hillside_z_m(spec.x_ft, spec.y_ft)
    h = m_ft(spec.height_ft)
    r = m_ft(spec.radius_ft)
    seed = _hash_seed(spec.x_ft, spec.y_ft)

    # 1. Buttressed cinnamon-redwood trunk (visible lower 18% below lowest bough skirt)
    trunk_r0 = max(0.46, r * 0.16)
    trunk_r1 = max(0.28, r * 0.10)
    _add_tapered_limb_m(
        mesh,
        (cx, cy, z0 - 2.0),
        (cx, cy, z0 + h * 0.24),
        trunk_r0,
        trunk_r1,
        sides=8,
        mat=BARK_SEQUOIA,
    )

    # 2. Single continuous 12-sided sculpted cathedral spire with 5 gentle rhythmic bough tiers
    # and a mature rounded Giant Sequoia dome apex (zero interpenetrating faces!).
    # Each entry: (z_frac, r_frac, twist_rad, tone_idx_for_band_above)
    profile = (
        (0.15, 0.70, 0.00, 0),  # Tucked lower skirt shadow underside
        (0.20, 1.00, 0.04, 0),  # Tier 1 drip edge
        (0.31, 0.84, 0.09, 0),  # Tier 1 taper-in waist
        (0.34, 0.91, 0.14, 1),  # Tier 2 bough ledge
        (0.46, 0.73, 0.20, 1),  # Tier 2 waist
        (0.49, 0.80, 0.25, 1),  # Tier 3 bough ledge
        (0.61, 0.61, 0.31, 2),  # Tier 3 waist
        (0.64, 0.67, 0.36, 2),  # Tier 4 bough ledge
        (0.75, 0.49, 0.42, 2),  # Tier 4 waist
        (0.78, 0.53, 0.47, 3),  # Tier 5 upper shoulder
        (0.88, 0.36, 0.52, 3),  # Mature Sequoia rounded dome lower
        (0.95, 0.21, 0.56, 3),  # Mature Sequoia rounded dome upper
        (1.00, 0.00, 0.58, 3),  # Rounded dome apex point
    )

    rings = [(z0 + h * zf, r * rf, tw) for zf, rf, tw, _ in profile]
    ring_mats = [SEQUOIA_TONES[t_idx] for _, _, _, t_idx in profile[:-1]]

    _add_layered_ring_solid_m(
        mesh,
        cx,
        cy,
        rings,
        sides=12,
        rot_rad=seed,
        seed=seed + 1.37,
        wobble=0.075,
        ring_mats=ring_mats,
        cap_bot_mat=SEQUOIA_TONES[0],
        cap_top_mat=SEQUOIA_TONES[3],
        flute_amp=0.055,
    )


def add_deciduous_specimen(mesh, spec: TreeSpec) -> None:
    """
    Build a Quad specimen Copper Beech or Oak/Maple in carved geodesic maquette style.

    Tapered trunk splitting into 3 Y-boughs supporting 4–5 interlocking 80-facet
    geodesic canopy lobes with warm sunlit vertical tonal variation.
    """
    cx, cy = xy_m((spec.x_ft, spec.y_ft))
    z0 = natural_hillside_z_m(spec.x_ft, spec.y_ft)
    h = m_ft(spec.height_ft)
    r = m_ft(spec.radius_ft)
    seed = _hash_seed(spec.x_ft, spec.y_ft)
    tones = BEECH_TONES if spec.species == "copper_beech" else OAK_TONES

    trunk_r0 = max(0.28, r * 0.082)
    trunk_r1 = max(0.16, r * 0.048)
    fork_z = z0 + h * 0.28
    _add_tapered_limb_m(
        mesh,
        (cx, cy, z0 - 1.8),
        (cx, cy, fork_z),
        trunk_r0,
        trunk_r1,
        sides=7,
        mat=BARK_DECIDUOUS,
    )

    for k in range(3):
        ang = seed + (2.0 * math.pi * k) / 3.0
        off_r = r * (0.38 + 0.06 * math.sin(seed + k * 2.1))
        lx = cx + math.cos(ang) * off_r
        ly = cy + math.sin(ang) * off_r
        lz = z0 + h * (0.54 + 0.05 * math.cos(seed + k * 1.9))

        _add_tapered_limb_m(
            mesh,
            (cx, cy, fork_z - 0.25),
            (lx, ly, lz - h * 0.08),
            trunk_r1 * 0.85,
            trunk_r1 * 0.42,
            sides=5,
            mat=BARK_DECIDUOUS,
        )

        lr = r * (0.62 + 0.05 * math.sin(seed + k * 3.1))
        _add_geodesic_lobe_m(
            mesh,
            lx,
            ly,
            lz,
            rx=lr,
            ry=lr * 0.94,
            rz=h * 0.28,
            rot_rad=ang,
            seed=seed + k * 2.3,
            mat=tones[0 if k == 0 else 1],
        )

    _add_geodesic_lobe_m(
        mesh,
        cx + math.cos(seed + 1.0) * r * 0.08,
        cy + math.sin(seed + 1.0) * r * 0.08,
        z0 + h * 0.72,
        rx=r * 0.68,
        ry=r * 0.64,
        rz=h * 0.28,
        rot_rad=seed * 0.7,
        seed=seed + 9.1,
        mat=tones[2],
    )

    if spec.radius_ft >= 24.0:
        ang4 = seed + 1.05
        _add_geodesic_lobe_m(
            mesh,
            cx + math.cos(ang4) * r * 0.44,
            cy + math.sin(ang4) * r * 0.44,
            z0 + h * 0.46,
            rx=r * 0.52,
            ry=r * 0.50,
            rz=h * 0.23,
            rot_rad=ang4,
            seed=seed + 5.7,
            mat=tones[0],
        )


# =============================================================================
# SURVEYED MOUNT ANGEL ABBEY CAMPUS TREE CATALOG (WP #3 FEET)
# =============================================================================
# Verified against the 25-ft Reference-North ortho-aerial maps, Sheet 02-A2,
# and `docs/photos/campus_quad_aerial.jpg` (spring deciduous vs evergreen ID).

CAMPUS_TREES: tuple[TreeSpec, ...] = (
    # --- A. ICONIC CEDARS OF LEBANON (*Cedrus libani*) — Silvery Blue-Sage Spreading Crowns ---
    TreeSpec(-18.0, -116.0, 68.0, 26.0, "cedar_lebanon", "Library South Lawn West Cedar of Lebanon"),
    TreeSpec(38.0, -112.0, 78.0, 32.0, "cedar_lebanon", "Library South Lawn Monumental Cedar of Lebanon"),
    TreeSpec(150.0, -56.0, 74.0, 23.0, "cedar_lebanon", "Aquinas SW Historic Cedar of Lebanon"),
    TreeSpec(34.0, -285.0, 82.0, 29.0, "cedar_lebanon", "South-Central Quad Monumental Cedar of Lebanon"),
    TreeSpec(-56.0, -298.0, 72.0, 24.0, "cedar_lebanon", "SW Crescent Walk Cedar of Lebanon"),
    TreeSpec(-24.0, -268.0, 54.0, 16.0, "cedar_lebanon", "SW Quad Companion Cedar of Lebanon"),

    # --- B. SOUTH QUAD 100-FT GIANT SEQUOIA CATHEDRAL WALL (Retreat Center / South Rim) ---
    TreeSpec(-98.0, -342.0, 96.0, 22.0, "giant_sequoia", "SW Crescent Giant Sequoia"),
    TreeSpec(-38.0, -365.0, 100.0, 24.0, "giant_sequoia", "South Quad Sequoia #1"),
    TreeSpec(-8.0, -369.0, 106.0, 23.0, "giant_sequoia", "South Quad Sequoia #2"),
    TreeSpec(32.0, -366.0, 112.0, 25.0, "giant_sequoia", "South Quad Sequoia #3 (Tallest)"),
    TreeSpec(74.0, -368.0, 108.0, 25.0, "giant_sequoia", "South Quad Sequoia #4"),
    TreeSpec(115.0, -366.0, 104.0, 24.0, "giant_sequoia", "South Quad Sequoia #5"),
    TreeSpec(150.0, -366.0, 100.0, 24.0, "giant_sequoia", "South Quad Sequoia #6"),
    TreeSpec(178.0, -368.0, 95.0, 21.0, "giant_sequoia", "South Quad Sequoia #7"),

    # --- C. SHEET 02-A2 PRESERVED LIBRARY-AQUINAS EVERGREEN GROVE ---
    TreeSpec(102.0, -24.0, 96.0, 21.0, "giant_sequoia", "Sheet 02-A2 Preserved Grove North Conifer"),
    TreeSpec(126.0, -34.0, 84.0, 18.0, "giant_sequoia", "Sheet 02-A2 Preserved Grove East Conifer"),
    TreeSpec(88.0, -48.0, 58.0, 14.0, "giant_sequoia", "Sheet 02-A2 Preserved Grove South Conifer"),

    # --- D. ABBEY CHURCH, BELL TOWER & EAST MONASTERY BACKDROP SEQUOIA SPIRES ---
    TreeSpec(516.0, -268.0, 114.0, 28.0, "giant_sequoia", "East Monastery Giant Sequoia Spire #1"),
    TreeSpec(476.0, -312.0, 108.0, 24.0, "giant_sequoia", "East Monastery Giant Sequoia Spire #2"),
    TreeSpec(496.0, -346.0, 102.0, 23.0, "giant_sequoia", "East Monastery Giant Sequoia Spire #3"),
    TreeSpec(538.0, -322.0, 108.0, 25.0, "giant_sequoia", "East Monastery Giant Sequoia Spire #4"),
    TreeSpec(492.0, -396.0, 96.0, 23.0, "giant_sequoia", "SE Bluff Giant Sequoia"),
    TreeSpec(524.0, -110.0, 96.0, 24.0, "giant_sequoia", "NE Monastery Backdrop Conifer"),
    TreeSpec(502.0, -184.0, 86.0, 20.0, "giant_sequoia", "East Apse Garden Conifer"),
    TreeSpec(382.0, -388.0, 88.0, 21.0, "giant_sequoia", "Retreat-Monastery Framing Conifer"),

    # --- E. WEST BLUFF, POST-KNOX & DAMIAN CENTER MONUMENTAL CONIFERS ---
    TreeSpec(-252.0, 38.0, 90.0, 23.0, "giant_sequoia", "Post-Knox / Anselm Courtyard Conifer"),
    TreeSpec(-136.0, 82.0, 82.0, 19.0, "giant_sequoia", "Post-Knox NE Bluff Conifer"),
    TreeSpec(-216.0, 114.0, 94.0, 24.0, "giant_sequoia", "North Abbey Drive West Bluff Sequoia"),
    TreeSpec(-392.0, -88.0, 78.0, 20.0, "giant_sequoia", "NW Quad Gateway Conifer"),
    TreeSpec(-496.0, -162.0, 96.0, 22.0, "giant_sequoia", "Damian Center NW Giant Sequoia"),
    TreeSpec(-496.0, -238.0, 88.0, 21.0, "giant_sequoia", "Damian Center SW Giant Sequoia"),

    # --- F. TWO ICONIC QUAD COPPER BEECHES (*Fagus sylvatica* 'Purpurea') ---
    TreeSpec(148.0, -142.0, 74.0, 30.0, "copper_beech", "North Quad Grand Copper Beech"),
    TreeSpec(116.0, -276.0, 62.0, 20.0, "copper_beech", "South Quad Specimen Copper Beech"),

    # --- G. QUAD & PERIMETER SPECIMEN DECIDUOUS OAKS / MAPLES (Verified via Spring Aerial) ---
    TreeSpec(-92.0, -138.0, 54.0, 21.0, "oak", "Anselm-Library SW Quad Specimen Oak"),
    TreeSpec(-122.0, -104.0, 48.0, 18.0, "oak", "Anselm East Wing Courtyard Oak"),
    TreeSpec(-84.0, -252.0, 56.0, 20.0, "oak", "SW Crescent Walk Specimen Oak"),
    TreeSpec(232.0, -108.0, 58.0, 20.0, "oak", "Abbey Church NW Forecourt Oak"),
    TreeSpec(228.0, -280.0, 52.0, 18.0, "oak", "Abbey Church SW Forecourt Oak"),
    TreeSpec(232.0, -322.0, 48.0, 16.0, "oak", "Abbey Church SW Companion Maple"),
    TreeSpec(-268.0, -148.0, 56.0, 21.0, "oak", "Anselm Hall South Lawn Oak"),
    TreeSpec(-292.0, -268.0, 48.0, 18.0, "oak", "SW Quad Specimen Oak West"),
    TreeSpec(-268.0, -284.0, 44.0, 15.0, "oak", "SW Quad Specimen Oak East"),
    TreeSpec(-370.0, -28.0, 60.0, 23.0, "oak", "Anselm NW Arrival Oak"),
    TreeSpec(-460.0, -76.0, 56.0, 21.0, "oak", "Damian North Arrival Oak"),
    TreeSpec(-425.0, -356.0, 58.0, 23.0, "oak", "SW Bluff Annunciation Oak"),
    TreeSpec(-336.0, 112.0, 62.0, 23.0, "oak", "NW Bluff Roadway Oak"),

    # --- H. FAR NORTH BLUFF MARGIN FRAMING (Keeping Library North View Corridor 100% Open) ---
    TreeSpec(-355.0, 194.0, 86.0, 22.0, "giant_sequoia", "Far NW Bluff Rim Conifer"),
    TreeSpec(-265.0, 196.0, 92.0, 23.0, "giant_sequoia", "NW Bluff Rim Conifer"),
    TreeSpec(-185.0, 196.0, 80.0, 21.0, "oak", "NW Bluff Rim Broadleaf"),
    TreeSpec(255.0, 166.0, 86.0, 22.0, "giant_sequoia", "NE Bluff Rim Conifer"),
    TreeSpec(355.0, 162.0, 88.0, 23.0, "giant_sequoia", "NE Bluff Rim Conifer East"),
    TreeSpec(455.0, 154.0, 82.0, 22.0, "oak", "Far NE Bluff Rim Broadleaf"),
)


def build_campus_trees(scene):
    """Build Layer 9 (`9_Campus_Trees`): sculptural surveyed hilltop arboretum."""
    grp = create_scene_group(scene, "9_Campus_Trees")
    mesh = grp.mesh

    for spec in CAMPUS_TREES:
        if spec.species == "cedar_lebanon":
            add_cedar_of_lebanon(mesh, spec)
        elif spec.species == "giant_sequoia":
            add_giant_sequoia(mesh, spec)
        else:
            add_deciduous_specimen(mesh, spec)

    return grp
