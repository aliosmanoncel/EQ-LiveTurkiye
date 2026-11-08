"""
donemsel_mc_weichert.py — 3. tur (ikinci aşama): Türkiye'de dönemsel Mc(t) ve çok dönemli Weichert, GK74 ↔ Reasenberg.

Soru: Δb (RB − GK74) ≈ +0,13, dönemsel tamlık hesaba katıldığında da istatistiksel olarak anlamlı mı?
Kapsam: Türkiye 30 km (turkiye_sinir_30km.geojson), EMSC 1998–2026, M ≥ 3,0, EMSC büyüklüğü (aynı ölçek).
Sınıflar: iki yöntem Türkiye alt kümesinde ayrı çalıştırılır ("yeniden"); kataloglar birleştirilmez.
Mc(t): HAM Türkiye kataloğunda, her dönem için (tamlık kataloğun özelliği) → aynı Mc iki kataloğa uygulanır.
  Tahminciler: MAXC+0,2 (sitenin computeMcSrc kuralı), kümülatif GFT (Wiemer & Wyss 2000; R ≥ %95, yoksa %90,
  yoksa MAXC+0,2), MAXC+0,2 bootstrap (500) %84'lük üst değeri (ihtiyatlı).
Dönem başına: N(≥Mc), b (Aki–Utsu, ΔM=0,1) ± σ (Shi & Bolt), %95 aralık, yıllık a = log10(N/Tp) + b·Mc; Δb ve σ_Δb.
Birleşik: dönemlerin ters-varyans ağırlıklı Δb'si + heterojenlik (χ², Cochran Q).
Weichert (1980): çok dönemli; bir 0,1 büyüklük sınıfı yalnız Mc(dönem) ≤ sınıf olan dönemlerde sayılır.
Duyarlılık: dönem uzunluğu 4/5/7 yıl, 5 yılda başlangıç kaydırma (+2 yıl), tahminci değişimi, Mc + 0,1.
Çıktı: donemsel_sonuc.json, fig_donemsel.png, ekran özeti.
"""
import json, math, os, sys
from datetime import datetime, timezone

import numpy as np
from shapely.geometry import Point
from shapely.prepared import prep
from scipy import stats

sys.path.insert(0, 'scripts')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bok_analiz import parse, aki_utsu  # noqa: E402
from turkiye_sinir import load  # noqa: E402
from turkiye_alt_kume import classify, mc_site  # noqa: E402

DM = 0.1
RNG = np.random.default_rng(20261108)


def gft(m, r_req=(95, 90)):
    """Kümülatif GFT: aday Mc'ler için Aki b ile sentetik kümülatif dağılım; R = 100 − 100·Σ|B−S|/ΣB."""
    m = np.asarray(m)
    if len(m) < 50:
        return None, None
    best = {}
    for mc in np.round(np.arange(3.0, min(m.max() - 0.5, 5.0) + 1e-9, 0.1), 1):
        x = m[m >= mc - 1e-9]
        if len(x) < 50:
            break
        b = math.log10(math.e) / (x.mean() - (mc - DM / 2))
        a = math.log10(len(x)) + b * mc
        bins = np.round(np.arange(mc, x.max() + 1e-9, DM), 1)
        B = np.array([(x >= v - 1e-9).sum() for v in bins], float)
        S = 10 ** (a - b * bins)
        R = 100 - 100 * np.abs(B - S).sum() / B.sum()
        best[float(mc)] = R
    for req in r_req:
        ok = [mc for mc, R in sorted(best.items()) if R >= req]
        if ok:
            return ok[0], req
    return None, None


def mc_estimates(m):
    m = np.asarray(m)
    out = dict(maxc=mc_site(m) if len(m) >= 10 else None)
    g, req = gft(m)
    out['gft'] = g; out['gft_R'] = req
    if len(m) >= 50:
        bs = [mc_site(RNG.choice(m, len(m), replace=True)) for _ in range(500)]
        out['maxc_boot_p16'], out['maxc_boot_p84'] = float(np.percentile(bs, 16)), float(np.percentile(bs, 84))
    return out


def periods(start, end, length, offset=0):
    """[t0, t1) yıl sınırları; ilk dönem başlangıcı start, offset > 0 ise ilk dönem kısalır."""
    edges = [start]
    y = start + (offset if offset else length)
    while y < end:
        edges.append(y); y += length
    edges.append(end)
    return list(zip(edges[:-1], edges[1:]))


