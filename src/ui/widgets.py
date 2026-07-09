from typing import Callable
import customtkinter as ctk


class RecordButton(ctk.CTkButton):
    def __init__(self, master, size: int = 100, command: Callable | None = None, **kwargs):
        self._size = size
        self._is_recording = False
        super().__init__(
            master,
            text="REC",
            width=size,
            height=size,
            corner_radius=size // 2,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=ctk.CTkFont(size=size // 4, weight="bold"),
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
            self.configure(fg_color="#c62828", hover_color="#b71c1c", text="STOP")
        else:
            self.configure(fg_color="#2e7d32", hover_color="#1b5e20", text="REC")
        if self._external_command:
            self._external_command(self._is_recording)

    def reset(self):
        self._is_recording = False
        self.configure(fg_color="#2e7d32", hover_color="#1b5e20", text="REC")


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=32, **kwargs)
        self.pack_propagate(False)
        self._label = ctk.CTkLabel(
            self,
            text="Listo",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._label.pack(side="left", padx=10, pady=4)

    def set_status(self, text: str, icon: str = ""):
        self._label.configure(text=f"{icon} {text}".strip())
        self.update_idletasks()
