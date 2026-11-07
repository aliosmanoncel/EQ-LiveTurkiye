"""
build_reasenberg_gk74_compare.py — GK74 / Reasenberg karsilastirmasi (STATIK site urunu).

Ayni olay listesi (1998-2026 EMSC, eq_historical.json icinde src == 'EMSC'; tumu M >= 3.0)
uzerinde iki yontem calistirilir:
  * GK74      : scripts/decluster_gk74.py (degistirilmeden), mag alani
  * Reasenberg: scripts/decluster_reasenberg.py, rule = zmap (varsayilan), xmeff = 3.0
ve sonuc data/reasenberg_gk74_emsc.json dosyasina yazilir. Site bu dosyayi okur;
tarayicida yeniden hesap YAPILMAZ.

Cikti deterministiktir (duvar saati kullanilmaz; tarih = katalogun 'generated' alani),
boylece CI yeniden uretip birebir ayni oldugunu denetler.

Terimler: Reasenberg siniflari algoritmiktir (tekil / temsilci / bagimli; bagimlilar
temsilciden once ise "oncu", sonra ise "artci" diye ayrilir). GK74 burada yalniz artci
ayiklar (oncu kalir). Hicbiri fiziksel ana sok iddiasi degildir; urun deprem tahmini
icin degildir. Sonuclar karisik buyukluk olcegine (ML/MD/mb/Mw) kosulludur.

Kullanim (depo kokunden):  python scripts/build_reasenberg_gk74_compare.py
"""

import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decluster_gk74 as GK  # noqa: E402
import decluster_reasenberg as RB  # noqa: E402

CATALOG = 'data/eq_historical.json'
OUTPUT = 'data/reasenberg_gk74_emsc.json'
SRC = 'EMSC'
MAG_MIN = 3.0
XMEFF = 3.0
RULE = 'zmap'
CELL_DEG = 1.0
CELL_MIN_N = 30
PRODUCT_VERSION = 'rb-gk74-emsc-2026-11-07'

CAT_CODES = {'both_independent': 0, 'both_dependent': 1, 'R_only_independent': 2, 'GK_only_independent': 3}


def _sha_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def boundary_bin(e, la0, la1, lo0, lo1):
    """Distance (km) to the nearest edge of the catalog rectangle; edge effect diagnostic:
    clusters can be cut by the boundary for both methods."""
    kx = 111.195 * math.cos(math.radians(e['lat']))
    d = min((e['lat'] - la0) * 111.195, (la1 - e['lat']) * 111.195, (e['lon'] - lo0) * kx, (lo1 - e['lon']) * kx)
    return '1: <25 km' if d < 25 else '2: 25-100 km' if d < 100 else '3: >100 km'


def mag_bin(m):
    return '3.0-3.4' if m < 3.5 else '3.5-3.9' if m < 4.0 else '4.0-4.9' if m < 5.0 else '>=5.0'


