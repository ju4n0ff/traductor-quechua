from typing import Callable
import customtkinter as ctk
from src.ui.icons import mic, mic_filled, speaker, arrows
from src.ui.theme import (
    ACCENT, ACCENT_HOVER, ACCENT_SOFT, ACCENT_SECONDARY, ACCENT_SECONDARY_SOFT,
    DANGER, DANGER_HOVER, WARNING,
    SURFACE, SURFACE_ALT, SURFACE_HOVER, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, FONT_FAMILY,
    BUTTON_RADIUS,
)


class Card(ctk.CTkFrame):
    def __init__(self, master, accent_color=None, **kwargs):
        super().__init__(master, fg_color=SURFACE, corner_radius=14, border_width=1, border_color=BORDER, **kwargs)
        if accent_color:
            self._accent = ctk.CTkLabel(self, text="", fg_color=accent_color, width=4, corner_radius=2)
            self._accent.place(x=0, rely=0.5, anchor="w", relheight=0.7)


class EyebrowLabel(ctk.CTkLabel):
    def __init__(self, master, text: str, **kwargs):
        super().__init__(
            master, text=text.upper(),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=TEXT_SECONDARY, **kwargs,
        )


class Badge(ctk.CTkFrame):
    def __init__(self, master, text: str, **kwargs):
        super().__init__(master, fg_color=ACCENT_SOFT, corner_radius=100, **kwargs)
        self._label = ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=ACCENT,
        )
        self._label.pack(padx=14, pady=5)

    def set_text(self, text: str):
        self._label.configure(text=text)


class IconButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon=None, icon_active=None, **kwargs):
        self._icon = icon
        self._icon_active = icon_active
        display_text = f"  {text}" if icon else text
        super().__init__(
            master, text=display_text, image=icon,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent",
            hover_color=ACCENT_SOFT,
            text_color=ACCENT,
            border_width=1, border_color=ACCENT,
            corner_radius=BUTTON_RADIUS,
            cursor="hand2",
            **kwargs,
        )

    def set_active(self, active: bool):
        if active and self._icon_active:
            self.configure(image=self._icon_active, fg_color=ACCENT, text_color="#ffffff", border_color=ACCENT)
        else:
            self.configure(image=self._icon, fg_color="transparent", text_color=ACCENT, border_color=ACCENT)


class RecordRing(ctk.CTkFrame):
    def __init__(self, master, size: int = 104, **kwargs):
        super().__init__(master, fg_color="transparent", border_width=2, border_color=ACCENT_SOFT,
                         corner_radius=size // 2, width=size, height=size, **kwargs)
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
        super().__init__(master, fg_color="transparent", **kwargs)
        self._is_recording = False
        self._text_record = text_record
        self._text_stop = text_stop
        self._external_command = command

        self._ring = RecordRing(self, size=size + 16)
        self._ring.pack(expand=True)

        self._btn = ctk.CTkButton(
            self._ring,
            text=text_record,
            width=size, height=size, corner_radius=size // 2,
            border_width=0,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
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
    _COLORS = {"idle": ACCENT, "busy": WARNING, "error": DANGER}

    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=8, fg_color=SURFACE,
                         border_width=1, border_color=BORDER, height=34, **kwargs)
        self.pack_propagate(False)
        self._dot = ctk.CTkLabel(self, text="●", text_color=ACCENT, font=ctk.CTkFont(size=10), width=12)
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
        super().__init__(master, fg_color="transparent", **kwargs)
        self._command = command
        self._active = active

        self._es_btn = ctk.CTkButton(
            self, text="ES", width=40, height=26, corner_radius=6,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            command=lambda: self._set_active("es"),
        )
        self._es_btn.pack(side="left", padx=(0, 4))

        self._qu_btn = ctk.CTkButton(
            self, text="QU", width=40, height=26, corner_radius=6,
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
                btn.configure(fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff", border_width=0)
            else:
                btn.configure(fg_color="transparent", hover_color=SURFACE,
                              text_color=TEXT_SECONDARY, border_width=1, border_color=BORDER)
