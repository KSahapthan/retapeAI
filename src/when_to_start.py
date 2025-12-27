# src/when_to_start.py
from pathlib import Path
import sys
from typing import Generator

# setup project path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils.streaming import stream_wav
from beep import detect_beep  # Tier 2 beep detector

# Tiered Voicemail Trigger
class VoicemailTrigger:
    """
    Orchestrates multi-tier detection for when to start voicemail playback.
    Currently implements only Tier 2 (Goertzel beep detection)
    """

    def __init__(self, audio_stream: Generator[bytes, None, None]):
        self.audio_stream = audio_stream
        # Future states for Tier 1/3
        self.speech_state = None
        self.max_time_ms = 25000  # fallback timeout
        self.current_time_ms = 0

    def run(self):
        """
        Processes the audio stream and yields an event when voicemail should be triggered.
        """
        # TODO: Tier 1 — VAD / speech end detection (no beep)

        # Tier 2: Beep detection
        for event in detect_beep(self.audio_stream):
            yield event
            return  # Stop processing once beep triggers voicemail

        # TODO: Tier 3 — Hard timeout fail-safe
        # These tiers can be implemented by analyzing energy/speech states or elapsed time

# main script
if __name__ == "__main__":
    audio_path = "data/vm6_output.wav"

    # real-time generator of 20ms chunks
    stream = stream_wav(audio_path)  

    trigger_system = VoicemailTrigger(stream)

    for event in trigger_system.run():
        print(event)
