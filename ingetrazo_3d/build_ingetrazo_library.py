"""
Alvar Aalto's Mount Angel Abbey Library — IngeTrazo 0.6.0 Master 3D Builder
===========================================================================
Assembles all 8 modular architectural layers from `ingetrazo_3d.components`
(driven by canonical constructive geometry in `phiarchitect.mountangel.vectors`)
into:
  1. `ingetrazo_3d/mount_angel_library.igz` (native IngeTrazo 0.6.0 project)
  2. `ingetrazo_3d/mount_angel_library.obj` + `.mtl` (Wavefront OBJ + materials)
  3. `docs/overlays/library_3d_scene.json` (1:1 per-layer WebGL2 mesh + edge bundle)
  4. Optional `--live` push over IngeTrazo's AI TCP Bridge (`127.0.0.1:4763`)
  5. Automated 2560x1440 QHD architectural studio renders (`ingetrazo_3d/renders/`)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

INGETRAZO_ROOT = Path("/home/phi/PROJECTS/phi-WORKS/ingetrazo")
if str(INGETRAZO_ROOT) not in sys.path:
    sys.path.insert(0, str(INGETRAZO_ROOT))
if str(INGETRAZO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(INGETRAZO_ROOT / "scripts"))

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from ingetrazo_3d.components import (
    build_envelope_and_south_wing,
    build_level3_reading_room,
    build_lower_levels,
    build_regulating_lines,
    build_roof_and_skylights,
    build_site_terrain,
)


def build_mount_angel_scene(scene):
    """Populate `scene` with all 8 architectural layers of Mount Angel Abbey Library."""
    scene.clear()
    build_regulating_lines(scene)
    build_site_terrain(scene)
    build_lower_levels(scene)
    build_level3_reading_room(scene)
    build_envelope_and_south_wing(scene)
    build_roof_and_skylights(scene)
    scene.version += 1


def export_web_scene_json(scene, out_path: Path):
    """
    Export exact IngeTrazo `scene.groups` to a compact WebGL2 JSON bundle with:
      - Opaque & translucent triangle buffers (positions, normals, colors, alpha, emissive)
      - Clean polygon-perimeter architectural ink edges (automatically stripping internal diagonals!)
    """
    from formats.meshexport import export_triangles

    out_path.parent.mkdir(parents=True, exist_ok=True)
    layers_out = []

    def r3(v: float) -> float:
        return round(float(v), 3)

    for grp in scene.groups:
        struct_pos: list[float] = []
        struct_nrm: list[float] = []
        struct_col: list[float] = []

        furn_pos: list[float] = []
        furn_nrm: list[float] = []
        furn_col: list[float] = []

        trans_pos: list[float] = []
        trans_nrm: list[float] = []
        trans_col: list[float] = []

        edge_pos: list[float] = []
        edge_adj: dict[tuple[tuple[float, float, float], tuple[float, float, float]], list[tuple[float, float, float, tuple[float, float, float], bool, bool]]] = {}

        is_terrain = grp.name.startswith("1_")
        is_reg = grp.name.startswith("0_")

        # Pre-pass: accumulate smooth vertex normals across smooth-tagged faces sharing position & material
        import math as _math
        smooth_acc: dict[tuple[tuple[float, float, float], tuple[float, float, float]], list[float]] = {}
        face_records = []
        for face in grp.mesh.faces:
            attrs = face.attrs or {}
            col = attrs.get("color", (0.94, 0.93, 0.90))
            col_key = (round(col[0], 3), round(col[1], 3), round(col[2], 3))
            opacity = float(attrs.get("opacity", 1.0))
            emissive = 1.0 if attrs.get("emissive", False) else 0.0
            is_furn = bool(attrs.get("furniture", False))
            is_smooth = bool(attrs.get("smooth", False))
            n = face.normal()
            fnx, fny, fnz = float(n.x()), float(n.y()), float(n.z())

            tris = list(export_triangles(face))
            if not tris:
                continue

            tri_pts = []
            for a, b, c in tris:
                pa = (r3(a.x()), r3(a.y()), r3(a.z()))
                pb = (r3(b.x()), r3(b.y()), r3(b.z()))
                pc = (r3(c.x()), r3(c.y()), r3(c.z()))
                tri_pts.append((pa, pb, pc))
                if is_smooth:
                    for pv in (pa, pb, pc):
                        acc = smooth_acc.setdefault((pv, col_key), [0.0, 0.0, 0.0])
                        acc[0] += fnx
                        acc[1] += fny
                        acc[2] += fnz

            face_records.append((col_key, opacity, emissive, is_furn, is_smooth, r3(fnx), r3(fny), r3(fnz), fnx, fny, fnz, tri_pts))

        for col_key, opacity, emissive, is_furn, is_smooth, nx, ny, nz, fnx, fny, fnz, tri_pts in face_records:
            is_trans = opacity < 0.98
            if is_trans:
                t_pos, t_nrm, t_col = trans_pos, trans_nrm, trans_col
            elif is_furn:
                t_pos, t_nrm, t_col = furn_pos, furn_nrm, furn_col
            else:
                t_pos, t_nrm, t_col = struct_pos, struct_nrm, struct_col

            face_edges: Counter = Counter()
            rgba = (*col_key, round(opacity if is_trans else (2.0 if emissive else 1.0), 3))
            for pa, pb, pc in tri_pts:
                t_pos.extend((*pa, *pb, *pc))
                if is_smooth:
                    for pv in (pa, pb, pc):
                        sx, sy, sz = smooth_acc.get((pv, col_key), (fnx, fny, fnz))
                        sl = _math.sqrt(sx * sx + sy * sy + sz * sz)
                        if sl > 1e-6 and (sx * fnx + sy * fny + sz * fnz) > 0.35 * sl:
                            t_nrm.extend((r3(sx / sl), r3(sy / sl), r3(sz / sl)))
                        else:
                            t_nrm.extend((nx, ny, nz))
                else:
                    t_nrm.extend((nx, ny, nz, nx, ny, nz, nx, ny, nz))
                t_col.extend((*rgba, *rgba, *rgba))

                if not is_terrain and not is_reg:
                    for u, v in ((pa, pb), (pb, pc), (pc, pa)):
                        ek = (u, v) if u <= v else (v, u)
                        face_edges[ek] += 1

            # Collect per-face outer boundary edges for layer-wide coplanar / smooth-surface crease filtering
            for ek, cnt in face_edges.items():
                if cnt == 1:
                    edge_adj.setdefault(ek, []).append((nx, ny, nz, col_key, is_trans, is_smooth))

        for ek, infos in edge_adj.items():
            if len(infos) == 2:
                n0x, n0y, n0z, c0, tr0, sm0 = infos[0]
                n1x, n1y, n1z, c1, tr1, sm1 = infos[1]
                dot_n = n0x * n1x + n0y * n1y + n0z * n1z
                thresh = 0.55 if (sm0 and sm1) else 0.985
                if c0 == c1 and tr0 == tr1 and dot_n > thresh:
                    continue
            edge_pos.extend((*ek[0], *ek[1]))

        poche_verts = len(struct_pos) // 3
        opaque_pos = struct_pos + furn_pos
        opaque_nrm = struct_nrm + furn_nrm
        opaque_col = struct_col + furn_col

        layers_out.append(
            {
                "name": grp.name,
                "poche_verts": poche_verts,
                "opaque_pos": opaque_pos,
                "opaque_nrm": opaque_nrm,
                "opaque_col": opaque_col,
                "trans_pos": trans_pos,
                "trans_nrm": trans_nrm,
                "trans_col": trans_col,
                "edge_pos": edge_pos,
            }
        )

    payload = {
        "title": "Mount Angel Abbey Library — Alvar Aalto (1970)",
        "units": "metres",
        "origin": "Working Point #4 on Level 3 Finished Floor",
        "layers": layers_out,
    }
    out_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Saved WebGL2 3D scene bundle: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


LIVE_BRIDGE_CODE = r"""
import math
import sys
from pathlib import Path
from PySide6.QtGui import QVector3D

