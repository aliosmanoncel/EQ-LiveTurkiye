"""
build_bvalue_grid.py
Gutenberg-Richter b-degeri grid haritasi — iki yontem:

  FC  Fixed Circle  (Oncel & Wyss 2000 — mevcut):
        Sabit R=100 km, N>=50 sart. Az sismik alanlarda bos.

  FN  Fixed Number  (ZMAP varsayilan — Wiemer 2001):
        Sabit N=50 en yakin olay, R degisken (adaptif).
        Her grid noktasi her zaman dolu; R_max ile buyuk daire sinirlanir.

Referanslar:
  Aki (1965) MLE: b = log10(e) / (mean(Mw) - Mc_eff)
  Utsu (1966) binom duzeltme: Mc_eff = Mc - 0.05
  Oncel & Wyss (2000) Fixed Area Method: R=100km, STEP~10km
  Wiemer (2001) ZMAP: Fixed Number, N=50, R_max=150km

Kullanim:
  python scripts/build_bvalue_grid.py                          # FC varsayilan
  python scripts/build_bvalue_grid.py --method fn              # Fixed Number
  python scripts/build_bvalue_grid.py --method fn --n 100      # N=100
  python scripts/build_bvalue_grid.py --method fc --r 150      # R=150 km
  python scripts/build_bvalue_grid.py --output data/bvalue_grid_fn.json --method fn
"""

import json, math, sys
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Sabitler ─────────────────────────────────────────────────────────
MC     = 3.0    # Tamamlılık buyuklugu (EMSC donemi)
DM     = 0.05   # Utsu (1966) binom duzeltmesi: Mc_eff = MC - DM
N_MIN  = 50     # FC: minimum N; FN: hedef N
R_KM   = 100.0  # FC: sabit yarıçap
R_MAX  = 200.0  # FN: maksimum R siniri (km) — buyuk bos alanlari sinirlar
STEP   = 0.09   # kaydırma adimi ~10 km
BOUNDS = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)

INPUT  = 'data/eq_historical.json'


def parse_args():
    args = sys.argv[1:]
    def get(flag, default):
        return type(default)(args[args.index(flag)+1]) if flag in args else default
    method     = get('--method',     'fc').lower()
    n_fixed    = get('--n',          N_MIN)
    r_fixed    = get('--r',          R_KM)
    output     = get('--output',     'data/bvalue_grid.json')
    year_start = get('--year_start', 1998)
    year_end   = get('--year_end',   2100)
    step       = get('--step',       STEP)
    mc         = get('--mc',         MC)
    minlat     = get('--minlat',     BOUNDS['minlat'])
    maxlat     = get('--maxlat',     BOUNDS['maxlat'])
    minlon     = get('--minlon',     BOUNDS['minlon'])
    maxlon     = get('--maxlon',     BOUNDS['maxlon'])
    src        = get('--src',        'EMSC')
    return method, n_fixed, r_fixed, output, year_start, year_end, step, mc, minlat, maxlat, minlon, maxlon, src


