"""
buyukluk_sinifi_ayiklama.py — 4. tur (üçüncü aşama): Δb'nin kaynağı — büyüklük sınıflarına göre ayıklama.

Soru: GK74'ün Reasenberg'e göre daha düşük b vermesi, belirli büyüklük sınıflarındaki olayların seçici biçimde
çıkarılmasından mı kaynaklanıyor?
Mantık: ayrıştırılmış katalogda N_d(m) = N_ham(m)·f(m), f = kalan oran. f(m) ∝ 10^(k·m) ise b_d = b_ham − k.
  Büyüklükten bağımsız ayıklama (k = 0) b'yi değiştirmez; küçük olayları daha çok ayıklamak (k > 0) b'yi düşürür.
  Δb = b_RB − b_GK ≈ k_GK − k_RB.
Ölçüler (Türkiye 30 km, "yeniden" sınıflar, EMSC büyüklüğü):
  - 0,1 ve geniş sınıflarda: N ham, GK74/RB ayıkladığı, ikisi de, yalnız biri; kalan oranlar.
  - k: log10 f(m)'nin m'ye ağırlıklı (binom varyansı) doğrusal eğimi, M ≥ Mc.
  - Sınıf katkısı: GK74 sayımlarında YALNIZ j sınıfını RB sayımıyla değiştirince b'nin değişimi (gruplanmış Aki).
  - md (1998–2013) ve ml (2013–2026) dönemleri; 2023+ hariç duyarlılığı.
Bulgular istatistikseldir (katalog seçimi), fiziksel sismisite değişimi kanıtı değildir.
Çıktı: buyukluk_sonuc.json, fig_ayiklama.png.
"""
import json, math, os, sys

import numpy as np
from shapely.geometry import Point
from shapely.prepared import prep

sys.path.insert(0, 'scripts')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bok_analiz import parse  # noqa: E402
from turkiye_sinir import load  # noqa: E402
from turkiye_alt_kume import classify  # noqa: E402
from donemsel_mc_weichert import yfrac  # noqa: E402

DM = 0.1
WIDE = [(3.0, 3.2), (3.2, 3.5), (3.5, 4.0), (4.0, 4.5), (4.5, 5.0), (5.0, 6.0), (6.0, 9.9)]
MCS = [3.2, 3.5]
SUBSETS = {'tümü 1998–2026': lambda y: True, 'md dönemi 1998–2013': lambda y: y < 2013,
           'ml dönemi 2013–2026': lambda y: y >= 2013, 'ml dönemi, 2023+ hariç': lambda y: 2013 <= y < 2023,
           'tümü, 2023+ hariç': lambda y: y < 2023}


def b_binned(counts, cen, mc):
    """Gruplanmış Aki–Utsu: sınıf merkezleri (alt kenar) ve sayılar, M ≥ Mc."""
    sel = cen >= mc - 1e-9
    n = counts[sel].sum()
    if n < 10:
        return None
    mean = (counts[sel] * cen[sel]).sum() / n
    return math.log10(math.e) / (mean - (mc - DM / 2))


def slope_k(cen, n_raw, n_keep, mc):
    """log10 f(m) = c + k·m, ağırlık 1/var(log10 f) (binom, delta yöntemi); M ≥ Mc ve n_raw ≥ 5."""
    x, y, w = [], [], []
    for m, nr, nk in zip(cen, n_raw, n_keep):
        if m < mc - 1e-9 or nr < 5 or nk < 1:
            continue
        f = nk / nr
        var = (1 - f) / (nk * math.log(10) ** 2) if f < 1 else 1.0 / (nr * math.log(10) ** 2)
        x.append(m); y.append(math.log10(f)); w.append(1 / var)
    x, y, w = map(np.array, (x, y, w))
    W = w.sum(); xm = (w * x).sum() / W; ym = (w * y).sum() / W
    sxx = (w * (x - xm) ** 2).sum()
    k = (w * (x - xm) * (y - ym)).sum() / sxx
    return dict(k=k, sigma_k=math.sqrt(1 / sxx), n_sinif=len(x))


