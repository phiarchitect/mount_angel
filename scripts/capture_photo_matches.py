#!/usr/bin/env python3
"""
Capture calibrated photo-comparison renders (`docs/renders/photo_match_01..08.png`, no 04)
from `docs/library-3d.html` at exact archival photograph aspect ratios, with optional
50/50 onion-skin + wipe diagnostic overlays.

Usage:
  uv run --offline --no-project --with pillow python3 scripts/capture_photo_matches.py
  uv run --offline --no-project --with pillow python3 scripts/capture_photo_matches.py --shot 1 --overlay-dir /tmp/overlays
"""

from __future__ import annotations

import argparse
import functools
import http.server
import math
import shutil
import socketserver
import subprocess
import threading
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
RENDERS_DIR = DOCS_DIR / "renders"

PHOTO_MATCH_SHOTS = [
    {
        "shot": 1,
        "name": "Campus Quad Approach & Cantilevered Bluff Aerial",
        "photo": "photos/campus_quad_aerial.jpg",
        "render": "renders/photo_match_01.png",
        "width": 2048,
        "height": 1330,
        "tx": 14.0,
        "ty": -45.3,
        "tz": 2.0,
        "yaw": 3.1225,
        "pitch": 0.236,
        "dist": 436.0,
        "fov": 15.8,
        "shiftx": 0.0,
        "shifty": 0.0,
        "doy": 264,
        "hour": 15.25,
        "hide": "0_Regulating_Grid",
    },
    {
        "shot": 2,
        "name": "Three-Tier Roof Hierarchy & Conical Lanterns Aerial",
        "photo": "photos/roof_tiers_aerial.jpg",
        "render": "renders/photo_match_02.png",
        "width": 2048,
        "height": 1416,
        "tx": 0.25,
        "ty": 0.95,
        "tz": 4.50,
        "yaw": -1.115,
        "pitch": 1.525,
        "dist": 244.0,
        "fov": 13.8,
        "shiftx": 0.0,
        "shifty": 0.0,
        "doy": 172,
        "hour": 10.75,
        "hide": "0_Regulating_Grid",
    },
    {
        "shot": 3,
        "name": "Level 3 Control Peninsula, Slatted Drum & Glazed Offices",
        "photo": "photos/control_glass_wide.jpg",
        "render": "renders/photo_match_03.png",
        "width": 2400,
        "height": 1200,
        "tx": 7.43,
        "ty": 3.67,
        "tz": 2.77,
        "yaw": 2.660,
        "pitch": -0.285,
        "dist": 8.5,
        "fov": 53.0,
        "shiftx": 0.0,
        "shifty": 0.0,
        "doy": 172,
        "hour": 9.5,
        "hide": "0_Regulating_Grid",
    },
    {
        "shot": 5,
        "name": "Level 3 Reading Workbench Vista Along Mezzanine Rim",
        "photo": "drawings/mezzaninewithdictionaryweb2-crop-1550026550-1867x934.jpg",
        "render": "renders/photo_match_05.png",
        "width": 2400,
        "height": 1200,
        "tx": 3.5,
        "ty": 11.2,
        "tz": 0.35,
        "yaw": 3.02,
        "pitch": 0.08,
        "dist": 11.8,
        "fov": 58.0,
        "shiftx": 0.0,
        "shifty": 0.0,
        "doy": 172,
        "hour": 9.0,
        "hide": "0_Regulating_Grid",
    },
    {
        "shot": 6,
        "name": "Mezzanine Upward View to Control Peninsula Rail, Scoop & Drum",
        "photo": "photos/MA-121713-578-web-1400x700.jpg",
        "render": "renders/photo_match_06.png",
        "width": 2400,
        "height": 1200,
        "tx": 1.73,
        "ty": 6.98,
        "tz": 3.69,
        "yaw": 2.88,
        "pitch": -0.61,
        "dist": 6.0,
        "fov": 60.0,
        "shiftx": 0.0,
        "shifty": 0.0,
        "doy": 172,
        "hour": 10.5,
        "hide": "0_Regulating_Grid",
    },
    {
        "shot": 7,
        "name": "Central Well West Stair Looking Up to Oculus & Bookwall",
        "photo": "drawings/mezzaninestairsweb-crop-1550397981-1401x701.jpg",
        "render": "renders/photo_match_07.png",
        "width": 2400,
        "height": 1200,
        "tx": -5.32,
        "ty": 4.58,
        "tz": 1.84,
        "yaw": 2.720,
        "pitch": -0.520,
        "dist": 8.0,
        "fov": 58.0,
        "shiftx": 0.0,
        "shifty": 0.0,
        "doy": 172,
        "hour": 10.0,
        "hide": "0_Regulating_Grid",
    },
    {
        "shot": 8,
        "name": "Curved North Daylight Scoop Concave Reflector Vault",
        "photo": "drawings/MA-121713-565web-1400x700.jpg",
        "render": "renders/photo_match_08.png",
        "width": 2400,
        "height": 1200,
        "tx": -0.08,
        "ty": 8.0,
        "tz": 5.6,
        "yaw": -0.460,
        "pitch": -0.680,
        "dist": 7.20,
        "fov": 68.0,
        "shiftx": 0.0,
        "shifty": 0.0,
        "doy": 172,
        "hour": 11.5,
        "hide": "0_Regulating_Grid",
    },
]


