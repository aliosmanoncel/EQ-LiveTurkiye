"""
Faz 1 / Adım 1 — ISC-GEM doğrulaması ve eşleştirme (yalnız analiz; ana koda ve data/eq_historical.json'a dokunmaz).

Girdi : ISC-GEM v12.1 (isc-gem-cat.csv, isc-gem-suppl.csv) — kullanıcı tarafından resmî formdan indirildi (isc-gem.zip).
Lisans: CC BY-SA 3.0; atıf: International Seismological Centre (2025), ISC-GEM Earthquake Catalogue, doi:10.31905/D808B825.
Eşleştirme: yalnız zaman ve konum (Candia & Macedo 2026, Tablo 2 ΔT ve ΔR). Tablo 2'de 1940 öncesi için ΔR tanımlı
değildir; burada 250 km üst sınır EKLENDİ (aynı zaman penceresinde uzak ayrı olayların eşleşmesini önlemek için) — bu bir
uyarlamadır, raporda belirtilir. ΔM eşleştirme koşulu DEĞİLDİR; tanı olarak raporlanır. Birden çok aday varsa en küçük
normalleştirilmiş uzaklık (Δt/ΔT + Δr/ΔR) seçilir ve aday sayısı kaydedilir.
Kullanım: python analysis/homog_faz1/faz1_iscgem.py <isc-gem-cat.csv> <isc-gem-suppl.csv> [comcat_m45.json]
"""
import bisect, collections, hashlib, json, math, sys
from datetime import datetime, timezone
B = dict(minlat=33.0, maxlat=45.0, minlon=23.0, maxlon=48.0)
COLS = ['date', 'lat', 'lon', 'smajax', 'sminax', 'strike', 'q_loc', 'depth', 'unc_dep', 'q_dep', 'mw', 'unc_mw', 'q_mw', 's_mw', 'mo', 'fac', 'mo_auth',
        'mpp', 'mpr', 'mrr', 'mrt', 'mtp', 'mtt', 'str1', 'dip1', 'rake1', 'str2', 'dip2', 'rake2', 'type', 'eventid']
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def read(p, tag):
    head = [l for l in open(p, encoding='utf-8', errors='replace') if l.startswith('#')]
    ver = next((l[1:].strip() for l in head if 'Version' in l and 'released' in l.lower()), '?')
    hdr = [h.strip() for h in head[-1].lstrip('#').split(',')]
    rows, bad = [], 0
    for l in open(p, encoding='utf-8', errors='replace'):
        if l.startswith('#') or not l.strip(): continue
        x = [v.strip() for v in l.split(',')]
        if len(x) != len(COLS): bad += 1; continue
        d = dict(zip(COLS, x))
        try:
            d['lat'], d['lon'] = float(d['lat']), float(d['lon']); d['mw'] = float(d['mw']) if d['mw'] else None
            d['unc_mw'] = float(d['unc_mw']) if d['unc_mw'] else None; d['depth'] = float(d['depth']) if d['depth'] else None
            d['_t'] = datetime.strptime(d['date'][:19], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp() + float('0.' + d['date'][20:] if len(d['date']) > 20 else 0)
        except ValueError: bad += 1; continue
        d['set'] = tag; rows.append(d)
    return {'file': p.split('/')[-1], 'sha256': sha(p), 'version_line': ver, 'header': hdr, 'header_ok': len(hdr) == len(COLS) and [h for h in hdr if h not in ('q', 'unc')] == [c for c in COLS if not c.startswith(('q_', 'unc_'))], 'n_rows': len(rows), 'n_bad': bad}, rows
def inbox(d): return B['minlat'] <= d['lat'] <= B['maxlat'] and B['minlon'] <= d['lon'] <= B['maxlon']
def hav(a, b):
    r = math.pi / 180; dl = (b['lat'] - a['lat']) * r; do = (b['lon'] - a['lon']) * r
    x = math.sin(dl / 2) ** 2 + math.cos(a['lat'] * r) * math.cos(b['lat'] * r) * math.sin(do / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))
