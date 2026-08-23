import pandas as pd, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# Batı (EPICA v1.1, Avrupa kapsamı, 1005-1899) zaten data/epica_europe_historical.json'da.
# Bu script Doğu/Orta Anadolu'yu (SHARE-CET) TEK bir "Tarihsel Depremler" katmanı olarak
# aynı dosyaya birleştirir (kullanıcı: "ikisi tek parca gorunse iyi olmazmi", 2026-08-23).
# 1900 sonrası alınmıyor (ISC/EMSC zaten aletsel dönemi kapsıyor, kullanıcı onayı).

MW_MIN = 4.0
YEAR_MAX = 1899

with open('data/epica_europe_historical.json', encoding='utf-8') as f:
    existing = json.load(f)
# Idempotency guard: script yeniden calistirilirsa onceki CET birlestirmesi
# tekrar eklenmesin diye once CET kayitlari cikarilir (2026-08-23'te bir kez
# cift-sayim hatasi yasandi, duzeltildi).
west_events = [e for e in existing['events'] if e.get('reg') != 'CET']
print(f'Mevcut (EPICA/Batı, CET haric): {len(west_events)}')

df = pd.read_excel('data/SHARE_CET.xls', sheet_name='catalogue')
df = df[(df['Year'] <= YEAR_MAX) & df['Mw'].notna() & (df['Mw'] >= MW_MIN)]

east_events = []
for _, r in df.iterrows():
    lat = r['Lat']; lon = r['Lon']; mw = r['Mw']; yr = r['Year']
    if pd.isna(lat) or pd.isna(lon): continue
    mo = int(r['Mo']) if pd.notna(r['Mo']) else None
    da = int(r['Da']) if pd.notna(r['Da']) else None
    date_str = f'{int(yr):04d}'
    if mo: date_str += f'-{mo:02d}'
    if mo and da: date_str += f'-{da:02d}'
    east_events.append({
        'lon': round(float(lon), 4),
        'lat': round(float(lat), 4),
        'mag': round(float(mw), 2),
        'year': int(yr),
        'date': date_str,
        'loc': str(r['Ax'])[:30] if pd.notna(r['Ax']) else '',
        'reg': 'CET',
    })
print(f'Yeni (SHARE-CET/Doğu, M>={MW_MIN}, <={YEAR_MAX}): {len(east_events)}')

# Kaba çakışma kontrolü: aynı yıl + ~aynı koordinat (0.1 derece) + ~aynı büyüklük (0.2)
dupes = 0
for e in east_events:
    for w in west_events:
        if (w['year'] == e['year'] and abs(w['lat']-e['lat']) < 0.1
                and abs(w['lon']-e['lon']) < 0.1 and abs(w['mag']-e['mag']) < 0.2):
            dupes += 1
            break
print(f'Olası çakışma (batı ile aynı yıl+konum+büyüklük): {dupes}')

merged = west_events + east_events
merged.sort(key=lambda e: e['year'])
years = [e['year'] for e in merged]

out = {
    'meta': {
        'source': 'EPICA v1.1 (batı/Avrupa) + SHARE-CET (doğu/orta Anadolu)',
        'reference': 'Rovida & Antonucci (2021) INGV CC-BY 4.0, doi:10.13127/epica.1.1; '
                     'Sesetyan, Demircioglu, Rovida, Albini & Stucchi (2011), SHARE-CET, '
                     'emidius.eu/SHEEC',
        'doi': '10.13127/epica.1.1',
        'mw_min': MW_MIN,
        'count': len(merged),
        'year_range': [min(years), max(years)],
        'note': 'Tek parca tarihsel katman - bati (EPICA) + dogu (SHARE-CET) birlestirildi, '
                '1900 sonrasi aletsel (ISC/EMSC) katmanla cakismasin diye alinmadi. '
                'METODOLOJI NOTU: EPICA ve SHARE-CET 1900-oncesi Mw icin AYNI donusum '
                'zincirini kullanmiyor - SHARE-CET Soysal ve ark. (1981) tarihsel '
                'kataloguna dayanip Io->Ms (Kalafat ve ark. 2007) -> Mw (Zare 2012, EMME '
                'ic raporu) iki asamali donusumu kullanirken, EPICA v1.1 (2021) INGVnin '
                'kendi guncel homojenizasyon semasini kullanir. Ikisi de Mw skalasinda '
                'sonuc verir ama tam metodolojik ozdeslik iddia edilmez.',
    },
    'events': merged,
}
with open('data/epica_europe_historical.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
print(f'Birlesik toplam: {len(merged)} | Yil: {min(years)}-{max(years)}')
print(f'Kaydedildi: {os.path.getsize("data/epica_europe_historical.json")/1024:.1f} KB')