def build(catalog=CATALOG):
    with open(catalog, 'rb') as f:
        raw = f.read()
    data = json.loads(raw.decode('utf-8'))
    events = [e for e in data['events'] if e.get('src') == SRC]
    below = [e for e in events if (GK.event_mag(e, 'mag') or 0) < MAG_MIN - 1e-9]
    events = [e for e in events if e not in below] if below else events

    # --- GK74 (unchanged project code)
    gk_evs, gk_cl = GK.decluster(events, 'mag')
    gk_main = {e['id'] for e, c in zip(gk_evs, gk_cl) if not c}
    # --- Reasenberg (frozen module via adapter)
    if RB.module_sha256() != RB.MODULE_SHA256_FROZEN:
        sys.exit('scripts/reasenberg.py dondurulmus v0.3.0 degil. Durduruldu.')
    evs, out = RB.decluster(events, XMEFF, RULE, 'mag')
    assert [e['id'] for e in evs] == [e['id'] for e in gk_evs], 'iki yontemin olay sirasi farkli'

    res = out['res']
    vi = out['valid_index']
    rep_time = {}
    for k in range(res.n_clusters):
        rep_time[k] = GK.parse_time_ms(evs[vi[int(res.representative[k])]]['time'])

    rows = []
    for e, cid, cls in zip(evs, out['cluster_id'], out['event_class']):
        gk_ind = e['id'] in gk_main
        r_ind = cls != 'dependent'
        role = cls
        if cls == 'dependent':
            role = 'foreshock' if GK.parse_time_ms(e['time']) < rep_time[cid] else 'aftershock'
        cat = ('both_independent' if gk_ind and r_ind else 'GK_only_independent' if gk_ind else
               'R_only_independent' if r_ind else 'both_dependent')
        rows.append(dict(e=e, gk_ind=gk_ind, r_cls=cls, r_role=role, cat=cat))

    n = len(rows)
    cats = Counter(r['cat'] for r in rows)
    roles = Counter(r['r_role'] for r in rows)
    lat = [r['e']['lat'] for r in rows]
    lon = [r['e']['lon'] for r in rows]
    years = [r['e']['time'][:4] for r in rows]

    def breakdown(key):
        acc = defaultdict(Counter)
        for r in rows:
            acc[key(r)][r['cat']] += 1
        return [dict(key=k, n=sum(c.values()), **{c2: c[c2] for c2 in CAT_CODES}) for k, c in sorted(acc.items())]

    cells = defaultdict(Counter)
    for r in rows:
        la0 = math.floor(r['e']['lat'] / CELL_DEG) * CELL_DEG
        lo0 = math.floor(r['e']['lon'] / CELL_DEG) * CELL_DEG
        cells[(la0, lo0)][r['cat']] += 1
    cell_list = [dict(lat0=k[0], lon0=k[1], n=sum(c.values()), **{c2: c[c2] for c2 in CAT_CODES})
                 for k, c in sorted(cells.items()) if sum(c.values()) >= CELL_MIN_N]

    gk_removed = n - len(gk_main & {r['e']['id'] for r in rows})
    r_dep = roles['foreshock'] + roles['aftershock']
    product = dict(
        product='GK74 / Reasenberg karşılaştırması (statik)',
        product_version=PRODUCT_VERSION,
        data_date=data.get('generated'),
        definition=dict(
            catalog=CATALOG, catalog_sha256=hashlib.sha256(raw).hexdigest(),
            catalog_generated=data.get('generated'),
            source=SRC, period=f'{min(years)}–{max(years)}',
            time_first=min(r['e']['time'] for r in rows), time_last=max(r['e']['time'] for r in rows),
            mag_field='mag', mag_min=MAG_MIN, n_below_mag_min_excluded=len(below),
            bounds=dict(lat_min=min(lat), lat_max=max(lat), lon_min=min(lon), lon_max=max(lon),
                        note='katalogun kendi sınırı (33–45°N, 23–48°E dikdörtgeni); iki yönteme aynı olaylar'),
            same_events_both_methods=True),
        methods=dict(
            gk74=dict(script='scripts/decluster_gk74.py', script_sha256=_sha_file('scripts/decluster_gk74.py'),
                      rule='GK74 Tablo 1 pencereleri; yalnız artçı (ileri pencere), episantral mesafe, UTC'),
            reasenberg=dict(module='scripts/reasenberg.py', module_version=RB.R.__version__,
                            module_sha256=RB.module_sha256(), adapter='scripts/decluster_reasenberg.py',
                            adapter_sha256=_sha_file('scripts/decluster_reasenberg.py'),
                            rule=RULE, rule_status='default', params=dict(res.params.__dict__),
                            assumptions=['kayıtlı derinlikler (hiposantral mesafe)',
                                         'err = derr = 0 (katalogda konum hatası yok; belgelenmiş varsayım)']),
            builder='scripts/build_reasenberg_gk74_compare.py',
            builder_sha256=_sha_file(os.path.abspath(__file__))),
        status='Koşullu algoritmik karşılaştırma: 1998–2026 EMSC, M ≥ 3,0 ve karışık büyüklük ölçeğine '
               'koşullu; katalog tamlık doğrulaması veya deprem tehlikesi değerlendirmesi değildir.',
        caveats=['Statik ürün: haritada bölge veya dönem değiştirildiğinde yeniden hesaplanmaz.',
                 'Aynı sınıflandırma oranı iki yöntemin birbirine uyumudur; doğruluk ölçüsü değildir.',
                 'GK74 burada yalnız artçı ayıklar (öncüler kalır); Reasenberg kümeleri öncüleri de içerir.',
                 'Sınıflar algoritmiktir; fiziksel ana şok iddiası değildir.',
                 'Büyüklük ölçeği karışıktır (ML/MD/mb/Mw); farkların fiziksel yorumu bu ürünle yapılmaz.',
                 'Deprem tahmini için değildir.'],
        totals=dict(
            n=n,
            gk74=dict(independent=len(gk_main), aftershock_removed=gk_removed,
                      removed_frac=round(gk_removed / n, 4)),
            reasenberg=dict(independent=roles['single'] + roles['representative'],
                            single=roles['single'], representative=roles['representative'],
                            clusters=res.n_clusters, dependent=r_dep,
                            dependent_foreshock=roles['foreshock'], dependent_aftershock=roles['aftershock'],
                            removed_frac=round(r_dep / n, 4), invalid=out['event_class'].count('invalid'))),
        categories={k: cats[k] for k in CAT_CODES},
        agreement_rate=round((cats['both_independent'] + cats['both_dependent']) / n, 4),
        by_magnitude=breakdown(lambda r: mag_bin(r['e']['mag'])),
        by_year=breakdown(lambda r: r['e']['time'][:4]),
        by_boundary_distance=breakdown(lambda r: boundary_bin(r['e'], min(lat), max(lat), min(lon), max(lon))),
        cells=dict(size_deg=CELL_DEG, min_n=CELL_MIN_N, items=cell_list),
    )
    return product


def main():
    p = build()
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(RB.json_safe(p), f, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    t = p['totals']
    print(f"[*] {t['n']} olay | GK74 bağımsız {t['gk74']['independent']} | Reasenberg bağımsız "
          f"{t['reasenberg']['independent']} ({t['reasenberg']['clusters']} küme) | uyum {p['agreement_rate']}")
    print(f'[OK] Kaydedildi: {OUTPUT} ({os.path.getsize(OUTPUT)} bayt)')


if __name__ == '__main__':
    main()
