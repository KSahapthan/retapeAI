# utils/calculate_goertzel.py
import numpy as np

def calculate_goertzel(chunk: np.ndarray, target_freq=1000, sample_rate=8000) -> float:
    """
    Compute the normalized Goertzel power for a single-frequency detection.
    chunk: 1D numpy array of float samples (normalized to -1.0 to 1.0)
    Returns: float power (normalized to be comparable to signal energy)
    """
    N = len(chunk)
    if N == 0:
        return 0.0

    # standard Goertzel Parameters
    k = int(0.5 + (N * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / N
    coeff = 2.0 * np.cos(omega)

    # Goertzel iteration
    s1, s2 = 0.0, 0.0
    for sample in chunk:
        s0 = float(sample) + coeff * s1 - s2
        s2 = s1
        s1 = s0

    # calculate raw power
    raw_power = s1**2 + s2**2 - coeff * s1 * s2

    # normalization to get a power value on the same scale as np.mean(samples**2)
    normalized_power = (2.0 * raw_power) / (N**2)
    
    return normalized_power