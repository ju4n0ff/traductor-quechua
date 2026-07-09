import threading
import numpy as np
import sounddevice as sd
from src.utils.config import SAMPLE_RATE, CHANNELS, DTYPE


class AudioRecorder:
    def __init__(self):
        self._recording = False
        self._audio_data: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start_recording(self) -> None:
        with self._lock:
            if self._recording:
                return
            self._audio_data = []
            self._recording = True

        def callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            if self._recording:
                self._audio_data.append(indata.copy())

        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=callback,
            blocksize=2048,
        )
        self._stream.start()

    def stop_recording(self) -> tuple[np.ndarray | None, float]:
        with self._lock:
            if not self._recording:
                return None, 0.0
            self._recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if not self._audio_data:
            return None, 0.0

        audio = np.concatenate(self._audio_data, axis=0).flatten()
        peak = float(np.max(np.abs(audio))) if len(audio) > 0 else 0.0
        return audio, peak

    def get_devices(self):
        return sd.query_devices()