def fmt_ft_in(metres: float) -> str:
    sign = "+" if metres >= 0 else "-"
    total_in = round(abs(metres) / 0.0254)
    ft, inch = divmod(total_in, 12)
    return f"{sign}{ft}'-{inch}\""


def compute_eye(s: dict) -> tuple[float, float, float]:
    cp, sp = math.cos(s["pitch"]), math.sin(s["pitch"])
    ex = s["tx"] + s["dist"] * cp * math.cos(s["yaw"])
    ey = s["ty"] + s["dist"] * cp * math.sin(s["yaw"])
    ez = s["tz"] + s["dist"] * sp
    return ex, ey, ez


def build_webgl_href(s: dict, include_wh: bool = False) -> str:
    q: dict[str, str | int | float] = {
        "tx": s["tx"],
        "ty": s["ty"],
        "tz": s["tz"],
        "yaw": s["yaw"],
        "pitch": s["pitch"],
        "dist": s["dist"],
        "fov": s["fov"],
    }
    if abs(s.get("shiftx", 0.0)) > 1e-6:
        q["shiftx"] = s["shiftx"]
    if abs(s.get("shifty", 0.0)) > 1e-6:
        q["shifty"] = s["shifty"]
    q["doy"] = s["doy"]
    q["hour"] = s["hour"]
    q["studio"] = 1
    if include_wh:
        q["hud"] = 0
        q["w"] = s["width"]
        q["h"] = s["height"]
    if s.get("hide"):
        q["hide"] = s["hide"]
    return "library-3d.html?" + urllib.parse.urlencode(q)


def find_browser_bin() -> str | None:
    browser_bin = (
        shutil.which("google-chrome")
        or shutil.which("google-chrome-stable")
        or shutil.which("chromium")
        or shutil.which("chromium-browser")
    )
    if not browser_bin:
        pw_root = Path.home() / ".cache" / "ms-playwright"
        if pw_root.is_dir():
            for candidate in sorted(pw_root.glob("chromium-*/chrome-linux*/chrome"), reverse=True):
                return str(candidate)
    return browser_bin


def capture_shots(selected_shots: list[int] | None = None, overlay_dir: Path | None = None):
    from PIL import Image

    browser_bin = find_browser_bin()
    if not browser_bin:
        raise RuntimeError("No headless Chromium binary found.")

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    if overlay_dir is not None:
        overlay_dir.mkdir(parents=True, exist_ok=True)

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            pass

    handler = functools.partial(QuietHandler, directory=str(DOCS_DIR))

    class QuietTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with QuietTCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        threading.Thread(target=httpd.serve_forever, daemon=True).start()

        for s in PHOTO_MATCH_SHOTS:
            if selected_shots and s["shot"] not in selected_shots:
                continue

            w, h = s["width"], s["height"]
            out_file = DOCS_DIR / s["render"]
            rel_url = build_webgl_href(s, include_wh=True)
            url = f"http://127.0.0.1:{port}/{rel_url}"

            cmd = [
                browser_bin,
                "--headless=new",
                "--hide-scrollbars",
                "--no-sandbox",
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--use-gl=angle",
                "--use-angle=swiftshader",
                f"--window-size={w},{h + 160}",
                "--virtual-time-budget=5500",
                f"--screenshot={out_file}",
                url,
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            with Image.open(out_file) as im:
                if im.size != (w, h):
                    im.crop((0, 0, w, h)).save(out_file)

            ex, ey, ez = compute_eye(s)
            print(
                f"[Shot {s['shot']:02d}] {out_file.relative_to(REPO_ROOT)} ({w}x{h}) | "
                f"Eye=({ex:+.1f}, {ey:+.1f}, {ez:+.1f} m) [{fmt_ft_in(ex)}, {fmt_ft_in(ey)}, {fmt_ft_in(ez)}] | "
                f"FOV={s['fov']}° dist={s['dist']}m"
            )
            print(f"          WebGL: {build_webgl_href(s, include_wh=False)}")

            if overlay_dir is not None:
                photo_path = DOCS_DIR / s["photo"]
                if photo_path.is_file():
                    p_im = Image.open(photo_path).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
                    r_im = Image.open(out_file).convert("RGBA")
                    blend = Image.blend(p_im, r_im, 0.50)
                    blend_path = overlay_dir / f"shot_{s['shot']:02d}_onion.png"
                    blend.save(blend_path)
                    print(f"          Onion: {blend_path}")

        httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Capture calibrated photo-match renders")
    parser.add_argument("--shot", type=int, action="append", help="Capture specific shot number(s) 1..8")
    parser.add_argument("--overlay-dir", type=Path, help="Optional directory to write 50/50 onion-skin overlays")
    args = parser.parse_args()
    capture_shots(args.shot, args.overlay_dir)


if __name__ == "__main__":
    main()
