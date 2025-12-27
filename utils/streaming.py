# utils/streaming.py
import wave
import time
import numpy as np
from typing import Generator
from scipy.signal import resample_poly

TARGET_SR = 8000

def stream_wav(
    file_path: str,
    chunk_ms: int = 20,
) -> Generator[bytes, None, None]:
    """
    Streams WAV audio normalized to:
    - mono
    - 16-bit PCM
    - 8 kHz
    - fixed-duration real-time chunks (20ms) standard for VoIP applications
    """
    with wave.open(file_path, "rb") as wf:
        src_sr = wf.getframerate()
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()

        if sample_width != 2:
            raise ValueError("Only 16-bit PCM supported")

        target_samples = int(TARGET_SR * chunk_ms / 1000)
        src_chunk = int(src_sr * chunk_ms / 1000)

        # buffer to protect time correctness 
        # when resampling produces uneven chunk sizes (159/161)
        buffer = np.empty(0, dtype=np.int16)

        while True:
            frames = wf.readframes(src_chunk)
            if not frames:
                break

            samples = np.frombuffer(frames, dtype=np.int16)

            # stereo → mono
            if channels == 2:
                samples = samples.reshape(-1, 2).mean(axis=1)
            elif channels != 1:
                raise ValueError("Unsupported channel count")

            # resample if needed
            if src_sr != TARGET_SR:
                samples = resample_poly(samples, TARGET_SR, src_sr)

            buffer = np.concatenate([buffer, samples.astype(np.int16)])

            while len(buffer) >= target_samples:
                out = buffer[:target_samples]
                buffer = buffer[target_samples:]

                yield out.tobytes()

                # simulate real-time streaming
                time.sleep(chunk_ms / 1000)

# Do NOT flush leftover buffer
# Intentionally drop last partial frame to keep chunk sizes uniform