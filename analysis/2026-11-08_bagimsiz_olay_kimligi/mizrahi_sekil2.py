"""
mizrahi_sekil2.py — Mizrahi vd. (2021, SRL 92(4), 2333–2342) Şekil 2'nin Türkiye 30 km alt kümesinde karşılığı.

  (a) M ≥ Mc ana şokların zamana göre kümülatif sayısı: tam katalog, GK74, Reasenberg.
  (b) Tamamlayıcı kümülatif frekans fonksiyonu (CCFF), N(≥m), gözlenen.
  (c) Uydurulmuş G–R doğruları: Aki–Utsu b, a = log10 N(≥Mc) + b·Mc.
  (d) r(m) = N_ana(≥m) / N(≥m): gözlenen ve G–R yaklaşımı r̂(m) = 10^((a_d − a) − (b_d − b)·m);
      m_x = r̂(m_x) = 1 olduğu büyüklük (Mizrahi vd. Eş. 3–4). r > 1 fiziksel olarak olanaksızdır
      (ayrıştırılmış katalog tam katalogdan fazla olay içeremez).
Ölçekler: H0 ham EMSC (Mc 3,2) ve H2+A (sitenin combined_dispatch_md_eqml + otoriter Mw; Mc 3,3) — 5. tur ile aynı.
Farklar (makaleye göre): bölge/katalog farklı; GK74 burada YALNIZ ileri pencere (öncü işaretlemez), Reasenberg
zmap kuralı (sabit v0.3.0, xmeff 3,0). Ham katalog değişmez, iki katalog birleştirilmez.
Çıktı: fig_mizrahi2_H0.png, fig_mizrahi2_H2A.png, mizrahi_sekil2.json.
"""
import json, math, os, sys

import numpy as np
from shapely.geometry import Point
from shapely.prepared import prep

sys.path.insert(0, 'scripts')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bok_analiz import parse, aki_utsu  # noqa: E402
from turkiye_sinir import load  # noqa: E402
from turkiye_alt_kume import classify, apply_mwauth  # noqa: E402
from donemsel_mc_weichert import yfrac  # noqa: E402
from olcek_homojenlestirme import convert, rnd  # noqa: E402

COL = {'tam': '#111111', 'gk74': '#dc2626', 'rb': '#16a34a'}
LAB = {'tam': 'Tam katalog', 'gk74': 'Gardner–Knopoff (GK74)', 'rb': 'Reasenberg'}
MARK = [('1999-08-17', 'İzmit'), ('2011-10-23', 'Van'), ('2020-01-24', 'Elazığ'), ('2023-02-06', 'Kahramanmaraş')]


def analyse(ev, mc):
    gk, rb = classify(ev)
    m = rnd([e['mag'] for e in ev]); y = np.array([e['_y'] for e in ev])
    sel = {'tam': np.ones(len(ev), bool), 'gk74': np.array([gk[e['id']] for e in ev]), 'rb': np.array([rb[e['id']] for e in ev])}
    out = dict(mc=mc, kataloglar={})
    grid = np.round(np.arange(mc, m.max() + 1e-9, 0.1), 1)
    for k, s in sel.items():
        x = m[s & (m >= mc - 1e-9)]; A = aki_utsu(m[s], mc)
        a = math.log10(len(x)) + A['b'] * mc
        t = np.sort(y[s & (m >= mc - 1e-9)])
        out['kataloglar'][k] = dict(n=int(len(x)), b=A['b'], sigma_b=A['sigma_b'], a=a, zaman=t.tolist(),
                                    ccff_m=grid.tolist(), ccff_n=[int((x >= g - 1e-9).sum()) for g in grid])
    F = out['kataloglar']['tam']
    F.update(N6_gr=10 ** (F['a'] - F['b'] * 6.0), N7_gr=10 ** (F['a'] - F['b'] * 7.0))
    for k in ('gk74', 'rb'):
        C = out['kataloglar'][k]
        r_obs = [c / f if f else None for c, f in zip(C['ccff_n'], F['ccff_n'])]
        db = C['b'] - F['b']; da = C['a'] - F['a']
        mx = (da / db) if abs(db) > 1e-9 else None          # r̂(mx) = 1
        C.update(N6_gr=10 ** (C['a'] - C['b'] * 6.0), N7_gr=10 ** (C['a'] - C['b'] * 7.0), r_gozlenen=r_obs, r_yaklasik=[10 ** (da - db * g) for g in grid], m_x=mx,
                 r66=(r_obs[list(grid).index(6.6)] if 6.6 in list(grid) else None))
    return out


