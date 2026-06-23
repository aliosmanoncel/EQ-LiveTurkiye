"""
build_bvalue_kriging.py
b-değeri noktalarından (19 719 nokta) Ordinary Kriging interpolasyonu.
Yöntem: pykrige OrdinaryKriging — linear variogram (Surfer varsayılanı)
Çıktı: data/bvalue_kriging.png  →  Leaflet imageOverlay

Gereksinimler:
  pip install pykrige numpy matplotlib pillow scipy
"""

import json, sys, time
import numpy as np

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

try:
    from pykrige.ok import OrdinaryKriging
except ImportError:
    sys.exit('[!] pykrige kurulu degil: pip install pykrige')

INPUT       = 'data/bvalue_grid.json'
OUTPUT_PNG  = 'data/bvalue_kriging.png'
OUTPUT_META = 'data/bvalue_kriging_meta.json'

BOUNDS = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)

# Raster çözünürlüğü: 0.05° adım ~ 5 km
GRID_W = 400   # lon yönü: 25–45° / 400 = 0.05°/piksel
GRID_H = 180   # lat yönü: 34–43° / 180 = 0.05°/piksel

# b-değeri renk skalası: 0.5→kırmızı · 1.0→sarı · 1.5→yeşil (sabit)
B_LOW, B_HIGH = 0.5, 1.5
CMAP = LinearSegmentedColormap.from_list('bvalue_rdylgn', [
    (0.00, '#d73027'),   # b=0.5  kırmızı
    (0.25, '#fc8d59'),
    (0.50, '#fee08b'),   # b=1.0  sarı
    (0.75, '#91cf60'),
    (1.00, '#1a9850'),   # b=1.5  yeşil
])

# Variogram fit için alt örnekleme (pykrige N×N sistem çözer; 2000 yeterli)
SUBSAMPLE_FIT  = 2000
# Kriging tahmin işi için lokal pencere (execute_local ile)
USE_SUBSAMPLE_PREDICT = True  # True → daha hızlı; False → tam veri


def main():
    t0 = time.time()

    # ── Veri yükle ────────────────────────────────────────────────
    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)

    grid = data['grid']
    lats  = np.array([p['lat']  for p in grid], dtype=float)
    lons  = np.array([p['lon']  for p in grid], dtype=float)
    bvals = np.array([p['b']    for p in grid], dtype=float)

    print(f'[*] {len(grid)} nokta yüklendi')
    print(f'    b: {bvals.min():.3f} – {bvals.max():.3f}  |  ort: {bvals.mean():.3f}')

    # ── Variogram fit: alt örnekleme ──────────────────────────────
    np.random.seed(42)
    if len(grid) > SUBSAMPLE_FIT:
        idx = np.random.choice(len(grid), SUBSAMPLE_FIT, replace=False)
        lats_f = lats[idx]; lons_f = lons[idx]; bvals_f = bvals[idx]
        print(f'[*] Variogram fit için {len(idx)} nokta seçildi (rastgele)')
    else:
        lats_f, lons_f, bvals_f = lats, lons, bvals

    # ── Ordinary Kriging — linear variogram ───────────────────────
    print('[*] OrdinaryKriging başlıyor (linear variogram)...')
    OK = OrdinaryKriging(
        lons_f, lats_f, bvals_f,
        variogram_model='linear',
        verbose=False,
        enable_plotting=False,
        nlags=12,
        weight=True,
    )
    print(f'    Variogram fit: {time.time()-t0:.1f}s')

    # ── Output grid ───────────────────────────────────────────────
    grid_lons = np.linspace(BOUNDS['minlon'], BOUNDS['maxlon'], GRID_W)
    grid_lats = np.linspace(BOUNDS['maxlat'], BOUNDS['minlat'], GRID_H)

    print(f'[*] {GRID_W}×{GRID_H} grid interpolasyonu...')

    if USE_SUBSAMPLE_PREDICT:
        # Tahmin için daha büyük örnekleme (doğruluk/hız dengesi)
        N_PRED = min(len(grid), 5000)
        if N_PRED < len(grid):
            idx2 = np.random.choice(len(grid), N_PRED, replace=False)
            lats_p = lats[idx2]; lons_p = lons[idx2]; bvals_p = bvals[idx2]
        else:
            lats_p, lons_p, bvals_p = lats, lons, bvals
        print(f'    Tahmin için {N_PRED} nokta kullanılıyor...')
        OK2 = OrdinaryKriging(
            lons_p, lats_p, bvals_p,
            variogram_model='linear',
            verbose=False, enable_plotting=False,
            nlags=12, weight=True,
        )
        z, ss = OK2.execute('grid', grid_lons, grid_lats)
    else:
        z, ss = OK.execute('grid', grid_lons, grid_lats)

    print(f'    Kriging tamamlandı: {time.time()-t0:.1f}s')
    print(f'    Tahmin z: {z.min():.3f} – {z.max():.3f}')

    # ── RGBA raster üret ──────────────────────────────────────────
    z_norm = np.clip((z.data - B_LOW) / (B_HIGH - B_LOW), 0, 1)
    rgba   = (CMAP(z_norm) * 255).astype(np.uint8)
    rgba[:, :, 3] = 210  # sabit alpha

    img = Image.fromarray(rgba, 'RGBA')
    img.save(OUTPUT_PNG, optimize=True)
    print(f'[OK] PNG kaydedildi: {OUTPUT_PNG}  ({GRID_W}×{GRID_H} px)')

    # ── Meta JSON ─────────────────────────────────────────────────
    import datetime
    meta = {
        'generated' : datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'method'    : 'Ordinary Kriging · linear variogram · pykrige',
        'variogram' : 'linear',
        'source_pts': len(grid),
        'fit_pts'   : int(lons_f.shape[0]),
        'pred_pts'  : int(lons_p.shape[0]) if USE_SUBSAMPLE_PREDICT else len(grid),
        'grid_w'    : GRID_W,
        'grid_h'    : GRID_H,
        'b_min_pred': float(z.min()),
        'b_max_pred': float(z.max()),
        'b_norm'    : [B_LOW, B_HIGH],
        'bounds'    : BOUNDS,
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'[OK] Meta kaydedildi: {OUTPUT_META}')
    print(f'[*] Toplam süre: {time.time()-t0:.1f}s')


if __name__ == '__main__':
    main()
