"""Segment 04 Score & Audio Builder — Section of Light (32.0s).

Harmonic world: 60 BPM (1 bar = 4.00s) Warm Dmaj9 Descending Cycle
(Gmaj7 – F#m7 – Em9 – Dmaj9 repeated across 8 bars + 1 tail bar):
  Bar 1 (0–4s)   : Gmaj7  — East-North-East perspective; section sweep begins; speech @ 2.50s
  Bar 2 (4–8s)   : F#m7   — "...gathers sky light and reflects it..." slicing westward
  Bar 3 (8–12s)  : Em9    — "...shadowless, down three stories" arrives at Sheet 13 Section A-A
  Bar 4 (12–16s) : Dmaj9  — Pure daylight & section study begins across open Reading Well
  Bar 5 (16–20s) : Gmaj7  — Gliding closer into 3'-11" roof plenum & conical skylight shafts
  Bar 6 (20–24s) : F#m7   — Curved northern Daylight Scoop & three-tone stencil poché
  Bar 7 (24–28s) : Em9    — Panning northward along terraced Mezzanine & Sunken Well
  Bar 8 (28–32s) : Dmaj9  — Warm northern light resolution with Cascade horizon beyond
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SEG_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = SEG_DIR.parent
MIDIATOR_SRC = Path("/home/phi/PROJECTS/harmonic-resonance/midiator/src")
sys.path.insert(0, str(VIDEOS_DIR))
if MIDIATOR_SRC.exists():
    sys.path.insert(0, str(MIDIATOR_SRC))

import harmonic_resonance.midiator as pm
from compose_score import (
    mix_segment_master_wav,
    render_midi_with_timidity,
    synthesize_narration,
)

DURATION_SEC = 32.0
SPEECH_START_SEC = 2.50  # 2.5s lead-in before narrator cues section slice


def build_seg04_midi(midi_out: Path) -> Path:
    tempo = pm.bpm2tempo(60)  # 60 BPM -> 1 beat = 1.00s (480 ticks), 1 bar = 4.00s (1920 ticks)
    mf = pm.new_midi(title="Mount Angel Seg 04 - Section of Light", tempo=tempo)
    tpb = mf.ticks_per_beat  # 480
    bar = tpb * 4            # 1920 ticks = 4.00s

    # 1. Solo Ooh (KBH Bank 1, channel 8) — luminous upper vocal line (B4 -> A4 -> G4 -> F#4)
    solo = pm.Voice(mf, pm.V.solo_ooh, channel=8)
    solo.set_pan(70, 0)

    # 2. Choir Ooh (KBH Bank 1, channel 14) — soft sustained 4-second harmonic bed
    choir = pm.Voice(mf, pm.V.choir_ooh, channel=14)
    choir.set_pan(56, 0)

    # 3. Celesta (GM Bank 0, channel 5) — delicate crystalline 1-beat bell droplets
    celesta = pm.Instrument(mf, pm.I.celesta, channel=5)
    celesta.set_pan(74, 0)

    # 4. Warm Cello (GM Bank 0, channel 1) — descending bass roots (G2 -> F#2 -> E2 -> D2)
    cello = pm.Instrument(mf, pm.I.cello, channel=1)
    cello.set_pan(62, 0)

    # MIDI notes: D2=38, E2=40, F#2=42, G2=43 | D3=50, E3=52, F#3=54, G3=55, A3=57, B3=59
    # C#4=61, D4=62, E4=64, F#4=66, G4=67, A4=69, B4=71, C#5=73, D5=74
    # Tuple: (cello_root, choir_notes, celesta_4beats, solo_notes)
    progression = [
        # Cycle 1 (Bars 1–4): serene whole notes B4 -> A4 -> G4 -> F#4
        (43, [55, 59, 62, 66], [74, 71, 66, 71], (71,)),          # Bar 1: Gmaj7  (B4)
        (42, [54, 57, 61, 64], [73, 69, 64, 69], (69,)),          # Bar 2: F#m7   (A4)
        (40, [52, 55, 59, 62, 66], [71, 67, 62, 66], (67,)),      # Bar 3: Em9    (G4)
        (38, [50, 57, 61, 64, 66], [69, 66, 64, 69], (66,)),      # Bar 4: Dmaj9  (F#4)
        # Cycle 2 (Bars 5–8): luminous half-note descant descending through B4 -> A4 -> G4 -> F#4
        (43, [55, 59, 62, 66], [74, 71, 66, 71], (71, 74)),       # Bar 5: Gmaj7  (B4 -> D5)
        (42, [54, 57, 61, 64], [73, 69, 64, 69], (69, 73)),       # Bar 6: F#m7   (A4 -> C#5)
        (40, [52, 55, 59, 62, 66], [71, 67, 62, 66], (67, 71)),   # Bar 7: Em9    (G4 -> B4)
        (38, [50, 57, 61, 64, 66], [69, 66, 64, 66], (66, 69)),   # Bar 8: Dmaj9  (F#4 -> A4)
        # Bar 9: Tail bar for smooth cosine release
        (38, [50, 57, 61, 64, 66], [66, 64, 62, 66], (66,)),      # Bar 9: Dmaj9  (F#4)
    ]

    bell_velocities = [47, 39, 44, 38]  # strictly within 38..48

    for idx, (bass_note, chord_notes, bell_notes, solo_notes) in enumerate(progression):
        # Choir Ooh soft sustained 4-second harmonic bed (lo=34, hi=78)
        choir.set_notes(chord_notes, duration=bar - 56, offset=10, velocity=68)
        choir.set_rest(56)
        choir.ramp_volume_up(int(bar * 0.48), lo=34, hi=78)
        choir.ramp_volume_down(bar - int(bar * 0.48), lo=34, hi=78)

        # Warm Cello descending bass root per bar (G2 -> F#2 -> E2 -> D2)
        cello.set_note(bass_note, duration=bar - 44, velocity=62)
        cello.set_rest(44)
        cello.ramp_volume_up(int(bar * 0.42), lo=36, hi=72)
        cello.ramp_volume_down(bar - int(bar * 0.42), lo=36, hi=72)

        # Celesta crystalline 1-beat bell droplets (velocity 38..48)
        for b_i, bn in enumerate(bell_notes):
            celesta.set_note(bn, duration=tpb - 24, velocity=bell_velocities[b_i])
            celesta.set_rest(24)
        celesta.set_volume(60, bar)

        # Solo Ooh luminous upper vocal line (gentler during Bars 1–2 narration, radiant in Bars 3–8)
        solo_hi = 64 if idx < 2 else 82
        if len(solo_notes) == 1:
            solo.set_note(solo_notes[0], duration=bar - 48, velocity=62)
            solo.set_rest(48)
        else:
            n1, n2 = solo_notes
            solo.set_note(n1, duration=tpb * 2 - 24, velocity=64)
            solo.set_rest(24)
            solo.set_note(n2, duration=tpb * 2 - 40, velocity=60)
            solo.set_rest(40)
        solo.ramp_volume_up(int(bar * 0.50), lo=32, hi=solo_hi)
        solo.ramp_volume_down(bar - int(bar * 0.50), lo=32, hi=solo_hi)

    midi_out.parent.mkdir(parents=True, exist_ok=True)
    mf.save(str(midi_out))
    return midi_out


def main() -> None:
    midi_path = SEG_DIR / "seg04_score.mid"
    music_wav = SEG_DIR / "seg04_music.wav"
    narr_wav = SEG_DIR / "seg04_narration.wav"
    master_wav = SEG_DIR / "seg04_section_of_light.wav"
    script_scr = SEG_DIR / "script.scr"

    print("[Seg 04] 1/3 Building harmonic-resonance MIDI score (60 BPM, Solo/Choir Ooh + Celesta + Cello)...")
    build_seg04_midi(midi_path)

    print("[Seg 04] 2/3 Rendering MIDI via timidity (FluidR3_GM + KBH_Real_and_Swell_Choir)...")
    render_midi_with_timidity(midi_path, music_wav)

    print("[Seg 04] 3/3 Synthesizing sparse Argon III-C narration via studio speak...")
    synthesize_narration(script_scr, narr_wav)

    info = mix_segment_master_wav(
        music_wav=music_wav,
        narration_wav=narr_wav,
        master_wav_out=master_wav,
        duration_sec=DURATION_SEC,
        speech_start_sec=SPEECH_START_SEC,
        music_gain=0.35,
        duck_ratio=0.55,
        voice_gain=0.92,
        fade_in_sec=1.60,
        fade_out_sec=3.00,
    )
    print(f"[Seg 04] Master WAV ready: {master_wav}")
    print("         Timing:", json.dumps(info))


if __name__ == "__main__":
    main()
