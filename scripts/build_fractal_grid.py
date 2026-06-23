"""
build_fractal_grid.py
Grassberger-Procaccia korelasyon boyutu (D_c) grid haritasi.
ZMAP7 @fractal/dofdim.m yontemiyle esit:
  C(r) = (cift sayisi <= r) / toplam cift sayisi
  D_c  = d[log C(r)] / d[log r]  (scaling range icinde lineer regresyon)

Referans: Grassberger & Procaccia (1983), ZMAP7 (Wiemer 2001)

Parametreler (b-degeri ile ayni pencere):
  R_KM   = 100   km  yarıçap
  N_MIN  = 50    minimum olay sayisi
  STEP   = 0.09° kaydirma adimi (~10 km)

Cikctilar:
  data/fractal_grid.json      — grid noktalari (lat, lon, dc, n)
  data/fractal_triangulation.png
  data/fractal_triangulation_meta.json

Gereksinimler:
  pip install numpy scipy matplotlib pillow
"""

import json, sys, time, datetime, math
import numpy as np
from scipy.stats import linregress
from scipy.interpolate import LinearNDInterpolator
import matplotlib
matplotlib.use('Agg')
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Parametreler ───────────────────────────────────────────────────────────────
INPUT_CAT   = 'data/eq_historical.json'
OUT_GRID    = 'data/fractal_grid.json'
OUT_PNG     = 'data/fractal_triangulation.png'
OUT_META    = 'data/fractal_triangulation_meta.json'

MC     = 3.0
N_MIN  = 50
R_KM   = 100.0
STEP   = 0.09
BOUNDS = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)

# Korelasyon integrali için mesafe bölmeleri (km)
# Scaling range: depolasyon mesafesi rad – doygunluk mesafesi ras
N_BINS = 25         # log-esit r degerleri
R_MIN  = 5.0        # km — küçük skala eşiği (katalog hataları)
R_MAX  = 80.0       # km — doygunluk eşiği (R_KM'nin alt sınırı)

# Renk skalası: D_c 0.5 (nokta kümelenme) → 2.0 (düzlem dolumu)
DC_LOW, DC_HIGH = 0.5, 2.0
CMAP = LinearSegmentedColormap.from_list('fractal_viridis', [
    (0.00, '#440154'),   # Dc~0.5  koyu mor  — güçlü kümelenme
    (0.25, '#3b528b'),   # Dc~0.9
    (0.50, '#21918c'),   # Dc~1.25 teal
    (0.75, '#5ec962'),   # Dc~1.6  yeşil
    (1.00, '#fde725'),   # Dc~2.0  sarı     — homojen dağılım
])

GRID_W, GRID_H = 500, 225
ALPHA = 210

# ── Yardımcı fonksiyonlar ──────────────────────────────────────────────────────
DEG2RAD = math.pi / 180.0
R_EARTH  = 6371.0

