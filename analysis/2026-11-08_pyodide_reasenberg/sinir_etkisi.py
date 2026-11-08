"""
sinir_etkisi.py — D-P2: daire sınırı Reasenberg üyeliğini ne kadar değiştiriyor?

Yöntem (dondurulmuş modül + adaptör, değişiklik yok):
  Referans  : tüm EMSC kataloğunda (1998–2026, 80 929 olay) tek bir hesap; daire içindeki
              olayların sınıfı bu hesaptan alınır (sınır yok sayılır).
  Dinamik   : yalnız daire içindeki olaylarla hesap (sitedeki bölge sorgusu gibi).
  Ölçü      : daire içindeki her olay için "bağımsız (tekil+temsilci) / bağımlı" sınıfı iki hesapta
              farklı mı? Kenara uzaklık d, ölçek L = 10·r(Mmax) = 10·0.011·10^(0.4·Mmax) km ile
              (gates.mjs K7 ile aynı) normalleştirilir.
Sonuç: sinir_etkisi.json ve ekrana özet. Bu bir duyarlılık ölçümüdür, algoritmanın doğrulaması değildir.

Kullanım (depo kökünden): python analysis/2026-11-08_pyodide_reasenberg/sinir_etkisi.py
"""
import json, math, os, sys

sys.path.insert(0, 'scripts')
import decluster_reasenberg as D  # noqa: E402

XMEFF = 3.0
CENTERS = {'izmit': (40.75, 29.95), 'van': (38.60, 43.40), 'kahramanmaras': (37.60, 37.00),
           'denizli': (37.90, 29.10), 'elazig': (38.60, 39.20), 'ege_samos': (37.80, 26.80)}
RADII = [50, 100, 200]
BINS = [(0, 0.5), (0.5, 1), (1, 2), (2, math.inf)]


def km(a, b, c, d):
    r = math.pi / 180
    x = math.sin((c - a) * r / 2) ** 2 + math.cos(a * r) * math.cos(c * r) * math.sin((d - b) * r / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(min(1, x)))


def indep_map(events):
    evs, o = D.decluster(events, XMEFF, 'zmap', 'mag')
    return {e['id']: (c != 'dependent') for e, c in zip(evs, o['event_class'])}


def main():
    ev = [e for e in json.load(open('data/eq_historical.json', encoding='utf-8'))['events'] if e.get('src') == 'EMSC']
    ref = indep_map(ev)
    rows = []
    agg = {b: [0, 0] for b in BINS}
    for name, (la, lo) in CENTERS.items():
        for R in RADII:
            sub = [e for e in ev if km(la, lo, e['lat'], e['lon']) <= R]
            if len(sub) < 50:
                continue
            dyn = indep_map(sub)
            mmax = max(e['mag'] for e in sub)
            L = min(R, 10 * 0.011 * 10 ** (0.4 * mmax))
            per = {b: [0, 0] for b in BINS}
            near = 0
            for e in sub:
                d = R - km(la, lo, e['lat'], e['lon'])
                near += d <= L
                x = d / (10 * 0.011 * 10 ** (0.4 * mmax))
                b = next(b for b in BINS if b[0] <= x < b[1])
                ch = dyn[e['id']] != ref[e['id']]
                per[b][0] += ch; per[b][1] += 1
                agg[b][0] += ch; agg[b][1] += 1
            changed = sum(v[0] for v in per.values())
            dep_ref = sum(1 for e in sub if not ref[e['id']])
            dep_dyn = sum(1 for e in sub if not dyn[e['id']])
            rows.append(dict(center=name, R=R, n=len(sub), mmax=mmax, L_km=round(L, 1),
                             k7_near_frac=round(near / len(sub), 3), changed=changed,
                             changed_frac=round(changed / len(sub), 4),
                             dependent_ref=dep_ref, dependent_dyn=dep_dyn,
                             by_bin={f'{b[0]}-{b[1]}': [v[0], v[1]] for b, v in per.items()}))
    out = dict(xmeff=XMEFF, rule='zmap', reference='tüm EMSC kataloğu (sınırsız)', module_sha256=D.module_sha256(),
               cases=rows, aggregate_by_bin={f'{b[0]}-{b[1]}': dict(changed=v[0], n=v[1],
                                                                     frac=round(v[0] / v[1], 4) if v[1] else None)
                                             for b, v in agg.items()})
    with open(os.path.join(os.path.dirname(__file__), 'sinir_etkisi.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"{'merkez':14s} {'R':>4s} {'N':>6s} {'Mmax':>5s} {'L':>6s} {'K7 yakın':>9s} {'değişen':>8s} {'oran':>7s} {'bağımlı ref→din':>16s}")
    for r in rows:
        print(f"{r['center']:14s} {r['R']:4d} {r['n']:6d} {r['mmax']:5.1f} {r['L_km']:6.1f} {r['k7_near_frac']:9.3f} "
              f"{r['changed']:8d} {r['changed_frac']:7.3%} {r['dependent_ref']:>7d}→{r['dependent_dyn']:<7d}")
    print('Kenara uzaklık / L kutularında değişen oranı:', {k: v['frac'] for k, v in out['aggregate_by_bin'].items()})


if __name__ == '__main__':
    main()
