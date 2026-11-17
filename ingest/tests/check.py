"""Assert the synthetic test came out as expected."""
import glob, json, sys

root = sys.argv[1]
items = {json.load(open(f))['file']: json.load(open(f)) for f in glob.glob(f'{root}/queue/*.json')}
fails = []

def top(name):
    p = items[name]['proposals']
    return (p[0]['type'], p[0]['target']) if p else (None, None)

def expect(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond:
        fails.append(msg)

t, tg = top('A vocal version.wav')
expect(tg == 'HT-T001' and t.startswith('same riddim'), 'vocal version -> same riddim as HT-T001, not a copy')
t, tg = top('A vinyl +6pct.wav')
sp = items['A vinyl +6pct.wav']['proposals'][0]['speed']
expect(tg == 'HT-T001' and t == 'same recording' and 1.05 <= sp <= 1.07, f'worn vinyl at +6% -> same recording as HT-T001, speed {sp}')
expect(not items['D unknown riddim.wav']['proposals'], 'unknown riddim -> no false match')
t, tg = top('D vocal version.wav')
expect(tg == items['D unknown riddim.wav']['candidate_id'] and t.startswith('same riddim'), 'vocal over the unknown riddim -> matched to it')
m = items['A vocal version.wav']['measurements']
expect(136 <= m['tempo_bpm'] <= 144, f"tempo under an MC -> {m['tempo_bpm']} BPM (truth 140)")
s = [p['target'] for p in items['pirate set.wav']['proposals']]
d = items['D unknown riddim.wav']['candidate_id']
expect(s == ['HT-T002', 'HT-T001', 'HT-T001', d, 'HT-T003'], f'radio set order -> {s}')
print(f'\n{len(fails)} failure(s)')
sys.exit(1 if fails else 0)
