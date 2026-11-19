#!/usr/bin/env python3
"""Capture the QHD (2560x1440) studio renders from ``docs/library-3d.html``.

Standalone, retrying counterpart to ``capture_web_renders()`` in
``ingetrazo_3d/build_ingetrazo_library.py``. Each shot is captured in its own
headless Chromium; a capture only counts if the local server finished serving
the scene JSON during that run (a "Failed to fetch" frame shows only sky and
ground). Failed captures are retried with a longer virtual-time budget.

Usage::

    uv run --offline --no-project --with pillow python3 scripts/capture_studio_renders.py
    uv run --offline --no-project --with pillow python3 scripts/capture_studio_renders.py --only 02 05 09
"""

from __future__ import annotations

import argparse
import functools
import http.server
import shutil
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
DOCS_RENDERS = DOCS_DIR / "renders"
BUILD_RENDERS = REPO_ROOT / "ingetrazo_3d" / "renders"
SCENE_JSON = "/overlays/library_3d_scene.json"

W, H = 2560, 1440

SHOTS = [
    ("hillside_hero", "studio_01_hillside_hero.png"),
    ("south_entry", "studio_02_south_entry_canopy.png"),
    ("cutaway_axon", "studio_03_roof_cutaway_axon.png"),
    ("mezzanine_pov", "studio_04_mezzanine_counter_pov.png"),
    ("sunken_well", "studio_05_sunken_well_scoop.png"),
    ("lounge_mthood", "studio_06_east_mthood_lounge.png"),
    ("h_columns_north", "studio_07_north_h_columns.png"),
    ("section_aa", "studio_08_section_aa_ortho.png"),
    ("section_well", "studio_09_section_well_persp.png"),
    ("section_bb", "studio_10_section_bb_ortho.png"),
    ("section_plan_l3", "studio_11_section_plan_l3.png"),
    ("sun_summer_noon", "studio_12_sun_summer_noon_section.png"),
    ("sun_morning_louvers", "studio_13_sun_morning_mthood_louvers.png"),
    ("sun_summer_west", "studio_14_sun_summer_west_hcolumns.png"),
    ("sun_winter_heliodon", "studio_15_sun_winter_heliodon.png"),
    ("alcove_mthood", "studio_16_entry_mthood_alcove.png"),
    ("blockout_match", "studio_17_blockout_match_axon.png"),
    ("campus_aerial", "studio_18_campus_aerial.png"),
    ("control_glass_wall", "studio_19_control_glass_wall.png"),
    ("auditorium_cutaway", "studio_20_auditorium_cutaway.png"),
]


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="*", default=None, help="Shot numbers (e.g. 02 05) or camera keys")
    parser.add_argument("--budget", type=int, default=15000, help="Initial --virtual-time-budget (ms)")
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    from PIL import Image

    browser_bin = find_browser_bin()
    if not browser_bin:
        print("No headless Chromium binary found.", file=sys.stderr)
        return 1

    selected = SHOTS
    if args.only:
        wanted = set(args.only)
        selected = [(k, f) for k, f in SHOTS if k in wanted or f.split("_")[1] in wanted]

    DOCS_RENDERS.mkdir(parents=True, exist_ok=True)
    BUILD_RENDERS.mkdir(parents=True, exist_ok=True)

    served: list[str] = []

    class TrackingHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            pass

        def do_GET(self) -> None:
            super().do_GET()
            # Only reached if the full body was written without a broken pipe.
            served.append(self.path.split("?", 1)[0])

    class QuietTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

        def handle_error(self, request, client_address) -> None:
            pass

    handler = functools.partial(TrackingHandler, directory=str(DOCS_DIR))
    failures = []
    with QuietTCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        threading.Thread(target=httpd.serve_forever, daemon=True).start()

        for cam_key, fname in selected:
            out_file = BUILD_RENDERS / fname
            url = f"http://127.0.0.1:{port}/library-3d.html?cam={cam_key}&studio=1"
            ok = False
            for attempt in range(1, args.retries + 1):
                served.clear()
                budget = args.budget * attempt
                cmd = [
                    browser_bin,
                    "--headless=new",
                    "--hide-scrollbars",
                    "--no-sandbox",
                    "--enable-webgl",
                    "--ignore-gpu-blocklist",
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                    f"--window-size={W},{H + 80}",
                    f"--virtual-time-budget={budget}",
                    f"--screenshot={out_file}",
                    url,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                if out_file.is_file() and SCENE_JSON in served:
                    ok = True
                    break
                print(f"  retry {fname} (attempt {attempt} failed, budget {budget} ms)")
            if not ok:
                failures.append(fname)
                print(f"FAILED  {fname}")
                continue
            with Image.open(out_file) as im:
                if im.size != (W, H):
                    im.crop((0, 0, W, H)).save(out_file)
            shutil.copy2(out_file, DOCS_RENDERS / fname)
            print(f"OK      {fname}")

        httpd.shutdown()

    if failures:
        print(f"{len(failures)} failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
