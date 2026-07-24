import os
import re
import ctranslate2
import transformers
from src.utils.config import NLLB_CT2_DIR, QUE_SRC, SPA_SRC
from src.core.lang_detect import LanguageDetector
from src.core import phrasebook

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


class TextTranslator:
    """Traductor NLLB-200 vía CTranslate2 (int8, CPU).

    Antes: transformers.AutoModelForSeq2SeqLM en fp32 puro. Con modelos de
    600M parámetros en CPU, esto es lento y usa 2-4x más RAM de lo necesario.
    CTranslate2 es el mismo motor que ya usa faster-whisper, así que no se
    suma tecnología nueva al proyecto. El modelo ya viene pre-convertido
    (ver scripts/download_nllb_ct2.py) — no hace falta convertirlo localmente.
    """

    def __init__(self):
        self._tokenizer: transformers.AutoTokenizer | None = None
        self._translator: ctranslate2.Translator | None = None
        self._lang_detector = LanguageDetector()

    def _ensure_model(self):
        if self._translator is not None:
            return
        if not NLLB_CT2_DIR.is_dir():
            raise FileNotFoundError(
                f"No se encontró el modelo NLLB en {NLLB_CT2_DIR}. "
                "Corré 'python scripts/download_nllb_ct2.py' primero."
            )
        self._tokenizer = transformers.AutoTokenizer.from_pretrained(str(NLLB_CT2_DIR))
        self._translator = ctranslate2.Translator(
            str(NLLB_CT2_DIR),
            device="cpu",
            compute_type="int8",
            inter_threads=1,
            intra_threads=max(1, os.cpu_count() or 1),
        )

    def _detect_lang(self, text: str) -> str:
        return self._lang_detector.detect(text)

    def _translate_one(self, text: str, src_lang: str, tgt_lang: str) -> str:
        self._tokenizer.src_lang = src_lang
        source_tokens = self._tokenizer.convert_ids_to_tokens(
            self._tokenizer(text, truncation=True, max_length=512)["input_ids"]
        )
        results = self._translator.translate_batch(
            [source_tokens],
            target_prefix=[[tgt_lang]],
            beam_size=3,
            max_decoding_length=512,
        )
        output_tokens = results[0].hypotheses[0][1:]
        output_ids = self._tokenizer.convert_tokens_to_ids(output_tokens)
        return self._tokenizer.decode(output_ids, skip_special_tokens=True)

    def translate(self, text: str, source_lang: str | None = None, direction: str | None = None) -> str:
        if direction == "qu_to_es":
            resolved_direction = "qu_to_es"
        elif direction == "es_to_qu":
            resolved_direction = "es_to_qu"
        else:
            detected = source_lang or self._detect_lang(text)
            resolved_direction = "qu_to_es" if detected == "qu" else "es_to_qu"

        # Saludos o Cortesias como "Hola" "Gracias" y asi
        fixed = phrasebook.lookup(text, resolved_direction)
        if fixed is not None:
            return fixed

        self._ensure_model()
        src_lang, tgt_lang = (
            (QUE_SRC, SPA_SRC) if resolved_direction == "qu_to_es" else (SPA_SRC, QUE_SRC)
        )

        # Texto corto
        token_count = len(self._tokenizer(text)["input_ids"])
        if token_count <= 480:
            return self._translate_one(text, src_lang, tgt_lang)

        # Texto largo partiendo de oraciones
        sentences = [s for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
        translated_parts = [self._translate_one(s, src_lang, tgt_lang) for s in sentences]
        return " ".join(translated_parts)
