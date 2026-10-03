"""Monitor MIDI de diagnóstico para el AKAI LPD8.

Imprime todos los mensajes MIDI entrantes (Note On/Off, CC, Program Change, etc.)
para descubrir los números exactos de nota y CC que manda tu LPD8 con el preset actual.

Uso:
    python midi_monitor.py            # elige automáticamente el puerto que contenga "LPD8"
    python midi_monitor.py --list     # lista los puertos MIDI de entrada y sale
    python midi_monitor.py 1          # abre el puerto con índice 1

Ctrl+C para salir (cierra el puerto limpiamente).

Autor: Adolfo Rosas (GitHub: @ahrsml) - https://github.com/ahrsml
Licencia: MIT
"""
import sys
import time

import rtmidi

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_name(n):
    # Convención MIDI: nota 60 = C4
    return "{}{}".format(NOTE_NAMES[n % 12], n // 12 - 1)


def describe(msg):
    status = msg[0]
    kind = status & 0xF0
    ch = (status & 0x0F) + 1
    d1 = msg[1] if len(msg) > 1 else None
    d2 = msg[2] if len(msg) > 2 else None

    if kind == 0x90 and d2 > 0:
        return "NOTE ON   ch={:<2} note={:<3} ({:<4}) velocity={}".format(ch, d1, note_name(d1), d2)
    if kind == 0x80 or (kind == 0x90 and d2 == 0):
        return "NOTE OFF  ch={:<2} note={:<3} ({:<4}) velocity={}".format(ch, d1, note_name(d1), d2)
    if kind == 0xB0:
        return "CC        ch={:<2} cc={:<3}             value={}".format(ch, d1, d2)
    if kind == 0xC0:
        return "PROG CHG  ch={:<2} program={}".format(ch, d1)
    if kind == 0xA0:
        return "POLY AT   ch={:<2} note={:<3} ({:<4}) pressure={}".format(ch, d1, note_name(d1), d2)
    if kind == 0xD0:
        return "CHAN AT   ch={:<2} pressure={}".format(ch, d1)
    if kind == 0xE0:
        return "PITCHBEND ch={:<2} value={}".format(ch, (d2 << 7 | d1) - 8192)
    return "OTRO      bytes={}".format(" ".join("{:02X}".format(b) for b in msg))


def pick_port(midi_in, args):
    ports = midi_in.get_ports()
    if not ports:
        print("No se encontraron puertos MIDI de entrada. ¿Está conectado el LPD8?")
        return None

    print("Puertos MIDI de entrada:")
    for i, name in enumerate(ports):
        print("  [{}] {}".format(i, name))

    if "--list" in args:
        return None

    numeric = [a for a in args if a.isdigit()]
    if numeric:
        idx = int(numeric[0])
        if idx >= len(ports):
            print("Índice {} fuera de rango.".format(idx))
            return None
        return idx

    for i, name in enumerate(ports):
        if "LPD8" in name.upper():
            return i

    print("No encontré un puerto con 'LPD8' en el nombre. Usá: python midi_monitor.py <índice>")
    return None


def main():
    midi_in = rtmidi.MidiIn()
    try:
        idx = pick_port(midi_in, sys.argv[1:])
        if idx is None:
            return

        midi_in.open_port(idx)
        # Ignorar sysex, timing clock y active sensing (ruido que no nos interesa)
        midi_in.ignore_types(sysex=True, timing=True, active_sense=True)
        print("\nEscuchando en: {}".format(midi_in.get_port_name(idx)))
        print("Apretá cada pad (1 a 8) y mové cada knob (1 a 8). Ctrl+C para salir.\n")

        while True:
            event = midi_in.get_message()
            if event:
                msg, _delta = event
                print("{}   raw=[{}]".format(describe(msg), " ".join("{:02X}".format(b) for b in msg)))
            else:
                time.sleep(0.001)
    except KeyboardInterrupt:
        print("\nSaliendo...")
    finally:
        midi_in.close_port()
        del midi_in
        print("Puerto MIDI cerrado.")


if __name__ == "__main__":
    main()
