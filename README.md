# Mount Angel Abbey Library — Alvar Aalto (1970)

**Constructive Vector Blueprint Overlays & IngeTrazo 0.6.0 Parametric 3D Reconstruction**

This repository reconstructs Alvar Aalto's landmark library at Mount Angel Abbey (St. Benedict, Oregon, 1970) directly from the 47 low-resolution architectural & structural blueprint scans (`docs/drawings/`) and Fr. Barnabas Reasoner's 1965 Helsinki program report (`references/documents/Barnabas-Report.pdf`).

---

## Architecture of the Pipeline

1. **Sub-Pixel Constructive Vector Engine (`src/phiarchitect/mountangel/vectors.py`)**
   - Establishes a single canonical 3D coordinate system anchored at **Working Point #4 (`WP #4 = (0, 0, 0)`)** on the Level 3 Finished Floor (lying directly along **Survey Grid Line `(6)`**; `+X` = East, `+Y` = North, `+Z` = Up).
   - Cross-registers 7 primary architectural & structural sheets (`03-a3`, `04-a4`, `05-a5`, `06-a6`, `07-a7`, `13-a13`, `35-s4`) to sub-pixel accuracy (`0.68–1.21 px` RMS) and emits multi-layer *College Geometry*-style SVG overlays (`docs/overlays/sheet_*.svg`) and dark-blueprint verification proofs (`docs/overlays/proofs/`).

2. **Interactive Web Suite (`docs/`)**
   - **Project Introduction & Suite Overview (`docs/index.html`)**: Unified landing page introducing Alvar Aalto's 1970 Mount Angel Abbey Library and the digital reconstruction, with an interactive 4-view QHD stage, live draggable Photo-vs-Model curtain wipe, Mount Angel Abbey angel crest & `favicon.ico`, and consistent suite navigation (`docs/suite.css`).
   - **Standalone WebGL2 3D Viewer (`docs/library-3d.html`)**: Zero-dependency WebGL2 architectural viewer loading `docs/overlays/library_3d_scene.json` with real-time Orbit/Pan/Zoom, per-layer toggles, GPU stencil architectural **Red Poché** section cuts, dynamic 4096px solar shadows, 45.07°N Mount Angel heliodon studies, 1-click **Roof Cutaway**, 20 camera presets, and keyboard hotkeys (`F` fullscreen, `M` hide/show menus).
   - **Making-Of Architectural Monograph (`docs/making-of.html`)**: Comprehensive interactive monograph detailing the constructive reverse-engineering methodology, structural mechanics, daylighting acoustics, and an interactive before/after curtain slider comparing early blockouts against the final 134,459-face model.
   - **Photographic Registration & Evaluation Lab (`docs/photo-compare.html`)**: Accuracy evaluation lab comparing 8 archival and contemporary photographs against matched IngeTrazo camera perspectives via Curtain Wipe, Onion-Skin Difference/Multiply, and Side-by-Side modes.
   - **Blueprint & Vector Archive (`docs/drawings.html`)**: Browse all 47 sheets (`A1–A28`, `F1–F3`, `S1–S16`) with a **✦ Vector Calibrated (7)** filter, toggle constructive layers (`Regulating Grid & Rays`, `Columns & H-Piers`, `Walls, Slabs & Carrels`, `Well, Stairs & Bookstacks`, `Roof, Scoop & Skylights`), switch **Dark Blueprint** mode, and dim raster scan opacity (`0%–100%`).
   - **Visitor Rack Card & Lobby Orientation Poster Studio (`docs/visitor-guide.html`)**: Flexible CSS-variable-driven print & wayfinding workbench featuring a double-sided `4" × 9"` visitor rack card, three `24" × 36"` Lobby orientation posters, skylight cross-section, Abbey hilltop campus map, 4 Abbey & Model palettes with architectural red poché, and Lobby wall installation preview (`src/phiarchitect/mountangel/wayfinding.py`, `visitor_guide.py`).

