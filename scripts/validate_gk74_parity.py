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
ap.add_argument('--context', nargs='+', default=None, metavar='FIXTURE',
                help='Baglamli GK74 dogrulamasi: scripts/fixtures/gk74_ctx_*_ref_*.json (Python referans + JS birebir)')
ap.add_argument('--mwauth', nargs='+', default=None, metavar='FIXTURE',
                help='Faz 2a (otoriter Mw) dogrulamasi: scripts/fixtures/gk74_mwauth_*_ref_*.json (JS == Python == donmus)')
a = ap.parse_args()

if a.mwauth:
    import hashlib
    from gk74_mwauth import run as mw_run, GK74_MWAUTH_VERSION
    from mw_authority import load_table
    from decluster_gk74 import parse_time_ms, haversine as _hv
    allok = True
    _html = open(a.html, encoding='utf-8').read()
    _m = re.search(r'function gk74Window\(m\).*?(?=\n// GK74 filtresi)', _html, re.S)
    if not _m:
        sys.exit('index.html icinde GK74 araligi bulunamadi')
    _jsv = re.search(r"const GK74_MWAUTH_VERSION = '([^']+)'", _m.group(0))
    js3 = _m.group(0) + r'''
const fs = require('fs');
const inp = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const field = inp.field, P = inp.P;
const all = inp.events.map(e => ({ id: e.id, lat: e.lat, lon: e.lon, mag: e.mag, mtype: e.mtype,
  mw: field === 'mw' ? (e.mw ?? undefined) : undefined, time: new Date(e.time) }));
const ents = inp.entries.filter(x => x.status === 'verified').map(x => ({ ...x, _t: Date.parse(x.time_utc) }));
const tset = new Set(inp.target);
const target = all.filter(e => tset.has(e.id));
const ctx = gk74SelectContext(all, P.lat, P.lon, P.radius_km, Date.parse(P.start + 'T00:00:00Z'), P.t_end_ms, P.mmin, ents);
const B = gk74Decluster(target, ctx, ents);
const A = gk74Decluster(target, [], ents);
const union = target.concat(ctx.map(c => c.e));
const ovr = union.filter(e => B.override.has(e)).map(e => ({ id: e.id, role: tset.has(e.id) ? 'target' : 'context',
  entry: B.override.get(e).name, catalog_mag: e.mag, catalog_mtype: e.mtype, mw: B.override.get(e).mw }));
const recs = [];
for (const [e, r] of B.rec) recs.push({ id: e.id, role: r.role, ring: r.ring, status: r.status, by: r.by ? r.by.id : null, by_role: r.byRole });
process.stdout.write(JSON.stringify({ ctx: ctx.map(c => [c.e.id, c.ring]), B: [...B.keep].map(e => e.id), A: [...A.keep].map(e => e.id), ovr, recs }));
'''
    for fxp in a.mwauth:
        fx = json.load(open(fxp, encoding='utf-8')); P = fx['params']
        sraw = open(fx['catalog_subset'], 'rb').read(); traw = open(fx['mw_authority'], 'rb').read()
        okd = hashlib.sha256(sraw).hexdigest() == fx['catalog_subset_sha256']
        okt = hashlib.sha256(traw).hexdigest() == fx['mw_authority_sha256']
        pool = json.loads(sraw.decode('utf-8'))['events']; _, ents = load_table(fx['mw_authority'])
        t0 = parse_time_ms(P['start'])
        target = [e for e in pool if _hv(P['lat'], P['lon'], e['lat'], e['lon']) <= P['radius_km']
                  and parse_time_ms(e.get('time')) is not None and parse_time_ms(e['time']) >= t0]
        ctx, kept, recs, ovr = mw_run(target, pool, P['lat'], P['lon'], P['radius_km'], t0, P['t_end_ms'], P['mmin'], ents, P['mag_field'])
        checks = [('surum  Python == fixture', fx['version'] == GK74_MWAUTH_VERSION),
                  ('alt katalog sha256', okd), ('otoriter Mw tablosu sha256', okt),
                  ('gecersiz kilinan olaylar == donmus', ovr == fx['overridden']),
                  ('B  Python == donmus', sorted(e['id'] for e in kept) == fx['B']['ids']),
                  ('B  gerekce kayitlari == donmus', recs == fx['B_records']),
                  ('B == G (donmus)', fx['B_equals_G'])]
        print(f"{os.path.basename(fxp)}: hedef {len(target)} | baglam {len(ctx)} | B {len(kept)} | G {fx['G']['n']} | gecersiz kilinan {len(ovr)}")
        for nm, okk in checks:
            print(f"   {nm:45s} {'OK' if okk else 'FARK'}"); allok &= okk
        # JS (index.html) — ayni girdiyle birebir
        from gk74_context import decluster_with_context as _dwc
        from mw_authority import make_mag_fn as _mmf
        pA, _ = _dwc(target, [], P['mag_field'], _mmf(target, ents, P['mag_field']))
        with tempfile.TemporaryDirectory() as td:
            jf, df = os.path.join(td, 'gkm.js'), os.path.join(td, 'in.json')
            open(jf, 'w', encoding='utf-8').write(js3)
            json.dump(dict(field=P['mag_field'], P=P, events=pool, target=[e['id'] for e in target],
                           entries=json.loads(traw.decode('utf-8'))['entries']), open(df, 'w', encoding='utf-8'))
            res = subprocess.run(['node', jf, df], capture_output=True, text=True, check=True)
        J = json.loads(res.stdout)
        jchecks = [('surum  JS == Python', bool(_jsv) and _jsv.group(1) == GK74_MWAUTH_VERSION),
                   ('baglam secimi  JS == Python', [tuple(x) for x in J['ctx']] == [(e['id'], r) for e, r in ctx]),
                   ('gecersiz kilinan  JS == Python', J['ovr'] == ovr),
                   ('B  JS == Python', sorted(J['B']) == sorted(e['id'] for e in kept)),
                   ('B  gerekce kayitlari JS == Python', J['recs'] == recs),
                   ('A (baglamsiz + otorite)  JS == Python', sorted(J['A']) == sorted(e['id'] for e in pA))]
        for nm, okk in jchecks:
            print(f"   {nm:45s} {'OK' if okk else 'FARK'}"); allok &= okk
    print('SONUC:', 'BIREBIR AYNI' if allok else 'FARK VAR')
    sys.exit(0 if allok else 1)