def yfrac(dt):
    y0 = datetime(dt.year, 1, 1, tzinfo=timezone.utc); y1 = datetime(dt.year + 1, 1, 1, tzinfo=timezone.utc)
    return dt.year + (dt - y0).total_seconds() / (y1 - y0).total_seconds()


def weichert_multi(m_by_period, mc_by_period, dur_by_period, mref):
    """Çok dönemli Weichert (1980). Sınıf alt kenarı x; dönem p katkı verir ⇔ mc_p ≤ x."""
    allm = np.concatenate([m for m in m_by_period if len(m)])
    lo = min(mc_by_period)
    cen = np.round(np.arange(lo, allm.max() + 1e-9, DM), 1)
    n_i = np.zeros(len(cen)); t_i = np.zeros(len(cen))
    for m, mc, dur in zip(m_by_period, mc_by_period, dur_by_period):
        for k, x in enumerate(cen):
            if x >= mc - 1e-9:
                t_i[k] += dur
                n_i[k] += ((m >= x - 1e-9) & (m < x + DM - 1e-9)).sum()
    keep = t_i > 0
    cen, n_i, t_i = cen[keep], n_i[keep], t_i[keep]
    N = n_i.sum(); beta = 2.0
    for _ in range(500):
        w = t_i * np.exp(-beta * cen); s0, s1, s2 = w.sum(), (w * cen).sum(), (w * cen * cen).sum()
        f = s1 / s0 - (n_i * cen).sum() / N; fp = (s1 / s0) ** 2 - s2 / s0
        step = f / fp; beta -= step
        if abs(step) < 1e-12:
            break
    w = t_i * np.exp(-beta * cen); s0, s1, s2 = w.sum(), (w * cen).sum(), (w * cen * cen).sum()
    sb = math.sqrt(1.0 / (N * (s2 / s0 - (s1 / s0) ** 2))) / math.log(10)
    # λ(≥ alt sınıf) = N / Σ(t_i e^{-βm_i}) · e^{-β m_lo} ; mref'e taşı
    lam_lo = N * math.exp(-beta * cen[0]) / s0
    lam_ref = lam_lo * math.exp(-beta * (mref - cen[0]))
    return dict(b=beta / math.log(10), sigma_b=sb, N=int(N), m_alt=float(cen[0]), lambda_ge_mref=lam_ref,
                sigma_lambda=lam_ref / math.sqrt(N), a_yillik=math.log10(lam_ref) + beta / math.log(10) * mref)


def analyse(ev, gk, rb, per, est, mc_add=0.0):
    rows = []
    mp = {k: [] for k in ('gk74', 'reasenberg')}; mcs = []; durs = []
    for (y0, y1) in per:
        sub = [e for e in ev if y0 <= e['_y'] < y1]
        dur = y1 - y0
        m_raw = np.array([e['mag'] for e in sub])
        est_all = mc_estimates(m_raw)
        if est == 'max_gft_maxc':
            mc = max(v for v in (est_all['gft'], est_all['maxc']) if v is not None)
        elif isinstance(est, float):
            mc = est
        else:
            mc = est_all[est] if est_all.get(est) is not None else est_all['maxc']
        mc = round(mc + mc_add, 1)
        types = {}
        for e in sub:
            t = (e['mtype'] or '?').lower(); types[t] = types.get(t, 0) + 1
        row = dict(donem=f'{y0:g}–{y1:g}', sure_yil=dur, n_ham=len(sub), mc=mc, mc_tahminleri=est_all,
                   olcek_payi={k: round(v / len(sub), 3) for k, v in sorted(types.items(), key=lambda kv: -kv[1])[:5]})
        for name, ind in (('gk74', gk), ('reasenberg', rb)):
            m = np.array([e['mag'] for e in sub if ind[e['id']]])
            au = aki_utsu(m, mc)
            if au:
                au['b95'] = [au['b'] - 1.96 * au['sigma_b'], au['b'] + 1.96 * au['sigma_b']]
                au['a_yillik'] = math.log10(au['n'] / dur) + au['b'] * mc
            row[name] = au
            mp[name].append(m)
        g, r = row['gk74'], row['reasenberg']
        if g and r:
            d = r['b'] - g['b']; s = math.hypot(g['sigma_b'], r['sigma_b'])
            row['delta_b'] = dict(db=d, sigma=s, z=d / s, p=2 * (1 - stats.norm.cdf(abs(d / s))))
        rows.append(row); mcs.append(mc); durs.append(dur)
    ok = [r['delta_b'] for r in rows if 'delta_b' in r]
    w = np.array([1 / x['sigma'] ** 2 for x in ok]); d = np.array([x['db'] for x in ok])
    mean = float((w * d).sum() / w.sum()); se = float(1 / math.sqrt(w.sum()))
    Q = float((w * (d - mean) ** 2).sum()); dfree = len(ok) - 1
    comb = dict(db=mean, sigma=se, z=mean / se, p=2 * (1 - stats.norm.cdf(abs(mean / se))), Q=Q, df=dfree,
                p_heterojenlik=float(1 - stats.chi2.cdf(Q, dfree)) if dfree > 0 else None, n_donem=len(ok))
    mref = max(mcs)
    W = {name: weichert_multi(mp[name], mcs, durs, mref) for name in mp}
    W['delta_b'] = dict(db=W['reasenberg']['b'] - W['gk74']['b'], sigma=math.hypot(W['reasenberg']['sigma_b'], W['gk74']['sigma_b']))
    W['delta_b']['z'] = W['delta_b']['db'] / W['delta_b']['sigma']
    W['mref'] = mref
    return dict(donemler=rows, birlesik=comb, weichert=W)


