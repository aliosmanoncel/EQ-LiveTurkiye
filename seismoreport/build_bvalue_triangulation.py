"""
build_bvalue_triangulation.py
b-değeri noktalarından Delaunay triangülasyonu ile lineer interpolasyon.
Yöntem: scipy.interpolate.LinearNDInterpolator
  → Surfer "Triangulation with Linear Interpolation" ile eşdeğer
  → Yalnızca mevcut nokta üçgenleri içinde tahmin yapar
  → N<N_MIN nedeniyle boş kalan alanlar şeffaf kalır (NaN → alpha=0)

Çıktı:
  data/bvalue_triangulation.png  — Leaflet imageOverlay
  data/bvalue_triangulation_meta.json

Gereksinimler:
  pip install scipy numpy matplotlib pillow
"""

import json, sys, time, datetime
import numpy as np

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import matplotlib
matplotlib.use('Agg')
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
from scipy.interpolate import LinearNDInterpolator

def _parse():
    args = sys.argv[1:]
    def get(f, d): return args[args.index(f)+1] if f in args else d
    return (get('--input',  'data/bvalue_grid.json'),
            get('--output', 'data/bvalue_triangulation.png'),
            get('--meta',   'data/bvalue_triangulation_meta.json'),
            get('--label',  'FC'))
INPUT, OUTPUT_PNG, OUTPUT_META, LABEL = _parse()

DEFAULT_BOUNDS = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)
GRID_W = 500
GRID_H = 225

# B_LOW / B_HIGH: main() içinde P10–P90 adaptif olarak hesaplanıyor
CMAP = LinearSegmentedColormap.from_list('bvalue_rdylgn', [
    (0.00, '#d73027'),
    (0.25, '#fc8d59'),
    (0.50, '#fee08b'),
    (0.75, '#91cf60'),
    (1.00, '#1a9850'),
])

ALPHA = 210  # raster saydamlığı (0–255)


def main():
    t0 = time.time()

    # ── Veri yükle ────────────────────────────────────────────────
    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)

    grid  = data['grid']
    lons  = np.array([p['lon'] for p in grid], dtype=float)
    lats  = np.array([p['lat'] for p in grid], dtype=float)
    bvals = np.array([p['b']   for p in grid], dtype=float)
    nvals = np.array([p['n']   for p in grid], dtype=int)

    # Bounds: JSON'dan oku (varsa), yoksa DEFAULT_BOUNDS
    BOUNDS = data.get('bounds', DEFAULT_BOUNDS)
    # Aspect-ratio'ya göre çözünürlük
    dlon = BOUNDS['maxlon'] - BOUNDS['minlon']
    dlat = BOUNDS['maxlat'] - BOUNDS['minlat']
    ratio = dlon / dlat if dlat > 0 else 2.0
    gw = max(200, min(800, int(GRID_H * ratio)))
    gh = GRID_H

    print(f'[*] {len(grid)} nokta yüklendi (N≥50 kriteri geçmiş)')
    print(f'    b: {bvals.min():.3f} – {bvals.max():.3f}  |  ort: {bvals.mean():.3f}  std: {bvals.std():.3f}')
    print(f'    N aralığı: {nvals.min()} – {nvals.max()}')
    print(f'    Bounds: {BOUNDS}  |  Grid: {gw}×{gh}')

    # Renk skalasi: P10-P90 adaptif (sabit 0.5-1.5 yerine)
    B_LOW  = float(np.percentile(bvals, 10))
    B_HIGH = float(np.percentile(bvals, 90))
    print(f'    Renk skala: P10={B_LOW:.3f} – P90={B_HIGH:.3f}  (adaptif)')

    print('[*] Delaunay triangülasyonu + lineer interpolasyon...')
    interp = LinearNDInterpolator(
        list(zip(lons, lats)),
        bvals,
        fill_value=np.nan
    )

    grid_lons = np.linspace(BOUNDS['minlon'], BOUNDS['maxlon'], gw)
    grid_lats = np.linspace(BOUNDS['maxlat'], BOUNDS['minlat'], gh)
    LON, LAT  = np.meshgrid(grid_lons, grid_lats)

    z = interp(LON, LAT)

    n_valid = np.sum(~np.isnan(z))
    n_total = z.size
    print(f'    Tamamlandı: {time.time()-t0:.1f}s')
    print(f'    Geçerli piksel: {n_valid}/{n_total} ({100*n_valid/n_total:.1f}%)')
    print(f'    z (geçerli): {np.nanmin(z):.3f} – {np.nanmax(z):.3f}')

    # ── RGBA raster ───────────────────────────────────────────────
    z_norm = np.clip((z - B_LOW) / (B_HIGH - B_LOW), 0, 1)
    rgba   = (CMAP(z_norm) * 255).astype(np.uint8)

    # NaN olan pikselleri şeffaf yap
    mask = np.isnan(z)
    rgba[mask, 3] = 0      # alpha=0 → şeffaf
    rgba[~mask, 3] = ALPHA  # veri olan pikseller yarı saydam

    img = Image.fromarray(rgba, 'RGBA')
    img.save(OUTPUT_PNG, optimize=True)
    print(f'[OK] PNG kaydedildi: {OUTPUT_PNG}  ({gw}×{gh} px)')

    meta = {
        'generated'  : datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'method'     : 'Delaunay Triangulation + Linear Interpolation · scipy',
        'source_pts' : len(grid),
        'valid_px'   : int(n_valid),
        'total_px'   : int(n_total),
        'coverage_pct': round(100 * n_valid / n_total, 1),
        'grid_w'     : gw,
        'grid_h'     : gh,
        'b_min_pred' : float(np.nanmin(z)),
        'b_max_pred' : float(np.nanmax(z)),
        'b_norm'     : [round(B_LOW,3), round(B_HIGH,3)],
        'b_norm_method': 'P10-P90 adaptif',
        'bounds'     : BOUNDS,
        'note'       : 'N<50 nedeniyle veri olmayan alanlar seffaf (NaN->alpha=0)',
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'[OK] Meta kaydedildi: {OUTPUT_META}')
    print(f'[*] Toplam süre: {time.time()-t0:.1f}s')


if __name__ == '__main__':
    main()
