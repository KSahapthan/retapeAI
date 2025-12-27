# utils/calculate_goertzel.py
import numpy as np

def calculate_goertzel(chunk: np.ndarray, target_freq=1000, sample_rate=8000) -> float:
    """
    Compute the Goertzel power for a single-frequency detection
    chunk: 1D numpy array of int16 samples
    Returns: float power
    """
    N = len(chunk)
    k = int(0.5 + (N * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / N
    coeff = 2.0 * np.cos(omega)

    # Goertzel algorithm
    s0, s1, s2 = 0.0, 0.0, 0.0
    for sample in chunk:
        s0 = float(sample) + coeff * s1 - s2
        s2 = s1
        s1 = s0

    power = s1**2 + s2**2 - coeff * s1 * s2
    return power
