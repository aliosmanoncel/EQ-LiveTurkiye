"""
Katalog homojenizasyonu — Faz 0 (yalnızca inceleme; EQ-Live ana koduna ve data/eq_historical.json'a DOKUNMAZ).

Amaç
 1. Referans Mw kaynaklarını indirmek: USGS ComCat (FDSN; GCMT/USGS W-faz Mw'lerini içerir) ve ISC-GEM.
 2. eq_historical.json olaylarını referans olaylarla eşleştirmek (Candia & Macedo 2026, Tablo 2 dönem eşikleri:
    ΔT, ΔR, ΔM). Eşleşme yalnızca FARKLI kataloglar arasında yapılır (aynı katalog içindeki yakın olaylar
    gerçek artçılar olabilir).
 3. Raporlamak: eşleşme oranı (dönem × büyüklük), ΔM = M_katalog − Mw_ref (tür bazında), Scordilis (2006)
    dönüşümünün referansa göre sapması, ve b-değeri / Mc'nin referans Mw ile değiştirildiğinde nasıl değiştiği.

Çıktılar: analysis/homog_faz0/out/*.json ve rapor.md (iş akışı bunları homog-faz0 dalına yazar).
"""
import csv, io, json, math, os, sys, time, urllib.request, zipfile, collections
from datetime import datetime, timezone

OUT = 'analysis/homog_faz0/out'; os.makedirs(OUT, exist_ok=True)
B = dict(minlat=33.0, maxlat=45.0, minlon=23.0, maxlon=48.0)   # eq_historical.json ile aynı kutu
LOG = []
def log(s): print(s); LOG.append(s)
def get(url, timeout=180, tries=3):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'EQ-LiveTurkiye homog-faz0'})
            with urllib.request.urlopen(req, timeout=timeout) as r: return r.read()
        except Exception as e:
            last = e; time.sleep(5 * (k + 1))
    raise last

# ── 1a. ComCat (USGS FDSN), M ≥ 4.5, 10 yıllık dilimler ───────────────────────────────────────────────
def comcat():
    ev = []
    for y0 in range(1900, 2030, 10):
        y1 = min(y0 + 10, datetime.now(timezone.utc).year + 1)
        u = ('https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&orderby=time-asc&minmagnitude=4.5'
             f'&starttime={y0}-01-01&endtime={y1}-01-01&minlatitude={B["minlat"]}&maxlatitude={B["maxlat"]}'
             f'&minlongitude={B["minlon"]}&maxlongitude={B["maxlon"]}&limit=20000')
        try:
            rows = list(csv.DictReader(io.StringIO(get(u).decode('utf-8', 'replace'))))
        except Exception as e:
            log(f'ComCat {y0}-{y1}: HATA {e}'); continue
        for r in rows:
            try: ev.append({'id': r['id'], 'time': r['time'].replace('Z', ''), 'lat': float(r['latitude']), 'lon': float(r['longitude']),
                            'dep': float(r['depth'] or 0), 'mag': float(r['mag']), 'mtype': r['magType'].lower(), 'src': 'ComCat', 'net': r.get('net', '')})
            except ValueError: pass
        log(f'ComCat {y0}-{y1}: {len(rows)} olay'); time.sleep(1)
    return ev

# ── 1b. ISC-GEM (birkaç olası adres denenir; biçim CSV, '#' yorum satırları) ────────────────────────────
ISCGEM_URLS = ['http://www.isc.ac.uk/iscgem/iscgem_download/isc-gem-cat.zip', 'https://www.isc.ac.uk/iscgem/iscgem_download/isc-gem-cat.zip',
               'http://www.isc.ac.uk/iscgem/iscgem_download/isc-gem-cat.csv', 'https://www.isc.ac.uk/iscgem/iscgem_download/isc-gem-cat.csv']
