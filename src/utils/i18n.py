STRINGS = {
    "es": {
        "app_title": "Traductor Quechua — Español",
        "app_subtitle": "Traduccion por voz y texto entre quechua y espanol",
        "dir_badge": "QUECHUA  \u21C4  ESPA\u00d1OL",
        "dir_label": "Direccion:",
        "dir_auto": "Automatico",
        "dir_qu_es": "Quechua \u2192 Espanol",
        "dir_es_qu": "Espanol \u2192 Quechua",
        "src_eyebrow": "Texto original",
        "src_dictar": "Dictar",
        "src_detener": "Detener",
        "translate": "Traducir",
        "translating": "...",
        "tgt_eyebrow": "Traduccion",
        "listen": "Escuchar",
        "record_btn": "GRABAR",
        "record_stop": "DETENER",
        "hint_record": "Presiona para grabar",
        "hint_stop": "Presiona para detener",
        "hint_processing": "Procesando...",
        "hint_speak_closer": "Habla mas cerca del microfono",
        "status_ready": "Listo",
        "status_recording": "Grabando...",
        "status_processing": "Procesando audio...",
        "status_translating": "Traduciendo...",
        "status_translating_text": "Traduciendo texto...",
        "status_listening": "Reproduciendo audio...",
        "status_no_speech": "No se reconocio voz",
        "status_audio_short": "Audio muy corto",
        "status_volume_low": "Volumen muy bajo ({peak:.4f})",
        "status_done": "Traduccion lista",
        "status_done_timed": "Listo ({t:.1f}s)",
        "status_error": "Error: {msg}",
        "lang_es": "ES",
        "lang_qu": "QU",
    },
    "qu": {
        "app_title": "Traductor Quechua — Español",
        "app_subtitle": "Quechua-Espanol t'aqrachiq",
        "dir_badge": "QUECHUA  \u21C4  ESPA\u00d1OL",
        "dir_label": "Puriy:",
        "dir_auto": "Kikillanmanta",
        "dir_qu_es": "Quechua \u2192 Espanol",
        "dir_es_qu": "Espanol \u2192 Quechua",
        "src_eyebrow": "Qallariy qillqa",
        "src_dictar": "Uyarichiy",
        "src_detener": "Sayay",
        "translate": "T'aqrachiy",
        "translating": "...",
        "tgt_eyebrow": "T'aqrachisqa",
        "listen": "Rimay",
        "record_btn": "UYARIY",
        "record_stop": "SAYAY",
        "hint_record": "Uyariypaq ñit'iy",
        "hint_stop": "Sayapaq ñit'iy",
        "hint_processing": "Ruwaspa...",
        "hint_speak_closer": "Astawan qaylla rimay",
        "status_ready": "Listo",
        "status_recording": "Uyarichka...",
        "status_processing": "Uyarita ruwachka...",
        "status_translating": "T'aqrachichka...",
        "status_translating_text": "Qillqata t'aqrachichka...",
        "status_listening": "Uyarichichka...",
        "status_no_speech": "Mana rimay tarisqachu",
        "status_audio_short": "Uyarina pisillan",
        "status_volume_low": "Uyarina sinchi pisilla ({peak:.4f})",
        "status_done": "T'aqrachisqa",
        "status_done_timed": "Listo ({t:.1f}s)",
        "status_error": "Pantasqa: {msg}",
        "lang_es": "ES",
        "lang_qu": "QU",
    },
}

_DIR_CODE_TO_KEY = {
    "auto": "dir_auto",
    "qu_to_es": "dir_qu_es",
    "es_to_qu": "dir_es_qu",
}

_DIR_LABEL_TO_CODE = {}


def _build_label_map():
    for code, key in _DIR_CODE_TO_KEY.items():
        for lang in STRINGS:
            _DIR_LABEL_TO_CODE[STRINGS[lang][key]] = code


_build_label_map()


def get(lang: str, key: str, **kwargs) -> str:
    val = STRINGS.get(lang, STRINGS["es"]).get(key, key)
    if kwargs:
        return val.format(**kwargs)
    return val


def dir_labels(lang: str) -> list[str]:
    return [get(lang, key) for key in _DIR_CODE_TO_KEY.values()]


def dir_label(lang: str, code: str) -> str:
    key = _DIR_CODE_TO_KEY.get(code, "dir_auto")
    return get(lang, key)


def dir_code(label: str) -> str:
    return _DIR_LABEL_TO_CODE.get(label, "auto")
