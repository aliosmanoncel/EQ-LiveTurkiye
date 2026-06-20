"""
eq_fetch_turkey.py
Türkiye sınırları içindeki son depremleri EMSC FDSN'den çeker,
data/turkey_eq.json olarak kaydeder.

Kullanım:
  python scripts/eq_fetch_turkey.py            # son 7 günü çeker
  python scripts/eq_fetch_turkey.py --hours 48 # son 48 saati çeker
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

# Windows encoding fix
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Ayarlar ──────────────────────────────────────────────────────────
CFG = {
    'emsc_url'  : 'https://www.seismicportal.eu/fdsnws/event/1/query',
    'minlat'    : 33.0,
    'maxlat'    : 45.0,
    'minlon'    : 23.0,
    'maxlon'    : 48.0,
    'minmag'    : 1.0,
    'limit'     : 2000,
    'hours'     : 168,   # varsayılan: 7 gün
    'output'    : 'data/turkey_eq.json',
}

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'[{ts}] {msg}')

def parse_hours():
    for i, arg in enumerate(sys.argv):
        if arg == '--hours' and i + 1 < len(sys.argv):
            return int(sys.argv[i + 1])
    return CFG['hours']

# ── EMSC'den veri çek (format=text, pipe-separated) ──────────────────
def fetch_emsc(hours):
    now_utc   = datetime.now(timezone.utc)
    start_utc = now_utc - timedelta(hours=hours)
    fmt = lambda d: d.strftime('%Y-%m-%dT%H:%M:%S')

    params = (
        f"?format=text"
        f"&starttime={fmt(start_utc)}"
        f"&endtime={fmt(now_utc)}"
        f"&minlat={CFG['minlat']}"
        f"&maxlat={CFG['maxlat']}"
        f"&minlon={CFG['minlon']}"
        f"&maxlon={CFG['maxlon']}"
        f"&minmagnitude={CFG['minmag']}"
        f"&limit={CFG['limit']}"
        f"&orderby=time"
    )
    url = CFG['emsc_url'] + params
    log(f'EMSC sorgusu: {url[:90]}…')

    req  = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')
    lines = [l for l in resp.splitlines() if l.strip() and '|' in l and not l.startswith('#')]
    log(f'EMSC: {len(lines)} satır alındı')
    return lines

# ── Pipe-separated text → dict ───────────────────────────────────────
# Sütunlar: EventID|Time|Lat|Lon|Depth|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|MagAuthor|EventLocationName
def parse_line(line):
    c = [x.strip() for x in line.split('|')]
    if len(c) < 11:
        return None
    try:
        return {
            'id'   : c[0],
            'time' : c[1],
            'lat'  : float(c[2]),
            'lon'  : float(c[3]),
            'dep'  : float(c[4]) if c[4] else 0.0,
            'mag'  : float(c[10]),
            'mtype': c[9],
            'place': c[12] if len(c) > 12 else '',
        }
    except (ValueError, IndexError):
        return None

# ── Ana akış ─────────────────────────────────────────────────────────
def main():
    hours = parse_hours()
    log(f'Son {hours} saatin Türkiye depremleri çekiliyor…')

    lines  = fetch_emsc(hours)
    events = [e for e in (parse_line(l) for l in lines) if e]
    log(f'Ayrıştırıldı: {len(events)} deprem')

    out = {
        'generated' : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'    : 'EMSC SeismicPortal FDSN',
        'hours'     : hours,
        'count'     : len(events),
        'events'    : events,
    }

    with open(CFG['output'], 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    log(f'Kaydedildi: {CFG["output"]} ({len(events)} olay)')

if __name__ == '__main__':
    main()
