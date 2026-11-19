"""Deterministic 30fps Camera Collision & Sightline Validator for Mount Angel Studio.

Simulates the exact Fritsch-Carlson monotonic cubic Hermite (PCHIP) spline from
`videos/library_choreography.js` across every frame `0..N-1` of a `motion.json` file
and checks `viewEye` against:
  1. Surrounding Abbey Campus buildings & roofs (from `site_terrain.py`),
  2. Natural hillside grade (`natural_hillside_z_m`), and
  3. Library exterior roof/wall solids (when `mode == "exterior"`).

Usage:
  uv run --offline --no-project python3 videos/check_clearance.py videos/seg01_hilltop/motion.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

FT_TO_M = 0.3048
M_TO_FT = 1.0 / FT_TO_M

# Exact surrounding campus building envelopes from `ingetrazo_3d/components/site_terrain.py`
# Tuple: (name, x_min_ft, x_max_ft, y_min_ft, y_max_ft, z_top_m)
CAMPUS_BUILDINGS = [
    ("Aquinas Hall Main", -244.0, -146.0, -82.0, -40.0, 14.55),
    ("Aquinas Hall North Wing", -244.0, -206.0, -42.0, 16.0, 14.55),
    ("Aquinas Hall South Entry", -206.5, -173.5, -95.5, -78.5, 14.05),
    ("Aquinas East Porch", -149.0, -135.0, -71.0, -51.0, 5.85),
    ("Downhill NW Annex", -197.0, -133.0, 38.0, 77.0, 2.75),
    ("Bluff-Side East Monastery Wing", 123.5, 211.5, -59.5, -16.5, 14.05),
    ("Abbey Church Portico & Nave", 235.0, 357.0, -185.5, -58.5, 18.25),
    ("Abbey Bell Tower", 258.0, 280.0, -164.0, -142.0, 38.60),
    ("East 3-Story Monastery", 314.0, 382.0, -256.0, 12.0, 15.05),
    ("SW Romanesque Academic Hall", -237.0, -133.0, -187.0, -123.0, 12.50),
    ("Modern Seminary North Pavilion", -65.5, 15.5, -235.5, -189.5, 8.40),
    ("Modern Seminary South Pavilion", -50.5, 25.5, -290.5, -244.5, 8.40),
]


def natural_hillside_z_m(x_ft: float, y_ft: float) -> float:
    """Match `natural_hillside_z_m` from `site_terrain.py`."""
    if y_ft <= 2.0:
        base = 0.55 - max(0.0, (-y_ft - 80.0)) * 0.004
    else:
        u = min(1.0, (y_ft - 2.0) / 118.0)
        drop = 14.8 * (u**1.35)
        base = 0.55 - drop
    east_roll = -max(0.0, x_ft - 95.0) * 0.018
    return base + east_roll


def prepare_keyframes(raw_kfs: list[dict]) -> list[dict]:
    kfs = sorted((dict(k) for k in raw_kfs), key=lambda k: k["t"])
    for i in range(1, len(kfs)):
        if "yaw" in kfs[i] and "yaw" in kfs[i - 1]:
            dy = kfs[i]["yaw"] - kfs[i - 1]["yaw"]
            while dy > math.pi:
                kfs[i]["yaw"] -= 2.0 * math.pi
                dy -= 2.0 * math.pi
            while dy < -math.pi:
                kfs[i]["yaw"] += 2.0 * math.pi
                dy += 2.0 * math.pi
    return kfs


def eval_pchip(ts: list[float], ys: list[float], t: float) -> float:
    n = len(ts)
    if n == 0:
        return 0.0
    if n == 1 or t <= ts[0]:
        return ys[0]
    if t >= ts[-1]:
        return ys[-1]

    h = [max(1e-6, ts[i + 1] - ts[i]) for i in range(n - 1)]
    delta = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    if n == 2:
        m[0] = m[1] = delta[0]
    else:
        for i in range(1, n - 1):
            if delta[i - 1] * delta[i] > 0.0:
                w1 = 2.0 * h[i] + h[i - 1]
                w2 = h[i] + 2.0 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / delta[i - 1] + w2 / delta[i])
        m0 = ((2.0 * h[0] + h[1]) * delta[0] - h[0] * delta[1]) / (h[0] + h[1])
        if m0 * delta[0] <= 0.0:
            m0 = 0.0
        elif delta[0] * delta[1] < 0.0 and abs(m0) > abs(3.0 * delta[0]):
            m0 = 3.0 * delta[0]
        m[0] = m0

        mn = ((2.0 * h[n - 2] + h[n - 3]) * delta[n - 2] - h[n - 2] * delta[n - 3]) / (h[n - 2] + h[n - 3])
        if mn * delta[n - 2] <= 0.0:
            mn = 0.0
        elif delta[n - 2] * delta[n - 3] < 0.0 and abs(mn) > abs(3.0 * delta[n - 2]):
            mn = 3.0 * delta[n - 2]
        m[n - 1] = mn

    seg = 0
    for i in range(n - 1):
        if ts[i] <= t <= ts[i + 1]:
            seg = i
            break
    dt = h[seg]
    s = (t - ts[seg]) / dt
    h00 = 2 * s**3 - 3 * s**2 + 1
    h10 = s**3 - 2 * s**2 + s
    h01 = -2 * s**3 + 3 * s**2
    h11 = s**3 - s**2
    return h00 * ys[seg] + h10 * dt * m[seg] + h01 * ys[seg + 1] + h11 * dt * m[seg + 1]


def sample_prop(kfs: list[dict], prop: str, default: float, t: float) -> float:
    sub = [k for k in kfs if isinstance(k.get(prop), (int, float))]
    if not sub:
        return default
    return eval_pchip([float(k["t"]) for k in sub], [float(k[prop]) for k in sub], t)


def audit_motion_file(motion_path: Path, interior: bool = False) -> int:
    spec = json.loads(motion_path.read_text(encoding="utf-8"))
    dur = float(spec.get("duration_sec", 28.0))
    fps = int(spec.get("fps", 30))
    kfs = prepare_keyframes(spec.get("keyframes", []))
    total_frames = round(dur * fps)

    pad_xy_ft = 6.0  # 1.8 m horizontal safety margin around neighboring buildings
    pad_z_m = 1.6    # 1.6 m vertical roof clearance safety margin
    violations: list[str] = []

    for idx in range(total_frames):
        t = idx / float(fps)
        tx = sample_prop(kfs, "tx", 0.0, t)
        ty = sample_prop(kfs, "ty", 0.0, t)
        tz = sample_prop(kfs, "tz", 0.0, t)
        yaw = sample_prop(kfs, "yaw", 0.0, t)
        pitch = sample_prop(kfs, "pitch", 0.2, t)
        dist = sample_prop(kfs, "dist", 50.0, t)

        cp, sp = math.cos(pitch), math.sin(pitch)
        ex = tx + dist * cp * math.cos(yaw)
        ey = ty + dist * cp * math.sin(yaw)
        ez = tz + dist * sp

        x_ft = ex * M_TO_FT
        y_ft = ey * M_TO_FT

        # 1. Check surrounding campus buildings
        for bname, x0, x1, y0, y1, ztop in CAMPUS_BUILDINGS:
            if (
                (x0 - pad_xy_ft) <= x_ft <= (x1 + pad_xy_ft)
                and (y0 - pad_xy_ft) <= y_ft <= (y1 + pad_xy_ft)
                and ez < ztop + pad_z_m
            ):
                violations.append(
                    f"Frame {idx:04d} (t={t:5.2f}s): Eye ({ex:.1f}m, {ey:.1f}m, {ez:.2f}m) "
                    f"[{x_ft:.0f}ft, {y_ft:.0f}ft] collides/clips '{bname}' (roof {ztop:.2f}m)"
                )

        if not interior:
            # 2. Check natural terrain clearance
            gz = natural_hillside_z_m(x_ft, y_ft)
            if ez < gz + 1.1:
                violations.append(
                    f"Frame {idx:04d} (t={t:5.2f}s): Eye Z={ez:.2f}m too close to terrain ({gz:.2f}m) at ({ex:.1f}m, {ey:.1f}m)"
                )
            # 3. Check Library exterior envelope clearance (rough outer footprint + roof)
            if (
                -128.0 <= x_ft <= 98.0
                and -66.0 <= y_ft <= 90.0
                and ez < 6.80
                and not (-38.0 <= x_ft <= 18.0 and y_ft <= -51.5 and 1.2 <= ez <= 2.95)
            ):
                violations.append(
                    f"Frame {idx:04d} (t={t:5.2f}s): Exterior Eye ({ex:.1f}m, {ey:.1f}m, {ez:.2f}m) "
                    f"dips into Library massing [{x_ft:.0f}ft, {y_ft:.0f}ft]"
                )

    if violations:
        print(f"FAIL: {len(violations)} collision/clearance frames in {motion_path}:")
        for v in violations[:12]:
            print("  -", v)
        if len(violations) > 12:
            print(f"  ... and {len(violations) - 12} more frames.")
        return 1

    print(f"OK: {motion_path.name} verified 0 collisions across all {total_frames} frames ({dur:.1f}s @ {fps}fps).")
    return 0


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: check_clearance.py [--interior] <motion.json>")
        sys.exit(2)
    interior = "--interior" in sys.argv
    paths = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    rc = 0
    for p in paths:
        rc |= audit_motion_file(p, interior=interior)
    sys.exit(rc)


if __name__ == "__main__":
    main()
