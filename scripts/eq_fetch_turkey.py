"""
eq_fetch_turkey.py
Türkiye sismisitesini EMSC, AFAD veya KOERI'den çeker.

Kullanım:
  python scripts/eq_fetch_turkey.py --hours 24 --minmag 1.0 --output data/eq_daily.json
  python scripts/eq_fetch_turkey.py --hours 24 --minmag 1.0 --output data/eq_daily_afad.json --source afad
  python scripts/eq_fetch_turkey.py --hours 24 --minmag 1.0 --output data/eq_daily_koeri.json --source koeri
"""

import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Sabitler ─────────────────────────────────────────────────────────
SOURCES = {
    'emsc' : 'https://www.seismicportal.eu/fdsnws/event/1/query',
    'usgs' : 'https://earthquake.usgs.gov/fdsnws/event/1/query',
    'koeri': 'http://eida.koeri.boun.edu.tr/fdsnws/event/1/query',
    'afad' : 'https://deprem.afad.gov.tr/apiv2/event/filter',
}

# Sorgu sınırları: AFAD/KOERI → Türkiye, EMSC → Akdeniz havzası, USGS → küresel
GLOBAL_BOUNDS = dict(minlat=-90.0, maxlat=90.0,  minlon=-180.0, maxlon=180.0)
EMSC_BOUNDS   = dict(minlat=10.0,  maxlat=75.0,  minlon=-45.0,  maxlon=120.0)
TR_BOUNDS     = dict(minlat=34.0,  maxlat=43.0,  minlon=25.0,   maxlon=46.0)

LIMIT = 2000

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'[{ts}] {msg}')

def parse_args():
    hours  = 168
    minmag = 1.5
    output = 'data/eq_recent.json'
    source = 'emsc'
    for i, arg in enumerate(sys.argv):
        if arg == '--hours'  and i+1 < len(sys.argv): hours  = int(sys.argv[i+1])
        if arg == '--minmag' and i+1 < len(sys.argv): minmag = float(sys.argv[i+1])
        if arg == '--output' and i+1 < len(sys.argv): output = sys.argv[i+1]
        if arg == '--source' and i+1 < len(sys.argv): source = sys.argv[i+1].lower()
    return hours, minmag, output, source

# ── Scordilis (2006) büyüklük homojenleştirme → Mw ──────────────────
def to_mw(mag, mag_type):
    mt = (mag_type or '').lower().strip()
    if mt in ('mw', 'mww', 'mwb', 'mwc', 'mwr', 'mwp', ''):
        return round(mag, 2)
    if mt == 'mb':
        if 3.5 <= mag <= 6.2:
            return round(0.85 * mag + 1.03, 2)
    if mt in ('ml', 'md', 'mc'):
        if 1.0 <= mag <= 6.5:
            return round(0.0376 * mag**2 + 0.646 * mag - 0.269, 2)
    if mt in ('ms', 'ms_20'):
        if 3.0 <= mag <= 6.1:
            return round(0.646 * mag + 2.079, 2)
        elif mag > 6.1:
            return round(0.994 * mag + 0.115, 2)
    return round(mag, 2)

# ── EMSC / KOERI (standart FDSN text) ────────────────────────────────
def fetch_fdsn_text(source, hours, minmag):
    base = SOURCES[source]
    if source == 'usgs':
        bnd = GLOBAL_BOUNDS
    elif source == 'emsc':
        bnd = EMSC_BOUNDS
    else:
        bnd = TR_BOUNDS
    now  = datetime.now(timezone.utc)
    t0   = now - timedelta(hours=hours)
    fmt  = lambda d: d.strftime('%Y-%m-%dT%H:%M:%S')

    params = (
        f"?format=text&starttime={fmt(t0)}&endtime={fmt(now)}"
        f"&minlat={bnd['minlat']}&maxlat={bnd['maxlat']}"
        f"&minlon={bnd['minlon']}&maxlon={bnd['maxlon']}"
        f"&minmagnitude={minmag}&limit={LIMIT}&orderby=time"
    )
    url = base + params
    log(f'{source.upper()} sorgusu: {url[:100]}…')
    req  = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')
    lines = [l for l in resp.splitlines() if l.strip() and '|' in l and not l.startswith('#')]
    log(f'{source.upper()}: {len(lines)} satır')
    return lines

