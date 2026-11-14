# Changelog

All notable changes to the Mount Angel Abbey Library constructive vector and 3D architectural modeling project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
