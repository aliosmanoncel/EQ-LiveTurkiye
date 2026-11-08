"""
rb_parametre_duyarlilik.py — 8. tur: Reasenberg'in Türkiye'de b'yi YÜKSELTMESİ parametre seçiminden mi kaynaklanıyor?

Mizrahi vd. (2021) Tablo S1 / Metin S3 (arXiv:2012.09053) Reasenberg ayarları:
  standart: τ_min 1,0 · τ_max 10,0 · x_k 0,5 · p 0,95 · r_fact 10 · xm_eff = Mc
  aralıklar: τ_min {0,5 … 2,5} · τ_max {3, 6, 8, 10, 11, 13, 15} · x_k {0 … 1, 7 değer} · p {0,75 … 0,95} · r_fact {5, 10, 15, 20}
  etkileşim bağıntısı: Reasenberg (1985) r = 0,011·10^(0,4M) km  VEYA  Wells & Coppersmith (1994) tabanlı f = 0,01·10^(0,5M)
EQ-Live sabit kodu (reasenberg.py v0.3.0, sha c5b1248a…) standart değerlerle aynıdır; tek farklar xm_eff (3,0 ↔ Mc) ve bağıntı.
W&C bağıntısı sabit kodda YOKTUR: bu betik reasenberg.interaction_radius_km'yi yalnız çalışma süresince geçici olarak
değiştirir (dosya değişmez; sha her koşuda denetlenir). Bu bir araştırma deneyidir, sitenin yöntemi değildir.

Deney: Türkiye 30 km, H0 (Mc 3,2) — tek seferde bir parametre (OAT) ve 120 rastgele kombinasyon (her bağıntı için 60,
tohum 20261108); H2+A (Mc 3,3) için standart ve W&C standart. Her koşuda: N, b (Aki–Utsu), k_RB (kalan oran eğimi),
b_RB − b_tam, r(6,6), m_x. GK74 ve tam katalog karşılaştırma için.
Çıktı: rb_parametre_sonuc.json, fig_rb_parametre.png.
"""
import contextlib, hashlib, itertools, json, math, os, sys, time

import numpy as np
from shapely.geometry import Point
from shapely.prepared import prep

sys.path.insert(0, 'scripts')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reasenberg as R  # noqa: E402
import decluster_reasenberg as D  # noqa: E402
import decluster_gk74 as GK  # noqa: E402
from bok_analiz import parse, aki_utsu  # noqa: E402
from turkiye_sinir import load  # noqa: E402
from turkiye_alt_kume import apply_mwauth  # noqa: E402
from donemsel_mc_weichert import yfrac  # noqa: E402
from olcek_homojenlestirme import convert, rnd, slope_k  # noqa: E402

FROZEN = 'c5b1248af557f29b4f04bf7c6ed9adfefd97c4153975a8989804b872ccf99bc9'
STD = dict(tau_min=1.0, tau_max=10.0, xk=0.5, p=0.95, rfact=10.0)
RANGES = dict(tau_min=[0.5, 1.0, 1.5, 2.0, 2.5], tau_max=[3.0, 6.0, 8.0, 10.0, 11.0, 13.0, 15.0],
              xk=[0.0, 0.167, 0.333, 0.5, 0.667, 0.833, 1.0], p=[0.75, 0.8, 0.85, 0.9, 0.95], rfact=[5.0, 10.0, 15.0, 20.0])
_R85 = R.interaction_radius_km


def _wc(magnitude):
    return 0.01 * 10.0 ** (0.5 * np.asarray(magnitude, dtype=float))


@contextlib.contextmanager
def relation(name):
    R.interaction_radius_km = _wc if name == 'W&C1994' else _R85
    try:
        yield
    finally:
        R.interaction_radius_km = _R85


def stats(m, keep, mc, full):
    A = aki_utsu(m[keep], mc); x = m[keep & (m >= mc - 1e-9)]
    a = math.log10(len(x)) + A['b'] * mc
    k = slope_k(m, keep, mc)
    out = dict(n=int(len(x)), b=A['b'], sigma_b=A['sigma_b'], a=a, k=k['k'], sigma_k=k['sigma_k'])
    if full is not None:
        n66 = int((m >= 6.6 - 1e-9).sum())
        out['db_tam'] = A['b'] - full['b']
        out['r66'] = int((keep & (m >= 6.6 - 1e-9)).sum()) / n66 if n66 else None
        out['m_x'] = (a - full['a']) / (A['b'] - full['b']) if A['b'] < full['b'] else None
    return out


def run_rb(ev, m, mc, rel, xmeff, prm):
    with relation(rel):
        revs, o = D.decluster(ev, xmeff, 'zmap', 'mag', **prm)
    ind = {e['id']: c != 'dependent' for e, c in zip(revs, o['event_class'])}
    return np.array([ind[e['id']] for e in ev])


