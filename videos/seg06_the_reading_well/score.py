"""Segment 06 Score & Audio Builder — The Reading Well (32.0s).

Harmonic world: 60 BPM (1 bar = 4.00s) Reflective Modal-Plagal Pulse:
  Bar 1 (0–4s)   : D6/9    — Level 3 workbench, stools & lamps; speech enters at 2.50s
  Bar 2 (4–8s)   : Am9/D   — Gliding over the parapet into the open Reading Well
  Bar 3 (8–12s)  : Gmaj7/D — Narration concludes (~9.5s); descending toward Mezzanine
  Bar 4 (12–16s) : Gm6/D   — Warm Nordic minor-plagal color (Bb3 + F4) over -4'-6" Mezzanine
  Bar 5 (16–20s) : D6/9    — Solo Ooh enters gently (F#4 -> A4) past curved Reference Bookwall
  Bar 6 (20–24s) : Am9/D   — Crossing into the Sunken Well (A4 -> G4)
  Bar 7 (24–28s) : Gmaj7/D — Upward-tilted pan across 18" round columns (F#4 -> B4)
  Bar 8 (28–32s) : Gm6/D   — Glowing concave North Daylight Scoop hold (G4 -> F4)
  Bar 9 (32–36s) : D6/9    — Tail bar for smooth cosine fade-out resolution
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
SPEECH_START_SEC = 2.50  # 2.5s meditative lead-in before narration enters


def build_seg06_midi(midi_out: Path) -> Path:
    tempo = pm.bpm2tempo(60)  # 60 BPM -> 1 beat = 1.00s (480 ticks), 1 bar = 4.00s (1920 ticks)
    mf = pm.new_midi(title="Mount Angel Seg 06 - The Reading Well", tempo=tempo)
    tpb = mf.ticks_per_beat  # 480
    bar = tpb * 4            # 1920 ticks = 4.00s

    # 1. Mixed Choir (KBH Bank 1, channel 11) — warm 4-second modal-plagal chord swells (lo=36, hi=84)
    choir = pm.Voice(mf, pm.V.choir_mixed, channel=11)
    choir.set_pan(54, 0)

    # 2. Solo Ooh (KBH Bank 1, channel 8) — gentle contemplative melody in Bars 5–8 after speech concludes
    solo = pm.Voice(mf, pm.V.solo_ooh, channel=8)
    solo.set_pan(74, 0)

    # 3. Warm Cello (GM Bank 0, channel 1) — sustained D2 (38) + A2 (45) monastic foundation
    cello = pm.Instrument(mf, pm.I.cello, channel=1)
    cello.set_pan(64, 0)

    # 4. Soft Vibraphone (GM Bank 0, channel 2) — bell-like quarter-note pattern (velocity 38..50)
    vibes = pm.Instrument(mf, pm.I.vibraphone, channel=2)
    vibes.set_pan(70, 0)

    # MIDI note numbers:
    # Foundation: D2=38, A2=45
    # Choir/Bells: D3=50, F#3=54, G3=55, A3=57, Bb3=58, B3=59,
    #              C4=60, D4=62, E4=64, F4=65, F#4=66, G4=67, A4=69, B4=71
    progression = [
        # (choir_voicing, vibe_pattern_4beats, solo_half_notes_or_None)
        ([50, 54, 59, 64, 66], [62, 66, 64, 69], None),      # Bar 1: D6/9    (speech enters @ 2.50s)
        ([50, 57, 60, 64, 67], [60, 64, 67, 71], None),      # Bar 2: Am9/D   (narration active)
        ([50, 55, 59, 62, 66], [59, 66, 62, 69], None),      # Bar 3: Gmaj7/D (narration concludes ~9.5s)
        ([50, 55, 58, 62, 65], [58, 65, 62, 67], None),      # Bar 4: Gm6/D   (Bb3=58 & F4=65 Nordic color)
        ([50, 54, 59, 64, 66], [62, 66, 64, 69], (66, 69)),  # Bar 5: D6/9    + Solo Ooh (F#4 -> A4)
        ([50, 57, 60, 64, 67], [60, 64, 67, 71], (69, 67)),  # Bar 6: Am9/D   + Solo Ooh (A4 -> G4)
        ([50, 55, 59, 62, 66], [59, 66, 62, 69], (66, 71)),  # Bar 7: Gmaj7/D + Solo Ooh (F#4 -> B4)
        ([50, 55, 58, 62, 65], [58, 65, 62, 67], (67, 65)),  # Bar 8: Gm6/D   + Solo Ooh (G4 -> F4)
        ([50, 54, 59, 64, 66], [62, 69, 66, 62], None),      # Bar 9: D6/9    (tail bar resolution)
    ]

    vibe_vels = [50, 38, 44, 40]

    for idx, (chord_notes, vibe_notes, solo_pair) in enumerate(progression):
        # Mixed Choir warm 4-second breath swell (lo=36, hi=84)
        choir.set_notes(chord_notes, duration=bar - 60, offset=12, velocity=70)
        choir.set_rest(60)
        choir.ramp_volume_up(int(bar * 0.45), lo=36, hi=84)
        choir.ramp_volume_down(bar - int(bar * 0.45), lo=36, hi=84)

        # Cello sustained D2 + A2 warm foundation breathing across 2-bar (or final 1-bar) spans
        if idx % 2 == 0 and idx < len(progression) - 1:
            cello.set_notes([38, 45], duration=bar * 2 - 40, offset=0, velocity=62)
            cello.set_rest(40)
            cello.ramp_volume_up(bar, lo=38, hi=72)
            cello.ramp_volume_down(bar, lo=38, hi=72)
        elif idx == len(progression) - 1:
            cello.set_notes([38, 45], duration=bar - 40, offset=0, velocity=58)
            cello.set_rest(40)
            cello.ramp_volume_down(bar, lo=34, hi=66)

        # Vibraphone soft, bell-like quarter-note pattern (velocity 38..50)
        for b_i, vn in enumerate(vibe_notes):
            vibes.set_note(vn, duration=tpb - 20, velocity=vibe_vels[b_i])
            vibes.set_rest(20)
        vibes.set_volume(60, bar)

        # Solo Ooh gentle contemplative melody in Bars 5–8
        if solo_pair is not None:
            n1, n2 = solo_pair
            solo.set_note(n1, duration=tpb * 2 - 24, velocity=62)
            solo.set_rest(24)
            solo.set_note(n2, duration=tpb * 2 - 40, velocity=60)
            solo.set_rest(40)
            solo.ramp_volume_up(int(bar * 0.5), lo=32, hi=76)
            solo.ramp_volume_down(bar - int(bar * 0.5), lo=32, hi=76)
        else:
            solo.set_rest(bar)
            solo.set_volume(0, bar)

    midi_out.parent.mkdir(parents=True, exist_ok=True)
    mf.save(str(midi_out))
    return midi_out


def main() -> None:
    midi_path = SEG_DIR / "seg06_score.mid"
    music_wav = SEG_DIR / "seg06_music.wav"
    narr_wav = SEG_DIR / "seg06_narration.wav"
    master_wav = SEG_DIR / "seg06_the_reading_well.wav"
    script_scr = SEG_DIR / "script.scr"

    print("[Seg 06] 1/3 Building harmonic-resonance MIDI score (60 BPM, Mixed Choir + Solo Ooh + Vibes + Cello)...")
    build_seg06_midi(midi_path)

    print("[Seg 06] 2/3 Rendering MIDI via timidity (FluidR3_GM + KBH_Real_and_Swell_Choir)...")
    render_midi_with_timidity(midi_path, music_wav)

    print("[Seg 06] 3/3 Synthesizing sparse Argon III-C narration via studio speak...")
    synthesize_narration(script_scr, narr_wav)

    info = mix_segment_master_wav(
        music_wav=music_wav,
        narration_wav=narr_wav,
        master_wav_out=master_wav,
        duration_sec=DURATION_SEC,
        speech_start_sec=SPEECH_START_SEC,
        music_gain=0.34,
        duck_ratio=0.55,
        voice_gain=0.92,
        fade_in_sec=1.60,
        fade_out_sec=3.00,
    )
    print(f"[Seg 06] Master WAV ready: {master_wav}")
    print("         Timing:", json.dumps(info))


if __name__ == "__main__":
    main()
