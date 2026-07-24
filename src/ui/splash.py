import os
import threading
import time
import customtkinter as ctk
from pathlib import Path
from huggingface_hub import list_repo_tree, snapshot_download

from src.ui.theme import ACCENT, SURFACE, APP_BG, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, FONT_FAMILY
from src.utils.config import WHISPER_MODEL_DIR, NLLB_CT2_DIR, NLLB_CT2_REPO_ID

ctk.set_appearance_mode("dark")

WHISPER_REPO_ID = "Systran/faster-whisper-tiny"


def _repo_size(repo_id: str) -> int:
    total = 0
    for item in list_repo_tree(repo_id):
        total += item.size
    return total


def _dir_size(path: Path) -> int:
    if not path.is_dir():
        return 0
    total = 0
    for dirpath, _, filenames in os.walk(str(path)):
        for f in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass
    return total


def models_missing() -> list[tuple[str, str, Path, int]]:
    missing = []
    w_size = _repo_size(WHISPER_REPO_ID)
    if _dir_size(WHISPER_MODEL_DIR) < w_size * 0.9:
        missing.append(("faster-whisper tiny", WHISPER_REPO_ID, WHISPER_MODEL_DIR, w_size))
    n_size = _repo_size(NLLB_CT2_REPO_ID)
    if _dir_size(NLLB_CT2_DIR) < n_size * 0.9:
        missing.append(("NLLB 600M (CTranslate2)", NLLB_CT2_REPO_ID, NLLB_CT2_DIR, n_size))
    return missing


class SplashWindow(ctk.CTk):
    def __init__(self, models: list):
        super().__init__()
        self.title("Preparando tu Traductor")
        self.geometry("520x340")
        self.resizable(False, False)
        self.configure(fg_color=APP_BG)

        self._models = models
        self._grand_total = sum(m[3] for m in models)
        self._cancel = False

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(expand=True, fill="both", padx=40, pady=32)

        ctk.CTkLabel(
            main, text="Preparando tu Traductor",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            main, text="Descargando modelos por primera vez.\nEsto puede tomar varios minutos.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_SECONDARY,
            justify="left",
        ).pack(anchor="w", pady=(0, 24))

        self._total_bar = ctk.CTkProgressBar(
            main, mode="determinate", corner_radius=4, height=10,
            fg_color=SURFACE, progress_color=ACCENT,
        )
        self._total_bar.pack(fill="x")
        self._total_bar.set(0)

        self._total_lbl = ctk.CTkLabel(
            main, text="Iniciando...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._total_lbl.pack(pady=(6, 16))

        self._model_lbl = ctk.CTkLabel(
            main, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_SECONDARY,
        )
        self._model_lbl.pack(anchor="w")

        self._file_bar = ctk.CTkProgressBar(
            main, mode="determinate", corner_radius=3, height=6,
            fg_color=SURFACE, progress_color=ACCENT,
        )
        self._file_bar.pack(fill="x", pady=(4, 0))
        self._file_bar.set(0)

        self._file_lbl = ctk.CTkLabel(
            main, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_MUTED,
        )
        self._file_lbl.pack(anchor="w", pady=(2, 0))

        self._cancel_btn = ctk.CTkButton(
            main, text="Cancelar",
            width=100, height=30,
            corner_radius=8,
            fg_color="transparent", hover_color=SURFACE,
            text_color=TEXT_SECONDARY, border_width=1, border_color=SURFACE,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            cursor="hand2",
            command=self._on_cancel,
        )
        self._cancel_btn.pack(pady=(20, 0))

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_cancel(self):
        self._cancel = True
        self.destroy()
        raise SystemExit(0)

    def run(self):
        self.after(100, self._begin)
        self.mainloop()

    def _begin(self):
        threading.Thread(target=self._download_all, daemon=True).start()
        self._poll_progress()

    def _poll_progress(self):
        if self._cancel:
            return
        self._update_ui()
        self.after(300, self._poll_progress)

    def _update_ui(self):
        accumulated = 0
        for _, _, target_dir, total_size in self._models:
            done = _dir_size(target_dir)
            accumulated += min(done, total_size)

        frac = accumulated / self._grand_total if self._grand_total > 0 else 0
        self._total_bar.set(frac)
        self._total_lbl.configure(text=f"{frac*100:.0f}% completado — {accumulated/1024/1024:.0f} / {self._grand_total/1024/1024:.0f} MB")

        current_name, current_dir, current_total = "", None, 0
        for name, _, d, ts in self._models:
            if _dir_size(d) < ts * 0.95:
                current_name, current_dir, current_total = name, d, ts
                break

        if current_name and current_dir:
            done = _dir_size(current_dir)
            file_frac = min(done / current_total, 1.0) if current_total > 0 else 0
            self._model_lbl.configure(text=f"Descargando {current_name}...")
            self._file_bar.set(file_frac)
            self._file_lbl.configure(text=f"{done/1024/1024:.0f} / {current_total/1024/1024:.0f} MB")
        else:
            self._total_bar.set(1.0)
            self._total_lbl.configure(text="100% completado")
            self._model_lbl.configure(text="")
            self._file_bar.set(1.0)
            self._file_lbl.configure(text="")
            if not self._cancel:
                self.after(200, self.destroy)

    def _download_all(self):
        for _, repo_id, target_dir, _ in self._models:
            if self._cancel:
                return
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                snapshot_download(
                    repo_id=repo_id,
                    local_dir=str(target_dir),
                )
            except Exception as e:
                if not self._cancel:
                    self.after(0, lambda: self._model_lbl.configure(text=f"Error: {e}"))
                return