def iscgem():
    for u in ISCGEM_URLS:
        try: raw = get(u, timeout=300, tries=2)
        except Exception as e: log(f'ISC-GEM {u}: HATA {e}'); continue
        if raw[:2] == b'PK':
            z = zipfile.ZipFile(io.BytesIO(raw)); name = [n for n in z.namelist() if n.lower().endswith('.csv')][0]; txt = z.read(name).decode('utf-8', 'replace')
        else: txt = raw.decode('utf-8', 'replace')
        lines = [l for l in txt.splitlines() if l.strip() and not l.lstrip().startswith('#')]
        hdr_i = next((i for i, l in enumerate(txt.splitlines()) if 'date' in l.lower() and 'lat' in l.lower() and l.lstrip().startswith('#')), None)
        hdr = [h.strip().lower() for h in txt.splitlines()[hdr_i].lstrip('#').split(',')] if hdr_i is not None else None
        log(f'ISC-GEM {u}: {len(lines)} satır; başlık: {hdr[:16] if hdr else "bulunamadı"}')
        if not hdr: return []
        ix = {k: hdr.index(k) for k in hdr}
        out = []
        for l in lines:
            p = [x.strip() for x in l.split(',')]
            try:
                lat, lon = float(p[ix['lat']]), float(p[ix['lon']])
                if not (B['minlat'] <= lat <= B['maxlat'] and B['minlon'] <= lon <= B['maxlon']): continue
                mw = float(p[ix['mw']]); t = p[ix['date']].replace(' ', 'T')
                out.append({'id': p[ix.get('eventid', len(p) - 1)] if 'eventid' in ix else t, 'time': t, 'lat': lat, 'lon': lon, 'dep': float(p[ix['depth']] or 0) if 'depth' in ix else 0,
                            'mag': mw, 'mtype': 'mw', 'src': 'ISC-GEM'})
            except (ValueError, KeyError, IndexError): pass
        log(f'ISC-GEM kutu içi: {len(out)} olay'); return out
    return []

# ── 2. Eşleştirme (Candia & Macedo 2026, Tablo 2) ─────────────────────────────────────────────────────
CM = [(-1e9, 1900, 1.75, None, 1440), (1900, 1940, 1.5, None, 200), (1940, 1963, 1.25, 200, 10), (1963, 1990, 1.0, 150, 2), (1990, 3000, 0.75, 100, 0.5)]
def thr(y):
    for a, b, dm, dr, dt in CM:
        if a <= y < b: return dm, dr, dt
def ts(s): return datetime.fromisoformat(s.replace('Z', '').split('.')[0]).replace(tzinfo=timezone.utc).timestamp()
def hav(a, b):
    r = math.pi / 180; dl = (b['lat'] - a['lat']) * r; do = (b['lon'] - a['lon']) * r
    x = math.sin(dl / 2) ** 2 + math.cos(a['lat'] * r) * math.cos(b['lat'] * r) * math.sin(do / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))
def match(cat, ref):
    for e in cat + ref: e['_t'] = ts(e['time'])
    ref = sorted(ref, key=lambda e: e['_t']); import bisect; rt = [e['_t'] for e in ref]
    pairs = []
    for e in cat:
        y = int(e['time'][:4]); dm, dr, dtm = thr(y)
        i0 = bisect.bisect_left(rt, e['_t'] - dtm * 60); best = None
        for r in ref[i0:]:
            if r['_t'] > e['_t'] + dtm * 60: break
            d = hav(e, r); m_e = e['mag']
            if (dr is None or d <= dr) and abs(m_e - r['mag']) <= dm:
                s = abs(r['_t'] - e['_t']) / (dtm * 60) + (d / dr if dr else 0) + abs(m_e - r['mag']) / dm   # en yakın aday
                if best is None or s < best[0]: best = (s, r, d)
        if best: pairs.append((e, best[1], best[2]))
    return pairs

# ── 3. b-değeri (Aki 1965) ve Mc (maks. eğrilik + 0,2) ─────────────────────────────────────────────────
def mc_maxc(m):
    if len(m) < 30: return None
    c = collections.Counter(round(x, 1) for x in m); return round(max(c, key=c.get) + 0.2, 1)
def aki(m, mc, dm=0.1):
    s = [x for x in m if x >= mc - 1e-9]
    if len(s) < 30: return None, None, len(s)
    b = math.log10(math.e) / (sum(s) / len(s) - mc + dm / 2); return b, b / math.sqrt(len(s)), len(s)