def haversine(la1, lo1, la2, lo2):
    R = 6371.0; r = math.pi / 180
    dl = (la2 - la1) * r; dlo = (lo2 - lo1) * r
    a = math.sin(dl/2)**2 + math.cos(la1*r)*math.cos(la2*r)*math.sin(dlo/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def aki_b(mags, mc, n_min):
    """Aki (1965) MLE b-degeri + Utsu (1966) binom duzeltmesi."""
    mc_eff = mc - DM
    m = [x for x in mags if x >= mc]
    if len(m) < n_min:
        return None, len(m), None
    mean_m = sum(m) / len(m)
    denom  = mean_m - mc_eff
    if denom <= 0:
        return None, len(m), None
    b = math.log10(math.e) / denom
    return round(b, 3), len(m), round(mean_m, 3)


# ── Fixed Circle (FC) ─────────────────────────────────────────────────
def compute_fc(events, lats, lons, r_km, n_min):
    """Sabit R=r_km dairesi icindeki olaylardan b-degeri."""
    grid = []
    skipped = 0
    deg_margin = r_km / 111.0 + 0.1

    for i, lat in enumerate(lats):
        if i % 5 == 0:
            pct = 100 * i // len(lats)
            print(f'    FC {pct}%  ({i}/{len(lats)} satır)', end='\r')
        for lon in lons:
            nearby = []
            for e in events:
                if abs(e['lat'] - lat) > deg_margin or abs(e['lon'] - lon) > deg_margin * 1.3:
                    continue
                d = haversine(lat, lon, e['lat'], e['lon'])
                if d <= r_km:
                    nearby.append(e.get('mag', 0))

            b, n, mean_m = aki_b(nearby, MC, n_min)
            if b is None:
                skipped += 1
                continue
            grid.append({'lat': lat, 'lon': lon, 'b': b, 'n': n, 'r': r_km})

    print()
    return grid, skipped


# ── Fixed Number (FN) — ZMAP yontemi ─────────────────────────────────
def compute_fn(events, lats, lons, n_fixed, r_max):
    """
    Her grid noktasi icin en yakin n_fixed olayi bul (adaptif R).
    R = n_fixed'inci olayın mesafesi.
    R > r_max ise nokta atlanır (cok az yerel sismisita).
    """
    grid = []
    skipped = 0

    # Olayları numpy olmadan basit tuple listesine cevir
    ev_tuples = [(e['lat'], e['lon'], e.get('mag', 0)) for e in events]

    for i, lat in enumerate(lats):
        if i % 5 == 0:
            pct = 100 * i // len(lats)
            print(f'    FN {pct}%  ({i}/{len(lats)} satır)', end='\r')
        for lon in lons:
            # Kaba on-eleme (hesap hizi icin)
            deg_margin = r_max / 111.0 + 0.5
            candidates = [
                (haversine(lat, lon, la, lo), mg)
                for la, lo, mg in ev_tuples
                if abs(la - lat) <= deg_margin and abs(lo - lon) <= deg_margin * 1.4
            ]
            # Mesafeye gore sirala
            candidates.sort(key=lambda x: x[0])

            if len(candidates) < n_fixed:
                skipped += 1
                continue

            r_adaptive = candidates[n_fixed - 1][0]  # N'inci olayin mesafesi
            if r_adaptive > r_max:
                skipped += 1
                continue

            mags = [mg for _, mg in candidates[:n_fixed]]
            b, n, mean_m = aki_b(mags, MC, n_fixed)
            if b is None:
                skipped += 1
                continue

            grid.append({
                'lat': lat,
                'lon': lon,
                'b'  : b,
                'n'  : n,
                'r'  : round(r_adaptive, 1),  # adaptif R (km)
            })

    print()
    return grid, skipped


def main():
    method, n_fixed, r_fixed, output, year_start, year_end, step, mc, minlat, maxlat, minlon, maxlon, src = parse_args()
    bounds = dict(minlat=minlat, maxlat=maxlat, minlon=minlon, maxlon=maxlon)
    print(f'[*] Yontem: {"Fixed Circle (FC)" if method=="fc" else "Fixed Number (FN)"}'
          f'  |  R={r_fixed} km  N={n_fixed}  step={step}°  Mc={mc}'
          f'  |  {year_start}–{year_end}  |  Src={src}'
          f'  |  Bounds: {minlat}-{maxlat}N {minlon}-{maxlon}E')

    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)

    events = [e for e in data['events']
              if e.get('src') == src
              and e.get('mag', 0) >= mc
              and year_start <= int(e.get('time', '1900')[:4]) <= year_end
              and minlat <= e.get('lat', 0) <= maxlat
              and minlon <= e.get('lon', 0) <= maxlon]
    print(f'[*] {len(events)} olay yuklendi ({src}, mag>={mc}, {year_start}–{year_end})')

    # Grid
    lats, lons = [], []
    cur = minlat
    while cur <= maxlat + 1e-9:
        lats.append(round(cur, 4)); cur += step
    cur = minlon
    while cur <= maxlon + 1e-9:
        lons.append(round(cur, 4)); cur += step
    print(f'[*] Grid: {len(lats)}x{len(lons)} = {len(lats)*len(lons)} nokta')

    if method == 'fc':
        grid, skipped = compute_fc(events, lats, lons, r_fixed, n_fixed)
        method_label = f'Fixed Circle | R={r_fixed} km | N_min={n_fixed} | Oncel & Wyss (2000) | {year_start}-{year_end}'
    else:
        grid, skipped = compute_fn(events, lats, lons, n_fixed, R_MAX)
        method_label = f'Fixed Number | N={n_fixed} | R_max={R_MAX} km | ZMAP (Wiemer 2001) | {year_start}-{year_end}'

    print(f'[*] Haritlanan: {len(grid)} | Atlanan: {skipped}')

    if not grid:
        print('[!] Hicbir nokta kriterleri gecemedi.'); return

    b_vals = [p['b'] for p in grid]
    print(f'[*] b: {min(b_vals):.3f} – {max(b_vals):.3f}  ort={sum(b_vals)/len(b_vals):.3f}')

    all_mags = [e.get('mag', 0) for e in events if e.get('mag', 0) >= mc]
    b_region, n_region, _ = aki_b(all_mags, mc, n_fixed)
    print(f'[*] Bolge b = {b_region}  (N={n_region})')

    B_LOW, B_HIGH = 0.5, 1.5
    for p in grid:
        w = 1.0 - (p['b'] - B_LOW) / (B_HIGH - B_LOW)
        p['w'] = round(max(0.0, min(1.0, w)), 4)

    out = {
        'generated'   : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'      : f'{src} {year_start}-{year_end} | Aki (1965) MLE + Utsu (1966)',
        'method'      : method_label,
        'train_period': [year_start, year_end],
        'bounds'      : bounds,
        'b_region'    : b_region,
        'b_min'       : min(b_vals),
        'b_max'       : max(b_vals),
        'count'       : len(grid),
        'grid'        : grid,
    }
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'[OK] Kaydedildi: {output}')


if __name__ == '__main__':
    main()
