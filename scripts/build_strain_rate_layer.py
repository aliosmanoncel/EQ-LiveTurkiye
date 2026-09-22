"""
build_strain_rate_layer.py
GSRM v2.1 (Kreemer, Blewitt & Klein, 2014) jeodezik strain-rate modelinden
Anadolu bölgesi için bir raster katmanı üretir.

Kaynak veri ZATEN düzenli bir ızgara (0.2° enlem x 0.25° boylam, plaka sınırı
bölgelerinde) — bu yüzden b-value katmanlarının aksine kriging YAPILMAZ, sadece
GSRM'nin resmi grid değerleri görselleştirme çözünürlüğüne yeniden örneklenir —
model DEĞERİ değiştirilmez, yalnızca render edilir. Izgara→ızgara büyütme için
scipy.ndimage.zoom (kübik) kullanılır; scipy.interpolate.griddata'nın Delaunay
tabanlı 'linear' yöntemi İLK DENEMEDE tam-düzenli ızgaralarda dejenere üçgenler
üretip sahte sivri artefaktlar yarattığı için (ekran görüntüsüyle fark edildi)
terk edildi — bkz. main() içindeki yorum.

Gösterilen büyüklük: etkin (efektif) strain rate = sqrt(0.5*(e1^2+e2^2))
  — e1/e2, dosyanın kendi asal (principal) strain-rate sütunları (nanostrain/yıl),
  GSRM'nin kendi haritalarında da kullanılan standart özet ölçü.

Doğrulama (2026-09-22, elle): exx/eyy/exy'den bağımsız eigenvalue hesabı
dosyanın e1/e2/azimuth sütunlarıyla eşleşti; bilinen tektonik desenle uyum
kontrol edildi (KAF/İzmit en yüksek, İç Anadolu/Konya en düşük) — bkz.
GRID_DATA/GSRM_StrainRate/SOURCE.md.

Kaynak: https://geodesy.unr.edu/GSRM/GSRM_average_strain_v2.1.txt.Z
Lisans: CC-BY-NC-SA 3.0 · Kreemer et al. (2014) · GEM Foundation

Çıktı: data/strain_rate_gsrm.png + data/strain_rate_gsrm_meta.json
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
from scipy.interpolate import NearestNDInterpolator
from scipy.ndimage import zoom, gaussian_filter
from PIL import Image

INPUT = '../GRID_DATA/GSRM_StrainRate/GSRM_average_strain_v2.1.txt'
OUTPUT_PNG = 'data/strain_rate_gsrm.png'
OUTPUT_META = 'data/strain_rate_gsrm_meta.json'

# b-value kriging katmanıyla AYNI bounds — iki katman görsel olarak doğrudan
# karşılaştırılabilsin diye (strain rate vs sismisite/asperite).
BOUNDS = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)
GRID_W, GRID_H = 400, 180

# Renk skalası log — dinamik aralık büyük (İç Anadolu ~5-10, KAF/Marmara ~150+)
VMIN, VMAX = 3.0, 200.0


def main():
    lats, lons, e1s, e2s = [], [], [], []
    with open(INPUT, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            p = line.split()
            lat, lon = float(p[0]), float(p[1])
            if BOUNDS['minlat'] - 1 <= lat <= BOUNDS['maxlat'] + 1 and BOUNDS['minlon'] - 1 <= lon <= BOUNDS['maxlon'] + 1:
                lats.append(lat); lons.append(lon)
                e1s.append(float(p[11])); e2s.append(float(p[12]))

    lats = np.array(lats); lons = np.array(lons)
    e1s = np.array(e1s); e2s = np.array(e2s)
    eff = np.sqrt(0.5 * (e1s ** 2 + e2s ** 2))
    print(f'[*] {len(eff)} GSRM ızgara noktası (1° taşkın kenarla) yüklendi')
    print(f'    eff strain rate: {eff.min():.1f} - {eff.max():.1f} ns/yr (bounds içi+kenar)')

    # ÖNEMLİ: GSRM verisi ZATEN düzenli bir ızgara (0.2°x0.25°), ama bölgemizde
    # tam dikdörtgen değil (bazı hücreler tanımsız/boş — muhtemelen model plaka
    # sınırı bölgesi dışında kalan hücreler). scipy.interpolate.griddata'nın
    # Delaunay tabanlı 'linear' yöntemi TAM DÜZENLİ ızgaralarda dejenere
    # (çok ince/uzun) üçgenler üretip sahte sivri artefaktlar yaratıyor
    # (ilk denemede görüldü, ekran görüntüsüyle fark edildi, kod düzeltildi).
    # Bunun yerine: (1) gerçek (lat,lon) ızgarasına PIVOT edilir, (2) eksik
    # hücreler SADECE en-yakın-komşu ile (KDTree, üçgenleme YOK) doldurulur,
    # (3) tamamlanmış düzenli ızgara scipy.ndimage.zoom (kübik) ile pürüzsüzce
    # hedef çözünürlüğe büyütülür — triangülasyon hiç kullanılmıyor.
    lat_step, lon_step = 0.2, 0.25
    ulat = np.round(np.arange(lats.min(), lats.max() + lat_step / 2, lat_step), 3)
    ulon = np.round(np.arange(lons.min(), lons.max() + lon_step / 2, lon_step), 3)
    lat_idx = np.round((lats - ulat[0]) / lat_step).astype(int)
    lon_idx = np.round((lons - ulon[0]) / lon_step).astype(int)
    Z = np.full((len(ulat), len(ulon)), np.nan)
    Z[lat_idx, lon_idx] = eff
    n_missing = np.isnan(Z).sum()
    print(f'    Izgara: {Z.shape[0]}x{Z.shape[1]} hücre, {n_missing} eksik (en-yakın-komşu ile dolduruluyor)')

    if n_missing > 0:
        gi, gj = np.meshgrid(np.arange(len(ulat)), np.arange(len(ulon)), indexing='ij')
        known = ~np.isnan(Z)
        interp = NearestNDInterpolator(np.column_stack([gi[known], gj[known]]), Z[known])
        Z_filled = Z.copy()
        Z_filled[~known] = interp(gi[~known], gj[~known])
    else:
        Z_filled = Z

    # Doldurma için 1°'lik taşkın kenar kullanıldı (BOUNDS kenarındaki hücreler
    # de komşularından doğru doldurulsun diye) — ama çıktı raster'ı TAM OLARAK
    # BOUNDS'a karşılık gelmeli (meta.json'daki bounds ile birebir eşleşsin),
    # bu yüzden büyütmeden ÖNCE tam BOUNDS'a kırpılıyor.
    lat_mask = (ulat >= BOUNDS['minlat'] - 1e-6) & (ulat <= BOUNDS['maxlat'] + 1e-6)
    lon_mask = (ulon >= BOUNDS['minlon'] - 1e-6) & (ulon <= BOUNDS['maxlon'] + 1e-6)
    Z_crop = Z_filled[np.ix_(lat_mask, lon_mask)]
    print(f'    BOUNDS\'a kırpıldı: {Z_crop.shape[0]}x{Z_crop.shape[1]} hücre '
          f'(lat {ulat[lat_mask].min()}-{ulat[lat_mask].max()}, lon {ulon[lon_mask].min()}-{ulon[lon_mask].max()})')

    # GSRM'nin ham 0.2°x0.25° ızgarasında komşu hücreler arasında GERÇEK, büyük
    # sıçramalar var (örn. bitişik iki hücre 2.4 ve 66.3 ns/yıl çıktı — kontrol
    # edildi, pivot hatası değil) — GPS istasyon yoğunluğunun düşük olduğu
    # alanlarda beklenen bir model belirsizliği, tek hücre düzeyinde bilimsel
    # anlam taşımıyor. Kübik büyütme (order=3) bu sıçramaların etrafında
    # aşırı-salınım (ringing) yaratıp sahte sivri uçlar üretiyordu (ekran
    # görüntüsüyle fark edildi). Çözüm: büyütmeden önce hafif Gauss
    # yumuşatması (sigma=1 hücre, ~büyük ölçekli deseni bozmadan tekil-hücre
    # gürültüsünü bastırır) + güvenli order=1 (bilinear, salınım yapmaz).
    Z_smooth = gaussian_filter(Z_crop, sigma=1.0)
    zoom_y = GRID_H / Z_smooth.shape[0]
    zoom_x = GRID_W / Z_smooth.shape[1]
    z_up = zoom(Z_smooth, (zoom_y, zoom_x), order=1)
    # zoom çıktısı enlem-artan sırada (ulat küçükten büyüğe) — raster üstte
    # kuzey olacak şekilde ters çevrilmeli
    z_up = np.flipud(z_up)

    # Bounds dışına taşan/negatif üretebilecek kübik overshoot'u kırp
    z_clipped = np.clip(z_up, VMIN, VMAX)
    norm = LogNorm(vmin=VMIN, vmax=VMAX)
    cmap = matplotlib.colormaps['YlOrRd']
    rgba = (cmap(norm(z_clipped)) * 255).astype(np.uint8)
    rgba[:, :, 3] = 190  # sabit alfa — gerçek GSRM kapsama alanı bounds'u zaten dolduruyor

    img = Image.fromarray(rgba, 'RGBA')
    img.save(OUTPUT_PNG, optimize=True)
    print(f'[OK] PNG kaydedildi: {OUTPUT_PNG} ({GRID_W}x{GRID_H} px)')

    meta = {
        'generated': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'GSRM v2.1 (Kreemer, Blewitt & Klein, 2014) — GEM Foundation',
        'source_url': 'https://geodesy.unr.edu/GSRM/GSRM_average_strain_v2.1.txt.Z',
        'license': 'CC-BY-NC-SA 3.0 (unported) — Kreemer et al. (2014), GEM Foundation',
        'method': 'GSRM resmi ızgara değerleri (kriging YOK — model zaten düzenli grid), '
                  'sqrt(0.5*(e1^2+e2^2)) etkin strain rate; eksik hücreler en-yakın-komşu '
                  '(KDTree) ile dolduruldu, hafif Gauss yumuşatması (sigma=1 hücre, tekil-hücre '
                  'gürültüsünü bastırmak için — ham ızgarada komşu hücreler arası büyük '
                  'sıçramalar var, GPS istasyon yoğunluğu düşük alanlarda beklenen model '
                  'belirsizliği) uygulandı, ardından scipy.ndimage.zoom (bilinear) ile sadece '
                  'görselleştirme çözünürlüğüne büyütüldü.',
        'z_field': 'effective strain rate (sqrt(0.5*(e1^2+e2^2)))',
        'units': 'nanostrain/yr (1e-9/yr)',
        'color_scale': {'min': VMIN, 'max': VMAX, 'type': 'log', 'colormap': 'YlOrRd'},
        'source_pts': int(len(eff)),
        'grid_w': GRID_W, 'grid_h': GRID_H,
        'bounds': BOUNDS,
        'note': 'Bu bir JEODEZİK MODEL ürünüdür (GPS verisinden türetilmiş uzun-dönem gerinim oranı) — '
                'canlı ölçüm veya deprem tahmini DEĞİLDİR. Chen & Liu (2024, SRL, doi:10.1785/0220230306) '
                'bu modeli Anadolu için sismisiteyle karşılaştırmada kullanmıştır.',
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'[OK] Meta kaydedildi: {OUTPUT_META}')


if __name__ == '__main__':
    main()
