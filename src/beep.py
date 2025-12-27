# src/beep.py
from typing import Generator
import numpy as np
import sys
from pathlib import Path

# add project root (retapeAI) to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils.calculate_goertzel import calculate_goertzel

CHUNK_MS = 20        
BEEP_FREQS = [850, 900, 950, 1000, 1050, 1100, 1150]

# A pure tone usually occupies > 70% of the energy in a chunk
RATIO_THRESHOLD = 0.5
# Minimum energy floor to ignore absolute silence/background hiss
ENERGY_FLOOR = 1e-6

# 10 consecutive chunks (~200ms) for beep start
CONSECUTIVE_REQD = 10
# 4 consecutive chunks (~80ms) below threshold to confirm beep end
BEEP_END_CONSECUTIVE = 4 

# Safety buffer after beep end
BUFFER_MS = 200     

def detect_beep(audio_stream: Generator[bytes, None, None], stop_event=None):
    # initialize state variables
    state = "LISTENING"
    beep_counter = 0
    miss_counter = 0
    current_time_ms = 0

    for chunk in audio_stream:
        # check for stop event
        if stop_event and stop_event.is_set():
            return
        
        samples = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
        samples /= 32768.0  
        # calculate total Energy in the chunk
        total_energy = np.sum(samples**2) / len(samples)
        # calculate Goertzel Power
        powers = [calculate_goertzel(samples, freq) for freq in BEEP_FREQS]
        max_target_power = max(powers)
        # calculate ratio
        if total_energy > ENERGY_FLOOR:
            energy_ratio = max_target_power / total_energy
        else:
            energy_ratio = 0

        # print(f"Time {current_time_ms}ms: Ratio = {energy_ratio:.3f}, Energy = {total_energy:.4f}")
        is_beep_present = energy_ratio > RATIO_THRESHOLD

        if state == "LISTENING":
            if is_beep_present:
                beep_counter += 1
                if beep_counter >= CONSECUTIVE_REQD:
                    state = "BEEPING"
                    beep_counter = 0
                    miss_counter = 0
            else:
                beep_counter = 0

        elif state == "BEEPING":
            if not is_beep_present:
                miss_counter += 1
                if miss_counter >= BEEP_END_CONSECUTIVE:
                    trigger_time = current_time_ms + BUFFER_MS
                    yield {
                        "timestamp_ms": trigger_time,
                        "mode": "beep",
                        "status": "sent"
                    }
                    if stop_event: stop_event.set()
                    return
            else:
                miss_counter = 0

        # increment time stamp
        current_time_ms += CHUNK_MS
    
    # this runs only if loop finishes without detecting beep
    if stop_event and stop_event.is_set():
        return
    yield {
        "timestamp_ms": current_time_ms,
        "mode": None,
        "status": "sent"
    }