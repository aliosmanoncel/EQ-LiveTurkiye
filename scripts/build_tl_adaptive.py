"""
build_tl_adaptive.py
Öncel & Wyss (2000, 2001) — T_L Yerel Yineleme Süresi Haritası
Triple-Target M Stratejisi: Mw 6.8 / 7.4 / 7.8

Formül (Öncel & Wyss 2000, GJI 143):
  T_L = 10^(b * M_target - a_ann)   [yıl]
  a_ann = log10(N / ΔT) + b * Mc    (yıllık normalize)

Üçlü Senaryo:
  Mw 6.8 → Operasyonel Risk     (sigorta / tahliye planı)
  Mw 7.4 → Bilimsel Konsensüs   (Marmara karakteristik depremi)
  Mw 7.8 → Uç Değer Senaryosu   (mega-kırılma / sismik borç)

Girdi : data/bvalue_grid_adaptive.json  (a_ann alanı gereklidir)
Çıktı : data/tl_grid_adaptive.json
"""

import json, math, pathlib, datetime

# ── Sabitler ─────────────────────────────────────────────────────────────────
INPUT  = pathlib.Path('data/bvalue_grid_adaptive.json')
OUTPUT = pathlib.Path('data/tl_grid_adaptive.json')

M_TARGETS = [6.8, 7.4, 7.8]          # Triple-Target M stratejisi
TL_MIN    = 1.0                        # Fiziksel alt sınır (yıl) — log negatif engel
TL_MAX    = 100_000.0                  # Pratik üst sınır (yıl)

# ── Yükleme ──────────────────────────────────────────────────────────────────
print('=' * 60)
print(' T_L Yerel Yineleme Süresi — Triple-Target M')
print('=' * 60)

raw = json.loads(INPUT.read_text(encoding='utf-8'))
grid_in = raw['grid']
print(f'[*] {len(grid_in)} nokta yuklendi  (b_ort={raw["b_mean"]}, a_ann ort={raw.get("a_ann_mean","?")})')

# ── T_L Hesaplama ────────────────────────────────────────────────────────────
grid_out = []
skipped  = 0

for pt in grid_in:
    b     = pt.get('b')
    a_ann = pt.get('a_ann')

    if b is None or a_ann is None or b <= 0 or a_ann <= 0:
        skipped += 1
        continue

    row = {
        'lat'  : pt['lat'],
        'lon'  : pt['lon'],
        'b'    : b,
        'a_ann': a_ann,
        'n'    : pt.get('n'),
        'r'    : pt.get('r'),
        'zone' : pt.get('zone'),
    }

    for M in M_TARGETS:
        key = f'tl_m{str(M).replace(".", "p")}'
        exponent = b * M - a_ann
        tl_raw = 10 ** exponent
        row[key] = round(max(TL_MIN, min(TL_MAX, tl_raw)), 1)

    grid_out.append(row)

print(f'[*] Hesaplanan: {len(grid_out)} | Atlanan (eksik alan): {skipped}')

# ── İstatistikler ─────────────────────────────────────────────────────────────
for M in M_TARGETS:
    key = f'tl_m{str(M).replace(".", "p")}'
    vals = [p[key] for p in grid_out]
    mn   = min(vals); mx = max(vals); av = sum(vals)/len(vals)
    print(f'    Mw {M}: T_L {mn:.1f} - {mx:.0f} yr  (ort {av:.0f} yr)')

# ── JSON Çıktısı ──────────────────────────────────────────────────────────────
meta = {
    'count'         : len(grid_out),
    'm_targets'     : M_TARGETS,
    'method'        : 'Öncel & Wyss (2000, 2001) T_L = 10^(b*M - a_ann)',
    'catalog_years' : raw.get('catalog_years', '1900-2026'),
    'generated'     : datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    'grid'          : grid_out,
}

# Senaryo başına min/max
for M in M_TARGETS:
    key = f'tl_m{str(M).replace(".", "p")}'
    vals = [p[key] for p in grid_out]
    meta[f'{key}_min'] = min(vals)
    meta[f'{key}_max'] = max(vals)
    meta[f'{key}_mean'] = round(sum(vals)/len(vals), 1)

OUTPUT.write_text(json.dumps(meta, ensure_ascii=False, separators=(',', ':')),
                  encoding='utf-8')
print(f'[OK] Kaydedildi: {OUTPUT}')
print(f'     {len(grid_out)} nokta, {len(M_TARGETS)} senaryo (6.8 / 7.4 / 7.8)')
