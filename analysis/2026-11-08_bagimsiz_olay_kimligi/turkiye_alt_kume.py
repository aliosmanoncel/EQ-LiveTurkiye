"""
turkiye_alt_kume.py — 2. tur: Türkiye alt kümesinde GK74 ↔ Reasenberg (ayrı kataloglar).

Merkez soru: ~0,10'luk b farkı Türkiye'de sürüyor mu, yoksa Türkiye dışındaki olaylardan mı geliyor?
Alt küme: turkiye_sinir_{0,30,50}km.geojson (30 km ana tanım). Ham katalog aynı (EMSC 1998–2026, M ≥ 3,0).
İki uygulama, ikisi de raporlanır:
  (i)  yeniden: iki yöntem YALNIZ alt küme olaylarıyla yeniden çalıştırılır (sınır dışı olaylar bağ kuramaz);
  (ii) tam: tüm katalogdaki sınıf, alt kümeye süzülür (sınır kesilmesi yok).
Ayrıca Türkiye DIŞI (30 km tanımının tümleyeni) aynı ölçülerle — farkın kaynağını ayırmak için.
Sonuçlar birleştirilmez; fark yöntem duyarlılığıdır. Çıktı: turkiye_sonuc.json + ekran özeti.
"""
import json, os, sys

import numpy as np
from shapely.geometry import Point
from shapely.prepared import prep

sys.path.insert(0, 'scripts')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decluster_gk74 as GK  # noqa: E402
import decluster_reasenberg as D  # noqa: E402
from bok_analiz import aki_utsu, weichert, poisson_ci, p_exceed, parse, km, XMEFF  # noqa: E402
from turkiye_sinir import load  # noqa: E402


def mc_site(m):
    """index.html computeMcSrc ile aynı kural: 0,1 kutularında en kalabalık + 0,2 (ilk en büyük)."""
    bins = {}
    for x in m:
        k = f'{np.floor(x * 10 + 0.5) / 10:.1f}'   # JS Math.round (yarım yukarı)
        bins[k] = bins.get(k, 0) + 1
    best, cnt = None, -1
    for k, v in bins.items():
        if v > cnt:
            best, cnt = float(k), v
    return round(best + 0.2, 1) if best is not None else None


def classify(ev):
    gevs, gcl = GK.decluster(ev, 'mag')
    revs, o = D.decluster(ev, XMEFF, 'zmap', 'mag')
    return {e['id']: (not c) for e, c in zip(gevs, gcl)}, {e['id']: k != 'dependent' for e, k in zip(revs, o['event_class'])}


def apply_mwauth(ev):
    A = json.load(open('data/mw_authority.json', encoding='utf-8'))
    ev = [dict(e) for e in ev]
    for a in A['entries']:
        if a['status'] != 'verified':
            continue
        ta = parse(a['time_utc'])
        c = [e for e in ev if abs((parse(e['time']) - ta).total_seconds()) <= A['match']['dt_s'] and km(a['lat'], a['lon'], e['lat'], e['lon']) <= A['match']['dist_km']]
        if c:
            max(c, key=lambda e: e['mag'])['mag'] = a['mw']
    return ev


def summarize(ev, gk, rb, T, label):
    ids = [e['id'] for e in ev]
    cat = dict(ortak_bagimsiz=sum(gk[i] and rb[i] for i in ids), yalniz_gk74_bagimsiz=sum(gk[i] and not rb[i] for i in ids),
               yalniz_rb_bagimsiz=sum(rb[i] and not gk[i] for i in ids), ikisi_de_bagimli=sum(not gk[i] and not rb[i] for i in ids))
    m_all = np.array([e['mag'] for e in ev])
    mcs = mc_site(m_all)
    out = dict(etiket=label, n=len(ev), kimlik=cat, mc_site=mcs, b={})
    for mc in sorted({3.2, 3.5, mcs}):
        row = {}
        for name, ind in (('ham', None), ('gk74', gk), ('reasenberg', rb)):
            m = np.array([e['mag'] for e in ev if ind is None or ind[e['id']]])
            row[name] = dict(aki=aki_utsu(m, mc), weichert=weichert(m, mc, T))
        g, r = row['gk74']['aki'], row['reasenberg']['aki']
        if g and r:
            d = r['b'] - g['b']; s = (g['sigma_b'] ** 2 + r['sigma_b'] ** 2) ** 0.5
            row['fark_rb_eksi_gk'] = dict(db=d, sigma=s, oran=d / s if s else None)
        out['b'][f'{mc:.1f}'] = row
    big = {}
    for thr in (6.0, 7.0):
        r = {}
        for name, ind in (('ham', None), ('gk74', gk), ('reasenberg', rb)):
            k = sum(1 for e in ev if e['mag'] >= thr - 1e-9 and (ind is None or ind[e['id']]))
            lo, hi = poisson_ci(k)
            r[name] = dict(sayi=k, lam=k / T, lam95=[lo / T, hi / T], P1y=p_exceed(k / T, 1), P1y95=[p_exceed(lo / T, 1), p_exceed(hi / T, 1)])
        r['farkli'] = [f"{e['time'][:16]} M{e['mag']} {e['place'][:26]} — GK74 {'bağımsız' if gk[e['id']] else 'artçı'} / RB {'bağımsız' if rb[e['id']] else 'bağımlı'}"
                       for e in sorted(ev, key=lambda e: e['time']) if e['mag'] >= thr - 1e-9 and gk[e['id']] != rb[e['id']]]
        big[f'M{thr:g}'] = r
    out['buyuk'] = big
    return out


