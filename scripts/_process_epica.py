import pandas as pd, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('data/EPICA_v1.1.xlsx', sheet_name='EPICA')
print(f'Toplam: {len(df)}')

MW_MIN = 4.0
events = []
for _, r in df.iterrows():
    lat = r['Lat']; lon = r['Lon']; mw = r['Mw']; yr = r['Year']
    if pd.isna(lat) or pd.isna(lon) or pd.isna(mw) or pd.isna(yr): continue
    if float(mw) < MW_MIN: continue
    mo = int(r['Mo']) if pd.notna(r['Mo']) else None
    da = int(r['Da']) if pd.notna(r['Da']) else None
    date_str = f'{int(yr):04d}'
    if mo: date_str += f'-{mo:02d}'
    if mo and da: date_str += f'-{da:02d}'
    events.append({
        'lon': round(float(lon), 4),
        'lat': round(float(lat), 4),
        'mag': round(float(mw), 2),
        'year': int(yr),
        'date': date_str,
        'loc': str(r['Ax'])[:30] if pd.notna(r['Ax']) else '',
        'reg': str(r['Reg'])[:10] if pd.notna(r['Reg']) else '',
    })

mags = [e['mag'] for e in events]
years = [e['year'] for e in events]
print(f'M>={MW_MIN} ve koordinatli: {len(events)}')
for m in [4, 5, 6, 7]:
    print(f'  M>={m}: {sum(1 for x in mags if x >= m)}')
print(f'Yil: {min(years)} - {max(years)}')

out = {
    'meta': {
        'source': 'EPICA v1.1',
        'reference': 'Rovida & Antonucci (2021) INGV CC-BY 4.0',
        'doi': '10.13127/epica.1.1',
        'mw_min': MW_MIN,
        'count': len(events),
        'year_range': [min(years), max(years)],
    },
    'events': events,
}
with open('data/epica_europe_historical.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
print(f'Kaydedildi: {os.path.getsize("data/epica_europe_historical.json")/1024:.1f} KB')