repo_root = Path("/home/phi/PROJECTS/phiarchitect/mountangel")
for p in (str(repo_root), str(repo_root / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

import importlib
import phiarchitect.mountangel.vectors as _vec
import ingetrazo_3d.components.primitives as _pr
import ingetrazo_3d.components.aalto_bookcases as _ab
import ingetrazo_3d.components.south_wing_interiors as _swi
import ingetrazo_3d.components.regulating_lines as _rl
import ingetrazo_3d.components.site_terrain as _st
import ingetrazo_3d.components.lower_levels as _ll
import ingetrazo_3d.components.level3_reading_room as _l3
import ingetrazo_3d.components.envelope_and_south_wing as _ew
import ingetrazo_3d.components.roof_and_skylights as _rs
import ingetrazo_3d.components as _comp
import ingetrazo_3d.build_ingetrazo_library as _bld

for _m in (_vec, _pr, _ab, _swi, _rl, _st, _ll, _l3, _ew, _rs, _comp, _bld):
    importlib.reload(_m)

_bld.build_mount_angel_scene(scene)

renders_dir = repo_root / "ingetrazo_3d" / "renders"
renders_dir.mkdir(parents=True, exist_ok=True)

# 1. North-East Hillside Hero Looking Up at 3-Story Faceted Fan & Daylight Scoop
viewport.camera.target = QVector3D(0.0, 8.0, -1.5)
viewport.camera.distance = 62.0
viewport.camera.yaw = math.radians(135.0)
viewport.camera.pitch = math.radians(16.0)
viewport.camera.fov = 48.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_01_hillside_hero.png"))

# 2. South Entrance Plaza, Portico Canopy & Conical Skylight Roofscape
viewport.camera.target = QVector3D(-4.0, -8.0, 2.0)
viewport.camera.distance = 52.0
viewport.camera.yaw = math.radians(-58.0)
viewport.camera.pitch = math.radians(15.0)
viewport.camera.fov = 48.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_02_south_entry.png"))

# 3. Level 3 Mezzanine Reading Counter & Dome Lamps Looking Across Well to Scoop
viewport.camera.target = QVector3D(0.5, 4.0, 1.4)
viewport.camera.distance = 13.5
viewport.camera.yaw = math.radians(102.0)
viewport.camera.pitch = math.radians(6.0)
viewport.camera.fov = 62.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_03_mezzanine_pov.png"))

# Park live viewport on the dramatic North-East Hillside Hero view
viewport.camera.target = QVector3D(0.0, 8.0, -1.5)
viewport.camera.distance = 62.0
viewport.camera.yaw = math.radians(135.0)
viewport.camera.pitch = math.radians(16.0)
viewport.camera.fov = 48.0
viewport.update()

result = {"groups": [g.name for g in scene.groups], "faces": sum(len(g.mesh.faces) for g in scene.groups)}
"""


def capture_web_renders(repo_root: Path):
    """Capture 2560x1440 QHD studio renders from `docs/library-3d.html` across all 6 camera presets."""
    import functools
    import http.server
    import shutil
    import socketserver
    import subprocess
    import threading

    docs_dir = repo_root / "docs"
    renders_dir = repo_root / "ingetrazo_3d" / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(docs_dir))

    class QuietTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with QuietTCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

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
                    browser_bin = str(candidate)
                    break

        shots = [
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
        if browser_bin:
            try:
                from PIL import Image
            except ImportError:
                Image = None

            docs_renders_dir = docs_dir / "renders"
            docs_renders_dir.mkdir(parents=True, exist_ok=True)
            for cam_key, fname in shots:
                out_file = renders_dir / fname
                url = f"http://127.0.0.1:{port}/library-3d.html?cam={cam_key}&studio=1"
                cmd = [
                    browser_bin,
                    "--headless=new",
                    "--hide-scrollbars",
                    "--no-sandbox",
                    "--enable-webgl",
                    "--ignore-gpu-blocklist",
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                    "--window-size=2560,1520",
                    "--virtual-time-budget=6500",
                    f"--screenshot={out_file}",
                    url,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                if out_file.is_file():
                    if Image is not None:
                        try:
                            with Image.open(out_file) as im:
                                if im.size != (2560, 1440):
                                    im.crop((0, 0, 2560, 1440)).save(out_file)
                        except OSError as err:
                            print(f"Warning: Could not crop {out_file.name}: {err}")
                    shutil.copy2(out_file, docs_renders_dir / fname)
                print(f"Captured QHD Studio Render: {out_file}")
        else:
            print("Warning: No headless Chromium binary found for WebGL studio capture.")
        httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Build Alvar Aalto's Mount Angel Abbey Library in IngeTrazo 0.6.0")
    parser.add_argument("--live", action="store_true", help="Push directly to running IngeTrazo MCP bridge (127.0.0.1:4763)")
    parser.add_argument("--skip-web", action="store_true", help="Skip headless browser QHD studio render capture")
    args = parser.parse_args()

    out_dir = REPO_ROOT / "ingetrazo_3d"
    out_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from core.scene import Scene
    from formats.igz import save_scene
    from formats.obj import save_obj
    from PySide6.QtWidgets import QApplication

    _app = QApplication.instance() or QApplication(sys.argv)
    scene = Scene()
    build_mount_angel_scene(scene)

    igz_path = out_dir / "mount_angel_library.igz"
    obj_path = out_dir / "mount_angel_library.obj"
    web_json_path = REPO_ROOT / "docs" / "overlays" / "library_3d_scene.json"

    save_scene(scene, igz_path)
    save_obj(scene, obj_path)
    export_web_scene_json(scene, web_json_path)

    total_faces = sum(len(g.mesh.faces) for g in scene.groups)
    print(f"Saved IngeTrazo project: {igz_path} ({len(scene.groups)} layers, {total_faces} faces)")
    print(f"Saved Wavefront OBJ:     {obj_path}")

    if args.live:
        import ingetrazo_mcp
        resp = ingetrazo_mcp._bridge("run_python", {"code": LIVE_BRIDGE_CODE})
        print("Live IngeTrazo 0.6.0 response:", resp)

    if not args.skip_web:
        capture_web_renders(REPO_ROOT)


if __name__ == "__main__":
    main()
