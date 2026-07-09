import os
import numpy as np
from faster_whisper import WhisperModel
from src.utils.config import WHISPER_MODEL_SIZE, WHISPER_MODEL_DIR, ASR_LANGUAGE


class SpeechRecognizer:
    def __init__(self):
        self._model: WhisperModel | None = None
        self._model_size = WHISPER_MODEL_SIZE

    def _ensure_model(self):
        if self._model is not None:
            return
        os.makedirs(WHISPER_MODEL_DIR, exist_ok=True)
        self._model = WhisperModel(
            self._model_size,
            download_root=str(WHISPER_MODEL_DIR),
            device="cpu",
            compute_type="int8",
        )

    def transcribe(self, audio: np.ndarray, language: str | None = None) -> tuple[str | None, str | None]:
        self._ensure_model()
        lang = language if language is not None else ASR_LANGUAGE

        segments, info = self._model.transcribe(
            audio,
            language=lang,
            beam_size=3,
            vad_filter=False,
            without_timestamps=True,
        )

        detected_lang = info.language if info else lang
        text = " ".join(seg.text for seg in segments)
        result = text.strip() or None
        return result, detected_lang
