# src/vad.py
from typing import Generator
import numpy as np

CHUNK_MS = 20

# How much louder than background noise the audio must be (1.5 = 50% louder)
ENERGY_RATIO_THRESHOLD = 1.5
# Initial guess for noise floor (will adapt)
INITIAL_NOISE_FLOOR = 0.01
# Smoothing factor for the noise floor window (0.95 = slow adaptation)
ALPHA = 0.95

# 0.3 sec of speech to confirm greeting start
MIN_SPEECH_MS = 300     
# 1.2 sec of silence to confirm greeting end
MIN_SILENCE_MS = 1200  

SPEECH_FRAMES_REQD = MIN_SPEECH_MS // CHUNK_MS
SILENCE_FRAMES_REQD = MIN_SILENCE_MS // CHUNK_MS

def rms_energy(samples: np.ndarray) -> float:
    samples = samples.astype(np.float32)
    return np.sqrt(np.mean(samples ** 2))

def detect_greeting_end(audio_stream: Generator[bytes, None, None], stop_event=None):
    # initialize state variables
    speech_frames = 0
    silence_frames = 0
    current_time_ms = 0
    heard_speech = False
    
    # window state: noise floor tracks the background energy level
    noise_floor = INITIAL_NOISE_FLOOR

    for chunk in audio_stream:
        # check for stop event
        if stop_event and stop_event.is_set():
            return

        samples = np.frombuffer(chunk, dtype=np.int16) / 32768.0
        energy = rms_energy(samples)
        
        # calculate energy ratio against current noise floor
        energy_ratio = energy / noise_floor if noise_floor > 1e-6 else 0
        
        # update noise floor window if current chunk is "quiet" (likely background noise)
        if energy < noise_floor * ENERGY_RATIO_THRESHOLD:
            noise_floor = (ALPHA * noise_floor) + ((1 - ALPHA) * energy)

        # print(f"Time {current_time_ms}ms: Ratio = {energy_ratio:.2f}, Floor = {noise_floor:.4f}")

        # VAD state machine using ratio instead of absolute threshold
        # Added a small absolute floor check (0.005) to ignore dead silence
        if energy_ratio > ENERGY_RATIO_THRESHOLD and energy > 0.005:
            speech_frames += 1
            silence_frames = 0
            if speech_frames >= SPEECH_FRAMES_REQD:
                heard_speech = True
        else:
            if heard_speech:
                silence_frames += 1
                speech_frames = 0
                if silence_frames >= SILENCE_FRAMES_REQD:
                    yield {
                        "timestamp_ms": current_time_ms,
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
    
    # this runs only if loop finishes without detecting silence
    if stop_event and stop_event.is_set():
        return
    yield {
        "timestamp_ms": current_time_ms,
        "mode": None,
        "status": "sent"
    }