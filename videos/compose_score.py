"""Mount Angel Abbey Library — Tonal Choir Score & Sparse Narration Mixer.

Uses `harmonic_resonance.midiator` (`Voice` + `Instrument`) rendered via `timidity`
(`KBH_Real_and_Swell_Choir.sf2` + `FluidR3_GM.sf2`) and `studio speak` (Argon III-C)
to build each segment's exact-duration 48 kHz stereo master WAV with gentle ducking.
"""

from __future__ import annotations

import math
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

TIMIDITY_GM_CFG = Path("/etc/timidity/timidity.cfg")
TIMIDITY_CHOIR_CFG = Path.home() / ".photon" / "timidity.cfg"
STUDIO_BIN = Path.home() / ".local" / "bin" / "studio"


def render_midi_with_timidity(
    midi_path: Path,
    wav_out: Path,
    sample_rate: int = 48000,
) -> Path:
    """Render a `midiator` `.mid` file to 48 kHz stereo WAV using GM + KBH Choir soundfonts."""
    timidity_bin = shutil.which("timidity") or "/usr/bin/timidity"
    cmd = [
        timidity_bin,
        "-Ow",
        "-s",
        str(sample_rate),
        "-EFreverb=d,68",
        "-A85",
    ]
    if TIMIDITY_GM_CFG.exists():
        cmd.extend(["-c", str(TIMIDITY_GM_CFG)])
    if TIMIDITY_CHOIR_CFG.exists():
        cmd.extend(["-c", str(TIMIDITY_CHOIR_CFG)])
    cmd.extend(["-o", str(wav_out), str(midi_path)])
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return wav_out


def synthesize_narration(script_path: Path, narr_wav_out: Path) -> Path:
    """Synthesize sparse Argon III-C narration from `script.scr` via `studio speak`."""
    studio_exe = str(STUDIO_BIN) if STUDIO_BIN.exists() else (shutil.which("studio") or "studio")
    cmd = [
        studio_exe,
        "speak",
        str(script_path),
        "-o",
        str(narr_wav_out),
    ]
    subprocess.run(cmd, check=True)
    return narr_wav_out


def _read_wav_float_stereo(wav_path: Path, target_sr: int = 48000) -> np.ndarray:
    """Read any mono/stereo 16-bit PCM WAV (resampling via ffmpeg if needed) as float32 (N, 2) in [-1, 1]."""
    with wave.open(str(wav_path), "rb") as wf:
        sr = wf.getframerate()
        ch = wf.getnchannels()
        sw = wf.getsampwidth()

    if sr != target_sr or sw != 2 or ch not in (1, 2):
        tmp_resampled = wav_path.with_suffix(".48k_tmp.wav")
        subprocess.run(
            [
                "/usr/bin/ffmpeg",
                "-y",
                "-i",
                str(wav_path),
                "-ar",
                str(target_sr),
                "-ac",
                "2",
                "-sample_fmt",
                "s16",
                str(tmp_resampled),
            ],
            check=True,
            capture_output=True,
        )
        read_target = tmp_resampled
    else:
        read_target = wav_path

    try:
        with wave.open(str(read_target), "rb") as wf:
            n_frames = wf.getnframes()
            ch = wf.getnchannels()
            raw = wf.readframes(n_frames)
        pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if ch == 1:
            stereo = np.stack([pcm, pcm], axis=1)
        else:
            stereo = pcm.reshape(-1, ch)[:, :2]
        return stereo
    finally:
        if read_target != wav_path and read_target.exists():
            read_target.unlink()


def _trim_leading_trailing_silence(stereo: np.ndarray, sr: int, thresh: float = 0.004) -> np.ndarray:
    """Trim leading/trailing silence from TTS WAV so cue timing (`speech_start_sec`) is exact."""
    peak_env = np.max(np.abs(stereo), axis=1)
    idx = np.where(peak_env > thresh)[0]
    if len(idx) == 0:
        return stereo
    pad = int(0.06 * sr)
    i0 = max(0, int(idx[0]) - pad)
    i1 = min(len(stereo), int(idx[-1]) + pad)
    return stereo[i0:i1]


