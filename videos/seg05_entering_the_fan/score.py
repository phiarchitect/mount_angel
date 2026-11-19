"""Segment 05 Score & Audio Builder — Entering the Fan (28.0s).

Harmonic world: 60 BPM (1 bar = 4.00s) Intimate Chamber Progression:
  Bar 1 (0–4s)   : Bm9    — Upper Lobby & birch screen; speech enters at 2.50s
  Bar 2 (4–8s)   : Gmaj7  — Descending wide Entry Steps beneath radial slatted ceiling
  Bar 3 (8–12s)  : D/F#   — Passing Control Desk & glass wall ("...toward Mount Hood" ends ~9.3s)
  Bar 4 (12–16s) : Em9    — Alcove vista opens; Solo Aah enters softly (F#4 -> G4)
  Bar 5 (16–20s) : Bm9    — Gliding over stairwell bookcase into Ray D radial aisle (A4 -> B4)
  Bar 6 (20–24s) : Gmaj7  — Open 14-ft radial avenue between slatted birch bookcases (B4 -> G4)
  Bar 7 (24–28s) : D/F#   — Sunlit perimeter gallery facing H-Column D & Mt. Hood (A4 -> F#4)
  Bar 8 (28–32s) : Em9    — Tail bar for smooth cosine fade-out
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
SPEECH_START_SEC = 2.50  # 2.5s chamber lead-in before narration enters on the entry steps


def build_seg05_midi(midi_out: Path) -> Path:
    tempo = pm.bpm2tempo(60)  # 60 BPM -> 1 beat = 1.00s (480 ticks), 1 bar = 4.00s (1920 ticks)
    mf = pm.new_midi(title="Mount Angel Seg 05 - Entering the Fan", tempo=tempo)
    tpb = mf.ticks_per_beat  # 480
    bar = tpb * 4            # 1920 ticks = 4.00s

    # 1. Little Swell Choir (KBH Bank 1, channel 12) — hushed velvety chord swells (lo=32, hi=74)
    choir = pm.Voice(mf, pm.V.choir_little_swell, channel=12)
    choir.set_pan(54, 0)

    # 2. Solo Aah (KBH Bank 1, channel 10) — warm, intimate single choral voice
    solo = pm.Voice(mf, pm.V.solo_aah, channel=10)
    solo.set_pan(72, 0)

    # 3. Acoustic Grand Piano (GM Bank 0, channel 0) — quiet, spacious 4-beat arpeggiated chord tones
    piano = pm.Instrument(mf, pm.I.acoustic_grand_piano, channel=0)
    piano.set_pan(58, 0)

    # 4. Warm Cello (GM Bank 0, channel 1) — legato bass (B2 -> G2 -> F#2 -> E2)
    cello = pm.Instrument(mf, pm.I.cello, channel=1)
    cello.set_pan(68, 0)

    # MIDI note numbers:
    # Bass: E2=40, F#2=42, G2=43, B2=47
    # Mid/Treble: D3=50, E3=52, F#3=54, G3=55, A3=57, B3=59, C#4=61, D4=62, F#4=66, G4=67, A4=69, B4=71, C#5=73
    progression = [
        # (cello_bass, choir_voicing, piano_arp_4beats, solo_notes_or_None)
        (47, [50, 54, 57, 61, 66], [59, 62, 66, 73], (66,)),     # Bar 1: Bm9   (whole note F#4 lead-in)
        (43, [50, 55, 59, 62, 66], [59, 62, 66, 71], None),      # Bar 2: Gmaj7 (narration active)
        (42, [50, 57, 62, 66, 69], [57, 62, 66, 69], None),      # Bar 3: D/F#  (narration concludes ~9.3s)
        (40, [52, 55, 59, 62, 66], [59, 62, 66, 67], (66, 67)),  # Bar 4: Em9   + Solo Aah (F#4 -> G4)
        (47, [50, 54, 57, 61, 66], [59, 62, 66, 73], (69, 71)),  # Bar 5: Bm9   + Solo Aah (A4 -> B4)
        (43, [50, 55, 59, 62, 66], [59, 62, 66, 71], (71, 67)),  # Bar 6: Gmaj7 + Solo Aah (B4 -> G4)
        (42, [50, 57, 62, 66, 69], [57, 62, 66, 69], (69, 66)),  # Bar 7: D/F#  + Solo Aah (A4 -> F#4)
        (40, [52, 55, 59, 62, 66], [59, 62, 66, 64], None),      # Bar 8: Em9   (tail bar for fade-out)
    ]

    arp_vels = [52, 42, 46, 40]

    for bass_note, chord_notes, piano_notes, solo_phrase in progression:
        # Hushed velvety choir swell (lo=32, hi=74)
        choir.set_notes(chord_notes, duration=bar - 60, offset=12, velocity=68)
        choir.set_rest(60)
        choir.ramp_volume_up(int(bar * 0.45), lo=32, hi=74)
        choir.ramp_volume_down(bar - int(bar * 0.45), lo=32, hi=74)

        # Warm legato cello bass (B2 -> G2 -> F#2 -> E2)
        cello.set_note(bass_note, duration=bar - 30, velocity=62)
        cello.set_rest(30)
        cello.ramp_volume_up(int(bar * 0.45), lo=36, hi=70)
        cello.ramp_volume_down(bar - int(bar * 0.45), lo=36, hi=70)

        # Quiet, spacious 4-beat arpeggiated piano chord tones (velocity 40..52)
        for b_i, pn in enumerate(piano_notes):
            piano.set_note(pn, duration=tpb - 20, velocity=arp_vels[b_i])
            piano.set_rest(20)
        piano.set_volume(64, bar)

        # Intimate Solo Aah voice (whole note or gentle half-note pairs)
        if solo_phrase is not None and len(solo_phrase) == 1:
            solo.set_note(solo_phrase[0], duration=bar - 80, velocity=58)
            solo.set_rest(80)
            solo.ramp_volume_up(int(bar * 0.45), lo=28, hi=66)
            solo.ramp_volume_down(bar - int(bar * 0.45), lo=28, hi=66)
        elif solo_phrase is not None and len(solo_phrase) == 2:
            n1, n2 = solo_phrase
            solo.set_note(n1, duration=tpb * 2 - 24, velocity=62)
            solo.set_rest(24)
            solo.set_note(n2, duration=tpb * 2 - 40, velocity=60)
            solo.set_rest(40)
            solo.ramp_volume_up(int(bar * 0.5), lo=32, hi=74)
            solo.ramp_volume_down(bar - int(bar * 0.5), lo=32, hi=74)
        else:
            solo.set_rest(bar)
            solo.set_volume(0, bar)

    midi_out.parent.mkdir(parents=True, exist_ok=True)
    mf.save(str(midi_out))
    return midi_out


def main() -> None:
    midi_path = SEG_DIR / "seg05_score.mid"
    music_wav = SEG_DIR / "seg05_music.wav"
    narr_wav = SEG_DIR / "seg05_narration.wav"
    master_wav = SEG_DIR / "seg05_entering_the_fan.wav"
    script_scr = SEG_DIR / "script.scr"

    print("[Seg 05] 1/3 Building harmonic-resonance MIDI score (60 BPM, Solo Aah + Choir + Piano + Cello)...")
    build_seg05_midi(midi_path)

    print("[Seg 05] 2/3 Rendering MIDI via timidity (FluidR3_GM + KBH_Real_and_Swell_Choir)...")
    render_midi_with_timidity(midi_path, music_wav)

    print("[Seg 05] 3/3 Synthesizing sparse Argon III-C narration via studio speak...")
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
    print(f"[Seg 05] Master WAV ready: {master_wav}")
    print("         Timing:", json.dumps(info))


if __name__ == "__main__":
    main()
