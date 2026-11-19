"""Segment 01 Score & Audio Builder — Hilltop, Mt. Hood & Bluff Reveal (28.0s).

Harmonic world: 60 BPM (1 bar = 4.00s) D open modal cycle:
  Bar 1 (0–4s)   : D5(add9)    — Pure dawn flight over Abbey Quad & Mt. Hood
  Bar 2 (4–8s)   : Cadd9/D     — Focus shifts to Library; narration enters at 4.50s
  Bar 3 (8–12s)  : G6/D        — "...that faces two worlds" concludes (~10.2s)
  Bar 4 (12–16s) : Asus4/D     — Sweeping past South Pergolas & East Lounge
  Bar 5 (16–20s) : Bm11/D      — Crossing bluff rim; Solo Ooh descant enters
  Bar 6 (20–24s) : Gmaj9/D     — 3-story North-East fan & Daylight Scoop reveal
  Bar 7 (24–28s) : Dadd9       — Peaceful morning resolution
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

DURATION_SEC = 28.0
SPEECH_START_SEC = 4.50  # 4.5s of pure music & dawn flight before narrator speaks


def build_seg01_midi(midi_out: Path) -> Path:
    tempo = pm.bpm2tempo(60)  # 60 BPM -> 1 beat = 1.00s (480 ticks), 1 bar = 4.00s (1920 ticks)
    mf = pm.new_midi(title="Mount Angel Seg 01 - Hilltop and Bluff", tempo=tempo)
    tpb = mf.ticks_per_beat  # 480
    bar = tpb * 4            # 1920 ticks = 4.00s

    # 1. Little Swell Choir (KBH Bank 1, Prog 3) — rhythmic 4-second modal chord swells
    choir = pm.Voice(mf, pm.V.choir_little_swell, channel=12)
    choir.set_pan(54, 0)

    # 2. Solo Ooh descant (KBH Bank 1, Prog 0) — enters softly after narration in Bars 5–7
    solo = pm.Voice(mf, pm.V.solo_ooh, channel=8)
    solo.set_pan(74, 0)

    # 3. Warm Cello pedal (GM Bank 0, Prog 42) — deep D2 monastic ground
    cello = pm.Instrument(mf, pm.I.cello, channel=1)
    cello.set_pan(64, 0)

    # 4. Gentle Vibraphone fifths (GM Bank 0, Prog 11) — unhurried rhythmic pulse
    vibes = pm.Instrument(mf, pm.I.vibraphone, channel=2)
    vibes.set_pan(70, 0)

    # MIDI note numbers: D2=38, A2=45, D3=50, F#3=54, G3=55, A3=57, B3=59,
    # C4=60, D4=62, E4=64, F#4=66, G4=67, A4=69, B4=71
    progression = [
        # (choir_notes, vibe_pattern_4beats, solo_half_notes_or_None)
        ([50, 57, 62, 64, 69], [62, 69, 64, 69], None),          # Bar 1: D5(add9)
        ([50, 55, 60, 64, 67], [60, 67, 64, 67], None),          # Bar 2: Cadd9/D (speech enters @ 4.5s)
        ([50, 55, 59, 64, 67], [59, 67, 64, 67], None),          # Bar 3: G6/D
        ([50, 57, 62, 64, 69], [62, 69, 64, 69], None),          # Bar 4: Asus4/D
        ([50, 54, 57, 62, 66], [62, 66, 69, 66], (69, 71)),      # Bar 5: Bm11/D + Solo Ooh (A4 -> B4)
        ([50, 55, 59, 66, 69], [59, 66, 69, 66], (69, 67)),      # Bar 6: Gmaj9/D + Solo Ooh (A4 -> G4)
        ([50, 57, 62, 64, 66], [62, 66, 69, 66], (66, 69)),      # Bar 7: Dadd9   + Solo Ooh (F#4 -> A4)
        ([50, 57, 62, 66, 69], [62, 69, 66, 62], None),          # Bar 8: Tail bar for smooth fade-out
    ]

    for idx, (chord_notes, vibe_notes, solo_pair) in enumerate(progression):
        # Choir gentle 4-second breath swell
        choir.set_notes(chord_notes, duration=bar - 60, offset=12, velocity=72)
        choir.set_rest(60)
        choir.ramp_volume_up(int(bar * 0.45), lo=40, hi=88)
        choir.ramp_volume_down(bar - int(bar * 0.45), lo=40, hi=88)

        # Cello low D2 + A2 fifth breathing every 2 bars
        if idx % 2 == 0:
            cello.set_notes([38, 45], duration=bar * 2 - 40, offset=0, velocity=64)
            cello.set_rest(40)
            cello.ramp_volume_up(bar, lo=38, hi=74)
            cello.ramp_volume_down(bar, lo=38, hi=74)

        # Vibraphone soft quarter-note bell cycle (1 beat = 1.00s per note)
        for b_i, vn in enumerate(vibe_notes):
            vel = 52 if b_i == 0 else 40
            vibes.set_note(vn, duration=tpb - 20, velocity=vel)
            vibes.set_rest(20)
        vibes.set_volume(62, bar)

        # Solo Ooh floating descant in second half of segment
        if solo_pair is not None:
            n1, n2 = solo_pair
            solo.set_note(n1, duration=tpb * 2 - 20, velocity=64)
            solo.set_rest(20)
            solo.set_note(n2, duration=tpb * 2 - 40, velocity=62)
            solo.set_rest(40)
            solo.ramp_volume_up(int(bar * 0.5), lo=34, hi=78)
            solo.ramp_volume_down(bar - int(bar * 0.5), lo=34, hi=78)
        else:
            solo.set_rest(bar)
            solo.set_volume(0, bar)

    midi_out.parent.mkdir(parents=True, exist_ok=True)
    mf.save(str(midi_out))
    return midi_out


def main() -> None:
    midi_path = SEG_DIR / "seg01_score.mid"
    music_wav = SEG_DIR / "seg01_music.wav"
    narr_wav = SEG_DIR / "seg01_narration.wav"
    master_wav = SEG_DIR / "seg01_hilltop.wav"
    script_scr = SEG_DIR / "script.scr"

    print("[Seg 01] 1/3 Building harmonic-resonance MIDI score (60 BPM, KBH Choir + Cello + Vibes)...")
    build_seg01_midi(midi_path)

    print("[Seg 01] 2/3 Rendering MIDI via timidity (FluidR3_GM + KBH_Real_and_Swell_Choir)...")
    render_midi_with_timidity(midi_path, music_wav)

    print("[Seg 01] 3/3 Synthesizing sparse Argon III-C narration via studio speak...")
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
        fade_in_sec=1.80,
        fade_out_sec=3.00,
    )
    print(f"[Seg 01] Master WAV ready: {master_wav}")
    print("         Timing:", json.dumps(info))


if __name__ == "__main__":
    main()
