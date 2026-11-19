"""Segment 07 Score & Audio Builder — Ascent & Dusk Finale (28.0s).

Harmonic world: 60 BPM (1 bar = 4.00s) Benedictine Finale Cadence:
  Bar 1 (0–4s)   : Gmaj9/D     — Roof-off cutaway ascent; speech enters at 3.00s
  Bar 2 (4–8s)   : Dm9/D       — "...built from the inside out." concludes (~8.2s)
  Bar 3 (8–12s)  : Asus4/D     — Roof seals on; Choir Aah bloom enters
  Bar 4 (12–16s) : Dadd9       — High dusk orbit around West sky
  Bar 5 (16–20s) : G6/D        — Banking toward ENE & Mt. Hood alpenglow
  Bar 6 (20–24s) : Asus4/D     — Golden-rose horizon suspension
  Bar 7 (24–28s) : D(add9)     — Final Benedictine resolution fading gently to silence
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
SPEECH_START_SEC = 3.00


def build_seg07_midi(midi_out: Path) -> Path:
    tempo = pm.bpm2tempo(60)
    mf = pm.new_midi(title="Mount Angel Seg 07 - Ascent and Dusk", tempo=tempo)
    tpb = mf.ticks_per_beat  # 480
    bar = tpb * 4            # 1920 ticks = 4.00s

    # 1. Full Swell Choir (KBH Bank 1, Prog 4) — warm Benedictine chordal swells
    swell = pm.Voice(mf, pm.V.choir_swell, channel=13)
    swell.set_pan(56, 0)

    # 2. Choir Aah (KBH Bank 1, Prog 6) — luminous upper triad bloom after narration
    aah = pm.Voice(mf, pm.V.choir_aah, channel=15)
    aah.set_pan(72, 0)

    # 3. Orchestral Harp (GM Bank 0, Prog 46) — slow half-note harmonic fifths
    harp = pm.Instrument(mf, pm.I.orchestral_harp, channel=3)
    harp.set_pan(68, 0)

    # 4. Deep Cello pedal (GM Bank 0, Prog 42) — monastic D2 + A2 ground
    cello = pm.Instrument(mf, pm.I.cello, channel=1)
    cello.set_pan(62, 0)

    # MIDI notes: D2=38, A2=45, D3=50, F3=53, F#3=54, G3=55, A3=57, B3=59,
    # C4=60, D4=62, E4=64, F4=65, F#4=66, G4=67, A4=69, B4=71
    progression = [
        ([50, 55, 59, 66, 69], (59, 66), None),            # Bar 1: Gmaj9/D
        ([50, 53, 57, 60, 64], (57, 64), None),            # Bar 2: Dm9/D
        ([50, 57, 62, 64, 69], (62, 69), [62, 64, 69]),    # Bar 3: Asus4/D (roof seals on)
        ([50, 54, 57, 62, 66], (57, 66), [62, 66, 69]),    # Bar 4: Dadd9
        ([50, 55, 59, 64, 67], (59, 67), [64, 67, 71]),    # Bar 5: G6/D
        ([50, 57, 62, 64, 69], (62, 69), [62, 64, 69]),    # Bar 6: Asus4/D
        ([50, 54, 57, 62, 66], (62, None), [57, 62, 66]),  # Bar 7: D(add9) final cadence
        ([50, 54, 57, 62, 66], (None, None), [57, 62, 66]),  # Bar 8: Release tail
    ]

    for idx, (chord_notes, harp_pair, aah_triad) in enumerate(progression):
        is_tail = idx >= 6
        hi_vel = 74 if is_tail else 88
        lo_vel = 28 if is_tail else 38

        swell.set_notes(chord_notes, duration=bar - 40, offset=14, velocity=70)
        swell.set_rest(40)
        swell.ramp_volume_up(int(bar * 0.45), lo=lo_vel, hi=hi_vel)
        swell.ramp_volume_down(bar - int(bar * 0.45), lo=lo_vel, hi=hi_vel)

        if idx % 2 == 0:
            cello.set_notes([38, 45], duration=bar * 2 - 40, offset=0, velocity=64)
            cello.set_rest(40)
            cello.ramp_volume_up(bar, lo=34, hi=74 if not is_tail else 58)
            cello.ramp_volume_down(bar, lo=34, hi=74 if not is_tail else 58)

        h1, h2 = harp_pair
        if h1 is not None:
            harp.set_note(h1, duration=tpb * 2 - 20, velocity=48)
            harp.set_rest(20)
        else:
            harp.set_rest(tpb * 2)
        if h2 is not None:
            harp.set_note(h2, duration=tpb * 2 - 20, velocity=42)
            harp.set_rest(20)
        else:
            harp.set_rest(tpb * 2)
        harp.set_volume(60, bar)

        if aah_triad is not None:
            aah.set_notes(aah_triad, duration=bar - 50, offset=10, velocity=64)
            aah.set_rest(50)
            aah.ramp_volume_up(int(bar * 0.5), lo=28, hi=74 if not is_tail else 58)
            aah.ramp_volume_down(bar - int(bar * 0.5), lo=28, hi=74 if not is_tail else 58)
        else:
            aah.set_rest(bar)
            aah.set_volume(0, bar)

    midi_out.parent.mkdir(parents=True, exist_ok=True)
    mf.save(str(midi_out))
    return midi_out


def main() -> None:
    midi_path = SEG_DIR / "seg07_score.mid"
    music_wav = SEG_DIR / "seg07_music.wav"
    narr_wav = SEG_DIR / "seg07_narration.wav"
    master_wav = SEG_DIR / "seg07_ascent_and_dusk.wav"
    script_scr = SEG_DIR / "script.scr"

    print("[Seg 07] 1/3 Building harmonic-resonance Benedictine Finale MIDI...")
    build_seg07_midi(midi_path)

    print("[Seg 07] 2/3 Rendering MIDI via timidity...")
    render_midi_with_timidity(midi_path, music_wav)

    print("[Seg 07] 3/3 Synthesizing Argon III-C closing narration via studio speak...")
    synthesize_narration(script_scr, narr_wav)

    info = mix_segment_master_wav(
        music_wav=music_wav,
        narration_wav=narr_wav,
        master_wav_out=master_wav,
        duration_sec=DURATION_SEC,
        speech_start_sec=SPEECH_START_SEC,
        music_gain=0.36,
        duck_ratio=0.55,
        voice_gain=0.92,
        fade_in_sec=1.60,
        fade_out_sec=4.20,
    )
    print(f"[Seg 07] Master WAV ready: {master_wav}")
    print("         Timing:", json.dumps(info))


if __name__ == "__main__":
    main()
