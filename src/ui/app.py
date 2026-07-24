import threading
import queue
import time
import customtkinter as ctk
from src.utils.config import APP_TITLE, APP_SIZE
import src.utils.i18n as i18n
from src.ui import icons
from src.ui.widgets import (
    StatusBar, Card, EyebrowLabel, Badge, LangToggle, IconButton,
)
from src.ui.theme import (
    APP_BG, SURFACE, SURFACE_ALT, BORDER,
    ACCENT, ACCENT_HOVER, ACCENT_SOFT, ACCENT_SECONDARY, ACCENT_SECONDARY_SOFT,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, FONT_FAMILY,
    BUTTON_RADIUS,
)
from src.core.audio import AudioRecorder
from src.core.asr import SpeechRecognizer
from src.core.translator import TextTranslator
from src.core.tts import TextToSpeech

ctk.set_appearance_mode("dark")
ctk.set_widget_scaling(1.0)


class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(800, 600)
        self.configure(fg_color=APP_BG)

        self._recorder = AudioRecorder()
        self._recognizer = SpeechRecognizer()
        self._translator = TextTranslator()
        self._tts = TextToSpeech()

        self._lang = "es"
        self._direction_code = "auto"
        self._src_mic_recording = False
        self._processing_queue: queue.Queue = queue.Queue()
        self._processing_thread: threading.Thread | None = None
        self._running = True
        self._last_audio_task_id = 0

        self._setup_ui()
        self._apply_language()
        self._start_processing_thread()

    # ------------------------------------------------------------------ UI

    def _setup_ui(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_banner(outer)
        self._main = ctk.CTkFrame(outer, fg_color="transparent")
        self._main.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        self._build_direction_section()
        self._build_text_cards()
        self._build_status_bar()

    def _build_banner(self, parent):
        banner = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=0, height=72, border_width=0)
        banner.pack(fill="x", pady=(0, 20))
        banner.pack_propagate(False)

        inner = ctk.CTkFrame(banner, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32)

        top_accent = ctk.CTkLabel(inner, text="", fg_color=ACCENT, width=5, height=28, corner_radius=3)
        top_accent.pack(side="left", padx=(0, 14))
        top_accent.place(relx=0, rely=0.5, anchor="w")

        title_col = ctk.CTkFrame(inner, fg_color="transparent")
        title_col.pack(side="left", anchor="w")

        ctk.CTkLabel(
            title_col,
            text=APP_TITLE,
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        self._subtitle_lbl = ctk.CTkLabel(
            title_col,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_MUTED,
        )
        self._subtitle_lbl.pack(anchor="w", pady=(1, 0))

        lang_toggle = LangToggle(inner, command=self._on_lang_change, active=self._lang)
        lang_toggle.pack(side="right", anchor="e")

    def _build_direction_section(self):
        container = ctk.CTkFrame(self._main, fg_color=SURFACE, corner_radius=12, border_width=1, border_color=BORDER)
        container.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        self._dir_badge = Badge(inner, text="QUECHUA  \u21C4  ESPA\u00d1OL")
        self._dir_badge.pack(side="left")

        ctk.CTkLabel(inner, text="", fg_color=BORDER, width=1, height=24).pack(side="left", padx=14)

        self._dir_label = ctk.CTkLabel(inner, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self._dir_label.pack(side="left", padx=(0, 8))
        self._dir_menu = ctk.CTkOptionMenu(
            inner,
            values=[],
            command=self._on_dir_change,
            width=200,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        )
        self._dir_menu.pack(side="left")

    def _build_text_cards(self):
        text_frame = ctk.CTkFrame(self._main, fg_color="transparent")
        text_frame.pack(fill="both", expand=True)

        src_card = Card(text_frame, accent_color=ACCENT)
        src_card.pack(fill="both", expand=True, pady=(0, 8))
        src_header = ctk.CTkFrame(src_card, fg_color="transparent")
        src_header.pack(fill="x", padx=18, pady=(14, 0))
        self._src_eyebrow = EyebrowLabel(src_header, "")
        self._src_eyebrow.pack(side="left")
        self._src_mic_btn = IconButton(src_header, text="Dictar", icon=icons.mic, icon_active=icons.mic_filled,
                                       command=self._on_src_mic_click)
        self._src_mic_btn.pack(side="right")
        self._src_text = ctk.CTkTextbox(
            src_card,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            height=100,
            corner_radius=8,
            fg_color=SURFACE_ALT,
            border_width=0,
            text_color=TEXT_PRIMARY,
        )
        self._src_text.pack(fill="both", expand=True, padx=18, pady=(8, 16))
        self._src_text.bind("<KeyRelease>", self._on_text_change)

        # Translate button
        ctr_row = ctk.CTkFrame(text_frame, fg_color="transparent")
        ctr_row.pack(fill="x", pady=4)

        sep_left = ctk.CTkFrame(ctr_row, fg_color=BORDER, height=1)
        sep_left.pack(side="left", fill="x", expand=True)
        sep_left.pack(side="left", padx=(0, 8))

        self._swap_btn = ctk.CTkButton(
            ctr_row,
            text="  Traducir",
            image=icons.arrows,
            width=160,
            height=36,
            corner_radius=BUTTON_RADIUS,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            cursor="hand2",
            command=self._translate_text_input,
        )
        self._swap_btn.pack(side="left", padx=8)

        sep_right = ctk.CTkFrame(ctr_row, fg_color=BORDER, height=1)
        sep_right.pack(side="left", fill="x", expand=True)
        sep_right.pack(side="left", padx=(8, 0))

        # Target card
        tgt_card = Card(text_frame, accent_color=ACCENT_SECONDARY)
        tgt_card.pack(fill="both", expand=True, pady=(8, 0))
        tgt_header = ctk.CTkFrame(tgt_card, fg_color="transparent")
        tgt_header.pack(fill="x", padx=18, pady=(14, 0))
        self._tgt_eyebrow = EyebrowLabel(tgt_header, "")
        self._tgt_eyebrow.pack(side="left")
        self._speak_tgt_btn = IconButton(tgt_header, text="Escuchar", icon=icons.speaker,
                                         command=self._speak_translated)
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
        self._tgt_text.pack(fill="both", expand=True, padx=18, pady=(8, 16))

    def _build_status_bar(self):
        self._progress = ctk.CTkProgressBar(
            self._main, mode="indeterminate", corner_radius=3, height=3,
            fg_color=SURFACE, progress_color=ACCENT,
        )
        self._progress.pack(fill="x", pady=(8, 8))
        self._progress.pack_forget()

        self._status = StatusBar(self._main)
        self._status.pack(fill="x")

    # -------------------------------------------------------------- idioma

    def _on_lang_change(self, lang: str):
        self._lang = lang
        self._apply_language()

    def _apply_language(self):
        self._subtitle_lbl.configure(text=i18n.get(self._lang, "app_subtitle"))
        self._dir_label.configure(text=i18n.get(self._lang, "dir_label"))
        self._dir_badge.set_text(i18n.get(self._lang, "dir_badge"))
        self._dir_menu.configure(values=i18n.dir_labels(self._lang))
        self._dir_menu.set(i18n.dir_label(self._lang, self._direction_code))
        self._src_eyebrow.configure(text=i18n.get(self._lang, "src_eyebrow").upper())
        self._tgt_eyebrow.configure(text=i18n.get(self._lang, "tgt_eyebrow").upper())
        self._update_mic_btn_text()
        self._swap_btn.configure(text="  " + i18n.get(self._lang, "translate"))
        self._update_speak_btn_text()
        self._status.set_status(i18n.get(self._lang, "status_ready"), state="idle")

    def _update_mic_btn_text(self):
        txt = i18n.get(self._lang, "src_detener") if self._src_mic_recording else i18n.get(self._lang, "src_dictar")
        self._src_mic_btn.set_active(self._src_mic_recording)
        self._src_mic_btn.configure(text=f"  {txt}" if self._src_mic_btn._icon else txt)

    def _update_speak_btn_text(self):
        self._speak_tgt_btn.configure(text=f"  {i18n.get(self._lang, 'listen')}")

    def _on_dir_change(self, label: str):
        self._direction_code = i18n.dir_code(label)

    # ------------------------------------------------------------- eventos

    def _on_text_change(self, event=None):
        pass

    def _on_src_mic_click(self):
        if not self._src_mic_recording:
            self._src_mic_recording = True
            self._update_mic_btn_text()
            self._recorder.start_recording()
            self._status.set_status(i18n.get(self._lang, "status_recording"), state="busy")
        else:
            self._src_mic_recording = False
            self._update_mic_btn_text()
            self._status.set_status(i18n.get(self._lang, "status_processing"), state="busy")
            self.update_idletasks()
            audio, peak = self._recorder.stop_recording()
            if audio is None or len(audio) < 8000:
                self._status.set_status(i18n.get(self._lang, "status_audio_short"), state="error")
                return
            if peak < 0.01:
                self._status.set_status(i18n.get(self._lang, "status_volume_low", peak=peak), state="error")
                return
            task_id = self._last_audio_task_id + 1
            self._last_audio_task_id = task_id
            self._processing_queue.put(("audio", audio, task_id))

    def _translate_text_input(self):
        text = self._src_text.get("0.0", "end").strip()
        if not text:
            return
        self._status.set_status(i18n.get(self._lang, "status_translating_text"), state="busy")
        self._progress.pack(fill="x", pady=(8, 8))
        self._progress.start()
        self._swap_btn.configure(state="disabled", text=i18n.get(self._lang, "translating"))
        self.update_idletasks()
        self._processing_queue.put(("text", text, 0))

    def _speak_translated(self):
        text = self._tgt_text.get("0.0", "end").strip()
        if not text:
            return
        tts_lang = "qu" if self._direction_code == "es_to_qu" else "es"
        self._status.set_status(i18n.get(self._lang, "status_listening"), state="busy")
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
        self._status.set_status(i18n.get(self._lang, "status_error", msg=msg), state="error")
        self._progress.stop()
        self._progress.pack_forget()
        self._swap_btn.configure(state="normal", text="  " + i18n.get(self._lang, "translate"))

    def _process_audio(self, audio, task_id):
        result, detected_lang = self._recognizer.transcribe(audio)
        if task_id != self._last_audio_task_id:
            return
        if not result:
            self.after(0, lambda: self._status.set_status(i18n.get(self._lang, "status_no_speech"), state="error"))
            self.after(0, lambda: (self._progress.stop(), self._progress.pack_forget()))
            return
        self.after(0, lambda: self._update_src_text(result))
        self.after(0, lambda: self._status.set_status(i18n.get(self._lang, "status_translating"), state="busy"))
        dir_param = self._direction_code if self._direction_code != "auto" else None
        translation = self._translator.translate(result, direction=dir_param)
        if task_id != self._last_audio_task_id:
            return
        self.after(0, lambda t=translation: self._update_tgt_text(t))
        self.after(0, lambda: self._status.set_status(i18n.get(self._lang, "status_done"), state="idle"))
        self.after(0, lambda: (self._progress.stop(), self._progress.pack_forget()))

    def _process_text(self, text):
        start = time.time()
        dir_param = self._direction_code if self._direction_code != "auto" else None
        translation = self._translator.translate(text, direction=dir_param)
        elapsed = time.time() - start
        self.after(0, lambda: self._update_tgt_text(translation))
        self.after(0, lambda t=elapsed: self._status.set_status(i18n.get(self._lang, "status_done_timed", t=t), state="idle"))
        self.after(0, lambda: (self._progress.stop(), self._progress.pack_forget()))
        self.after(0, lambda: self._swap_btn.configure(state="normal", text="  " + i18n.get(self._lang, "translate")))

    def _update_src_text(self, text: str):
        self._src_text.delete("0.0", "end")
        self._src_text.insert("0.0", text)

    def _update_tgt_text(self, text: str):
        self._tgt_text.delete("0.0", "end")
        self._tgt_text.insert("0.0", text)

    def destroy(self):
        self._running = False
        super().destroy()
