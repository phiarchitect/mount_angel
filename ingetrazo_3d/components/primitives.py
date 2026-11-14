"""
Shared 3D geometry primitives, ear-clipping concave polygon triangulation,
extruded architectural elements, and Alvar Aalto material palette for
IngeTrazo 0.6.0 (`mount_angel_library.igz`).

Coordinate System (Metres, Z-Up):
  - Origin (0, 0, 0): Working Point #4 on Level 3 Finished Floor
  - +X = East, +Y = North (Grid Line 6 along Y = 0), +Z = Upward
"""

from __future__ import annotations

import math

FT_TO_M = 0.3048


def m_ft(val_ft: float) -> float:
    """Convert decimal feet to metres."""
    return float(val_ft) * FT_TO_M


def xy_m(pt_ft: tuple[float, float]) -> tuple[float, float]:
    """Convert 2D (X_ft, Y_ft) to (X_m, Y_m)."""
    return (pt_ft[0] * FT_TO_M, pt_ft[1] * FT_TO_M)


# =============================================================================
# ALVAR AALTO MATERIAL PALETTE (MOUNT ANGEL ABBEY LIBRARY, 1970)
# =============================================================================

MATERIALS: dict[str, dict] = {
    # Exterior Masonry & Concrete
    "buff_brick": {"color": (0.80, 0.68, 0.50), "roughness": 0.84, "metallic": 0.04},
    "buff_brick_dark": {"color": (0.70, 0.57, 0.40), "roughness": 0.88, "metallic": 0.05},
    "concrete": {"color": (0.66, 0.65, 0.61), "roughness": 0.86, "metallic": 0.05},
    "concrete_dark": {"color": (0.50, 0.50, 0.48), "roughness": 0.90, "metallic": 0.05},
    "plaza_paving": {"color": (0.75, 0.72, 0.66), "roughness": 0.82, "metallic": 0.04},
    "hill_grass": {"color": (0.37, 0.49, 0.31), "roughness": 0.94, "metallic": 0.02},
    "hill_earth": {"color": (0.43, 0.38, 0.31), "roughness": 0.95, "metallic": 0.02},

    # Interior Plaster, Structure & Flooring
    "white_plaster": {"color": (0.95, 0.94, 0.91), "roughness": 0.72, "metallic": 0.02},
    "white_soffit": {"color": (0.92, 0.91, 0.88), "roughness": 0.75, "metallic": 0.02},
    "white_column": {"color": (0.93, 0.92, 0.89), "roughness": 0.58, "metallic": 0.06},
    "steel_pier": {"color": (0.22, 0.23, 0.25), "roughness": 0.46, "metallic": 0.72},
    "floor_oatmeal": {"color": (0.71, 0.67, 0.60), "roughness": 0.80, "metallic": 0.03},
    "floor_lobby": {"color": (0.62, 0.58, 0.53), "roughness": 0.76, "metallic": 0.04},
    "floor_lower": {"color": (0.66, 0.64, 0.59), "roughness": 0.82, "metallic": 0.03},

    # Aalto Birch, Hemlock, Black Linoleum & Brass Millwork
    "birch_wood": {"color": (0.82, 0.63, 0.40), "roughness": 0.54, "metallic": 0.05},
    "hemlock_slat": {"color": (0.75, 0.55, 0.33), "roughness": 0.58, "metallic": 0.05},
    "louver_wood": {"color": (0.67, 0.47, 0.28), "roughness": 0.64, "metallic": 0.06},
    "black_linoleum": {"color": (0.14, 0.15, 0.17), "roughness": 0.48, "metallic": 0.08},
    "brass": {"color": (0.82, 0.66, 0.31), "roughness": 0.28, "metallic": 0.86},
    "lamp_shade": {"color": (0.98, 0.96, 0.90), "roughness": 0.30, "metallic": 0.12},
    "lamp_glow": {"color": (1.00, 0.95, 0.82), "emissive": True},

    # Roof & Skylights
    "copper_roof": {"color": (0.45, 0.32, 0.23), "roughness": 0.42, "metallic": 0.76},
    "copper_patina": {"color": (0.37, 0.47, 0.41), "roughness": 0.50, "metallic": 0.62},
    "builtup_roof": {"color": (0.76, 0.74, 0.70), "roughness": 0.88, "metallic": 0.04},
    "mullion_bronze": {"color": (0.28, 0.26, 0.24), "roughness": 0.42, "metallic": 0.74},
    "mullion_alum": {"color": (0.78, 0.80, 0.82), "roughness": 0.34, "metallic": 0.80},
    "glass_clear": {"color": (0.56, 0.77, 0.88), "opacity": 0.30, "roughness": 0.12, "metallic": 0.12},
    "glass_skylight": {"color": (0.78, 0.91, 0.98), "opacity": 0.42, "roughness": 0.16, "metallic": 0.10},

    # Book Collection Accents
    "book_terracotta": {"color": (0.66, 0.31, 0.25), "roughness": 0.78, "metallic": 0.02},
    "book_slate": {"color": (0.27, 0.36, 0.46), "roughness": 0.78, "metallic": 0.02},
    "book_ochre": {"color": (0.72, 0.56, 0.28), "roughness": 0.78, "metallic": 0.02},
    "book_sage": {"color": (0.38, 0.48, 0.39), "roughness": 0.78, "metallic": 0.02},

    # Constructive Regulating Lines
    "reg_cyan": {"color": (0.10, 0.85, 0.98), "emissive": True},
    "reg_amber": {"color": (0.98, 0.62, 0.16), "emissive": True},
    "reg_purple": {"color": (0.74, 0.44, 0.98), "emissive": True},
}


