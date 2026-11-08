"""
bok_analiz.py — Bağımsız Olay Kimliği Belirsizliği (Independent Event Identification Uncertainty)
GK74 ve Reasenberg (1985) ile aynı ham katalogdan elde edilen İKİ AYRI bağımsız olay kataloğu.

Koşullar (karar 2026-11-08):
  1. Ham katalog değişmez: data/eq_historical.json, src == EMSC (1998–2026, M ≥ 3,0); iki yöntem aynı olaylarda.
  2. Sonuçlar birleştirilmez: her parametre her katalog için ayrı hesaplanır; fark "yöntem duyarlılığı"dır,
     güven aralığı değildir.
  3. Kimlik farkları korunur: ortak / yalnız GK74 / yalnız Reasenberg bağımsız olaylar ayrı listelenir.
Kod: scripts/decluster_gk74.py (değişmeden), scripts/decluster_reasenberg.py + dondurulmuş reasenberg.py v0.3.0
(zmap, xmeff = 3,0 = statik ürünle aynı). "Bağımsız" algoritmik sınıftır; fiziksel ana şok iddiası değildir.
GK74 burada yalnız artçı ayıklar (öncüler bağımsız kalır); Reasenberg'de bağımsız = tekil + temsilci.

Çıktılar (bu klasör): sonuc.json, bagimsiz_olaylar.csv.gz (her olay: iki sınıf), buyuk_farklar.csv (M ≥ 6),
doublet_adaylari.csv, fig_gr.png.
Kullanım (depo kökünden): python analysis/2026-11-08_bagimsiz_olay_kimligi/bok_analiz.py
"""
import csv, json, math, os, sys
from datetime import datetime

import numpy as np
from scipy import stats

sys.path.insert(0, 'scripts')
import decluster_gk74 as GK  # noqa: E402
import decluster_reasenberg as D  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
XMEFF = 3.0
DM = 0.1
MC_LIST = [3.2, 3.5]            # 3,2 = sitenin MAXC+0,2 tahmini (tüm EMSC); 3,5 = duyarlılık
M_THR = [6.0, 7.0]
HORIZONS = [1, 10, 50]
DOUBLET = dict(mmin=6.0, dm=0.5, dt_days=365.0, dkm=150.0)   # aday listesi 150 km'ye kadar; 100 km işareti ayrıca yazılır


def parse(t):
    return datetime.fromisoformat(t.replace('Z', '+00:00'))


# ---------- yardımcı istatistikler ----------
def aki_utsu(m, mc, dm=DM):
    """b (Aki 1965, Utsu ΔM/2 düzeltmesi), σ_b (Shi & Bolt 1982), a (N(≥Mc) için), N."""
    x = m[m >= mc - 1e-9]
    n = len(x)
    if n < 10:
        return None
    mean = x.mean()
    b = math.log10(math.e) / (mean - (mc - dm / 2))
    sb = 2.30 * b * b * math.sqrt(((x - mean) ** 2).sum() / (n * (n - 1)))
    return dict(n=n, b=b, sigma_b=sb, a=math.log10(n) + b * mc)


def weichert(m, mc, T, dm=DM):
    """Weichert (1980) EOB, tek tamlık dönemi (EMSC 1998–2026: tüm sınıflar için T aynı).
    Dönüş: b, σ_b, yıllık λ(≥Mc) ve σ. Tek dönemde Aki-Utsu'ya çok yakın olmalıdır (iç denetim)."""
    x = m[m >= mc - 1e-9]
    if len(x) < 10:
        return None
    edges = np.arange(mc, x.max() + dm + 1e-9, dm)
    cen = np.round(edges[:-1] + dm / 2 - dm / 2, 3)          # sınıf merkezi = alt kenar (0,1 ızgarası)
    n_i = np.array([((x >= lo - 1e-9) & (x < lo + dm - 1e-9)).sum() for lo in edges[:-1]], float)
    t_i = np.full_like(n_i, T)
    N = n_i.sum()
    beta = 2.0
    for _ in range(200):
        w = t_i * np.exp(-beta * cen)
        s0, s1, s2 = w.sum(), (w * cen).sum(), (w * cen * cen).sum()
        f = s1 / s0 - (n_i * cen).sum() / N
        fp = (s1 / s0) ** 2 - s2 / s0
        step = f / fp
        beta -= step
        if abs(step) < 1e-10:
            break
    w = t_i * np.exp(-beta * cen)
    s0, s1, s2 = w.sum(), (w * cen).sum(), (w * cen * cen).sum()
    var_beta = 1.0 / (N * (s2 / s0 - (s1 / s0) ** 2))
    lam = N / T        # tek dönemde λ(≥Mc) = N/T
    return dict(n=int(N), b=beta / math.log(10), sigma_b=math.sqrt(var_beta) / math.log(10),
                rate_ge_mc=lam, sigma_rate=math.sqrt(N) / T)


