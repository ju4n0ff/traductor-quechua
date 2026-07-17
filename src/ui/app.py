import threading
import queue
import time
import customtkinter as ctk
from src.utils.config import APP_TITLE, APP_SIZE
from src.ui.widgets import RecordButton, StatusBar, Card, EyebrowLabel, Badge
from src.ui.theme import (
    APP_BG, SURFACE, SURFACE_ALT, ACCENT, ACCENT_HOVER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, FONT_FAMILY,
)
from src.core.audio import AudioRecorder
from src.core.asr import SpeechRecognizer
from src.core.translator import TextTranslator
from src.core.tts import TextToSpeech

ctk.set_appearance_mode("dark")


class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(760, 560)
        self.configure(fg_color=APP_BG)

        self._recorder = AudioRecorder()
        self._recognizer = SpeechRecognizer()
        self._translator = TextTranslator()
        self._tts = TextToSpeech()

        self._dir_var = ctk.StringVar(value="Automatico")
        self._processing_queue: queue.Queue = queue.Queue()
        self._processing_thread: threading.Thread | None = None
        self._running = True
        self._last_audio_task_id = 0

        self._setup_ui()
        self._start_processing_thread()

    # ------------------------------------------------------------------ UI

    def _setup_ui(self):
        self._main = ctk.CTkFrame(self, fg_color="transparent")
        self._main.pack(fill="both", expand=True, padx=28, pady=24)

        self._build_header()
        self._build_mode_bar()
        self._build_text_cards()
        self._build_record_section()
        self._build_status_bar()

    def _build_header(self):
        header_row = ctk.CTkFrame(self._main, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 18))

        title_col = ctk.CTkFrame(header_row, fg_color="transparent")
        title_col.pack(side="left", anchor="w")

        title_row = ctk.CTkFrame(title_col, fg_color="transparent")
        title_row.pack(anchor="w")
        ctk.CTkLabel(title_row, text="", fg_color=ACCENT, width=4, height=22, corner_radius=2).pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkLabel(
            title_row,
            text=APP_TITLE,
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            title_col,
            text="Traduccion por voz y texto entre quechua y espanol",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=(14, 0), pady=(2, 0))

        self._dir_badge = Badge(header_row, text="QUECHUA  \u21C4  ESPA\u00d1OL")
        self._dir_badge.pack(side="right", anchor="e", pady=(4, 0))

    def _build_mode_bar(self):
        self._mode_switch = ctk.CTkSegmentedButton(
            self._main,
            values=["Voz", "Texto"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=SURFACE,
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            unselected_color=SURFACE,
            unselected_hover_color=SURFACE_ALT,
            text_color=TEXT_PRIMARY,
            corner_radius=10,
            height=38,
        )
        self._mode_switch.set("Voz")
        self._mode_switch.pack(fill="x")

        dir_row = ctk.CTkFrame(self._main, fg_color="transparent")
        dir_row.pack(fill="x", pady=(12, 16))
        ctk.CTkLabel(dir_row, text="Direccion:", font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left", padx=(0, 8))
        self._dir_menu = ctk.CTkOptionMenu(
            dir_row,
            values=["Automatico", "Quechua → Espanol", "Espanol → Quechua"],
            variable=self._dir_var,
            width=200,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        )
        self._dir_menu.pack(side="left")

    def _build_text_cards(self):
        text_frame = ctk.CTkFrame(self._main, fg_color="transparent")
        text_frame.pack(fill="both", expand=True)

        # ---- Tarjeta: texto original ----
        src_card = Card(text_frame)
        src_card.pack(fill="both", expand=True, pady=(0, 10))
        EyebrowLabel(src_card, "Texto original").pack(anchor="w", padx=16, pady=(14, 0))
        self._src_text = ctk.CTkTextbox(
            src_card,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            height=100,
            corner_radius=8,
            fg_color=SURFACE_ALT,
            border_width=0,
            text_color=TEXT_PRIMARY,
        )
        self._src_text.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        self._src_text.bind("<KeyRelease>", self._on_text_change)

        # ---- Boton traducir (primario, centrado) ----
        ctr_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        ctr_frame.pack(fill="x")
        self._swap_btn = ctk.CTkButton(
            ctr_frame,
            text="Traducir  \u2192",
            width=150,
            height=36,
            corner_radius=8,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            cursor="hand2",
            command=self._translate_text_input,
        )
        self._swap_btn.pack(pady=8)

        # ---- Tarjeta: traduccion ----
        tgt_card = Card(text_frame)
        tgt_card.pack(fill="both", expand=True, pady=(10, 0))
        tgt_header = ctk.CTkFrame(tgt_card, fg_color="transparent")
        tgt_header.pack(fill="x", padx=16, pady=(14, 0))
        EyebrowLabel(tgt_header, "Traduccion").pack(side="left")
        self._speak_tgt_btn = ctk.CTkButton(
            tgt_header,
            text="Escuchar",
            width=110,
            height=26,
            corner_radius=8,
            fg_color="transparent",
            hover_color=SURFACE_ALT,
            border_width=1,
            border_color=ACCENT,
            text_color=ACCENT,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            cursor="hand2",
            command=self._speak_translated,
        )
        self._speak_tgt_btn.pack(side="right")
        self._tgt_text = ctk.CTkTextbox(
            tgt_card,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            height=100,
            corner_radius=8,
            fg_color=SURFACE_ALT,
            border_width=0,
            text_color=TEXT_PRIMARY,
        )
        self._tgt_text.pack(fill="both", expand=True, padx=16, pady=(8, 16))

    def _build_record_section(self):
        record_frame = ctk.CTkFrame(self._main, fg_color="transparent")
        record_frame.pack(pady=18)
        self._record_btn = RecordButton(record_frame, size=88, command=self._on_record_toggle)
        self._record_btn.pack()
        self._record_hint = ctk.CTkLabel(
            record_frame,
            text="Presiona para grabar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_MUTED,
        )
        self._record_hint.pack(pady=(8, 0))

    def _build_status_bar(self):
        self._progress = ctk.CTkProgressBar(
            self._main, mode="indeterminate", corner_radius=4, height=4,
            fg_color=SURFACE, progress_color=ACCENT,
        )
        self._progress.pack(fill="x", pady=(0, 8))
        self._progress.pack_forget()

        self._status = StatusBar(self._main)
        self._status.pack(fill="x")

    # ------------------------------------------------------------- eventos

    def _on_text_change(self, event=None):
        pass  # Se traduce manualmente via boton

    def _on_record_toggle(self, is_recording: bool):
        if is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self._recorder.start_recording()
        self._status.set_status("Grabando...", state="busy")
        self._record_hint.configure(text="Presiona para detener")
        self._src_text.delete("0.0", "end")
        self._tgt_text.delete("0.0", "end")
        self._progress.pack(fill="x", pady=(0, 8))
        self._progress.start()

    def _stop_recording(self):
        self._status.set_status("Procesando audio...", state="busy")
        self._record_hint.configure(text="Procesando...")
        self._record_btn.reset()
        self.update_idletasks()

        audio, peak = self._recorder.stop_recording()
        if audio is None or len(audio) < 8000:
            self._status.set_status("Audio muy corto", state="error")
            self._record_hint.configure(text="Presiona para grabar")
            self._progress.stop()
            self._progress.pack_forget()
            return
        if peak < 0.01:
            self._status.set_status(f"Volumen muy bajo ({peak:.4f})", state="error")
            self._record_hint.configure(text="Habla mas cerca del microfono")
            self._progress.stop()
            self._progress.pack_forget()
            return

        task_id = self._last_audio_task_id + 1
        self._last_audio_task_id = task_id
        self._processing_queue.put(("audio", audio, task_id))

    def _translate_text_input(self):
        text = self._src_text.get("0.0", "end").strip()
        if not text:
            return
        self._status.set_status("Traduciendo texto...", state="busy")
        self._progress.pack(fill="x", pady=(0, 8))
        self._progress.start()
        self._swap_btn.configure(state="disabled", text="...")
        self.update_idletasks()
        self._processing_queue.put(("text", text, 0))

    def _speak_translated(self):
        text = self._tgt_text.get("0.0", "end").strip()
        if not text:
            return
        direction = self._dir_var.get()
        if direction == "Espanol → Quechua":
            tts_lang = "qu"
        else:
            tts_lang = "es"
        self._status.set_status("Reproduciendo audio...", state="busy")
        threading.Thread(target=self._tts.speak, args=(text, tts_lang), daemon=True).start()

    def _start_processing_thread(self):
        self._processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._processing_thread.start()

    def _process_queue(self):
        while self._running:
            try:
                task_type, data, task_id = self._processing_queue.get(timeout=0.3)
            except (queue.Empty, ValueError):
                continue

            try:
                if task_type == "audio":
                    self._process_audio(data, task_id)
                elif task_type == "text":
                    self._process_text(data)
            except Exception as e:
                err = str(e)
                print(f"Error: {err}")
                self.after(0, lambda m=err: self._on_error(m))
            finally:
                try:
                    self._processing_queue.task_done()
                except ValueError:
                    pass

    def _on_error(self, msg: str):
        self._status.set_status(f"Error: {msg}", state="error")
        self._record_hint.configure(text="Presiona para grabar")
        self._progress.stop()
        self._progress.pack_forget()
        self._swap_btn.configure(state="normal", text="Traducir")

    def _process_audio(self, audio, task_id):
        result, detected_lang = self._recognizer.transcribe(audio)

        if task_id != self._last_audio_task_id:
            return

        if not result:
            self.after(0, lambda: self._status.set_status("No se reconocio voz", state="error"))
            self.after(0, lambda: self._record_hint.configure(text="Presiona para grabar"))
            self.after(0, lambda: (self._progress.stop(), self._progress.pack_forget()))
            return

        self.after(0, lambda: self._update_src_text(result))
        self.after(0, lambda: self._status.set_status("Traduciendo...", state="busy"))

        direction = self._dir_var.get()
        dir_map = {"Quechua → Espanol": "qu_to_es", "Espanol → Quechua": "es_to_qu", "Automatico": None}
        translation = self._translator.translate(result, direction=dir_map.get(direction))

        if task_id != self._last_audio_task_id:
            return

        self.after(0, lambda t=translation: self._update_tgt_text(t))
        self.after(0, lambda: self._status.set_status("Traduccion lista", state="idle"))
        self.after(0, lambda: self._record_hint.configure(text="Presiona para grabar"))
        self.after(0, lambda: (self._progress.stop(), self._progress.pack_forget()))

    def _process_text(self, text):
        start = time.time()
        direction = self._dir_var.get()
        dir_map = {"Quechua → Espanol": "qu_to_es", "Espanol → Quechua": "es_to_qu", "Automatico": None}
        translation = self._translator.translate(text, direction=dir_map.get(direction))
        elapsed = time.time() - start

        self.after(0, lambda: self._update_tgt_text(translation))
        self.after(0, lambda t=elapsed: self._status.set_status(f"Listo ({t:.1f}s)", state="idle"))
        self.after(0, lambda: (self._progress.stop(), self._progress.pack_forget()))
        self.after(0, lambda: self._swap_btn.configure(state="normal", text="Traducir"))

    def _update_src_text(self, text: str):
        self._src_text.delete("0.0", "end")
        self._src_text.insert("0.0", text)

    def _update_tgt_text(self, text: str):
        self._tgt_text.delete("0.0", "end")
        self._tgt_text.insert("0.0", text)

    def destroy(self):
        self._running = False
        super().destroy()