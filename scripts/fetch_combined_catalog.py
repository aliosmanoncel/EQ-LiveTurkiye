"""
fetch_combined_catalog.py
ISC (1900-1997) + EMSC (1998-bugun) birlestirme
Scordilis (2006) Mw homojenizasyonu uygulanir.
Cikti: data/eq_historical.json

Kullanim:
  python scripts/fetch_combined_catalog.py
"""

import json, sys, time, urllib.request
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ISC_URL  = 'http://www.isc.ac.uk/fdsnws/event/1/query'
EMSC_URL = 'https://www.seismicportal.eu/fdsnws/event/1/query'
BOUNDS   = dict(minlat=33.0, maxlat=45.0, minlon=23.0, maxlon=48.0)
MINMAG   = 4.5
LIMIT    = 20000
OUTPUT   = 'data/eq_historical.json'

# ── Scordilis (2006) Mw donusumu ─────────────────────────────────────
def to_mw(mag, mtype):
    mt = (mtype or '').lower().strip()
    if mt in ('mw','mww','mwb','mwc','mwr','mwp',''):
        return round(mag, 2)
    if mt == 'mb' and 3.5 <= mag <= 6.2:
        return round(0.85*mag + 1.03, 2)
    if mt in ('ml','md','mc') and 1.0 <= mag <= 6.5:
        return round(0.0376*mag**2 + 0.646*mag - 0.269, 2)
    if mt in ('ms','ms_20'):
        if 3.0 <= mag <= 6.1: return round(0.646*mag + 2.079, 2)
        if mag > 6.1:          return round(0.994*mag + 0.115, 2)
    return round(mag, 2)

def parse_line(line, source):
    c = [x.strip() for x in line.split('|')]
    if len(c) < 11: return None
    try:
        mag   = float(c[10])
        mtype = c[9]
        return {
            'id'    : c[0],
            'time'  : c[1],
            'lat'   : float(c[2]),
            'lon'   : float(c[3]),
            'dep'   : float(c[4]) if c[4] else 10.0,
            'mag'   : mag,
            'mtype' : mtype,
            'mw'    : to_mw(mag, mtype),
            'place' : c[12] if len(c) > 12 else '',
            'src'   : source,
        }
    except (ValueError, IndexError):
        return None

def fetch_chunk(base_url, start, end, source, delay=1.5):
    params = (f"?format=text&starttime={start}&endtime={end}"
              f"&minlat={BOUNDS['minlat']}&maxlat={BOUNDS['maxlat']}"
              f"&minlon={BOUNDS['minlon']}&maxlon={BOUNDS['maxlon']}"
              f"&minmagnitude={MINMAG}&limit={LIMIT}&orderby=time-asc")
    url = base_url + params
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='replace')
        lines = [l for l in resp.splitlines() if l.strip() and '|' in l and not l.startswith('#')]
        evs   = [e for e in (parse_line(l, source) for l in lines) if e]
        time.sleep(delay)
        return evs
    except Exception as ex:
        print(f'    HATA ({source} {start}): {ex}')
        time.sleep(delay * 2)
        return []

def fetch_period(base_url, start_year, end_year, source, chunk=5):
    """Yillara bolunmus dilimler halinde ceker."""
    all_evs = {}
    cur = start_year
    while cur < end_year:
        nxt = min(cur + chunk, end_year)
        s, e = f'{cur}-01-01', f'{nxt}-01-01'
        evs  = fetch_chunk(base_url, s, e, source)
        for ev in evs:
            all_evs[ev['id']] = ev
        print(f'  {s} → {e}: {len(evs)} olay ({len(all_evs)} toplam)')
        cur = nxt
    return all_evs

def dedup(evs_dict, tol_sec=60, tol_km=50):
    """Zaman + konum toleransiyla tekrar eden olaylari kaldir."""
    import math
    def hav(la1, lo1, la2, lo2):
        R = 6371; r = math.pi/180
        dl = (la2-la1)*r; dlo = (lo2-lo1)*r
        a = math.sin(dl/2)**2 + math.cos(la1*r)*math.cos(la2*r)*math.sin(dlo/2)**2
        return R*2*math.atan2(math.sqrt(a), math.sqrt(1-a))

    events = sorted(evs_dict.values(), key=lambda e: e['time'])
    kept = []
    for ev in events:
        t = ev['time']
        duplicate = False
        for k in kept[-30:]:  # son 30 olayla karsilastir
            def parse_t(s):
                from datetime import timezone as tz
                dt_obj = datetime.fromisoformat(s.replace('Z', '').replace(' ', 'T').split('.')[0])
                return dt_obj.replace(tzinfo=None)
            dt = abs((parse_t(t) - parse_t(k['time'])).total_seconds())
            if dt > tol_sec: continue
            dk = hav(ev['lat'], ev['lon'], k['lat'], k['lon'])
            if dk < tol_km:
                duplicate = True
                # Mw buyuk olani tut
                if ev['mw'] > k['mw']:
                    kept.remove(k)
                    kept.append(ev)
                break
        if not duplicate:
            kept.append(ev)
    return kept

def main():
    now = datetime.now(timezone.utc)
    today = now.strftime('%Y-%m-%d')

    # ── 1. ISC: 1900-1997 ────────────────────────────────────────────
    print('\n=== ISC: 1900-1997 ===')
    isc_evs = fetch_period(ISC_URL, 1900, 1998, 'ISC', chunk=10)
    print(f'ISC toplam: {len(isc_evs)} olay')

    # ── 2. EMSC: 1998-bugun ─────────────────────────────────────────
    print('\n=== EMSC: 1998-bugun ===')
    emsc_evs = fetch_period(EMSC_URL, 1998, now.year + 1, 'EMSC', chunk=5)
    print(f'EMSC toplam: {len(emsc_evs)} olay')

    # ── 3. Birlestir + tekrar kaldir ────────────────────────────────
    print('\n=== Birlestirme + tekrar temizleme ===')
    merged = {**isc_evs, **emsc_evs}  # ID cakismasinda EMSC kazanir
    print(f'Ham birlestirme: {len(merged)} olay')
    cleaned = dedup(merged)
    cleaned.sort(key=lambda e: e['time'], reverse=True)
    print(f'Tekrar sonrasi: {len(cleaned)} olay')

    # Mtype dagilimi
    from collections import Counter
    ct = Counter(e['mtype'] for e in cleaned)
    print('Mtype:', ct.most_common(8))

    # Mw istatistik
    mws = [e['mw'] for e in cleaned]
    print(f'Mw aralik: {min(mws):.1f} – {max(mws):.1f}  |  Ort: {sum(mws)/len(mws):.2f}')

    out = {
        'generated' : now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'    : 'ISC (1900-1997) + EMSC (1998-bugun) | Scordilis (2006) Mw',
        'starttime' : '1900-01-01',
        'endtime'   : today,
        'minmag'    : MINMAG,
        'bounds'    : BOUNDS,
        'count'     : len(cleaned),
        'events'    : cleaned,
    }
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'\n[OK] Kaydedildi: {OUTPUT} ({len(cleaned)} olay)')

if __name__ == '__main__':
    main()
