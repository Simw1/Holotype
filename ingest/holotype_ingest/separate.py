"""Vocal / instrumental separation.

Preferred: Demucs (htdemucs), if installed. Fallback: REPET-SIM (Rafii and Pardo, 2012), which needs no model:
it treats what repeats as the backing and what doesn't as the voice. Loop-built riddims are close to its
ideal case, which is why it is a reasonable fallback for grime. Both return (instrumental, vocal) at `sr`.
"""
import os
import shutil
import subprocess
import tempfile

import numpy as np

from . import audio

MAX_REPET_S = 10 * 60


def demucs_available():
    try:
        import demucs  # noqa: F401
        return True
    except ImportError:
        return False


def demucs(path, sr):
    out = tempfile.mkdtemp(prefix='holotype-stems-')
    try:
        subprocess.run(['python3', '-m', 'demucs.separate', '--two-stems', 'vocals', '-n', 'htdemucs', '-o', out, str(path)],
                       check=True, capture_output=True)
        d = os.path.join(out, 'htdemucs', os.path.splitext(os.path.basename(path))[0])
        return audio.load(os.path.join(d, 'no_vocals.wav'), sr), audio.load(os.path.join(d, 'vocals.wav'), sr)
    finally:
        shutil.rmtree(out, ignore_errors=True)


def repet_sim(y, sr):
    import librosa
    n_fft, hop = 2048, 512
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop)
    S, phase = np.abs(D), np.angle(D)
    width = int(librosa.time_to_frames(2, sr=sr, hop_length=hop))
    S_filter = librosa.decompose.nn_filter(S, aggregate=np.median, metric='cosine', width=width)
    S_filter = np.minimum(S, S_filter)
    margin_i, margin_v, power = 2, 6, 2
    mask_i = librosa.util.softmask(S_filter, margin_i * (S - S_filter), power=power)
    mask_v = librosa.util.softmask(S - S_filter, margin_v * S_filter, power=power)
    inst = librosa.istft(mask_i * S * np.exp(1j * phase), hop_length=hop, length=len(y))
    voc = librosa.istft(mask_v * S * np.exp(1j * phase), hop_length=hop, length=len(y))
    return inst.astype(np.float32), voc.astype(np.float32)


def separate(path, y, sr, method='auto'):
    """Returns (instrumental, vocal, method_used) or (None, None, None)."""
    if method in ('auto', 'demucs') and demucs_available():
        try:
            i, v = demucs(path, sr)
            return i, v, 'demucs'
        except Exception:
            pass
    if method in ('auto', 'repet') and len(y) / sr <= MAX_REPET_S:
        i, v = repet_sim(y, sr)
        return i, v, 'repet-sim'
    return None, None, None
