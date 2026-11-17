"""Ingestion pipeline: file -> sealed hash -> fingerprints -> matches -> measurements -> review queue.

Single recordings get the full treatment. Long recordings (radio sets, mixes) are cut into overlapping
windows; each window is matched, and runs of windows that match the same thing become dated segments.
"""
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

import numpy as np

from . import audio, fingerprint as fp, measure, separate
from .index import Index

LONG_S = 8 * 60              # longer than this is treated as a set or mix
WIN_S, HOP_S = 20.0, 10.0    # set windows
SET_SPEEDS = [round(0.92 + 0.02 * i, 2) for i in range(9)]

# Match strength: votes must stand out from the index background (ratio) and cover enough of the query (share).
# Tuned on the synthetic test set; re-tune on real audio.
STRONG = {'full': (3.0, 0.04), 'riddim': (3.0, 0.06), 'vocal': (3.0, 0.04)}
POSSIBLE = {'full': (3.0, 0.02), 'riddim': (3.0, 0.035), 'vocal': (3.0, 0.02)}
VOCAL_PRESENT = 0.08       # vocal stem share of energy above which a recording counts as voiced


def strength(prof, m):
    r, sh = STRONG[prof]
    if m['ratio'] >= r and m['share'] >= sh:
        return 'strong'
    r, sh = POSSIBLE[prof]
    if m['ratio'] >= r and m['share'] >= sh:
        return 'possible'
    return None


