# Changelog

All notable changes to the Mount Angel Abbey Library constructive vector and 3D architectural modeling project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.8.0] - 2026-11-23

### Added
- **Tier 1 Cast-in-Place Concrete Structure Isolation** (`ingetrazo_3d/components/`, `docs/library-3d.html`): tagged primary cast-in-place concrete structure (`concrete_struct`) across all building layers and added the **`▦ Structure [S]`** toolbar button (`S` hotkey, `?structure=1`) with a procedural board-formed concrete shader, isolated concrete edge buffers, and structural stencil poché cuts.
- **Monumental Campus Trees (`9_Campus_Trees`, `ingetrazo_3d/components/campus_trees.py`)**: 52 surveyed hilltop specimens calibrated directly to zoom-19 Google ortho-aerial imagery, Sheet `02-A2` (*"Preserve Existing Trees"*), and `docs/photos/campus_quad_aerial.jpg` — featuring cantilevered flat-topped **Cedars of Lebanon** (*Cedrus libani*), continuous single-envelope fluted **100-ft Giant Sequoias** (*Sequoiadendron giganteum*), and 80-facet geodesic **Copper Beeches & Quad Oaks** (`19,162` tris, `0` boundary/non-manifold/winding errors, `0` building collisions).
- **3-State `🌲 Trees` Viewer Control (`T` hotkey, `?trees=solid|ghost|off`)** in `docs/library-3d.html`: switches smoothly between **Solid** (real-time 4096px shadows), **Ghost** (front-face-culled matte frosted architectural veil via `uAlphaScale`), and **Off** (automatic on section cuts, Cutaway, Structure, and bare-hill modes).
- **Pre-Construction Bare Hill & "Unfolding" Film Workspace** (`8_PreConstruction_Hill`, `videos/unfolding/`, `videos/library_choreography.js`, `videos/STUDIO.md`): added toggleable bare-hill excavation patch (`?barehill=1`), procedural draped Aalto radial regulating sweep (`?reg=1`), progressive vertical build-clip & cladding wipe shaders, and complete 8-segment production scripts for the *Unfolding* architectural film.

### Changed
- **Surveyed Abbey Hilltop Campus & Formal Quad Walkways** (`ingetrazo_3d/components/site_terrain.py`, `videos/check_clearance.py`): GPS-calibrated hilltop terrain (`X = [-560, +580] ft`, `Y = [-480, +240] ft`, Reference North `26.81°` CW from True North), seamless mitered ribbons (`_add_mitered_ribbon_ft`) for North/South Abbey Drive and all formal Quad walkways (Central Promenade at `Y = -198 ft`, semicircular Church Forecourt, square crossing node, curved crescent walk), and all 8 surveyed campus buildings (**Damian Center**, **Anselm Hall**, **Post-Knox**, **Aquinas Hall**, **Abbey Church / 118-ft Campanile / 318-ft Monastery**, **Annunciation Hall**, **Saint Benedict Guesthouse & Retreat Center**, and **Abbey Press**; `0` boundary/winding errors).
- **Rebuilt 10-layer 3D scene bundle** (`docs/overlays/library_3d_scene.json`, `181,196` faces), widened hilltop shadow frustum (`shadowRadius` up to `188 m`) and zoom-out range (`340 m`), updated `campus_aerial` and `south_entry` presets in `docs/library-3d.html`, and regenerated QHD studio renders `studio_01_hillside_hero.png`, `studio_02_south_entry_canopy.png`, and `studio_18_campus_aerial.png`.

## [0.7.0] - 2026-11-19

### Added
- **3 outer-fan rooftop exhaust fan hoods** (`FAN_ROOF_EXHAUST_FANS`) alongside Rays B, C, and D: cross-checked across Roof Plan `07-a7`, Roof Framing `36-s5` (`EXH. FAN` framed openings), Reflected Ceiling Plan `10-a10`, and `roof_tiers_aerial.jpg`, overlaid in cyan on `proof_sheet_07.png`, and modeled in `roof_and_skylights.py`.
- **2 newly verified West staff/elevator corridor conical skylights** (`(-76.5, +2.0)` and `(-76.5, -12.0)`), bringing the South Wing roof to all **14 conical dome skylights** shown on `07-a7` and `10-a10`.
- **Deep Calibration stories & before/after plates** (`docs/code/calib_*.jpg`) added to `docs/making-of.html` (Chapter II) and `docs/code.html` (Catches 05–07), documenting the polycentric Working Point rebuild, the missing third Mezzanine shelf audit, and the roof skylight/exhaust-fan forensics.
- Recorded close-up cameras for shots `02`, `04`, `05`, and `06` in `scripts/capture_furniture_renders.py` alongside `03`.