def parse_fdsn_line(line):
    c = [x.strip() for x in line.split('|')]
    if len(c) < 11:
        return None
    try:
        mag   = float(c[10])
        mtype = c[9]
        return {
            'id'   : c[0],
            'time' : c[1],
            'lat'  : float(c[2]),
            'lon'  : float(c[3]),
            'dep'  : float(c[4]) if c[4] else 0.0,
            'mag'  : mag,
            'mtype': mtype,
            'mw'   : to_mw(mag, mtype),
            'place': c[12] if len(c) > 12 else '',
        }
    except (ValueError, IndexError):
        return None

# ── AFAD (özel JSON API) ──────────────────────────────────────────────
def fetch_afad(hours, minmag):
    now  = datetime.now(timezone.utc)
    t0   = now - timedelta(hours=hours)
    fmt  = lambda d: d.strftime('%Y-%m-%dT%H:%M:%S')

    params = (
        f"?start={fmt(t0)}&end={fmt(now)}"
        f"&minlat={TR_BOUNDS['minlat']}&maxlat={TR_BOUNDS['maxlat']}"
        f"&minlon={TR_BOUNDS['minlon']}&maxlon={TR_BOUNDS['maxlon']}"
        f"&minmag={minmag}&format=json&limit={LIMIT}"
    )
    url = SOURCES['afad'] + params
    log(f'AFAD sorgusu: {url[:100]}…')
    req  = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')
    raw  = json.loads(resp)
    log(f'AFAD: {len(raw)} olay')
    return raw

def parse_afad_event(e):
    try:
        mag   = float(e['magnitude'])
        mtype = e.get('type', 'ML')
        return {
            'id'      : str(e.get('eventID', '')),
            'time'    : e.get('date', ''),
            'lat'     : float(e['latitude']),
            'lon'     : float(e['longitude']),
            'dep'     : float(e.get('depth', 0)),
            'mag'     : mag,
            'mtype'   : mtype,
            'mw'      : to_mw(mag, mtype),
            'place'   : e.get('location', ''),
            'province': e.get('province', ''),
            'district': e.get('district', ''),
        }
    except (ValueError, KeyError, TypeError):
        return None

# ── Ana akış ─────────────────────────────────────────────────────────
def main():
    hours, minmag, output, source = parse_args()
    log(f'Kaynak: {source.upper()} | Son {hours} saat | M>={minmag} → {output}')

    if source == 'afad':
        raw    = fetch_afad(hours, minmag)
        events = [e for e in (parse_afad_event(r) for r in raw) if e]
        src_label = 'AFAD TDVMS REST API'
    elif source in ('emsc', 'usgs', 'koeri'):
        lines  = fetch_fdsn_text(source, hours, minmag)
        events = [e for e in (parse_fdsn_line(l) for l in lines) if e]
        src_label = {'emsc': 'EMSC SeismicPortal FDSN', 'usgs': 'USGS FDSN', 'koeri': 'KOERI EIDA FDSN'}[source]
    else:
        log(f'Bilinmeyen kaynak: {source}. Desteklenenler: emsc, afad, koeri')
        sys.exit(1)

    log(f'Ayrıştırıldı: {len(events)} deprem')

    out = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'   : src_label,
        'hours'    : hours,
        'minmag'   : minmag,
        'count'    : len(events),
        'events'   : events,
    }

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    log(f'Kaydedildi: {output} ({len(events)} olay)')

if __name__ == '__main__':
    main()
