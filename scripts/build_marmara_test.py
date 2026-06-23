import json
from datetime import datetime, timezone

with open('data/eq_historical.json', encoding='utf-8') as f:
    data = json.load(f)

BOUNDS = dict(minlat=39.5, maxlat=41.5, minlon=26.0, maxlon=32.0)
TEST_START, TEST_END, TEST_MINMAG = 2020, 2030, 3.0

events = []
for e in data['events']:
    if e.get('src') != 'EMSC':
        continue
    mag = e.get('mag', 0)
    if mag < TEST_MINMAG:
        continue
    t = e.get('time', '')
    if not t:
        continue
    yr = int(t[:4])
    if not (TEST_START <= yr <= TEST_END):
        continue
    lat, lon = e.get('lat', 0), e.get('lon', 0)
    if not (BOUNDS['minlat'] <= lat <= BOUNDS['maxlat'] and BOUNDS['minlon'] <= lon <= BOUNDS['maxlon']):
        continue
    mw = e.get('mw') or mag
    events.append({
        'time': t, 'lat': lat, 'lon': lon,
        'mag': round(mag, 1), 'mw': round(mw, 1),
        'dep': e.get('dep', 0), 'place': e.get('place', '')
    })

events.sort(key=lambda x: x['mw'], reverse=True)
print(f'Test olaylari {TEST_START}-{TEST_END} M>={TEST_MINMAG}: {len(events)}')
for thr in [3.0, 3.5, 4.0, 4.5, 5.0]:
    n = sum(1 for ev in events if ev['mw'] >= thr)
    print(f'  M>={thr}: {n}')
print('En buyuk 5:')
for ev in events[:5]:
    print(f"  Mw{ev['mw']} {ev['time'][:10]} {ev['place']}")

out = {
    'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'description': f'Marmara forecast test: EMSC {TEST_START}-{TEST_END} M>={TEST_MINMAG}',
    'train_period': [1998, 2019],
    'test_period': [TEST_START, TEST_END],
    'min_mag': TEST_MINMAG,
    'bounds': BOUNDS,
    'count': len(events),
    'events': events,
}
with open('data/forecast_marmara_test_events.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('[OK] Kaydedildi: data/forecast_marmara_test_events.json')