def experiment(ev, mc, label, full_grid=True):
    m = rnd([e['mag'] for e in ev])
    full = stats(m, np.ones(len(ev), bool), mc, None)
    gevs, gcl = GK.decluster(ev, 'mag'); gi = {e['id']: not c for e, c in zip(gevs, gcl)}
    gk = stats(m, np.array([gi[e['id']] for e in ev]), mc, full)
    rows = []

    def add(rel, xmeff, prm, tag):
        t0 = time.time(); keep = run_rb(ev, m, mc, rel, xmeff, prm)
        s = stats(m, keep, mc, full); s.update(baginti=rel, xmeff=xmeff, etiket=tag, sure_s=round(time.time() - t0, 1), **prm)
        rows.append(s)
        print(f"  {label:6s} {rel:10s} xmeff {xmeff:.1f} {tag:22s} N {s['n']:6d} b {s['b']:.3f} (b−b_tam {s['db_tam']:+.3f}) k {s['k']:+.3f} r6.6 {s['r66']} m_x {s['m_x']}")

    for rel in ('Reasenberg1985', 'W&C1994'):
        add(rel, 3.0, STD, 'standart, xmeff 3,0 (EQ-Live)')
        add(rel, mc, STD, 'standart, xmeff = Mc')
        if not full_grid:
            continue
        for par, vals in RANGES.items():
            for v in vals:
                if v != STD[par]:
                    add(rel, mc, dict(STD, **{par: v}), f'OAT {par}={v:g}')
        rng = np.random.default_rng(20261108)
        for _ in range(60):
            prm = {par: float(rng.choice(vals)) for par, vals in RANGES.items()}
            add(rel, mc, prm, 'rastgele')
    return dict(mc=mc, tam=full, gk74=gk, rb=rows)


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
    res = {'H0 ham (Mc 3,2)': experiment(base, 3.2, 'H0'), 'H2+A otoriter Mw (Mc 3,3)': experiment(evA, 3.3, 'H2+A', full_grid=False)}
    assert hashlib.sha256(open('scripts/reasenberg.py', 'rb').read()).hexdigest() == FROZEN
    assert R.interaction_radius_km is _R85
    for n, X in res.items():
        print(f"\n{n}: tam b {X['tam']['b']:.3f}  GK74 b {X['gk74']['b']:.3f} (k {X['gk74']['k']:+.3f})")
        for rel in ('Reasenberg1985', 'W&C1994'):
            r = [x for x in X['rb'] if x['baginti'] == rel and x['etiket'] != 'standart, xmeff 3,0 (EQ-Live)']
            db = np.array([x['db_tam'] for x in r]); kk = np.array([x['k'] for x in r])
            print(f"  {rel:14s} koşu {len(r):3d}: b−b_tam min {db.min():+.3f} medyan {np.median(db):+.3f} maks {db.max():+.3f}; "
                  f"b < b_tam olan {int((db < 0).sum())}; k medyan {np.median(kk):+.3f} [{kk.min():+.3f}, {kk.max():+.3f}]")
        X['ozet'] = {rel: dict(kosu=len(r := [x for x in X['rb'] if x['baginti'] == rel and x['etiket'] != 'standart, xmeff 3,0 (EQ-Live)']),
                               db_min=min(x['db_tam'] for x in r), db_medyan=float(np.median([x['db_tam'] for x in r])), db_maks=max(x['db_tam'] for x in r),
                               b_dusen=sum(x['db_tam'] < 0 for x in r)) for rel in ('Reasenberg1985', 'W&C1994')}
    json.dump(dict(kaynak='Mizrahi vd. 2021, Tablo S1 / Metin S3 (arXiv:2012.09053)', sabit_kod_sha=FROZEN, standart=STD, araliklar=RANGES, sonuc=res),
              open(os.path.join(HERE, 'rb_parametre_sonuc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    figure(res['H0 ham (Mc 3,2)'])


def figure(X):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.3), dpi=150)
    col = {'Reasenberg1985': '#16a34a', 'W&C1994': '#0891b2'}
    ax = axs[0]
    for rel in col:
        r = [x for x in X['rb'] if x['baginti'] == rel]
        ax.scatter([x['a'] for x in r], [x['b'] for x in r], s=10, color=col[rel], alpha=.6, label=f'Reasenberg, bağıntı {rel}')
        s = [x for x in r if x['etiket'] == 'standart, xmeff = Mc'][0]
        ax.scatter(s['a'], s['b'], s=90, marker='*', color=col[rel], edgecolor='k', lw=.6, zorder=5)
    ax.scatter(X['tam']['a'], X['tam']['b'], s=70, marker='D', facecolor='none', edgecolor='k', label='Tam katalog')
    ax.scatter(X['gk74']['a'], X['gk74']['b'], s=70, marker='s', color='#dc2626', label='GK74')
    ax.axhline(X['tam']['b'], color='k', ls=':', lw=.8)
    ax.set_xlabel('a'); ax.set_ylabel('b (Aki–Utsu, Mc 3,2)'); ax.grid(alpha=.3); ax.legend(fontsize=7)
    ax.set_title('(a) Mizrahi vd. Şekil 3a karşılığı: a–b (★ standart)', fontsize=9, loc='left')
    ax = axs[1]
    for rel in col:
        r = [x for x in X['rb'] if x['baginti'] == rel]
        ax.scatter([x['n'] for x in r], [x['k'] for x in r], s=10, color=col[rel], alpha=.6, label=rel)
    ax.scatter(X['gk74']['n'], X['gk74']['k'], s=70, marker='s', color='#dc2626', label='GK74')
    ax.axhline(0, color='k', ls=':', lw=.8); ax.set_xscale('log')
    ax.set_xlabel('Kalan olay sayısı N (M ≥ Mc)'); ax.set_ylabel('k (kalan oran eğimi; b_d ≈ b_tam − k)'); ax.grid(alpha=.3, which='both'); ax.legend(fontsize=7)
    ax.set_title('(b) Ayıklama eğimi k ve agresiflik', fontsize=9, loc='left')
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'fig_rb_parametre.png')); plt.close(fig)


if __name__ == '__main__':
    main()
