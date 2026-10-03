# Soundboard LPD8

Soundboard ultraliviano en Python controlado por un **AKAI LPD8 / LPD8 mk2**.

- **Pads 1–8** → reproducen `sounds/1.wav` … `sounds/8.wav` (one-shot, o modo hold opcional)
- **Knobs 1–8** → volumen en vivo del pad correspondiente (CC 0–127 → 0.0–1.0)

Creado por **Adolfo Rosas** ([@ahrsml](https://github.com/ahrsml)).

## Requisitos

- Windows (probado en Windows 11). También debería funcionar en macOS/Linux ejecutando los `.py` directamente.
- Python 3.8 o superior ([python.org](https://www.python.org/downloads/))
- Dependencias: `python-rtmidi` (MIDI) y `pygame` (audio)

## Instalación

**Opción rápida (Windows):** hacer doble clic en `soundboard.bat`. La primera vez crea un entorno virtual (`.venv`) e instala las dependencias automáticamente.

**Instalación manual:**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Sonidos

Los archivos de audio van en la carpeta `sounds/` con estos nombres: `1.wav` … `8.wav` (también se aceptan `01.wav`, `.ogg` y `.mp3`).
Si falta alguno, el programa muestra un aviso en la consola y ese pad queda en silencio.

## Uso

### 1. Diagnóstico MIDI (`midi_monitor.bat`)

```powershell
.\.venv\Scripts\python.exe midi_monitor.py          # detecta el LPD8 automáticamente
.\.venv\Scripts\python.exe midi_monitor.py --list   # lista los puertos MIDI
.\.venv\Scripts\python.exe midi_monitor.py 1        # abre un puerto por su índice
```

Muestra cada mensaje MIDI recibido (Note On/Off, CC, Program Change). Sirve para identificar los números de nota y CC del preset cargado, ya que estos dependen de la configuración del LPD8.

### 2. Soundboard (`soundboard.bat`)

```powershell
.\.venv\Scripts\python.exe soundboard.py             # detecta el LPD8 automáticamente
.\.venv\Scripts\python.exe soundboard.py --devices   # lista las salidas de audio
```

Ctrl+C cierra el puerto MIDI y el audio de forma limpia.

## Mapeo por defecto (preset de fábrica del LPD8 mk2)

| Pad/Knob | Nota del pad (canal 10) | CC del knob (canal 1) |
|---------:|:-----------------------:|:---------------------:|
| 1 | 36 | 70 |
| 2 | 37 | 71 |
| 3 | 38 | 72 |
| 4 | 39 | 73 |
| 5 | 40 | 74 |
| 6 | 41 | 75 |
| 7 | 42 | 76 |
| 8 | 43 | 77 |

Si el preset es distinto, ejecutar `midi_monitor.py` y actualizar `PAD_NOTES` / `KNOB_CCS` al inicio de `soundboard.py`.

## Configuración (al inicio de `soundboard.py`)

- `AUDIO_DEVICE` → parte del nombre de la salida de audio (por ejemplo `"ZOOM"` o `"Realtek"`). `None` usa la salida predeterminada del sistema, que también se usa si no se encuentra el dispositivo indicado. Driver: SDL2 (WASAPI en modo compartido en Windows).
- `HOLD_MODE = True` → el sonido se reproduce solo mientras se mantiene presionado el pad (`HOLD_LOOP = True` para que se repita).
- `DEFAULT_VOLUME` → volumen inicial de cada pad hasta que se mueve su knob (el LPD8 no informa la posición de los knobs al iniciar).
- `BUFFER_SIZE` → un valor menor reduce la latencia; un valor mayor (por ejemplo 1024) evita cortes de audio.

## Notas

- El LPD8 debe estar en modo **PAD** (no CC ni PROG CHANGE) para que los pads envíen notas.
- Cualquier otro programa que use el LPD8 (DAW, etc.) debe cerrarse antes de ejecutar los scripts.

## Licencia

[MIT](LICENSE) © 2026 Adolfo Rosas ([@ahrsml](https://github.com/ahrsml))