def haversine_vec(lat0, lon0, lats, lons):
    """Tek merkez → nokta dizisi arası haversine (km), numpy."""
    dlat = (lats - lat0) * DEG2RAD
    dlon = (lons - lon0) * DEG2RAD
    a = np.sin(dlat/2)**2 + math.cos(lat0*DEG2RAD)*np.cos(lats*DEG2RAD)*np.sin(dlon/2)**2
    return R_EARTH * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def haversine_pair(lat1, lon1, lat2, lon2):
    """Tek çift haversine (km)."""
    dlat = (lat2 - lat1) * DEG2RAD
    dlon = (lon2 - lon1) * DEG2RAD
    a = (math.sin(dlat/2)**2
         + math.cos(lat1*DEG2RAD)*math.cos(lat2*DEG2RAD)*math.sin(dlon/2)**2)
    return R_EARTH * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def correlation_dimension(lats_ev, lons_ev):
    """
    Grassberger-Procaccia D_c hesabi.
    Giriş: olay konumlari (numpy arrays, derece)
    Cikis: D_c (float) veya None
    """
    n = len(lats_ev)
    if n < N_MIN:
        return None

    # Tüm çift mesafeleri — C(r) için
    # n*(n-1)/2 çift
    dists = []
    for i in range(n):
        for j in range(i+1, n):
            d = haversine_pair(lats_ev[i], lons_ev[i], lats_ev[j], lons_ev[j])
            if d > 0:
                dists.append(d)
    dists = np.array(dists, dtype=float)
    if len(dists) == 0:
        return None

    # Log-eşit r dizisi
    r_bins = np.logspace(np.log10(max(R_MIN, dists.min()+0.01)),
                         np.log10(min(R_MAX, dists.max())),
                         N_BINS)

    # C(r): r'den küçük çift oranı
    total_pairs = len(dists)
    cr = np.array([np.sum(dists < r) / total_pairs for r in r_bins])

    # Sıfır C(r) değerlerini dışla (log alamayız)
    mask = cr > 0
    if mask.sum() < 4:
        return None

    log_r  = np.log10(r_bins[mask])
    log_cr = np.log10(cr[mask])

    # Lineer regresyon: eğim = D_c
    slope, intercept, r_val, p_val, stderr = linregress(log_r, log_cr)

    if r_val**2 < 0.85:   # zayıf fit → güvenilmez
        return None

    dc = round(float(slope), 3)
    return dc if 0.1 <= dc <= 3.5 else None


