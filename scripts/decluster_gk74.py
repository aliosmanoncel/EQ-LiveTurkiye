"""
decluster_gk74.py
Gardner-Knopoff (1974) declustering.

Her buyuk olay (mainshock) etrafinda:
  - Zaman penceresi T(M) gun
  - Mesafe penceresi D(M) km
icindeki kucuk olaylar "aftershock/foreshock" olarak isaretlenir.

Referans:
  Gardner & Knopoff (1974) BSSA 64(5): 1363-1367
"""

import json, math, sys
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INPUT  = 'data/eq_marmara_catalog.json'
OUTPUT = 'data/eq_marmara_declustered.json'


def gk_window(m):
    """Gardner-Knopoff (1974) Tablo 1 penceresi."""
    if m >= 6.5:
        T_days = 10 ** (0.032 * m + 2.7389)
    else:
        T_days = 10 ** (0.5409 * m - 0.547)
    D_km = 10 ** (0.1238 * m + 0.983)
    return T_days, D_km


def haversine(la1, lo1, la2, lo2):
    R = 6371.0; r = math.pi / 180
    dl = (la2 - la1) * r; dlo = (lo2 - lo1) * r
    a = math.sin(dl/2)**2 + math.cos(la1*r) * math.cos(la2*r) * math.sin(dlo/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_time(s):
    """ISO zamanini saniyeye cevir."""
    s = s.replace(' ', 'T')[:19]
    try:
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S').timestamp()
    except:
        return datetime.strptime(s[:10], '%Y-%m-%d').timestamp()


def main():
    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)

    events = data['events']
    # Zamana gore sirala
    events.sort(key=lambda e: e.get('time', ''))
    n = len(events)
    print(f'[*] {n} olay yuklendi')

    # Zaman (float saniye) ve is_cluster bayraklari
    times = [parse_time(e['time']) for e in events]
    mags  = [e.get('mag', 0) for e in events]
    lats  = [e.get('lat', 0) for e in events]
    lons  = [e.get('lon', 0) for e in events]
    cluster = [False] * n

    for i in range(n):
        if cluster[i]:
            continue  # zaten artci, mainshock degil
        m = mags[i]
        T_days, D_km = gk_window(m)
        T_sec = T_days * 86400
        t0 = times[i]

        for j in range(i + 1, n):
            if times[j] - t0 > T_sec:
                break  # zaman sirali, kalan hepsi disinda
            if cluster[j]:
                continue
            if mags[j] >= m:
                continue  # buyuk olay artci sayilmaz
            dist = haversine(lats[i], lons[i], lats[j], lons[j])
            if dist <= D_km:
                cluster[j] = True

    main_events = [e for e, c in zip(events, cluster) if not c]
    removed     = sum(cluster)

    print(f'[*] Mainshock: {len(main_events)} | Artci/onsici: {removed} ({100*removed//n}%)')

    # Yillara gore karsilastirma
    from collections import defaultdict
    by_year_all  = defaultdict(int)
    by_year_main = defaultdict(int)
    for e, c in zip(events, cluster):
        yr = int(e['time'][:4])
        by_year_all[yr]  += 1
        if not c:
            by_year_main[yr] += 1
    for yr in sorted(by_year_all):
        print(f'  {yr}: {by_year_all[yr]:5d} → {by_year_main[yr]:5d}')

    out = {
        'generated'   : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'      : data['source'] + ' | Declustered: Gardner-Knopoff (1974)',
        'original_n'  : n,
        'main_n'      : len(main_events),
        'removed_n'   : removed,
        'count'       : len(main_events),
        'events'      : main_events,
    }
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'[OK] Kaydedildi: {OUTPUT}')


if __name__ == '__main__':
    main()
