import urllib.request, ssl
ctx = ssl._create_unverified_context()

base = 'https://efehrmaps.ethz.ch/cgi-bin/mapserv?map=/var/www/mapfile/eshm20data.map'

# seismic-hazard katmanini test et
combos = [
    ('seismic-hazard', 'EPSG:4326', '30,20,50,50'),
    ('seismic-hazard', 'EPSG:3857', '2226389,3503549,6261722,6261722'),
    ('seismic-hazard', 'CRS:84',    '20,30,50,50'),
]
for layer, crs, bbox in combos:
    url = (base + f'&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap'
           f'&LAYERS={layer}&STYLES=default&CRS={crs}&BBOX={bbox}'
           '&WIDTH=512&HEIGHT=256&FORMAT=image/png&TRANSPARENT=TRUE')
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            ctype = r.headers.get('Content-Type','')
            cors  = r.headers.get('Access-Control-Allow-Origin','YOK')
            size  = len(r.read())
            print(f'OK  {crs:12} size={size:7}  CORS={cors}  type={ctype[:20]}')
    except Exception as e:
        print(f'ERR {crs:12} {str(e)[:60]}')
