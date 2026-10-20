"""
Faz 5 (salt okunur aktarım planı) — etki analizi için katalog serileri.
C0: üretimdeki eq_historical.json (Original: yerel Mw varsa mw, yoksa mag — index.html panelBaseMag ile aynı).
C1: sabitlenmiş prototip (faz4_merdiven.build_P: ISC-GEM v12.1 Mw aktarımı + 1963 öncesi ISC-GEM olayları).
Her ikisi ham ve GK74 (scripts/decluster_gk74.py) olarak; dönem 1900-01-01 – 2021-12-31 (ISC-GEM kapsamı).
Hiçbir üretim dosyası yazılmaz; çıktı yalnız argv[1] dizinine.
"""
import importlib.util, json, sys, io, contextlib, subprocess, os
sys.path.insert(0, 'scripts'); import decluster_gk74 as GK
s = importlib.util.spec_from_file_location('f4', 'analysis/homog_faz4/faz4_merdiven.py'); F4 = importlib.util.module_from_spec(s); s.loader.exec_module(F4)
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
A = json.load(open('data/eq_historical.json'))['events']
C0 = [{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'mag': e['mw'] if e['mw'] is not None else e['mag']} for e in A]
with contextlib.redirect_stdout(io.StringIO()): P, _ = F4.build_P()
subprocess.run(['git', 'checkout', '--', 'analysis/homog_faz3/out/faz3_rapor.json'], check=False)
C1 = [{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'mag': e['M']} for e in P]
keep = lambda L: [e for e in L if e['mag'] is not None and '1900' <= e['time'][:4] <= '2021']
meta = {}
for name, L in (('C0', keep(C0)), ('C1', keep(C1))):
    rr, fl = GK.decluster([dict(e) for e in L], mag_field='mag')
    for tag, S in (('ham', L), ('gk74', [r for r, c in zip(rr, fl) if not c])):
        json.dump([[e['time'], round(e['mag'], 3)] for e in S], open(f'{out}/{name}_{tag}.json', 'w'))
        meta[f'{name}_{tag}'] = len(S)
print(json.dumps(meta))
