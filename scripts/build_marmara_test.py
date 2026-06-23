"""
build_marmara_test.py
Marmara prospektif forecast test olaylarini JSON'a yazar.

Egitim: 2016-2025 (son 10 yil, declustered katalog)
Test  : 2026-06-23 - 2030-06-23  M>=5.0  (prospektif — gelecekte dolacak)

GitHub Actions her saat calistiginda bu script de calisip
yeni M>=5 olaylari varsa ekler.
"""

import json
from datetime import datetime, timezone

INPUT_CAT       = 'data/eq_marmara_catalog.json'
OUTPUT          = 'data/forecast_marmara_test_events.json'

TEST_START_DATE = '2026-06-23'
TEST_END_DATE   = '2030-06-23'
TEST_MINMAG     = 5.0

BOUNDS = dict(minlat=39.5, maxlat=41.5, minlon=26.0, maxlon=32.0)


def main():
    # Guncel katalog dosyalarindan M>=5 test olaylari topla
    catalog_files = [
        'data/eq_month.json',
        'data/eq_month_afad.json',
        'data/eq_annual.json',
        'data/eq_annual_usgs.json',
        INPUT_CAT,
    ]

    all_ev = {}  # duplikat onlemek icin key=time+lat+lon
    for path in catalog_files:
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            for e in data.get('events', []):
                mag = e.get('mag', 0) or e.get('mw', 0)
                if float(mag) < TEST_MINMAG:
                    continue
                t = e.get('time', '')
                if not t or not (TEST_START_DATE <= t[:10] <= TEST_END_DATE):
                    continue
                lat = e.get('lat', 0)
                lon = e.get('lon', 0)
                if not (BOUNDS['minlat'] <= lat <= BOUNDS['maxlat'] and
                        BOUNDS['minlon'] <= lon <= BOUNDS['maxlon']):
                    continue
                mw  = e.get('mw') or mag
                key = f"{t[:13]}_{round(lat,1)}_{round(lon,1)}"
                if key not in all_ev:
                    all_ev[key] = {
                        'time' : t,
                        'lat'  : lat,
                        'lon'  : lon,
                        'mag'  : round(float(mag), 1),
                        'mw'   : round(float(mw), 1),
                        'dep'  : e.get('dep', 0),
                        'place': e.get('place', ''),
                        'src'  : e.get('src', ''),
                    }
        except FileNotFoundError:
            pass

    events = sorted(all_ev.values(), key=lambda x: x['mw'], reverse=True)

    print(f'Marmara prospektif test {TEST_START_DATE} - {TEST_END_DATE} M>={TEST_MINMAG}: {len(events)} olay')
    if events:
        for ev in events[:5]:
            print(f"  Mw{ev['mw']} {ev['time'][:10]} {ev['place']}")
    else:
        print('  Henuz test olayi yok — prospektif pencere acik')

    out = {
        'generated'  : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'description': (f'Marmara prospektif forecast: egitim 2016-2025 (son 10 yil) | '
                        f'test {TEST_START_DATE} - {TEST_END_DATE} M>={TEST_MINMAG}'),
        'train_period': [2016, 2025],
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
