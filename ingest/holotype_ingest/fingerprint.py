"""Landmark ('constellation') fingerprints, in the style Shazam made famous.

Three profiles:
  full   - the whole recording, 100 Hz to 3.8 kHz: identifies a specific recording or pressing.
  vocal  - the vocal stem only (when separation is available): tells a copy of a recording from a
           different vocal over the same riddim.
  riddim - the bass register only, 30 to 300 Hz: identifies the instrumental under an MC, so different
           vocal versions of one riddim match each other. If an instrumental stem is available (Demucs),
           the full profile run on that stem is stronger still.

A fingerprint is a set of hashes, each (anchor frequency, target frequency, time gap) for a pair of
spectral peaks, stored with the anchor's time. Fingerprints cannot be turned back into audio.
"""
import numpy as np
from scipy.ndimage import maximum_filter

PROFILES = {
    'full':   dict(sr=8000, n_fft=1024, hop=256, fmin=100.0, fmax=3800.0, nbhd=(15, 9), per_sec=24, fanout=8, dtmax=48, dfmax=96),
    'vocal':  dict(sr=8000, n_fft=1024, hop=256, fmin=150.0, fmax=3800.0, nbhd=(15, 9), per_sec=24, fanout=8, dtmax=48, dfmax=96),
    'riddim': dict(sr=2000, n_fft=1024, hop=128, fmin=30.0, fmax=300.0, nbhd=(7, 9), per_sec=12, fanout=8, dtmax=48, dfmax=60),
}


def frame_seconds(profile):
    p = PROFILES[profile]
    return p['hop'] / p['sr']


def spectrogram(y, p):
    n, hop = p['n_fft'], p['hop']
    if len(y) < n:
        y = np.pad(y, (0, n - len(y)))
    frames = 1 + (len(y) - n) // hop
    idx = np.arange(n)[None, :] + hop * np.arange(frames)[:, None]
    win = np.hanning(n).astype(np.float32)
    S = np.abs(np.fft.rfft(y[idx] * win, axis=1)).T          # (freq, time)
    return 20 * np.log10(S + 1e-6)


def peaks(y, profile):
    p = PROFILES[profile]
    S = spectrogram(y, p)
    freqs = np.fft.rfftfreq(p['n_fft'], 1 / p['sr'])
    band = (freqs >= p['fmin']) & (freqs <= p['fmax'])
    S = S.copy()
    S[~band, :] = S.min()
    local = maximum_filter(S, size=p['nbhd'], mode='constant', cval=S.min())
    floor = np.percentile(S[band], 60)
    f, t = np.nonzero((S == local) & (S > floor) & band[:, None])
    if len(f) == 0:
        return np.zeros((0, 2), dtype=np.int32)
    amp = S[f, t]
    # keep the strongest peaks, per_sec on average, spread across time
    frames_per_sec = p['sr'] / p['hop']
    keep = []
    block = int(frames_per_sec)
    for b0 in range(0, S.shape[1], block):
        sel = np.nonzero((t >= b0) & (t < b0 + block))[0]
        if len(sel) > p['per_sec']:
            sel = sel[np.argsort(amp[sel])[-p['per_sec']:]]
        keep.extend(sel.tolist())
    keep = np.array(sorted(keep, key=lambda i: (t[i], f[i])), dtype=np.int64)
    return np.stack([t[keep], f[keep]], axis=1).astype(np.int32)


def hashes(y, profile):
    """Return (hash uint32 array, anchor time-frame uint32 array)."""
    p = PROFILES[profile]
    pk = peaks(y, profile)
    hs, ts = [], []
    n = len(pk)
    for i in range(n):
        t1, f1 = pk[i]
        c = 0
        j = i + 1
        while j < n and c < p['fanout']:
            t2, f2 = pk[j]
            dt = t2 - t1
            if dt > p['dtmax']:
                break
            if dt >= 1 and abs(int(f2) - int(f1)) <= p['dfmax']:
                hs.append(((int(f1) & 0x3FF) << 16) | ((int(f2) & 0x3FF) << 6) | (int(dt) & 0x3F))
                ts.append(t1)
                c += 1
            j += 1
    return np.array(hs, dtype=np.uint32), np.array(ts, dtype=np.uint32)