def main():
    cat = json.load(open('data/eq_historical.json'))['events']
    log(f'eq_historical.json: {len(cat)} olay')
    cc = comcat(); json.dump(cc, open(f'{OUT}/comcat_m45.json', 'w'), separators=(',', ':'))
    ig = iscgem(); json.dump(ig, open(f'{OUT}/iscgem_box.json', 'w'), separators=(',', ':'))
    ref_mw = [e for e in cc if e['mtype'].startswith('mw')] + ig
    log(f'Referans Mw olayları: ComCat Mw {sum(1 for e in cc if e["mtype"].startswith("mw"))}, ISC-GEM {len(ig)}')
    big = [e for e in cat if e['mag'] >= 4.0]
    P = match(big, ref_mw)
    # eşleşme oranı
    tab = collections.defaultdict(lambda: [0, 0])
    for e in big:
        y = int(e['time'][:4]); per = '1900-1963' if y < 1963 else '1963-1990' if y < 1990 else '1990-1998' if y < 1998 else '1998-'
        mb = '4.0-4.5' if e['mag'] < 4.5 else '4.5-5.0' if e['mag'] < 5 else '5.0-5.5' if e['mag'] < 5.5 else '>=5.5'
        tab[(per, mb)][0] += 1
    for e, r, d in P:
        y = int(e['time'][:4]); per = '1900-1963' if y < 1963 else '1963-1990' if y < 1990 else '1990-1998' if y < 1998 else '1998-'
        mb = '4.0-4.5' if e['mag'] < 4.5 else '4.5-5.0' if e['mag'] < 5 else '5.0-5.5' if e['mag'] < 5.5 else '>=5.5'
        tab[(per, mb)][1] += 1
    # ΔM tür bazında; Scordilis (mw alanı dolu ve native değilse) sapması
    dM = collections.defaultdict(list); dS = collections.defaultdict(list)
    for e, r, d in P:
        t = (e['mtype'] or '?').lower(); dM[t].append(e['mag'] - r['mag'])
        if e.get('mw') is not None and e.get('mw_method') != 'native': dS[e.get('mw_method')].append(e['mw'] - r['mag'])
    st = lambda a: {'n': len(a), 'ort': round(sum(a) / len(a), 3), 'std': round((sum((x - sum(a) / len(a)) ** 2 for x in a) / max(1, len(a) - 1)) ** .5, 3), 'ortanca': round(sorted(a)[len(a) // 2], 3)} if a else None
    # b / Mc etkisi: (A) mevcut (mw ?? mag) ; (B) eşleşenlerde referans Mw
    sub = {id(e): r['mag'] for e, r, d in P}
    res_b = {}
    for per, (a, b_) in {'1998-': (1998, 3000), '1963-1998': (1963, 1998), 'tümü': (0, 3000)}.items():
        A = [e['mw'] if e['mw'] is not None else e['mag'] for e in cat if a <= int(e['time'][:4]) < b_]
        Bm = [sub.get(id(e), e['mw'] if e['mw'] is not None else e['mag']) for e in cat if a <= int(e['time'][:4]) < b_]
        for lab, m in (('A_mevcut', A), ('B_refMw', Bm)):
            mc = mc_maxc(m); bb, sb, n = aki(m, mc) if mc else (None, None, 0)
            mc45 = aki(m, 4.5)
            res_b[f'{per}|{lab}'] = {'N': len(m), 'Mc_maxc': mc, 'b_Mc': bb and round(bb, 3), 'sb': sb and round(sb, 3), 'N_ge_Mc': n,
                                    'b_M4.5': mc45[0] and round(mc45[0], 3), 'sb_M4.5': mc45[1] and round(mc45[1], 3), 'N_ge_4.5': mc45[2]}
    rep = {'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'n_catalog': len(cat), 'n_cat_ge4': len(big),
           'n_comcat': len(cc), 'n_comcat_mw': sum(1 for e in cc if e['mtype'].startswith('mw')), 'n_iscgem': len(ig), 'n_pairs': len(P),
           'match_rate': {f'{k[0]}|{k[1]}': {'N': v[0], 'eslesen': v[1], 'oran': round(v[1] / v[0], 3) if v[0] else None} for k, v in sorted(tab.items())},
           'dM_by_type': {k: st(v) for k, v in sorted(dM.items(), key=lambda x: -len(x[1]))},
           'scordilis_minus_ref': {k: st(v) for k, v in dS.items()}, 'bvalue': res_b, 'log': LOG}
    json.dump(rep, open(f'{OUT}/faz0_rapor.json', 'w'), ensure_ascii=False, indent=1)
    json.dump([{'cat_id': e['id'], 'cat_time': e['time'], 'cat_src': e['src'], 'cat_mag': e['mag'], 'cat_mtype': e['mtype'], 'cat_mw': e.get('mw'), 'cat_mw_method': e.get('mw_method'),
                'ref_id': r['id'], 'ref_src': r['src'], 'ref_mw': r['mag'], 'ref_mtype': r['mtype'], 'dt_s': round(abs(r['_t'] - e['_t']), 1), 'dr_km': round(d, 1)} for e, r, d in P],
              open(f'{OUT}/eslesmeler.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    log('Bitti.')

if __name__ == '__main__':
    main()
