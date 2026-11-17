"""Synthetic test material with known ground truth (no real recordings are used or needed).

  ref/HT-T001 eski riddim.wav      140 BPM, half-time snare, sparse kick, square bass, pentatonic bleeps
  ref/HT-T002 2-step grime.wav     140 BPM, 2-step kick, shuffled hats, saw bass, string chords
  ref/HT-T003 garage outgroup.wav  132 BPM 2-step garage, warped bass, organ chords
  new/A vocal version.wav          HT-T001 with a synthetic MC on top
  new/A vinyl +6pct.wav            HT-T001 played 6% fast, crackle and rolled-off top (a worn 12-inch)
  new/D unknown riddim.wav         a riddim not in the index
  new/D vocal version.wav          an MC over D: should match D once D has been ingested
  set/pirate set.wav               talk, B, A vocal, A vinyl, D, C, with hiss: a mock radio set
"""
import os
import sys

import numpy as np
import soundfile as sf

SR = 44100
rng = np.random.default_rng(7)


def osc(freq, dur, kind='sine'):
    t = np.arange(int(dur * SR)) / SR
    ph = 2 * np.pi * freq * t
    if kind == 'square':
        return np.sign(np.sin(ph)) * 0.7
    if kind == 'saw':
        return 2 * ((freq * t) % 1.0) - 1
    return np.sin(ph)


def env(n, a=0.005, d=0.25):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def kick(dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.12)


def snare(dur=0.25):
    n = int(dur * SR)
    return (rng.standard_normal(n) * 0.6 + osc(190, dur) * 0.4) * env(n, 0.001, 0.07)


def hat(dur=0.06):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    x = np.diff(x, prepend=0)          # crude high-pass
    return x * env(n, 0.0005, 0.015) * 0.5


def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += gain * sig[:j - i]


def riddim(bpm, bars, kick_steps, snare_steps, hat_steps, swing, bass_notes, bass_kind, lead, chords=None, seed=0):
    r = np.random.default_rng(seed)
    beat = 60 / bpm; step = beat / 4; bar = beat * 4
    n = int(bars * bar * SR) + SR
    drums, bass, mel = np.zeros(n), np.zeros(n), np.zeros(n)
    for b in range(bars):
        t0 = b * bar
        for s in kick_steps:
            place(drums, kick(), t0 + s * step, 1.0)
        for s in snare_steps:
            place(drums, snare(), t0 + s * step, 0.8)
        for s in hat_steps:
            dt = step * swing if s % 2 else 0
            place(drums, hat(), t0 + s * step + dt, 0.35 + 0.1 * r.random())
        note = bass_notes[b % len(bass_notes)]
        bn = osc(note, bar * 0.95, bass_kind) * env(int(bar * 0.95 * SR), 0.01, 1.2)
        place(bass, bn, t0, 0.55)
        if lead:
            notes, rhythm, kind = lead
            for k, s in enumerate(rhythm):
                f = notes[(b * len(rhythm) + k) % len(notes)]
                ln = osc(f, step * 1.5, kind) * env(int(step * 1.5 * SR), 0.002, 0.08)
                place(mel, ln, t0 + s * step, 0.22)
        if chords:
            for f in chords[b % len(chords)]:
                place(mel, osc(f, bar * 0.9) * env(int(bar * 0.9 * SR), 0.05, 0.9), t0, 0.08)
    mix = drums * 0.7 + bass + mel
    return (mix / np.max(np.abs(mix)) * 0.8).astype(np.float32)


def mc(dur, f0=118, seed=3, rate=6.5):
    """Synthetic MC: a pitched pulse train through moving vowel formants, chopped into syllables."""
    r = np.random.default_rng(seed)
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (1 + 0.08 * np.sin(2 * np.pi * 0.7 * t) + 0.03 * r.standard_normal(n).cumsum() / np.sqrt(n))
    src = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + 0.1 * r.standard_normal(n)
    from scipy.signal import lfilter
    out = np.zeros(n)
    seg = int(SR / rate)
    for i in range(0, n, seg):
        F1, F2 = r.choice([300, 450, 700, 850]), r.choice([900, 1200, 1700, 2200])
        x = src[i:i + seg]
        for F, bw in ((F1, 90), (F2, 120)):
            rr = np.exp(-np.pi * bw / SR); th = 2 * np.pi * F / SR
            x = lfilter([1 - rr], [1, -2 * rr * np.cos(th), rr * rr], x)
        e = np.sin(np.linspace(0, np.pi, len(x))) ** 0.6 if r.random() > 0.15 else np.zeros(len(x))
        out[i:i + seg] = x * e
    return (out / (np.max(np.abs(out)) + 1e-9) * 0.7).astype(np.float32)


