"""Segment 03 Score & Audio Builder — Sun & Seasons (32.0s).

Harmonic world: 60 BPM (1 bar = 4.00s) luminous D Lydian solar cycle
(G#4 = MIDI 68 gives radiant Lydian sunlight shimmer):
  Bar 1 (0–4s)   : Dmaj7#11 — Morning sun raking East hemlock louvers (speech @ 2.50s)
  Bar 2 (4–8s)   : E/D      — Gliding North along radial curtain wall under narration
  Bar 3 (8–12s)  : Bm7/D    — Narration concludes (~9.0s); sun swings past solar noon
  Bar 4 (12–16s) : Asus2/D  — 290° WNW evening sun rakes splayed H-columns; Heliodon ON @ 14.5s
  Bar 5 (16–20s) : Dmaj7#11 — Ascending into full-site 45.07° N Heliodon dome
  Bar 6 (20–24s) : Eadd9/D  — Sweeping across Equinox solar trajectory
  Bar 7 (24–28s) : Bm7/D    — Autumnal descent across hourly analemma spokes
  Bar 8 (28–32s) : Asus2/D  — Winter Solstice golden glow with Cascade horizon
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
SPEECH_START_SEC = 2.50  # 2.5s musical lead-in, ~6.5s speech, ~23.0s solar flight


def build_seg03_midi(midi_out: Path) -> Path:
    tempo = pm.bpm2tempo(60)  # 60 BPM -> 1 beat = 1.00s (480 ticks), 1 bar = 4.00s (1920 ticks)
    mf = pm.new_midi(title="Mount Angel Seg 03 - Sun and Seasons", tempo=tempo)
    tpb = mf.ticks_per_beat  # 480
    bar = tpb * 4            # 1920 ticks = 4.00s

    # 1. Swell Choir (KBH Bank 1) — radiant 4-second Lydian chord swells
    choir = pm.Voice(mf, pm.V.choir_swell, channel=13)
    choir.set_pan(56, 0)

    # 2. Vibraphone (GM Bank 0, Prog 11) — shimmering 4-note Lydian bell cycle
    vibes = pm.Instrument(mf, pm.I.vibraphone, channel=2)
    vibes.set_pan(72, 0)

    # 3. Orchestral Harp (GM Bank 0, Prog 46) — soft half-note harmonic fifths
    harp = pm.Instrument(mf, pm.I.orchestral_harp, channel=3)
    harp.set_pan(48, 0)

    # 4. Cello (GM Bank 0, Prog 42) — warm D2 + A2 monastic ground pedal
    cello = pm.Instrument(mf, pm.I.cello, channel=1)
    cello.set_pan(64, 0)

    # D Lydian pitch set: D2=38, A2=45, D3=50, E3=52, F#3=54, G#3=56, A3=57, B3=59,
    # C#4=61, D4=62, E4=64, F#4=66, G#4=68, A4=69, B4=71, C#5=73, D5=74, E5=76
    progression = [
        # (choir_notes, vibe_4notes, harp_half_dyads)
        ([50, 57, 61, 66, 68], [62, 68, 69, 73], ([50, 57], [57, 64])),  # Bar 1: Dmaj7#11
        ([50, 56, 59, 64, 68], [64, 68, 71, 68], ([50, 59], [52, 59])),  # Bar 2: E/D
        ([50, 54, 59, 62, 69], [62, 66, 69, 73], ([50, 57], [54, 61])),  # Bar 3: Bm7/D
        ([50, 57, 61, 64, 69], [61, 64, 69, 73], ([50, 57], [57, 64])),  # Bar 4: Asus2/D
        ([50, 57, 62, 68, 73], [62, 68, 69, 74], ([50, 57], [62, 69])),  # Bar 5: Dmaj7#11 (Heliodon bloom)
        ([50, 56, 59, 66, 71], [64, 68, 71, 76], ([50, 59], [59, 66])),  # Bar 6: Eadd9/D
        ([50, 54, 59, 66, 69], [62, 66, 71, 69], ([50, 57], [59, 66])),  # Bar 7: Bm7/D
        ([50, 57, 61, 66, 69], [62, 68, 69, 66], ([50, 57], [57, 62])),  # Bar 8: Asus2/D -> Dmaj9
        ([50, 57, 62, 66, 69], [62, 69, 66, 62], ([50, 57], [50, 57])),  # Bar 9: Tail bar for fade-out
    ]

    for idx, (chord_notes, vibe_notes, harp_pair) in enumerate(progression):
        # Radiant 4-second choir swell
        choir.set_notes(chord_notes, duration=bar - 60, offset=12, velocity=74)
        choir.set_rest(60)
        choir.ramp_volume_up(int(bar * 0.45), lo=42, hi=90)
        choir.ramp_volume_down(bar - int(bar * 0.45), lo=42, hi=90)

        # Warm Cello D2 + A2 pedal breathing every 2 bars (1 bar on final tail)
        if idx == len(progression) - 1:
            cello.set_notes([38, 45], duration=bar - 40, offset=0, velocity=58)
            cello.set_rest(40)
            cello.ramp_volume_down(bar, lo=32, hi=66)
        elif idx % 2 == 0:
            cello.set_notes([38, 45], duration=bar * 2 - 40, offset=0, velocity=64)
            cello.set_rest(40)
            cello.ramp_volume_up(bar, lo=38, hi=74)
            cello.ramp_volume_down(bar, lo=38, hi=74)

        # Vibraphone 4-note Lydian bell cycle (1 quarter-note = 1.00s)
        for b_i, vn in enumerate(vibe_notes):
            vel = 54 if b_i == 0 else 42
            vibes.set_note(vn, duration=tpb - 20, velocity=vel)
            vibes.set_rest(20)
        vibes.set_volume(64, bar)

        # Orchestral Harp soft half-note harmonic fifths (2 beats = 2.00s each)
        h1, h2 = harp_pair
        harp.set_notes(h1, duration=tpb * 2 - 30, offset=18, velocity=52)
        harp.set_rest(30)
        harp.set_notes(h2, duration=tpb * 2 - 30, offset=18, velocity=48)
        harp.set_rest(30)
        harp.set_volume(60, bar)

    midi_out.parent.mkdir(parents=True, exist_ok=True)
    mf.save(str(midi_out))
    return midi_out


def main() -> None:
    midi_path = SEG_DIR / "seg03_score.mid"
    music_wav = SEG_DIR / "seg03_music.wav"
    narr_wav = SEG_DIR / "seg03_narration.wav"
    master_wav = SEG_DIR / "seg03_sun_and_seasons.wav"
    script_scr = SEG_DIR / "script.scr"

    print("[Seg 03] 1/3 Building D Lydian MIDI score (60 BPM, Swell Choir + Vibes + Harp + Cello)...")
    build_seg03_midi(midi_path)

    print("[Seg 03] 2/3 Rendering MIDI via timidity (FluidR3_GM + KBH_Real_and_Swell_Choir)...")
    render_midi_with_timidity(midi_path, music_wav)

    print("[Seg 03] 3/3 Synthesizing sparse Argon III-C narration via studio speak...")
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
    print(f"[Seg 03] Master WAV ready: {master_wav}")
    print("         Timing:", json.dumps(info))


if __name__ == "__main__":
    main()
