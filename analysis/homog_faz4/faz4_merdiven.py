"""
Faz 4 — Tamlık merdiveninin değerlendirilmesi (yalnız analiz; mevcut merdiven, üretim kodu ve korunan dosyalar değişmez).
Girdi: sabitlenmiş prototip (homog-faz0 @ f09b26c), faz3_mw_aktarim.py ile yeniden üretilir; GK74 (scripts/decluster_gk74.py).
Önceden tanımlı kanıt ölçütleri — bir büyüklük sınıfı için tamlık başlangıcı ancak İKİSİ birlikte sağlanırsa kabul edilir:
  K1 (bağımsız katalog): o yıldan itibaren her 10 yıllık dilimde ISC-GEM olaylarının ≥ %90'ı prototipte bulunur
     (yalnız ISC-GEM'in kapsadığı M ≥ 5,0 sınıflarında ve 2021'e kadar uygulanabilir).
  K2 (Stepp 1972, Faz 1c'deki Poisson ölçütü): T_ref = 20, 30, 40 yıl için bulunan başlangıç yıllarının en GEÇ olanı
     (en tutucu değer).
  Kabul edilen başlangıç = max(K1, K2). K1 uygulanamayan sınıflarda (M < 5) yalnız K2 raporlanır ve "bağımsız doğrulama yok"
  olarak işaretlenir.
"""
import importlib.util, json, math, collections, sys
sys.path.insert(0, 'scripts'); import decluster_gk74 as GK
def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
F3 = load('analysis/homog_faz3/faz3_mw_aktarim.py', 'f3')
END_Y = 2022.0
CLS = [(3.0, 3.5), (3.5, 4.0), (4.0, 4.5), (4.5, 5.0), (5.0, 5.5), (5.5, 6.0), (6.0, 10.0)]
LADDER = [(1900, 5.5), (1965, 4.5), (1980, 4.0), (1990, 3.5), (1998, 3.0)]
def build_P():
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()): F3.main()
    # faz3 betiği P'yi dosyaya yazmaz; aynı kurallarla yeniden kurmak için aktarım kaydını kullan
    A = json.load(open('data/eq_historical.json'))['events']; L = {l['A_id']: l for l in json.load(open('analysis/homog_faz3/out/aktarim_kaydi.json'))}
    G = [g for g in json.load(open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json')) if g['set'] == 'main' and g['mw'] is not None]
    used = {l['gem_id'] for l in L.values()}
    alt = {a['id'] for a in json.load(open('analysis/homog_faz3/out/alternatif_buyuklukler.json'))}
    P = []
    for e in A:
        y = int(e['time'][:4]); M0 = e['mw'] if e['mw'] is not None else e['mag']
        if e['id'] in L:
            l = L[e['id']]
            if y < 1963:
                g = next(g for g in G if g['eventid'] == l['gem_id']); P.append({'time': g['date'], 'lat': g['lat'], 'lon': g['lon'], 'M': g['mw'], 'gem': g['eventid']})
            else: P.append({'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'M': l['M_yeni'], 'gem': l['gem_id']})
        else: P.append({'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'M': M0, 'gem': None})
    for g in G:
        if int(g['date'][:4]) < 1963 and g['eventid'] not in used and g['eventid'] not in {'16958073'}:
            P.append({'time': g['date'], 'lat': g['lat'], 'lon': g['lon'], 'M': g['mw'], 'gem': g['eventid']})
    return P, G
def stepp_start(ev, lo, hi, Tref):
    yrs = sorted(F3.ts(e['time']) for e in ev if lo <= e['M'] < hi and int(e['time'][:4]) <= 2021)
    yrs = [1970 + t / (365.2425 * 86400) for t in yrs]
    if len(yrs) < 10: return None
    tmax = int(END_Y - math.floor(min(yrs))); lam = lambda T: sum(1 for y in yrs if y >= END_Y - T) / T
    if tmax < Tref: return None
    lr = lam(Tref); Tp = Tref
    for T in range(Tref + 1, tmax + 1):
        if lam(T) < lr - 2 * math.sqrt(lr / T): break
        Tp = T
    return int(END_Y - Tp)
def main():
    P, G = build_P()
    rows, _ = GK.decluster([{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'mag': e['M'], '_gem': e['gem']} for e in P], mag_field='mag')
    _, fl = rows, None
    rr, fl = GK.decluster([{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'mag': e['M'], '_gem': e['gem']} for e in P], mag_field='mag')
    Pd = [{'time': r['time'], 'M': r['mag'], 'gem': r['_gem']} for r, c in zip(rr, fl) if not c]
    pg = {e['gem'] for e in P if e['gem']}
    out = {}
    for lo, hi in CLS:
        key = f'{lo}-{hi if hi < 10 else "+"}'
        k2 = {T: stepp_start(Pd, lo, hi, T) for T in (20, 30, 40)}; k2v = [v for v in k2.values() if v is not None]; K2 = max(k2v) if k2v else None
        K1 = None; dec = []
        if lo >= 5.0:
            for d0 in range(1900, 2020, 10):
                gs = [g for g in G if lo <= g['mw'] < hi and d0 <= int(g['date'][:4]) < d0 + 10]
                if gs: dec.append((d0, len(gs), sum(1 for g in gs if g['eventid'] in pg)))
            ok = [d0 for d0, n, f in dec if f / n >= 0.9]
            # en erken yıl: ondan sonraki TÜM dilimler ≥ %90
            for d0, n, f in dec:
                if all(ff / nn >= 0.9 for dd, nn, ff in dec if dd >= d0): K1 = d0; break
        acc = max([x for x in (K1, K2) if x is not None]) if (K1 is not None or K2 is not None) else None
        cur = next((y for y, mc in LADDER if lo >= mc), None)
        out[key] = {'K1_bagimsiz': K1, 'K1_dilimler(yil,N_ISCGEM,bulunan)': dec, 'K2_Stepp(Tref20/30/40)': k2, 'K2': K2, 'kabul_edilen_baslangic': acc,
                    'dogrulama': 'K1+K2' if K1 is not None else 'yalnız K2 (bağımsız doğrulama yok)', 'mevcut_merdiven_baslangic': cur}
    json.dump({'meta': {'prototip_commit': 'f09b26c91525c5ced2c76db11ac06b3bfbad84ea', 'bitis': '2021-12-31', 'GK74': True, 'olcutler': __doc__.strip().splitlines()[3:9]}, 'siniflar': out},
              open('analysis/homog_faz4/out/merdiven_degerlendirme.json', 'w'), ensure_ascii=False, indent=1)
    print('sınıf | K1 bağımsız | K2 Stepp (20/30/40) | kabul | mevcut merdiven')
    for k, v in out.items(): print(k, '|', v['K1_bagimsiz'], '|', v['K2_Stepp(Tref20/30/40)'], '|', v['kabul_edilen_baslangic'], v['dogrulama'], '|', v['mevcut_merdiven_baslangic'])
if __name__ == '__main__': main()