def _jsonable(o):
    import numpy as _np
    if isinstance(o, set):
        return sorted(o)
    if isinstance(o, _np.generic):
        return o.item()
    if isinstance(o, _np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def _now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


# ---- provenance log (append-only, hash-chained) ------------------------------------------------
def log_event(root, sha, event, detail=None):
    path = os.path.join(root, 'log.jsonl')
    prev = '0' * 64
    n = 0
    if os.path.exists(path):
        lines = [l for l in open(path) if l.strip()]
        if lines:
            last = json.loads(lines[-1])
            prev, n = last['hash'], last['n'] + 1
    entry = {'n': n, 'at': _now(), 'sha256': sha, 'event': event, 'detail': detail or {}, 'prev': prev}
    entry['hash'] = hashlib.sha256((prev + json.dumps({k: entry[k] for k in ('n', 'at', 'sha256', 'event', 'detail')}, sort_keys=True)).encode()).hexdigest()
    with open(path, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    return entry


def verify_log(root):
    path = os.path.join(root, 'log.jsonl')
    prev = '0' * 64
    for line in open(path):
        if not line.strip():
            continue
        e = json.loads(line)
        h = hashlib.sha256((prev + json.dumps({k: e[k] for k in ('n', 'at', 'sha256', 'event', 'detail')}, sort_keys=True)).encode()).hexdigest()
        if e['prev'] != prev or e['hash'] != h:
            return False, e['n']
        prev = e['hash']
    return True, None


# ---- optional extras -------------------------------------------------------------------------
def transcribe(path):
    """Whisper transcript if installed. MLE and patois are handled poorly: treat as a draft for correction."""
    try:
        import whisper
    except ImportError:
        return None
    model = whisper.load_model('small')
    r = model.transcribe(str(path), language='en')
    return [{'start': round(s['start'], 1), 'end': round(s['end'], 1), 'text': s['text'].strip()} for s in r['segments']]


# ---- core --------------------------------------------------------------------------------------
def fingerprints(y_full, sr, y_inst=None, y_voc=None):
    out = {}
    out['full'] = fp.hashes(audio.resample(y_full, sr, fp.PROFILES['full']['sr']), 'full')
    src = y_inst if y_inst is not None else y_full
    out['riddim'] = fp.hashes(audio.resample(src, sr, fp.PROFILES['riddim']['sr']), 'riddim')
    if y_voc is not None:
        out['vocal'] = fp.hashes(audio.resample(y_voc, sr, fp.PROFILES['vocal']['sr']), 'vocal')
    return out


def proposals_from(matches, idx=None, q_voiced=None):
    """Turn raw matches into proposals a reviewer can accept or reject.

    Copy or version? If both recordings are instrumental, a strong full match is the same recording.
    If the new one is voiced, its vocal stem is matched too: vocal matches too means the same recording;
    no vocal match means a different vocal over the same riddim. Without separation it says it can't tell.
    """
    props = []
    full = {m['id']: m for m in matches.get('full', [])}
    rid = {m['id']: m for m in matches.get('riddim', [])}
    voc = {m['id']: m for m in matches.get('vocal', [])}
    cat = {c['id']: c for c in idx.catalogue} if idx else {}
    for ident in list(dict.fromkeys(list(full) + list(rid))):
        f, r = full.get(ident), rid.get(ident)
        fs = strength('full', f) if f else None
        rs = strength('riddim', r) if r else None
        t_voiced = cat.get(ident, {}).get('meta', {}).get('voiced')
        why = None
        if fs == 'strong' or rs == 'strong':
            if q_voiced is None or t_voiced is None:
                kind = 'same recording or a version of it' if fs == 'strong' else 'same riddim (different version or vocal)'
                why = 'no vocal separation, so a copy and a vocal version cannot be told apart'
            elif not q_voiced and not t_voiced:
                kind = 'same recording' if fs == 'strong' else 'same riddim (different version or vocal)'
                why = 'both instrumental'
            elif q_voiced and t_voiced and voc.get(ident) and strength('vocal', voc[ident]) == 'strong':
                kind, why = 'same recording', 'vocals match as well as the riddim'
            else:
                kind = 'same riddim (different version or vocal)'
                why = ('instrumental of this vocal' if (t_voiced and not q_voiced) else
                       'vocal over this instrumental' if (q_voiced and not t_voiced) else 'different vocals over the same riddim')
        elif fs == 'possible' or rs == 'possible':
            kind = 'possible match'
        else:
            continue
        m = f if fs else r
        props.append({'type': kind, 'target': ident, 'target_kind': m['kind'], 'label': m['label'], 'why': why,
                      'evidence': {'full': f, 'riddim': r, 'vocal': voc.get(ident)},
                      'speed': m['speed'], 'offset_s': m['offset_s'],
                      'note': (f"plays at {round((m['speed'] - 1) * 100, 1):+}% speed relative to the indexed copy"
                               if abs(m['speed'] - 1) >= 0.015 else None)})
    order = {'same recording': 0, 'same recording or a version of it': 1, 'same riddim (different version or vocal)': 2, 'possible match': 3}
    return sorted(props, key=lambda p: order[p['type']])


def ingest_track(path, idx, root, args):
    sha = audio.sha256_file(path)
    if any(c['sha256'] == sha for c in idx.catalogue) and not args.get('force'):
        return None
    y = audio.load(path, measure.SR)
    log_event(root, sha, 'received', {'file': os.path.basename(path), 'bytes': os.path.getsize(path)})
    inst, voc, method = separate.separate(path, y, measure.SR) if args.get('stems', True) else (None, None, None)
    vshare = voiced = None
    if inst is not None:
        vshare = float(np.sum(voc ** 2) / (np.sum(voc ** 2) + np.sum(inst ** 2) + 1e-12))
        voiced = vshare >= VOCAL_PRESENT
    fps = fingerprints(y, measure.SR, inst, voc if voiced else None)
    matches = {'full': idx.match(y, measure.SR, 'full', exclude_sha=sha),
               'riddim': idx.match(inst if inst is not None else y, measure.SR, 'riddim', exclude_sha=sha)}
    if voiced:
        matches['vocal'] = idx.match(voc, measure.SR, 'vocal', exclude_sha=sha)
    props = proposals_from(matches, idx, voiced)
    meas = measure.measure(y, measure.SR, vocal_share=vshare, y_inst=inst)
    trans = transcribe(path) if args.get('transcribe') else None
    cand = 'CAND-' + sha[:10]
    idx.add(cand, 'candidate', sha, os.path.basename(path), fps,
            meta={'duration_s': meas['duration_s'], 'voiced': voiced, 'vocal_share': vshare, 'separation': method})
    item = {'sha256': sha, 'candidate_id': cand, 'file': os.path.basename(path), 'mode': 'recording',
            'ingested_at': _now(), 'duration_s': meas['duration_s'], 'separation': method,
            'proposals': props, 'matches': matches, 'measurements': meas, 'transcript': trans,
            'status': 'awaiting review'}
    log_event(root, sha, 'fingerprinted and measured', {'proposals': len(props), 'candidate_id': cand})
    return item


def ingest_set(path, idx, root, args):
    """Long recording: identify what plays when."""
    sha = audio.sha256_file(path)
    if any(c['sha256'] == sha for c in idx.catalogue) and not args.get('force'):
        return None
    total = audio.duration(path)
    log_event(root, sha, 'received', {'file': os.path.basename(path), 'bytes': os.path.getsize(path), 'duration_s': round(total, 1)})
    y_all = audio.load(path, measure.SR)
    wins = []
    t = 0.0
    while t + WIN_S / 2 < total:
        seg = y_all[int(t * measure.SR):int((t + WIN_S) * measure.SR)]
        best = None
        for prof in ('full', 'riddim'):
            for m in idx.match(seg, measure.SR, prof, exclude_sha=sha, speeds=SET_SPEEDS, top=1):
                st = strength(prof, m)
                if st and (best is None or (st, prof == 'full') > (best['strength'], best['profile'] == 'full')):
                    best = dict(m, profile=prof, strength=st)
        wins.append({'t': t, 'best': best})
        t += HOP_S
    # merge runs of windows with the same target
    segments, cur = [], None
    for w in wins:
        b = w['best']
        key = b['id'] if b else None
        if cur and cur['target'] == key:
            cur['end_s'] = w['t'] + WIN_S
            if b:
                cur['windows'] += 1
                cur['profiles'].add(b['profile'])
                cur['max_score'] = max(cur['max_score'], b['score'])
        else:
            if cur:
                segments.append(cur)
            cur = {'target': key, 'start_s': w['t'], 'end_s': w['t'] + WIN_S, 'windows': 1 if b else 0,
                   'profiles': {b['profile']} if b else set(), 'max_score': b['score'] if b else 0,
                   'label': b['label'] if b else None, 'kind': b['kind'] if b else None, 'speed': b['speed'] if b else None}
    if cur:
        segments.append(cur)
    out = []
    for s in segments:
        if s['target'] and s['windows'] < 2 and s['max_score'] < STRONG['full'][0]:
            s = dict(s, target=None, label=None, kind=None, speed=None, profiles=set())   # lone weak window: noise
        if out and out[-1]['target'] == s['target']:
            out[-1]['end_s'] = s['end_s']
            continue
        s['profiles'] = sorted(s['profiles'])
        s['relation'] = (None if not s['target'] else 'same recording' if 'full' in s['profiles'] else 'same riddim (vocal version)')
        s['start_s'] = round(s['start_s'], 1)
        s['end_s'] = round(min(s['end_s'], total), 1)
        out.append(s)
    # a candidate that an earlier upload linked to a specimen points through to that specimen
    via = {}
    for qf in os.listdir(os.path.join(root, 'queue')) if os.path.isdir(os.path.join(root, 'queue')) else []:
        if qf.endswith('.json'):
            q = json.load(open(os.path.join(root, 'queue', qf)))
            top = next((p for p in q.get('proposals', []) if p.get('target_kind') == 'specimen'
                        and not (p.get('decision') or {}).get('verdict') == 'reject'), None)
            if top:
                via[q['candidate_id']] = top
    props = []
    for s in out:
        if not s['target']:
            continue
        p = {'type': 'played in set', 'target': s['target'], 'target_kind': s['kind'], 'label': s['label'],
             'relation': s['relation'], 'start_s': s['start_s'], 'end_s': s['end_s'], 'speed': s['speed']}
        v = via.get(s['target'])
        if v:
            sp = round((s['speed'] or 1) * (v.get('speed') or 1), 3)
            p.update({'via': s['target'], 'target': v['target'], 'target_kind': 'specimen', 'label': v['label'],
                      'relation': f"{v['type']} (through {s['target']})", 'speed': sp})
        props.append(p)
    trans = transcribe(path) if args.get('transcribe') else None
    fps = fingerprints(y_all, measure.SR)
    idx.add('SET-' + sha[:10], 'candidate', sha, os.path.basename(path), fps, meta={'duration_s': round(total, 1), 'set': True})
    item = {'sha256': sha, 'candidate_id': 'SET-' + sha[:10], 'file': os.path.basename(path), 'mode': 'set',
            'ingested_at': _now(), 'duration_s': round(total, 1), 'segments': out, 'proposals': props,
            'transcript': trans, 'status': 'awaiting review',
            'note': 'Each identified segment is a dated play once the set itself is dated and its source confirmed.'}
    log_event(root, sha, 'set segmented', {'segments': len(out), 'identified': len(props)})
    return item


def scan(paths, root, args):
    idx = Index(os.path.join(root, 'index'))
    qdir = os.path.join(root, 'queue')
    os.makedirs(qdir, exist_ok=True)
    files = []
    for p in paths:
        if os.path.isdir(p):
            for dirpath, _, names in os.walk(p):
                files += [os.path.join(dirpath, n) for n in sorted(names) if os.path.splitext(n)[1].lower() in audio.AUDIO_EXT]
        else:
            files.append(p)
    done = []
    for f in files:
        long = audio.duration(f) > LONG_S or args.get('set')
        item = (ingest_set if long else ingest_track)(f, idx, root, args)
        if item is None:
            print(f'skip (already ingested): {f}')
            continue
        json.dump(item, open(os.path.join(qdir, item['sha256'][:16] + '.json'), 'w'), indent=1, default=_jsonable)
        idx.save()
        done.append(item)
        print(f"{item['mode']:9} {os.path.basename(f)}: {len(item['proposals'])} proposal(s)")
        for p in item['proposals']:
            where = f" at {p['start_s']}-{p['end_s']}s" if 'start_s' in p else ''
            print(f"           -> {p['type']}: {p['target']} ({p['label']}){where}")
    return done


def index_reference(paths, root, ident=None, label=None):
    """Add known specimens. Files named 'HT-G###...' take their id from the name."""
    import re
    idx = Index(os.path.join(root, 'index'))
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += [os.path.join(p, n) for n in sorted(os.listdir(p)) if os.path.splitext(n)[1].lower() in audio.AUDIO_EXT]
        else:
            files.append(p)
    for f in files:
        m = re.match(r'(HT-[A-Z]\d{3})', os.path.basename(f))
        i = ident or (m.group(1) if m else None)
        if not i:
            print(f'skip (no specimen id; name the file HT-G###... or pass --id): {f}')
            continue
        sha = audio.sha256_file(f)
        y = audio.load(f, measure.SR)
        inst, voc, method = separate.separate(f, y, measure.SR)
        vshare = voiced = None
        if inst is not None:
            vshare = float(np.sum(voc ** 2) / (np.sum(voc ** 2) + np.sum(inst ** 2) + 1e-12))
            voiced = vshare >= VOCAL_PRESENT
        idx.add(i, 'specimen', sha, label or os.path.splitext(os.path.basename(f))[0], fingerprints(y, measure.SR, inst, voc if voiced else None),
                meta={'voiced': voiced, 'vocal_share': vshare, 'separation': method})
        log_event(root, sha, 'indexed as specimen', {'id': i, 'file': os.path.basename(f)})
        print(f'indexed {i}: {os.path.basename(f)}' + (f' (vocal stem {vshare:.0%})' if vshare is not None else ''))
    idx.save()
