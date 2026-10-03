"""Soundboard controlado por AKAI LPD8 mk2.

- 8 pads  -> disparan sounds/1.wav ... sounds/8.wav (un canal de audio por pad)
- 8 knobs -> volumen en vivo de cada pad (CC 0-127 -> 0.0-1.0)

Uso:
    python soundboard.py        # abre automáticamente el puerto que contenga "LPD8"
    python soundboard.py 1      # o el puerto MIDI con ese índice

Ctrl+C para salir.

Autor: Adolfo Rosas (GitHub: @ahrsml) - https://github.com/ahrsml
Licencia: MIT
"""
import os
import sys
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402
import rtmidi  # noqa: E402

# --- Configuración ----------------------------------------------------------

# Mapeo confirmado con midi_monitor.py (preset actual del LPD8 mk2).
# Índice 0..7 = pad/knob 1..8.
PAD_NOTES = [36, 37, 38, 39, 40, 41, 42, 43]   # Note On/Off, canal 10
KNOB_CCS = [70, 71, 72, 73, 74, 75, 76, 77]    # Control Change, canal 1

# Modo de disparo:
#   False -> one-shot: el sample suena entero al tocar el pad (se ignora el Note Off).
#   True  -> hold: suena solo mientras mantenés el pad; al soltarlo se corta.
HOLD_MODE = False
HOLD_FADEOUT_MS = 30   # fade corto al soltar en modo hold, evita el "click"
HOLD_LOOP = False      # en modo hold: True = el sample se repite mientras mantenés el pad

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
SOUND_EXTENSIONS = [".wav", ".ogg", ".mp3"]  # se busca 1.wav, 01.wav, 1.ogg, ...

# Salida de audio: parte del nombre del dispositivo (ver lista al arrancar o con --devices).
# None = dispositivo predeterminado de Windows.
AUDIO_DEVICE = "ZOOM"
DEFAULT_VOLUME = 1.0   # volumen inicial hasta que se mueva cada knob

# Audio: buffer chico = menos latencia. Si escuchás cortes/chasquidos, subilo a 1024.
SAMPLE_RATE = 44100
BUFFER_SIZE = 512

# ----------------------------------------------------------------------------

NOTE_TO_PAD = {note: i for i, note in enumerate(PAD_NOTES)}
CC_TO_PAD = {cc: i for i, cc in enumerate(KNOB_CCS)}


class Soundboard:
    def __init__(self):
        device = pick_audio_device()
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, BUFFER_SIZE, devicename=device)
        pygame.mixer.init()
        print("Salida de audio: {}".format(device or "predeterminada de Windows"))
        pygame.mixer.set_num_channels(8)
        pygame.mixer.set_reserved(8)  # los 8 canales son exclusivos de los pads

        self.channels = [pygame.mixer.Channel(i) for i in range(8)]
        self.volumes = [DEFAULT_VOLUME] * 8
        self.sounds = [self._load(i) for i in range(8)]

    def _load(self, pad):
        n = pad + 1
        candidates = [os.path.join(SOUNDS_DIR, name + ext)
                      for name in ("{}".format(n), "{:02d}".format(n))
                      for ext in SOUND_EXTENSIONS]
        path = next((p for p in candidates if os.path.isfile(p)), None)
        if path is None:
            print("[aviso] Pad {}: falta sounds/{}.wav (el pad queda mudo)".format(n, n))
            return None
        try:
            sound = pygame.mixer.Sound(path)
        except pygame.error as e:
            print("[aviso] Pad {}: no se pudo cargar {}: {}".format(pad + 1, path, e))
            return None
        print("Pad {}: {} ({:.2f}s)".format(pad + 1, os.path.basename(path), sound.get_length()))
        return sound

    def pad_on(self, pad):
        sound = self.sounds[pad]
        if sound is None:
            return
        ch = self.channels[pad]
        loops = -1 if (HOLD_MODE and HOLD_LOOP) else 0
        ch.play(sound, loops=loops)  # volver a tocar el pad reinicia el sample
        ch.set_volume(self.volumes[pad])  # re-aplicar: play() puede resetear el volumen del canal

    def pad_off(self, pad):
        if HOLD_MODE:
            self.channels[pad].fadeout(HOLD_FADEOUT_MS)
        # En one-shot el Note Off se ignora: el sample sigue hasta el final.

    def set_volume(self, pad, value):
        vol = value / 127.0
        self.volumes[pad] = vol
        self.channels[pad].set_volume(vol)  # se aplica en vivo aunque ya esté sonando

    def handle_midi(self, event, _data=None):
        msg, _delta = event
        if len(msg) < 3:
            return  # Program Change u otros mensajes cortos: ignorados
        kind = msg[0] & 0xF0
        d1, d2 = msg[1], msg[2]

        if kind == 0x90 and d2 > 0:
            pad = NOTE_TO_PAD.get(d1)
            if pad is not None:
                self.pad_on(pad)
        elif kind == 0x80 or (kind == 0x90 and d2 == 0):
            pad = NOTE_TO_PAD.get(d1)
            if pad is not None:
                self.pad_off(pad)
        elif kind == 0xB0:
            pad = CC_TO_PAD.get(d1)
            if pad is not None:
                self.set_volume(pad, d2)
        # Cualquier otro mensaje (CCs ajenos, aftertouch, etc.) se ignora.

    def close(self):
        pygame.mixer.stop()
        pygame.mixer.quit()


