"""
Faz 1b — 1963 öncesi tamlık incelemesi (homojenizasyondan AYRI; ana koda ve kataloglara dokunmaz).

Sınanan olasılıklar, her ISC-GEM olayı için (kutu 33–45° K, 23–48° D; 1904–1962; ana katalog):
  A. Eşleşme sorunu: EQ-Live'da olay VAR ama Tablo 2 eşiklerinin dışında (±1 gün, ≤ 400 km içinde en yakın aday aranır).
  B. Kaynak/filtre sorunu: ISC FDSN aynı olayı döndürüyor mu (±5 dk, ±3°)?
       B1 büyüklük süzgeci olmadan, B2 EQ-Live'ın kullandığı minmagnitude=5.5 ile.
     B1 var, B2 yok → olay ISC'de var ama ISC'nin tercih ettiği büyüklük < 5,5 ya da büyüklük yok (süzgeç etkisi).
     B1 yok → olay ISC FDSN'de yok (kaynak kapsamı).
  C. Eşik duyarlılığı: 1940 öncesi ΔR üst sınırı 100/150/250/400 km için eşleşme oranı.
Kullanım: python analysis/homog_faz1b/tamlik_1963oncesi.py [--no-net]
"""
import bisect, collections, json, math, sys, time, urllib.request
from datetime import datetime, timezone, timedelta
OUT = 'analysis/homog_faz1b/out'
ISC = 'http://www.isc.ac.uk/fdsnws/event/1/query'
def ts(s): return datetime.fromisoformat(s.replace('Z', '').replace(' ', 'T').split('.')[0]).replace(tzinfo=timezone.utc).timestamp()
def hav(a, b):
    r = math.pi / 180; dl = (b[0] - a[0]) * r; do = (b[1] - a[1]) * r
    x = math.sin(dl / 2) ** 2 + math.cos(a[0] * r) * math.cos(b[0] * r) * math.sin(do / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))
def mcls(m): return '5.0-5.5' if m < 5.5 else '5.5-6.0' if m < 6 else '>=6.0'
def per(y): return '1904-1939' if y < 1940 else '1940-1962'
def thr(y): return (200, None) if y < 1940 else (10, 200)          # Tablo 2: ΔT dk, ΔR km (1940 öncesi ΔR tanımsız)
def isc_query(t, lat, lon, minmag=None):
    t0 = (datetime.fromtimestamp(t, timezone.utc) - timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')
    t1 = (datetime.fromtimestamp(t, timezone.utc) + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')
    u = (f'{ISC}?format=text&starttime={t0}&endtime={t1}&minlat={lat-3:.2f}&maxlat={lat+3:.2f}&minlon={lon-3:.2f}&maxlon={lon+3:.2f}'
         + (f'&minmagnitude={minmag}' if minmag else ''))
    for k in range(3):
        try:
            txt = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'EQ-LiveTurkiye homog-faz1b'}), timeout=60).read().decode('utf-8', 'replace')
            rows = [l.split('|') for l in txt.splitlines() if '|' in l and not l.startswith('#')]
            return [{'id': r[0].strip(), 'time': r[1].strip(), 'lat': float(r[2]), 'lon': float(r[3]), 'author': r[5].strip(), 'mtype': r[9].strip() if len(r) > 9 else '',
                     'mag': float(r[10]) if len(r) > 10 and r[10].strip() else None, 'magauthor': r[11].strip() if len(r) > 11 else ''} for r in rows], u
        except urllib.error.HTTPError as e:
            if e.code == 204: return [], u
            time.sleep(5 * (k + 1)); err = e
        except Exception as e:
            time.sleep(5 * (k + 1)); err = e
    return None, f'{u} HATA {err}'
