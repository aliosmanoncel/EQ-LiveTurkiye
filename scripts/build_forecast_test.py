"""
build_forecast_test.py
Seismik öngörü doğrulama (prospective forecast test).

Yöntem:
  - Eğitim dönemi (1998-2019): bvalue_grid_train.json (önceden hesaplanmış)
  - Test dönemi   (2020-2026): EMSC katalogdan M>=5.0 olaylar → forecast_test_events.json
  - Görsel: bvalue_forecast.png üzerine test olayları bindirme

Çıktı:
  data/forecast_test_events.json   — test dönemi M>=5.0 olaylar (harita için)

Referans:
  Wiemer & Wyss (2002) Seismol. Res. Lett. — spatial b-value forecasting
  Öncel & Wyss (2000) — Fixed Area Method
"""

import json, sys, math
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INPUT_CAT  = 'data/eq_historical.json'
OUTPUT     = 'data/forecast_test_events.json'

TRAIN_END  = 2019   # eğitim dönemi sonu (dahil)
TEST_START = 2020   # test dönemi başlangıcı
TEST_END   = 2030
TEST_MINMAG = 5.0   # Yunnan çalışmasıyla aynı eşik

BOUNDS = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)


def main():
    with open(INPUT_CAT, encoding='utf-8') as f:
        data = json.load(f)

    # Test olaylarını filtrele
    test_events = []
    for e in data['events']:
        if e.get('src') != 'EMSC':
            continue
        mag = e.get('mag', 0)
        if mag < TEST_MINMAG:
            continue
        time_str = e.get('time', '')
        if not time_str:
            continue
        year = int(time_str[:4])
        if not (TEST_START <= year <= TEST_END):
            continue
        lat, lon = e.get('lat', 0), e.get('lon', 0)
        if not (BOUNDS['minlat'] <= lat <= BOUNDS['maxlat'] and
                BOUNDS['minlon'] <= lon <= BOUNDS['maxlon']):
            continue
        mw = e.get('mw') or mag
        test_events.append({
            'time': time_str,
            'lat' : lat,
            'lon' : lon,
            'mag' : round(mag, 1),
            'mw'  : round(mw, 1),
            'dep' : e.get('dep', 0),
            'place': e.get('place', ''),
        })

    # Mw'ye göre büyükten küçüğe sırala
    test_events.sort(key=lambda x: x['mw'], reverse=True)

    print(f'[*] Test dönemi {TEST_START}-{TEST_END} M≥{TEST_MINMAG}: {len(test_events)} olay')
    if test_events:
        print(f'    En büyük: Mw{test_events[0]["mw"]} — {test_events[0]["time"][:10]} {test_events[0]["place"]}')
        mags = [e['mw'] for e in test_events]
        for threshold in [5.0, 5.5, 6.0, 6.5, 7.0]:
            n = sum(1 for m in mags if m >= threshold)
            if n > 0:
                print(f'    M≥{threshold}: {n} olay')

    out = {
        'generated'   : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'description' : f'Forecast test olaylari: EMSC {TEST_START}-{TEST_END} M>={TEST_MINMAG}',
        'train_period': [1998, TRAIN_END],
        'test_period' : [TEST_START, TEST_END],
        'min_mag'     : TEST_MINMAG,
        'bounds'      : BOUNDS,
        'count'       : len(test_events),
        'events'      : test_events,
    }
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'[OK] Kaydedildi: {OUTPUT}')


if __name__ == '__main__':
    main()
