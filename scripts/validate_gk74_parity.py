"""
validate_gk74_parity.py
Tarayici (index.html: gk74Window/gk74Decluster) ile scripts/decluster_gk74.py
ayni katalogda ayni ana soklari mi buluyor? Node.js gerektirir.

Kullanim (depo kokunden):
  python scripts/validate_gk74_parity.py                       # tum tarihsel katalog + 70 km daire
  python scripts/validate_gk74_parity.py --mag-field mw
Beklenen (2026-09-28, eq_historical.json 88.333 olay, --mag-field mag):
  daire 37.33N 38.86E R=70 km : 447 -> 295
  tum katalog                 : 88.333 -> 39.424
Saat dilimi bagimsizligi icin betigi farkli TZ ile calistirin
(orn. TZ=Europe/Istanbul ve TZ=UTC); sonuclar ayni olmalidir.
"""
import argparse, json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decluster_gk74 import decluster, haversine  # noqa: E402

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ap = argparse.ArgumentParser()
ap.add_argument('--catalog', default='data/eq_historical.json')
ap.add_argument('--html', default='index.html')
ap.add_argument('--mag-field', choices=['mag', 'mw'], default='mag')
ap.add_argument('--lat', type=float, default=37.33)
ap.add_argument('--lon', type=float, default=38.86)
ap.add_argument('--radius', type=float, default=70.0)
a = ap.parse_args()

html = open(a.html, encoding='utf-8').read()
m = re.search(r'function gk74Window\(m\).*?(?=\n// GK74 filtresi)', html, re.S)
if not m:
    sys.exit('index.html icinde gk74Window/gk74Decluster bulunamadi')
events = json.load(open(a.catalog, encoding='utf-8'))['events']
circle = [e for e in events if haversine(a.lat, a.lon, e['lat'], e['lon']) <= a.radius]

js = m.group(0) + r'''
const fs = require('fs');
const [inp, field] = process.argv.slice(2);
const sets = JSON.parse(fs.readFileSync(inp, 'utf8'));
const out = sets.map(evs => {
  const list = evs.map(e => ({ id: e.id, lat: e.lat, lon: e.lon, mag: e.mag,
    mw: field === 'mw' ? (e.mw ?? undefined) : undefined, time: new Date(e.time) }));
  return [...gk74Decluster(list).keep].map(e => e.id);
});
process.stdout.write(JSON.stringify(out));
'''
with tempfile.TemporaryDirectory() as td:
    jf, df = os.path.join(td, 'gk.js'), os.path.join(td, 'in.json')
    open(jf, 'w', encoding='utf-8').write(js)
    json.dump([circle, events], open(df, 'w', encoding='utf-8'))
    res = subprocess.run(['node', jf, df, a.mag_field], capture_output=True, text=True, check=True)
js_sets = [set(x) for x in json.loads(res.stdout)]

ok = True
for name, sub, jset in [(f'daire {a.lat}N {a.lon}E R={a.radius:g} km', circle, js_sets[0]),
                        ('tum katalog', events, js_sets[1])]:
    evs, cl = decluster(sub, a.mag_field)
    pset = {e['id'] for e, c in zip(evs, cl) if not c}
    diff = len(pset ^ jset)
    ok &= diff == 0
    print(f'{name:40s} ham {len(sub):>7,} | Python {len(pset):>7,} | tarayici {len(jset):>7,} | fark {diff}'.replace(',', '.'))
print('SONUC:', 'BIREBIR AYNI' if ok else 'FARK VAR')
sys.exit(0 if ok else 1)
