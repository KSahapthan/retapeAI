# src/eda.py
from pathlib import Path
import wave
import numpy as np
from scipy.signal import periodogram

# configuration (pipeline-aware)
TARGET_SR = 8000
CHUNK_MS = 20
CHUNK_SAMPLES = int(TARGET_SR * CHUNK_MS / 1000)
SILENCE_AMPLITUDE_THRESHOLD = 50  

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

wav_files = sorted(DATA_DIR.glob("*.wav"))

if not wav_files:
    raise RuntimeError(f"No WAV files found in {DATA_DIR}")

# EDA loop
for audio_path in wav_files:
    with wave.open(str(audio_path), "rb") as wf:
        channels = wf.getnchannels()
        sample_rate = wf.getframerate()
        sample_width = wf.getsampwidth()
        nframes = wf.getnframes()

        print(f"File: {audio_path.name}")
        print("Channels:", channels)
        print("Sample rate:", sample_rate)
        print("Sample width (bytes):", sample_width)
        print("Total frames:", nframes)

        frames = wf.readframes(nframes)
        samples = np.frombuffer(frames, dtype=np.int16)

        # global signal sanity
        print("Max amplitude:", int(np.max(samples)))
        print("Min amplitude:", int(np.min(samples)))

        silence_ratio = np.mean(np.abs(samples) < SILENCE_AMPLITUDE_THRESHOLD)
        print("Silence ratio:", round(float(silence_ratio), 4))

        # chunk-level energy statistics
        energies = []
        for i in range(0, len(samples) - CHUNK_SAMPLES + 1, CHUNK_SAMPLES):
            chunk = samples[i:i + CHUNK_SAMPLES].astype(np.float32)
            energy = np.mean(chunk ** 2)
            energies.append(energy)
        if energies:
            energies = np.array(energies)
            print(
                "Chunk energy (min / mean / max):",
                round(float(np.min(energies)), 2),
                "/",
                round(float(np.mean(energies)), 2),
                "/",
                round(float(np.max(energies)), 2),
            )
        else:
            print("No full chunks available for energy analysis")

        # frequency sanity check (Goertzel relevance)
        if sample_rate > 0:
            freqs, power_spec = periodogram(samples, fs=sample_rate)
            dominant_freq = freqs[np.argmax(power_spec)]
            print("Dominant frequency (Hz):", round(float(dominant_freq), 2))

print("\nEDA complete.")

# audio is mostly silence (55–76%), so dropping the final partial 20 ms frame is safe and matches real-time behavior
# chunk-level energy varies widely across files, so fixed-size framing and conservative thresholds are required
# frequency content differs significantly (hum, noise, tones); Goertzel is necessary since energy alone would cause false positives
# mixed sample rates (8 kHz / 44.1 kHz) validate the need for resampling to keep timing and frequency detection correct
