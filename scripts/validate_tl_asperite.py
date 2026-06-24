"""
validate_tl_asperite.py
Retrospektif Kalibrasyon — T_L Minima vs. Epicenter Offset Analizi
Öncel & Wyss (2000, 2001) asperite sabitliği hipotezi testi

AŞAMA 1: Modern validasyon (EMSC 1998-2026, Mw≥6.5)
  → Her ana şok için en yakın T_L minimini bul
  → Offset dağılımı dar + sistematikse → yöntem geçerli

AŞAMA 2: Tarihsel düzeltme (EPICA, Mw≥6.5)
  → Aynı ofseti tarihsel epicenterlere uygula
  → "Düzeltilmiş konum" = T_L minimina yakınsama

Magnitude bantları (Triple-Target):
  Mw 6.5–7.0  → T_L key: tl_m6p8
  Mw 7.0–7.6  → T_L key: tl_m7p4
  Mw 7.6+     → T_L key: tl_m7p8
"""

import json, math, pathlib

# ── Yardımcı: Haversine mesafe (km) ──────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    d2r = math.pi / 180
    dlat = (lat2 - lat1) * d2r
    dlon = (lon2 - lon1) * d2r
    a = math.sin(dlat/2)**2 + math.cos(lat1*d2r)*math.cos(lat2*d2r)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

# ── T_L bantı seçici ─────────────────────────────────────────────────────────
def tl_key_for(mw):
    if mw < 7.0:  return 'tl_m6p8'
    if mw < 7.6:  return 'tl_m7p4'
    return 'tl_m7p8'

def tl_band(mw):
    if mw < 7.0:  return 'Mw 6.5–7.0 (T_L 6.8)'
    if mw < 7.6:  return 'Mw 7.0–7.6 (T_L 7.4)'
    return 'Mw 7.6+ (T_L 7.8)'

# ── Yükleme ──────────────────────────────────────────────────────────────────
tl_raw   = json.loads(pathlib.Path('data/tl_grid_adaptive.json').read_text('utf-8'))
cat_raw_full = json.loads(pathlib.Path('data/eq_historical_dc.json').read_text('utf-8'))
cat_raw = cat_raw_full.get('events', cat_raw_full) if isinstance(cat_raw_full, dict) else cat_raw_full
epica_full = json.loads(pathlib.Path('data/epica_europe_historical.json').read_text('utf-8'))
epica_raw  = epica_full.get('events', epica_full) if isinstance(epica_full, dict) else epica_full

tl_grid = tl_raw['grid']
print(f'[*] T_L grid: {len(tl_grid)} nokta')

# ── Türkiye sınırı ───────────────────────────────────────────────────────────
LAT_MIN, LAT_MAX = 36.0, 42.5
LON_MIN, LON_MAX = 25.5, 45.0

# ── En yakın T_L minimini bul ────────────────────────────────────────────────
def find_nearest_tl_min(lat, lon, key, r_geo_km=50, r_max_km=150):
    """
    2-aşamalı arama:
      1. r_geo_km içindeki en düşük T_L → coğrafi yakın + istatistiksel minimum
      2. Eğer bulunamazsa r_max_km içindeki en düşük T_L (fallback)
    """
    close, far = None, None
    best_close_tl = float('inf')
    best_far_tl   = float('inf')
    for pt in tl_grid:
        tl = pt.get(key)
        if tl is None: continue
        d = haversine(lat, lon, pt['lat'], pt['lon'])
        if d <= r_geo_km and tl < best_close_tl:
            best_close_tl = tl
            close = {'lat': pt['lat'], 'lon': pt['lon'], 'tl': tl, 'b': pt['b'],
                     'dist_km': round(d, 1), 'search': 'R50'}
        if d <= r_max_km and tl < best_far_tl:
            best_far_tl = tl
            far = {'lat': pt['lat'], 'lon': pt['lon'], 'tl': tl, 'b': pt['b'],
                   'dist_km': round(d, 1), 'search': 'R150'}
    return close if close else far

# ════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print(' AŞAMA 1: Modern Validasyon — EMSC/AFAD 1998-2026, Mw>=6.5')
print('=' * 65)

modern = []
for e in cat_raw:
    mw = e.get('mw') or e.get('mag', 0)
    if mw < 6.5: continue
    yr = int(str(e.get('time', '1900'))[:4]) if e.get('time') else 0
    if yr < 1998: continue
    lat = e.get('lat'); lon = e.get('lon')
    if not lat or not lon: continue
    if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX): continue
    modern.append({'lat': lat, 'lon': lon, 'mw': mw, 'time': e.get('time','?')[:10],
                   'place': e.get('place', '')})

print(f'[*] Modern Mw>=6.5 olaylar (Turkiye, 1998-2026): {len(modern)}')
print()

