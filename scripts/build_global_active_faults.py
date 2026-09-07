"""
build_global_active_faults.py
GEM Global Active Faults Database (GAF-DB) -> data/global_active_faults.geojson

Kaynak: GEM GAF-DB, harmonize edilmis global katalog
  (Styron & Pagani 2020, Earthquake Spectra,
   doi:10.1177/8755293020944182, CC-BY-SA-4.0)
  https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/master/geojson/gem_active_faults_harmonized.geojson
  (2026-09-07 itibariyle 13.696 hat, ~10.6 MB)

Amac: MTA'nin zaten detayli Turkiye diri fay katmaniyla cakisan GEM
hatlarini elemek ("Dunya Diri Faylari" katmani bilincli olarak Turkiye
karasini haric tutuyor, bkz. index.html "gaf" toggle tooltip).

ONCEKI yontem (commit 93a2b2d3, 2026-08-30): dikdortgen bbox
(lat 34-43, lon 25-46 -- TR_BOUNDS, eq_fetch_turkey.py'deki ayni kutu)
icinde TAMAMEN kalan hatlar elendi. Bu kutu Turkiye'nin gercek kara
sinirlarindan cok daha genis -- Karadeniz'in guney yarisini ve tum
Dogu Akdeniz/Kibris havzasini da kapsiyor. Ham veriyle karsilastirma
(2026-09-07) bunun MTA'nin hic kapsamadigi deniz-alti fay verisini de
sildigini gosterdi: Karadeniz'de 60 ham hattan sadece 11'i, Dogu
Akdeniz/Kibris'ta 83 ham hattan sadece 22'si kaliyordu.

YENI yontem (bu script): Natural Earth 10m cozunurluklu Turkiye kara
siniri poligonu kullanilarak SADECE bu poligonun icinde TAMAMEN kalan
hatlar elendi -- denizdeki hatlar (Karadeniz, Ege, Dogu Akdeniz) artik
korunuyor.
  https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson
  ("Turkey" ozelligi)

10m cozunurluk kasitli secildi: kiyi hatti girinti/cikintilarini
(korfezler, yarimadalar) 110m/50m gibi dusuk cozunurluklu bir poligona
gore cok daha dogru temsil ediyor -- kiyiya yakin hatlarin iceri/disari
siniflandirmasi rastgele/kaba olmasin diye.

Bagimlilik: pip install shapely (bu depoda baska hicbir script'te
kullanilmiyor, sadece bu build script'i icin gerekli).

Kullanim:
  python scripts/build_global_active_faults.py
"""
import json
import sys
import urllib.request

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from shapely.geometry import shape

GAF_URL = (
    'https://raw.githubusercontent.com/GEMScienceTools/'
    'gem-global-active-faults/master/geojson/'
    'gem_active_faults_harmonized.geojson'
)
TURKEY_BOUNDARY_URL = (
    'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/'
    'master/geojson/ne_10m_admin_0_countries.geojson'
)
OUT_PATH = 'data/global_active_faults.geojson'


def fetch_json(url):
    print(f'Fetching {url} ...')
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def main():
    raw = fetch_json(GAF_URL)
    features = raw['features']
    print(f'GEM GAF-DB ham veri: {len(features)} hat')

    countries = fetch_json(TURKEY_BOUNDARY_URL)
    turkey_poly = None
    for f in countries['features']:
        props = f['properties']
        name = props.get('NAME') or props.get('NAME_EN') or props.get('ADMIN')
        if name == 'Turkey':
            turkey_poly = shape(f['geometry'])
            break
    if turkey_poly is None:
        raise RuntimeError('Turkey polygon not found in Natural Earth dataset')
    print(f'Turkiye poligonu bulundu, bounds={turkey_poly.bounds}')

    out_features = []
    excluded = 0
    skipped_geom = 0
    for f in features:
        geom = f['geometry']
        if geom['type'] not in ('LineString', 'MultiLineString'):
            skipped_geom += 1
            continue
        line = shape(geom)
        if turkey_poly.contains(line):
            excluded += 1
            continue
        p = f['properties']
        out_features.append({
            'type': 'Feature',
            'properties': {
                'name': p.get('name'),
                'slip_type': p.get('slip_type'),
                'catalog': p.get('catalog_name'),
            },
            'geometry': geom,
        })

    print(f'Gecersiz/desteklenmeyen geometri (atlandi): {skipped_geom}')
    print(f'Turkiye poligonu icinde tamamen kalan (elenen): {excluded}')
    print(f'Kalan (yazilacak): {len(out_features)}')

    out = {
        'type': 'FeatureCollection',
        'metadata': {
            'source': 'GEM Global Active Faults Database (GAF-DB)',
            'citation': 'Styron & Pagani (2020), Earthquake Spectra, doi:10.1177/8755293020944182',
            'license': 'CC-BY-SA-4.0',
            'note': (
                'Turkiye kara siniri icinde TAMAMEN kalan hatlar filtrelendi '
                '(MTA diri fay katmaniyla ortusmeyi onlemek icin); sinir-otesi '
                've deniz-alti (Karadeniz, Ege, Dogu Akdeniz) hatlar korundu. '
                'Filtre Natural Earth 10m cozunurluklu Turkiye kara siniri '
                'poligonu kullanilarak yapildi (onceki surum: dikdortgen bbox, '
                'bkz. commit 93a2b2d3 -- deniz-alti veriyi gereksiz yere '
                'siliyordu; bkz. scripts/build_global_active_faults.py).'
            ),
        },
        'features': out_features,
    }

    with open(OUT_PATH, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(',', ':'))
    print(f'Yazildi: {OUT_PATH}')


if __name__ == '__main__':
    main()
