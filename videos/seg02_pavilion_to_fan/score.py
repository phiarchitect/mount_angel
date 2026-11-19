"""Segment 02 Score & Audio Builder — Pavilion to Fan (28.0s).

Harmonic world: 60 BPM (1 bar = 4.00s) D Dorian modal cycle:
  Bar 1 (0–4s)   : Dm9       — Low approach to South Entry Canopy; narration cues at 2.50s
  Bar 2 (4–8s)   : Bbmaj7/D  — Rising over copper marquee & 12 conical skylights
  Bar 3 (8–12s)  : Gm9/D     — "...fanning north toward the light" concludes; pure flight begins
  Bar 4 (12–16s) : Asus4/D   — Cresting West Cataloging courtyard as afternoon shadows sweep
  Bar 5 (16–20s) : Dm9       — Solo Aah modal arch enters past 73.3° West brick prow
  Bar 6 (20–24s) : Bbmaj7/D  — Descending over NW bluff past splayed H-Columns B & C
  Bar 7 (24–28s) : Gm9/D     — Holding on monumental 3-story North Curtain Wall
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
SPEECH_START_SEC = 2.50  # 2.5s lead-in before sparse narration enters


def build_seg02_midi(midi_out: Path) -> Path:
    tempo = pm.bpm2tempo(60)  # 60 BPM -> 1 beat = 1.00s (480 ticks), 1 bar = 4.00s (1920 ticks)
    mf = pm.new_midi(title="Mount Angel Seg 02 - Pavilion to Fan", tempo=tempo)
    tpb = mf.ticks_per_beat  # 480
    bar = tpb * 4            # 1920 ticks = 4.00s

    # 1. Choir Ooh (KBH Bank 1) — lush 4-second chord swells
    choir = pm.Voice(mf, pm.V.choir_ooh, channel=14)
    choir.set_pan(56, 0)

    # 2. Solo Aah (KBH Bank 1) — gentle half-note modal arch in Bars 5–7 after speech ends
    solo = pm.Voice(mf, pm.V.solo_aah, channel=10)
    solo.set_pan(72, 0)

    # 3. Orchestral Harp (GM Bank 0) — gentle 4-beat Dorian arpeggio cycle (1.0s quarter notes)
    harp = pm.Instrument(mf, pm.I.orchestral_harp, channel=3)
    harp.set_pan(68, 0)

    # 4. Warm Cello pedal (GM Bank 0) — grounded D2 + A2 fifth
    cello = pm.Instrument(mf, pm.I.cello, channel=1)
    cello.set_pan(62, 0)

    # MIDI note numbers:
    # D2=38, A2=45, D3=50, F3=53, G3=55, A3=57, Bb3=58,
    # C4=60, D4=62, E4=64, F4=65, G4=67, A4=69, C5=72
    progression = [
        # (choir_notes, harp_4beats, solo_half_notes_or_None)
        ([50, 53, 57, 60, 64], [62, 64, 65, 69], None),          # Bar 1: Dm9 (speech @ 2.50s)
        ([50, 53, 58, 62, 69], [58, 62, 65, 69], None),          # Bar 2: Bbmaj7/D
        ([50, 55, 58, 65, 69], [58, 62, 67, 69], None),          # Bar 3: Gm9/D
        ([50, 55, 57, 62, 64], [57, 62, 64, 69], None),          # Bar 4: Asus4/D
        ([50, 53, 57, 60, 64], [62, 64, 69, 72], (64, 69)),      # Bar 5: Dm9      + Solo Aah (E4 -> A4)
        ([50, 53, 58, 62, 69], [58, 62, 65, 69], (72, 69)),      # Bar 6: Bbmaj7/D + Solo Aah (C5 -> A4)
        ([50, 55, 58, 65, 69], [58, 62, 67, 69], (67, 69)),      # Bar 7: Gm9/D    + Solo Aah (G4 -> A4)
        ([50, 55, 57, 62, 64], [57, 62, 64, 62], None),          # Bar 8: Asus4/D tail bar for clean fade
    ]

    harp_vels = (54, 44, 48, 42)

    for idx, (chord_notes, harp_notes, solo_pair) in enumerate(progression):
        # Choir lush 4-second breath swell
        choir.set_notes(chord_notes, duration=bar - 60, offset=12, velocity=72)
        choir.set_rest(60)
        choir.ramp_volume_up(int(bar * 0.45), lo=40, hi=88)
        choir.ramp_volume_down(bar - int(bar * 0.45), lo=40, hi=88)

        # Cello warm D2 + A2 pedal breathing every 2 bars
        if idx % 2 == 0:
            cello.set_notes([38, 45], duration=bar * 2 - 40, offset=0, velocity=64)
            cello.set_rest(40)
            cello.ramp_volume_up(bar, lo=38, hi=74)
            cello.ramp_volume_down(bar, lo=38, hi=74)

        # Orchestral Harp soft quarter-note Dorian arpeggio (velocity 42..54)
        for b_i, hn in enumerate(harp_notes):
            harp.set_note(hn, duration=tpb - 20, velocity=harp_vels[b_i])
            harp.set_rest(20)
        harp.set_volume(66, bar)

        # Solo Aah modal arch in Bars 5–7
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
    midi_path = SEG_DIR / "seg02_score.mid"
    music_wav = SEG_DIR / "seg02_music.wav"
    narr_wav = SEG_DIR / "seg02_narration.wav"
    master_wav = SEG_DIR / "seg02_pavilion_to_fan.wav"
    script_scr = SEG_DIR / "script.scr"

    print("[Seg 02] 1/3 Building harmonic-resonance MIDI score (60 BPM D Dorian, Choir Ooh + Harp + Cello)...")
    build_seg02_midi(midi_path)

    print("[Seg 02] 2/3 Rendering MIDI via timidity (FluidR3_GM + KBH_Real_and_Swell_Choir)...")
    render_midi_with_timidity(midi_path, music_wav)

    print("[Seg 02] 3/3 Synthesizing sparse Argon III-C narration via studio speak...")
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
    print(f"[Seg 02] Master WAV ready: {master_wav}")
    print("         Timing:", json.dumps(info))


if __name__ == "__main__":
    main()
