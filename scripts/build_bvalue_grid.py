"""
build_bvalue_grid.py
eq_historical.json verisinden Gutenberg-Richter b-degeri grid'i uretir.
Yontem: Aki (1965) maksimum olabilirlik tahmini
  b = log10(e) / (mean(Mw) - Mc)
Kriter: N >= 50 olmayan grid noktasi haritalanmaz.

Kullanim:
  python scripts/build_bvalue_grid.py
"""

import json, math, sys
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INPUT  = 'data/eq_historical.json'
OUTPUT = 'data/bvalue_grid.json'
# Katalog birlestirme yontemi:
#   1965-1997 ISC  : M>=4.5  (WWSSN tam operasyonel)
#   1998-2026 EMSC : M>=3.0  (dijital genis bant)
#   → birlesik katalog, Aki (1965) MLE b-degeri Mc=3.0 ile
# Utsu (1966) binom duzeltmesi: DM=0.05 → Mc_eff = 3.0 - 0.05 = 2.95
MC     = 3.0    # b-degeri Aki MLE esigi
DM     = 0.05   # Utsu (1966) binom duzeltmesi
MC_ISC = 4.5    # ISC donemi (1965-1997) tamamlilik esigi
START_YEAR = 1965
N_MIN  = 100    # minimum olay sayisi kriteri
R_KM   = 150.0  # arama yaricapi (km)
STEP   = 0.5    # grid adimi (derece) — b-degeri icin daha kaba yeterli
BOUNDS = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)

def haversine(la1, lo1, la2, lo2):
    R = 6371.0; r = math.pi/180
    dl = (la2-la1)*r; dlo = (lo2-lo1)*r
    a = math.sin(dl/2)**2 + math.cos(la1*r)*math.cos(la2*r)*math.sin(dlo/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def aki_b(mags, mc):
    """Aki (1965) MLE b-degeri + Utsu (1966) binom duzeltmesi.
    b = log10(e) / (mean(Mw) - (Mc - DM))
    DM = 0.05: katalog 0.1 birimlik araliklar -> efektif Mc = Mc - DM
    """
    mc_eff = mc - DM  # 3.0 - 0.05 = 2.95
    m = [m for m in mags if m >= mc]
    if len(m) < N_MIN:
        return None, len(m)
    mean_m = sum(m) / len(m)
    denom  = mean_m - mc_eff
    if denom <= 0:
        return None, len(m)
    b = math.log10(math.e) / denom
    return round(b, 3), len(m)

def main():
    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)

    # Katalog birlestirme:
    #   ISC  1965-1997 : M>=4.5
    #   EMSC 1998-2026 : M>=3.0
    events = []
    for e in data['events']:
        yr  = int(e['time'][:4])
        mw  = e.get('mw') or e.get('mag', 0)
        src = e.get('src', '')
        if yr < START_YEAR:
            continue
        if src == 'ISC'  and mw >= MC_ISC:
            events.append(e)
        elif src == 'EMSC' and mw >= MC:
            events.append(e)
    n_isc  = sum(1 for e in events if e.get('src') == 'ISC')
    n_emsc = sum(1 for e in events if e.get('src') == 'EMSC')
    print(f'[*] {len(events)} olay yuklendi (katalog birlestirme, {START_YEAR}-2026)')
    print(f'    ISC 1965-1997 M>={MC_ISC}: {n_isc} | EMSC 1998-2026 M>={MC}: {n_emsc}')

    # Grid olustur
    lats, lons = [], []
    cur = BOUNDS['minlat']
    while cur <= BOUNDS['maxlat'] + 1e-9:
        lats.append(round(cur, 4)); cur += STEP
    cur = BOUNDS['minlon']
    while cur <= BOUNDS['maxlon'] + 1e-9:
        lons.append(round(cur, 4)); cur += STEP

    print(f'[*] Grid: {len(lats)} x {len(lons)} = {len(lats)*len(lons)} nokta')

    grid = []
    skipped = 0
    for i, lat in enumerate(lats):
        if i % 5 == 0:
            print(f'    {i}/{len(lats)} satir...')
        for lon in lons:
            nearby_mw = []
            for e in events:
                if abs(e['lat']-lat) > 1.5 or abs(e['lon']-lon) > 2.5:
                    continue  # hizli on-eleme
                d = haversine(lat, lon, e['lat'], e['lon'])
                if d <= R_KM:
                    nearby_mw.append(e.get('mw') or e.get('mag', 0))

            b, n = aki_b(nearby_mw, MC)
            if b is None:
                skipped += 1
                continue

            grid.append({
                'lat': lat,
                'lon': lon,
                'b'  : b,
                'n'  : n,
            })

    print(f'[*] Haritlanan: {len(grid)} nokta | Atlanan (N<{N_MIN}): {skipped}')

    if not grid:
        print('[!] Hicbir nokta N>=50 kriterini gecemedi. R veya STEP artir.')
        return

    b_vals = [p['b'] for p in grid]
    b_min, b_max = min(b_vals), max(b_vals)
    print(f'[*] b aralik: {b_min:.3f} – {b_max:.3f}  |  Ort: {sum(b_vals)/len(b_vals):.3f}')

    # Normalize: dusuk b (yuksek stres) -> yuksek w (kirmizi)
    # b dusukse tehlike yuksek -> renk yogun olmali
    b_range = b_max - b_min or 1.0
    for p in grid:
        p['w'] = round(1.0 - (p['b'] - b_min) / b_range, 4)  # ters: dusuk b = kirmizi

    out = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'   : 'ISC+EMSC eq_historical | Aki (1965) MLE b-degeri',
        'method'   : f'Mc={MC}, N_min={N_MIN}, R={R_KM} km',
        'b_min'    : b_min,
        'b_max'    : b_max,
        'count'    : len(grid),
        'grid'     : grid,
    }
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'[OK] Kaydedildi: {OUTPUT} ({len(grid)} nokta)')

if __name__ == '__main__':
    main()
