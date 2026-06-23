"""
build_marmara_test.py
Marmara prospektif + retrospektif forecast test olaylari.

Egitim : 1998-2018 (GK74 declustered)
Test   : 2019-01-01 - 2030-06-23  M>=5.0
         Gecmis: 2019 M5.7, 2022 M6.1, 2025 M6.2 (retrospektif dogrulama)
         Gelecek: 2026-2030 (prospektif)
"""

import json, sys
from datetime import datetime, timezone
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUTPUT = 'data/forecast_marmara_test_events.json'

TEST_START_DATE = '2019-01-01'
TEST_END_DATE   = '2030-06-23'
TEST_MINMAG     = 5.0

BOUNDS = dict(minlat=39.5, maxlat=41.5, minlon=26.0, maxlon=32.0)

CATALOG_FILES = [
    'data/eq_marmara_catalog.json',
    'data/eq_month.json',
    'data/eq_month_afad.json',
    'data/eq_annual.json',
    'data/eq_annual_usgs.json',
]


def main():
    all_ev = {}
    for path in CATALOG_FILES:
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
            for e in d.get('events', []):
                mag = float(e.get('mag', 0) or e.get('mw', 0))
                if mag < TEST_MINMAG:
                    continue
                t = e.get('time', '')
                if not t or not (TEST_START_DATE <= t[:10] <= TEST_END_DATE):
                    continue
                lat, lon = e.get('lat', 0), e.get('lon', 0)
                if not (BOUNDS['minlat'] <= lat <= BOUNDS['maxlat'] and
                        BOUNDS['minlon'] <= lon <= BOUNDS['maxlon']):
                    continue
                mw  = float(e.get('mw') or mag)
                key = f"{t[:13]}_{round(lat,1)}_{round(lon,1)}"
                if key not in all_ev:
                    all_ev[key] = {
                        'time' : t,
                        'lat'  : lat,
                        'lon'  : lon,
                        'mag'  : round(mag, 1),
                        'mw'   : round(mw, 1),
                        'dep'  : e.get('dep', 0),
                        'place': e.get('place', ''),
                        'src'  : e.get('src', ''),
                    }
        except FileNotFoundError:
            pass

    events = sorted(all_ev.values(), key=lambda x: x['mw'], reverse=True)

    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    retro = [e for e in events if e['time'][:10] < today]
    prosp = [e for e in events if e['time'][:10] >= today]

    print(f'Test {TEST_START_DATE} - {TEST_END_DATE} M>={TEST_MINMAG}: {len(events)} olay')
    print(f'  Retrospektif (gecmis): {len(retro)}')
    for ev in retro:
        print(f"    Mw{ev['mw']} {ev['time'][:10]} {ev['place']}")
    print(f'  Prospektif (gelecek) : {len(prosp)}')

    out = {
        'generated'   : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'description' : (f'Marmara forecast: egitim 1998-2018 GK74 declustered | '
                         f'test {TEST_START_DATE}-{TEST_END_DATE} M>={TEST_MINMAG}'),
        'train_period': [1998, 2018],
        'test_start'  : TEST_START_DATE,
        'test_end'    : TEST_END_DATE,
        'min_mag'     : TEST_MINMAG,
        'bounds'      : BOUNDS,
        'count'       : len(events),
        'events'      : events,
    }
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'[OK] {OUTPUT}')


if __name__ == '__main__':
    main()