# =============================================================================
# LOW-LEVEL INGETRAZO MESH HELPERS
# =============================================================================

def create_scene_group(scene, name: str):
    """Create a named IngeTrazo Group with an empty Mesh and append to scene.groups."""
    from core.group import Group
    from core.mesh import Mesh

    grp = Group(name=name, mesh=Mesh())
    scene.groups.append(grp)
    return grp


def add_face(mesh, pts, attrs: dict):
    from PySide6.QtGui import QVector3D

    qpts = [p if isinstance(p, QVector3D) else QVector3D(*p) for p in pts]
    f = mesh.add_face(qpts)
    if f is not None and attrs:
        f.attrs.update(attrs)
    return f


def add_tri(mesh, p0, p1, p2, attrs: dict):
    add_face(mesh, [p0, p1, p2], dict(attrs))


def add_quad(mesh, p0, p1, p2, p3, attrs: dict):
    add_face(mesh, [p0, p1, p2, p3], dict(attrs))


def add_box_m(mesh, x0: float, y0: float, z0: float, x1: float, y1: float, z1: float, attrs: dict):
    """Add an axis-aligned 3D box in metres with outward-facing CCW normals."""
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    if z0 > z1:
        z0, z1 = z1, z0
    p000 = (x0, y0, z0)
    p100 = (x1, y0, z0)
    p110 = (x1, y1, z0)
    p010 = (x0, y1, z0)
    p001 = (x0, y0, z1)
    p101 = (x1, y0, z1)
    p111 = (x1, y1, z1)
    p011 = (x0, y1, z1)
    add_quad(mesh, p000, p010, p110, p100, attrs)  # bottom (-Z)
    add_quad(mesh, p001, p101, p111, p011, attrs)  # top (+Z)
    add_quad(mesh, p000, p100, p101, p001, attrs)  # south (-Y)
    add_quad(mesh, p100, p110, p111, p101, attrs)  # east (+X)
    add_quad(mesh, p110, p010, p011, p111, attrs)  # north (+Y)
    add_quad(mesh, p010, p000, p001, p011, attrs)  # west (-X)


