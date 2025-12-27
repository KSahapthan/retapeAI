# src/when_to_start.py
from pathlib import Path
import sys
from threading import Thread, Event
from queue import Queue, Empty

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils.streaming import stream_wav
from beep import detect_beep
from vad import detect_greeting_end

class VoicemailTrigger:
    """
    Tiered system:
    Tier 1 — VAD greeting-end detection
    Tier 2 — Beep detection (highest confidence)
    Tier 3 — Timeout (TODO)
    """

    def __init__(self, audio_path: str):
        self.audio_path = audio_path
        self.max_time_ms = 25000
        self.event_queue = Queue()
        self.stop_event = Event()

    def _run_beep_detection(self):
        """Run beep detection and send events to the queue."""
        beep_stream = stream_wav(self.audio_path)
        for event in detect_beep(beep_stream, stop_event=self.stop_event):
            if self.stop_event.is_set():
                return
            self.event_queue.put(event)
            self.stop_event.set()
            return

    def _run_vad_detection(self):
        """Run VAD detection and send events to the queue."""
        vad_stream = stream_wav(self.audio_path)
        for event in detect_greeting_end(vad_stream, stop_event=self.stop_event):
            if self.stop_event.is_set():
                return
            self.event_queue.put(event)
            self.stop_event.set()
            return

    def run(self):
        """
        Run beep and VAD detection in parallel. Yield the first event detected.
        """
        # Start threads for beep and VAD detection
        beep_thread = Thread(target=self._run_beep_detection)
        vad_thread = Thread(target=self._run_vad_detection)

        beep_thread.start()
        vad_thread.start()

        try:
            # Wait for the first event or timeout
            event = self.event_queue.get(timeout=self.max_time_ms / 1000)
            yield event
        except Empty:
            # Tier 3 — Hard timeout
            yield {
                "timestamp_ms": self.max_time_ms,
                "mode": "timeout",
                "status": "sent"
            }
        finally:
            # Signal threads to stop and wait for them to finish
            self.stop_event.set()
            beep_thread.join()
            vad_thread.join()


if __name__ == "__main__":
    audio_path = "data/vm6_output.wav"

    trigger = VoicemailTrigger(audio_path)

    for event in trigger.run():
        print(event)