html = open(a.html, encoding='utf-8').read()
m = re.search(r'function gk74Window\(m\).*?(?=\n// GK74 filtresi)', html, re.S)
if not m:
    sys.exit('index.html icinde gk74Window/gk74Decluster bulunamadi')
events = json.load(open(a.catalog, encoding='utf-8'))['events']

if a.context:
    import hashlib
    from gk74_context import select_context, decluster_with_context
    from decluster_gk74 import parse_time_ms, event_mag
    allok = True
    for fxp in a.context:
        fx = json.load(open(fxp, encoding='utf-8'))
        P = fx['params']; mf = P['mag_field']
        catp = fx.get('catalog_subset') or fx['catalog']
        want = fx.get('catalog_subset_sha256') or fx['catalog_sha256']
        raw = open(catp, 'rb').read()
        if hashlib.sha256(raw).hexdigest() != want:
            print(f'{fxp}: UYARI katalog degismis (sha256 farkli) — dondurulmus kimliklerle karsilastirma gecersiz'); allok = False; continue
        allev = json.loads(raw.decode('utf-8'))['events']
        t0 = parse_time_ms(P['start'])
        target = [e for e in allev if haversine(P['lat'], P['lon'], e['lat'], e['lon']) <= P['radius_km']
                  and parse_time_ms(e.get('time')) is not None and parse_time_ms(e['time']) >= t0]
        ctx = select_context(allev, P['lat'], P['lon'], P['radius_km'], t0, P['t_end_ms'], P['mmin'], mf)
        pA, _ = decluster_with_context(target, [], mf)
        pB, precB = decluster_with_context(target, ctx, mf)
        pA = {e['id'] for e in pA}; pB = {e['id'] for e in pB}
        js2 = m.group(0) + r'''
const fs = require('fs');
const inp = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const field = inp.field, P = inp.P;
const all = inp.events.map(e => ({ id: e.id, lat: e.lat, lon: e.lon, mag: e.mag,
  mw: field === 'mw' ? (e.mw ?? undefined) : undefined, time: new Date(e.time) }));
const tset = new Set(inp.target);
const target = all.filter(e => tset.has(e.id));
const ctx = gk74SelectContext(all, P.lat, P.lon, P.radius_km, Date.parse(P.start + 'T00:00:00Z'), P.t_end_ms, P.mmin);
const A = gk74Decluster(target, []), B = gk74Decluster(target, ctx);
const recs = [];
for (const [e, r] of B.rec) recs.push([e.id, r.role, r.ring, r.status, r.by ? r.by.id : null, r.byRole]);
process.stdout.write(JSON.stringify({ ctx: ctx.map(c => [c.e.id, c.ring]), A: [...A.keep].map(e => e.id), B: [...B.keep].map(e => e.id),
  removed: B.removed, removedByCtx: B.removedByCtx, recs }));
'''
        with tempfile.TemporaryDirectory() as td:
            jf, df = os.path.join(td, 'gkc.js'), os.path.join(td, 'in.json')
            open(jf, 'w', encoding='utf-8').write(js2)
            json.dump(dict(field=mf, P=P, events=allev, target=[e['id'] for e in target]), open(df, 'w', encoding='utf-8'))
            res = subprocess.run(['node', jf, df], capture_output=True, text=True, check=True)
        J = json.loads(res.stdout)
        jctx = [tuple(x) for x in J['ctx']]; pctx = [(e['id'], r) for e, r in ctx]
        jA, jB = set(J['A']), set(J['B'])
        frA, frB = set(fx['A']['ids']), set(fx['B']['ids'])
        fr_recs = {r['id']: (r['role'], r['ring'], r['status'], r['by'], r['by_role']) for r in fx['B_records']}
        j_recs = {r[0]: tuple(r[1:]) for r in J['recs']}
        p_recs = {r['id']: (r['role'], r['ring'], r['status'], r['by'], r['by_role']) for r in precB}
        jsver = re.search(r"const GK74_VERSION = '([^']+)'", m.group(0))
        checks = [
            ('surum  JS == fixture', bool(jsver) and jsver.group(1) == fx.get('version')),
            ('baglam secimi  JS == Python', jctx == pctx),
            ('A  Python == dondurulmus', pA == frA), ('A  JS == Python', jA == pA),
            ('B  Python == dondurulmus', pB == frB), ('B  JS == Python', jB == pB),
            ('B  gerekce kayitlari JS == Python', j_recs == p_recs),
            ('B  gerekce kayitlari Python == dondurulmus', p_recs == fr_recs),
            ('B == G (dondurulmus)', fx['B_equals_G']),
        ]
        print(f"{os.path.basename(fxp)}: hedef {len(target)} | baglam {len(pctx)} | A {len(pA)} | B {len(pB)} | G {fx['G']['n']}")
        for name, okk in checks:
            print(f'   {name:45s} {"OK" if okk else "FARK"}'); allok &= okk
    print('SONUC:', 'BIREBIR AYNI' if allok else 'FARK VAR')
    sys.exit(0 if allok else 1)
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
