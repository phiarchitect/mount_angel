"""Assemble all 8 Mount Angel Abbey Library Unfolding segments into mount_angel_unfolding.mp4."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SEGMENTS = [
    "seg01_dawn_circuit/seg01_dawn_circuit.mp4",
    "seg02_bare_hill_and_sweep/seg02_bare_hill_and_sweep.mp4",
    "seg03_concrete_genesis/seg03_concrete_genesis.mp4",
    "seg04_sun_and_seasons/seg04_sun_and_seasons.mp4",
    "seg05_section_of_light/seg05_section_of_light.mp4",
    "seg06_entering_the_fan/seg06_entering_the_fan.mp4",
    "seg07_the_reading_well/seg07_the_reading_well.mp4",
    "seg08_ascent_and_dusk/seg08_ascent_and_dusk.mp4",
]


def main() -> None:
    missing = [s for s in SEGMENTS if not (ROOT / s).exists()]
    if missing:
        raise FileNotFoundError(f"Missing segment MP4s: {missing}")

    out_mp4 = ROOT / "mount_angel_unfolding.mp4"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
        for rel in SEGMENTS:
            abs_p = (ROOT / rel).resolve().as_posix()
            tf.write(f"file '{abs_p}'\n")
        list_path = Path(tf.name)

    try:
        subprocess.run(
            [
                "/usr/bin/ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(out_mp4),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        list_path.unlink(missing_ok=True)

    probe = subprocess.run(
        [
            "/usr/bin/ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames",
            "-of",
            "json",
            str(out_mp4),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    info = json.loads(probe.stdout)
    print(f"Assembled complete Unfolding film: {out_mp4}")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
