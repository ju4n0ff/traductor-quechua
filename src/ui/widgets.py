from typing import Callable
import customtkinter as ctk
from src.ui.theme import (
    ACCENT, ACCENT_HOVER, ACCENT_SOFT, ACCENT_GLOW,
    DANGER, DANGER_HOVER, WARNING,
    SURFACE, SURFACE_HOVER, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT_FAMILY,
    BUTTON_RADIUS,
)


class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", SURFACE)
        kwargs.setdefault("corner_radius", 14)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDER)
        super().__init__(master, **kwargs)


class EyebrowLabel(ctk.CTkLabel):
    def __init__(self, master, text: str, **kwargs):
        kwargs.setdefault("font", ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"))
        kwargs.setdefault("text_color", TEXT_SECONDARY)
        super().__init__(master, text=text.upper(), **kwargs)


class Badge(ctk.CTkFrame):
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


class PillButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon: str = "", **kwargs):
        display = f"{icon}  {text}" if icon else text
        kwargs.setdefault("font", ctk.CTkFont(family=FONT_FAMILY, size=12))
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("hover_color", ACCENT_SOFT)
        kwargs.setdefault("text_color", ACCENT)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", ACCENT)
        kwargs.setdefault("corner_radius", BUTTON_RADIUS)
        kwargs.setdefault("cursor", "hand2")
        super().__init__(master, text=display, **kwargs)


class RecordRing(ctk.CTkFrame):
    def __init__(self, master, size: int = 104, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("border_width", 2)
        kwargs.setdefault("border_color", ACCENT_SOFT)
        kwargs.setdefault("corner_radius", size // 2)
        kwargs.setdefault("width", size)
        kwargs.setdefault("height", size)
        super().__init__(master, **kwargs)
        self._pulse_id: str | None = None
        self._pulse_on = False

    def start_pulse(self):
        self._pulse_on = True
        self._pulse()

    def stop_pulse(self):
        self._pulse_on = False
        if self._pulse_id:
            self.after_cancel(self._pulse_id)
            self._pulse_id = None
        self.configure(border_color=ACCENT_SOFT)

    def _pulse(self):
        if not self._pulse_on:
            return
        current = self.cget("border_color")
        nxt = ACCENT if current == ACCENT_SOFT else ACCENT_SOFT
        self.configure(border_color=nxt)
        self._pulse_id = self.after(700, self._pulse)


class RecordButton(ctk.CTkFrame):
    def __init__(self, master, size: int = 88, command: Callable | None = None,
                 text_record: str = "GRABAR", text_stop: str = "DETENER", **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._is_recording = False
        self._text_record = text_record
        self._text_stop = text_stop
        self._external_command = command
        self._size = size

        self._ring = RecordRing(self, size=size + 16)
        self._ring.pack(expand=True)

        self._btn = ctk.CTkButton(
            self._ring,
            text=text_record,
            width=size,
            height=size,
            corner_radius=size // 2,
            border_width=0,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(family=FONT_FAMILY, size=max(13, size // 7), weight="bold"),
            cursor="hand2",
            command=self._on_click,
        )
        self._btn.place(relx=0.5, rely=0.5, anchor="center")

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def _on_click(self):
        self._is_recording = not self._is_recording
        if self._is_recording:
            self._btn.configure(fg_color=DANGER, hover_color=DANGER_HOVER, text=self._text_stop)
            self._ring.start_pulse()
        else:
            self.reset()
        if self._external_command:
            self._external_command(self._is_recording)

    def set_texts(self, record_text: str, stop_text: str):
        self._text_record = record_text
        self._text_stop = stop_text
        if not self._is_recording:
            self._btn.configure(text=record_text)

    def reset(self):
        self._is_recording = False
        self._ring.stop_pulse()
        self._btn.configure(fg_color=ACCENT, hover_color=ACCENT_HOVER, text=self._text_record)


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


class LangToggle(ctk.CTkFrame):
    def __init__(self, master, command=None, active="es", **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        self._command = command
        self._active = active

        self._es_btn = ctk.CTkButton(
            self, text="ES", width=40, height=26,
            corner_radius=6,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            command=lambda: self._set_active("es"),
        )
        self._es_btn.pack(side="left", padx=(0, 4))

        self._qu_btn = ctk.CTkButton(
            self, text="QU", width=40, height=26,
            corner_radius=6,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            command=lambda: self._set_active("qu"),
        )
        self._qu_btn.pack(side="left")

        self._update_style()

    def _set_active(self, lang: str):
        if lang == self._active:
            return
        self._active = lang
        self._update_style()
        if self._command:
            self._command(lang)

    def _update_style(self):
        for btn, lang in [(self._es_btn, "es"), (self._qu_btn, "qu")]:
            if lang == self._active:
                btn.configure(
                    fg_color=ACCENT, hover_color=ACCENT_HOVER,
                    text_color="#ffffff", border_width=0,
                )
            else:
                btn.configure(
                    fg_color="transparent", hover_color=SURFACE,
                    text_color=TEXT_SECONDARY, border_width=1, border_color=BORDER,
                )