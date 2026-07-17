# AGENTS.md - Traductor Quechua-Español

## Project Overview
Desktop app for Quechua ↔ Spanish translation with speech-to-text, text translation, and text-to-speech. Windows-only (uses `winsound`, `edge-tts`).

## Architecture
```
src/
├── main.py                    # Entry point → TranslatorApp
├── ui/
│   ├── app.py                 # Main window, UI, processing threads
│   └── widgets.py             # RecordButton, StatusBar
├── core/
│   ├── asr.py                 # SpeechRecognizer (faster-whisper tiny)
│   ├── translator.py          # TextTranslator (NLLB 600M)
│   ├── tts.py                 # TextToSpeech (edge-tts + ffmpeg)
│   └── audio.py               # AudioRecorder (sounddevice)
└── utils/
    └── config.py              # All constants: paths, models, lang codes
models/
├── whisper/                   # faster-whisper tiny (local)
└── nllb/                      # facebook/nllb-200-distilled-600M (local)
```

## Key Dependencies
```
customtkinter>=6.0.0
faster-whisper>=1.2.1
sounddevice>=0.5.5
soundfile>=0.14.0
numpy>=2.5.1
transformers>=5.13.0
torch>=2.12.1
edge-tts>=7.2.8
```

## How to Run
```bash
# Activate venv
.\venv\Scripts\activate
# Run app
python -m src.main
```

## Models
Models are stored locally in `models/`:
- `models/whisper/` - faster-whisper tiny (ASR)
- `models/nllb/` - NLLB 600M (translation)

Config in `src/utils/config.py`:
- `WHISPER_MODEL_SIZE = "tiny"`
- `NLLB_MODEL_NAME = "facebook/nllb-200-distilled-600M"`
- Quechua code: `quy_Latn` (NLLB), Spanish: `spa_Latn`
- TTS voices: `es-PE-AlexNeural` (ES), `es-PE-CamilaNeural` (QU)

## Key Implementation Details

**ASR (src/core/asr.py):**
- Uses `faster_whisper.WhisperModel` with `device="cpu"`, `compute_type="int8"`
- Language auto-detect (`ASR_LANGUAGE = None`); Whisper doesn't support `qu` code

**Translation (src/core/translator.py):**
- NLLB via transformers; lazy model loading
- Language detection: simple Quechua wordlist match (≥1 match = Quechua)
- Forced BOS token for target language

**TTS (src/core/tts.py):**
- `edge_tts` → MP3 → ffmpeg → WAV (16kHz mono) → `winsound.PlaySound`
- ffmpeg auto-discovered from PATH or LOCALAPPDATA

**Audio Recording (src/core/audio.py):**
- `sounddevice.InputStream` at 16kHz mono float32
- Thread-safe with lock; returns flattened numpy array + peak amplitude

**UI (src/ui/app.py):**
- `customtkinter` dark theme, green accent
- Two modes: Voice (record→ASR→translate→TTS) and Text (type→translate)
- Background processing thread + queue for ASR/translation
- Task ID tracking to discard stale audio results

## Configuration (src/utils/config.py)
All constants in one file:
- Paths: `BASE_DIR`, `MODELS_DIR`, `CACHE_DIR`
- Audio: 16kHz, mono, float32, 8000 block size
- Models: WHISPER_MODEL_SIZE, NLLB_MODEL_NAME, language codes
- TTS voices, app title/size/theme

## Development Notes
- Windows-only (winsound, edge-tts voice selection)
- Models download on first run to `models/` via transformers/faster-whisper cache
- ffmpeg required for TTS (auto-found in PATH or LOCALAPPDATA)
- No tests, lint, or typecheck configured
- Python 3.14 (venv shows 3.14)

## Running the App
```powershell
cd C:\Users\xlol5\Desktop\Traductor
.\venv\Scripts\activate
python -m src.main
```

## Common Issues
- **ffmpeg not found**: Install ffmpeg and add to PATH, or it will try LOCALAPPDATA/ffmpegio
- **Model download**: First run downloads ~1.2GB (whisper tiny + NLLB 600M) to `models/`
- **Audio device**: Uses default input device; check `AudioRecorder.get_devices()` for options
- **Quechua detection**: Simple wordlist match in `TextTranslator._detect_lang()` - may need tuning for dialect coverage