def add_oriented_box_ft(
    mesh,
    center_ft: tuple[float, float],
    length_ft: float,
    width_ft: float,
    angle_deg: float,
    z0_m: float,
    z1_m: float,
    attrs: dict,
):
    """Add a rotated 3D box given 2D center/size in feet and Z bounds in metres."""
    rad = math.radians(angle_deg)
    ux, uy = math.cos(rad), math.sin(rad)
    nx, ny = -uy, ux
    hl, hw = length_ft * 0.5, width_ft * 0.5
    cx, cy = center_ft
    poly_ft = [
        (cx - hl * ux - hw * nx, cy - hl * uy - hw * ny),
        (cx + hl * ux - hw * nx, cy + hl * uy - hw * ny),
        (cx + hl * ux + hw * nx, cy + hl * uy + hw * ny),
        (cx - hl * ux + hw * nx, cy - hl * uy + hw * ny),
    ]
    add_extruded_polygon_ft(mesh, poly_ft, z0_m, z1_m, attrs)


# =============================================================================
# CONCAVE 2D POLYGON EAR-CLIPPING & EXTRUSION
# =============================================================================

def _signed_area_2d(pts: list[tuple[float, float]]) -> float:
    area = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        area += x0 * y1 - x1 * y0
    return 0.5 * area


def _pt_in_tri_2d(p, a, b, c) -> bool:
    def cross(o, u, v):
        return (u[0] - o[0]) * (v[1] - o[1]) - (u[1] - o[1]) * (v[0] - o[0])

    c1 = cross(a, b, p)
    c2 = cross(b, c, p)
    c3 = cross(c, a, p)
    return (c1 >= -1e-9 and c2 >= -1e-9 and c3 >= -1e-9)


def triangulate_polygon_2d(poly: list[tuple[float, float]]) -> tuple[list[tuple[float, float]], list[tuple[int, int, int]]]:
    """
    Ear-clipping triangulation of a simple (possibly concave) 2D polygon.
    Returns `(ccw_pts, triangles)` where every triangle `(i, j, k)` is CCW (+Z normal).
    """
    pts = list(poly)
    # Remove consecutive duplicate vertices
    cleaned: list[tuple[float, float]] = []
    for p in pts:
        if not cleaned or math.hypot(p[0] - cleaned[-1][0], p[1] - cleaned[-1][1]) > 1e-5:
            cleaned.append(p)
    if len(cleaned) > 1 and math.hypot(cleaned[0][0] - cleaned[-1][0], cleaned[0][1] - cleaned[-1][1]) <= 1e-5:
        cleaned.pop()

    if _signed_area_2d(cleaned) < 0.0:
        cleaned.reverse()

    n = len(cleaned)
    if n < 3:
        return cleaned, []
    if n == 3:
        return cleaned, [(0, 1, 2)]

    idxs = list(range(n))
    tris: list[tuple[int, int, int]] = []
    guard = 0
    while len(idxs) > 3 and guard < n * n + 20:
        guard += 1
        ear_found = False
        m = len(idxs)
        for k in range(m):
            i_prev = idxs[(k - 1) % m]
            i_curr = idxs[k]
            i_next = idxs[(k + 1) % m]
            a, b, c = cleaned[i_prev], cleaned[i_curr], cleaned[i_next]
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if cross <= 1e-8:
                continue
            # Check no other active vertex lies inside triangle (a, b, c)
            inside = False
            for j in idxs:
                if j in (i_prev, i_curr, i_next):
                    continue
                if _pt_in_tri_2d(cleaned[j], a, b, c):
                    inside = True
                    break
            if not inside:
                tris.append((i_prev, i_curr, i_next))
                idxs.pop(k)
                ear_found = True
                break
        if not ear_found:
            # Fallback fan for degenerate collinear vertices
            tris.append((idxs[0], idxs[1], idxs[2]))
            idxs.pop(1)

    if len(idxs) == 3:
        tris.append((idxs[0], idxs[1], idxs[2]))
    return cleaned, tris