### Changed
- **True archival polycentric radial geometry & plan scale** (`src/phiarchitect/mountangel/vectors.py`): re-anchored to archival `WP #3 = (0, 0)`, `WP #2 = (+2'-10", -5'-3")`, and `WP #3A` (`3'-9"` along Ray D), analytically deriving Rays A–E (`168.3°`, `137.0°`, `99.4°`, `64.5°`, `40.3°`), `Well_1/2/3` (`0.0000"` ray error), symmetric `Pair_B/C/D`, and `H-Col B/C/D`, removing the ~2% global plan scale shrinkage across all 7 calibrated blueprint overlays (`sheet_03..35.svg` & `proof_sheet_03..35.png`).
- **Exact archival vertical floor, stair & roof datums**: corrected Level 1 (`-28'-6"`), Level 2 (`-14'-0"`), Mezzanine (`-5'-4"` with `1'-0"` concrete slab and `4"` Level 3 drop lip), Level 3 (`0'-0"`), Lobby (`+1'-4"`, 3 risers), South Roof (`+13'-8"`), Main Fan Roof (`+15'-3"..+16'-2"`), Auditorium Roof (`+17'-10"`), North Parapet (`+17'-11 3/8"`), and North Daylight Scoop (`+21'-4"`), plus exact `10R + 16R` U-turn well stairs and `22R` SE flank stair (`22-a22`).
- **Rebuilt watertight 3D model** (`166,645` faces / `254,008` WebGL2 triangles, `0` unpaired edges), updated `docs/library-3d.html` (`WP3_M = [0, 0]`, `99.4°` radial cut, `Section B-B` shifted to `Y = -26'-5"` through all 6 skylight throats), regenerated `docs/visitor-guide.html`, and re-captured all 20 QHD studio renders, all 7 recalibrated Photo vs. Model comparisons, and all 5 updated Furniture close-ups.

### Fixed
- **Off-by-one bookcase shelf-spacing bug** in `ingetrazo_3d/components/aalto_bookcases.py` (`dz_tier = z_span / n_tiers`): Mezzanine curved and straight end bookcases now show all **3 full open shelves** seen in archival photographs, stairwell counters show **3 shelves**, and full-height radial stacks show **6 shelves**.
- **Radial stack clearances around `Pair_B/C/D`** recomputed for `WP #3A`'s offset (`+2.37..+3.96 ft` clearance on all 6 paired columns).
- **Conical skylight coordinates & West Cataloging throat flare**: shifted all conical skylights ~3–4 ft South to lock onto `07-a7` and `10-a10`, widened Control Desk slatted ceiling drum inner opening to `R = 5.0'`, and clamped the West Cataloging skylight throat flare cleanly inside the `Y = -29'-0"` buff-brick exterior wall.

## [0.6.2] - 2026-11-19

### Added
- `scripts/capture_furniture_renders.py`: re-renders furniture-page close-ups from recorded cameras. It starts with the Stool 60 shot; the other close-ups don't have cameras yet.

### Fixed
- Furniture page Stool 60 close-up (`docs/furniture/render_03_stool60.jpg`) re-rendered so it shows the three-legged stools along the Level 3 workbench.

## [0.6.1] - 2026-11-19

### Fixed
- Level 3 reading stools are now three-legged Artek **Stool 60**s (L-legs at 120°), as seen in the photos. The model previously built the four-legged E60. The furniture and making-of pages are corrected to match, and all static renders have been regenerated (model is now 133,921 faces).

## [0.6.0] - 2026-11-19

### Added
- **Scoop skylight header beams**: three plaster beams run through the main skylight along radial guide rays B, C and D from WP3, spanning radius 25.8–40.0 ft from WP3A at z 3.85–4.55 m (Sheet 48-s17, Main Skylight Frame Details / Detail B). Beam size is estimated from the photos.
- `scripts/capture_studio_renders.py`: standalone studio-render capture. It shoots one camera at a time, checks that the scene JSON finished loading, and retries with a longer wait if it didn't.

### Changed
- Scoop columns Well_1, Well_2 and Well_3 snapped onto rays B, C and D, and cut to stop at the underside of the beams (z 3.85 m).
- All 20 studio renders and 7 Photo vs. Model renders regenerated with the beams, all at 2560×1440.

### Fixed
- Studio renders that had captured a "Scene Load Error: Failed to fetch" frame (sky and ground only) have been re-shot.

## [0.5.0] - 2026-11-19