# ── Ana hesap ─────────────────────────────────────────────────────────────────
def main():
    t0 = time.time()

    # Katalog yükle
    with open(INPUT_CAT, encoding='utf-8') as f:
        data = json.load(f)

    # b-değeri ile aynı filtre: EMSC 1998-2026, mag>=MC
    events = [e for e in data['events']
              if e.get('src') == 'EMSC' and e.get('mag', 0) >= MC]
    print(f'[*] {len(events)} olay yüklendi (EMSC, mag>={MC})')

    ev_lat = np.array([e['lat'] for e in events])
    ev_lon = np.array([e['lon'] for e in events])

    # Hız için kabataslak lon/lat filtresi (R~100km → ~1° marj)
    DEG_MARGIN = R_KM / 111.0 + 0.2

    # Grid noktaları
    lat_vals = np.arange(BOUNDS['minlat'], BOUNDS['maxlat'] + STEP*0.5, STEP)
    lon_vals = np.arange(BOUNDS['minlon'], BOUNDS['maxlon'] + STEP*0.5, STEP)
    total_nodes = len(lat_vals) * len(lon_vals)
    print(f'[*] Grid: {len(lat_vals)}×{len(lon_vals)} = {total_nodes} aday nokta')

    results = []
    skipped_n = 0
    skipped_fit = 0
    node_count  = 0
    log_interval = max(1, total_nodes // 20)

    for lat in lat_vals:
        # Kabataslak lat filtresi
        lat_mask = np.abs(ev_lat - lat) <= DEG_MARGIN
        sub_lat = ev_lat[lat_mask]
        sub_lon = ev_lon[lat_mask]

        for lon in lon_vals:
            node_count += 1

            # Kabataslak lon filtresi
            lon_mask = np.abs(sub_lon - lon) <= DEG_MARGIN
            cand_lat = sub_lat[lon_mask]
            cand_lon = sub_lon[lon_mask]

            if len(cand_lat) < N_MIN:
                skipped_n += 1
                continue

            # Kesin haversine filtresi
            d_km = haversine_vec(lat, lon, cand_lat, cand_lon)
            in_r = d_km <= R_KM
            ev_lats_r = cand_lat[in_r]
            ev_lons_r = cand_lon[in_r]
            n = int(in_r.sum())

            if n < N_MIN:
                skipped_n += 1
                continue

            # D_c hesapla
            dc = correlation_dimension(ev_lats_r, ev_lons_r)

            if dc is None:
                skipped_fit += 1
                continue

            results.append({'lat': round(lat, 4), 'lon': round(lon, 4),
                            'dc': dc, 'n': n})

            if node_count % log_interval == 0:
                pct = 100 * node_count / total_nodes
                elapsed = time.time() - t0
                eta = elapsed / node_count * (total_nodes - node_count)
                print(f'    {pct:.0f}%  tamamlandı  |  {len(results)} nokta  |  '
                      f'geçen: {elapsed:.0f}s  tahmini kalan: {eta:.0f}s')

    print(f'\n[*] {len(results)} nokta hesaplandı  '
          f'(N<{N_MIN}: {skipped_n}  zayıf fit: {skipped_fit})')
    dc_vals = [r['dc'] for r in results]
    print(f'    D_c: {min(dc_vals):.3f} – {max(dc_vals):.3f}  |  '
          f'ort: {sum(dc_vals)/len(dc_vals):.3f}')

    # ── JSON kaydet ───────────────────────────────────────────────
    out = {
        'generated' : datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'method'    : 'Grassberger-Procaccia korelasyon boyutu (D_c)',
        'reference' : 'Grassberger & Procaccia (1983); ZMAP7 dofdim.m (Wiemer 2001)',
        'params'    : {'R_km': R_KM, 'N_min': N_MIN, 'step_deg': STEP,
                       'Mc': MC, 'r_min_km': R_MIN, 'r_max_km': R_MAX,
                       'r2_threshold': 0.85},
        'count'     : len(results),
        'grid'      : results,
    }
    with open(OUT_GRID, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)
    print(f'[OK] Grid kaydedildi: {OUT_GRID}')

    # ── Triangülasyon PNG ─────────────────────────────────────────
    print('[*] Delaunay triangülasyon + PNG üretimi...')
    lons_g = np.array([r['lon'] for r in results])
    lats_g = np.array([r['lat'] for r in results])
    dc_g   = np.array([r['dc']  for r in results])

    interp = LinearNDInterpolator(list(zip(lons_g, lats_g)), dc_g, fill_value=np.nan)

    grid_lons = np.linspace(BOUNDS['minlon'], BOUNDS['maxlon'], GRID_W)
    grid_lats = np.linspace(BOUNDS['maxlat'], BOUNDS['minlat'], GRID_H)
    LON, LAT  = np.meshgrid(grid_lons, grid_lats)
    z = interp(LON, LAT)

    z_norm = np.clip((z - DC_LOW) / (DC_HIGH - DC_LOW), 0, 1)
    rgba   = (CMAP(z_norm) * 255).astype(np.uint8)
    mask   = np.isnan(z)
    rgba[mask,  3] = 0
    rgba[~mask, 3] = ALPHA

    Image.fromarray(rgba, 'RGBA').save(OUT_PNG, optimize=True)
    print(f'[OK] PNG kaydedildi: {OUT_PNG}  ({GRID_W}×{GRID_H} px)')

    valid_px = int(np.sum(~mask))
    meta = {
        'generated'   : datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'method'      : 'Grassberger-Procaccia D_c · Delaunay triangülasyon',
        'source_pts'  : len(results),
        'valid_px'    : valid_px,
        'total_px'    : int(z.size),
        'coverage_pct': round(100 * valid_px / z.size, 1),
        'grid_w'      : GRID_W,
        'grid_h'      : GRID_H,
        'dc_min'      : float(np.nanmin(z)),
        'dc_max'      : float(np.nanmax(z)),
        'dc_norm'     : [DC_LOW, DC_HIGH],
        'bounds'      : BOUNDS,
        'colormap'    : 'Viridis: mor (Dc=0.5 kümelenme) → sarı (Dc=2.0 düzlem dolumu)',
    }
    with open(OUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'[OK] Meta kaydedildi: {OUT_META}')
    print(f'[*] Toplam süre: {time.time()-t0:.1f}s')


if __name__ == '__main__':
    main()
