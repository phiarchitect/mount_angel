"""Segment 08 Score & Audio Builder — Ascent and Dusk (28.0s)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SEG_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = SEG_DIR.parent.parent
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
SPEECH_START_SEC = 3.0


def build_midi(midi_out: Path) -> Path:
    tempo = pm.bpm2tempo(60)  # 60 BPM -> 1 bar = 4.00s
    mf = pm.new_midi(title="Mount Angel Unfolding Seg 08 - Ascent and Dusk", tempo=tempo)
    tpb = mf.ticks_per_beat
    bar = tpb * 4

    choir = pm.Voice(mf, pm.V.choir_swell, channel=12)
    choir.set_pan(54, 0)

    solo = pm.Voice(mf, pm.V.solo_aah, channel=8)
    solo.set_pan(74, 0)

    cello = pm.Instrument(mf, pm.I.cello, channel=1)
    cello.set_pan(64, 0)

    accent = pm.Instrument(mf, pm.I.vibraphone, channel=2)
    accent.set_pan(70, 0)

    progression = [([50, 55, 59, 66, 69], [62, 66, 69, 66], None), ([50, 57, 60, 64, 69], [62, 64, 69, 64], None), ([50, 57, 62, 64, 69], [64, 69, 67, 64], (69, 71)), ([50, 54, 57, 62, 66], [62, 66, 69, 66], (71, 69)), ([50, 55, 59, 64, 67], [59, 64, 67, 64], (67, 66)), ([50, 57, 62, 64, 69], [62, 64, 69, 64], (64, 62)), ([50, 54, 57, 62, 66], [62, 66, 69, 62], (66, 62)), ([50, 57, 62, 66, 69], [62, 69, 66, 62], None)]

    for idx, (chord_notes, pulse_notes, solo_pair) in enumerate(progression):
        choir.set_notes(chord_notes, duration=bar - 60, offset=12, velocity=74)
        choir.set_rest(60)
        choir.ramp_volume_up(int(bar * 0.46), lo=38, hi=92)
        choir.ramp_volume_down(bar - int(bar * 0.46), lo=38, hi=92)

        if idx % 2 == 0:
            cello.set_notes([38, 45], duration=bar * 2 - 40, offset=0, velocity=62)
            cello.set_rest(40)
            cello.ramp_volume_up(bar, lo=36, hi=74)
            cello.ramp_volume_down(bar, lo=36, hi=74)

        for b_i, pn in enumerate(pulse_notes):
            vel = 52 if b_i == 0 else 40
            accent.set_note(pn, duration=tpb - 20, velocity=vel)
            accent.set_rest(20)
        accent.set_volume(56, bar)

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
    midi_path = SEG_DIR / "seg08_ascent_and_dusk_score.mid"
    music_wav = SEG_DIR / "seg08_ascent_and_dusk_music.wav"
    narr_wav = SEG_DIR / "seg08_ascent_and_dusk_narration.wav"
    master_wav = SEG_DIR / "seg08_ascent_and_dusk.wav"
    script_scr = SEG_DIR / "script.scr"

    print("[Seg 08] 1/3 Building harmonic-resonance MIDI score...")
    build_midi(midi_path)
    render_midi_with_timidity(midi_path, music_wav)

    print("[Seg 08] 2/3 Synthesizing Argon III-C narration...")
    synthesize_narration(script_scr, narr_wav)

    print("[Seg 08] 3/3 Mixing 48 kHz stereo master WAV...")
    stats = mix_segment_master_wav(
        music_wav=music_wav,
        narration_wav=narr_wav,
        master_wav_out=master_wav,
        duration_sec=DURATION_SEC,
        speech_start_sec=SPEECH_START_SEC,
        music_gain=0.36,
        duck_ratio=0.54,
        voice_gain=0.92,
        fade_in_sec=1.6,
        fade_out_sec=3.6,
    )
    print(f"[Seg 08] Complete -> {master_wav.name} | {json.dumps(stats)}")


if __name__ == "__main__":
    main()