def add_extruded_polygon_ft(
    mesh,
    poly_ft: list[tuple[float, float]],
    z0_m: float,
    z1_m: float,
    top_attrs: dict,
    side_attrs: dict | None = None,
    bottom_attrs: dict | None = None,
):
    """Extrude a 2D polygon (in feet) vertically between `z0_m` and `z1_m`."""
    if z0_m > z1_m:
        z0_m, z1_m = z1_m, z0_m
    s_attrs = side_attrs or top_attrs
    b_attrs = bottom_attrs or s_attrs

    pts_m = [xy_m(p) for p in poly_ft]
    ccw_pts, tris = triangulate_polygon_2d(pts_m)
    if len(ccw_pts) < 3:
        return

    # Top (+Z) and Bottom (-Z) triangulated caps
    for i0, i1, i2 in tris:
        x0, y0 = ccw_pts[i0]
        x1, y1 = ccw_pts[i1]
        x2, y2 = ccw_pts[i2]
        add_tri(mesh, (x0, y0, z1_m), (x1, y1, z1_m), (x2, y2, z1_m), top_attrs)
        add_tri(mesh, (x0, y0, z0_m), (x2, y2, z0_m), (x1, y1, z0_m), b_attrs)

    # Perimeter side quads (CCW loop -> outward normal when ordered p0_b, p1_b, p1_t, p0_t)
    m = len(ccw_pts)
    for i in range(m):
        x0, y0 = ccw_pts[i]
        x1, y1 = ccw_pts[(i + 1) % m]
        add_quad(
            mesh,
            (x0, y0, z0_m),
            (x1, y1, z0_m),
            (x1, y1, z1_m),
            (x0, y0, z1_m),
            s_attrs,
        )


def add_wall_strip_ft(
    mesh,
    pts_ft: list[tuple[float, float]],
    thickness_ft: float,
    z0_m: float,
    z1_m: float,
    attrs: dict,
    offset_mode: str = "center",  # "center", "left", "right"
):
    """Extrude a multi-segment wall along `pts_ft` with clean mitered corners."""
    n = len(pts_ft)
    if n < 2:
        return
    if offset_mode == "center":
        d_left, d_right = thickness_ft * 0.5, -thickness_ft * 0.5
    elif offset_mode == "left":
        d_left, d_right = thickness_ft, 0.0
    else:
        d_left, d_right = 0.0, -thickness_ft

    seg_normals = []
    for i in range(n - 1):
        dx = pts_ft[i + 1][0] - pts_ft[i][0]
        dy = pts_ft[i + 1][1] - pts_ft[i][1]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            seg_normals.append((0.0, 1.0))
        else:
            seg_normals.append((-dy / L, dx / L))  # left normal

    left_pts = []
    right_pts = []
    for i in range(n):
        if i == 0:
            nx, ny = seg_normals[0]
        elif i == n - 1:
            nx, ny = seg_normals[-1]
        else:
            n0x, n0y = seg_normals[i - 1]
            n1x, n1y = seg_normals[i]
            mx, my = n0x + n1x, n0y + n1y
            ml = math.hypot(mx, my)
            if ml < 1e-4:
                nx, ny = n1x, n1y
            else:
                mx /= ml
                my /= ml
                dot = max(0.45, mx * n1x + my * n1y)
                nx, ny = mx / dot, my / dot
        px, py = pts_ft[i]
        left_pts.append((px + nx * d_left, py + ny * d_left))
        right_pts.append((px + nx * d_right, py + ny * d_right))

    poly_ft = right_pts + list(reversed(left_pts))
    add_extruded_polygon_ft(mesh, poly_ft, z0_m, z1_m, attrs)


def add_arc_band_ft(
    mesh,
    center_ft: tuple[float, float],
    r_in_ft: float,
    r_out_ft: float,
    deg0: float,
    deg1: float,
    z0_m: float,
    z1_m: float,
    attrs: dict,
    steps: int = 36,
):
    """Build a solid curved annular band (parapet, counter, drum, skylight curb)."""
    if deg0 > deg1:
        deg0, deg1 = deg1, deg0
    cx, cy = center_ft
    outer_arc = []
    inner_arc = []
    for i in range(steps + 1):
        ang = math.radians(deg0 + (deg1 - deg0) * (i / steps))
        ca, sa = math.cos(ang), math.sin(ang)
        outer_arc.append((cx + r_out_ft * ca, cy + r_out_ft * sa))
        inner_arc.append((cx + r_in_ft * ca, cy + r_in_ft * sa))

    # Build as individual annular quad segments so convexity is guaranteed without ear-clipping stress
    for i in range(steps):
        seg_poly = [inner_arc[i], outer_arc[i], outer_arc[i + 1], inner_arc[i + 1]]
        add_extruded_polygon_ft(mesh, seg_poly, z0_m, z1_m, attrs)


