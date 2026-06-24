"""
build_delta_b.py
Artci Baskisi Indeksi: delta_b = b(main) - b(all)
Oncel (2026) -- katalog kalite ve guveni paneli

Yontem:
  1. Mevcut b(main) grid'ini yukle  (data/bvalue_grid_adaptive.json -- declustered)
  2. Raw katalog uzerinden ayni grid noktalarinda b(all) hesapla
  3. delta_b = b(main) - b(all) kaydet

Yorum:
  delta_b < 0  : b(main) < b(all)  -- artcilar b'yi yukari cekiyordu, declustering dogru karar
  delta_b ~ 0  : b(main) ~ b(all)  -- bolge zaten ana deprem karakterli, artci etkisi minimal
  delta_b > 0  : b(main) > b(all)  -- artcilar dusuk-b kume olusturmus (stres artcilari)

Cikti: data/delta_b_grid.json
"""

import json, math, pathlib

MC       = 2.0    # tamamlilik buyukluğu (Mw)
DM       = 0.05   # Utsu (1966) binom duzeltmesi
N_MIN    = 50     # Aki (1965) minimum olay sayisi
KM_PER_DEG = 111.195

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    d2r = math.pi / 180
    dlat = (lat2 - lat1) * d2r
    dlon = (lon2 - lon1) * d2r
    a = math.sin(dlat/2)**2 + math.cos(lat1*d2r)*math.cos(lat2*d2r)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

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

# ── Veri yukle ────────────────────────────────────────────────────────────────
print('[*] b(main) grid yukleniyor...')
main_raw = json.loads(pathlib.Path('data/bvalue_grid_adaptive.json').read_text('utf-8'))
main_grid = {(p['lat'], p['lon']): p for p in main_raw['grid']}
print(f'    {len(main_grid)} nokta')

print('[*] Raw katalog yukleniyor...')
raw_full = json.loads(pathlib.Path('data/eq_historical.json').read_text('utf-8'))
raw_events = raw_full if isinstance(raw_full, list) else raw_full.get('events', [])
print(f'    {len(raw_events)} olay')

# Mw filtresi
raw_mw = []
for e in raw_events:
    mw = e.get('mw') or e.get('mag', 0)
    lat = e.get('lat')
    lon = e.get('lon')
    try:
        mw = float(mw); lat = float(lat); lon = float(lon)
    except:
        continue
    if mw >= MC:
        raw_mw.append((lat, lon, mw))
print(f'    Mw>={MC} filtre sonrasi: {len(raw_mw)} olay')

# ── Her grid noktasinda b(all) hesapla ───────────────────────────────────────
print('[*] b(all) hesaplaniyor...')
results = []
total = len(main_grid)
done  = 0

for (lat, lon), mp in main_grid.items():
    r_km = mp['r']  # ayni adaptif R kullan
    deg_margin = r_km / KM_PER_DEG + 0.1
    nearby = [
        mg for la, lo, mg in raw_mw
        if abs(la - lat) <= deg_margin and abs(lo - lon) <= deg_margin * 1.3
        and haversine(lat, lon, la, lo) <= r_km
    ]
    b_all, n_all = aki_b(nearby, MC, N_MIN)
    done += 1
    if done % 200 == 0:
        print(f'    {100*done//total}%  ({done}/{total})', end='\r')

    if b_all is None:
        continue

    b_main  = mp['b']
    delta_b = round(b_main - b_all, 3)

    # Yorum
    if delta_b < -0.10:
        interp = 'artci_baskisi'    # artcilar b'yi yukari cekiyordu
    elif delta_b > 0.10:
        interp = 'stres_artcisi'    # artcilar dusuk-b kume (yuksek stres artcilari)
    else:
        interp = 'ana_deprem_karakterli'  # b(main) ~ b(all)

    results.append({
        'lat'    : lat,
        'lon'    : lon,
        'b_main' : b_main,
        'b_all'  : b_all,
        'delta_b': delta_b,
        'n_main' : mp['n'],
        'n_all'  : n_all,
        'r'      : r_km,
        'zone'   : mp['zone'],
        'interp' : interp,
    })

print()
print(f'[*] Hesaplanan: {len(results)} nokta')

# ── Istatistikler ─────────────────────────────────────────────────────────────
deltas = [r['delta_b'] for r in results]
neg  = sum(1 for d in deltas if d < -0.10)
zero = sum(1 for d in deltas if -0.10 <= d <= 0.10)
pos  = sum(1 for d in deltas if d > 0.10)
print(f'    delta_b < -0.10 (artci baskisi)        : {neg}  nokta ({100*neg//len(deltas)}%)')
print(f'    delta_b ~ 0     (ana deprem karakterli) : {zero} nokta ({100*zero//len(deltas)}%)')
print(f'    delta_b > +0.10 (stres artcisi)         : {pos}  nokta ({100*pos//len(deltas)}%)')
print(f'    delta_b aralik  : {min(deltas):.3f} -- {max(deltas):.3f}')
print(f'    delta_b ortalama: {sum(deltas)/len(deltas):.3f}')

# ── Cikti ─────────────────────────────────────────────────────────────────────
out = {
    'meta': {
        'title'  : 'Artci Baskisi Indeksi -- delta_b = b(main) - b(all)',
        'method' : 'Oncel (2026) -- Aki (1965) MLE, Mc=2.0(Mw), N>=50',
        'ref'    : 'Gardner & Knopoff (1974) declustering vs raw catalog',
        'n'      : len(results),
        'delta_b_min': min(deltas),
        'delta_b_max': max(deltas),
        'delta_b_mean': round(sum(deltas)/len(deltas), 3),
        'artci_baskisi_n': neg,
        'ana_deprem_n'   : zero,
        'stres_artcisi_n': pos,
    },
    'grid': results
}
pathlib.Path('data/delta_b_grid.json').write_text(
    json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print('[OK] Kaydedildi: data/delta_b_grid.json')
