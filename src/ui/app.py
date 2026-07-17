import threading
import queue
import time
import customtkinter as ctk
from src.utils.config import APP_TITLE, APP_SIZE, APP_THEME
from src.ui.widgets import RecordButton, StatusBar
from src.core.audio import AudioRecorder
from src.core.asr import SpeechRecognizer
from src.core.translator import TextTranslator
from src.core.tts import TextToSpeech

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(APP_THEME)


class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(700, 500)

        self._recorder = AudioRecorder()
        self._recognizer = SpeechRecognizer()
        self._translator = TextTranslator()
        self._tts = TextToSpeech()

        self._processing_queue: queue.Queue = queue.Queue()
        self._processing_thread: threading.Thread | None = None
        self._running = True
        self._last_audio_task_id = 0

        self._setup_ui()
        self._start_processing_thread()

    def _setup_ui(self):
        self._main = ctk.CTkFrame(self)
        self._main.pack(fill="both", expand=True, padx=16, pady=16)

        header = ctk.CTkLabel(
            self._main,
            text="Traductor Quechua ↔ Español",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        header.pack(pady=(0, 12))

        # Mode selector
        mode_frame = ctk.CTkFrame(self._main)
        mode_frame.pack(fill="x", pady=(0, 10))
        self._mode_var = ctk.StringVar(value="audio")
        ctk.CTkRadioButton(
            mode_frame, text="Voz", variable=self._mode_var, value="audio"
        ).pack(side="left", padx=10)
        ctk.CTkRadioButton(
            mode_frame, text="Texto", variable=self._mode_var, value="text"
        ).pack(side="left", padx=10)

        dir_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        dir_frame.pack(side="right", padx=10)
        ctk.CTkLabel(dir_frame, text="Direccion:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        self._dir_var = ctk.StringVar(value="auto")
        self._dir_menu = ctk.CTkOptionMenu(
            dir_frame,
            values=["Automatico", "Quechua → Espanol", "Espanol → Quechua"],
            variable=self._dir_var,
            width=180,
        )
        self._dir_menu.pack(side="left")

        # Text areas
        text_frame = ctk.CTkFrame(self._main)
        text_frame.pack(fill="both", expand=True, pady=4)

        src_frame = ctk.CTkFrame(text_frame)
        src_frame.pack(fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(src_frame, text="Texto original", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        self._src_text = ctk.CTkTextbox(src_frame, font=ctk.CTkFont(size=14), height=100)
        self._src_text.pack(fill="both", expand=True, padx=4, pady=(2, 4))
        self._src_text.bind("<KeyRelease>", self._on_text_change)

        ctr_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        ctr_frame.pack(fill="x")
        self._swap_btn = ctk.CTkButton(
            ctr_frame,
            text="Traducir",
            width=120,
            command=self._translate_text_input,
        )
        self._swap_btn.pack(pady=4)

        tgt_frame = ctk.CTkFrame(text_frame)
        tgt_frame.pack(fill="both", expand=True, padx=6, pady=6)
        tgt_header = ctk.CTkFrame(tgt_frame)
        tgt_header.pack(fill="x")
        ctk.CTkLabel(tgt_header, text="Traduccion", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        self._speak_tgt_btn = ctk.CTkButton(
            tgt_header,
            text="Escuchar",
            width=100,
            height=24,
            command=self._speak_translated,
        )
        self._speak_tgt_btn.pack(side="right", padx=4)
        self._tgt_text = ctk.CTkTextbox(tgt_frame, font=ctk.CTkFont(size=14), height=100)
        self._tgt_text.pack(fill="both", expand=True, padx=4, pady=(2, 4))

        # Record button
        record_frame = ctk.CTkFrame(self._main, fg_color="transparent")
        record_frame.pack(pady=10)
        self._record_btn = RecordButton(record_frame, size=90, command=self._on_record_toggle)
        self._record_btn.pack()
        self._record_hint = ctk.CTkLabel(record_frame, text="Presiona para grabar", font=ctk.CTkFont(size=12), text_color="gray")
        self._record_hint.pack()

        # Progress bar
        self._progress = ctk.CTkProgressBar(self._main, mode="indeterminate")
        self._progress.pack(fill="x", pady=(4, 0))
        self._progress.pack_forget()

        # Status
        self._status = StatusBar(self._main)
        self._status.pack(fill="x", pady=(6, 0))

    def _on_text_change(self, event=None):
        pass  # We translate manually via button

    def _on_record_toggle(self, is_recording: bool):
        if is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self._recorder.start_recording()
        self._status.set_status("Grabando...")
        self._record_hint.configure(text="Presiona para detener")
        self._src_text.delete("0.0", "end")
        self._tgt_text.delete("0.0", "end")
        self._progress.pack(fill="x", pady=(4, 0))
        self._progress.start()

    def _stop_recording(self):
        self._status.set_status("Procesando audio...")
        self._record_hint.configure(text="Procesando...")
        self._record_btn.reset()
        self.update_idletasks()

        audio, peak = self._recorder.stop_recording()
        if audio is None or len(audio) < 8000:
            self._status.set_status("Audio muy corto")
            self._record_hint.configure(text="Presiona para grabar")
            self._progress.stop()
            self._progress.pack_forget()
            return
        if peak < 0.01:
            self._status.set_status(f"Volumen muy bajo ({peak:.4f})")
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
        self._status.set_status("Traduciendo texto...")
        self._progress.pack(fill="x", pady=(4, 0))
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
        self._status.set_status("Reproduciendo audio...")
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
        self._status.set_status(f"Error: {msg}")
        self._record_hint.configure(text="Presiona para grabar")
        self._progress.stop()
        self._progress.pack_forget()
        self._swap_btn.configure(state="normal", text="Traducir")

    def _process_audio(self, audio, task_id):
        result, detected_lang = self._recognizer.transcribe(audio)

        if task_id != self._last_audio_task_id:
            return

        if not result:
            self.after(0, lambda: self._status.set_status("No se reconocio voz"))
            self.after(0, lambda: self._record_hint.configure(text="Presiona para grabar"))
            self.after(0, lambda: (self._progress.stop(), self._progress.pack_forget()))
            return

        self.after(0, lambda: self._update_src_text(result))
        self.after(0, lambda: self._status.set_status("Traduciendo..."))

        direction = self._dir_var.get()
        dir_map = {"Quechua → Espanol": "qu_to_es", "Espanol → Quechua": "es_to_qu", "Automatico": None}
        translation = self._translator.translate(result, direction=dir_map.get(direction))

        if task_id != self._last_audio_task_id:
            return

        self.after(0, lambda t=translation: self._update_tgt_text(t))
        self.after(0, lambda: self._status.set_status("Traduccion lista"))
        self.after(0, lambda: self._record_hint.configure(text="Presiona para grabar"))
        self.after(0, lambda: (self._progress.stop(), self._progress.pack_forget()))

    def _process_text(self, text):
        start = time.time()
        direction = self._dir_var.get()
        dir_map = {"Quechua → Espanol": "qu_to_es", "Espanol → Quechua": "es_to_qu", "Automatico": None}
        translation = self._translator.translate(text, direction=dir_map.get(direction))
        elapsed = time.time() - start

        self.after(0, lambda: self._update_tgt_text(translation))
        self.after(0, lambda t=elapsed: self._status.set_status(f"Listo ({t:.1f}s)"))
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
