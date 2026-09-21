import urllib.request, ssl, json, os
ctx = ssl._create_unverified_context()

# Tam Türkiye extent (capabilities'ten): lon 24.47–46.0, lat 32.8–45.1
# CRS=EPSG:4326 → BBOX: lat_min, lon_min, lat_max, lon_max (WMS 1.3.0 axis order)
url = (
    'https://tucbs-public-api.csb.gov.tr/trk_afad_tdth_wms'
    '?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap'
    '&LAYERS=58&STYLES=default'
    '&CRS=EPSG:4326&BBOX=32.8,24.468125,45.099,45.991'
    '&WIDTH=2000&HEIGHT=1000'
    '&FORMAT=image/png&TRANSPARENT=TRUE'
)
print('İndiriliyor...')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
    ctype = r.headers.get('Content-Type', '')
    data = r.read()
    print(f'Content-Type: {ctype}  Boyut: {len(data)} bytes')

if b'PNG' in data[:8] or b'\x89PNG' == data[:4]:
    out = os.path.join(os.path.dirname(__file__), '..', 'data', 'afad_tsth_pga475.png')
    out = os.path.normpath(out)
    with open(out, 'wb') as f:
        f.write(data)
    print(f'Kaydedildi: {out}')
    # Meta
    meta = {
        'layer': 'TSTH_PGA_475 (ID=58)',
        'source': 'AFAD · CSB/TUCBS · tucbs-public-api.csb.gov.tr',
        'crs': 'EPSG:4326',
        'bounds': {'minlat': 32.8, 'maxlat': 45.099, 'minlon': 24.468, 'maxlon': 45.991},
        'return_period': '475yr (10%/50yr)',
        'parameter': 'PGA',
        'reference': 'TBDY 2018',
        'width': 2000, 'height': 1000,
    }
    mout = out.replace('.png', '_meta.json')
    with open(mout, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'Meta: {mout}')
else:
    print('PNG değil! İlk 200 byte:')
    print(data[:200])
