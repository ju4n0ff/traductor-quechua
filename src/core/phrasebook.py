import re

_ES_TO_QU = {
    "hola": "Imaynalla",
    "buenos dias": "Allin p'unchay",
    "buenas noches": "Allin tuta",
    "como estas": "Allillanchu",
    "gracias": "Añay",
    "hasta manana": "Paqarinkama",
    "un poco": "uj chicata",

}

_QU_TO_ES = {
    "imaynalla": "Hola / ¿Cómo estás?",
    "allin p'unchay": "Buenos días",
    "allin tuta": "Buenas noches",
    "allillanchu": "¿Cómo estás? / ¿Estás bien?",
    "añay": "Gracias",
    "paqarinkama": "Hasta mañana",
}


def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[¿?¡!.,;:]", "", text)
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        text = text.replace(a, b)
    return text.strip()


def lookup(text: str, direction: str) -> str | None:
    """direction: 'es_to_qu' o 'qu_to_es'. None si no hay match exacto
    (seguir con NLLB)."""
    key = _normalize(text)
    if direction == "es_to_qu":
        return _ES_TO_QU.get(key)
    if direction == "qu_to_es":
        return _QU_TO_ES.get(key)
    return None