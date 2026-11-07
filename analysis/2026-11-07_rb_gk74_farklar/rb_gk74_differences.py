"""
rb_gk74_differences.py — GK74 ile Reasenberg (zmap) arasindaki siniflandirma farklarinin
bilimsel incelemesi (arastirma dali; main ve canli site degismez).

Referans surum: main @ be61bae (PR #3). Girdi ve tanim, site urunu ile AYNI:
eq_historical.json icinde src == 'EMSC' (1998-2026), M >= 3.0, mag alani; GK74 =
scripts/decluster_gk74.py (degismeden), Reasenberg = scripts/decluster_reasenberg.py
(zmap, xmeff 3.0, donmus reasenberg.py v0.3.0).

Iki fark grubu (YON ONEMLI):
  R_only  : GK74 ARTCI saydi (cikardi), Reasenberg BAGIMSIZ birakti      (beklenen ~30 976)
  GK_only : GK74 BAGIMSIZ birakti, Reasenberg BAGIMLI sayardi             (beklenen ~334)

Her GK74 artcisi icin "isaretleyen" GK74 olayi (penceresini acan olay = 'ebeveyn')
decluster_gk74.decluster ile AYNI dongu tekrarlanarak bulunur; bayraklarin projeyle
birebir ayni oldugu denetlenir. Ebeveyn, bir kume yorumu degil, GK74'un kendi
pencere kuralinin kaydidir.

R_only olaylari icin mekanizma siniflamasi (Reasenberg zmap, ebeveyn -> olay
dogrudan baglantisi acisindan; zincirleme baglantilar yok sayilir — tanisal):
  far      : d > rfact * r(M_ebeveyn)               (Reasenberg etkilesim yaricapi disi)
  late     : d <= yaricap ve dt > tau_max (10 gun)   (Reasenberg ileri bakis suresi disi)
  window   : d <= yaricap ve dt <= 10 gun, ama baglanmadi (tau < dt: kumelenmemis olayda
             tau = 1 gun; kumedeki olaylarda Omori-tipi tau)
r(M) = 0.011 * 10**(0.4 M) km, rfact = 10.

Ciktilar (bu klasore): differences_events.csv, summary.json, fig_*.png
Kullanim (depo kokunden): python analysis/2026-11-07_rb_gk74_farklar/rb_gk74_differences.py
"""

import csv
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)
import decluster_gk74 as GK  # noqa: E402
import decluster_reasenberg as RB  # noqa: E402

CATALOG = 'data/eq_historical.json'
PRODUCT = 'data/reasenberg_gk74_emsc.json'
RFACT, TAU_MAX = 10.0, 10.0


def r_int(m):
    return 0.011 * 10 ** (0.4 * m)


def gk74_with_parent(events):
    """decluster_gk74.decluster dongusunun birebir kopyasi + isaretleyen olay kaydi."""
    rows = []
    for e in events:
        rows.append((e, GK.parse_time_ms(e.get('time')), GK.event_mag(e, 'mag'),
                     GK._num(e.get('lat')), GK._num(e.get('lon'))))
    rows.sort(key=lambda r: (r[1] is None, r[1] if r[1] is not None else 0))
    n = len(rows)
    cl = [False] * n
    parent = [-1] * n
    for i in range(n):
        if cl[i]:
            continue
        _, t0, m, la, lo = rows[i]
        if None in (t0, m, la, lo):
            continue
        T_days, D_km = GK.gk_window(m)
        T_ms = T_days * 86400000
        for j in range(i + 1, n):
            _, tj, mj, laj, loj = rows[j]
            if tj is None or tj - t0 > T_ms:
                break
            if cl[j] or mj is None or not (mj < m) or laj is None or loj is None:
                continue
            if GK.haversine(la, lo, laj, loj) <= D_km:
                cl[j] = True
                parent[j] = i
    return [r[0] for r in rows], cl, parent


