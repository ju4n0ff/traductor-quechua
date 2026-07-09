import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from src.utils.config import NLLB_MODEL_NAME, NLLB_MODEL_DIR, QUE_SRC, SPA_SRC


class TextTranslator:
    def __init__(self):
        self._tokenizer: AutoTokenizer | None = None
        self._model: AutoModelForSeq2SeqLM | None = None
        self._model_name = NLLB_MODEL_NAME

    def _ensure_model(self):
        if self._model is not None:
            return
        os.makedirs(NLLB_MODEL_DIR, exist_ok=True)
        self._tokenizer = AutoTokenizer.from_pretrained(
            self._model_name,
            cache_dir=str(NLLB_MODEL_DIR),
        )
        self._model = AutoModelForSeq2SeqLM.from_pretrained(
            self._model_name,
            cache_dir=str(NLLB_MODEL_DIR),
        )

    def _detect_lang(self, text: str) -> str:
        quechua_words = {
            "allin", "sumaq", "runa", "simi", "yacha", "wasi", "mama",
            "yaya", "tayta", "ima", "kay", "kuna", "ñan", "punchaw",
            "tuta", "inti", "killa", "yaku", "mikuy", "puñuy",
            "rimay", "uyariy", "rikuy", "hamuy", "ripuy", "tiyay",
            "imaynalla", "allillanchu", "añay", "askha", "huk",
        }
        lower = text.lower().split()
        matches = sum(1 for w in lower if w in quechua_words)
        if matches >= 1:
            return "qu"
        return "es"

    def translate(self, text: str, source_lang: str | None = None) -> str:
        self._ensure_model()
        detected = source_lang or self._detect_lang(text)
        src_lang = QUE_SRC if detected == "qu" else SPA_SRC
        tgt_lang = SPA_SRC if detected == "qu" else QUE_SRC

        self._tokenizer.src_lang = src_lang
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        tgt_lang_id = self._tokenizer.convert_tokens_to_ids(tgt_lang)
        translated = self._model.generate(
            **inputs,
            forced_bos_token_id=tgt_lang_id,
            max_length=512,
            num_beams=3,
        )
        result = self._tokenizer.decode(translated[0], skip_special_tokens=True)
        return result
