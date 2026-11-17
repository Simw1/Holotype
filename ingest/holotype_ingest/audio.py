"""Audio loading and simple resampling. Decodes anything ffmpeg can read; falls back to soundfile."""
import hashlib
import shutil
import subprocess

import numpy as np

AUDIO_EXT = {'.wav', '.flac', '.mp3', '.m4a', '.aac', '.ogg', '.opus', '.aif', '.aiff', '.wma'}


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load(path, sr, start=None, duration=None):
    """Mono float32 at `sr`. Optional start/duration in seconds."""
    if shutil.which('ffmpeg'):
        cmd = ['ffmpeg', '-v', 'error', '-nostdin']
        if start:
            cmd += ['-ss', str(start)]
        if duration:
            cmd += ['-t', str(duration)]
        cmd += ['-i', str(path), '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
        out = subprocess.run(cmd, capture_output=True, check=True).stdout
        return np.frombuffer(out, dtype=np.float32).copy()
    import soundfile as sf
    y, fs = sf.read(str(path), dtype='float32', always_2d=True)
    y = y.mean(axis=1)
    if start:
        y = y[int(start * fs):]
    if duration:
        y = y[:int(duration * fs)]
    return resample(y, fs, sr)


def resample(y, sr_in, sr_out):
    if sr_in == sr_out:
        return y
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(int(sr_in), int(sr_out))
    return resample_poly(y, sr_out // g, sr_in // g).astype(np.float32)


def change_speed(y, factor):
    """Play `y` at `factor` times the speed (pitch and tempo move together, as on a turntable)."""
    if abs(factor - 1.0) < 1e-6:
        return y
    n = int(len(y) / factor)
    x = np.arange(n) * factor
    return np.interp(x, np.arange(len(y)), y).astype(np.float32)


def duration(path):
    if shutil.which('ffprobe'):
        out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                             capture_output=True, text=True).stdout.strip()
        try:
            return float(out)
        except ValueError:
            pass
    return len(load(path, 8000)) / 8000.0
