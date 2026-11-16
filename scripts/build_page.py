"""Build site/index.html and docs/coding-sheet.csv from data/register.json."""
import json, os, csv
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
data = json.load(open(os.path.join(ROOT, 'data', 'register.json')))
tpl = open(os.path.join(HERE, 'template.html')).read()
blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
os.makedirs(os.path.join(ROOT, 'site'), exist_ok=True); os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
out = os.path.join(ROOT, 'site', 'index.html')
open(out, 'w').write(tpl.replace('/*DATA*/null', blob))
L = data['loci']
with open(os.path.join(ROOT, 'docs', 'coding-sheet.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'artist', 'title', 'date', 'character', 'code', 'variant', 'basis', 'confirmed (y/n)', 'corrected code', 'notes'])
    for s in sorted(data['specimens'], key=lambda s: s['id']):
        if not s['geno']: continue
        for i, c in enumerate(s['geno']):
            w.writerow([s['id'], s['artist'], s['title'], s['date'], L[i]['name'],
                        chr(65 + c['a']) if c else '', L[i]['alleles'][c['a']] if c else 'not coded',
                        ('sourced' if c['b'] == 's' else 'drafted') if c else '', '', '', ''])
print('site/index.html', os.path.getsize(out), 'bytes')
