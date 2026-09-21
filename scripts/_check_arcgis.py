import urllib.request, ssl
ctx = ssl._create_unverified_context()

# Katman adi "58" (sayisal ID) ile test
combos = [
    ('58',            'EPSG:4326', '32.8,24.5,45.1,46.0'),
    ('58',            'CRS:84',    '24.5,32.8,46.0,45.1'),
    ('TSTH_PGA_475',  'EPSG:4326', '32.8,24.5,45.1,46.0'),
    ('TSTH_PGA_475',  'CRS:84',    '24.5,32.8,46.0,45.1'),
    ('58',            'EPSG:3857', '2726958,3875375,5124074,5682462'),
]
for layer, crs, bbox in combos:
    url = (
        'https://tucbs-public-api.csb.gov.tr/trk_afad_tdth_wms'
        f'?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap'
        f'&LAYERS={layer}&STYLES=default'
        f'&CRS={crs}&BBOX={bbox}'
        '&WIDTH=512&HEIGHT=256&FORMAT=image/png&TRANSPARENT=TRUE'
    )
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            ctype = r.headers.get('Content-Type','')
            cors  = r.headers.get('Access-Control-Allow-Origin','YOK')
            size  = len(r.read())
            print(f'OK  layer={layer:16} crs={crs:12} size={size:7}  CORS={cors}  type={ctype[:15]}')
    except Exception as e:
        print(f'ERR layer={layer:16} crs={crs:12} {str(e)[:50]}')
