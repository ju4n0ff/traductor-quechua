import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"
BLOCK_SIZE = 8000  # 0.5s at 16kHz

# Whisper ASR
WHISPER_MODEL_SIZE = "tiny"  # tiny, base, small, medium, large-v3
WHISPER_MODEL_DIR = MODELS_DIR / "whisper"
ASR_LANGUAGE = None  # None = auto-detect (Whisper no soporta 'qu' como código)

# NLLB Translation
NLLB_CT2_REPO_ID = "entai2965/nllb-200-distilled-600M-ctranslate2"
NLLB_CT2_DIR = MODELS_DIR / "nllb-ct2-int8"
# Language codes for NLLB / FLORES-200:
QUE_SRC = "quy_Latn"   # Southern Quechua (Ayacucho)
SPA_SRC = "spa_Latn"   # Spanish

# TTS
TTS_VOICE_ES = "es-PE-AlexNeural"  # Peruvian Spanish voice (male)
TTS_VOICE_QU = "es-PE-CamilaNeural"  # Peruvian Spanish voice (female, for Quechua)
TTS_SPEED = "+0%"  # Normal speed

# App settings
APP_TITLE = "Traductor Quechua — Español"
APP_SIZE = "900x600"
APP_THEME = "green"  # customtkinter theme
RECORD_BUTTON_SIZE = 100
