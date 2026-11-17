"""Fingerprint index: reference specimens plus every candidate ingested so far.

Stored as one .npz per profile plus a JSON catalogue, so it can live in the repository or on a laptop.
Matching votes on time offsets (the classic landmark method) and searches a range of playback speeds,
because DJs and worn turntables run records fast or slow.
"""
import json
import os

import numpy as np

from . import audio, fingerprint as fp

SPEEDS = [round(0.90 + 0.01 * i, 2) for i in range(21)]   # 0.90 .. 1.10, turntable pitch range and beyond


class Index:
    def __init__(self, root):
        self.root = root
        os.makedirs(root, exist_ok=True)
        self.cat_path = os.path.join(root, 'catalogue.json')
        self.catalogue = json.load(open(self.cat_path)) if os.path.exists(self.cat_path) else []
        self.data = {}
        for prof in fp.PROFILES:
            path = os.path.join(root, f'{prof}.npz')  # profiles absent from an item simply contribute no hashes
            if os.path.exists(path):
                z = np.load(path)
                self.data[prof] = [z['h'], z['t'], z['i']]
            else:
                self.data[prof] = [np.zeros(0, np.uint32), np.zeros(0, np.uint32), np.zeros(0, np.int32)]
        self._sorted = {}

    # ---- writing ---------------------------------------------------------------
    def find(self, ident=None, sha=None):
        for n, c in enumerate(self.catalogue):
            if (ident and c['id'] == ident) or (sha and c['sha256'] == sha):
                return n
        return None

    def add(self, ident, kind, sha, label, fps, meta=None):
        """fps: {profile: (hashes, times)}. kind: 'specimen' or 'candidate'."""
        n = self.find(sha=sha)
        if n is not None:
            return self.catalogue[n]['id']
        n = len(self.catalogue)
        self.catalogue.append({'id': ident, 'kind': kind, 'sha256': sha, 'label': label, 'meta': meta or {}})
        for prof, (h, t) in fps.items():
            H, T, I = self.data[prof]
            self.data[prof] = [np.concatenate([H, h]), np.concatenate([T, t]), np.concatenate([I, np.full(len(h), n, np.int32)])]
        self._sorted = {}
        return ident

    def save(self):
        for prof, (H, T, I) in self.data.items():
            np.savez_compressed(os.path.join(self.root, f'{prof}.npz'), h=H, t=T, i=I)
        json.dump(self.catalogue, open(self.cat_path, 'w'), indent=1)

    # ---- matching --------------------------------------------------------------
    def _lookup(self, prof):
        if prof not in self._sorted:
            H, T, I = self.data[prof]
            o = np.argsort(H, kind='stable')
            self._sorted[prof] = (H[o], T[o], I[o])
        return self._sorted[prof]

    def vote(self, prof, qh, qt, exclude=None):
        """{track: (score, offset_frames, matched query-hash indices)} for every track with any hits."""
        H, T, I = self._lookup(prof)
        if len(H) == 0 or len(qh) == 0:
            return {}
        lo = np.searchsorted(H, qh, 'left')
        hi = np.searchsorted(H, qh, 'right')
        cnt = hi - lo
        if cnt.sum() == 0:
            return {}
        rep = np.repeat(np.arange(len(qh)), cnt)
        pos = np.concatenate([np.arange(a, b) for a, b in zip(lo, hi) if b > a])
        tracks = I[pos]
        offs = T[pos].astype(np.int64) - qt[rep].astype(np.int64)
        out = {}
        for tr in np.unique(tracks):
            if exclude is not None and tr == exclude:
                continue
            sel = tracks == tr
            o = offs[sel]
            vals, counts = np.unique(o, return_counts=True)
            k = np.argmax(counts)
            near = np.abs(o - vals[k]) <= 1          # allow one frame of jitter
            out[int(tr)] = (int(near.sum()), int(vals[k]), np.unique(rep[sel][near]))
        return out

    def match(self, y, sr, prof, exclude_sha=None, speeds=SPEEDS, top=3):
        """Best matches for audio y under one profile, searching playback speed.

        Each result carries `ratio`: its score over the background (median best score of every other entry in the index),
        so a match must stand out from the coincidental agreement any two riddims at the same tempo share.
        `band_rates` gives the match rate of query landmarks below and above 300 Hz: a copy of the same
        recording matches evenly; a different vocal over the same riddim matches far less in the vocal band.
        """
        p = fp.PROFILES[prof]
        base = audio.resample(y, sr, p['sr'])
        excl = self.find(sha=exclude_sha) if exclude_sha else None
        best = {}
        for f in speeds:
            qh, qt = fp.hashes(audio.change_speed(base, f), prof)
            for tr, (score, off, hit) in self.vote(prof, qh, qt, exclude=excl).items():
                if tr not in best or score > best[tr]['score']:
                    best[tr] = {'score': score, 'offset_s': off * fp.frame_seconds(prof), 'speed': round(1 / f, 3),
                                'nq': len(qh), 'qh': qh, 'hit': hit}
        n_tracks = len(self.catalogue) - (1 if excl is not None else 0)
        allscores = {tr: b['score'] for tr, b in best.items()}
        def background(tr):
            others = [v for k, v in allscores.items() if k != tr] + [0] * max(0, n_tracks - len(allscores) - (0 if tr in allscores else 1))
            return max(float(np.median(others)) if others else 0.0, 5.0)
        hz_per_bin = p['sr'] / p['n_fft']
        res = []
        for tr, b in best.items():
            c = self.catalogue[tr]
            f1 = ((b['qh'] >> 16) & 0x3FF) * hz_per_bin
            hitmask = np.zeros(len(b['qh']), bool); hitmask[b['hit']] = True
            lo, mid = f1 < 300, f1 >= 300
            rates = {'below_300hz': round(float(hitmask[lo].mean()) if lo.any() else 0.0, 4),
                     'above_300hz': round(float(hitmask[mid].mean()) if mid.any() else 0.0, 4)}
            res.append({'id': c['id'], 'kind': c['kind'], 'label': c['label'], 'score': b['score'],
                        'share': round(b['score'] / max(b['nq'], 1), 4), 'ratio': round(b['score'] / background(tr), 1),
                        'offset_s': round(b['offset_s'], 2), 'speed': b['speed'], 'band_rates': rates})
        res.sort(key=lambda r: -r['score'])
        return res[:top]
