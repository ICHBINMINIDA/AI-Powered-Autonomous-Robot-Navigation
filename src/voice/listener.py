"""Microphone input and offline VOSK speech recognition."""

from __future__ import annotations

import json
import queue
import re
from typing import Optional

from vosk import KaldiRecognizer, Model


class VoiceListener:
    """Owns the VOSK recognizers and audio queue used by the state machine."""

    def __init__(self, model_path: str, sample_rate: int, wake_word: str) -> None:
        self.sample_rate = sample_rate
        self.wake_word = wake_word.lower().strip()
        self.audio_queue: queue.Queue[bytes] = queue.Queue()

        model = Model(model_path)
        self.wake_recognizer = KaldiRecognizer(
            model,
            sample_rate,
            json.dumps([self.wake_word]),
        )
        self.command_recognizer = KaldiRecognizer(model, sample_rate)

    def audio_callback(self, indata, frames, time_info, status) -> None:  # noqa: ANN001
        """sounddevice callback: copy microphone bytes into a thread-safe queue."""
        del frames, time_info
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))

    def get_audio(self, timeout: float = 0.01) -> Optional[bytes]:
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def heard_wake_word(self, audio_bytes: bytes | None) -> bool:
        if not audio_bytes:
            return False

        if not self.wake_recognizer.AcceptWaveform(audio_bytes):
            return False

        text = json.loads(self.wake_recognizer.Result()).get("text", "")
        text = re.sub(r"\s+", " ", text.lower().strip())
        return text == self.wake_word

    def accept_command(self, audio_bytes: bytes | None) -> Optional[str]:
        """Return a finalized command, or None while speech is still being captured."""
        if not audio_bytes or not self.command_recognizer.AcceptWaveform(audio_bytes):
            return None

        text = json.loads(self.command_recognizer.Result()).get("text", "")
        return text.lower().strip()

    def reset_wake_recognizer(self) -> None:
        self.wake_recognizer.Reset()

    def reset_command_recognizer(self) -> None:
        self.command_recognizer.Reset()
