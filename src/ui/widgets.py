from typing import Callable
import customtkinter as ctk
from src.ui.theme import (
    ACCENT, ACCENT_HOVER, ACCENT_SOFT, DANGER, DANGER_HOVER, WARNING,
    SURFACE, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, FONT_FAMILY,
)


class Card(ctk.CTkFrame):
    """Contenedor tipo tarjeta: fondo elevado + borde sutil (patron SaaS)."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", SURFACE)
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDER)
        super().__init__(master, **kwargs)


class EyebrowLabel(ctk.CTkLabel):
    """Etiqueta pequena en mayusculas, estilo 'eyebrow' de interfaces SaaS."""

    def __init__(self, master, text: str, **kwargs):
        kwargs.setdefault("font", ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"))
        kwargs.setdefault("text_color", TEXT_SECONDARY)
        super().__init__(master, text=text.upper(), **kwargs)


class Badge(ctk.CTkFrame):
    """Pastilla/badge para mostrar la direccion de traduccion."""

    def __init__(self, master, text: str, **kwargs):
        kwargs.setdefault("fg_color", ACCENT_SOFT)
        kwargs.setdefault("corner_radius", 100)
        super().__init__(master, **kwargs)
        self._label = ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=ACCENT,
        )
        self._label.pack(padx=14, pady=5)

    def set_text(self, text: str):
        self._label.configure(text=text)


class RecordButton(ctk.CTkButton):
    """Boton circular de grabacion (solo texto, sin iconos generados)."""

    def __init__(self, master, size: int = 96, command: Callable | None = None, **kwargs):
        self._size = size
        self._is_recording = False
        super().__init__(
            master,
            text="GRABAR",
            width=size,
            height=size,
            corner_radius=size // 2,
            border_width=0,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(family=FONT_FAMILY, size=max(12, size // 8), weight="bold"),
            cursor="hand2",
            command=self._on_click,
            **kwargs,
        )
        self._external_command = command

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def _on_click(self):
        self._is_recording = not self._is_recording
        if self._is_recording:
            self.configure(fg_color=DANGER, hover_color=DANGER_HOVER, text="DETENER")
        else:
            self.reset()
        if self._external_command:
            self._external_command(self._is_recording)

    def reset(self):
        self._is_recording = False
        self.configure(fg_color=ACCENT, hover_color=ACCENT_HOVER, text="GRABAR")


class StatusBar(ctk.CTkFrame):
    """Barra de estado inferior: punto de color (idle/busy/error) + texto."""

    _COLORS = {"idle": ACCENT, "busy": WARNING, "error": DANGER}

    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("fg_color", SURFACE)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDER)
        super().__init__(master, height=36, **kwargs)
        self.pack_propagate(False)

        self._dot = ctk.CTkLabel(self, text="\u25CF", text_color=ACCENT, font=ctk.CTkFont(size=12), width=14)
        self._dot.pack(side="left", padx=(14, 6), pady=4)

        self._label = ctk.CTkLabel(
            self, text="Listo",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_PRIMARY, anchor="w",
        )
        self._label.pack(side="left", padx=(0, 12), pady=4, fill="x", expand=True)

    def set_status(self, text: str, state: str = "idle"):
        self._dot.configure(text_color=self._COLORS.get(state, ACCENT))
        self._label.configure(text=text)
        self.update_idletasks()