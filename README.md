# Mount Angel Abbey Library — Alvar Aalto (1970)

**Constructive Vector Blueprint Overlays & IngeTrazo 0.6.0 Parametric 3D Reconstruction**

This repository reconstructs Alvar Aalto's landmark library at Mount Angel Abbey (St. Benedict, Oregon, 1970) directly from the 47 low-resolution architectural & structural blueprint scans (`docs/drawings/`) and Fr. Barnabas Reasoner's 1965 Helsinki program report (`references/documents/Barnabas-Report.pdf`).

---

## Architecture of the Pipeline

1. **Sub-Pixel Constructive Vector Engine (`src/phiarchitect/mountangel/vectors.py`)**
   - Establishes a single canonical 3D coordinate system anchored at **Working Point #4 (`WP #4 = (0, 0, 0)`)** on the Level 3 Finished Floor (lying directly along **Survey Grid Line `(6)`**; `+X` = East, `+Y` = North, `+Z` = Up).
   - Cross-registers 7 primary architectural & structural sheets (`03-a3`, `04-a4`, `05-a5`, `06-a6`, `07-a7`, `13-a13`, `35-s4`) to sub-pixel accuracy (`0.68–1.21 px` RMS) and emits multi-layer *College Geometry*-style SVG overlays (`docs/overlays/sheet_*.svg`) and dark-blueprint verification proofs (`docs/overlays/proofs/`).

2. **Interactive Blueprint & Vector Archive (`docs/index.html`)**
   - Browse all 47 sheets with a **✦ Vector Calibrated (7)** filter.
   - Open any calibrated sheet to toggle constructive layers (`Regulating Grid & Rays`, `Columns & H-Piers`, `Walls, Slabs & Carrels`, `Well, Stairs & Bookstacks`, `Roof, Scoop & Skylights`), switch **Dark Blueprint** mode, and dim the raster scan opacity (`0%–100%`) to inspect the extracted vectors cleanly.

3. **Modular IngeTrazo 0.6.0 3D Model (`ingetrazo_3d/`)**
   - Compiles an 8-layer parametric 3D architectural model (`ingetrazo_3d/mount_angel_library.igz` + `.obj`/`.mtl`) directly from `AaltoGeometry` (`FT_TO_M = 0.3048`):
     - `0_Regulating_Grid`: Polycentric working points (`WP #4`, `WP #3A`, `WP_LOWER`), structural rays `B`/`C`/`D`, boundary rays `A`/`E`, and `R = 31'-10"` arc.
     - `1_Abbey_Hillside_Site`: Contoured Mount Angel bluff dropping from the `+1'-8"` South Entry Plaza down to `-34'-0"` along the grassy North hillside.
     - `2_Level_1_Base`: Downhill stack floor (`-26'-6"` / `-8.08 m`), 5-sided interior concrete retaining wall, and radial archival bookstacks.
     - `3_Level_2_Middle`: Lower reading well & stack floor (`-12'-6"` / `-3.81 m`), `R = 31'-10"` curved birch reference bookcases, study carrel alcoves, Semicircular Reference Gallery (`-4'-6"` / `-1.37 m`), and West & East stepped radial flanking stairs.
     - `4_Level_3_Reading_Room`: Asymmetric fan mezzanine (`0'-0"` / `0.00 m`) framing the open double-height Reading Well (`R = 43.8 ft`), continuous curved birch & matte-black-linoleum reading counter with 16 Aalto dome lamps, curved Control Desk, 15 radiating bookstack ranges, Periodical Lounge, and Upper South Wing (`+2'-0"` / `+0.61 m`).
     - `5_Structural_Frame`: 18"Ø white round columns (including the **paired twin columns** at `4'-10"` c/c along Rays `B`, `C`, `D`) and 3 full-height Buff-Brick & Steel **Perimeter H-Piers**.
     - `6_Envelope_And_South_Wing`: 3-story faceted Mount Angel buff-brick North curtain wall (`A–B`, `B–C`, `C–D`, `D–E`) with exterior hemlock sun louvers, East Mt. Hood picture window, South Rare Book Auditorium wing, and cantilevered copper/hemlock South Entry Canopy.
     - `7_Roof_And_Daylight_Scoop`: Curved copper-and-white-plaster **Central North Daylight Scoop** (`+21'-6"` / `+6.55 m`) with sloped north glazing & radial mullions, **Tipped North Perimeter Roof Scoop**, suspended slatted wood ceiling drum, and **12 Conical Roof Skylight Lanterns**.

4. **Standalone WebGL2 Interactive 3D Viewer (`docs/library-3d.html`)**
   - Zero-dependency WebGL2 architectural viewer loading `docs/overlays/library_3d_scene.json` with real-time Orbit/Pan/Zoom, per-layer toggles, 1-click **Roof Cutaway**, and 6 architectural camera presets.

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

### 3. Launch the Interactive Blueprint Archive & 3D Web Viewer

```bash
python3 -m http.server 8080 --directory docs
```

Then open:
- Blueprint & Vector Overlay Archive: `http://localhost:8080/index.html`
- Interactive 3D Model Viewer: `http://localhost:8080/library-3d.html`