offsets = []
results_modern = []
for ev in sorted(modern, key=lambda x: -x['mw']):
    key = tl_key_for(ev['mw'])
    nearest = find_nearest_tl_min(ev['lat'], ev['lon'], key)
    if not nearest:
        print(f"  {ev['time']} Mw{ev['mw']:.1f} → T_L minimum bulunamadi (R>150km)")
        continue
    offset = nearest['dist_km']
    offsets.append(offset)
    flag = ' *** OTURUYOR' if offset < 20 else (' ** YAKIN' if offset < 50 else '')
    print(f"  {ev['time']} Mw{ev['mw']:.1f} {ev['place'][:30]:30s} "
          f"→ T_L min @ ({nearest['lat']:.1f},{nearest['lon']:.1f}) "
          f"b={nearest['b']:.3f} TL={nearest['tl']:.0f}yr  ofset={offset:.0f}km{flag}")
    results_modern.append({**ev, 'nearest_tl': nearest, 'offset_km': offset, 'tl_key': key})

if offsets:
    print()
    print(f'  Ofset istatistikleri (n={len(offsets)}):')
    print(f'    Minimum : {min(offsets):.1f} km')
    print(f'    Maksimum: {max(offsets):.1f} km')
    print(f'    Ortalama: {sum(offsets)/len(offsets):.1f} km')
    pct50 = sorted(offsets)[len(offsets)//2]
    print(f'    Medyan  : {pct50:.1f} km')
    close = sum(1 for d in offsets if d < 50)
    print(f'    R<50km  : {close}/{len(offsets)} (%{100*close//len(offsets)})')

# ════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print(' AŞAMA 2: Tarihsel Test — EPICA, Mw>=6.5, Türkiye bölgesi')
print('=' * 65)

epica_events = epica_raw if isinstance(epica_raw, list) else []
print(f'[*] EPICA toplam: {len(epica_events)} olay -- filtre uygulanıyor...')

historical = []
for e in epica_events:
    mw  = e.get('mw') or e.get('mag') or 0
    lat = e.get('lat')
    lon = e.get('lon')
    yr  = e.get('year') or e.get('date', '')
    place = e.get('loc') or e.get('reg', '')
    try: mw = float(mw)
    except: continue
    try: lat = float(lat); lon = float(lon)
    except: continue
    if mw < 6.5: continue
    if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX): continue
    historical.append({'lat': lat, 'lon': lon, 'mw': mw, 'year': str(yr), 'place': str(place)})

print(f'[*] EPICA Mw>=6.5 Türkiye bölgesi: {len(historical)} olay')
print()

hist_offsets = []
results_hist = []
for ev in sorted(historical, key=lambda x: -x['mw']):
    key = tl_key_for(ev['mw'])
    nearest = find_nearest_tl_min(ev['lat'], ev['lon'], key)
    if not nearest: continue
    offset = nearest['dist_km']
    hist_offsets.append(offset)
    flag = ' *** OTURUYOR' if offset < 20 else (' ** YAKIN' if offset < 50 else '')
    print(f"  {ev['year']:>5} Mw{ev['mw']:.1f} {str(ev['place'])[:30]:30s} "
          f"→ TL_min @ ({nearest['lat']:.1f},{nearest['lon']:.1f}) "
          f"b={nearest['b']:.3f}  ofset={offset:.0f}km{flag}")
    results_hist.append({**ev, 'nearest_tl': nearest, 'offset_km': offset,
                         'tl_key': key, 'corrected_lat': nearest['lat'], 'corrected_lon': nearest['lon']})

if hist_offsets:
    print()
    print(f'  Tarihsel ofset istatistikleri (n={len(hist_offsets)}):')
    print(f'    Minimum : {min(hist_offsets):.1f} km')
    print(f'    Maksimum: {max(hist_offsets):.1f} km')
    print(f'    Ortalama: {sum(hist_offsets)/len(hist_offsets):.1f} km')
    pct50 = sorted(hist_offsets)[len(hist_offsets)//2]
    print(f'    Medyan  : {pct50:.1f} km')
    close = sum(1 for d in hist_offsets if d < 50)
    print(f'    R<50km  : {close}/{len(hist_offsets)} (%{100*close//max(1,len(hist_offsets))})')

# ── Çıktı JSON ───────────────────────────────────────────────────────────────
out = {
    'method': 'T_L Minima Retrospektif Kalibrasyon — Oncel & Wyss (2000)',
    'triple_target': [6.8, 7.4, 7.8],
    'modern_validation': results_modern,
    'historical_correction': results_hist,
    'summary': {
        'modern_n': len(offsets),
        'modern_median_km': round(sorted(offsets)[len(offsets)//2], 1) if offsets else None,
        'historical_n': len(hist_offsets),
        'historical_median_km': round(sorted(hist_offsets)[len(hist_offsets)//2], 1) if hist_offsets else None,
    }
}
pathlib.Path('data/tl_asperite_validation.json').write_text(
    json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print()
print('[OK] Kaydedildi: data/tl_asperite_validation.json')
