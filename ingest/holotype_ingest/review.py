"""Review queue: a static HTML page of everything awaiting a decision, and the decide command."""
import glob
import html
import json
import os

from .pipeline import log_event

H = html.escape


def load_queue(root):
    items = []
    for f in sorted(glob.glob(os.path.join(root, 'queue', '*.json'))):
        it = json.load(open(f))
        it['_path'] = f
        items.append(it)
    return items


def decide(root, sha_prefix, n, verdict, note=None, reviewer=None):
    for it in load_queue(root):
        if it['sha256'].startswith(sha_prefix):
            p = it['proposals'][n]
            p['decision'] = {'verdict': verdict, 'note': note, 'reviewer': reviewer}
            if all('decision' in q for q in it['proposals']):
                it['status'] = 'reviewed'
            path = it.pop('_path')
            json.dump(it, open(path, 'w'), indent=1)
            log_event(root, it['sha256'], f'proposal {verdict}', {'proposal': n, 'target': p.get('target'), 'type': p['type'], 'note': note, 'reviewer': reviewer})
            return p
    raise SystemExit(f'no queue item starting {sha_prefix}')


def fmt_t(s):
    s = int(s)
    return f'{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}' if s >= 3600 else f'{s // 60}:{s % 60:02d}'


def render(root, loci_path=None):
    items = load_queue(root)
    loci = json.load(open(loci_path)) if loci_path and os.path.exists(loci_path) else None
    css = """body{font:15px/1.5 system-ui,sans-serif;margin:0;padding:24px 16px;background:#eef0ee;color:#11161d}
main{max-width:1000px;margin:auto;display:grid;gap:18px}h1{margin:0;font-size:1.8rem}
.item{background:#f8f9f7;border:1px solid #c2c9c4;border-radius:6px;padding:16px 18px;display:grid;gap:10px}
.k{font:600 .72rem ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;color:#55606b}
table{border-collapse:collapse;width:100%;font-size:.88rem}td,th{text-align:left;padding:5px 8px;border-bottom:1px solid #d6dcd8;vertical-align:top}
.pill{font:600 .72rem ui-monospace,monospace;padding:2px 7px;border-radius:3px;border:1px solid currentColor}
.rec{color:#1e7548}.rid{color:#2b45c4}.pos{color:#a35f00}code{font-size:.8rem;background:#e6eae6;padding:1px 4px;border-radius:3px}
.bar{position:relative;height:26px;background:#e2e6e3;border-radius:3px;overflow:hidden}.seg{position:absolute;top:0;bottom:0;border-right:1px solid #f8f9f7;color:#fff;font:600 .68rem ui-monospace,monospace;padding:5px 4px;overflow:hidden;white-space:nowrap}
.s-rec{background:#1e7548}.s-rid{background:#2b45c4}.muted{color:#55606b}"""
    out = [f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Holotype ingest review</title><style>{css}</style><main>',
           f'<h1>Ingest review queue</h1><p class="muted">{len(items)} item(s). Nothing here is in the register until a person accepts it: <code>python3 -m holotype_ingest decide &lt;sha&gt; &lt;n&gt; accept|reject --note "..."</code></p>']
    cls = {'same recording': 'rec', 'played in set': 'rec', 'same riddim (different version or vocal)': 'rid', 'possible match': 'pos'}
    for it in items:
        out.append('<section class="item">')
        out.append(f"<div class='k'>{H(it['mode'])} · {H(it['status'])} · {H(it['candidate_id'])}</div><h2 style='margin:0;font-size:1.15rem'>{H(it['file'])}</h2>")
        out.append(f"<div class='muted' style='font:.75rem ui-monospace,monospace;overflow-wrap:anywhere'>sha256 {it['sha256']} · {fmt_t(it['duration_s'])} · ingested {H(it['ingested_at'])}</div>")
        if it['mode'] == 'set' and it.get('segments'):
            tot = max(it['duration_s'], 1)
            bars = ''.join(f"<div class='seg {'s-rec' if s['relation']=='same recording' else 's-rid'}' style='left:{100*s['start_s']/tot:.2f}%;width:{100*(s['end_s']-s['start_s'])/tot:.2f}%' title='{H(str(s['label']))} {fmt_t(s['start_s'])}-{fmt_t(s['end_s'])}'>{H(str(s['target']))}</div>"
                           for s in it['segments'] if s['target'])
            out.append(f"<div class='k'>What plays when</div><div class='bar'>{bars}</div>")
        if it['proposals']:
            rows = []
            for n, p in enumerate(it['proposals']):
                when = f"{fmt_t(p['start_s'])}–{fmt_t(p['end_s'])}" if 'start_s' in p else ''
                rel = p.get('relation') or ''
                d = p.get('decision')
                dec = f"<b>{H(d['verdict'])}</b> {H(d.get('note') or '')}" if d else f"<code>decide {it['sha256'][:12]} {n} accept</code>"
                ev = p.get('evidence') or {}
                sc = ', '.join(f"{k} {v['score']} votes" for k, v in ev.items() if v)
                rows.append(f"<tr><td>{n}</td><td><span class='pill {cls.get(p['type'],'pos')}'>{H(p['type'])}</span> {H(rel)}</td><td><b>{H(str(p['target']))}</b><br><span class='muted'>{H(str(p['label']))}</span></td><td>{when}{'<br>' if when else ''}speed ×{p.get('speed')}<br><span class='muted'>{H(sc)}{(' · ' + H(p['why'])) if p.get('why') else ''}{(' · ' + H(p['note'])) if p.get('note') else ''}</span></td><td>{dec}</td></tr>")
            out.append("<div class='k'>Proposals</div><table><tr><th>#</th><th>Proposal</th><th>Target</th><th>Detail</th><th>Decision</th></tr>" + ''.join(rows) + '</table>')
        else:
            out.append("<p class='muted'>No match in the index: a new candidate. It stays in the index, so later uploads can match it.</p>")
        m = it.get('measurements')
        if m:
            codes = m.get('codes', {})
            crow = []
            for i, (k, v) in enumerate(codes.items()):
                if not v:
                    continue
                name = loci[i]['name'] if loci else k
                allele = loci[i]['alleles'][v['a']] if loci else v['a']
                crow.append(f"<tr><td><code>{k}</code> {H(name)}</td><td>{H(str(allele))}</td><td>{v['conf']:.2f}</td><td class='muted'>{H(v['why'])}</td></tr>")
            out.append(f"<div class='k'>Measured</div><p>{m['tempo_bpm']} BPM (raw {m['tempo_bpm_raw']}) · RMS {m['rms_dbfs']} dBFS · crest {m['crest_db']} dB · sub-bass {m['sub_bass_share_pct']}%"
                       + (f" · vocal stem {m['vocal_share_pct']}%" if 'vocal_share_pct' in m else '') + '</p>')
            out.append("<div class='k'>Machine-drafted codes (basis: machine, to confirm by ear)</div><table><tr><th>Character</th><th>Draft</th><th>Confidence</th><th>Why</th></tr>" + ''.join(crow) + '</table>')
        if it.get('transcript'):
            out.append("<div class='k'>Transcript (draft)</div><p>" + ' '.join(H(s['text']) for s in it['transcript'][:40]) + '</p>')
        out.append('</section>')
    out.append('</main>')
    path = os.path.join(root, 'queue', 'review.html')
    open(path, 'w').write('\n'.join(out))
    return path