def poisson_ci(k, conf=0.95):
    """Kesin (Garwood) Poisson aralığı, olay sayısı için."""
    a = 1 - conf
    lo = 0.0 if k == 0 else stats.chi2.ppf(a / 2, 2 * k) / 2
    hi = stats.chi2.ppf(1 - a / 2, 2 * k + 2) / 2
    return lo, hi


def p_exceed(lam, t):
    return 1 - math.exp(-lam * t)


def km(a, b, c, d):
    return GK.haversine(a, b, c, d)


# ---------- ana analiz ----------
def main():
    raw = json.load(open('data/eq_historical.json', encoding='utf-8'))
    ev = [e for e in raw['events'] if e.get('src') == 'EMSC']
    assert all(e['mag'] >= 3.0 - 1e-9 for e in ev)
    t0, t1 = min(parse(e['time']) for e in ev), max(parse(e['time']) for e in ev)
    T = (t1 - t0).total_seconds() / (365.25 * 86400)

    gevs, gcl = GK.decluster(ev, 'mag')
    gk_ind = {e['id']: (not c) for e, c in zip(gevs, gcl)}
    revs, o = D.decluster(ev, XMEFF, 'zmap', 'mag')
    rb_cls = {e['id']: k for e, k in zip(revs, o['event_class'])}
    rb_cid = {e['id']: c for e, c in zip(revs, o['cluster_id'])}
    rb_ind = {i: k != 'dependent' for i, k in rb_cls.items()}
    res = o['res']
    rep_of = {k: revs[o['valid_index'][int(res.representative[k])]] for k in range(res.n_clusters)}
    byid = {e['id']: e for e in ev}

    # 1) kimlik karşılaştırması
    cat = {'ortak_bagimsiz': [], 'yalniz_gk74_bagimsiz': [], 'yalniz_rb_bagimsiz': [], 'ikisi_de_bagimli': []}
    for e in ev:
        g, r = gk_ind[e['id']], rb_ind[e['id']]
        cat['ortak_bagimsiz' if g and r else 'yalniz_gk74_bagimsiz' if g else 'yalniz_rb_bagimsiz' if r else 'ikisi_de_bagimli'].append(e['id'])
    import gzip
    with gzip.open(os.path.join(HERE, 'bagimsiz_olaylar.csv.gz'), 'wt', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['id', 'time', 'lat', 'lon', 'dep', 'mag', 'mtype', 'gk74', 'reasenberg', 'rb_kume', 'grup'])
        for e in sorted(ev, key=lambda e: e['time']):
            g, r = gk_ind[e['id']], rb_cls[e['id']]
            grp = next(k for k, v in cat.items() if e['id'] in set(v)) if False else (
                'ortak_bagimsiz' if g and r != 'dependent' else 'yalniz_gk74_bagimsiz' if g else
                'yalniz_rb_bagimsiz' if r != 'dependent' else 'ikisi_de_bagimli')
            w.writerow([e['id'], e['time'], e['lat'], e['lon'], e['dep'], e['mag'], e['mtype'],
                        'bagimsiz' if g else 'artci', r, rb_cid[e['id']], grp])

    # GK74 için "bastıran" olay (yalnız raporlama; GK74 kodunun pencere kuralı aynen)
    order = sorted(ev, key=lambda e: e['time'])

    def gk_parent(e):
        te, me = parse(e['time']), e['mag']
        for p in order:
            tp = parse(p['time'])
            if tp >= te:
                break
            if not gk_ind[p['id']] or p['mag'] <= me:
                continue
            T_days, D_km = GK.gk_window(p['mag'])
            if (te - tp).total_seconds() / 86400 <= T_days and km(p['lat'], p['lon'], e['lat'], e['lon']) <= D_km:
                return p
        return None

    # 2) M ≥ 6 ve M ≥ 7 farkları
    big = []
    for e in sorted((e for e in ev if e['mag'] >= 6.0), key=lambda e: e['time']):
        g, r = gk_ind[e['id']], rb_cls[e['id']]
        if g == (r != 'dependent'):
            continue
        gp = None if g else gk_parent(e)
        rp = rep_of.get(rb_cid[e['id']]) if r == 'dependent' else None
        big.append(dict(id=e['id'], time=e['time'], mag=e['mag'], mtype=e['mtype'], place=e['place'],
                        gk74='bağımsız' if g else 'artçı', reasenberg=r,
                        gk74_bastiran=(f"{gp['time'][:16]} M{gp['mag']} {gp['place']}" if gp else ''),
                        rb_temsilci=(f"{rp['time'][:16]} M{rp['mag']} {rp['place']}" if rp else ''),
                        rb_temsilciye_km=(round(km(rp['lat'], rp['lon'], e['lat'], e['lon']), 1) if rp else ''),
                        rb_temsilciye_saat=(round((parse(e['time']) - parse(rp['time'])).total_seconds() / 3600, 2) if rp else '')))
    with open(os.path.join(HERE, 'buyuk_farklar.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(big[0].keys()) if big else ['id']); w.writeheader(); w.writerows(big)

    # 3) DOUBLET adayları (işlevsel tanım; yalnız aday)
    m6 = sorted((e for e in ev if e['mag'] >= DOUBLET['mmin']), key=lambda e: e['time'])
    dbl = []
    for i, a in enumerate(m6):
        for b in m6[i + 1:]:
            dt = (parse(b['time']) - parse(a['time'])).total_seconds() / 86400
            if dt > DOUBLET['dt_days']:
                break
            d = km(a['lat'], a['lon'], b['lat'], b['lon'])
            if d <= DOUBLET['dkm'] and abs(a['mag'] - b['mag']) <= DOUBLET['dm']:
                dbl.append(dict(dkm_100_icinde=(d <= 100.0), olay1=f"{a['time'][:16]} M{a['mag']} {a['place']}", olay2=f"{b['time'][:16]} M{b['mag']} {b['place']}",
                                dt_gun=round(dt, 3), uzaklik_km=round(d, 1), dM=round(b['mag'] - a['mag'], 2),
                                gk74_ikinci=('bağımsız' if gk_ind[b['id']] else 'artçı'), rb_ikinci=rb_cls[b['id']],
                                gk74_birinci=('bağımsız' if gk_ind[a['id']] else 'artçı'), rb_birinci=rb_cls[a['id']],
                                ayni_rb_kumesi=(rb_cid[a['id']] == rb_cid[b['id']] and rb_cid[a['id']] >= 0),
                                yontemler_ayrisiyor=(gk_ind[b['id']] != rb_ind[b['id']]) or (gk_ind[a['id']] != rb_ind[a['id']])))
    with open(os.path.join(HERE, 'doublet_adaylari.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(dbl[0].keys()) if dbl else ['olay1']); w.writeheader(); w.writerows(dbl)

    # 4–7) her katalog AYRI: b, a, Weichert, Poisson
    cats = {'ham': [e for e in ev], 'gk74': [e for e in ev if gk_ind[e['id']]], 'reasenberg': [e for e in ev if rb_ind[e['id']]]}
    params = {}
    for name, lst in cats.items():
        m = np.array([e['mag'] for e in lst])
        row = dict(n=len(lst))
        for mc in MC_LIST:
            au, wh = aki_utsu(m, mc), weichert(m, mc, T)
            row[f'mc{mc}'] = dict(aki_utsu=au, weichert=wh)
        for thr in M_THR:
            k = int((m >= thr - 1e-9).sum())
            lo, hi = poisson_ci(k)
            lam, llo, lhi = k / T, lo / T, hi / T
            row[f'M{thr:g}'] = dict(
                sayi=k, lambda_yil=lam, lambda_95=[llo, lhi], tekrarlanma_yil=(1 / lam if lam else None),
                tekrarlanma_95=[(1 / lhi if lhi else None), (1 / llo if llo else None)],
                P={f'{t}y': dict(deger=p_exceed(lam, t), aralik_95=[p_exceed(llo, t), p_exceed(lhi, t)]) for t in HORIZONS})
            # G–R (Weichert, Mc 3,2) ile dışdeğerleme — karşılaştırma için
            wh = row['mc3.2']['weichert']
            lam_gr = wh['rate_ge_mc'] * 10 ** (-wh['b'] * (thr - 3.2))
            row[f'M{thr:g}']['lambda_GR_weichert_mc3.2'] = lam_gr
            row[f'M{thr:g}']['P_GR'] = {f'{t}y': p_exceed(lam_gr, t) for t in HORIZONS}
        params[name] = row

    out = dict(
        tanim=dict(katalog='data/eq_historical.json src=EMSC', n=len(ev), donem=[t0.isoformat(), t1.isoformat()], T_yil=T,
                   sinirlar='33–45°N, 23–48°E dikdörtgeni (İran, Yunanistan, Ege dahil)',
                   gk74='scripts/decluster_gk74.py (yalnız artçı, episantral)', reasenberg=f'zmap, xmeff={XMEFF}, modül {D.R.__version__}',
                   module_sha256=D.module_sha256(), dm=DM, doublet=DOUBLET),
        kimlik={k: len(v) for k, v in cat.items()},
        buyuk_farklar=big, doublet_adaylari=dbl, parametreler=params)
    json.dump(out, open(os.path.join(HERE, 'sonuc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)

    # şekil: G–R (her katalog ayrı)
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=150)
    for name, col in (('ham', '#888888'), ('gk74', '#7c3aed'), ('reasenberg', '#ea580c')):
        m = np.array([e['mag'] for e in cats[name]])
        ms = np.arange(3.0, m.max() + 0.05, 0.1)
        ax.semilogy(ms, [(m >= x - 1e-9).sum() / T for x in ms], 'o', ms=2.6, color=col,
                    label={'ham': 'Ham katalog', 'gk74': 'GK74 bağımsız', 'reasenberg': 'Reasenberg bağımsız'}[name])
    ax.axvline(3.2, color='#999', lw=.8, ls='--'); ax.text(3.22, 0.02, 'Mc 3,2', fontsize=7, color='#666')
    ax.set_xlabel('Büyüklük M (karışık ölçek)'); ax.set_ylabel('Yıllık N(≥M)'); ax.grid(alpha=.3, which='both')
    ax.set_title(f'EMSC {t0.year}–{t1.year}: üç katalog ayrı (birleştirilmedi)', fontsize=9); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'fig_gr.png')); plt.close(fig)

    # ekran özeti
    print(f"N={len(ev)}  T={T:.2f} yıl  kimlik: {out['kimlik']}")
    print('\nM ≥ 6 sınıfı farklı olaylar:')
    for b in big:
        print(f"  {b['time'][:16]} M{b['mag']} {b['place'][:26]:26s} GK74 {b['gk74']:9s} RB {b['reasenberg']:14s} "
              f"{('← ' + b['gk74_bastiran']) if b['gk74_bastiran'] else ''}{('← RB temsilci ' + b['rb_temsilci'] + f' ({b[chr(114)+"b_temsilciye_km"]} km, {b["rb_temsilciye_saat"]} sa)') if b['rb_temsilci'] else ''}")
    print(f'\nDOUBLET adayları (M≥{DOUBLET["mmin"]}, |ΔM|≤{DOUBLET["dm"]}, Δt≤{DOUBLET["dt_days"]:.0f} g, Δd≤{DOUBLET["dkm"]:.0f} km): {len(dbl)}')
    for d in dbl:
        print(f"  {'' if d['dkm_100_icinde'] else '[100–150 km] '}{d['olay1'][:45]:45s} → {d['olay2'][:45]:45s} {d['dt_gun']:7.2f} g {d['uzaklik_km']:5.1f} km | 2. olay GK74 {d['gk74_ikinci']}, RB {d['rb_ikinci']}{'  ◄ ayrışıyor' if d['yontemler_ayrisiyor'] else ''}")
    print('\nParametreler (her katalog ayrı):')
    for name, row in params.items():
        for mc in MC_LIST:
            au, wh = row[f'mc{mc}']['aki_utsu'], row[f'mc{mc}']['weichert']
            print(f"  {name:10s} Mc {mc}: N {au['n']:6d}  b(Aki) {au['b']:.3f}±{au['sigma_b']:.3f}  a {au['a']:.3f}  | b(Weichert) {wh['b']:.3f}±{wh['sigma_b']:.3f}  λ(≥Mc) {wh['rate_ge_mc']:.1f}/yıl")
        for thr in M_THR:
            r = row[f'M{thr:g}']
            print(f"  {name:10s} M≥{thr:g}: sayı {r['sayi']:3d}  λ {r['lambda_yil']:.3f}/yıl [{r['lambda_95'][0]:.3f}, {r['lambda_95'][1]:.3f}]  "
                  f"P1y {100*r['P']['1y']['deger']:.1f}% [{100*r['P']['1y']['aralik_95'][0]:.1f}, {100*r['P']['1y']['aralik_95'][1]:.1f}]  "
                  f"P10y {100*r['P']['10y']['deger']:.1f}%  P50y {100*r['P']['50y']['deger']:.2f}%  | G–R λ {r['lambda_GR_weichert_mc3.2']:.3f}")


if __name__ == '__main__':
    main()


# ---------- duyarlılık: otoriter Mw (data/mw_authority.json, yalnız 'verified', eşleşme ±60 s ve 50 km) ----------
def mwauth_sensitivity():
    raw = json.load(open('data/eq_historical.json', encoding='utf-8'))
    ev = [dict(e) for e in raw['events'] if e.get('src') == 'EMSC']
    A = json.load(open('data/mw_authority.json', encoding='utf-8'))
    dt_s, dkm = A['match']['dt_s'], A['match']['dist_km']
    changed = []
    for a in A['entries']:
        if a['status'] != 'verified':
            continue
        ta = parse(a['time_utc'])
        cand = [e for e in ev if abs((parse(e['time']) - ta).total_seconds()) <= dt_s and km(a['lat'], a['lon'], e['lat'], e['lon']) <= dkm]
        if not cand:
            continue
        e = max(cand, key=lambda e: e['mag'])
        changed.append(dict(ad=a['name'], emsc=f"{e['mag']} {e['mtype']}", otoriter_mw=a['mw']))
        e['mag'] = a['mw']
    t0, t1 = min(parse(e['time']) for e in ev), max(parse(e['time']) for e in ev)
    T = (t1 - t0).total_seconds() / (365.25 * 86400)
    gevs, gcl = GK.decluster(ev, 'mag'); gk = {e['id']: (not c) for e, c in zip(gevs, gcl)}
    revs, o = D.decluster(ev, XMEFF, 'zmap', 'mag'); rb = {e['id']: (k != 'dependent') for e, k in zip(revs, o['event_class'])}
    out = dict(degistirilen=changed, T_yil=T, sonuc={})
    for thr in M_THR:
        row = {}
        for name, ind in (('ham', None), ('gk74', gk), ('reasenberg', rb)):
            big = [e for e in ev if e['mag'] >= thr - 1e-9 and (ind is None or ind[e['id']])]
            k = len(big); lo, hi = poisson_ci(k)
            row[name] = dict(sayi=k, lambda_yil=k / T, lambda_95=[lo / T, hi / T],
                             P1y=p_exceed(k / T, 1), P1y_95=[p_exceed(lo / T, 1), p_exceed(hi / T, 1)],
                             P50y=p_exceed(k / T, 50), olaylar=[f"{e['time'][:10]} M{e['mag']} {e['place'][:24]}" for e in sorted(big, key=lambda e: e['time'])] if thr >= 7 else None)
        diff = [e for e in ev if e['mag'] >= thr - 1e-9 and gk[e['id']] != rb[e['id']]]
        row['sinifi_farkli'] = [f"{e['time'][:16]} M{e['mag']} {e['place'][:24]} GK74 {'bağımsız' if gk[e['id']] else 'artçı'} / RB {'bağımsız' if rb[e['id']] else 'bağımlı'}" for e in diff]
        out['sonuc'][f'M{thr:g}'] = row
    json.dump(out, open(os.path.join(HERE, 'sonuc_otoriter_mw.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n=== Duyarlılık: otoriter Mw ===')
    for c in changed:
        print(f"  {c['ad']:28s} EMSC {c['emsc']:10s} → Mw {c['otoriter_mw']}")
    for thr in M_THR:
        r = out['sonuc'][f'M{thr:g}']
        for name in ('ham', 'gk74', 'reasenberg'):
            x = r[name]
            print(f"  M≥{thr:g} {name:10s} sayı {x['sayi']:3d}  λ {x['lambda_yil']:.3f} [{x['lambda_95'][0]:.3f}, {x['lambda_95'][1]:.3f}]  P1y {100*x['P1y']:.1f}% [{100*x['P1y_95'][0]:.1f}, {100*x['P1y_95'][1]:.1f}]")
        for d in r['sinifi_farkli']:
            print('     fark:', d)
        if thr >= 7:
            print('     GK74 M≥7:', r['gk74']['olaylar']); print('     RB   M≥7:', r['reasenberg']['olaylar'])


if __name__ == '__main__' and '--mwauth' in sys.argv:
    mwauth_sensitivity()


# ---------- indirilebilir veri ürünleri (yöntem başına AYRI; asla birleştirilmez) ----------
def products(fmt=('csv',)):
    """5 ürün: GK74 bağımsız/bağımlı, Reasenberg bağımsız/bağımlı, yöntem farkları. Ham kimlik korunur.
    classification: independent | dependent; dependent_role: aftershock_candidate | foreshock_candidate
    (temsilci/bastıran olaya göre zaman sırası; fiziksel nedensellik iddiası değildir)."""
    import gzip, hashlib
    raw_bytes = open('data/eq_historical.json', 'rb').read()
    raw = json.loads(raw_bytes.decode('utf-8'))
    ev = [e for e in raw['events'] if e.get('src') == 'EMSC']
    gevs, gcl = GK.decluster(ev, 'mag')
    gdep = {e['id'] for e, c in zip(gevs, gcl) if c}
    # GK74 bastıran olay: GK74'ün kendi kuralı (decluster_gk74.gk_window, haversine, ileri pencere, daha büyük ve bağımsız olay)
    order = sorted(ev, key=lambda e: e['time'])
    tms = [parse(e['time']).timestamp() for e in order]
    gpar = {}
    for i, p in enumerate(order):
        if p['id'] in gdep:
            continue
        Td, Dk = GK.gk_window(p['mag'])
        for j in range(i + 1, len(order)):
            if tms[j] - tms[i] > Td * 86400:
                break
            q = order[j]
            if q['id'] in gdep and q['id'] not in gpar and q['mag'] < p['mag'] and km(p['lat'], p['lon'], q['lat'], q['lon']) <= Dk:
                gpar[q['id']] = p['id']
    missing = len(gdep - set(gpar))
    assert missing == 0, f'{missing} GK74 bağımlısı için bastıran olay bulunamadı (kural uyuşmazlığı)'
    revs, o = D.decluster(ev, XMEFF, 'zmap', 'mag')
    res = o['res']
    rep_id = {k: revs[o['valid_index'][int(res.representative[k])]]['id'] for k in range(res.n_clusters)}
    rcls = {e['id']: k for e, k in zip(revs, o['event_class'])}
    rcid = {e['id']: c for e, c in zip(revs, o['cluster_id'])}
    tm = {e['id']: parse(e['time']) for e in ev}
    base = lambda e: dict(event_id=e['id'], origin_time=e['time'], latitude=e['lat'], longitude=e['lon'], depth=e['dep'],
                          magnitude=e['mag'], magnitude_type=e['mtype'], place=e['place'])
    rows = {k: [] for k in ('gk74_bagimsiz', 'gk74_bagimli', 'reasenberg_bagimsiz', 'reasenberg_bagimli', 'yontem_farklari')}
    for e in order:
        g = dict(base(e), method='GK74', classification='dependent' if e['id'] in gdep else 'independent', cluster_id='',
                 representative_event_id=gpar.get(e['id'], ''),
                 dependent_role='aftershock_candidate' if e['id'] in gdep else '')
        rc = rcls[e['id']]; cid = rcid[e['id']]
        rep = rep_id.get(cid, '') if cid >= 0 else ''
        r = dict(base(e), method='Reasenberg1985', classification='dependent' if rc == 'dependent' else 'independent',
                 cluster_id=cid if cid >= 0 else '', representative_event_id=rep,
                 dependent_role=('' if rc != 'dependent' else 'aftershock_candidate' if tm[e['id']] > tm[rep] else 'foreshock_candidate'),
                 reasenberg_class=rc)
        rows['gk74_bagimli' if g['classification'] == 'dependent' else 'gk74_bagimsiz'].append(g)
        rows['reasenberg_bagimli' if r['classification'] == 'dependent' else 'reasenberg_bagimsiz'].append(r)
        if g['classification'] != r['classification']:
            rows['yontem_farklari'].append(dict(base(e), gk74_classification=g['classification'], gk74_representative_event_id=g['representative_event_id'],
                                                reasenberg_classification=r['classification'], reasenberg_class=rc, reasenberg_cluster_id=r['cluster_id'],
                                                reasenberg_representative_event_id=rep,
                                                group='yalniz_gk74_bagimsiz' if g['classification'] == 'independent' else 'yalniz_rb_bagimsiz'))
    outdir = os.path.join(HERE, 'urunler'); os.makedirs(outdir, exist_ok=True)
    files = {}
    for name, lst in rows.items():
        if 'csv' in fmt:
            p = os.path.join(outdir, f'{name}.csv.gz')
            with gzip.open(p, 'wt', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=list(lst[0].keys())); w.writeheader(); w.writerows(lst)
            files[f'{name}.csv.gz'] = dict(n=len(lst), sha256=hashlib.sha256(open(p, 'rb').read()).hexdigest())
        if 'geojson' in fmt:
            p = os.path.join(outdir, f'{name}.geojson')
            json.dump(dict(type='FeatureCollection', features=[dict(type='Feature', geometry=dict(type='Point', coordinates=[x['longitude'], x['latitude'], -x['depth']]),
                      properties=x) for x in lst]), open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        if 'json' in fmt:
            json.dump(lst, open(os.path.join(outdir, f'{name}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    meta = dict(
        urun='Ayrı ayrıştırılmış kataloglar — GK74 ve Reasenberg (birleştirilmez)', olusturma='2026-11-08',
        katalog=dict(dosya='data/eq_historical.json', sha256=hashlib.sha256(raw_bytes).hexdigest(), generated=raw.get('generated'),
                     kaynak='EMSC', n=len(ev), donem=[order[0]['time'], order[-1]['time']], buyukluk_esigi=3.0,
                     sinirlar='33–45°K, 23–48°D', buyukluk_olcegi='karışık (ML/mb/Ms/Mw); otoriter Mw uygulanmadı'),
        yontemler=dict(
            GK74=dict(betik='scripts/decluster_gk74.py', kural='Gardner & Knopoff (1974) Tablo 1; yalnız ileri pencere (artçı), episantral mesafe, UTC',
                      representative_event_id='olayı pencere içinde bağımlı kılan daha büyük bağımsız olay (GK74 kuralıyla, raporlama için)'),
            Reasenberg1985=dict(modul='scripts/reasenberg.py', surum=D.R.__version__, sha256=D.module_sha256(), adaptor='scripts/decluster_reasenberg.py',
                                kural='zmap (varsayılan)', parametreler=D.json_safe(dict(res.params.__dict__)), xmeff=XMEFF,
                                representative_event_id='kümenin en büyük olayı (temsilci)')),
        mc=dict(site_tahmini='MAXC+0,2 = 3,2 (tüm EMSC)', not_='xmeff = 3,0 statik ürünle aynı; Mc duyarlılığı açık iş'),
        alanlar=['event_id', 'origin_time', 'latitude', 'longitude', 'depth', 'magnitude', 'magnitude_type', 'place', 'method',
                 'classification', 'cluster_id', 'representative_event_id', 'dependent_role', 'reasenberg_class'],
        uyarilar=['bağımlı ≠ artçı: dependent_role yalnız temsilci/bastıran olaya göre zaman sırasıdır, fiziksel nedensellik iddiası değildir',
                  'GK74 bu uygulamada yalnız artçı ayıklar; GK74 bağımlıları tanım gereği "aftershock_candidate"dır',
                  'iki yöntemin sonuçları tek bir ortak artçı kataloğunda birleştirilmemelidir',
                  'Coulomb modellemesinin yerine geçmez; gözlemsel sınama verisidir', 'deprem tahmini için değildir'],
        dosyalar=files)
    json.dump(meta, open(os.path.join(outdir, 'metadata.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n=== Veri ürünleri ===')
    for k, v in files.items():
        print(f"  {k:32s} {v['n']:6d} satır")
    print('  GK74 bastıran olayı bulunamayan bağımlı: 0 (kural tutarlı)')


if __name__ == '__main__' and '--urunler' in sys.argv:
    products(tuple(a.split('=')[1].split(',') for a in sys.argv if a.startswith('--format='))[0] if any(a.startswith('--format=') for a in sys.argv) else ('csv',))
