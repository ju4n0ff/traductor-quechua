import os
import ctranslate2
import transformers
from src.utils.config import NLLB_CT2_DIR, QUE_SRC, SPA_SRC
from src.core.lang_detect import LanguageDetector


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

    def translate(self, text: str, source_lang: str | None = None, direction: str | None = None) -> str:
        self._ensure_model()

        if direction == "qu_to_es":
            src_lang, tgt_lang = QUE_SRC, SPA_SRC
        elif direction == "es_to_qu":
            src_lang, tgt_lang = SPA_SRC, QUE_SRC
        else:
            detected = source_lang or self._detect_lang(text)
            src_lang = QUE_SRC if detected == "qu" else SPA_SRC
            tgt_lang = SPA_SRC if detected == "qu" else QUE_SRC

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
        result = self._tokenizer.decode(output_ids, skip_special_tokens=True)
        return result