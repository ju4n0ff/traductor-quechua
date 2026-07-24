# Traductor Quechua-Español

Windows-only desktop app (customtkinter) for Quechua ↔ Spanish translation with STT (faster-whisper tiny int8), NLLB 600M via CTranslate2 int8, and TTS (edge-tts → ffmpeg → winsound).

## Run

```powershell
.\venv\Scripts\activate
python -m src.main
```

## One-time setup

```powershell
python scripts/download_nllb_ct2.py   # requires huggingface_hub (not in requirements.txt)
```

First run also auto-downloads whisper tiny (~150MB) to `models/whisper/`.

## Requirements

`requirements.txt` deliberately omits torch (CTranslate2 does CPU inference directly). `transformers` is used only for the NLLB tokenizer. ffmpeg must be on PATH or at `%LOCALAPPDATA%\ffmpegio\ffmpeg-downloader\ffmpeg\bin\ffmpeg.exe`.

## Architecture

```
src/
├── main.py                  # → TranslatorApp
├── ui/
│   ├── app.py               # Main window, processing thread, queue
│   ├── widgets.py           # Card, EyebrowLabel, Badge, RecordButton, StatusBar, LangToggle
│   └── theme.py             # Dark color palette
├── core/
│   ├── asr.py               # SpeechRecognizer (faster-whisper tiny, CPU int8)
│   ├── translator.py        # TextTranslator (CTranslate2 NLLB int8)
│   ├── lang_detect.py       # Quechua detection via suffix heuristics
│   ├── phrasebook.py        # Hardcoded common phrases — NOT wired anywhere (dead code)
│   ├── tts.py               # TextToSpeech (edge-tts → MP3 → ffmpeg → WAV → winsound)
│   └── audio.py             # AudioRecorder (sounddevice, 16kHz mono)
└── utils/
    ├── config.py            # All constants
    └── i18n.py              # ES/QU UI language strings + direction code helpers
scripts/
└── download_nllb_ct2.py    # Downloads pre-converted CTranslate2 model from HF Hub
```

## Gotchas

- **Translation engine** is CTranslate2 int8, NOT raw transformers/PyTorch. Model from `entai2965/nllb-200-distilled-600M-ctranslate2` — separate download step required.
- **Language detection:** suffix-based heuristic in `lang_detect.py`. Strong suffixes (4+ chars) need ≥1 hit; weak suffixes (3 chars) need ≥2 hits.
- **Phrasebook** (`core/phrasebook.py`) is dead code — never called by the translation or voice pipelines.
- **Audio blocksize:** `AudioRecorder` hardcodes `blocksize=2048`; `BLOCK_SIZE=8000` in config is unused.
- **Config unused:** `CACHE_DIR`, `BLOCK_SIZE` in `config.py` are defined but never referenced at runtime.
- **ASR language auto-detect:** `ASR_LANGUAGE = None` in config (Whisper auto-detects language). Whisper doesn't support `qu` language code, so auto-detect may be unreliable for Quechua.
- **Windows-only:** `winsound`, `subprocess.CREATE_NO_WINDOW`, edge-tts voice selection.
- **UI i18n:** `LangToggle` widget switches UI labels between ES and QU via `src/utils/i18n.py`. Not related to translation direction.
- **Model dirs in `.gitignore`** (`models/`, `venv/`). Must exist at runtime.
- **No tests, lint, typecheck, or CI configured.**
