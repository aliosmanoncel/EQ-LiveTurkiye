"""
build_strain_rate_layer_global.py
GSRM v2.1 (Kreemer, Blewitt & Klein, 2014) jeodezik strain-rate modelinden
DÜNYA GENELİ bir raster katmanı üretir — build_strain_rate_layer.py'nin
(Türkiye/Anadolu, b-value kriging katmanıyla aynı bounds) global karşılığı.

ÖNEMLİ FARK (Türkiye script'inden) — İKİ AYRI KARAR:

(1) GSRM v2.1 yalnızca plaka sınırı bölgelerinde tanımlı — global veride
olası hücrelerin çoğu boş. Türkiye script'i küçük/kenar boşlukları
en-yakın-komşu ile dolduruyordu; global ölçekte bu YAPILMAZ — okyanus
ortası veya kıta içi gibi GSRM'in hiç veri üretmediği alanları "doldurmak"
var olmayan bir strain sinyali icat etmek olurdu. Bunun yerine mesafe
sınırlı en-yakın-komşu kullanılır: bir çıktı pikseli, en yakın GSRM
noktasına MAX_DIST'ten uzaksa tamamen şeffaf bırakılır.

(2) Türkiye script'i (lat,lon)'u SABİT 0.2°x0.25° düzenli ızgaraya pivot
ediyordu — bu Türkiye/Anadolu alt-kümesinde doğrulanmış bir varsayımdı.
İlk global denemede bu varsayım YANLIŞ çıktı: 145 086 noktanın sadece
75 619'u benzersiz ızgara hücresine düştü, 69 419 hücrede çakışma vardı
(aynı hücreye 2-4 nokta) — GSRM'in çözünürlüğü bölgeye göre değişiyor
(makalede belirtildiği gibi plaka sınırı bölgelerinde 0.1°, CEUS gibi
bölgelerde 0.5°). Bu yüzden global render SABİT IZGARA VARSAYMAZ —
scipy.spatial.cKDTree ile gerçek scattered-point en-yakın-komşu araması
yapılır, hiçbir düzenlilik varsayımı içermez.

Gösterilen büyüklük: etkin strain rate = max(|e1|,|e2|) (nanostrain/yıl,
log ölçek) — Öncel & Wilson (2006) eq.1b tanımı, Türkiye script'iyle
tutarlı.

Kaynak: https://geodesy.unr.edu/GSRM/GSRM_average_strain_v2.1.txt.Z
Lisans: CC-BY-NC-SA 3.0 · Kreemer et al. (2014) · GEM Foundation

Çıktı: data/strain_rate_gsrm_global.png + data/strain_rate_gsrm_global_meta.json
"""
import json
import sys
import datetime

import numpy as np

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import matplotlib
matplotlib.use('Agg')
from matplotlib.colors import LogNorm
from scipy.spatial import cKDTree
from PIL import Image

INPUT = '../GRID_DATA/GSRM_StrainRate/GSRM_average_strain_v2.1.txt'
OUTPUT_PNG = 'data/strain_rate_gsrm_global.png'
OUTPUT_META = 'data/strain_rate_gsrm_global_meta.json'

# NOT: Leaflet'in varsayılan CRS'i (EPSG:3857, Web Mercator) enlemi
# ±85.0511287798°'de KIRPAR (bu değerde mercY=±pi olacak şekilde standart
# tanım) — GSRM verisinin kendi kapsamı 86.8°'ye kadar çıkıyor ama bunu
# BOUNDS'a olduğu gibi koymak, Leaflet'in köşe noktasını 85.05°'de
# projekte edip görüntüyü BEKLENENDEN FARKLI bir dikey ölçekte germesine
# yol açar (canlı testte fark edildi: içerik sistematik olarak güneye
# kaymış görünüyordu — ilk Mercator düzeltmesi ham enlemi kullanmıştı,
# bu ikinci düzeltme Leaflet'in gerçek kırpma sınırıyla eşleşiyor).
LEAFLET_MAX_LAT = 85.0511287798
BOUNDS = dict(minlat=-66.2, maxlat=LEAFLET_MAX_LAT, minlon=-180.0, maxlon=180.0)
GRID_W, GRID_H = 1440, 612  # ~0.25 deg/piksel

# En-yakın-komşu araması bu mesafeyi (derece, ~kabaca) aşarsa piksel şeffaf
# bırakılır — GSRM'in en ince çözünürlüğünün (0.1 deg) birkaç katı, veri
# olmayan bölgeleri doldurmadan küçük boşlukları makul biçimde köprüler.
MAX_DIST_DEG = 0.35

# Türkiye katmanıyla aynı alt sınır (VMIN=3) ama global dinamik aralık çok
# daha geniş (max ~17 700 ns/yr, %99.9'u <4560) — VMAX yükseltildi.
VMIN, VMAX = 3.0, 500.0


