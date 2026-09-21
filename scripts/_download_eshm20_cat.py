import sys, json, math
import dbfread
sys.stdout.reconfigure(encoding='utf-8')

# Turkiye + cevresini kapsa: lon 24-46, lat 34-44 (Marmara'dan Karadeniz'e)
LON_MIN, LON_MAX = 24.0, 46.0
LAT_MIN, LAT_MAX = 34.0, 44.0
MW_MIN = 4.0  # minimum buyukluk

print('DBF okunuyor...')
dbf = dbfread.DBF('data/eshm20_catalogue_declustered.dbf', load=False)

events = []
total = 0
for rec in dbf:
    total += 1
    lon = rec['longitude']
    lat = rec['latitude']
    mag = rec['magnitude']
    if lon is None or lat is None or mag is None: continue
    if math.isnan(float(lon)) or math.isnan(float(lat)) or math.isnan(float(mag)): continue
    if not (LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX): continue
    if mag < MW_MIN: continue
    events.append({
        'lon': round(float(lon), 4),
        'lat': round(float(lat), 4),
        'mag': round(float(mag), 2),
        'depth': round(float(rec['depth']), 1) if rec['depth'] and not math.isnan(float(rec['depth'])) else None,
        'year': int(rec['year']),
        'date': str(rec['Date']),
        'src': str(rec['source_cat'])[:20],
    })

print(f'Toplam: {total} | Turkiye filtresi M>={MW_MIN}: {len(events)}')
print(f'Yil aralik: {min(e["year"] for e in events)} - {max(e["year"] for e in events)}')
print(f'Mag aralik: {min(e["mag"] for e in events):.1f} - {max(e["mag"] for e in events):.1f}')

# Buyukluk dagilimi
for m in [4,5,6,7]:
    n = sum(1 for e in events if e['mag'] >= m)
    print(f'  M>={m}: {n}')

# JSON kaydet
out = {
    'meta': {
        'source': 'ESHM20 Unified Declustered Catalogue v02a',
        'reference': 'Danciu et al. (2021) EFEHR Technical Report 001',
        'region': f'lon {LON_MIN}-{LON_MAX}, lat {LAT_MIN}-{LAT_MAX}',
        'mw_min': MW_MIN,
        'count': len(events),
        'year_range': [min(e['year'] for e in events), max(e['year'] for e in events)],
    },
    'events': events
}
with open('data/eshm20_turkey_historical.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',',':'))
print(f'\nKaydedildi: data/eshm20_turkey_historical.json')
import os
print(f'Boyut: {os.path.getsize("data/eshm20_turkey_historical.json")/1024:.1f} KB')