### Added
- **Panoramic sky & mountain horizon** in `docs/library-3d.html`: camera-aware 3D sky shader with Mt. Hood, Jefferson, Adams and St. Helens placed at their true bearings (rotated to the Abbey's 28.5° reference-north grid), the western Cascade crest, and the Silverton Hills / Coast Range foothills, all lit by the sun-path model.
- **Tilt-shift lens** (`shiftx` / `shifty` URL parameters) and fixed-size rendering for exact-aspect captures. The far clip plane now scales with camera distance, and fog thins for telephoto views.
- `window.__mountAngelStudio` bridge for scripted film rendering.
- **Fly-through film workspace** (`videos/`): `STUDIO.md` production guide, camera choreography, score composer, clearance checker and film assembler, with 7 segment folders. Rendered media is git-ignored.
- `scripts/capture_photo_matches.py`: renders every Photo vs. Model shot at the photo's exact aspect ratio, with optional 50/50 overlays.
- Mezzanine-level reference photo (`docs/photos/MA-121713-578-web-1400x700.jpg`).

### Changed
- **Photo vs. Model** (`docs/photo-compare.html`): shots 01–03 recalibrated. Shot 06 now uses a new photo taken from the mezzanine looking up at the control peninsula rail (the old one repeated Shot 05's spot). Shot 07 camera moved to head height at the foot of the west stair. Shot 08 camera moved to the east side of the scoop, looking up and west. Shots 06–08 are first-pass alignments.

### Removed
- Shot 04 from Photo vs. Model: its photo was the same image as Shot 03.

## [0.4.6] - 2026-11-18

### Added
- **Building with Code** (`docs/code.html`): parametric Python modeling strategy, three-tier module organization (`vectors.py` → `primitives.py` → 8 domain builders), live IngeTrazo + manifold-verification feedback loop, 5-stage Git camera stepper, a 7-pass H-column calibration case study (`B`, `C`, `D`), and four before/after viewport bug catches.
- **Furniture & Lamps in Code** (`docs/furniture.html`): piece-by-piece study pairing archival photograph observations, macro 3D studio renders, and Python builder code for the parapet-mounted mushroom reading lamp (`add_aalto_parapet_lamp`), cantilevered linoleum workbench & two-lug steel wall T-brackets, Artek Stool E60 & Chair 69, radial birch bookcases with 5-batten directory screens, counter-height stairwell bookcases, and the curved slatted Control Desk.
- `hud=0` URL parameter on `docs/library-3d.html` alongside `studio=1` for clean caption-free macro renders.
- **Code** and **Furniture** navigation links across all suite pages, cards on `index.html`, and README entries.

## [0.4.5] - 2026-11-16

### Added
- **The Journey** (`docs/journey.html`): Fr. Barnabas Reasoner's March 1966 trip to meet Aalto — route map, stop-by-stop story, Wikimedia Commons photos of the buildings he saw (credited), his hopes for the library, and a request to help find his lost photographs.
- Journey link in every page's navigation and a Journey card on the home page.

### Fixed
- README dates the Barnabas report to 1966.

## [0.4.4] - 2026-11-16

### Changed
- **README rewritten for the Abbey community.** It now opens with the building, the live site and what each page is for. A new section covers uses for the library and the Abbey (visitors, tours, stewardship, archive), and sources and credits are listed. Technical notes moved to the end, with corrected build flags and no hard-coded local paths.

---

## [0.4.3] - 2026-11-15

### Added
- **Measuring-grid gallery** in Making the Model, Chapter II ("Scaling the Sheets"): Sheets 3, 4, 5, 6 and 7 with the registered foot grid centred on WP #4, the Sheet 5 ray registration, and the Sheet 13 Section A-A pixel ruler (`docs/overlays/grids/`). Opens in the lightbox; the 3D deep-link is hidden for drawings.

### Fixed
- **Photo vs. Model page** (`docs/photo-compare.html`): shots 03–07 all showed shot 08's photo and render because their `<img>` tags were copy-pasted. Each card now shows its own photo and render. Also corrected the Shot 03 photo size badge.

---

## [0.4.2] - 2026-11-15

### Fixed
- **Reading-room parapet continuity**: the west and east clerestory step walls in `roof_and_skylights.py` are now one continuous brick parapet with copper coping. It runs from the west junction along a 48-step arc behind the sloped daylight-scoop skylight to the lounge junction, matching Sheet 13 (A13) and the aerial photographs.

### Changed
- **Simplified home page** (`docs/index.html`): now a short project intro and a directory of the five suite pages (3D Model, Making the Model, Photo vs. Model, Blueprints, Visitor Guide). The detailed content stays in `making-of.html`.
- Rebuilt the 3D model (`134,737` faces) and re-captured the 20 QHD studio renders plus exterior photo-match renders 01–02.

---

## [0.4.1] - 2026-11-15

### Fixed
- **Auditorium roof z-fighting**: closed-loop walls in `add_wall_strip_ft` (`ingetrazo_3d/components/primitives.py`) were emitted as a single unmitred keyhole polygon whose top/bottom caps filled the entire enclosed area. The auditorium parapet & coping caps therefore spanned the whole roof at +6.15 m and z-fought with the envelope wall tops, hiding the slate membrane. Closed loops are now true ring solids (outer ring + inner hole) with wrap-around miters.
- Removed the duplicate roof-layer brick parapet (coplanar with the Layer 6 auditorium envelope wall), inset the auditorium roof slab to the wall's inner face, and aligned the copper coping with the envelope wall (0.08 ft overhang each side).

### Changed
- Rebuilt the 3D model (`134,405` faces, 0 unmatched edges in Layers 6–7) and re-captured the 20 QHD studio renders plus exterior photo-match renders 01–02.

---

## [0.4.0] - 2026-11-15

### Added
- **Visitor Rack Card & Lobby Orientation Poster Studio (`src/phiarchitect/mountangel/wayfinding.py`, `visitor_guide.py`, `docs/visitor-guide.html`)**:
  - Parametric SVG architectural wayfinding generators derived directly from `AaltoGeometry` (`Level 3 & South Wing`, `Mezzanine & Level 2`, `Level 1`, `Section A–A Skylight & Bluff Cut`, and `Mount Angel Abbey Hilltop Campus Map`).
  - Double-sided `4" × 9"` visitor rack card, three `24" × 36"` Lobby orientation boards, and interactive Lobby wall installation preview.
  - Four Abbey & Model palettes (`Abbey & Model`, `Warm Buff-Brick`, `White Plaster`, `Dark Studio`) featuring architectural **Red Poché** (`#a42d21`), bluff earth hatching, and Abbey Quad meadow tones.
- **Project Introduction Landing Page (`docs/index.html`) & Dedicated Blueprint Explorer (`docs/drawings.html`)**:
  - Editorial overview introducing Alvar Aalto's 1970 library and the digital reconstruction, with an interactive 4-view QHD stage, live draggable Photo-vs-Model curtain wipe, telemetry bar, and direct camera/chapter launch chips.
  - Relocated the 47-sheet blueprint & 7-sheet multi-layer SVG vector-overlay explorer cleanly to `docs/drawings.html`.
- **Unified Suite Design System, Favicons & 3D Hotkeys (`docs/suite.css`, `docs/favicon.ico`, `docs/favicon.svg`, `docs/angel-logo.svg`)**:
  - Consistent `.suite-header` navigation bar and shared Abbey birch / Red Poché design tokens across all 6 suite pages.
  - Multi-resolution `favicon.ico` and vector `favicon.svg` / `angel-logo.svg` derived from the Mount Angel Abbey heraldic angel crest.
  - Added keyboard shortcuts `F` (toggle fullscreen) and `M` (hide/show all menu panels) to `docs/library-3d.html`.

---

## [0.3.0] - 2026-11-14

### Added
- **134,459-Face 2-Manifold IngeTrazo 3D Model**:
  - Full parametric architectural reconstruction featuring watertight 2-manifold polygonal geometry across 8 discrete layers (`mount_angel_library.igz`, `mount_angel_library.obj`, `mount_angel_library.mtl`).
  - Compiled directly from sub-pixel constructive vector blueprints and Aalto's imperial-to-metric geometric constraints.
- **Mount Angel Abbey Campus Context**:
  - Hillside site terrain modeling the natural drop from the South Entry Plaza (+1'-8") down to -34'-0" on the North slope.
  - Symmetrical 3-story Monastery range flanking the library entrance courtyard.
  - Landmark 126-ft South-side Benedictine Bell Tower with arched belfry openings and pyramidal roof.
- **Parameterized Alvar Aalto Bookcases (`ingetrazo_3d/components/aalto_bookcases.py`)**:
  - Modular bookcase generation with birch veneer shelves, plinths, and end panels across all three library levels.
  - Level 1 downhill archival stack ranges.
  - Level 2 middle reading well reference stacks, curved birch reference bookcases (`R = 31'-10"`), and study carrel alcoves.
  - Level 3 fan mezzanine radial stack ranges and stairwell open-shelf bookcases.
- **3-Tier Roof Hierarchy & Fan Roof Plenum Structure (`ingetrazo_3d/components/roof_and_skylights.py`)**:
  - Structural 3'-11" `24WF68` fan roof plenum framing the expansive north daylight scoop.
  - Primary north daylight scoop curved reflector with sloped north-facing glazing and radial mullions.
  - Radial wood-slatted hemlock/birch ceiling sector suspended beneath the fan plenum over the mezzanine.
  - 12 conical roof skylight lanterns with white plaster reflector cones.
- **South Wing Interiors & Architectural Millwork (`ingetrazo_3d/components/south_wing_interiors.py`)**:
  - 14-bay glazed Director and Media room partition wall separating the south offices from the reading mezzanine.
  - Entrance lobby 32-batten natural wood bathroom partition screen.
  - Dual West squiggle walls featuring Aalto's signature free-form acoustic curves at the lobby entry and auditorium.
  - Rare Book Auditorium fitout with stepped lecture tiers, oak podium, and acoustic rear wall.
- **20 High-Resolution QHD Architectural Studio Renders (`docs/renders/`)**:
  - 20 photorealistic architectural visualizations (`studio_01_hillside_hero.png` through `studio_20_auditorium_cutaway.png`), including campus aerial, auditorium cutaway, control glass wall, and blockout match perspectives.
- **Interactive Making-Of Monograph (`docs/making-of.html`)**:
  - Interactive architectural monograph documenting the complete reverse-engineering and modeling methodology.
  - Interactive before/after curtain slider comparing early blockouts against the final 134,459-face model.
- **Photographic Calibration & Accuracy Evaluation Lab (`docs/photo-compare.html`)**:
  - Split-screen visual comparison lab matching 8 historical/contemporary archival photographs against exact IngeTrazo camera perspectives.
  - Detailed architectural verification notes for materials, structural framing, daylighting, and millwork.

### Changed
- Refactored `ingetrazo_3d/components/` into 9 focused modular builders (`regulating_lines`, `site_terrain`, `lower_levels`, `level3_reading_room`, `envelope_and_south_wing`, `roof_and_skylights`, `aalto_bookcases`, `south_wing_interiors`, `primitives`).
- Updated WebGL2 scene bundle (`docs/overlays/library_3d_scene.json`) with full campus context and updated material shading.
- Bumped project version to `0.3.0` in `pyproject.toml` and `src/phiarchitect/mountangel/__init__.py`.

---

## [0.2.0] - 2026-11-13

### Added
- **IngeTrazo 0.6.0 Parametric 3D Pipeline**:
  - Modular 8-layer constructive 3D model generator (`ingetrazo_3d/build_ingetrazo_library.py`).
  - Irregular perimeter brick-and-steel H-columns with custom pilaster profiles.
  - Paired cylindrical twin columns (`18"Ø` at `4'-10"` on center) along structural Rays `B`, `C`, and `D`.
  - Mezzanine outer-arc workstations, curved counter with matte-black linoleum and birch trim, Artek 69 chairs, and parapet-mounted brass mushroom lamps.
- **Zero-Dependency WebGL2 Interactive 3D Viewer (`docs/library-3d.html`)**:
  - Real-time Orbit/Pan/Zoom navigation with 6 architectural camera viewpoints.
  - Dynamic 4096px shadow mapping and 45.07°N Mount Angel heliodon solar studies (summer solstice, equinox, winter solstice).
  - Multi-layer visibility toggles and real-time stencil-poché section cut planes.
  - 1-click roof cutaway view for instant interior mezzanine inspection.
- **Initial Studio Renders 01–16 (`docs/renders/`)**:
  - Comprehensive lighting, daylight scoop, and section plan render studies.

---

## [0.1.0] - 2026-11-10

### Added
- **Sub-Pixel Constructive Vector Engine (`src/phiarchitect/mountangel/vectors.py`)**:
  - Established canonical 3D Cartesian coordinate system centered at Working Point #4 (`WP #4 = (0, 0, 0)`) on Level 3 Finished Floor.
  - Automated cross-registration of 7 primary architectural and structural blueprint sheets (`03-a3`, `04-a4`, `05-a5`, `06-a6`, `07-a7`, `13-a13`, `35-s4`) with sub-pixel RMS accuracy (`0.68–1.21 px`).
  - Generated multi-layer *College Geometry*-style SVG constructive vector overlays (`docs/overlays/sheet_*.svg`) and dark-blueprint verification proofs (`docs/overlays/proofs/`).
- **Interactive Blueprint Archive (`docs/index.html`)**:
  - Web interface cataloging all 47 blueprint scans with calibrated vector overlays, layer toggles, opacity sliders, and dark blueprint mode.
