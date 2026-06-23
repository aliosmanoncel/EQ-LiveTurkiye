"""
build_hazard_triangulation.py
hazard_grid.json → Delaunay triangülasyon + lineer interpolasyon → PNG imageOverlay
b-value ile aynı teknik: zoom bağımsız, Leaflet imageOverlay olarak yüklenir.

Çıktı:
  data/hazard_triangulation.png
  data/hazard_triangulation_meta.json
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

INPUT       = 'data/hazard_grid.json'
OUTPUT_PNG  = 'data/hazard_triangulation.png'
OUTPUT_META = 'data/hazard_triangulation_meta.json'

BOUNDS = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)
GRID_W, GRID_H = 500, 225
ALPHA = 210

# PGA renk skalası: mavi (düşük) → sarı → kırmızı (yüksek)
# 0 g → 0.40 g aralığı; Türkiye maks PGA ~0.4g (AFAD 2018)
PGA_LOW, PGA_HIGH = 0.0, 0.40

CMAP = LinearSegmentedColormap.from_list('hazard_pga', [
    (0.00, '#313695'),  # PGA~0.00g  koyu mavi   — düşük tehlike
    (0.20, '#4575b4'),  # PGA~0.08g
    (0.40, '#74add1'),  # PGA~0.16g  açık mavi
    (0.55, '#fee090'),  # PGA~0.22g  sarı
    (0.70, '#f46d43'),  # PGA~0.28g  turuncu
    (0.85, '#d73027'),  # PGA~0.34g  kırmızı
    (1.00, '#a50026'),  # PGA~0.40g+ koyu kırmızı — yüksek tehlike
])


def main():
    t0 = time.time()

    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)

    grid   = data['grid']
    lons   = np.array([p['lon'] for p in grid], dtype=float)
    lats   = np.array([p['lat'] for p in grid], dtype=float)
    pga    = np.array([p['pga'] for p in grid], dtype=float)

    print(f'[*] {len(grid)} hazard nokta yüklendi')
    print(f'    PGA: {pga.min():.4f} – {pga.max():.4f} g  |  ort: {pga.mean():.4f} g')

    print('[*] Delaunay triangülasyonu + lineer interpolasyon...')
    interp = LinearNDInterpolator(
        list(zip(lons, lats)), pga, fill_value=np.nan
    )

    grid_lons = np.linspace(BOUNDS['minlon'], BOUNDS['maxlon'], GRID_W)
    grid_lats = np.linspace(BOUNDS['maxlat'], BOUNDS['minlat'], GRID_H)
    LON, LAT  = np.meshgrid(grid_lons, grid_lats)
    z = interp(LON, LAT)

    n_valid = int(np.sum(~np.isnan(z)))
    print(f'    Geçerli piksel: {n_valid}/{z.size} ({100*n_valid/z.size:.1f}%)')
    print(f'    z PGA: {np.nanmin(z):.4f} – {np.nanmax(z):.4f} g')

    z_norm = np.clip((z - PGA_LOW) / (PGA_HIGH - PGA_LOW), 0, 1)
    rgba   = (CMAP(z_norm) * 255).astype(np.uint8)
    mask   = np.isnan(z)
    rgba[mask,  3] = 0
    rgba[~mask, 3] = ALPHA

    Image.fromarray(rgba, 'RGBA').save(OUTPUT_PNG, optimize=True)
    print(f'[OK] PNG: {OUTPUT_PNG}  ({GRID_W}×{GRID_H} px)')

    meta = {
        'generated'   : datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'method'      : 'Campbell (1981) GMPE · PGAmax · Delaunay triangülasyon',
        'source_pts'  : len(grid),
        'valid_px'    : n_valid,
        'total_px'    : int(z.size),
        'coverage_pct': round(100 * n_valid / z.size, 1),
        'grid_w'      : GRID_W,
        'grid_h'      : GRID_H,
        'pga_min_g'   : float(np.nanmin(z)),
        'pga_max_g'   : float(np.nanmax(z)),
        'pga_norm'    : [PGA_LOW, PGA_HIGH],
        'bounds'      : BOUNDS,
        'colormap'    : 'mavi(0g) → sarı(0.22g) → koyu kırmızı(≥0.4g)',
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'[OK] Meta: {OUTPUT_META}')
    print(f'[*] Toplam süre: {time.time()-t0:.1f}s')


if __name__ == '__main__':
    main()