def main():
    raw = json.load(open('data/eq_historical.json', encoding='utf-8'))
    ev = [e for e in raw['events'] if e.get('src') == 'EMSC']
    t0, t1 = min(parse(e['time']) for e in ev), max(parse(e['time']) for e in ev)
    T = (t1 - t0).total_seconds() / (365.25 * 86400)
    gk_full, rb_full = classify(ev)
    evA = apply_mwauth(ev)
    gkA_full, rbA_full = classify(evA)
    res = dict(T_yil=T, n_tum=len(ev), alt_kumeler={})
    res['tum_bolge'] = summarize(ev, gk_full, rb_full, T, 'tüm bölge (80 929)')
    for B in (0, 30, 50):
        poly, props = load(B)
        P = prep(poly)
        inside = {e['id'] for e in ev if P.contains(Point(e['lon'], e['lat']))}
        sub = [e for e in ev if e['id'] in inside]
        subA = [e for e in evA if e['id'] in inside]
        gk_s, rb_s = classify(sub)
        gkA_s, rbA_s = classify(subA)
        res['alt_kumeler'][f'{B}km'] = dict(
            tanim=props['tanim'],
            yeniden=summarize(sub, gk_s, rb_s, T, f'Türkiye {B} km — yeniden çalıştırma'),
            tam=summarize(sub, gk_full, rb_full, T, f'Türkiye {B} km — tam katalog sınıfı'),
            yeniden_otoriter_mw=summarize(subA, gkA_s, rbA_s, T, f'Türkiye {B} km — yeniden, otoriter Mw'),
            sinif_degisen_yeniden_vs_tam=dict(gk74=sum(gk_s[i] != gk_full[i] for i in inside), reasenberg=sum(rb_s[i] != rb_full[i] for i in inside)))
        if B == 30:
            out_ev = [e for e in ev if e['id'] not in inside]
            gk_o, rb_o = classify(out_ev)
            res['turkiye_disi_30km'] = summarize(out_ev, gk_o, rb_o, T, 'Türkiye dışı (30 km tümleyeni) — yeniden')
    json.dump(res, open(os.path.join(HERE, 'turkiye_sonuc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)

    def line(s):
        b = s['b']
        parts = []
        for mc in ('3.2', '3.5'):
            r = b[mc]; f = r.get('fark_rb_eksi_gk')
            parts.append(f"Mc{mc}: GK {r['gk74']['aki']['b']:.3f}±{r['gk74']['aki']['sigma_b']:.3f}  RB {r['reasenberg']['aki']['b']:.3f}±{r['reasenberg']['aki']['sigma_b']:.3f}  Δb {f['db']:+.3f} ({f['oran']:.0f}σ)")
        k = s['kimlik']
        print(f"{s['etiket']:44s} N {s['n']:6d} Mc(site) {s['mc_site']}  | " + ' | '.join(parts))
        print(f"{'':44s} kimlik ortak {k['ortak_bagimsiz']} · yalnız GK {k['yalniz_gk74_bagimsiz']} · yalnız RB {k['yalniz_rb_bagimsiz']} · ikisi bağımlı {k['ikisi_de_bagimli']}")
        for thr in ('M6', 'M7'):
            x = s['buyuk'][thr]
            print(f"{'':44s} {thr}: ham {x['ham']['sayi']} GK {x['gk74']['sayi']} RB {x['reasenberg']['sayi']}  λ_GK {x['gk74']['lam']:.3f} [{x['gk74']['lam95'][0]:.3f}–{x['gk74']['lam95'][1]:.3f}]  λ_RB {x['reasenberg']['lam']:.3f}  fark: {x['farkli']}")
    line(res['tum_bolge'])
    for B in ('0km', '30km', '50km'):
        a = res['alt_kumeler'][B]
        line(a['yeniden']); line(a['tam']); line(a['yeniden_otoriter_mw'])
        print(f"{'':44s} yeniden↔tam sınıf değişen: {a['sinif_degisen_yeniden_vs_tam']}")
    line(res['turkiye_disi_30km'])


if __name__ == '__main__':
    main()
