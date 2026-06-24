"""
build_bvalue_adaptive.py
Türkiye Geneli Adaptif b-Değeri Grid Haritası
Öncel (2026) — Değişken Tarama Yarıçapı Modeli

3 Aşamalı Metodoloji:
  Aşama 1 — Sismisite Yoğunluk Haritası
              Her grid noktası için D_km=50 km içindeki M>=Mc_dens olay sayısı.
              Zon sınırı PGA'dan bağımsız → circularity riski yok.

  Aşama 2 — Adaptif R Seçimi (Öncel 2026)
              Yüksek yoğunluk  (>= THR_HIGH) → R_SMALL = 20 km  dR=5 km
                  Kırmızı zon: KAFZ, DAFZ, Batı Anadolu fay/graben sistemi,
                               Ege Genişleme Bölgesi, Doğu Anadolu'daki aktif segmentler
              Orta yoğunluk   (>= THR_MID)  → R_MID   = 50 km  dR=10 km
              Düşük yoğunluk  (< THR_MID)   → R_LARGE = 100 km dR=20 km
                  Sarı/boş zon: İç Anadolu platosu (moment rate deficit korunur)

  Aşama 3 — Gaussian Yumuşatma
              Zon sınırlarındaki edge artifact'ları yumuşatır.
              σ = 0.5 × R_atanan (her nokta için ayrı σ)
              Sonuç: jeolojik gerilme gradyanlarıyla uyumlu harita.

Referanslar:
  Aki (1965) MLE: b = log10(e) / (mean(Mw) - Mc_eff)
  Utsu (1966) binom duzeltmesi: Mc_eff = Mc - 0.05
  Öncel & Wyss (2000) Fixed Area Method, GJI 143
  Wiemer (2001) ZMAP Fixed Number Method
  Chang et al. (2025) Entropy 27, 958 — stres odaklı b haritalama

Kullanım:
  python scripts/build_bvalue_adaptive.py
  python scripts/build_bvalue_adaptive.py --mc 2.5 --step 0.1
  python scripts/build_bvalue_adaptive.py --thr_high 15 --thr_mid 5
  python scripts/build_bvalue_adaptive.py --no_smooth
  python scripts/build_bvalue_adaptive.py --output data/bvalue_grid_adaptive.json
"""

import json, math, sys
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Sabitler ─────────────────────────────────────────────────────────────────
MC       = 2.0     # Tamamlılık büyüklüğü — Mw ölçeğinde
                   # Scordilis (2006) kuadratik ML→Mw: ML3.0 → Mw≈2.0 (quadratic form)
                   # Bu nedenle Mw Mc=2.0 ≡ ML Mc=3.0 — eşdeğer eşik
MC_DENS  = 1.5     # Yoğunluk sayımı eşiği — Mw (ML2.0 ≈ Mw1.4-1.5)
DM       = 0.05    # Utsu (1966) binom düzeltmesi
N_MIN    = 50      # b hesabı için minimum olay sayısı

# Adaptif R parametreleri (Öncel 2026)
R_SMALL  = 20.0    # km — yüksek yoğunluk: kırmızı zon (KAFZ, DAFZ, Batı Anadolu grabenleri)
R_MID    = 50.0    # km — orta yoğunluk: geçiş zonu
R_LARGE  = 100.0   # km — düşük yoğunluk: sarı/boş zon

# Yoğunluk eşikleri — D_km=50 km içindeki M>=MC_DENS olay sayısı
# Son 30 yılın yoğunluğuna göre kalibrasyon: KAFZ/DAFZ tipik ~20-50+ olay/50km
THR_HIGH = 20      # >= THR_HIGH → R_SMALL (kırmızı zon)
THR_MID  =  5      # >= THR_MID  → R_MID   (turuncu/geçiş zon)
                   # <  THR_MID  → R_LARGE  (sarı zon)

D_KM     = 50.0    # yoğunluk sayım yarıçapı (km)

STEP     = 0.1     # grid adımı (~11 km)
BOUNDS   = dict(minlat=34.0, maxlat=43.0, minlon=25.0, maxlon=45.0)

INPUT    = 'data/eq_historical.json'    # --input ile override edilebilir
OUTPUT   = 'data/bvalue_grid_adaptive.json'

# Gaussian yumuşatma
SMOOTH   = True    # --no_smooth ile devre dışı
SIGMA_FACTOR = 0.5 # σ = SIGMA_FACTOR × R_atanan (km cinsinden → derece dönüşümü)
KM_PER_DEG   = 111.0


