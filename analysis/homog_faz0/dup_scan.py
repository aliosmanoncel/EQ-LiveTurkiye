"""Faz 0: mevcut eq_historical.json içinde kalan olası tekrarları tarar (kataloğu DEĞİŞTİRMEZ).
Eşikler: (a) EQ-Live mevcut kuralı 60 s / 50 km; (b) Candia & Macedo (2026) Tablo 2 dönem eşikleri (ΔM, ΔR km, ΔT dk)."""
import json, math, sys, collections
from datetime import datetime
j = json.load(open(sys.argv[1])); ev = j['events']
def t(e): return datetime.fromisoformat(e['time'].replace('Z','').split('.')[0]).timestamp()
def hav(a, b):
    r = math.pi/180; dl=(b['lat']-a['lat'])*r; do=(b['lon']-a['lon'])*r
    x = math.sin(dl/2)**2 + math.cos(a['lat']*r)*math.cos(b['lat']*r)*math.sin(do/2)**2
    return 6371*2*math.atan2(math.sqrt(x), math.sqrt(1-x))
CM = [(-1e9, 1900, 1.75, None, 1440), (1900, 1940, 1.5, None, 200), (1940, 1963, 1.25, 200, 10), (1963, 1990, 1.0, 150, 2), (1990, 3000, 0.75, 100, 0.5)]
def thr(y):
    for a, b, dm, dr, dt in CM:
        if a <= y < b: return dm, dr, dt
for e in ev: e['_t'] = t(e); e['_y'] = int(e['time'][:4]); e['_m'] = e['mw'] if e['mw'] is not None else e['mag']
ev.sort(key=lambda e: e['_t'])
res = {'eqlive_60s_50km': [], 'candia2026': []}
for i, a in enumerate(ev):
    dm, dr, dtm = thr(a['_y'])
    for b in ev[i+1:]:
        dt = b['_t'] - a['_t']
        if dt > max(60, dtm*60): break
        d = hav(a, b); dmag = abs(a['_m'] - b['_m'])
        if dt <= 60 and d < 50: res['eqlive_60s_50km'].append((a, b, dt, d, dmag))
        if dt <= dtm*60 and (dr is None or d <= dr) and dmag <= dm: res['candia2026'].append((a, b, dt, d, dmag))
for k, L in res.items():
    c = collections.Counter((p[0]['src'] + '-' + p[1]['src'], (p[0]['_y']//10)*10) for p in L)
    print(f'\n## {k}: {len(L)} aday çift'); print(' kaynak/onyıl:', sorted(c.items())[:20])
    if L:
        dms = sorted(p[4] for p in L); print(' ΔM ortanca %.2f, %%90 %.2f' % (dms[len(dms)//2], dms[int(.9*len(dms))]))
        for p in L[:8]: print('  ', p[0]['time'][:19], p[0]['src'], p[0]['mtype'], p[0]['mag'], '|', p[1]['time'][:19], p[1]['src'], p[1]['mtype'], p[1]['mag'], '| Δt=%.0fs Δr=%.0fkm' % (p[2], p[3]))
json.dump({k: [{'a': p[0]['id'], 'b': p[1]['id'], 'ta': p[0]['time'], 'tb': p[1]['time'], 'src': p[0]['src']+'-'+p[1]['src'], 'ma': p[0]['mag'], 'mta': p[0]['mtype'], 'mb': p[1]['mag'], 'mtb': p[1]['mtype'], 'dt_s': round(p[2],1), 'dr_km': round(p[3],1), 'dM': round(p[4],2)} for p in L] for k, L in res.items()}, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
