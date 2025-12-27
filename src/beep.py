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
TARGET_FREQ = 1000  
THRESHOLD = 0.5      
# 10 consecutive chunks (~200ms) for beep start
CONSECUTIVE_REQD = 10 
# Safety buffer after beep end
BUFFER_MS = 200     
# 4 consecutive chunks (~80ms) below threshold to confirm beep end
BEEP_END_CONSECUTIVE = 4 

def detect_beep(audio_stream: Generator[bytes, None, None], stop_event=None):
    """
    Detects beep start and end in a real-time audio stream.
    Yields a dictionary with:
        {
            "timestamp_ms": int,   
            "mode": "beep",
            "status": "sent"
        }
    """
    # state variables
    state = "LISTENING"
    # counts consecutive chunks above threshold to confirm beep start (hysteresis)
    beep_counter = 0
    # counts consecutive chunks below threshold to confirm beep end
    miss_counter = 0
    # running time stamp of the stream
    current_time_ms = 0

    for chunk in audio_stream:
        # check for stop event
        if stop_event and stop_event.is_set():
            return
        
        samples = np.frombuffer(chunk, dtype=np.int16)
        # normalize to -1.0 to 1.0 using linear amplitude normalization
        samples = samples / 32768.0  

        # calculate Goertzel power at target frequency
        power = calculate_goertzel(samples, TARGET_FREQ)
        print(f"Time {current_time_ms}ms: Goertzel power = {power}")

        # state machine for beep start detection
        if state == "LISTENING":
            if power > THRESHOLD:
                beep_counter += 1
                if beep_counter >= CONSECUTIVE_REQD:
                    state = "BEEPING"
                    beep_counter = 0
                    miss_counter = 0
            else:
                beep_counter = 0

        # state machine for beep end detection
        elif state == "BEEPING":
            if power < THRESHOLD:
                miss_counter += 1
                if miss_counter >= BEEP_END_CONSECUTIVE:  
                    trigger_time = current_time_ms + BUFFER_MS
                    print(f"Beep end detected at {current_time_ms}ms, trigger at {trigger_time}ms") 

                    yield {
                        "timestamp_ms": trigger_time,
                        "mode": "beep",
                        "status": "sent"
                    }

                    # propagate the stop event to halt other detectors
                    if stop_event: 
                        stop_event.set()

                    return
            else:
                miss_counter = 0

        # increment time stamp
        current_time_ms += CHUNK_MS
