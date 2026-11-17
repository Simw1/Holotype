"""Measurements and machine-drafted codes.

Measured: tempo, loudness, crest factor, sub-bass share, and a 16-step drum profile per bar.
From those it drafts four of the ten register characters (TMP, KCK, HAT, BAS), plus VOC and STR
where it can, each with a confidence. Drafts carry basis 'm' (machine): evidence to confirm, not truth.
Allele indices follow data/loci.json.
"""
import numpy as np

SR = 22050


def _band_onsets(S, freqs, lo, hi):
    band = (freqs >= lo) & (freqs < hi)
    E = S[band].sum(axis=0)
    flux = np.maximum(0, np.diff(np.log1p(E), prepend=np.log1p(E[0])))
    return flux / (flux.max() + 1e-9)


def _step_profile(env, beat_frames, steps_per_beat=4):
    """Average onset strength at each 16th-note step of a 4/4 bar, aligned to tracked beats."""
    if len(beat_frames) < 9:
        return None
    prof = np.zeros(4 * steps_per_beat)
    cnt = np.zeros_like(prof)
    for b in range(len(beat_frames) - 1):
        a, z = beat_frames[b], beat_frames[b + 1]
        for s in range(steps_per_beat):
            f = int(round(a + (z - a) * s / steps_per_beat))
            if 0 <= f < len(env):
                w = env[max(0, f - 1):f + 2].max()
                k = (b % 4) * steps_per_beat + s
                prof[k] += w
                cnt[k] += 1
    prof = prof / np.maximum(cnt, 1)
    return prof / (prof.max() + 1e-9)


def _best_rotation(prof):
    """Pick the bar phase that puts the strongest low-band hit on step 0."""
    return int(np.argmax(prof[::4])) * 4


def measure(y, sr=SR, vocal_share=None, y_inst=None):
    import librosa
    if sr != SR:
        from .audio import resample
        y = resample(y, sr, SR)
    y = y.astype(np.float32)
    out = {'duration_s': round(len(y) / SR, 2)}
    rms = float(np.sqrt(np.mean(y ** 2)) + 1e-12)
    peak = float(np.max(np.abs(y)) + 1e-12)
    out['rms_dbfs'] = round(20 * np.log10(rms), 1)
    out['peak_dbfs'] = round(20 * np.log10(peak), 1)
    out['crest_db'] = round(out['peak_dbfs'] - out['rms_dbfs'], 1)

    n_fft, hop = 2048, 512
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop)) ** 2
    freqs = librosa.fft_frequencies(sr=SR, n_fft=n_fft)
    tot = S.sum() + 1e-12
    out['sub_bass_share_pct'] = round(float(100 * S[freqs < 100].sum() / tot), 1)
    # bass character from the instrumental stem when there is one, so a voice in 120-500 Hz can't pass for bass harmonics
    Sb = S
    if y_inst is not None:
        yi = y_inst if sr == SR else __import__('holotype_ingest.audio', fromlist=['resample']).resample(y_inst, sr, SR)
        Sb = np.abs(librosa.stft(yi.astype(np.float32), n_fft=n_fft, hop_length=hop)) ** 2
    bass = Sb[(freqs >= 30) & (freqs < 120)].sum()
    harm = Sb[(freqs >= 120) & (freqs < 500)].sum()
    out['bass_harmonic_ratio'] = round(float(harm / (bass + 1e-12)), 2)

    # track tempo from the drum bands only (sub-150 Hz and above 5 kHz), so an MC on top can't pull it off the beat
    drum_rows = (freqs < 150) | (freqs > 5000)
    onset = librosa.onset.onset_strength(S=librosa.power_to_db(S[drum_rows]), sr=SR, hop_length=hop)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=SR, hop_length=hop, start_bpm=140)
    tempo = float(np.atleast_1d(tempo)[0])
    raw = tempo
    while tempo < 100:
        tempo *= 2
    while tempo > 180:
        tempo /= 2
    out['tempo_bpm_raw'] = round(raw, 1)
    out['tempo_bpm'] = round(tempo, 1)

    kick = _band_onsets(S, freqs, 30, 120)
    snare = _band_onsets(S, freqs, 150, 2500)
    hats = _band_onsets(S, freqs, 6000, 11000)
    # if the tracker locked onto half-time, subdivide beats so steps stay 16ths of a 4/4 bar at the folded tempo
    if raw < 100 and len(beats) > 2:
        mids = ((beats[:-1] + beats[1:]) / 2).astype(int)
        beats = np.sort(np.concatenate([beats, mids]))
    kp, sp, hp = (_step_profile(e, beats) for e in (kick, snare, hats))
    out['drum_profile'] = None
    if kp is not None:
        r = _best_rotation(kp)
        kp, sp, hp = (np.roll(p, -r) for p in (kp, sp, hp))
        out['drum_profile'] = {'kick': [round(float(v), 2) for v in kp], 'snare': [round(float(v), 2) for v in sp],
                               'hats': [round(float(v), 2) for v in hp]}
    out['drums_energy'] = round(float(np.mean(kick) + np.mean(snare)), 3)
    out['hat_density_per_beat'] = round(float((hats > 0.3).sum() / max(len(beats), 1)), 2)

    # section length in bars from repetition (8 vs 16)
    out['section_bars'] = None
    try:
        if len(beats) >= 64:
            C = librosa.feature.chroma_stft(S=S, sr=SR)
            M = librosa.feature.mfcc(S=librosa.power_to_db(S), n_mfcc=13)
            F = librosa.util.sync(np.vstack([C, M / (np.abs(M).max() + 1e-9)]), beats)
            R = librosa.segment.recurrence_matrix(F, mode='affinity', sym=True)
            lag = librosa.segment.recurrence_to_lag(R, pad=False).mean(axis=1)
            cands = {8: lag[32] if len(lag) > 32 else 0, 16: lag[64] if len(lag) > 64 else 0}
            out['section_bars'] = int(max(cands, key=cands.get)) if max(cands.values()) > 0 else None
    except Exception:
        pass
    if vocal_share is not None:
        out['vocal_share_pct'] = round(100 * vocal_share, 1)
    out['codes'] = draft_codes(out)
    return out


