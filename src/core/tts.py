import asyncio
import os
import subprocess
import tempfile
import winsound
import edge_tts
from src.utils.config import TTS_VOICE_ES, TTS_VOICE_QU

TEMP_DIR = tempfile.gettempdir()


def _find_ffmpeg() -> str:
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpegio", "ffmpeg-downloader", "ffmpeg", "bin", "ffmpeg.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    for p in os.environ.get("PATH", "").split(os.pathsep):
        for name in ("ffmpeg.exe", "ffmpeg"):
            full = os.path.join(p, name)
            if os.path.isfile(full):
                return full
    return "ffmpeg.exe"


_FFMPEG_PATH = _find_ffmpeg()


class TextToSpeech:
    def __init__(self):
        self._loop: asyncio.AbstractEventLoop | None = None

    def _get_loop(self):
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop

    async def _speak_async(self, text: str, voice: str) -> bytes:
        communicate = edge_tts.Communicate(text, voice)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return audio_bytes

    def _mp3_to_wav(self, mp3_path: str, wav_path: str) -> None:
        subprocess.run(
            [_FFMPEG_PATH, "-y", "-i", mp3_path, "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", wav_path],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )

    def speak(self, text: str, language: str = "qu") -> None:
        voice = TTS_VOICE_QU if language == "qu" else TTS_VOICE_ES
        loop = self._get_loop()
        try:
            audio_bytes = loop.run_until_complete(self._speak_async(text, voice))
        except RuntimeError:
            loop.close()
            self._loop = asyncio.new_event_loop()
            audio_bytes = self._loop.run_until_complete(self._speak_async(text, voice))

        if not audio_bytes:
            print("No se generó audio TTS")
            return

        mp3_path = os.path.join(TEMP_DIR, "traductor_tts_output.mp3")
        with open(mp3_path, "wb") as f:
            f.write(audio_bytes)

        wav_path = os.path.join(TEMP_DIR, "traductor_tts_output.wav")
        try:
            self._mp3_to_wav(mp3_path, wav_path)
            winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Error reproduciendo audio: {e}")

    def speak_sync(self, text: str, language: str = "es") -> None:
        self.speak(text, language)
