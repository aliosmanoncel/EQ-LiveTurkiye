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
# Staircase katalog birlestirme (referans + 0.5 muhafazakar duzeltme):
#   1965-1979 ISC  : M>=4.5
#   1980-1989 ISC  : M>=4.0
#   1990-1997 ISC  : M>=3.5
#   1998-2026 EMSC : M>=3.0
# Aki MLE Mc = katalogdaki en dusuk esik = 3.0, Utsu: Mc_eff = 2.95
MC     = 3.0    # Aki MLE esigi (EMSC donemi Mc)
DM     = 0.05   # Utsu (1966) binom duzeltmesi
START_YEAR = 1900
# Donem bazli staircase esikleri — butunlesik katalog (1900-2026)
STAIRCASE = [
    (1900, 1965, 5.5),   # Pre-WWSSN: yalniz buyuk olaylar tam
    (1965, 1980, 4.5),   # WWSSN tam operasyonel
    (1980, 1990, 4.0),   # global ag yogunlasma
    (1990, 1998, 3.5),   # dijital ag gecisi
    (1998, 2100, 3.0),   # EMSC genis bant
]
N_MIN  = 200    # minimum olay sayisi kriteri
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

    # b-degeri icin EMSC 1998-2026 (homojen Mc=3.0)
    # Filtre: orijinal mag>=MC (Scordilis ML/MD->Mw donusumu kucuk Mw uretir,
    #         mw filtresinde 66k olay duser ve mean(Mw) yapay yukselir)
    # Aki hesabi: mw (Scordilis donusturulmus) kullan, yoksa mag
    events = [e for e in data['events']
              if e.get('src') == 'EMSC'
              and e.get('mag', 0) >= MC]
    print(f'[*] {len(events)} olay yuklendi (EMSC 1998-2026, mag>={MC}, orijinal filtre)')
    mw_vals = [(e.get('mw') or e.get('mag', 0)) for e in events]
    print(f'    mean(Mw)={sum(mw_vals)/len(mw_vals):.3f}  aralik={min(mw_vals):.1f}-{max(mw_vals):.1f}')

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
                    nearby_mw.append(e.get('mag', 0))  # orijinal mag (Scordilis bias yok)

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

    # Tum Turkiye b-degeri
    all_mags = [e.get('mag', 0) for e in events if e.get('mag', 0) >= MC]
    b_turkey, n_turkey = aki_b(all_mags, MC)
    print(f'[*] Tum Turkiye b-degeri: {b_turkey}  (N={n_turkey})')

    # Sabit normalizasyon: 0.5=kirmizi, 1.0=sari, 1.5=yesil
    B_LOW, B_HIGH = 0.5, 1.5
    for p in grid:
        w = 1.0 - (p['b'] - B_LOW) / (B_HIGH - B_LOW)
        p['w'] = round(max(0.0, min(1.0, w)), 4)  # 0-1 araligina kist

    out = {
        'generated'  : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source'     : 'EMSC 1998-2026 | Aki (1965) MLE + Utsu (1966)',
        'method'     : f'Mc={MC}, N_min={N_MIN}, R={R_KM} km, norm=[0.5-1.5]',
        'b_turkey'   : b_turkey,
        'b_min'      : b_min,
        'b_max'      : b_max,
        'count'      : len(grid),
        'grid'       : grid,
    }
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'[OK] Kaydedildi: {OUTPUT} ({len(grid)} nokta)')

if __name__ == '__main__':
    main()