def analyse(ev, gk, rb):
    m = np.array([e['mag'] for e in ev])
    cen = np.round(np.arange(3.0, m.max() + 1e-9, DM), 1)
    idx = np.clip(np.floor((m - 3.0) / DM + 1e-6).astype(int), 0, len(cen) - 1)
    g = np.array([gk[e['id']] for e in ev]); r = np.array([rb[e['id']] for e in ev])
    n_raw = np.bincount(idx, minlength=len(cen)).astype(float)
    n_gk = np.bincount(idx[g], minlength=len(cen)).astype(float)
    n_rb = np.bincount(idx[r], minlength=len(cen)).astype(float)
    wide = []
    for lo, hi in WIDE:
        s = (m >= lo - 1e-9) & (m < hi - 1e-9)
        if not s.any():
            continue
        N = int(s.sum())
        wide.append(dict(sinif=f'{lo:.1f}–{hi:.1f}' if hi < 9 else f'≥{lo:.1f}', n_ham=N,
                         gk_ayikladi=int((s & ~g).sum()), rb_ayikladi=int((s & ~r).sum()),
                         ikisi_de=int((s & ~g & ~r).sum()), yalniz_gk=int((s & ~g & r).sum()), yalniz_rb=int((s & g & ~r).sum()),
                         kalan_gk=float((s & g).sum() / N), kalan_rb=float((s & r).sum() / N)))
    out = dict(n=len(ev), siniflar=wide, mc={})
    for mc in MCS:
        bh, bg, br = b_binned(n_raw, cen, mc), b_binned(n_gk, cen, mc), b_binned(n_rb, cen, mc)
        kg, kr = slope_k(cen, n_raw, n_gk, mc), slope_k(cen, n_raw, n_rb, mc)
        contrib = []
        for lo, hi in WIDE:
            if hi <= mc + 1e-9:
                continue
            sel = (cen >= max(lo, mc) - 1e-9) & (cen < hi - 1e-9)
            hyb = n_gk.copy(); hyb[sel] = n_rb[sel]
            bhyb = b_binned(hyb, cen, mc)
            contrib.append(dict(sinif=f'{max(lo, mc):.1f}–{hi:.1f}' if hi < 9 else f'≥{lo:.1f}', katki=(bhyb - bg) if bhyb else None))
        out['mc'][f'{mc:.1f}'] = dict(b_ham=bh, b_gk=bg, b_rb=br, db=br - bg, k_gk=kg, k_rb=kr,
                                      db_egimden=kg['k'] - kr['k'], b_ham_eksi_k_gk=bh - kg['k'], b_ham_eksi_k_rb=bh - kr['k'],
                                      sinif_katkisi=contrib, katki_toplami=sum(c['katki'] for c in contrib if c['katki'] is not None))
    out['egri'] = dict(m=cen.tolist(), n_ham=n_raw.tolist(), n_gk=n_gk.tolist(), n_rb=n_rb.tolist())
    return out


def main():
    raw = json.load(open('data/eq_historical.json', encoding='utf-8'))
    ev = [e for e in raw['events'] if e.get('src') == 'EMSC']
    poly, _ = load(30); P = prep(poly)
    ev = [dict(e, _y=yfrac(parse(e['time']))) for e in ev if P.contains(Point(e['lon'], e['lat']))]
    gk, rb = classify(ev)                          # Türkiye alt kümesinde "yeniden"
    res = {}
    for name, f in SUBSETS.items():
        sub = [e for e in ev if f(e['_y'])]
        res[name] = analyse(sub, gk, rb)
    json.dump(res, open(os.path.join(HERE, 'buyukluk_sonuc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)

    A = res['tümü 1998–2026']
    print('=== Türkiye 30 km, tümü: geniş sınıflarda ayıklama ===')
    print(f"{'sınıf':9s} {'N ham':>6s} {'GK ayıkl.':>9s} {'RB ayıkl.':>9s} {'ikisi':>6s} {'yalnız GK':>9s} {'yalnız RB':>9s} {'kalan GK':>8s} {'kalan RB':>8s}")
    for w in A['siniflar']:
        print(f"{w['sinif']:9s} {w['n_ham']:6d} {w['gk_ayikladi']:9d} {w['rb_ayikladi']:9d} {w['ikisi_de']:6d} {w['yalniz_gk']:9d} {w['yalniz_rb']:9d} {w['kalan_gk']:8.3f} {w['kalan_rb']:8.3f}")
    for name, R in res.items():
        for mc in ('3.2', '3.5'):
            x = R['mc'][mc]
            print(f"{name:24s} Mc {mc}: b ham {x['b_ham']:.3f} GK {x['b_gk']:.3f} RB {x['b_rb']:.3f} Δb {x['db']:+.3f} | k_GK {x['k_gk']['k']:+.3f}±{x['k_gk']['sigma_k']:.3f} "
                  f"k_RB {x['k_rb']['k']:+.3f}±{x['k_rb']['sigma_k']:.3f} → Δb(eğim) {x['db_egimden']:+.3f} | katkı: "
                  + ', '.join(f"{c['sinif']} {c['katki']:+.3f}" for c in x['sinif_katkisi'] if c['katki'] is not None) + f" (toplam {x['katki_toplami']:+.3f})")

    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.8), dpi=150, sharey=True)
    for ax, name in zip(axs, ('md dönemi 1998–2013', 'ml dönemi 2013–2026')):
        E = res[name]['egri']; mm = np.array(E['m']); nr = np.array(E['n_ham'])
        ok = nr >= 5
        for key, col, lab in (('n_gk', '#7c3aed', 'GK74 kalan oranı'), ('n_rb', '#ea580c', 'Reasenberg kalan oranı')):
            f = np.array(E[key])[ok] / nr[ok]
            ax.plot(mm[ok], f, 'o-', ms=2.5, lw=.8, color=col, label=lab)
        ax.set_yscale('log'); ax.axvline(3.2, color='#999', ls='--', lw=.7); ax.grid(alpha=.3, which='both')
        x = res[name]['mc']['3.2']
        ax.set_title(f"{name}\nk_GK {x['k_gk']['k']:+.2f}, k_RB {x['k_rb']['k']:+.2f} → Δb(eğim) {x['db_egimden']:+.2f}; Δb {x['db']:+.2f}", fontsize=8)
        ax.set_xlabel('M (EMSC)')
    axs[0].set_ylabel('Kalan oran f(M) = N_ayrıştırılmış / N_ham'); axs[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'fig_ayiklama.png')); plt.close(fig)


if __name__ == '__main__':
    main()