def main():
    raw = json.load(open('data/eq_historical.json', encoding='utf-8'))
    ev = [e for e in raw['events'] if e.get('src') == 'EMSC']
    poly, _ = load(30); P = prep(poly)
    ev = [dict(e, _y=yfrac(parse(e['time']))) for e in ev if P.contains(Point(e['lon'], e['lat']))]
    gk, rb = classify(ev)
    t_start, t_end = math.floor(min(e['_y'] for e in ev)), max(e['_y'] for e in ev) + 1e-6
    variants = {
        'ana: 5 yıl, MAXC+0,2': dict(per=periods(t_start, t_end, 5), est='maxc'),
        '5 yıl, GFT': dict(per=periods(t_start, t_end, 5), est='gft'),
        '5 yıl, MAXC bootstrap %84': dict(per=periods(t_start, t_end, 5), est='maxc_boot_p84'),
        '5 yıl, MAXC+0,2 +0,1': dict(per=periods(t_start, t_end, 5), est='maxc', mc_add=0.1),
        '5 yıl, max(GFT, MAXC+0,2)': dict(per=periods(t_start, t_end, 5), est='max_gft_maxc'),
        '5 yıl, Mc = 3,5 sabit': dict(per=periods(t_start, t_end, 5), est=3.5),
        '4 yıl, MAXC+0,2': dict(per=periods(t_start, t_end, 4), est='maxc'),
        '7 yıl, MAXC+0,2': dict(per=periods(t_start, t_end, 7), est='maxc'),
        '5 yıl kaydırılmış (+2), MAXC+0,2': dict(per=periods(t_start, t_end, 5, offset=2), est='maxc'),
    }
    out = dict(kapsam='Türkiye 30 km, EMSC, M≥3,0, EMSC büyüklüğü', n=len(ev), donem=[t_start, t_end], varyantlar={})
    for name, v in variants.items():
        out['varyantlar'][name] = analyse(ev, gk, rb, v['per'], v['est'], v.get('mc_add', 0.0))
    json.dump(out, open(os.path.join(HERE, 'donemsel_sonuc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)

    A = out['varyantlar']['ana: 5 yıl, MAXC+0,2']
    print(f"Türkiye 30 km: N={len(ev)}  dönem {t_start}–{t_end:.2f}\n=== Ana: 5 yıllık dönemler, Mc = MAXC+0,2 (ham katalogda) ===")
    print(f"{'dönem':12s} {'N ham':>6s} {'Mc':>4s} {'GFT':>4s} {'boot16–84':>10s} | {'N GK':>5s} {'b GK [95]':>20s} {'a GK':>5s} | {'N RB':>5s} {'b RB [95]':>20s} {'a RB':>5s} | {'Δb':>6s} {'z':>5s}")
    for r in A['donemler']:
        g, b, e = r['gk74'], r['reasenberg'], r['mc_tahminleri']
        print(f"{r['donem']:12s} {r['n_ham']:6d} {r['mc']:4.1f} {e['gft'] if e['gft'] else '—':>4} {e.get('maxc_boot_p16','—')}–{e.get('maxc_boot_p84','—')} | "
              f"{g['n']:5d} {g['b']:.3f} [{g['b95'][0]:.2f},{g['b95'][1]:.2f}] {g['a_yillik']:5.2f} | {b['n']:5d} {b['b']:.3f} [{b['b95'][0]:.2f},{b['b95'][1]:.2f}] {b['a_yillik']:5.2f} | "
              f"{r['delta_b']['db']:+.3f} {r['delta_b']['z']:5.1f}")
    c = A['birlesik']; W = A['weichert']
    print(f"Birleşik (ters-varyans): Δb = {c['db']:+.3f} ± {c['sigma']:.3f}  z = {c['z']:.1f}  p = {c['p']:.1e} | heterojenlik Q = {c['Q']:.1f} (df {c['df']}), p = {c['p_heterojenlik']:.3f}")
    print(f"Weichert çok dönemli: GK74 b {W['gk74']['b']:.3f}±{W['gk74']['sigma_b']:.3f}, a {W['gk74']['a_yillik']:.2f} | RB b {W['reasenberg']['b']:.3f}±{W['reasenberg']['sigma_b']:.3f}, a {W['reasenberg']['a_yillik']:.2f} | Δb {W['delta_b']['db']:+.3f} (z {W['delta_b']['z']:.1f}); λ(≥{W['mref']}) GK {W['gk74']['lambda_ge_mref']:.1f}/yıl, RB {W['reasenberg']['lambda_ge_mref']:.1f}/yıl")
    for vn in ('5 yıl, max(GFT, MAXC+0,2)', '5 yıl, Mc = 3,5 sabit'):
        print(f'\n=== {vn} ===')
        for r in out['varyantlar'][vn]['donemler']:
            g, b = r['gk74'], r['reasenberg']
            print(f"{r['donem']:12s} Mc {r['mc']:.1f} | GK N {g['n']:5d} b {g['b']:.3f}±{g['sigma_b']:.3f} | RB N {b['n']:5d} b {b['b']:.3f}±{b['sigma_b']:.3f} | Δb {r['delta_b']['db']:+.3f} z {r['delta_b']['z']:.1f} | ölçek {r['olcek_payi']}")
    print('\n=== Duyarlılık ===')
    for name, V in out['varyantlar'].items():
        c, W = V['birlesik'], V['weichert']
        print(f"{name:34s} dönem {c['n_donem']}  Mc {[r['mc'] for r in V['donemler']]}  birleşik Δb {c['db']:+.3f}±{c['sigma']:.3f} (z {c['z']:.1f}, heterojenlik p {c['p_heterojenlik']:.2f})  Weichert Δb {W['delta_b']['db']:+.3f} (z {W['delta_b']['z']:.1f})")

    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(3, 1, figsize=(7, 8), dpi=150, sharex=True)
    x = [(float(r['donem'].split('–')[0]) + float(r['donem'].split('–')[1])) / 2 for r in A['donemler']]
    axs[0].step([float(r['donem'].split('–')[0]) for r in A['donemler']] + [float(A['donemler'][-1]['donem'].split('–')[1])],
                [r['mc'] for r in A['donemler']] + [A['donemler'][-1]['mc']], where='post', color='#333', label='Mc (MAXC+0,2)')
    axs[0].plot(x, [r['mc_tahminleri']['gft'] for r in A['donemler']], 's', color='#0ea5e9', ms=4, label='GFT')
    axs[0].set_ylabel('Mc(t)'); axs[0].legend(fontsize=7); axs[0].grid(alpha=.3)
    for name, col, dx in (('gk74', '#7c3aed', -0.3), ('reasenberg', '#ea580c', 0.3)):
        axs[1].errorbar([v + dx for v in x], [r[name]['b'] for r in A['donemler']], yerr=[1.96 * r[name]['sigma_b'] for r in A['donemler']],
                        fmt='o', ms=4, capsize=2, color=col, label={'gk74': 'GK74', 'reasenberg': 'Reasenberg'}[name])
    axs[1].set_ylabel('b (±%95)'); axs[1].legend(fontsize=7); axs[1].grid(alpha=.3)
    axs[2].errorbar(x, [r['delta_b']['db'] for r in A['donemler']], yerr=[1.96 * r['delta_b']['sigma'] for r in A['donemler']], fmt='o', ms=4, capsize=2, color='#111')
    c = A['birlesik']; axs[2].axhline(c['db'], color='#dc2626', lw=1, label=f"birleşik Δb {c['db']:+.3f} ± {1.96*c['sigma']:.3f}")
    axs[2].axhline(0, color='#999', lw=.7, ls='--'); axs[2].set_ylabel('Δb = b(RB) − b(GK74)'); axs[2].legend(fontsize=7); axs[2].grid(alpha=.3)
    axs[2].set_xlabel('Yıl'); fig.suptitle('Türkiye (30 km), EMSC: dönemsel Mc ve b — iki katalog ayrı', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'fig_donemsel.png')); plt.close(fig)


if __name__ == '__main__':
    main()
