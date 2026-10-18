"""Reprodução das batidas com FluidSynth."""

import os
import re
from pathlib import Path

from app.backend import config


class Audio:
    def __init__(self):
        self.synth = None
        self.error = ""
        self.notes = {}
        self.dll_directory = None

    def start(self):
        try:
            self.notes = config.drum_notes()
            if os.name == "nt":
                dll = Path(config.FLUIDSYNTH_DLL)
                if not dll.is_file():
                    raise FileNotFoundError("Confira FLUIDSYNTH_DLL no arquivo .env.")
                # O Windows também precisa encontrar as dependências da DLL.
                self.dll_directory = os.add_dll_directory(str(dll.parent))
                os.environ["PATH"] = (
                    str(dll.parent) + os.pathsep + os.environ.get("PATH", "")
                )

            import fluidsynth

            if not config.SOUNDFONT.is_file():
                raise FileNotFoundError(
                    "SoundFont não encontrada em soundfonts/GeneralUser-GS.sf2."
                )
            self.synth = fluidsynth.Synth(gain=0.4)
            soundfont = self.synth.sfload(str(config.SOUNDFONT))
            if soundfont < 0:
                raise RuntimeError("Não foi possível carregar a SoundFont.")
            # Canal 10 (índice 9), banco de percussão 128, kit padrão 0.
            if self.synth.program_select(9, soundfont, 128, 0) != 0:
                raise RuntimeError("Kit de bateria não encontrado na SoundFont.")
            # Abrimos somente a saída de áudio; não precisamos de entrada MIDI.
            self.synth.audio_driver = fluidsynth.new_fluid_audio_driver(
                self.synth.settings, self.synth.synth
            )
            if not self.synth.audio_driver:
                raise RuntimeError(
                    "Não foi possível abrir a saída de áudio do computador."
                )
            self.error = ""
        except Exception as exc:
            self.error = f"Áudio indisponível: {exc}"
            self.close()

    def hit(self, message):
        match = re.fullmatch(r"HIT,([0-9]+),([0-9]+)", message)
        if not self.synth or not match:
            return None
        if any(len(value) > 4 for value in match.groups()):
            return None
        sensor, reading = map(int, match.groups())
        if sensor not in self.notes or not 0 <= reading <= 1023:
            return None
        note = self.notes[sensor]
        try:
            # A nota vem do .env; a intensidade permanece fixa neste teste.
            self.synth.noteoff(9, note)
            if self.synth.noteon(9, note, 100) != 0:
                raise RuntimeError("Falha ao reproduzir a batida.")
            return note
        except Exception as exc:
            self.error = f"Áudio interrompido: {exc}"
            self.close()
            return None

    def stop_note(self, note):
        if self.synth:
            self.synth.noteoff(9, note)

    def close(self):
        if self.synth:
            self.synth.delete()
            self.synth = None
        if self.dll_directory:
            self.dll_directory.close()
            self.dll_directory = None

    def status(self):
        return {
            "ready": self.synth is not None,
            "error": self.error,
            "mapping": {f"A{sensor}": note for sensor, note in self.notes.items()},
        }