CM = [(-1e9, 1900, 1440, 250), (1900, 1940, 200, 250), (1940, 1963, 10, 200), (1963, 1990, 2, 150), (1990, 3000, 0.5, 100)]   # (ΔT dk, ΔR km); 1940 öncesi ΔR = 250 km uyarlama
def thr(y):
    for a, b, dt, dr in CM:
        if a <= y < b: return dt, dr
def per(y): return '1904-1939' if y < 1940 else '1940-1962' if y < 1963 else '1963-1975' if y < 1976 else '1976-1989' if y < 1990 else '1990-1997' if y < 1998 else '1998-2021'
def mcls(m): return '<5.0' if m < 5 else '5.0-5.5' if m < 5.5 else '5.5-6.0' if m < 6 else '>=6.0'
def match(cat, ref):
    ref = sorted(ref, key=lambda e: e['_t']); rt = [e['_t'] for e in ref]; out = []
    for e in cat:
        dtm, dr = thr(int(e['time'][:4])); i0 = bisect.bisect_left(rt, e['_t'] - dtm * 60); c = []
        for r in ref[i0:]:
            if r['_t'] > e['_t'] + dtm * 60: break
            d = hav(e, r)
            if d <= dr: c.append((abs(r['_t'] - e['_t']) / (dtm * 60) + d / dr, r, d))
        if c: c.sort(key=lambda z: z[0]); out.append((e, c[0][1], c[0][2], len(c)))
    return out
