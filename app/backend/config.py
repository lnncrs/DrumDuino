"""Caminhos usados pelo backend."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

FLUIDSYNTH_DLL = os.getenv("FLUIDSYNTH_DLL", "")
SOUNDFONT = ROOT / "soundfonts" / "GeneralUser-GS.sf2"


def drum_notes():
    notes = {}
    for sensor in range(8):
        value = os.getenv(f"DRUM_A{sensor}", "38" if sensor == 0 else "").strip()
        if value:
            note = int(value)
            if not 0 <= note <= 127:
                raise ValueError(f"DRUM_A{sensor} deve estar entre 0 e 127.")
            notes[sensor] = note
    return notes
