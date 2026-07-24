"""Descarga el modelo NLLB-200-distilled-600M ya convertido a CTranslate2 int8.

Uso:
    python scripts/download_nllb_ct2.py

Requiere (solo para este script, no para correr la app después):
    pip install huggingface_hub
"""

from huggingface_hub import snapshot_download

from src.utils.config import NLLB_CT2_REPO_ID, NLLB_CT2_DIR


def main():
    print(f"Descargando {NLLB_CT2_REPO_ID} -> {NLLB_CT2_DIR}")
    snapshot_download(
        repo_id=NLLB_CT2_REPO_ID,
        local_dir=str(NLLB_CT2_DIR),
    )
    print(f"Listo. Modelo en: {NLLB_CT2_DIR}")


if __name__ == "__main__":
    main()