def add_cylinder_ft(
    mesh,
    center_ft: tuple[float, float],
    radius_ft: float,
    z0_m: float,
    z1_m: float,
    attrs: dict,
    sides: int = 16,
):
    """Add a vertical cylinder centered at `center_ft` with radius in feet and Z in metres."""
    cx, cy = center_ft
    poly = [
        (cx + radius_ft * math.cos(2.0 * math.pi * i / sides), cy + radius_ft * math.sin(2.0 * math.pi * i / sides))
        for i in range(sides)
    ]
    add_extruded_polygon_ft(mesh, poly, z0_m, z1_m, attrs)


def add_frustum_ft(
    mesh,
    center_ft: tuple[float, float],
    r0_ft: float,
    r1_ft: float,
    z0_m: float,
    z1_m: float,
    attrs: dict,
    sides: int = 18,
    cap_top: bool = False,
    cap_bottom: bool = False,
    double_sided: bool = False,
):
    """Add a conical frustum (for Aalto's conical skylight throats & dome lamps)."""
    cx_m, cy_m = xy_m(center_ft)
    r0_m, r1_m = m_ft(r0_ft), m_ft(r1_ft)
    ring0 = []
    ring1 = []
    for i in range(sides):
        ang = 2.0 * math.pi * i / sides
        ca, sa = math.cos(ang), math.sin(ang)
        ring0.append((cx_m + r0_m * ca, cy_m + r0_m * sa, z0_m))
        ring1.append((cx_m + r1_m * ca, cy_m + r1_m * sa, z1_m))

    for i in range(sides):
        j = (i + 1) % sides
        add_quad(mesh, ring0[i], ring0[j], ring1[j], ring1[i], attrs)
        if double_sided:
            add_quad(mesh, ring0[j], ring0[i], ring1[i], ring1[j], attrs)

    if cap_top and r1_m > 1e-4:
        top_c = (cx_m, cy_m, z1_m)
        for i in range(sides):
            j = (i + 1) % sides
            add_tri(mesh, top_c, ring1[i], ring1[j], attrs)
    if cap_bottom and r0_m > 1e-4:
        bot_c = (cx_m, cy_m, z0_m)
        for i in range(sides):
            j = (i + 1) % sides
            add_tri(mesh, bot_c, ring0[j], ring0[i], attrs)


def add_louver_bank_ft(
    mesh,
    p0_ft: tuple[float, float],
    p1_ft: tuple[float, float],
    z0_m: float,
    z1_m: float,
    spacing_ft: float = 2.2,
    blade_depth_ft: float = 1.0,
    blade_thick_ft: float = 0.22,
    attrs: dict | None = None,
):
    """Add a bank of Aalto exterior vertical wood sun-shading louvers along segment p0 -> p1."""
    mat = attrs or MATERIALS["louver_wood"]
    dx, dy = p1_ft[0] - p0_ft[0], p1_ft[1] - p0_ft[1]
    L = math.hypot(dx, dy)
    if L < 1.0:
        return
    ux, uy = dx / L, dy / L
    # Outward normal (assuming p0 -> p1 runs clockwise around fan N facade: (-uy, ux) points North/Outward!)
    nx, ny = -uy, ux
    ang_deg = math.degrees(math.atan2(ny, nx))
    count = max(2, int(L / spacing_ft))
    for i in range(1, count):
        t = i / count
        bx = p0_ft[0] + dx * t + nx * (blade_depth_ft * 0.55)
        by = p0_ft[1] + dy * t + ny * (blade_depth_ft * 0.55)
        add_oriented_box_ft(mesh, (bx, by), blade_depth_ft, blade_thick_ft, ang_deg, z0_m, z1_m, mat)