def draft_codes(m):
    """Machine drafts for the ten characters: {abbr: {a: allele index, conf: 0-1, why: text}} or None."""
    c = {k: None for k in ('TMP', 'KCK', 'HAT', 'BAS', 'HRM', 'LED', 'SMP', 'STR', 'FX', 'VOC')}
    t = m['tempo_bpm']
    if 136 <= t <= 146:
        c['TMP'] = {'a': 0, 'conf': 0.8, 'why': f'tempo {t} BPM'}
    elif 128 <= t < 136:
        c['TMP'] = {'a': 1, 'conf': 0.8, 'why': f'tempo {t} BPM'}
    else:
        c['TMP'] = {'a': 2, 'conf': 0.6, 'why': f'tempo {t} BPM'}
    dp = m.get('drum_profile')
    if m['drums_energy'] < 0.02 or dp is None:
        c['KCK'] = {'a': 3, 'conf': 0.6, 'why': 'little drum energy'}
    else:
        k, s = np.array(dp['kick']), np.array(dp['snare'])
        on = k[[0, 4, 8, 12]]
        if on.min() > 0.6 and on.std() < 0.15:
            c['KCK'] = {'a': 2, 'conf': 0.6, 'why': 'kick on every beat'}
        elif s[8] > 0.6 and s[8] >= 1.5 * max(s[4], s[12]) and k[4] < 0.5:
            c['KCK'] = {'a': 1, 'conf': 0.55, 'why': 'snare on 3, sparse kick'}
        elif k[[2, 6, 10, 14]].max() > 0.5 or k[[3, 7, 11, 15]].max() > 0.5:
            c['KCK'] = {'a': 0, 'conf': 0.45, 'why': 'kicks on off-beats (2-step skip)'}
        else:
            c['KCK'] = {'a': 4, 'conf': 0.35, 'why': 'irregular kick pattern'}
        h = np.array(dp['hats'])
        dens = m['hat_density_per_beat']
        swing = h[[3, 7, 11, 15]].mean() - h[[1, 5, 9, 13]].mean()
        if dens < 0.5:
            c['HAT'] = {'a': 3, 'conf': 0.5, 'why': f'{dens} hat hits per beat'}
        elif dens > 3:
            c['HAT'] = {'a': 2, 'conf': 0.5, 'why': f'{dens} hat hits per beat'}
        elif swing > 0.15:
            c['HAT'] = {'a': 0, 'conf': 0.4, 'why': 'late 16ths stronger than early (shuffle)'}
        else:
            c['HAT'] = {'a': 1, 'conf': 0.45, 'why': f'{dens} hat hits per beat, even'}
    sb, hr = m['sub_bass_share_pct'], m['bass_harmonic_ratio']
    if sb < 3:
        c['BAS'] = {'a': 4, 'conf': 0.6, 'why': f'sub-bass {sb:.0f}% of energy'}
    elif hr < 0.35:
        c['BAS'] = {'a': 1, 'conf': 0.5, 'why': f'sub-bass {sb:.0f}%, few harmonics (sine-like)'}
    elif hr > 2.5:
        c['BAS'] = {'a': 2, 'conf': 0.35, 'why': f'bass harmonics {hr}x fundamental (distorted)'}
    else:
        c['BAS'] = {'a': 0, 'conf': 0.4, 'why': f'bass harmonics {hr}x fundamental (square or saw)'}
    if m.get('section_bars') in (8, 16):
        c['STR'] = {'a': 0 if m['section_bars'] == 8 else 1, 'conf': 0.3, 'why': f'repeats every {m["section_bars"]} bars'}
    if 'vocal_share_pct' in m:
        v = m['vocal_share_pct']
        c['VOC'] = {'a': 0, 'conf': 0.6, 'why': f'vocal stem {v}% of energy'} if v < 5 else {'a': 1, 'conf': 0.3, 'why': f'vocal stem {v}% (MC count not measured)'}
    return c
