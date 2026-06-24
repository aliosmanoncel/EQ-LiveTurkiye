import json, pathlib

tl = json.loads(pathlib.Path('data/tl_grid_adaptive.json').read_text('utf-8'))

LAT_MIN, LAT_MAX = 40.0, 41.5
LON_MIN, LON_MAX = 26.5, 30.5

marmara = [p for p in tl['grid']
           if LAT_MIN <= p['lat'] <= LAT_MAX and LON_MIN <= p['lon'] <= LON_MAX]

marmara.sort(key=lambda p: p['tl_m7p4'])

print(f'Marmara nokta sayisi: {len(marmara)}')
print()
header = f"{'Lat':>5} {'Lon':>5}  {'b':>6}  {'a_ann':>6}  {'TL-6.8':>8}  {'TL-7.4':>8}  {'TL-7.8':>8}  Zone"
print(header)
print('-' * 72)
for p in marmara[:25]:
    row = (f"{p['lat']:5.1f} {p['lon']:5.1f}  {p['b']:6.3f}  {p['a_ann']:6.3f}"
           f"  {p['tl_m6p8']:8.0f}  {p['tl_m7p4']:8.0f}  {p['tl_m7p8']:8.0f}  {p['zone']}")
    print(row)

alarm = [p for p in marmara if p['tl_m7p4'] < 200]
print(f'\nAsperite alarmlar (TL_7.4 < 200 yr): {len(alarm)} nokta')
for p in alarm:
    print(f"  ({p['lat']}, {p['lon']})  b={p['b']:.3f}  TL_7.4={p['tl_m7p4']:.0f}yr")
