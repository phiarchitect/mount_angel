#!/usr/bin/env python3
"""Capture the furniture close-up renders used on ``docs/furniture.html``.

Each close-up has a recorded camera so it can be re-shot whenever the model
changes. Only shots listed in ``FURNITURE_SHOTS`` can be regenerated; the other
``docs/furniture/render_0*.jpg`` images predate recorded cameras.

Usage::

    uv run --offline --no-project --with pillow python3 scripts/capture_furniture_renders.py
    uv run --offline --no-project --with pillow python3 scripts/capture_furniture_renders.py --only 03
"""

from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_studio_renders import SCENE_JSON, find_browser_bin

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

# Camera convention (library-3d.html): eye = target + dist·(cos p·cos y, cos p·sin y, sin p),
# metres, +X East, +Y North, Level 3 floor = 0.
FURNITURE_SHOTS = [
    {
        "id": "02",
        "out": "furniture/render_02_workbench_chair69.jpg",
        "desc": "Mezzanine cantilevered matte-black linoleum workbench, white steel T-brackets, and Artek Chair 69s (-5'-4\")",
        "tx": -0.45, "ty": 10.25, "tz": -1.08,
        "yaw": -0.55, "pitch": 0.36, "dist": 3.35, "fov": 56,
        "doy": 172, "hour": 8.5,
        "width": 1120, "height": 700,
    },
    {
        "id": "03",
        "out": "furniture/render_03_stool60.jpg",
        "desc": "Three-legged Artek Stool 60s along the Level 3 curved workbench",
        "tx": -2.85, "ty": 14.68, "tz": 0.10,
        "yaw": 0.60, "pitch": 0.52, "dist": 3.3, "fov": 58,
        "doy": 172, "hour": 10,
        "width": 1120, "height": 700,
    },
    {
        "id": "04",
        "out": "furniture/render_04_bookcase.jpg",
        "desc": "6-shelf radial birch bookcases with 5-batten vertical directory screens and recessed kick plinth",
        "tx": -0.35, "ty": 17.80, "tz": 1.08,
        "yaw": -1.22, "pitch": 0.08, "dist": 3.25, "fov": 56,
        "doy": 172, "hour": 9.5,
        "width": 1120, "height": 700,
    },
    {
        "id": "05",
        "out": "furniture/render_05_stair_bookcase.jpg",
        "desc": "East 3-shelf counter-height stairwell dictionary bookcase and linear parapet mushroom lamps",
        "tx": 7.55, "ty": 6.95, "tz": 0.65,
        "yaw": -0.58, "pitch": 0.14, "dist": 1.95, "fov": 60,
        "doy": 172, "hour": 9.5,
        "width": 1120, "height": 700,
    },
    {
        "id": "06",
        "out": "furniture/render_06_control_desk.jpg",
        "desc": "Control Peninsula, curved birch desk, 3-rail bronze guardrail, slatted drum, and 3-shelf Mezzanine Reference Bookwall",
        "tx": 0.35, "ty": 6.20, "tz": 0.25,
        "yaw": 1.68, "pitch": 0.12, "dist": 8.4, "fov": 58,
        "doy": 172, "hour": 9.5,
        "width": 1120, "height": 700,
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="*", default=None, help="Shot ids, e.g. 03")
    parser.add_argument("--budget", type=int, default=15000)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    from PIL import Image

    browser_bin = find_browser_bin()
    if not browser_bin:
        print("No headless Chromium binary found.", file=sys.stderr)
        return 1

    shots = [s for s in FURNITURE_SHOTS if not args.only or s["id"] in args.only]
    served: list[str] = []

    class TrackingHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            pass

        def do_GET(self) -> None:
            super().do_GET()
            served.append(self.path.split("?", 1)[0])

    class QuietTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

        def handle_error(self, request, client_address) -> None:
            pass

    failures = []
    handler = functools.partial(TrackingHandler, directory=str(DOCS_DIR))
    with QuietTCPServer(("127.0.0.1", 0), handler) as httpd, tempfile.TemporaryDirectory() as tmp:
        port = httpd.server_address[1]
        threading.Thread(target=httpd.serve_forever, daemon=True).start()

        for s in shots:
            w, h = s["width"], s["height"]
            query = "&".join(
                f"{k}={s[k]}" for k in ("tx", "ty", "tz", "yaw", "pitch", "dist", "fov", "doy", "hour")
            )
            url = (
                f"http://127.0.0.1:{port}/library-3d.html?{query}"
                f"&studio=1&hud=0&hide=0_Regulating_Grid&w={w}&h={h}"
            )
            png = Path(tmp) / f"{s['id']}.png"
            ok = False
            for attempt in range(1, args.retries + 1):
                served.clear()
                cmd = [
                    browser_bin, "--headless=new", "--hide-scrollbars", "--no-sandbox", "--enable-webgl",
                    "--ignore-gpu-blocklist", "--use-gl=angle", "--use-angle=swiftshader",
                    f"--window-size={w},{h + 100}", f"--virtual-time-budget={args.budget * attempt}",
                    f"--screenshot={png}", url,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                if png.is_file() and SCENE_JSON in served:
                    ok = True
                    break
                print(f"  retry {s['id']} (attempt {attempt} failed)")
            if not ok:
                failures.append(s["id"])
                print(f"FAILED  {s['out']}")
                continue
            out = DOCS_DIR / s["out"]
            with Image.open(png) as im:
                im.convert("RGB").crop((0, 0, w, h)).save(out, quality=90)
            print(f"OK      {s['out']}  ({s['desc']})")

        httpd.shutdown()

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