def main():
    raw = open(CATALOG, 'rb').read()
    em = [e for e in json.loads(raw.decode('utf-8'))['events'] if e.get('src') == 'EMSC']
    product = json.load(open(PRODUCT, encoding='utf-8'))
    assert hashlib.sha256(raw).hexdigest() == product['definition']['catalog_sha256'], 'katalog urunden farkli'

    evs, cl, parent = gk74_with_parent(em)
    ref_evs, ref_cl = GK.decluster(em, 'mag')
    assert [e['id'] for e in evs] == [e['id'] for e in ref_evs] and cl == ref_cl, 'GK74 kopyasi projeden farkli'
    r_evs, out = RB.decluster(em, 3.0, 'zmap', 'mag')
    assert [e['id'] for e in r_evs] == [e['id'] for e in evs]
    res = out['res']

    t = np.array([GK.parse_time_ms(e['time']) for e in evs], float) / 86400000.0
    lat = np.array([e['lat'] for e in evs]); lon = np.array([e['lon'] for e in evs])
    mag = np.array([e['mag'] for e in evs], float)
    ecls = out['event_class']
    rep_t = {k: t[out['valid_index'][int(res.representative[k])]] for k in range(res.n_clusters)}
    gk_ind = ~np.array(cl)
    r_ind = np.array([c != 'dependent' for c in ecls])
    cat = np.where(gk_ind & r_ind, 'both_independent', np.where(gk_ind, 'GK_only_independent',
                   np.where(r_ind, 'R_only_independent', 'both_dependent')))
    counts = Counter(cat.tolist())
    assert {k: counts[k] for k in product['categories']} == product['categories'], 'urun sayilariyla uyusmuyor'

    # ---------------- per-event table for the two difference groups
    rows = []
    mech = Counter()
    par_children = defaultdict(lambda: Counter())
    for j in np.flatnonzero(cat != 'both_independent'):
        if cat[j] == 'both_dependent':
            continue
        e = evs[j]
        rec = dict(id=e['id'], time=e['time'], lat=e['lat'], lon=e['lon'], dep=e['dep'], mag=e['mag'],
                   mtype=e['mtype'], group='R_only' if cat[j] == 'R_only_independent' else 'GK_only',
                   gk74='aftershock' if cl[j] else 'independent', reasenberg_class=ecls[j],
                   reasenberg_cluster=int(out['cluster_id'][j]),
                   reasenberg_role='')
        if ecls[j] == 'dependent':
            rec['reasenberg_role'] = 'foreshock' if t[j] < rep_t[int(out['cluster_id'][j])] else 'aftershock'
        if cl[j]:
            p = parent[j]
            d = GK.haversine(lat[p], lon[p], lat[j], lon[j])
            dt = t[j] - t[p]
            rad = RFACT * r_int(mag[p])
            m_ = 'far' if d > rad else 'late' if dt > TAU_MAX else 'window'
            rec.update(gk_parent_id=evs[p]['id'], gk_parent_time=evs[p]['time'], gk_parent_mag=mag[p],
                       dist_km=round(d, 2), dt_days=round(dt, 3), reasenberg_radius_parent_km=round(rad, 2),
                       gk_window_km=round(GK.gk_window(mag[p])[1], 1), mechanism=m_,
                       gk_parent_reasenberg_class=ecls[p])
            mech[m_] += 1
            par_children[p][m_] += 1
        rows.append(rec)
    fields = ['id', 'time', 'lat', 'lon', 'dep', 'mag', 'mtype', 'group', 'gk74', 'reasenberg_class',
              'reasenberg_role', 'reasenberg_cluster', 'gk_parent_id', 'gk_parent_time', 'gk_parent_mag',
              'dist_km', 'dt_days', 'reasenberg_radius_parent_km', 'gk_window_km', 'mechanism',
              'gk_parent_reasenberg_class']
    with open(os.path.join(HERE, 'differences_events.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    ro = [r for r in rows if r['group'] == 'R_only']
    go = [r for r in rows if r['group'] == 'GK_only']
    pm = np.array([r['gk_parent_mag'] for r in ro])
    dist = np.array([r['dist_km'] for r in ro]); dts = np.array([r['dt_days'] for r in ro])
    pbin = lambda m: '3.0-3.9' if m < 4 else '4.0-4.9' if m < 5 else '5.0-5.9' if m < 6 else '>=6.0'
    by_pmag = defaultdict(Counter)
    for r in ro:
        by_pmag[pbin(r['gk_parent_mag'])][r['mechanism']] += 1
    top = sorted(par_children.items(), key=lambda kv: -sum(kv[1].values()))[:15]
    top_tbl = [dict(time=evs[p]['time'][:16], lat=round(lat[p], 2), lon=round(lon[p], 2), mag=mag[p],
                    mtype=evs[p]['mtype'], n_R_only=sum(c.values()), **dict(c),
                    gk_window_km=round(GK.gk_window(mag[p])[1], 1),
                    gk_window_days=round(GK.gk_window(mag[p])[0], 1),
                    reasenberg_radius_km=round(RFACT * r_int(mag[p]), 1)) for p, c in top]
    years = Counter(r['time'][:4] for r in ro)
    allyears = Counter(e['time'][:4] for e in evs)
    seq_share = sum(sum(c.values()) for p, c in par_children.items() if mag[p] >= 6.0) / len(ro)

    summary = dict(
        reference=dict(main_commit='be61bae', catalog_sha256=product['definition']['catalog_sha256'],
                       script_sha256=hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()),
        checks=dict(gk74_copy_identical_to_project=True, counts_match_site_product=True),
        groups=dict(R_only=len(ro), GK_only=len(go)),
        R_only_reasenberg_class=dict(Counter(r['reasenberg_class'] for r in ro)),
        GK_only_reasenberg_role=dict(Counter(r['reasenberg_role'] for r in go)),
        R_only_mechanism=dict(mech),
        R_only_mechanism_by_parent_magnitude={k: dict(v) for k, v in sorted(by_pmag.items())},
        R_only_distance_km_quantiles={q: round(float(np.quantile(dist, q / 100)), 1) for q in (10, 25, 50, 75, 90)},
        R_only_dt_days_quantiles={q: round(float(np.quantile(dts, q / 100)), 2) for q in (10, 25, 50, 75, 90)},
        R_only_share_from_parents_M6plus=round(seq_share, 4),
        R_only_n_distinct_parents=len(par_children),
        top_gk74_parents=top_tbl,
        R_only_by_year={y: dict(n=years[y], of_all=allyears[y], frac=round(years[y] / allyears[y], 3))
                        for y in sorted(allyears)},
    )
    json.dump(summary, open(os.path.join(HERE, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    make_figures(ro, evs, lat, lon, cat, years, allyears, by_pmag)
    print(json.dumps({k: summary[k] for k in ('groups', 'R_only_reasenberg_class', 'GK_only_reasenberg_role',
                                              'R_only_mechanism', 'R_only_mechanism_by_parent_magnitude',
                                              'R_only_distance_km_quantiles', 'R_only_dt_days_quantiles',
                                              'R_only_share_from_parents_M6plus', 'R_only_n_distinct_parents')},
                     ensure_ascii=False, indent=1))
    for r in top_tbl[:10]:
        print(r)


def make_figures(ro, evs, lat, lon, cat, years, allyears, by_pmag):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    faults = []
    try:
        gj = json.load(open('data/turkiye_diri_fay_mta2026.geojson', encoding='utf-8'))
        for f in gj['features']:
            g = f['geometry']
            parts = [g['coordinates']] if g['type'] == 'LineString' else g['coordinates'] if g['type'] == 'MultiLineString' else []
            faults += [np.array(p) for p in parts]
    except Exception:
        pass

    # --- spatial: count and fraction on 0.25 deg grid
    cs = 0.25
    la_e = np.arange(33, 45 + cs, cs); lo_e = np.arange(23, 48 + cs, cs)
    rmask = cat == 'R_only_independent'
    H_all, _, _ = np.histogram2d(lat, lon, [la_e, lo_e])
    H_r, _, _ = np.histogram2d(lat[rmask], lon[rmask], [la_e, lo_e])
    frac = np.where(H_all >= 20, H_r / np.maximum(H_all, 1), np.nan)
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.2), constrained_layout=True)
    for a, Z, title, cmap, lab in ((ax[0], np.where(H_r > 0, H_r, np.nan), 'Yalnız Reasenberg\'de bağımsız: olay sayısı', 'viridis', 'olay / 0,25°'),
                                   (ax[1], frac, 'Yalnız Reasenberg\'de bağımsız: pay (hücrede n ≥ 20)', 'Oranges', 'pay')):
        im = a.pcolormesh(lo_e, la_e, Z, cmap=cmap, shading='flat', vmin=0, vmax=None if cmap == 'viridis' else 0.8)
        for fl in faults:
            a.plot(fl[:, 0], fl[:, 1], color='#555', lw=0.3)
        a.set_xlim(23, 48); a.set_ylim(33, 45); a.set_aspect(1.25); a.set_title(title, fontsize=10)
        a.set_xlabel('Boylam (°E)'); a.set_ylabel('Enlem (°N)')
        fig.colorbar(im, ax=a, shrink=0.8, label=lab)
    fig.suptitle('GK74 artçı sayıp Reasenberg (zmap) bağımsız bıraktığı olaylar — 1998–2026 EMSC, M ≥ 3,0 (koşullu algoritmik karşılaştırma)', fontsize=10)
    fig.savefig(os.path.join(HERE, 'fig_mekansal.png'), dpi=130)
    plt.close(fig)

    # --- temporal
    ys = sorted(allyears)
    fig, ax = plt.subplots(figsize=(11, 3.6), constrained_layout=True)
    ax.bar(ys, [allyears[y] for y in ys], color='#ccc', label='tüm olaylar')
    ax.bar(ys, [years[y] for y in ys], color='#d94801', label='yalnız Reasenberg\'de bağımsız')
    ax2 = ax.twinx()
    ax2.plot(ys, [years[y] / allyears[y] for y in ys], color='k', marker='o', ms=3, lw=1, label='pay')
    ax2.set_ylim(0, 0.8); ax2.set_ylabel('pay')
    ax.set_ylabel('olay sayısı'); ax.tick_params(axis='x', rotation=90)
    ax.legend(loc='upper left', fontsize=8); ax2.legend(loc='upper right', fontsize=8)
    ax.set_title('Yıllara göre dağılım — 1998–2026 EMSC, M ≥ 3,0', fontsize=10)
    fig.savefig(os.path.join(HERE, 'fig_zamansal.png'), dpi=130)
    plt.close(fig)

    # --- mechanism vs GK74 parent magnitude, and distance / window comparison
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.2), constrained_layout=True)
    keys = sorted(by_pmag); mechs = ['far', 'late', 'window']; cols = {'far': '#d94801', 'late': '#2563eb', 'window': '#9ca3af'}
    bottom = np.zeros(len(keys))
    for m_ in mechs:
        v = np.array([by_pmag[k][m_] for k in keys])
        ax[0].bar(keys, v, bottom=bottom, color=cols[m_], label=m_)
        bottom += v
    ax[0].set_xlabel('GK74 penceresini açan olayın büyüklüğü'); ax[0].set_ylabel('olay sayısı')
    ax[0].set_title('Mekanizma (tanısal): far = Reasenberg yarıçapı dışı, late = 10 günden sonra', fontsize=9)
    ax[0].legend(fontsize=8)
    pm = np.array([r['gk_parent_mag'] for r in ro]); d = np.array([r['dist_km'] for r in ro])
    ax[1].scatter(pm + np.random.default_rng(0).uniform(-0.04, 0.04, pm.size), d, s=1, alpha=0.15, color='#d94801')
    mm = np.linspace(3, 8, 100)
    ax[1].plot(mm, [GK.gk_window(x)[1] for x in mm], 'k-', lw=1.2, label='GK74 D(M)')
    ax[1].plot(mm, RFACT * r_int(mm), 'b--', lw=1.2, label='Reasenberg 10·r(M)')
    ax[1].set_yscale('log'); ax[1].set_xlabel('GK74 penceresini açan olayın büyüklüğü')
    ax[1].set_ylabel('uzaklık (km)'); ax[1].legend(fontsize=8)
    ax[1].set_title('Uzaklık: GK74 penceresi ile Reasenberg etkileşim yarıçapı', fontsize=9)
    fig.savefig(os.path.join(HERE, 'fig_mekanizma.png'), dpi=130)
    plt.close(fig)


if __name__ == '__main__':
    main()