def figure(R, title, path):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12, 7.6), dpi=150)
    ax = fig.add_axes([0.07, 0.56, 0.9, 0.38])
    for k in ('tam', 'gk74', 'rb'):
        t = np.array(R['kataloglar'][k]['zaman'])
        ax.step(t, np.arange(1, len(t) + 1), where='post', color=COL[k], lw=1.1, ls=':' if k == 'tam' else '-',
                label=f"{LAB[k]} (N = {len(t):,})".replace(',', ' '))
    for d, lab in MARK:
        ax.axvline(yfrac(parse(d + 'T00:00:00Z')), color='#999', lw=.6, ls='--'); ax.text(yfrac(parse(d + 'T00:00:00Z')), ax.get_ylim()[1] * .97, lab, fontsize=7, rotation=90, va='top', ha='right', color='#555')
    ax.set_ylabel('Kümülatif olay sayısı'); ax.set_xlim(1998, 2026.9); ax.legend(fontsize=8, loc='lower right'); ax.grid(alpha=.3)
    ax.set_title(f'(a) M ≥ {R["mc"]:.1f} ana şokların kümülatif sayısı — {title}', fontsize=9, loc='left')
    axb, axc, axd = (fig.add_axes([0.07 + i * 0.33, 0.07, 0.25, 0.4]) for i in range(3))
    for k in ('tam', 'gk74', 'rb'):
        C = R['kataloglar'][k]; g = np.array(C['ccff_m']); n = np.array(C['ccff_n'], float); ok = n > 0
        axb.plot(g[ok], n[ok], 'D', ms=3.2, mfc='none' if k == 'tam' else COL[k], mec=COL[k], mew=.8, label=LAB[k])
        axc.plot(g, 10 ** (C['a'] - C['b'] * g), color=COL[k], ls=':' if k == 'tam' else '-', lw=1.2)
        axc.text(0.97, 0.95 - 0.08 * ['tam', 'gk74', 'rb'].index(k), f"b = {C['b']:.2f} ± {C['sigma_b']:.2f}", color=COL[k], transform=axc.transAxes, ha='right', fontsize=8)
    for ax_, t in ((axb, '(b) CCFF, gözlenen'), (axc, '(c) Uydurulmuş G–R')):
        ax_.set_yscale('log'); ax_.set_xlabel('Büyüklük'); ax_.grid(alpha=.3, which='both'); ax_.set_title(t, fontsize=9, loc='left')
        ax_.set_ylim(0.6, None)
    axb.set_ylabel('N(≥ m)'); axb.legend(fontsize=7, loc='lower left')
    for i, k in enumerate(('gk74', 'rb')):
        C = R['kataloglar'][k]; g = np.array(C['ccff_m']); ro = np.array([v if v is not None else np.nan for v in C['r_gozlenen']])
        n = np.array(R['kataloglar']['tam']['ccff_n']); ok = n >= 3
        axd.plot(g[ok], ro[ok], 'D', ms=3, color=COL[k]); axd.plot(g, C['r_yaklasik'], color=COL[k], lw=1)
        mx = C['m_x']
        txt = f"m_x = {mx:.1f}" if mx is not None and C['b'] < R['kataloglar']['tam']['b'] else 'm_x yok (b_d > b)'
        axd.text(0.03, 0.95 - 0.08 * i, f"{LAB[k].split(' ')[0]}: {txt}", color=COL[k], transform=axd.transAxes, fontsize=8, va='top')
    axd.axhline(1, color='k', ls=':', lw=.8); axd.set_yscale('log'); axd.set_ylim(0.15, 2.5); axd.set_xlim(R['mc'] - 0.1, 8.2)
    axd.set_xlabel('Büyüklük'); axd.set_ylabel('r(m) = N_ana(≥m) / N(≥m)'); axd.grid(alpha=.3, which='both'); axd.set_title('(d) r(m): gözlenen (◆) ve G–R yaklaşımı', fontsize=9, loc='left')
    fig.savefig(path); plt.close(fig)


def main():
    raw = json.load(open('data/eq_historical.json', encoding='utf-8'))
    P = prep(load(30)[0])
    base = [dict(e, _y=yfrac(parse(e['time']))) for e in raw['events'] if e.get('src') == 'EMSC' and P.contains(Point(e['lon'], e['lat']))]
    evA = [dict(e) for e in base]
    for e in evA:
        v = convert(e, 'combined_dispatch_md_eqml')
        if v is not None:
            e['mag'] = v
    evA = apply_mwauth(evA)
    res = {'H0 ham (Mc 3,2)': analyse(base, 3.2), 'H2+A otoriter Mw (Mc 3,3)': analyse(evA, 3.3)}
    figure(res['H0 ham (Mc 3,2)'], 'Türkiye 30 km, ham EMSC büyüklüğü', os.path.join(HERE, 'fig_mizrahi2_H0.png'))
    figure(res['H2+A otoriter Mw (Mc 3,3)'], 'Türkiye 30 km, Mw (H2 + otoriter Mw)', os.path.join(HERE, 'fig_mizrahi2_H2A.png'))
    slim = {n: dict(mc=R['mc'], kataloglar={k: {kk: vv for kk, vv in C.items() if kk != 'zaman'} for k, C in R['kataloglar'].items()}) for n, R in res.items()}
    json.dump(slim, open(os.path.join(HERE, 'mizrahi_sekil2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    for n, R in res.items():
        print(n)
        for k, C in R['kataloglar'].items():
            extra = f" m_x {C['m_x']:.2f} r(6,6) {C['r66']}" if k != 'tam' and C.get('m_x') is not None else ''
            print(f"  {k:5s} N {C['n']:6d} b {C['b']:.3f}±{C['sigma_b']:.3f} a {C['a']:.2f} N(≥6) {C['ccff_n'][int(round((6.0 - R['mc']) * 10))]} N(≥7) {C['ccff_n'][int(round((7.0 - R['mc']) * 10))]} | G–R N(≥6) {C['N6_gr']:.1f} N(≥7) {C['N7_gr']:.2f}{extra}")


if __name__ == '__main__':
    main()