def main():
    net = '--no-net' not in sys.argv
    gem = [g for g in json.load(open('analysis/homog_faz1/out/iscgem_v12.1_kutu.json')) if g['set'] == 'main' and int(g['date'][:4]) < 1963]
    for g in gem: g['_t'] = ts(g['date'])
    cat = [e for e in json.load(open('data/eq_historical.json'))['events'] if int(e['time'][:4]) < 1963]
    for e in cat: e['_t'] = ts(e['time'])
    cat.sort(key=lambda e: e['_t']); ct = [e['_t'] for e in cat]
    def cands(g, dt_s, dr):
        i0 = bisect.bisect_left(ct, g['_t'] - dt_s); out = []
        for e in cat[i0:]:
            if e['_t'] > g['_t'] + dt_s: break
            d = hav((g['lat'], g['lon']), (e['lat'], e['lon']))
            if dr is None or d <= dr: out.append((e, abs(e['_t'] - g['_t']), d))
        return out
    # C. eşik duyarlılığı
    sens = {}
    for drp in (100, 150, 250, 400):
        tab = collections.defaultdict(lambda: [0, 0])
        for g in gem:
            y = int(g['date'][:4]); dtm, dr = thr(y); dr = drp if dr is None else dr
            k = (per(y), mcls(g['mw'])); tab[k][0] += 1; tab[k][1] += bool(cands(g, dtm * 60, dr))
        sens[f'dR_pre1940={drp}km'] = {f'{a}|{b}': f'{v[1]}/{v[0]} ({100 * v[1] / v[0]:.0f}%)' for (a, b), v in sorted(tab.items())}
    # A/B olay bazında (250 km uyarlamasıyla eşleşmeyenler)
    rows = []
    for g in gem:
        y = int(g['date'][:4]); dtm, dr = thr(y); dr = 250 if dr is None else dr
        if cands(g, dtm * 60, dr): continue
        near = sorted(cands(g, 86400, 400), key=lambda z: z[1] / 3600 + z[2] / 100)
        rec = {'gem_id': g['eventid'], 'date': g['date'], 'lat': g['lat'], 'lon': g['lon'], 'mw': g['mw'], 's_mw': g['s_mw'], 'q_mw': g['q_mw'], 'per': per(y), 'cls': mcls(g['mw']),
               'A_nearest_eqlive': ({'id': near[0][0]['id'], 'time': near[0][0]['time'], 'mag': near[0][0]['mag'], 'mtype': near[0][0]['mtype'], 'dt_min': round(near[0][1] / 60, 1), 'dr_km': round(near[0][2])} if near else None)}
        if net:
            r1, u1 = isc_query(g['_t'], g['lat'], g['lon']); time.sleep(1.5)
            r2, u2 = isc_query(g['_t'], g['lat'], g['lon'], 5.5); time.sleep(1.5)
            rec['B1_isc_any'] = r1; rec['B2_isc_ge55'] = r2
            if r1 is None or r2 is None: rec['B'] = 'sorgu hatası'
            elif not r1: rec['B'] = 'ISC FDSN döndürmüyor (kaynak kapsamı)'
            elif not r2: rec['B'] = 'ISC var, M≥5,5 süzgecinde yok (büyüklük süzgeci)'
            else: rec['B'] = 'ISC M≥5,5 ile döndürüyor (EQ-Live çekiminde başka bir kayıp)'
        rows.append(rec)
    A_hit = sum(1 for r in rows if r['A_nearest_eqlive'] and r['A_nearest_eqlive']['dt_min'] <= 60 and r['A_nearest_eqlive']['dr_km'] <= 300)
    summ = {'n_iscgem_pre1963': len(gem), 'n_unmatched_250km': len(rows), 'A_eqlive_has_nearby_event(<=60dk,<=300km)': A_hit,
            'B_counts': dict(collections.Counter(r.get('B', 'ağ kapalı') for r in rows)),
            'B_by_class': {f'{a}|{b}': dict(collections.Counter(r.get('B', 'ağ kapalı') for r in rows if r['per'] == a and r['cls'] == b)) for a in ('1904-1939', '1940-1962') for b in ('5.0-5.5', '5.5-6.0', '>=6.0')},
            'sensitivity': sens}
    # örnek olaylar
    ex = [r for r in rows if r['date'].startswith(('1905-11-08', '1912-09-13'))]
    json.dump({'ozet': summ, 'ornekler': ex, 'olaylar': rows}, open(f'{OUT}/tamlik_1963oncesi.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
if __name__ == '__main__': main()