def mix_segment_master_wav(
    music_wav: Path,
    narration_wav: Path | None,
    master_wav_out: Path,
    duration_sec: float,
    speech_start_sec: float = 4.50,
    music_gain: float = 0.34,
    duck_ratio: float = 0.56,
    voice_gain: float = 0.92,
    fade_in_sec: float = 1.60,
    fade_out_sec: float = 2.80,
    sample_rate: int = 48000,
) -> dict[str, float]:
    """Combine `timidity` choir/instrumental score with sparse narration at `speech_start_sec`."""
    total_samples = round(duration_sec * sample_rate)
    music = _read_wav_float_stereo(music_wav, target_sr=sample_rate)

    if len(music) < total_samples:
        pad = np.zeros((total_samples - len(music), 2), dtype=np.float32)
        music = np.vstack([music, pad])
    else:
        music = music[:total_samples]

    # Normalize music peak gently before applying `music_gain` so soundfont velocity stays predictable
    m_peak = float(np.max(np.abs(music)))
    if m_peak > 1e-4:
        music = music * (0.85 / m_peak)

    # Cosine fade-in and fade-out envelope on music
    env = np.ones(total_samples, dtype=np.float32) * music_gain
    n_in = min(total_samples, round(fade_in_sec * sample_rate))
    if n_in > 0:
        t_in = np.linspace(0.0, math.pi, n_in, dtype=np.float32)
        env[:n_in] *= 0.5 * (1.0 - np.cos(t_in))
    n_out = min(total_samples, round(fade_out_sec * sample_rate))
    if n_out > 0:
        t_out = np.linspace(0.0, math.pi, n_out, dtype=np.float32)
        env[-n_out:] *= 0.5 * (1.0 + np.cos(t_out))

    voice_track = np.zeros((total_samples, 2), dtype=np.float32)
    speech_dur_sec = 0.0

    if narration_wav is not None and narration_wav.exists():
        raw_voice = _read_wav_float_stereo(narration_wav, target_sr=sample_rate)
        trimmed_voice = _trim_leading_trailing_silence(raw_voice, sample_rate)
        v_peak = float(np.max(np.abs(trimmed_voice)))
        if v_peak > 1e-4:
            trimmed_voice = trimmed_voice * (voice_gain / v_peak)

        start_idx = round(speech_start_sec * sample_rate)
        end_idx = min(total_samples, start_idx + len(trimmed_voice))
        copy_len = max(0, end_idx - start_idx)
        speech_dur_sec = copy_len / float(sample_rate)

        if copy_len > 0:
            voice_track[start_idx:end_idx] = trimmed_voice[:copy_len]

            # Smooth cosine ducking curve around speech window (0.65s pre-duck, 0.95s bloom release)
            duck_curve = np.ones(total_samples, dtype=np.float32)
            ramp_down = int(0.65 * sample_rate)
            ramp_up = int(0.95 * sample_rate)
            d0 = max(0, start_idx - ramp_down)
            d1 = start_idx
            u0 = end_idx
            u1 = min(total_samples, end_idx + ramp_up)

            duck_curve[d1:u0] = duck_ratio
            if d1 > d0:
                c = 0.5 * (1.0 + np.cos(np.linspace(0.0, math.pi, d1 - d0, dtype=np.float32)))
                duck_curve[d0:d1] = duck_ratio + (1.0 - duck_ratio) * c
            if u1 > u0:
                c = 0.5 * (1.0 - np.cos(np.linspace(0.0, math.pi, u1 - u0, dtype=np.float32)))
                duck_curve[u0:u1] = duck_ratio + (1.0 - duck_ratio) * c

            env *= duck_curve

    mixed = music * env[:, None] + voice_track
    # Soft limiter guard so peaks never clip 0 dBFS
    peak = float(np.max(np.abs(mixed)))
    if peak > 0.96:
        mixed *= 0.96 / peak

    pcm16 = np.clip(mixed * 32767.0, -32767, 32767).astype(np.int16)
    master_wav_out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(master_wav_out), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16.tobytes())

    return {
        "duration_sec": duration_sec,
        "speech_start_sec": speech_start_sec,
        "speech_end_sec": round(speech_start_sec + speech_dur_sec, 3),
        "speech_dur_sec": round(speech_dur_sec, 3),
        "post_speech_flight_sec": round(duration_sec - (speech_start_sec + speech_dur_sec), 3),
    }