def st(a):
    if not a: return None
    m = sum(a) / len(a); return {'n': len(a), 'ort': round(m, 3), 'std': round((sum((x - m) ** 2 for x in a) / max(1, len(a) - 1)) ** .5, 3), 'ortanca': round(sorted(a)[len(a) // 2], 3)}
def main():
    i1, main_rows = read(sys.argv[1], 'main'); i2, sup_rows = read(sys.argv[2], 'suppl')
    gem = [d for d in main_rows if inbox(d)]; sup = [d for d in sup_rows if inbox(d)]
    yrs = [int(d['date'][:4]) for d in main_rows]
    cov = collections.defaultdict(lambda: collections.Counter())
    for d in gem:
        cov[per(int(d['date'][:4]))][(mcls(d['mw']) if d['mw'] is not None else 'yok', d['s_mw'] or '?')] += 1
    covtab = {p: {f'{k[0]}|{k[1]}': v for k, v in sorted(c.items())} for p, c in sorted(cov.items())}
    qmw = collections.Counter((d['s_mw'], d['q_mw']) for d in gem)
    # EQ-Live kataloğu
    cat = json.load(open('data/eq_historical.json'))['events']
    for e in cat: e['_t'] = datetime.fromisoformat(e['time'].replace('Z', '').split('.')[0]).replace(tzinfo=timezone.utc).timestamp()
    cat21 = [e for e in cat if int(e['time'][:4]) <= 2021]
    P = match(cat21, gem)
    Pg = {id(r) for e, r, d, n in P}
    gem_unmatched = [r for r in gem if id(r) not in Pg]
    # ISC-GEM olaylarının EQ-Live'da bulunma oranı (dönem × Mw)
    tab = collections.defaultdict(lambda: [0, 0])
    for r in gem:
        k = (per(int(r['date'][:4])), mcls(r['mw'])); tab[k][0] += 1; tab[k][1] += id(r) in Pg
    found = {f'{a}|{b}': {'ISC-GEM': v[0], 'EQ-Live_da_var': v[1], 'oran': round(v[1] / v[0], 3)} for (a, b), v in sorted(tab.items())}
    multi = sum(1 for p in P if p[3] > 1)
    dM = collections.defaultdict(list); dMp = collections.defaultdict(list)
    for e, r, d, n in P:
        t = (e['mtype'] or '?').lower(); dM[t].append(e['mag'] - r['mw']); dMp[(t, r['s_mw'])].append(e['mag'] - r['mw'])
    mb_bins = {}
    for lo, hi in [(5, 5.5), (5.5, 6), (6, 9)]:
        for s in ('d', 'p'):
            a = [e['mag'] - r['mw'] for e, r, d, n in P if (e['mtype'] or '').lower() == 'mb' and r['s_mw'] == s and lo <= r['mw'] < hi]
            mb_bins[f'mb|{s}|Mw {lo}-{hi}'] = st(a)
    # ComCat ile karşılaştırma: dönem × sınıf için referans Mw bulunan EQ-Live olayı sayısı
    comp = None
    if len(sys.argv) > 3:
        cc = [e for e in json.load(open(sys.argv[3])) if e['mtype'].startswith('mw')]
        for e in cc: e['_t'] = datetime.fromisoformat(e['time'].split('.')[0]).replace(tzinfo=timezone.utc).timestamp(); e['mw'] = e['mag']
        Pc = match(cat21, cc); hasC = {id(e) for e, r, d, n in Pc}; hasG = {id(e) for e, r, d, n in P}
        t2 = collections.defaultdict(lambda: [0, 0, 0, 0])
        for e in cat21:
            if e['mag'] < 4.5: continue
            k = (per(int(e['time'][:4])), '4.5-5.0' if e['mag'] < 5 else '5.0-5.5' if e['mag'] < 5.5 else '>=5.5')
            t2[k][0] += 1; t2[k][1] += id(e) in hasC; t2[k][2] += id(e) in hasG; t2[k][3] += (id(e) in hasC) or (id(e) in hasG)
        comp = {f'{a}|{b}': {'N_EQLive': v[0], 'ComCat_Mw': v[1], 'ISC-GEM': v[2], 'ikisinden_biri': v[3]} for (a, b), v in sorted(t2.items())}
    rep = {'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'files': [i1, i2],
           'global_main': {'n': len(main_rows), 'year_min': min(yrs), 'year_max': max(yrs)},
           'box': B, 'box_main': len(gem), 'box_suppl': len(sup), 'mw_source_quality': {f'{k[0]}|{k[1]}': v for k, v in sorted(qmw.items())},
           'coverage_box_period_by_Mw_and_source(d=direct,p=proxy)': covtab,
           'match': {'n_pairs': len(P), 'multi_candidate': multi, 'iscgem_unmatched': len(gem_unmatched), 'thresholds': CM},
           'iscgem_found_in_eqlive': found, 'dM_cat_minus_iscgem_by_type': {k: st(v) for k, v in sorted(dM.items(), key=lambda x: -len(x[1]))},
           'dM_by_type_and_mw_source': {f'{k[0]}|{k[1]}': st(v) for k, v in sorted(dMp.items(), key=lambda x: -len(x[1]))}, 'mb_saturation': mb_bins,
           'reference_coverage_vs_comcat': comp,
           'unmatched_iscgem_sample': [{k: r[k] for k in ('date', 'lat', 'lon', 'depth', 'mw', 's_mw', 'eventid')} for r in gem_unmatched[:40]]}
    json.dump(rep, open('analysis/homog_faz1/out/faz1_iscgem_rapor.json', 'w'), ensure_ascii=False, indent=1)
    json.dump([{'eventid': r['eventid'], 'date': r['date'], 'lat': r['lat'], 'lon': r['lon'], 'depth': r['depth'], 'mw': r['mw'], 'unc_mw': r['unc_mw'], 'q_mw': r['q_mw'], 's_mw': r['s_mw'], 'mo_auth': r['mo_auth'], 'set': r['set']} for r in gem + sup],
              open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump([{'cat_id': e['id'], 'cat_time': e['time'], 'cat_src': e['src'], 'cat_mag': e['mag'], 'cat_mtype': e['mtype'], 'gem_id': r['eventid'], 'gem_mw': r['mw'], 'gem_s': r['s_mw'], 'gem_q': r['q_mw'], 'dt_s': round(abs(r['_t'] - e['_t']), 1), 'dr_km': round(d, 1), 'n_cand': n} for e, r, d, n in P],
              open('analysis/homog_faz1/out/iscgem_eslesmeler.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(json.dumps({k: rep[k] for k in ('files', 'global_main', 'box_main', 'box_suppl', 'match')}, ensure_ascii=False, indent=1))
if __name__ == '__main__': main()
