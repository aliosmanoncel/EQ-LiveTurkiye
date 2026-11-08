"""
olcek_homojenlestirme.py — 5. tur (dördüncü aşama): md/ml → Mw ölçek homojenleştirmesi ve Δb.

Soru: 3.–4. turdaki Δb ≈ +0,13 ve zıt ayıklama eğimleri (k_GK > 0, k_RB < 0), büyüklükler sitenin kendi
dönüşüm bağıntılarıyla Mw'ye çevrilince korunuyor mu? M ≥ 5'te kalan oranlar ve gürültü nasıl şekilleniyor?

Dönüşümler: index.html MAG_CONVERSIONS kayıtlarının Python kopyası (yeni bağıntı EKLENMEDİ):
  H0 ham EMSC büyüklüğü (karşılaştırma tabanı)
  H1 combined_dispatch            — mb/Ms: Scordilis (2006); ML: Çıvgın & Scordilis (2019); Md ham
  H2 combined_dispatch_md_eqml    — H1 + Md < 4,0 için MD = ML varsayımı → Çıvgın & Scordilis (2019)
  H3 combined_dispatch_md         — H1 + Md < 4,0 için KOERI zinciri: Cambaz vd. (2019) Md→ML + Çıvgın & Scordilis
  H3* (TANI, site bağıntısı DEĞİL) — H3 zinciri Md ≥ 4,0'a da uygulanır; H3'ün Md < 4 sınırının yarattığı
                                    Mw ≈ 3,3–4,0 boşluğunu yöntem etkisinden ayırmak için. Yayın/öneri değildir.
  H2+A                            — H2 + data/mw_authority.json otoriter Mw (doğrulanmış büyük depremler)
Uygulanamayan olay (tür/aralık/bölge dışı) ham büyüklüğüyle kalır — sitedeki kural. Mw tipli olaylar dönüştürülmez.
Python kopyası, site_donusum_parite.mjs çıktısıyla (index.html bloğu Node'da değiştirilmeden çalıştırılır) olay
olay karşılaştırılır; eşleşmezse betik durur.

Her varyantta: iki yöntem dönüştürülmüş (yuvarlanmamış) büyüklüklerle Türkiye 30 km alt kümesinde YENİDEN çalıştırılır
(GK74 pencereleri ve Reasenberg etkileşimi M'ye bağlıdır); xmeff = 3,0 (sitedeki değer) sabit tutulur.
İstatistik: 0,1'e yuvarlanmış (yarım yukarı) büyüklükler; dönem başına Mc = max(GFT R≥95 [yoksa 90], MAXC+0,2,
tür tabanı) — tür tabanı: payı ≥ %1 olan büyüklük türlerinin dönüşüm sonrası en küçük değerlerinin en büyüğü,
ham (ayrıştırılmamış) dönem kataloğundan; aynı Mc iki yönteme uygulanır. Dönemler md 1998–2013, ml 2013–2026.
Çıktı: olcek_sonuc.json, fig_olcek.png. Bulgular istatistikseldir; fiziksel sismisite değişimi kanıtı değildir.
Kullanım: node .../site_donusum_parite.mjs <site_mw.json> && python .../olcek_homojenlestirme.py <site_mw.json>
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
from turkiye_alt_kume import classify, apply_mwauth, mc_site  # noqa: E402
from donemsel_mc_weichert import yfrac  # noqa: E402

DM = 0.1
PERIODS = {'md 1998–2013': lambda y: y < 2013, 'ml 2013–2026': lambda y: y >= 2013,
           'ml 2013–2023 (2023+ hariç)': lambda y: 2013 <= y < 2023}
HIGH = [(5.0, 5.5), (5.5, 6.0), (6.0, 9.9), (5.0, 9.9)]


# ── index.html MAG_CONVERSIONS kopyası (aynı işlem sırası) ──
def in_tr(e):
    return 34 <= e['lat'] <= 43 and 24 <= e['lon'] <= 47


def scordilis(e):
    t, m = e['mtype'].lower(), e['mag']
    if t == 'mb' and 3.5 <= m <= 6.2:
        return 0.85 * m + 1.03
    if t == 'ms' and e.get('dep') is not None and e['dep'] < 70 and ((3.0 <= m <= 6.1) or (6.2 <= m <= 8.2)):
        return 0.67 * m + 2.07 if m <= 6.1 else 0.99 * m + 0.08
    return None


def civgin(t, m, e):
    return 0.93 * m + 0.29 if t == 'ml' and 1.7 <= m <= 6.7 and in_tr(e) else None


def convert(e, key):
    t, m = e['mtype'].lower(), e['mag']
    if t == 'md':
        if key == 'koeri_zincir_sinirsiz':          # TANI: site bağıntısı değil — Md ≥ 4,0 da zincirle çevrilir
            return civgin('ml', 1.0313 * m - 0.7677, e)
        if key == 'combined_dispatch' or not m < 4.0:
            return None
        return civgin('ml', m, e) if key == 'combined_dispatch_md_eqml' else civgin('ml', 1.0313 * m - 0.7677, e)
    if t == 'ml':
        return civgin('ml', m, e)
    return scordilis(e)


VARIANTS = [('H0 ham', None, False), ('H1 Birleşik (Md ham)', 'combined_dispatch', False),
            ('H2 Birleşik + Md=ML', 'combined_dispatch_md_eqml', False), ('H3 Birleşik + KOERI Md zinciri', 'combined_dispatch_md', False),
            ('H3* KOERI zinciri, Md ≥ 4 dahil (tanı)', 'koeri_zincir_sinirsiz', False),
            ('H2+A otoriter Mw', 'combined_dispatch_md_eqml', True)]


def rnd(x):
    return np.floor(np.asarray(x) * 10 + 0.5) / 10


def gft_local(m):
    m = np.asarray(m); R = {}
    for mc in np.round(np.arange(m.min(), min(m.max() - 0.5, 5.0) + 1e-9, DM), 1):
        x = m[m >= mc - 1e-9]
        if len(x) < 50:
            break
        b = math.log10(math.e) / (x.mean() - (mc - DM / 2)); a = math.log10(len(x)) + b * mc
        bins = np.round(np.arange(mc, x.max() + 1e-9, DM), 1)
        B = np.array([(x >= v - 1e-9).sum() for v in bins], float)
        R[float(mc)] = 100 - 100 * np.abs(B - 10 ** (a - b * bins)).sum() / B.sum()
    for req in (95, 90):
        ok = [mc for mc, r in sorted(R.items()) if r >= req]
        if ok:
            return ok[0], req
    return None, None


def slope_k(m, keep, mc):
    x, y, w = [], [], []
    for c in np.round(np.arange(mc, m.max() + 1e-9, DM), 1):
        s = np.abs(m - c) < 1e-6; nr = s.sum(); nk = (s & keep).sum()
        if nr < 5 or nk < 1:
            continue
        f = nk / nr
        var = (1 - f) / (nk * math.log(10) ** 2) if f < 1 else 1.0 / (nr * math.log(10) ** 2)
        x.append(c); y.append(math.log10(f)); w.append(1 / var)
    x, y, w = map(np.array, (x, y, w)); W = w.sum(); xm = (w * x).sum() / W; ym = (w * y).sum() / W
    sxx = (w * (x - xm) ** 2).sum()
    return dict(k=float((w * (x - xm) * (y - ym)).sum() / sxx), sigma_k=float(math.sqrt(1 / sxx)), n_sinif=len(x))


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [c - h, c + h]


def type_floor(m, t, m0):
    """Ham dosya her türde M ≥ 3,0 ile kesik; dönüşüm sonrası türlerin alt sınırları farklılaşır. Dosya kesmesiyle
    kesilmiş (ham en küçük = 3,0) ve payı ≥ %1 olan türlerin dönüşüm sonrası en küçük (yuvarlanmış) değerlerinin en
    büyüğü: bunun altında katalog tür karışımı bakımından eksiktir. Ham en küçüğü 3,0'ın üstünde olan türler (ör. Mw,
    mb yalnız büyük olaylara atanır) dosya kesmesiyle değil ajansın tür seçimiyle sınırlıdır; tabana katılmaz."""
    out = {}
    for u in set(t):
        s = t == u
        if s.mean() >= 0.01 and m0[s].min() <= 3.0 + 1e-9:
            out[u] = float(m[s].min())
    return max(out.values()), out


def period_stats(m, g, r, t, m0):
    mx, gf = mc_site(m), gft_local(m)
    fl, fl_by = type_floor(m, t, m0)
    mc = max(v for v in (mx, gf[0], fl) if v is not None)
    A = {k: aki_utsu(m[s], mc) for k, s in (('ham', np.ones_like(g)), ('gk74', g), ('rb', r))}
    db = A['rb']['b'] - A['gk74']['b']; sd = math.hypot(A['rb']['sigma_b'], A['gk74']['sigma_b'])
    kg, kr = slope_k(m, g, mc), slope_k(m, r, mc)
    return dict(n=int(len(m)), mc=mc, mc_tur_tabani=fl, tur_tabanlari=fl_by, mc_maxc02=mx, mc_gft=gf[0], gft_R=gf[1], b_ham=A['ham']['b'], b_gk=A['gk74']['b'],
                b_rb=A['rb']['b'], n_gk=A['gk74']['n'], n_rb=A['rb']['n'], db=db, sigma_db=sd, z=db / sd,
                k_gk=kg, k_rb=kr, db_egimden=kg['k'] - kr['k'])


def main(site_json):
    raw = json.load(open('data/eq_historical.json', encoding='utf-8'))
    ev_all = [e for e in raw['events'] if e.get('src') == 'EMSC']
    S = json.load(open(site_json, encoding='utf-8'))
    assert S['ids'] == [e['id'] for e in ev_all]
    for key in ('combined_dispatch', 'combined_dispatch_md_eqml', 'combined_dispatch_md'):
        py = [convert(e, key) for e in ev_all]
        bad = sum(1 for a, b in zip(py, S[key]) if (a is None) != (b is None) or (a is not None and a != b))
        assert bad == 0, f'{key}: site ↔ Python {bad} olayda farklı'
        print(f'parite {key}: {len(py)} olay birebir aynı; dönüştürülen {sum(v is not None for v in py)}')

    P = prep(load(30)[0])
    base = [dict(e, _y=yfrac(parse(e['time']))) for e in ev_all if P.contains(Point(e['lon'], e['lat']))]
    res = dict(n=len(base), xmeff=3.0, varyantlar={})
    g0 = r0 = None
    for name, key, auth in VARIANTS:
        ev = [dict(e) for e in base]
        nconv = 0
        if key:
            for e in ev:
                v = convert(e, key)
                if v is not None:
                    e['mag'] = v; nconv += 1
        if auth:
            ev = apply_mwauth(ev)
        gk, rb = classify(ev)
        ids = [e['id'] for e in ev]
        if g0 is None:
            g0, r0 = gk, rb
        y = np.array([e['_y'] for e in ev]); m = rnd([e['mag'] for e in ev])
        g = np.array([gk[i] for i in ids]); r = np.array([rb[i] for i in ids]); tt = np.array([e['mtype'].lower() for e in ev]); m0 = rnd([e0['mag'] for e0 in base])
        V = dict(donusturulen=nconv, sinif_degisen_h0a_gore=dict(gk74=sum(gk[i] != g0[i] for i in ids), rb=sum(rb[i] != r0[i] for i in ids)),
                 donemler={}, yuksek={})
        for pn, f in PERIODS.items():
            s = np.array([f(v) for v in y])
            V['donemler'][pn] = period_stats(m[s], g[s], r[s], tt[s], m0[s])
        a, b = V['donemler']['md 1998–2013'], V['donemler']['ml 2013–2026']
        w1, w2 = 1 / a['sigma_db'] ** 2, 1 / b['sigma_db'] ** 2
        dbc = (w1 * a['db'] + w2 * b['db']) / (w1 + w2); sc = 1 / math.sqrt(w1 + w2)
        V['birlesik'] = dict(db=dbc, sigma=sc, z=dbc / sc, Q=(a['db'] - dbc) ** 2 * w1 + (b['db'] - dbc) ** 2 * w2)
        smd = y < 2013
        V['md_bosluk_3_4_3_9'] = dict(md_kaynakli=int(((m >= 3.35) & (m < 3.95) & smd & np.array([e['mtype'].lower() == 'md' for e in ev])).sum()),
                                      tum_md_donemi=int(((m >= 3.35) & (m < 3.95) & smd).sum()))
        for lo, hi in HIGH:
            s = (m >= lo - 1e-9) & (m < hi - 1e-9); n = int(s.sum()); kg = int((s & g).sum()); kr = int((s & r).sum())
            V['yuksek'][f'{lo:.1f}–{hi:.1f}' if hi < 9 else f'≥{lo:.1f}'] = dict(n=n, kalan_gk=kg, kalan_rb=kr,
                f_gk=kg / n if n else None, f_gk95=wilson(kg, n), f_rb=kr / n if n else None, f_rb95=wilson(kr, n))
        V['egri'] = {pn: dict(m=[], n=[], gk=[], rb=[]) for pn in ('md 1998–2013', 'ml 2013–2026')}
        for pn in V['egri']:
            s = np.array([PERIODS[pn](v) for v in y])
            for c in np.round(np.arange(m[s].min(), m[s].max() + 1e-9, DM), 1):
                q = s & (np.abs(m - c) < 1e-6)
                if q.sum():
                    E = V['egri'][pn]; E['m'].append(float(c)); E['n'].append(int(q.sum())); E['gk'].append(int((q & g).sum())); E['rb'].append(int((q & r).sum()))
        res['varyantlar'][name] = V
        print(f'\n== {name}: dönüştürülen {nconv}; sınıf değişen (H0\'a göre) GK74 {V["sinif_degisen_h0a_gore"]["gk74"]} RB {V["sinif_degisen_h0a_gore"]["rb"]}; '
              f'md dönemi 3,4–3,9 olay {V["md_bosluk_3_4_3_9"]["tum_md_donemi"]} (md kaynaklı {V["md_bosluk_3_4_3_9"]["md_kaynakli"]})')
        for pn, x in V['donemler'].items():
            print(f'  {pn:26s} Mc {x["mc"]:.1f} (tür tabanı {x["mc_tur_tabani"]:.1f}, MAXC+0,2 {x["mc_maxc02"]}, GFT{x["gft_R"]} {x["mc_gft"]}) b ham {x["b_ham"]:.3f} GK {x["b_gk"]:.3f} RB {x["b_rb"]:.3f} '
                  f'Δb {x["db"]:+.3f}±{x["sigma_db"]:.3f} (z {x["z"]:.1f}) | k_GK {x["k_gk"]["k"]:+.3f}±{x["k_gk"]["sigma_k"]:.3f} k_RB {x["k_rb"]["k"]:+.3f}±{x["k_rb"]["sigma_k"]:.3f} → {x["db_egimden"]:+.3f}')
        c = V['birlesik']
        print(f'  birleşik (md+ml) Δb {c["db"]:+.3f}±{c["sigma"]:.3f} z {c["z"]:.1f} Q {c["Q"]:.2f}')
        for k, h in V['yuksek'].items():
            print(f'  M {k:8s} N {h["n"]:4d}  f_GK {h["f_gk"]:.2f} [{h["f_gk95"][0]:.2f}–{h["f_gk95"][1]:.2f}]  f_RB {h["f_rb"]:.2f} [{h["f_rb95"][0]:.2f}–{h["f_rb95"][1]:.2f}]')
    json.dump(res, open(os.path.join(HERE, 'olcek_sonuc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    figure(res)


def figure(res):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    names = list(res['varyantlar']); x = np.arange(len(names))
    fig, axs = plt.subplots(1, 3, figsize=(13, 4), dpi=150)
    ax = axs[0]
    for j, (pn, col) in enumerate((('md 1998–2013', '#2563eb'), ('ml 2013–2026', '#16a34a'))):
        d = [res['varyantlar'][n]['donemler'][pn] for n in names]
        ax.errorbar(x + (j - .5) * .25, [v['db'] for v in d], yerr=[1.96 * v['sigma_db'] for v in d], fmt='o', color=col, ms=4, capsize=2, label=f'{pn} Δb (95%)')
        ax.plot(x + (j - .5) * .25, [v['db_egimden'] for v in d], 'x', color=col, ms=6, label=f'{pn} Δb (eğimden)')
    ax.axhline(0, color='#999', lw=.7); ax.set_xticks(x); ax.set_xticklabels([n.split(' ')[0] for n in names]); ax.set_ylabel('Δb = b_RB − b_GK74')
    ax.legend(fontsize=6); ax.grid(alpha=.3); ax.set_title('Δb: dönem ve dönüşüm varyantı', fontsize=9)
    for ax, pn in zip(axs[1:], ('md 1998–2013', 'ml 2013–2026')):
        for n, col in (('H0 ham', '#999999'), ('H2 Birleşik + Md=ML', '#7c3aed'), ('H3 Birleşik + KOERI Md zinciri', '#ea580c')):
            E = res['varyantlar'][n]['egri'][pn]; mm = np.array(E['m']); nn = np.array(E['n']); ok = nn >= 5
            ax.plot(mm[ok], np.array(E['gk'])[ok] / nn[ok], 'o-', ms=2, lw=.7, color=col, label=f'{n.split(" ")[0]} GK74')
            ax.plot(mm[ok], np.array(E['rb'])[ok] / nn[ok], 's--', ms=2, lw=.7, color=col, label=f'{n.split(" ")[0]} RB')
        ax.set_yscale('log'); ax.grid(alpha=.3, which='both'); ax.set_xlabel('M (varyant ölçeği, 0,1 kutu)'); ax.set_title(f'Kalan oran f(M) — {pn}', fontsize=9)
    axs[1].set_ylabel('f(M)'); axs[1].legend(fontsize=6, ncol=2)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'fig_olcek.png')); plt.close(fig)


if __name__ == '__main__':
    main(sys.argv[1])
