"""
turkiye_sinir.py — Tekrarlanabilir Türkiye sınır tanımı (araştırma alt kümesi için).

Kaynak: Natural Earth 1:10m Admin-0 Countries, sürüm v5.1.2
  https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_admin_0_countries.geojson
  sha256 239eec57ac17f100a11e2536cffc56752c318b50ae765b0918ff7aab4ce8f255 (betik denetler)
Tanım (deniz payı B km, B ∈ {0, 30, 50}):
  1. Türkiye kara poligonu (ADMIN == 'Turkey').
  2. B > 0: Türkiye'ye özgü eş-uzaklıklı projeksiyonda (azimutal eşit uzaklık, merkez 39°K 35°D) B km tampon;
     iç boşluklar (Marmara) doldurulur.
  3. Komşu ülkelerin KARA alanları çıkarılır (Yunanistan ve adaları, Bulgaristan, Gürcistan, Ermenistan,
     Azerbaycan, İran, Irak, Suriye, Kıbrıs, Kuzey Kıbrıs). Deniz alanları ülkeye göre bölünmez:
     B km içindeki deniz Türkiye alt kümesine girer (siyasi deniz yetki alanı değildir).
Çıktı: turkiye_sinir_{B}km.geojson (0,002° sadeleştirilmiş; kaynak karma ve tanım özelliklerde).
Kullanım: python analysis/2026-11-08_bagimsiz_olay_kimligi/turkiye_sinir.py <ne_10m_admin_0_countries.geojson>
"""
import hashlib, json, os, sys

from pyproj import Transformer
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import transform, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
NE_SHA = '239eec57ac17f100a11e2536cffc56752c318b50ae765b0918ff7aab4ce8f255'
NEIGH = ['Greece', 'Bulgaria', 'Georgia', 'Armenia', 'Azerbaijan', 'Iran', 'Iraq', 'Syria', 'Cyprus', 'Northern Cyprus']
BUFFERS = [0, 30, 50]
AEQD = '+proj=aeqd +lat_0=39 +lon_0=35 +datum=WGS84 +units=m'


def fill_holes(g):
    if isinstance(g, Polygon):
        return Polygon(g.exterior)
    return MultiPolygon([Polygon(p.exterior) for p in g.geoms])


def build(ne_path):
    raw = open(ne_path, 'rb').read()
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == NE_SHA, f'Natural Earth dosyası beklenen sürüm değil: {sha}'
    fc = json.loads(raw)
    by = {f['properties']['ADMIN']: shape(f['geometry']) for f in fc['features']}
    tr = by['Turkey']
    neigh = unary_union([by[n] for n in NEIGH])
    fwd = Transformer.from_crs('EPSG:4326', AEQD, always_xy=True).transform
    inv = Transformer.from_crs(AEQD, 'EPSG:4326', always_xy=True).transform
    out = {}
    for B in BUFFERS:
        if B == 0:
            g = tr
        else:
            g = transform(inv, fill_holes(transform(fwd, tr).buffer(B * 1000, resolution=16)))
            g = g.difference(neigh)
        g = g.simplify(0.002, preserve_topology=True)
        props = dict(tanim=f'Türkiye kara + {B} km deniz payı (komşu karalar hariç)' if B else 'Türkiye kara poligonu',
                     kaynak='Natural Earth 1:10m Admin-0 Countries v5.1.2', kaynak_sha256=sha,
                     projeksiyon=AEQD, cikarilan_komsular=NEIGH if B else [], sadelestirme_derece=0.002,
                     not_='deniz alanı siyasi yetki alanı değildir; araştırma alt kümesi tanımıdır')
        path = os.path.join(HERE, f'turkiye_sinir_{B}km.geojson')
        json.dump(dict(type='FeatureCollection', features=[dict(type='Feature', properties=props, geometry=mapping(g))]),
                  open(path, 'w', encoding='utf-8'), ensure_ascii=False)
        out[B] = g
        print(f'{B:3d} km: {path}  ({os.path.getsize(path) // 1024} KB)')
    return out


def load(B):
    fc = json.load(open(os.path.join(HERE, f'turkiye_sinir_{B}km.geojson'), encoding='utf-8'))
    return shape(fc['features'][0]['geometry']), fc['features'][0]['properties']


if __name__ == '__main__':
    build(sys.argv[1])
