"""
fetch_historical.py
USGS FDSN'den Turkiye icin uzun donemli (1970-bugun) M>=4.5 katalog ceker.
Veri: eq_historical.json — hazard grid icin kullanilir.

Kullanim:
  python scripts/fetch_historical.py
  python scripts/fetch_historical.py --starttime 1970-01-01 --minmag 4.5
"""

import json, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

USGS_URL = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
BOUNDS   = dict(minlat=33.0, maxlat=45.0, minlon=23.0, maxlon=48.0)
LIMIT    = 20000  # USGS max

def parse_args():
    args = sys.argv[1:]
    def get(flag, default):
        return args[args.index(flag)+1] if flag in args else default
    return get('--starttime','1970-01-01'), float(get('--minmag','4.5')), get('--output','data/eq_historical.json')

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

def parse_line(line):
    c = [x.strip() for x in line.split('|')]
    if len(c) < 11: return None
    try:
        mag   = float(c[10])
        mtype = c[9]
        return {
            'id'   : c[0],
            'time' : c[1],
            'lat'  : float(c[2]),
            'lon'  : float(c[3]),
            'dep'  : float(c[4]) if c[4] else 10.0,
            'mag'  : mag,
            'mtype': mtype,
            'mw'   : to_mw(mag, mtype),
            'place': c[12] if len(c) > 12 else '',
        }
    except (ValueError, IndexError):
        return None

def fetch_chunk(starttime, endtime, minmag):
    params = (f"?format=text&starttime={starttime}&endtime={endtime}"
              f"&minlat={BOUNDS['minlat']}&maxlat={BOUNDS['maxlat']}"
              f"&minlon={BOUNDS['minlon']}&maxlon={BOUNDS['maxlon']}"
              f"&minmagnitude={minmag}&limit={LIMIT}&orderby=time-asc")
    url = USGS_URL + params
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=60).read().decode('utf-8')
    return [l for l in resp.splitlines() if l.strip() and '|' in l and not l.startswith('#')]

def main():
    starttime, minmag, output = parse_args()
    endtime = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    print(f'[*] USGS FDSN: {starttime} → {endtime}, M>={minmag}, Turkiye sinirları')

    # 10 yıllık dilimler halinde çek (USGS limit aşımını önler)
    all_events = {}
    start_dt = datetime.strptime(starttime, '%Y-%m-%d')
    end_dt   = datetime.strptime(endtime,   '%Y-%m-%d')
    chunk_years = 10

    cur = start_dt
    while cur < end_dt:
        nxt = min(cur.replace(year=cur.year + chunk_years), end_dt)
        s = cur.strftime('%Y-%m-%d')
        e = nxt.strftime('%Y-%m-%d')
        print(f'  Dilim: {s} → {e}', end=' ... ')
        try:
            lines = fetch_chunk(s, e, minmag)
            evs   = [ev for ev in (parse_line(l) for l in lines) if ev]
            for ev in evs:
                all_events[ev['id']] = ev  # tekrar önleme
            print(f'{len(evs)} olay ({len(all_events)} toplam)')
        except Exception as ex:
            print(f'HATA: {ex}')
        time.sleep(1)  # USGS rate limit
        cur = nxt

    events = list(all_events.values())
    events.sort(key=lambda e: e['time'], reverse=True)
    print(f'[*] Toplam: {len(events)} benzersiz deprem')

    out = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'   : 'USGS FDSN (EarthScope/ComCat)',
        'starttime': starttime,
        'endtime'  : endtime,
        'minmag'   : minmag,
        'bounds'   : BOUNDS,
        'count'    : len(events),
        'events'   : events,
    }
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',',':'))
    print(f'[✓] Kaydedildi: {output} ({len(events)} olay)')

if __name__ == '__main__':
    main()
