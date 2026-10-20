"""
Faz 2 — 1904–1962 için üç seçeneğin karşılaştırması (yalnız analiz; üretim koduna, eq_historical.json'a, GK74 koduna,
mw_authority.json'a ve mevcut merdivene DOKUNMAZ).

A    : mevcut eq_historical.json (1904–1962), büyüklük mw ?? mag.
(a)  : süzgeçsiz ISC Bulletin (fetch_isc_nofilter.py). Büyüklük seçimi ÖNCEDEN tanımlı kural:
       1) Mw türü varsa o; 2) sığ (derinlik < 60 km ya da bilinmiyor): Ms > mb > diğer; derin: mb > Ms > diğer
       (Candia & Macedo 2026 sırası); aynı tür içinde yazar önceliği ISC > GUTE > PAS > B&D > MOS > diğer.
       Mw'ye çevrim yalnız Scordilis (2006) geçerlilik aralıklarında (Ms 3,0–6,1: 0,67Ms+2,07; Ms 6,2–8,2: 0,99Ms+0,08;
       mb 3,5–6,2: 0,85mb+1,03); diğer türler çevrilmez ve Mw tabanlı istatistiğe girmez (ayrı sayılır).
(b)  : ISC-GEM v12.1 ana katalog, Mw (doğrudan ve vekil AYRI raporlanır).
(c)  : (b) + (a)'nın (b) ile eşleşmeyen olayları. Eşleştirme yalnız kataloglar arası, zaman–konum (Tablo 2 ΔT/ΔR;
       1940 öncesi ΔR = 250 km uyarlaması). Eşleşmede Mw = ISC-GEM; eşleşmeyen (a) olayında Scordilis Mw.
Ölçütler (her seri, GK74 öncesi ve sonrası): sınıf sayıları; λ(≥5,5), λ(≥6,0) = N/T ± √N/T (T = 59 yıl);
  b (Aki 1965, M ≥ 5,5; ΔM: değerler 0,1 ızgarasındaysa 0,1, değilse 0) ± b/√N; Weichert (1980) b ve λ(≥5,5), tek dönem,
  0,1'lik sınıflar; Mc (maks. eğrilik + 0,2) bilgi amaçlı.
"""
import bisect, collections, hashlib, json, math, os, sys
from datetime import datetime, timezone
sys.path.insert(0, 'scripts'); import decluster_gk74 as GK
Y0, Y1 = 1904, 1963; T = Y1 - Y0
OUT = 'analysis/homog_faz2/out'
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None
def ts(s): return datetime.fromisoformat(s.replace('Z', '').replace(' ', 'T').split('.')[0]).replace(tzinfo=timezone.utc).timestamp()
def hav(a, b):
    r = math.pi / 180; dl = (b['lat'] - a['lat']) * r; do = (b['lon'] - a['lon']) * r
    x = math.sin(dl / 2) ** 2 + math.cos(a['lat'] * r) * math.cos(b['lat'] * r) * math.sin(do / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))
AUTH = ['ISC', 'GUTE', 'PAS', 'B&D', 'MOS']
def pick(e):
    ms = [m for m in e['mags'] if m['mag'] is not None]
    if not ms: return None, None, None
    def typ(m): t = (m['type'] or '').lower(); return 'mw' if t.startswith('mw') else 'ms' if t.startswith('ms') else 'mb' if t.startswith('mb') else 'other'
    deep = e.get('dep_km') is not None and e['dep_km'] >= 60
    order = ['mw', 'mb', 'ms', 'other'] if deep else ['mw', 'ms', 'mb', 'other']
    for tp in order:
        c = [m for m in ms if typ(m) == tp]
        if c:
            c.sort(key=lambda m: AUTH.index(m['author']) if m['author'] in AUTH else len(AUTH)); m = c[0]; return m['mag'], tp, m['author']
def scord(m, tp):
    if tp == 'mw': return m
    if tp == 'ms' and 3.0 <= m <= 6.1: return 0.67 * m + 2.07
    if tp == 'ms' and 6.2 <= m <= 8.2: return 0.99 * m + 0.08
    if tp == 'mb' and 3.5 <= m <= 6.2: return 0.85 * m + 1.03
    return None
def aki(m, mmin):
    s = [x for x in m if x >= mmin - 1e-9]
    if len(s) < 10: return None
    grid = all(abs(x * 10 - round(x * 10)) < 1e-6 for x in s); dm = 0.1 if grid else 0.0
    b = math.log10(math.e) / (sum(s) / len(s) - (mmin - dm / 2) if dm else sum(s) / len(s) - mmin)
    return {'b': round(b, 3), 'sb': round(b / math.sqrt(len(s)), 3), 'N': len(s), 'dM': dm}
