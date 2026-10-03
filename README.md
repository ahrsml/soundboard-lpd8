# Soundboard LPD8

Soundboard ultraliviano en Python controlado por un **AKAI LPD8 / LPD8 mk2**.

- **Pads 1–8** → disparan `sounds/1.wav` … `sounds/8.wav` (one-shot, o modo hold opcional)
- **Knobs 1–8** → volumen en vivo del pad correspondiente (CC 0–127 → 0.0–1.0)

Hecho por **Adolfo Rosas** ([@ahrsml](https://github.com/ahrsml)).

## Requisitos

- Windows (probado en Windows 11). Debería funcionar en macOS/Linux corriendo los `.py` directamente.
- Python 3.8 o superior ([python.org](https://www.python.org/downloads/))
- Dependencias: `python-rtmidi` (MIDI) y `pygame` (audio)

## Instalación

**Forma fácil (Windows):** doble clic en `soundboard.bat`. La primera vez crea un entorno virtual (`.venv`) e instala las dependencias.

**Manual:**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Sonidos

Poné los archivos en `sounds/` con estos nombres: `1.wav` … `8.wav` (también sirve `01.wav`, y `.ogg` / `.mp3`).
Si falta alguno, el script avisa por consola y ese pad queda mudo.

## Uso

### 1. Diagnóstico MIDI (`midi_monitor.bat`)

```powershell
.\.venv\Scripts\python.exe midi_monitor.py          # auto-detecta el LPD8
.\.venv\Scripts\python.exe midi_monitor.py --list   # lista los puertos
.\.venv\Scripts\python.exe midi_monitor.py 1        # puerto por índice
```

Imprime cada mensaje MIDI (Note On/Off, CC, Program Change). Usalo para descubrir los números de nota/CC de tu preset: dependen del preset cargado en el LPD8.

### 2. Soundboard (`soundboard.bat`)

```powershell
.\.venv\Scripts\python.exe soundboard.py             # auto-detecta el LPD8
.\.venv\Scripts\python.exe soundboard.py --devices   # lista las salidas de audio
```

Ctrl+C cierra el puerto MIDI y el audio limpiamente.

## Mapeo por defecto (preset de fábrica del LPD8 mk2)

| Pad/Knob | Nota pad (canal 10) | CC knob (canal 1) |
|---------:|:-------------------:|:-----------------:|
| 1 | 36 | 70 |
| 2 | 37 | 71 |
| 3 | 38 | 72 |
| 4 | 39 | 73 |
| 5 | 40 | 74 |
| 6 | 41 | 75 |
| 7 | 42 | 76 |
| 8 | 43 | 77 |

Si tu preset es distinto, corré `midi_monitor.py` y actualizá `PAD_NOTES` / `KNOB_CCS` arriba de `soundboard.py`.

## Configuración (arriba de `soundboard.py`)

- `AUDIO_DEVICE` → parte del nombre de la salida de audio (ej. `"ZOOM"`, `"Realtek"`). `None` = salida predeterminada del sistema. Si no se encuentra, usa la predeterminada. Driver: SDL2 (WASAPI en modo compartido en Windows).
- `HOLD_MODE = True` → el sonido suena solo mientras mantenés el pad (`HOLD_LOOP = True` para que se repita).
- `DEFAULT_VOLUME` → volumen inicial de cada pad hasta que muevas su knob (el LPD8 no informa la posición de los knobs al arrancar).
- `BUFFER_SIZE` → bajalo para menos latencia, subilo (1024) si hay cortes.

## Notas

- El LPD8 tiene que estar en modo **PAD** (no CC ni PROG CHANGE) para que los pads manden notas.
- Cerrá cualquier otro programa que esté usando el LPD8 (DAW, etc.) antes de correr los scripts.

## Licencia

[MIT](LICENSE) © 2026 Adolfo Rosas ([@ahrsml](https://github.com/ahrsml))