3. **Modular IngeTrazo 0.6.0 3D Model (`ingetrazo_3d/`)**
   - Compiles a complete **134,459-face 2-manifold** parametric 3D architectural model (`ingetrazo_3d/mount_angel_library.igz` + `.obj`/`.mtl`) directly from `AaltoGeometry` (`FT_TO_M = 0.3048`) across 9 modular component builders:
     - `regulating_lines.py`: Polycentric radial grid, working points (`WP #4`, `WP #3A`, `WP_LOWER`), structural rays `B`/`C`/`D`, boundary rays `A`/`E`, and `R = 31'-10"` regulating arcs.
     - `site_terrain.py`: Contoured Mount Angel hillside bluff dropping from the `+1'-8"` South Entry Plaza down to `-34'-0"` on the North slope, plus Mount Angel Abbey campus context including the landmark 126-ft South Bell Tower and 3-story Monastery range.
     - `lower_levels.py`: Level 1 downhill stack floor (`-26'-6"` / `-8.08 m`), 5-sided interior concrete retaining wall, Level 2 middle reading well & stack floor (`-12'-6"` / `-3.81 m`), Semicircular Reference Gallery (`-4'-6"` / `-1.37 m`), and West & East stepped radial flanking stairs.
     - `level3_reading_room.py`: Asymmetric fan mezzanine (`0'-0"` / `0.00 m`) framing the open double-height Reading Well (`R = 43.8 ft`), continuous curved birch & matte-black-linoleum reading counter with 16 Aalto dome lamps, curved Control Desk, Periodical Lounge, Artek 69 chairs, and Upper South Wing (`+2'-0"` / `+0.61 m`).
     - `aalto_bookcases.py`: Parameterized Alvar Aalto birch open-face bookcases across all three levels, including Level 1 radial archival stacks, Level 2 curved reference bookcases and study carrel alcoves, and Level 3 fan mezzanine ranges and stairwell open shelves.
     - `south_wing_interiors.py`: 14-bay glazed Director and Media room partition wall, Lobby 32-batten natural wood bathroom partition screen, dual West squiggle walls with Aalto acoustic curves, and Rare Book Auditorium fitout with stepped lecture tiers.
     - `envelope_and_south_wing.py`: 3-story faceted Mount Angel buff-brick North curtain wall (`A–B`, `B–C`, `C–D`, `D–E`) with exterior hemlock sun louvers, East Mt. Hood picture window, irregular perimeter brick/steel H-columns, paired twin columns, and cantilevered copper/hemlock South Entry Canopy.
     - `roof_and_skylights.py`: 3-tier roof hierarchy, 3'-11" `24WF68` fan roof plenum, curved copper-and-white-plaster **Central North Daylight Scoop** (`+21'-6"` / `+6.55 m`) with sloped north glazing & radial mullions, radial wood-slatted hemlock/birch ceiling sector, and **12 Conical Roof Skylight Lanterns**.
     - `primitives.py`: Geometric primitive generators, 2-manifold mesh stitching, coordinate transformations (`FT_TO_M`), and shared material definitions (`MATERIALS`).

4. **Architectural Visualizations & Studio Renders (`docs/renders/`)**
   - 20 high-resolution QHD studio renders (`studio_01_hillside_hero.png` through `studio_20_auditorium_cutaway.png`) capturing exterior hillside vistas, section perspectives, interior reading rooms, heliodon sun studies, and campus context.

---

## Quick Start

### 1. Regenerate Constructive Vector Overlays & Proofs

```bash
uv run --no-project --offline --with pillow --with numpy python3 -c "import sys; from pathlib import Path; r = Path('.'); sys.path.insert(0, str(r/'src')); from phiarchitect.mountangel.vectors import export_all_overlays; export_all_overlays(r, r/'docs'/'overlays'/'proofs')"
```

### 2. Build the IngeTrazo `.igz` + `.obj` Model & Studio Renders

```bash
/home/phi/PROJECTS/phi-WORKS/ingetrazo/.venv/bin/python ingetrazo_3d/build_ingetrazo_library.py
```

To push the model live into a running **IngeTrazo 0.6.0** window (with AI TCP Bridge enabled on `127.0.0.1:4763`):

```bash
/home/phi/PROJECTS/phi-WORKS/ingetrazo/.venv/bin/python ingetrazo_3d/build_ingetrazo_library.py --live
```

### 3. Launch the Interactive Web Suite

```bash
python3 -m http.server 8080 --directory docs
```

Then open:
- Project Overview & Suite Landing Page: `http://localhost:8080/index.html`
- Interactive 3D Model Viewer (`F` fullscreen, `M` hide menus): `http://localhost:8080/library-3d.html`
- Making-Of Architectural Monograph: `http://localhost:8080/making-of.html`
- Photographic Evaluation Lab: `http://localhost:8080/photo-compare.html`
- Blueprint & Vector Archive (47 Sheets): `http://localhost:8080/drawings.html`
- Visitor Rack Card & Lobby Posters: `http://localhost:8080/visitor-guide.html`
