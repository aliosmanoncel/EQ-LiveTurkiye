"""
build_hazard_grid.py
eq_annual.json verisinden basitleştirilmiş PGA tehlike grid'i üretir.
Yöntem: Boore-Atkinson 2008 (BA08) GMPE basitleştirilmiş formu
        Her grid noktasına 100 km içindeki tüm depremlerin
        PGA katkısı toplanır (SRSS değil, maksimum seçilir).

Kullanım:
  python scripts/build_hazard_grid.py
  python scripts/build_hazard_grid.py --bounds 33 23 45 48 --step 0.25
"""

import json
import math
import sys
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Argümanlar ────────────────────────────────────────────────────────
def parse_args():
    args = sys.argv[1:]
    def get(flag, default):
        if flag in args:
            i = args.index(flag)
            return type(default)(args[i+1])
        return default
    # Grid sınırları (minlat maxlat minlon maxlon)
    minlat = get('--minlat', 34.0)
    maxlat = get('--maxlat', 43.0)
    minlon = get('--minlon', 25.0)
    maxlon = get('--maxlon', 45.0)
    step   = get('--step',  0.25)
    inp    = get('--input',  'data/eq_annual.json')
    out    = get('--output', 'data/hazard_grid.json')
    return minlat, maxlat, minlon, maxlon, step, inp, out

# ── Haversine mesafe (km) ─────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    d2r = math.pi / 180
    dlat = (lat2 - lat1) * d2r
    dlon = (lon2 - lon1) * d2r
    a = math.sin(dlat/2)**2 + math.cos(lat1*d2r)*math.cos(lat2*d2r)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# ── Campbell (1981) basitleştirilmiş GMPE ────────────────────────────
# Referans: Campbell (1981), Bulunts. & Seism. GMPE
# ln(PGA[g]) = C1 + C2*Mw + C3*ln(R + C4*exp(C5*Mw))
# Kalibre: Mw=6 R=50km → ~0.04g, Mw=7 R=10km → ~0.3g
C1   = -4.141
C2   =  0.868
C3   = -1.09
C4   =  0.0606
C5   =  0.700
R_MAX = 200.0  # etki yarıçapı (km)
MW_MIN = 3.0   # küçük depremler ihmal

def gmpe_pga(mw, r_km, dep_km=10.0):
    """PGA (g cinsinden) döndürür — Campbell (1981)."""
    r_eff = r_km + C4 * math.exp(C5 * mw)
    if r_eff < 1.0:
        r_eff = 1.0
    ln_pga = C1 + C2 * mw + C3 * math.log(r_eff)
    return math.exp(ln_pga)

# ── Ana akış ─────────────────────────────────────────────────────────
def main():
    minlat, maxlat, minlon, maxlon, step, inp, out = parse_args()

    # Veriyi yükle
    with open(inp, encoding='utf-8') as f:
        data = json.load(f)
    events = data.get('events', [])
    print(f"[*] {len(events)} deprem yüklendi ({inp})")

    # Mw alanı yoksa mag kullan
    for e in events:
        if 'mw' not in e or e['mw'] is None:
            e['mw'] = e.get('mag', 0)

    # Grid noktaları oluştur
    lats = []
    cur = minlat
    while cur <= maxlat + 1e-9:
        lats.append(round(cur, 4))
        cur += step
    lons = []
    cur = minlon
    while cur <= maxlon + 1e-9:
        lons.append(round(cur, 4))
        cur += step

    total = len(lats) * len(lons)
    print(f"[*] Grid: {len(lats)} lat × {len(lons)} lon = {total} nokta")

    grid = []
    for i, lat in enumerate(lats):
        if i % 10 == 0:
            print(f"    {i}/{len(lats)} satır…")
        for lon in lons:
            pga_max = 0.0
            pga_sum = 0.0
            n_contrib = 0
            for e in events:
                mw = e['mw']
                if mw < MW_MIN:
                    continue  # küçük depremler ihmal
                r = haversine(lat, lon, e['lat'], e['lon'])
                if r > R_MAX:
                    continue
                dep = e.get('dep', 10.0) or 10.0
                pga = gmpe_pga(mw, r, dep)
                if pga > pga_max:
                    pga_max = pga
                pga_sum += pga
                n_contrib += 1
            if pga_max > 0:
                grid.append({
                    'lat': lat,
                    'lon': lon,
                    'pga': round(pga_max, 5),     # maksimum PGA (g)
                    'n'  : n_contrib,
                })

    # PGA normalize et (leaflet heatLayer için 0-1)
    if grid:
        max_pga = max(p['pga'] for p in grid)
        for p in grid:
            p['w'] = round(p['pga'] / max_pga, 4)
    else:
        max_pga = 0

    result = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'   : 'EMSC eq_annual.json + BA08 simplified GMPE',
        'method'   : 'PGA_max within 150 km, Vs30=760 m/s',
        'bounds'   : {'minlat': minlat, 'maxlat': maxlat, 'minlon': minlon, 'maxlon': maxlon},
        'step_deg' : step,
        'max_pga_g': round(max_pga, 5),
        'count'    : len(grid),
        'grid'     : grid,
    }

    with open(out, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))

    print(f"[✓] Kaydedildi: {out} ({len(grid)} nokta, max PGA={max_pga:.4f} g)")

if __name__ == '__main__':
    main()
