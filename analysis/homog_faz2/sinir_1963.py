"""1963 sınırında süreklilik kontrolü (yalnız analiz). Prototip P = ISC-GEM (≤ 1962) + A (≥ 1963).
Kontroller: (1) sınırı geçen yinelenen olay; (2) 1948–1977 beşer yıllık λ(≥5,5), λ(≥6,0): P ile ISC-GEM'in tamamı;
(3) 1963–1975'te aynı olaylar için ΔM = M_A − Mw_ISC-GEM (büyüklük ölçeği sıçraması)."""
import json, math, collections, importlib.util
spec = importlib.util.spec_from_file_location('f', 'analysis/homog_faz2/faz2_compare.py'); f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
A = [{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'M': e['mw'] if e['mw'] is not None else e['mag'], 'mt': (e['mtype'] or '').lower()} for e in json.load(open('data/eq_historical.json'))['events'] if 1945 <= int(e['time'][:4]) < 1980]
G = [{'time': g['date'], 'lat': g['lat'], 'lon': g['lon'], 'M': g['mw'], 's': g['s_mw']} for g in json.load(open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json')) if g['set'] == 'main' and 1945 <= int(g['date'][:4]) < 1980]
f.CM = f.CM + [(1963, 1990, 2, 150)]   # Tablo 2, 1963–1990: ΔT 2 dk, ΔR 150 km
for e in A + G: e['_t'] = f.ts(e['time'])
P = [e for e in G if int(e['time'][:4]) < 1963] + [e for e in A if int(e['time'][:4]) >= 1963]
# (1) sınır: 1962-12-01..1963-01-31 arasında P içinde Tablo 2 ile yakın çift
B = sorted([e for e in P if '1962-12' <= e['time'][:7] <= '1963-01'], key=lambda e: e['_t'])
dup = [(a['time'], b['time']) for i, a in enumerate(B) for b in B[i + 1:] if b['_t'] - a['_t'] <= 600 and f.hav(a, b) <= 200]
# (2) beşer yıllık oranlar (GK74 sonrası)
Pd, Gd = f.gk(P), f.gk(G)
rows = []
for y in range(1948, 1978, 5):
    def lam(ev, th): n = sum(1 for e in ev if y <= int(e['time'][:4]) < y + 5 and e['M'] >= th); return f'{n / 5:.1f}'
    rows.append((f'{y}-{y + 4}', lam(Pd, 5.5), lam(Gd, 5.5), lam(Pd, 6.0), lam(Gd, 6.0)))
# (3) 1963–1975 ΔM
A2 = [e for e in A if 1963 <= int(e['time'][:4]) < 1976]; G2 = [e for e in G if 1963 <= int(e['time'][:4]) < 1976]
mm = f.match(A2, G2); d = collections.defaultdict(list)
for e in A2:
    if id(e) in mm: d[e['mt']].append(e['M'] - mm[id(e)]['M'])
dm = {k: {'n': len(v), 'ort': round(sum(v) / len(v), 2)} for k, v in d.items() if len(v) >= 5}
out = {'sinir_yinelenen_cift': dup, 'oranlar_GK74_sonrasi': [{'donem': r[0], 'P_lam5.5': r[1], 'ISCGEM_lam5.5': r[2], 'P_lam6.0': r[3], 'ISCGEM_lam6.0': r[4]} for r in rows], 'dM_1963_1975_A_eksi_ISCGEM': dm}
json.dump(out, open('analysis/homog_faz2/out/sinir_1963.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(out, ensure_ascii=False, indent=1))