def weichert(m, mmin=5.5, dm=0.1):
    """Weichert (1980) MLE, tek dönem T; sınıf merkezleri mmin+dm/2, ..."""
    s = [x for x in m if x >= mmin - 1e-9]
    if len(s) < 10: return None
    grid = all(abs(x * 10 - round(x * 10)) < 1e-6 for x in s)   # 0,1 ızgarasındaki değerler sınıf merkezidir
    if grid:
        k = collections.Counter(int(round((x - mmin) / dm)) for x in s); bins = sorted(k); Mi = [mmin + i * dm for i in bins]
    else:
        k = collections.Counter(int((x - mmin + 1e-9) // dm) for x in s); bins = sorted(k); Mi = [mmin + (i + 0.5) * dm for i in bins]
    ni = [k[i] for i in bins]
    beta = 2.0
    for _ in range(100):
        w = [T * math.exp(-beta * M) for M in Mi]; sw = sum(w); swm = sum(a * M for a, M in zip(w, Mi)); swm2 = sum(a * M * M for a, M in zip(w, Mi))
        N = sum(ni); nm = sum(n * M for n, M in zip(ni, Mi))
        f = swm / sw - nm / N; d = (swm / sw) ** 2 - swm2 / sw
        if abs(d) < 1e-15: break
        nb = beta - f / d
        if abs(nb - beta) < 1e-7: beta = nb; break
        beta = nb
    w = [T * math.exp(-beta * M) for M in Mi]; sw = sum(w); swm = sum(a * M for a, M in zip(w, Mi)); swm2 = sum(a * M * M for a, M in zip(w, Mi))
    var = 1 / (N * (swm2 / sw - (swm / sw) ** 2)); b = beta / math.log(10)
    return {'b': round(b, 3), 'sb': round(math.sqrt(var) / math.log(10), 3), 'lam_ge_mmin': round(N / T, 3), 'sd_lam': round(math.sqrt(N) / T, 3), 'N': N}
def mc_maxc(m):
    c = collections.Counter(round(x, 1) for x in m)
    return round(max(c, key=c.get) + 0.2, 1) if len(m) >= 30 else None
def stats(ev):
    m = [e['M'] for e in ev]
    cl = collections.Counter('5.0-5.5' if x < 5.5 else '5.5-6.0' if x < 6 else '6.0-6.5' if x < 6.5 else '>=6.5' for x in m if x >= 5.0)
    per = collections.Counter(('1904-1939' if int(e['time'][:4]) < 1940 else '1940-1962', '5.5-6.0' if e['M'] < 6 else '>=6.0') for e in ev if e['M'] >= 5.5)
    n55 = sum(1 for x in m if x >= 5.5); n6 = sum(1 for x in m if x >= 6)
    return {'N_tumu': len(m), 'siniflar': dict(sorted(cl.items())), 'donem_sinif': {f'{a}|{b}': v for (a, b), v in sorted(per.items())},
            'lam_ge5.5': f'{n55 / T:.3f} ± {math.sqrt(n55) / T:.3f}', 'lam_ge6.0': f'{n6 / T:.3f} ± {math.sqrt(n6) / T:.3f}',
            'Mc_maxc': mc_maxc([x for x in m if x >= 4.0]), 'aki_M5.5': aki(m, 5.5), 'aki_M6.0': aki(m, 6.0), 'weichert_M5.5': weichert(m)}
def gk(ev):
    rows, fl = GK.decluster([{**e, 'mag': e['M']} for e in ev], mag_field='mag'); return [e for e, c in zip(rows, fl) if not c]
CM = [(1900, 1940, 200, 250), (1940, 1963, 10, 200)]
def match(a_ev, b_ev):
    bs = sorted(b_ev, key=lambda e: e['_t']); bt = [e['_t'] for e in bs]; used = {}
    for e in a_ev:
        dtm, dr = next((dt, d) for y0, y1, dt, d in CM if y0 <= int(e['time'][:4]) < y1)
        i0 = bisect.bisect_left(bt, e['_t'] - dtm * 60); best = None
        for r in bs[i0:]:
            if r['_t'] > e['_t'] + dtm * 60: break
            d = hav(e, r)
            if d <= dr:
                s = abs(r['_t'] - e['_t']) / (dtm * 60) + d / dr
                if best is None or s < best[0]: best = (s, r)
        if best: used[id(e)] = best[1]
    return used
def main():
    A = [{'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'M': e['mw'] if e['mw'] is not None else e['mag'], 'src': 'A'} for e in json.load(open('data/eq_historical.json'))['events'] if Y0 <= int(e['time'][:4]) < Y1]
    gem = [g for g in json.load(open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json')) if g['set'] == 'main' and Y0 <= int(g['date'][:4]) < Y1 and g['mw'] is not None]
    Bb = [{'time': g['date'], 'lat': g['lat'], 'lon': g['lon'], 'M': g['mw'], 'mw_src': 'iscgem_direct' if g['s_mw'] == 'd' else 'iscgem_proxy', 'id': g['eventid']} for g in gem]
    S = {'A_mevcut': A, 'b_ISCGEM': Bb}
    SPLIT = {'b_ISCGEM': 'mw_src'}   # doğrudan/vekil ayrımı: GK74 TÜM (b) üzerinde yapılır, sonra alt kümelere ayrılır (alt küme kümesizleştirilmez)
    pa = 'analysis/homog_faz2/out/isc_1904_1962_nofilter.json'; meta_a = None
    if os.path.exists(pa):
        J = json.load(open(pa)); meta_a = {k: J['meta'][k] for k in ('generated', 'n', 'params')}; meta_a['yillar_hatali'] = [l for l in J['meta']['log'] if l['status'] not in (200, 204)]
        a_raw, a_types, nomag = [], collections.Counter(), 0
        for e in J['events']:
            if not (Y0 <= int(e['time'][:4]) < Y1): continue
            m, tp, au = pick(e)
            if m is None: nomag += 1; continue
            a_types[(tp, au)] += 1
            a_raw.append({'time': e['time'], 'lat': e['lat'], 'lon': e['lon'], 'Mraw': m, 'tp': tp, 'author': au, 'Mw': scord(m, tp), 'id': e['id']})
        meta_a['buyukluksuz_olay'] = nomag; meta_a['secilen_tur_yazar'] = {f'{k[0]}|{k[1]}': v for k, v in a_types.most_common(15)}
        S['a_ham_buyukluk'] = [{**e, 'M': e['Mraw']} for e in a_raw]
        S['a_Scordilis_Mw'] = [{**e, 'M': e['Mw'], 'mw_src': 'scordilis2006_' + e['tp']} for e in a_raw if e['Mw'] is not None]
        meta_a['Mw_cevrilemeyen(tur disi)'] = sum(1 for e in a_raw if e['Mw'] is None)
        # (c) birleşik
        for e in a_raw + Bb: e['_t'] = ts(e['time'])
        mm = match(a_raw, Bb); matched_b = {id(r) for r in mm.values()}
        C = [dict(e) for e in Bb] + [{**e, 'M': e['Mw'], 'mw_src': 'scordilis2006_' + e['tp']} for e in a_raw if id(e) not in mm and e['Mw'] is not None]
        S['c_birlesik'] = C
        meta_a['c'] = {'a_olay_ISCGEM_ile_eslesen': len(mm), 'ISCGEM_olayi_a_da_bulunan': len(matched_b), 'eklenen_a_olayi': sum(1 for e in C if e.get('mw_src', '').startswith('scordilis')),
                       'eklenen_a_M>=5.5': sum(1 for e in C if e.get('mw_src', '').startswith('scordilis') and e['M'] >= 5.5)}
        # süzgeç kaybının ölçümü: (a)'da ham büyüklüğü >= 5,5 olup A'da olmayanlar
        for e in A: e['_t'] = ts(e['time'])
        inA = match([e for e in a_raw], [{**x} for x in A])
        meta_a['a_M>=5.5_ham_A_da_yok'] = sum(1 for e in a_raw if e['Mraw'] >= 5.5 and id(e) not in inA)
        meta_a['a_M>=5.5_ham_toplam'] = sum(1 for e in a_raw if e['Mraw'] >= 5.5)
    res = {}
    for k, ev in S.items():
        dc = gk(ev); res[k] = {'GK74_oncesi': stats(ev), 'GK74_sonrasi': stats(dc)}
        if k == 'b_ISCGEM':
            for src in ('iscgem_direct', 'iscgem_proxy'):
                res[f'{k}|{src}'] = {'GK74_oncesi': stats([e for e in ev if e['mw_src'] == src]), 'GK74_sonrasi': stats([e for e in dc if e['mw_src'] == src]),
                                     'not': 'alt küme; doğrudan Mw 1963 öncesinde yalnız büyük olaylarda var — b karşılaştırılamaz (seçim yanlılığı)'}
        if k == 'c_birlesik':
            for src in ('iscgem_direct', 'iscgem_proxy', 'scordilis2006_ms', 'scordilis2006_mb', 'scordilis2006_mw'):
                res[f'{k}|{src}'] = {'N_GK74_oncesi': sum(1 for e in ev if e.get('mw_src') == src), 'N_GK74_sonrasi': sum(1 for e in dc if e.get('mw_src') == src)}
    json.dump({'meta': {'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'period': f'{Y0}-{Y1 - 1}', 'T_yil': T,
                        'inputs': {p: sha(p) for p in ('data/eq_historical.json', 'analysis/homog_faz1/out/iscgem_v12.1_kutu.json', pa, 'scripts/decluster_gk74.py')}, 'a': meta_a},
               'sonuclar': res}, open(f'{OUT}/faz2_karsilastirma.json', 'w'), ensure_ascii=False, indent=1)
    for k, v in res.items():
        for g, s in v.items():
            if not isinstance(s, dict) or 'N_tumu' not in s: continue
            print(f"{k:20s} {g:12s} N={s['N_tumu']:5d} {s['siniflar']} λ5.5={s['lam_ge5.5']} λ6={s['lam_ge6.0']} b_aki={s['aki_M5.5'] and (s['aki_M5.5']['b'], s['aki_M5.5']['sb'])} W={s['weichert_M5.5'] and (s['weichert_M5.5']['b'], s['weichert_M5.5']['sb'])}")
    print(json.dumps(meta_a, ensure_ascii=False, indent=1) if meta_a else '(a) verisi henüz yok')
if __name__ == '__main__': main()