def add_stepped_stair_ft(
    mesh,
    p_top_ft: tuple[float, float],
    p_bot_ft: tuple[float, float],
    width_ft: float,
    z_top_m: float,
    z_bot_m: float,
    n_steps: int = 16,
):
    """Build a true 3D stepped architectural stair with birch treads, white stringers, and brass handrails."""
    dx, dy = p_bot_ft[0] - p_top_ft[0], p_bot_ft[1] - p_top_ft[1]
    L = math.hypot(dx, dy)
    if L < 0.5:
        return
    ang_deg = math.degrees(math.atan2(dy, dx))
    rad = math.radians(ang_deg)
    ux, uy = math.cos(rad), math.sin(rad)
    nx, ny = -uy, ux

    step_run = L / n_steps
    dz = (z_top_m - z_bot_m) / n_steps
    for s in range(n_steps):
        scx = p_top_ft[0] + ux * (s + 0.5) * step_run
        scy = p_top_ft[1] + uy * (s + 0.5) * step_run
        zt = z_top_m - s * dz
        zb = zt - dz - 0.14
        add_oriented_box_ft(mesh, (scx, scy), step_run * 1.04, width_ft - 0.3, ang_deg, zb, zt, MATERIALS["birch_wood"])

    # Flanking white stringer / balustrade walls + brass top handrails
    for side in (-1.0, 1.0):
        off = side * (width_ft * 0.5 - 0.12)
        s0 = xy_m((p_top_ft[0] + nx * off, p_top_ft[1] + ny * off))
        s1 = xy_m((p_bot_ft[0] + nx * off, p_bot_ft[1] + ny * off))
        s0_in = xy_m((p_top_ft[0] + nx * (off - side * 0.22), p_top_ft[1] + ny * (off - side * 0.22)))
        s1_in = xy_m((p_bot_ft[0] + nx * (off - side * 0.22), p_bot_ft[1] + ny * (off - side * 0.22)))

        # Sloped solid low parapet/stringer + brass rail
        h_rail = 0.88
        for quad_a, quad_b, z_lo_a, z_hi_a, z_lo_b, z_hi_b, mat in [
            (s0, s1, z_top_m - 0.28, z_top_m + 0.55, z_bot_m - 0.28, z_bot_m + 0.55, MATERIALS["white_plaster"]),
            (s0, s1, z_top_m + h_rail - 0.06, z_top_m + h_rail, z_bot_m + h_rail - 0.06, z_bot_m + h_rail, MATERIALS["brass"]),
        ]:
            # Outer & inner faces + top strip
            p_a0 = (quad_a[0], quad_a[1], z_lo_a)
            p_a1 = (quad_a[0], quad_a[1], z_hi_a)
            p_b0 = (quad_b[0], quad_b[1], z_lo_b)
            p_b1 = (quad_b[0], quad_b[1], z_hi_b)
            q_a0 = (s0_in[0], s0_in[1], z_lo_a)
            q_a1 = (s0_in[0], s0_in[1], z_hi_a)
            q_b0 = (s1_in[0], s1_in[1], z_lo_b)
            q_b1 = (s1_in[0], s1_in[1], z_hi_b)
            if side > 0:
                add_quad(mesh, p_a0, p_b0, p_b1, p_a1, mat)
                add_quad(mesh, q_b0, q_a0, q_a1, q_b1, mat)
                add_quad(mesh, p_a1, p_b1, q_b1, q_a1, mat)
                add_quad(mesh, q_a0, q_b0, p_b0, p_a0, mat)
                add_quad(mesh, q_a0, p_a0, p_a1, q_a1, mat)
                add_quad(mesh, p_b0, q_b0, q_b1, p_b1, mat)
            else:
                add_quad(mesh, p_b0, p_a0, p_a1, p_b1, mat)
                add_quad(mesh, q_a0, q_b0, q_b1, q_a1, mat)
                add_quad(mesh, q_a1, q_b1, p_b1, p_a1, mat)
                add_quad(mesh, p_a0, p_b0, q_b0, q_a0, mat)
                add_quad(mesh, p_a0, q_a0, q_a1, p_a1, mat)
                add_quad(mesh, q_b0, p_b0, p_b1, q_b1, mat)
