"""Sintetiza desde cero los efectos del video, sin usar muestras externas."""
import wave
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "sfx"
RATE = 48000
RNG = np.random.default_rng(20261103)


def save(name, signal):
    peak = np.max(np.abs(signal))
    data = signal / peak * 0.85
    fade = min(len(data), int(0.01 * RATE))
    data[:fade] *= np.linspace(0, 1, fade)
    data[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(OUT / name), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes((data * 32767).astype(np.int16).tobytes())
    print(name, f"{len(data) / RATE:.2f}s")


def swept_noise(duration, low, high, power=1.0):
    """Ruido blanco por un paso bajo cuya frecuencia de corte sube de low a high."""
    n = int(duration * RATE)
    noise = RNG.standard_normal(n)
    cutoff = low + (high - low) * np.linspace(0, 1, n) ** power
    alpha = 1 - np.exp(-2 * np.pi * cutoff / RATE)
    out = np.zeros(n)
    state = 0.0
    for i in range(n):
        state += alpha[i] * (noise[i] - state)
        out[i] = state
    return out


def whoosh():
    n = int(0.8 * RATE)
    position = np.linspace(0, 1, n)
    envelope = np.sin(np.pi * position**0.7) ** 2
    rising = swept_noise(0.8, 300, 3500)
    return rising * envelope


def water():
    n = int(4.5 * RATE)
    out = np.zeros(n)
    time = np.arange(n) / RATE
    base = swept_noise(4.5, 900, 900)
    out += 0.25 * base * np.minimum(time / 0.5, 1) * np.minimum((4.5 - time) / 2, 1)
    for _ in range(90):
        # Cada burbuja es un tono breve cuya frecuencia sube mientras se apaga.
        start = RNG.uniform(0, 4.2)
        length = RNG.uniform(0.03, 0.12)
        freq = RNG.uniform(500, 1800)
        m = int(length * RATE)
        i0 = int(start * RATE)
        local = np.arange(m) / RATE
        tone = np.sin(2 * np.pi * (freq * local + 0.5 * freq * 2.5 * local**2)) * np.exp(-local / (length / 4))
        out[i0:i0 + m] += RNG.uniform(0.25, 0.8) * tone[: len(out[i0:i0 + m])]
    return out


def riser():
    n = int(4.0 * RATE)
    position = np.linspace(0, 1, n)
    phase = 2 * np.pi * np.cumsum(70 * 2 ** (position * 3.2)) / RATE
    tone = np.sin(phase) + 0.45 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    air = swept_noise(4.0, 400, 6000, power=2.0)
    return (0.6 * tone + 0.9 * air) * position**2.2


def ding():
    n = int(1.8 * RATE)
    time = np.arange(n) / RATE
    partials = [(880, 1.0, 0.55), (1760, 0.45, 0.35), (2389, 0.3, 0.22), (3520, 0.14, 0.14)]
    return sum(a * np.sin(2 * np.pi * f * time) * np.exp(-time / d) for f, a, d in partials)


def main():
    OUT.mkdir(exist_ok=True)
    save("whoosh.wav", whoosh())
    save("water.wav", water())
    save("riser.wav", riser())
    save("ding.wav", ding())


if __name__ == "__main__":
    main()
