# src/vad.py
from typing import Generator
import numpy as np

CHUNK_MS = 20
# normalized RMS
ENERGY_THRESHOLD = 0.02 # adjust based on files 
MIN_SPEECH_MS = 20     # 0.8 sec of speech to confirm greeting start
MIN_SILENCE_MS = 1200   # 1.2 sec of silence to confirm greeting end

SPEECH_FRAMES_REQD = MIN_SPEECH_MS // CHUNK_MS
SILENCE_FRAMES_REQD = MIN_SILENCE_MS // CHUNK_MS

def rms_energy(samples: np.ndarray) -> float:
    samples = samples.astype(np.float32)
    return np.sqrt(np.mean(samples ** 2))

def detect_greeting_end(audio_stream: Generator[bytes, None, None], stop_event=None):
    speech_frames = 0
    silence_frames = 0
    current_time_ms = 0
    heard_speech = False

    for chunk in audio_stream:
        if stop_event and stop_event.is_set():
            return

        samples = np.frombuffer(chunk, dtype=np.int16) / 32768.0
        energy = rms_energy(samples)
        print(f"Time {current_time_ms}ms: RMS energy = {energy}")

        # VAD state machine
        if energy > ENERGY_THRESHOLD:
            speech_frames += 1
            silence_frames = 0
            if speech_frames >= SPEECH_FRAMES_REQD:
                heard_speech = True
        else:
            if heard_speech:
                silence_frames += 1
                speech_frames = 0
                if silence_frames >= SILENCE_FRAMES_REQD:
                    print(f"Greeting end detected at {current_time_ms}ms")
                    yield {
                        "timestamp_ms": current_time_ms - MIN_SILENCE_MS,
                        "mode": "vad",
                        "status": "sent"
                    }
                    if stop_event: 
                        stop_event.set()
                    return
            else:
                speech_frames = 0

        # increment time stamp
        current_time_ms += CHUNK_MS