def list_audio_devices():
    from pygame._sdl2 import audio as sdl_audio
    pygame.init()  # get_audio_device_names necesita el subsistema de audio de SDL inicializado
    try:
        return list(sdl_audio.get_audio_device_names(False))
    finally:
        pygame.quit()


def pick_audio_device():
    if not AUDIO_DEVICE:
        return None
    devices = list_audio_devices()
    for name in devices:
        if AUDIO_DEVICE.lower() in name.lower():
            return name
    print("[aviso] No encontré una salida de audio que contenga '{}'. Disponibles:".format(AUDIO_DEVICE))
    for name in devices:
        print("  - {}".format(name))
    print("        Uso la salida predeterminada de Windows.")
    return None


def find_port(midi_in, args):
    ports = midi_in.get_ports()
    numeric = [a for a in args if a.isdigit()]
    if numeric:
        idx = int(numeric[0])
        return idx if idx < len(ports) else None
    for i, name in enumerate(ports):
        if "LPD8" in name.upper():
            return i
    return None


def main():
    if "--devices" in sys.argv:
        print("Salidas de audio:")
        for name in list_audio_devices():
            print("  - {}".format(name))
        return

    midi_in = rtmidi.MidiIn()
    board = None
    try:
        idx = find_port(midi_in, sys.argv[1:])
        if idx is None:
            print("No se encontró el LPD8. Puertos disponibles:")
            for i, name in enumerate(midi_in.get_ports()):
                print("  [{}] {}".format(i, name))
            print("Usá: python soundboard.py <índice>")
            return

        board = Soundboard()
        midi_in.open_port(idx)
        midi_in.ignore_types(sysex=True, timing=True, active_sense=True)
        # Callback: los mensajes se procesan apenas llegan (menor latencia que hacer polling)
        midi_in.set_callback(board.handle_midi)

        print("\nSoundboard LPD8 - por Adolfo Rosas (github.com/ahrsml)")
        print("Soundboard listo en: {}  (modo: {})".format(
            midi_in.get_port_name(idx), "HOLD" if HOLD_MODE else "ONE-SHOT"))
        print("Ctrl+C para salir.")
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nSaliendo...")
    finally:
        midi_in.cancel_callback()
        midi_in.close_port()
        del midi_in
        if board is not None:
            board.close()
        print("Puerto MIDI y audio cerrados.")


if __name__ == "__main__":
    main()