def speed(y, f):
    n = int(len(y) / f)
    return np.interp(np.arange(n) * f, np.arange(len(y)), y).astype(np.float32)


def worn(y, seed=5):
    r = np.random.default_rng(seed)
    from scipy.signal import butter, lfilter
    b, a = butter(2, 7000 / (SR / 2))
    y = lfilter(b, a, y)
    crackle = (r.random(len(y)) > 0.9995) * r.standard_normal(len(y)) * 0.4
    return (y + crackle + 0.004 * r.standard_normal(len(y))).astype(np.float32)


def talk(dur, seed=11):
    return mc(dur, f0=105, seed=seed, rate=4.5) * 0.6


def main(out):
    os.makedirs(os.path.join(out, 'ref'), exist_ok=True)
    os.makedirs(os.path.join(out, 'new'), exist_ok=True)
    os.makedirs(os.path.join(out, 'set'), exist_ok=True)
    E1, G1, A1, D2, C2, B1, F1 = 41.2, 49.0, 55.0, 73.4, 65.4, 61.7, 43.65
    A = riddim(140, 40, [0, 11], [8], [0, 8], 0.0, [E1, E1, G1, A1], 'square',
               ([659, 784, 880, 988, 1175, 880, 784, 659], [0, 3, 6, 10, 14], 'square'), seed=1)
    B = riddim(140, 40, [0, 10], [4, 12], list(range(0, 16, 2)) + [3, 7, 11, 15], 0.33, [D2, D2, C2, B1], 'saw', None,
               chords=[[293.7, 349.2, 440.0], [261.6, 329.6, 392.0]], seed=2)
    C = riddim(132, 36, [0, 6, 10], [4, 12], list(range(16)), 0.4, [A1, A1, D2, E1 * 2], 'saw', None,
               chords=[[440, 523.3, 659.3], [392, 493.9, 587.3]], seed=3)
    D = riddim(140, 36, [0, 3, 8], [12], [2, 6, 10, 14], 0.0, [F1, F1, C2, B1], 'sine',
               ([1046, 1318, 1568, 1318], [0, 4, 8, 9, 12], 'sine'), seed=4)
    Avoc = A + mc(len(A) / SR, seed=21)
    Dvoc = D + mc(len(D) / SR, f0=135, seed=22)
    Avin = worn(speed(A, 1.06))
    nz = lambda y: (y / np.max(np.abs(y)) * 0.8).astype(np.float32)
    sf.write(os.path.join(out, 'ref', 'HT-T001 eski riddim.wav'), A, SR)
    sf.write(os.path.join(out, 'ref', 'HT-T002 2-step grime.wav'), B, SR)
    sf.write(os.path.join(out, 'ref', 'HT-T003 garage outgroup.wav'), C, SR)
    sf.write(os.path.join(out, 'new', 'A vocal version.wav'), nz(Avoc), SR)
    sf.write(os.path.join(out, 'new', 'A vinyl +6pct.wav'), nz(Avin), SR)
    sf.write(os.path.join(out, 'new', 'D unknown riddim.wav'), D, SR)
    sf.write(os.path.join(out, 'new', 'D vocal version.wav'), nz(Dvoc), SR)
    s = lambda y, a, b: y[int(a * SR):int(b * SR)]
    parts = [talk(12), s(B, 5, 65), s(nz(Avoc), 10, 70), talk(8, 12), s(Avin, 0, 45), s(D, 3, 53), s(C, 0, 40), talk(6, 13)]
    radio = np.concatenate(parts)
    radio = np.tanh(2.0 * radio) * 0.6 + 0.01 * rng.standard_normal(len(radio))
    sf.write(os.path.join(out, 'set', 'pirate set.wav'), radio.astype(np.float32), SR)
    # ground truth for the set (seconds)
    t, truth = 0.0, []
    for name, p in zip(['talk', 'HT-T002', 'HT-T001 vocal', 'talk', 'HT-T001 vinyl', 'D', 'HT-T003', 'talk'], parts):
        truth.append((name, round(t, 1), round(t + len(p) / SR, 1)))
        t += len(p) / SR
    print('set ground truth:', truth)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'testaudio')
