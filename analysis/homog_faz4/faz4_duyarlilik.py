"""
Faz 4 — 13 olay (1963–1964) duyarlılık analizi. Ana kataloğa EKLEME YOKTUR.
Kullanıcı kararı (2026-10-21): olaylar yalnız ayrı bir duyarlılık veri kümesinde tutulur; tamlık testleri
(K1 + K2, faz4_merdiven.py'deki önceden tanımlı ölçütlerin AYNISI) üç seri için karşılaştırılır:
  S0  prototip (13 olaysız)                         — referans
  S1  prototip + 13 olay (ISC-GEM vekil Mw, B+C)
  S2  prototip + yalnız kalite B olan 5 olay        — vekil Mw kalitesine duyarlılık
Mevcut merdiven, üretim kodu ve korunan dosyalar değişmez.
"""
import importlib.util, json, sys, io, contextlib, subprocess
sys.path.insert(0, 'scripts'); import decluster_gk74 as GK
s = importlib.util.spec_from_file_location('f4', 'analysis/homog_faz4/faz4_merdiven.py'); F4 = importlib.util.module_from_spec(s); s.loader.exec_module(F4)
OUT = 'analysis/homog_faz4/out/'
def evaluate(P, G):
    rr, fl = GK.decluster([{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'mag': e['M'], '_gem': e['gem']} for e in P], mag_field='mag')
    Pd = [{'time': r['time'], 'M': r['mag'], 'gem': r['_gem']} for r, c in zip(rr, fl) if not c]
    pg = {e['gem'] for e in P if e['gem']}; out = {}
    for lo, hi in F4.CLS:
        key = f'{lo}-{hi if hi < 10 else "+"}'
        k2 = {T: F4.stepp_start(Pd, lo, hi, T) for T in (20, 30, 40)}; v = [x for x in k2.values() if x is not None]; K2 = max(v) if v else None
        K1, dec = None, []
        if lo >= 5.0:
            for d0 in range(1900, 2020, 10):
                gs = [g for g in G if lo <= g['mw'] < hi and d0 <= int(g['date'][:4]) < d0 + 10]
                if gs: dec.append((d0, len(gs), sum(1 for g in gs if g['eventid'] in pg)))
            for d0, n, f in dec:
                if all(ff / nn >= 0.9 for dd, nn, ff in dec if dd >= d0): K1 = d0; break
        xs = [x for x in (K1, K2) if x is not None]
        out[key] = {'K1': K1, 'K1_dilimler': dec, 'K2_Tref': k2, 'K2': K2, 'kabul': max(xs) if xs else None,
                    'n_kumesiz': sum(1 for e in Pd if lo <= e['M'] < hi)}
    return out
def main():
    with contextlib.redirect_stdout(io.StringIO()): P, G = F4.build_P()
    subprocess.run(['git', 'checkout', '--', 'analysis/homog_faz3/out/faz3_rapor.json'], check=False)  # yalnız zaman damgası değişir
    V = json.load(open(OUT + 'dogrulama_13.json'))
    have = {e['gem'] for e in P if e['gem']}
    D = []
    for e in V:
        assert e['sonuc'].startswith('ISC var') and e['gem_id'] not in have
        isc = next(b for b in e['B1'] if b['id'] == e['gem_id'])
        D.append({'gem_id': e['gem_id'], 'time': e['tarih'].replace(' ', 'T'), 'lat': e['enlem'], 'lon': e['boylam'], 'derinlik': e['derinlik'],
                  'Mw': e['Mw'], 'mw_src': 'iscgem_proxy' if e['kaynak'] == 'p' else 'iscgem_direct', 'kalite': e['kalite'],
                  'isc_mag': isc['mag'], 'isc_mtype': isc['mtype'], 'isc_magauthor': isc['magauthor'],
                  'durum': 'yalnız duyarlılık — ana kataloğa eklenmedi'})
    json.dump({'meta': {'kaynak': 'ISC-GEM v12.1 (CC BY-SA 3.0) + ISC FDSN doğrulaması (dogrulama_13.json)', 'karar': 'b — yalnız duyarlılık, 2026-10-21'},
               'olaylar': D}, open(OUT + 'duyarlilik_13_veri.json', 'w'), ensure_ascii=False, indent=1)
    add = lambda sub: P + [{'time': d['time'], 'lat': d['lat'], 'lon': d['lon'], 'M': d['Mw'], 'gem': d['gem_id']} for d in sub]
    R = {'S0_13siz': evaluate(P, G), 'S1_13_ile_BC': evaluate(add(D), G), 'S2_yalniz_B': evaluate(add([d for d in D if d['kalite'] == 'B']), G)}
    json.dump({'meta': {'olcutler': 'faz4_merdiven.py ile aynı (K1 ≥%90/dilim, K2 Stepp Tref 20/30/40 en geç; kabul = max)', 'mevcut_merdiven': F4.LADDER,
               'n_eklenen': {'S0': 0, 'S1': len(D), 'S2': sum(d['kalite'] == 'B' for d in D)}}, 'seriler': R},
              open(OUT + 'duyarlilik_13_sonuc.json', 'w'), ensure_ascii=False, indent=1)
    print('sınıf     | ' + ' | '.join(f'{k}: K1 / K2(20,30,40) → kabul' for k in R))
    for c in R['S0_13siz']:
        print(c.ljust(9), '|', ' | '.join(f"{R[k][c]['K1']} / {tuple(R[k][c]['K2_Tref'].values())} → {R[k][c]['kabul']}" for k in R))
    for c in ('5.0-5.5', '5.5-6.0'):
        for k in R: print(c, k, 'K1 dilimleri 1950–1980:', [d for d in R[k][c]['K1_dilimler'] if 1950 <= d[0] <= 1980])
if __name__ == '__main__': main()