def main():
    lats, lons, e1s, e2s = [], [], [], []
    with open(INPUT, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            p = line.split()
            lats.append(float(p[0])); lons.append(float(p[1]))
            e1s.append(float(p[11])); e2s.append(float(p[12]))

    lats = np.array(lats); lons = np.array(lons)
    e1s = np.array(e1s); e2s = np.array(e2s)
    eff = np.maximum(np.abs(e1s), np.abs(e2s))
    print(f'[*] {len(eff)} global GSRM noktası yüklendi')
    print(f'    eff strain rate: min={eff.min():.1f} p50={np.percentile(eff,50):.1f} '
          f'p99={np.percentile(eff,99):.1f} max={eff.max():.1f} ns/yr')

    # Sabit ızgara VARSAYILMAZ — gerçek scattered-point en-yakın-komşu (KDTree).
    #
    # KRİTİK PROJEKSİYON DÜZELTMESİ: Leaflet L.imageOverlay, görüntüyü verilen
    # iki köşe arasında haritanın KENDİ Web Mercator projeksiyonunda doğrusal
    # gerer — görüntünün pikselleri düz ENLEM aralıklarıyla değil, Web Mercator
    # Y ekseninde eşit aralıklı olmalıdır. İlk denemede grid_lats basitçe
    # np.linspace(maxlat,minlat,...) ile düz enlemde üretilmişti — Türkiye'nin
    # dar enlem aralığında (34-43°, ~9°) bu yaklaşım görünmez bir hataydı, ama
    # global 153°'lik aralıkta (-66.2°..86.8°) BÜYÜK bir düşey kaymaya yol açtı
    # (canlı testte fark edildi: Türkiye'nin gerçek strain verisi haritada
    # Suriye'nin üzerinde görünüyordu — PNG dosyasının kendisi doğruydu,
    # sorun sadece Leaflet'in görüntüyü gerdiği projeksiyon varsayımıydı).
    # Çözüm: her piksel satırının GERÇEK enlemini ters-Mercator ile hesaplayıp
    # o enlemde örnekleme yapmak — böylece Leaflet doğrusal gerince sonuç
    # doğru enlemlere denk geliyor.
    def lat_to_mercY(lat_deg):
        phi = np.radians(lat_deg)
        return np.log(np.tan(np.pi / 4 + phi / 2))

    def mercY_to_lat(y):
        return np.degrees(2 * np.arctan(np.exp(y)) - np.pi / 2)

    y_north = lat_to_mercY(BOUNDS['maxlat'])
    y_south = lat_to_mercY(BOUNDS['minlat'])
    grid_y = np.linspace(y_north, y_south, GRID_H)  # Mercator Y'de eşit aralık
    grid_lats = mercY_to_lat(grid_y)  # bu Y'lere karşılık gelen GERÇEK enlemler

    tree = cKDTree(np.column_stack([lats, lons]))
    grid_lons = np.linspace(BOUNDS['minlon'], BOUNDS['maxlon'], GRID_W)
    glon, glat = np.meshgrid(grid_lons, grid_lats)
    query_pts = np.column_stack([glat.ravel(), glon.ravel()])
    dist, idx = tree.query(query_pts, k=1)
    Z = eff[idx].reshape(GRID_H, GRID_W)
    mask_far = dist.reshape(GRID_H, GRID_W) > MAX_DIST_DEG
    coverage = (~mask_far).sum() / mask_far.size * 100
    print(f'    Cikti izgarasi: {GRID_W}x{GRID_H} px, kapsama %{coverage:.1f} '
          f'(MAX_DIST_DEG={MAX_DIST_DEG}, boşluklar DOLDURULMADI, şeffaf kalacak)')

    z_clipped = np.clip(Z, VMIN, VMAX)
    norm = LogNorm(vmin=VMIN, vmax=VMAX)
    cmap = matplotlib.colormaps['YlOrRd']
    rgba = (cmap(norm(z_clipped)) * 255).astype(np.uint8)
    rgba[:, :, 3] = np.where(mask_far, 0, 190).astype(np.uint8)

    img = Image.fromarray(rgba)
    img.save(OUTPUT_PNG, optimize=True)
    print(f'[OK] PNG kaydedildi: {OUTPUT_PNG} ({GRID_W}x{GRID_H} px)')

    meta = {
        'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'GSRM v2.1 (Kreemer, Blewitt & Klein, 2014) — GEM Foundation',
        'source_url': 'https://geodesy.unr.edu/GSRM/GSRM_average_strain_v2.1.txt.Z',
        'license': 'CC-BY-NC-SA 3.0 (unported) — Kreemer et al. (2014), GEM Foundation',
        'method': f'GSRM resmi noktaları, sabit ızgara VARSAYILMADI (Türkiye katmanından farklı — '
                  f'global çözünürlük bölgeye göre değişiyor). scipy.spatial.cKDTree ile gerçek '
                  f'en-yakın-komşu araması, MAX_DIST_DEG={MAX_DIST_DEG}° üstü mesafeler şeffaf '
                  f'bırakıldı (var olmayan strain sinyali icat edilmedi, büyütme/yumuşatma da yok). '
                  f'Piksel satırları düz enlemde değil, ters-Mercator ile hesaplanmış gerçek '
                  f'enlemlerde örneklendi (Leaflet L.imageOverlay görüntüyü Web Mercator\'da '
                  f'doğrusal gerdiği için — bkz. script içi yorum, canlı testte fark edilip '
                  f'düzeltilen bir projeksiyon hatası).',
        'z_field': 'effective strain rate (max(|e1|,|e2|))',
        'units': 'nanostrain/yr (1e-9/yr)',
        'color_scale': {'min': VMIN, 'max': VMAX, 'type': 'log', 'colormap': 'YlOrRd'},
        'source_pts': int(len(eff)),
        'coverage_pct': round(float(coverage), 1),
        'grid_w': int(Z.shape[1]), 'grid_h': int(Z.shape[0]),
        'bounds': BOUNDS,
        'note': 'Bu bir JEODEZİK MODEL ürünüdür (GPS verisinden türetilmiş uzun-dönem gerinim '
                'oranı) — canlı ölçüm veya deprem tahmini DEĞİLDİR. Yalnızca GSRM\'in veri '
                'ürettiği plaka sınırı bölgeleri renklidir; boş alanlar "sıfır strain" değil, '
                '"model bu bölgede tanımsız" anlamına gelir.',
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'[OK] Meta kaydedildi: {OUTPUT_META}')


if __name__ == '__main__':
    main()