# ── Argüman ayrıştırıcı ──────────────────────────────────────────────────────
def parse_args():
    args = sys.argv[1:]
    def get(flag, default):
        return type(default)(args[args.index(flag)+1]) if flag in args else default
    global MC, MC_DENS, N_MIN, R_SMALL, R_MID, R_LARGE, THR_HIGH, THR_MID
    global D_KM, STEP, OUTPUT, SMOOTH, INPUT
    INPUT     = get('--input',     INPUT)
    MC        = get('--mc',        MC)
    MC_DENS   = get('--mc_dens',   MC_DENS)
    N_MIN     = get('--n_min',     N_MIN)
    R_SMALL   = get('--r_small',   R_SMALL)
    R_MID     = get('--r_mid',     R_MID)
    R_LARGE   = get('--r_large',   R_LARGE)
    THR_HIGH  = get('--thr_high',  THR_HIGH)
    THR_MID   = get('--thr_mid',   THR_MID)
    D_KM      = get('--d_km',      D_KM)
    STEP      = get('--step',      STEP)
    OUTPUT    = get('--output',    OUTPUT)
    if '--no_smooth' in args:
        SMOOTH = False


# ── Haversine mesafe (km) ─────────────────────────────────────────────────────
def haversine(la1, lo1, la2, lo2):
    R = 6371.0; r = math.pi / 180
    dl = (la2 - la1) * r; dlo = (lo2 - lo1) * r
    a = math.sin(dl/2)**2 + math.cos(la1*r)*math.cos(la2*r)*math.sin(dlo/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ── Aki (1965) MLE b-değeri ──────────────────────────────────────────────────
def aki_b(mags, mc, n_min):
    mc_eff = mc - DM
    m = [x for x in mags if x >= mc]
    if len(m) < n_min:
        return None, len(m)
    mean_m = sum(m) / len(m)
    denom  = mean_m - mc_eff
    if denom <= 0:
        return None, len(m)
    return round(math.log10(math.e) / denom, 3), len(m)


# ── Aşama 1: Her grid noktasında sismisite yoğunluğu ─────────────────────────
def compute_density(events_dens, lats, lons):
    """
    D_KM yarıçapı içindeki M>=MC_DENS olay sayısı → zon ataması.
    Döndürür: {(lat,lon): (density_count, zone, R_km)}
    """
    print(f'[Aşama 1] Sismisite yoğunluk haritası  '
          f'(D={D_KM} km, M>={MC_DENS}, eşik H={THR_HIGH} M={THR_MID})')
    density = {}
    ev_tuples = [(e['lat'], e['lon']) for e in events_dens]
    deg_margin = D_KM / KM_PER_DEG + 0.1

    total = len(lats) * len(lons)
    done = 0
    for lat in lats:
        for lon in lons:
            cnt = sum(
                1 for la, lo in ev_tuples
                if abs(la - lat) <= deg_margin and abs(lo - lon) <= deg_margin * 1.3
                and haversine(lat, lon, la, lo) <= D_KM
            )
            if cnt >= THR_HIGH:
                zone, r = 'HIGH', R_SMALL
            elif cnt >= THR_MID:
                zone, r = 'MID',  R_MID
            else:
                zone, r = 'LOW',  R_LARGE
            density[(lat, lon)] = (cnt, zone, r)
            done += 1
            if done % 500 == 0:
                print(f'    {100*done//total}%  ({done}/{total})', end='\r')
    print()

    # Zon istatistikleri
    zones = [v[1] for v in density.values()]
    print(f'    Kırmızı (R={R_SMALL}km): {zones.count("HIGH"):5d} nokta')
    print(f'    Turuncu (R={R_MID}km):  {zones.count("MID"):5d} nokta')
    print(f'    Sarı    (R={R_LARGE}km): {zones.count("LOW"):5d} nokta')
    return density


# ── Aşama 2: Her grid noktasında adaptif R ile b-değeri ─────────────────────
def compute_adaptive(events_b, lats, lons, density):
    """
    density'den R'yi al, o R içindeki M>=MC olaylardan b hesapla.
    """
    print(f'[Aşama 2] Adaptif R ile b-değeri  (N_min={N_MIN}, Mc={MC})')
    grid = []
    # mw: Scordilis (2006) dönüştürülmüş Mw; yoksa mag(ML) fallback
    ev_tuples = [(e['lat'], e['lon'], e.get('mw') or e.get('mag', 0)) for e in events_b]
    skipped = 0

    total = len(lats) * len(lons)
    done = 0
    for lat in lats:
        for lon in lons:
            cnt, zone, r_km = density[(lat, lon)]
            deg_margin = r_km / KM_PER_DEG + 0.1
            nearby_mags = [
                mg for la, lo, mg in ev_tuples
                if abs(la - lat) <= deg_margin and abs(lo - lon) <= deg_margin * 1.3
                and haversine(lat, lon, la, lo) <= r_km
            ]
            b, n = aki_b(nearby_mags, MC, N_MIN)
            if b is None:
                skipped += 1
            else:
                grid.append({
                    'lat' : lat,
                    'lon' : lon,
                    'b'   : b,
                    'n'   : n,
                    'r'   : r_km,
                    'zone': zone,
                    'dens': cnt,
                })
            done += 1
            if done % 500 == 0:
                print(f'    {100*done//total}%  hesaplandi={len(grid)} atlanan={skipped}', end='\r')
    print()
    print(f'    Hesaplanan: {len(grid)} | Atlanan (N<{N_MIN}): {skipped}')
    return grid


# ── Aşama 3: Gaussian yumuşatma ──────────────────────────────────────────────
def gaussian_smooth(grid):
    """
    Her nokta için σ = SIGMA_FACTOR × R_atanan.
    Komşu noktaları Gaussian ağırlıkla ortala.
    """
    if not SMOOTH:
        return grid
    print(f'[Aşama 3] Gaussian yumuşatma  (σ = {SIGMA_FACTOR} × R)')

    # Hızlı arama için dict
    pt = {(p['lat'], p['lon']): p for p in grid}
    smoothed = []

    for p in grid:
        sigma_km  = SIGMA_FACTOR * p['r']
        sigma_deg = sigma_km / KM_PER_DEG
        cutoff    = 3 * sigma_deg   # 3σ dışını say

        w_sum = 0.0
        b_sum = 0.0
        for q in grid:
            dlat = abs(q['lat'] - p['lat'])
            dlon = abs(q['lon'] - p['lon'])
            if dlat > cutoff or dlon > cutoff * 1.3:
                continue
            d_deg = math.sqrt(dlat**2 + dlon**2)
            w = math.exp(-0.5 * (d_deg / sigma_deg)**2)
            b_sum += w * q['b']
            w_sum += w

        b_s = round(b_sum / w_sum, 3) if w_sum > 0 else p['b']
        smoothed.append({**p, 'b_raw': p['b'], 'b': b_s})

    # Kalite kontrolü
    deltas = [abs(s['b'] - s['b_raw']) for s in smoothed]
    print(f'    Ortalama yumuşatma farkı: {sum(deltas)/len(deltas):.4f}')
    print(f'    Maksimum yumuşatma farkı: {max(deltas):.4f}')
    return smoothed


# ── Ana fonksiyon ─────────────────────────────────────────────────────────────
def main():
    parse_args()

    print('='*60)
    print(' Öncel (2026) Adaptif b-Değeri Modeli — Türkiye Geneli')
    print('='*60)
    print(f' R_SMALL={R_SMALL} km (kırmızı zon, yoğunluk>={THR_HIGH})')
    print(f' R_MID  ={R_MID}  km (turuncu zon, yoğunluk>={THR_MID})')
    print(f' R_LARGE={R_LARGE} km (sarı zon,    yoğunluk<{THR_MID})')
    print(f' Grid step={STEP}°  Mc={MC}  N_min={N_MIN}')
    print(f' Gaussian smooth: {"EVET (σ=0.5×R)" if SMOOTH else "HAYIR"}')
    print('='*60)

    # Katalog yükle
    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)
    all_events = data['events']

    # Yoğunluk kataloğu: 30 yıl, M>=MC_DENS, Türkiye bbox
    year_cut = datetime.now(timezone.utc).year - 30
    # Yoğunluk: mw alanı tercih; yoksa mag(ML) fallback
    events_dens = [
        e for e in all_events
        if (e.get('mw') or e.get('mag', 0)) >= MC_DENS
        and int(e.get('time', '1900')[:4]) >= year_cut
        and BOUNDS['minlat'] <= e.get('lat', 0) <= BOUNDS['maxlat']
        and BOUNDS['minlon'] <= e.get('lon', 0) <= BOUNDS['maxlon']
    ]
    print(f'[*] Yoğunluk kataloğu: {len(events_dens)} olay '
          f'({year_cut}–bugün, Mw>={MC_DENS})')

    # b-değeri: mw alanı tercih; yoksa mag(ML) fallback
    events_b = [
        e for e in all_events
        if (e.get('mw') or e.get('mag', 0)) >= MC
        and BOUNDS['minlat'] <= e.get('lat', 0) <= BOUNDS['maxlat']
        and BOUNDS['minlon'] <= e.get('lon', 0) <= BOUNDS['maxlon']
    ]
    print(f'[*] b-değeri kataloğu: {len(events_b)} olay (tüm dönem, Mw>={MC})')

    # Grid üret
    lats, lons = [], []
    cur = BOUNDS['minlat']
    while cur <= BOUNDS['maxlat'] + 1e-9:
        lats.append(round(cur, 4)); cur += STEP
    cur = BOUNDS['minlon']
    while cur <= BOUNDS['maxlon'] + 1e-9:
        lons.append(round(cur, 4)); cur += STEP
    print(f'[*] Grid: {len(lats)}×{len(lons)} = {len(lats)*len(lons)} nokta\n')

    # Aşama 1
    density = compute_density(events_dens, lats, lons)

    # Aşama 2
    grid = compute_adaptive(events_b, lats, lons, density)

    if not grid:
        print('[!] Hiçbir nokta N>=50 kriterini geçemedi.'); return

    # Aşama 3
    grid = gaussian_smooth(grid)

    # İstatistik özeti
    b_vals = [p['b'] for p in grid]
    zones  = [p['zone'] for p in grid]
    print(f'\n[*] Sonuç özeti:')
    print(f'    Toplam nokta : {len(grid)}')
    print(f'    b aralığı    : {min(b_vals):.3f} – {max(b_vals):.3f}')
    print(f'    b ortalaması : {sum(b_vals)/len(b_vals):.3f}')
    print(f'    Kırmızı zon  : {zones.count("HIGH")} nokta (R={R_SMALL} km)')
    print(f'    Turuncu zon  : {zones.count("MID")}  nokta (R={R_MID} km)')
    print(f'    Sarı zon     : {zones.count("LOW")}  nokta (R={R_LARGE} km)')

    # Zon bazlı b ortalamaları (sismotektonik özet)
    for z, r in [('HIGH', R_SMALL), ('MID', R_MID), ('LOW', R_LARGE)]:
        vals = [p['b'] for p in grid if p['zone'] == z]
        if vals:
            print(f'    b̄ ({z}, R={r}km) = {sum(vals)/len(vals):.3f}')

    # w (tehlike ağırlığı) ekle: düşük b → yüksek tehlike
    B_LOW, B_HIGH = 0.5, 1.5
    for p in grid:
        w = 1.0 - (p['b'] - B_LOW) / (B_HIGH - B_LOW)
        p['w'] = round(max(0.0, min(1.0, w)), 4)

    # Çıktı JSON
    out = {
        'generated'  : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'method'     : (
            f'Öncel (2026) Adaptif b-Değeri Modeli | '
            f'Aşama1: Sismisite Yoğunluğu (D={D_KM}km, Mc={MC_DENS}) | '
            f'Aşama2: Değişken R (H={THR_HIGH}→{R_SMALL}km, M={THR_MID}→{R_MID}km, L→{R_LARGE}km) | '
            f'Aşama3: Gaussian σ={SIGMA_FACTOR}×R | '
            f'Aki(1965) MLE + Utsu(1966) | N_min={N_MIN} | Mc={MC}'
        ),
        'references' : [
            'Aki (1965) Bull. ERI 43:237',
            'Utsu (1966) J. Phys. Earth 14:37',
            'Öncel & Wyss (2000) GJI 143:501',
            'Wiemer (2001) SRL 72:373',
            'Chang et al. (2025) Entropy 27:958',
        ],
        'params'     : {
            'MC': MC, 'MC_DENS': MC_DENS, 'N_MIN': N_MIN,
            'R_SMALL': R_SMALL, 'R_MID': R_MID, 'R_LARGE': R_LARGE,
            'THR_HIGH': THR_HIGH, 'THR_MID': THR_MID,
            'D_KM': D_KM, 'STEP': STEP, 'SIGMA_FACTOR': SIGMA_FACTOR,
            'SMOOTH': SMOOTH,
        },
        'bounds'     : BOUNDS,
        'count'      : len(grid),
        'b_min'      : min(b_vals),
        'b_max'      : max(b_vals),
        'b_mean'     : round(sum(b_vals)/len(b_vals), 3),
        'grid'       : grid,
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'\n[OK] Kaydedildi: {OUTPUT}')
    print(f'     EQ-LiveTürkiye entegrasyonu için: data/bvalue_grid_adaptive.json')
    print(f'     Görselleştirme: python scripts/build_bvalue_kriging.py '
          f'--input {OUTPUT}')


if __name__ == '__main__':
    main()
