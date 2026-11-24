# Mount Angel Abbey Library — PHOTON Studio Production Guide (`videos/STUDIO.md`)

Project-specific conventions for the 7-segment architectural fly-through film of Alvar Aalto's Mount Angel Abbey Library (1970). Loaded automatically alongside the global `/studio` skill.

---

## 1. Non-Negotiable Video & Storage Invariants

1. **Resolution & Cadence**: Native `2560×1440` QHD (`16:9`) at strict `30.00 fps` CFR (`r_frame_rate == avg_frame_rate == 30/1`), `yuv420p`, `-movflags +faststart`.
2. **Zero Artificial FFmpeg Filters**: Render via `studio motion <pkg_dir>` (`rawvideo_vflip` hardware WebGL2 `gl.readPixels` stream). Never inject artificial `-vf` colour, crop, pad, or scale filters.
3. **Strict No-Symlinks Policy**: Never symlink `videos/` to `/home/phi/MEDIA` or FUSE-mount Google Drive.
   - **Tier 1 (Git-tracked)**: `STUDIO.md`, `library_choreography.js`, `compose_score.py`, and per-segment `<seg>/motion.json`, `<seg>/script.scr`, `<seg>/score.py`, `<seg>/*_thumb.png`.
   - **Tier 2/3 (Git-ignored)**: `*.mp4`, `*.wav`, `*.mid`, `*_narration.json`, `.tts_cache/`, `frames/`, `test_frames/`.

---

## 2. WebGL2 Engine & Choreography (`docs/library-3d.{html,css,js}` + `library_choreography.js`)

- **Panoramic 3D Cascade & Mt. Hood Horizon (`FS_SKY`)**:
  - Calibrated to the Abbey's surveyed `28.5°` NNE Reference-North grid rotation (`45.0692° N, 122.7972° W`):
    - **Mt. Hood** (`92.7 km`, `68.2° ENE`) -> `XY = 50.3°` (framed in the Entry / Bay D–E vista and over the Library from the Abbey Quad).
    - **Mt. Jefferson** (`90.0 km`, `118.8° ESE`) -> `XY = -0.3°` (straight out the East Periodical Lounge glass).
    - **Mt. Adams** (`161.8 km`, `38.4° NE`) -> `XY = 80.1°`.
    - **Mt. St. Helens** (`133.3 km`, `20.3° NNE`) -> `XY = 98.2°`.
- **Deterministic Bridge (`window.__mountAngelStudio`)**:
  - `videos/library_choreography.js` polls `window.__mountAngelStudio.isLoaded()` during `__studioSetup` until all 7 reusable furniture components and all 10 layers (`0_Regulating_Grid` through `9_Campus_Trees`) referenced by `overlays/library_3d_scene.json` (`overlays/scene/`) are uploaded to WebGL2.
  - Keyframes in `<seg>/motion.json` (`keyframes` array) interpolate `tx, ty, tz, yaw, pitch, dist, fov, doy, hour, secD, buildClipZ, cladD, cladDeg, regAlpha, regWp, regSweepDeg, regArc, regDrape` via monotonic cubic Hermite splines (`PCHIP`), plus stepped state keys `secMode`, `secFlip`, `secRadialDeg`, `pocheTone`, `caster`, `heliodon`, `ortho`, `hideLayers`, `bareHill`, `structureOnly`, `cladMode`, `cladFlip`, and `regActive`.

---

## 3. Sparse Narration & Tonal Score (`studio speak` + `harmonic-resonance` + `timidity`)

- **Narration (`studio speak`)**:
  - Voice: **Argon III-C** (`voice_xdhacg1pn1cq`, `[style:resonant]`).
  - Pacing: Sparse — **1 concise sentence (`10–25` words) per segment**, leaving **`14–22 seconds` of pure visual flight and music**.
  - **Segment 01 Lead-In**: Let animation and music establish the scene for **`4.5–5.5s` ( > 1 musical bar)** before speech enters.
- **Tonal & Choral Score (`harmonic_resonance.midiator` + `timidity`)**:
  - Unified **`60 BPM` (`1 bar = 4.00s`) D-modal harmonic world**, with a distinct 4-chord rhythmic swell track per segment.
  - Rendered at `48 kHz` stereo via `timidity -c /etc/timidity/timidity.cfg -c /home/phi/.photon/timidity.cfg` combining Bank 1 (`KBH_Real_and_Swell_Choir.sf2` — `Little Swell Choir`, `Swell Choir`, `Mixed Choir`, `Choir Ooh`, `Solo Ooh`, `Solo Aah`) with Bank 0 (`FluidR3_GM.sf2` — cello pedal, vibraphone, harp, piano).

---

## 4. Segment Render Workflow (One Segment at a Time)

Active editions:
- **Unfolding Edition (8 segments, `4m 04s`)**: `videos/unfolding/seg01_dawn_circuit/` through `seg08_ascent_and_dusk/` → `videos/unfolding/mount_angel_unfolding.mp4` via `python3 videos/unfolding/assemble_film.py`.
- **Original Archive Edition (7 segments)**: `videos/seg01_hilltop/` through `seg07_ascent/` → `videos/mount_angel_library_film.mp4`.

```bash
# 1. Verify zero camera collisions against campus buildings & hillside
python3 videos/check_clearance.py videos/unfolding/seg01_dawn_circuit/motion.json

# 2. Build MIDI score + Argon III-C narration + ducked stereo master WAV
uv run --no-project --offline --with mido --with numpy --with pyyaml python3 videos/unfolding/seg01_dawn_circuit/score.py

# 3. Render 5 diagnostic QHD keyframes first & inspect visually
studio motion videos/unfolding/seg01_dawn_circuit --test-frames

# 4. Render full 2560x1440 @ 30.00 fps CFR segment MP4 + verify streams
studio motion videos/unfolding/seg01_dawn_circuit
ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration -of json videos/unfolding/seg01_dawn_circuit/seg01_dawn_circuit.mp4
```
