"""Detección de idioma quechua/español.

Heurístico basado en sufijos quechua distintivos. El quechua es
aglutinante: una raíz se combina con varios sufijos gramaticales
(wasi -> wasiykipi, wasikuna, wasichakuna...), así que buscar la
terminación de la palabra detecta mucho mejor que un wordlist de
raíces exactas como el que había antes.

Los sufijos de 4+ letras (kuna, manta, chka, nchik...) son muy
distintivos y casi no aparecen como terminación real en español, así
que un solo match ya es suficiente señal. Los de 3 letras (wan, paq,
kama, pura) son más cortos y con algo más de riesgo de coincidencia
casual, así que exigen un segundo match para confirmar.
"""

from __future__ import annotations

# Sufijos de 4+ letras: muy distintivos, casi no ocurren como
# terminación real de una palabra española. Un solo match alcanza.
_STRONG_SUFFIXES = (
    "kuna",     # plural
    "manta",    # ablativo "desde/de"
    "chka",     # progresivo
    "nchik",    # 1ra persona plural inclusiva
    "ninchik",
    "ykiku",
    "yki",      # posesivo 2da persona
    "sqa",      # perfecto/reportativo
)

# Sufijos de 3 letras: algo más de riesgo de coincidencia casual,
# se exige un segundo match para contar.
_WEAK_SUFFIXES = (
    "wan",   # instrumental/comitativo "con"
    "paq",   # benefactivo "para"
    "kama",  # "hasta"
    "pura",  # "entre/mutuamente"
    "naku",  # recíproco
    "ñan",   # partícula reportativa/de tópico
)

_PUNCT = ".,;:!?¡¿\"'()"


class LanguageDetector:
    def detect(self, text: str) -> str:
        """Devuelve 'qu' o 'es'."""
        text = text.strip()
        if not text:
            return "es"

        strong_hits = 0
        weak_hits = 0
        for w in text.lower().split():
            stripped = w.strip(_PUNCT)
            if len(stripped) < 4:
                continue
            if any(stripped.endswith(suf) for suf in _STRONG_SUFFIXES):
                strong_hits += 1
            elif any(stripped.endswith(suf) for suf in _WEAK_SUFFIXES):
                weak_hits += 1

        if strong_hits >= 1:
            return "qu"
        if weak_hits >= 2:
            return "qu"
        return "es"