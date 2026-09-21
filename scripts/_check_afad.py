import urllib.request, ssl
ctx = ssl._create_unverified_context()

tests = [
    'https://geoserver.afad.gov.tr/geoserver/wms?SERVICE=WMS&REQUEST=GetCapabilities',
    'https://geoserver.afad.gov.tr/geoserver/ows?SERVICE=WMS&REQUEST=GetCapabilities',
    'https://afadgis.afad.gov.tr/server/rest/services',
    'https://afadgis.afad.gov.tr/server/rest/services?f=json',
    'https://cbsgis.afad.gov.tr/arcgis/rest/services',
    'https://cbsgis.afad.gov.tr/arcgis/rest/services?f=json',
    'https://hazard.afad.gov.tr/',
    'https://tdth.afad.gov.tr/TDTH/json',
    'https://tdth.afad.gov.tr/TDTH/spectra',
]
for url in tests:
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            d = r.read(200).decode('utf-8','replace')
            print(f'OK  {r.status}  {url}')
            print(f'    {d[:120]}')
    except Exception as e:
        print(f'ERR {str(e)[:55]}  {url[-50:]}')
