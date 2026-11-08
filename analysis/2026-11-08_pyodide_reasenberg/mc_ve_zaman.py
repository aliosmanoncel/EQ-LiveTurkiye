"""
mc_ve_zaman.py — iki duyarlılık ölçümü (dondurulmuş modül + adaptör, zmap; değişiklik yok).

(1) Mc duyarlılığı: xmeff = 3,0 (statik ürün) ile 3,2 (sitenin MAXC+0,2 tahmini) arasındaki fark.
    A: katalog M ≥ 3,0, xmeff 3,0   (statik ürünün yapılandırması)
    B: katalog M ≥ 3,0, xmeff 3,2   (yalnız parametre değişir; aynı katalog)
    C: katalog M ≥ 3,2, xmeff 3,2   (modülün önerdiği tutarlı kurulum: katalog xmeff'te kesilir)
    Kapsam: tüm EMSC kataloğu + sinir_etkisi.py'deki 18 daire (aynı bölge, aynı dönem).
    Ölçüler: küme sayısı, bağımlı sayısı (ve oranı), ortak olaylarda sınıfı değişen oran,
    A'daki kümelerin (ortak olaylarla sınırlı, ≥2 üye) aynen yeniden üretilme oranı.
(2) Zaman penceresi sınırı: tüm katalog referansına göre, yalnız bir zaman penceresindeki olaylarla
    yapılan hesapta sınıfı değişen oran; pencere başından geçen süreye göre.
Bu ölçümler duyarlılıktır; doğruluk ölçüsü değildir.

Kullanım (depo kökünden): python analysis/2026-11-08_pyodide_reasenberg/mc_ve_zaman.py
"""
import json, math, os, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

sys.path.insert(0, 'scripts')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decluster_reasenberg as D  # noqa: E402
from sinir_etkisi import CENTERS, RADII, km  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def run(events, xmeff):
    evs, o = D.decluster(events, xmeff, 'zmap', 'mag')
    cls = {e['id']: (c != 'dependent') for e, c in zip(evs, o['event_class'])}
    clusters = defaultdict(set)
    for e, cid in zip(evs, o['cluster_id']):
        if cid >= 0:
            clusters[cid].add(e['id'])
    return dict(indep=cls, clusters=[frozenset(v) for v in clusters.values()], n_clusters=o['res'].n_clusters,
                dependent=sum(1 for v in cls.values() if not v), n=len(cls))


def compare(a, b):
    common = set(a['indep']) & set(b['indep'])
    changed = sum(a['indep'][i] != b['indep'][i] for i in common)
    ca = {c & common for c in a['clusters']}
    ca = {c for c in ca if len(c) >= 2}
    cb = {c & common for c in b['clusters']}
    same = len(ca & cb)
    return dict(common=len(common), changed=changed, changed_pct=round(100 * changed / len(common), 3) if common else None,
                clusters_reproduced_pct=round(100 * same / len(ca), 2) if ca else None)


def summary(r):
    return dict(n=r['n'], clusters=r['n_clusters'], dependent=r['dependent'],
                dependent_pct=round(100 * r['dependent'] / r['n'], 3))


def pct(x, y):
    return round(100 * (x - y) / y, 2) if y else None


def mc_part(ev):
    ev32 = [e for e in ev if e['mag'] >= 3.2 - 1e-9]
    scopes = [('tüm EMSC', ev, ev32)]
    for name, (la, lo) in CENTERS.items():
        for R in RADII:
            sub = [e for e in ev if km(la, lo, e['lat'], e['lon']) <= R]
            if len(sub) >= 50:
                scopes.append((f'{name} R={R}', sub, [e for e in sub if e['mag'] >= 3.2 - 1e-9]))
    rows = []
    for name, s30, s32 in scopes:
        A, B, C = run(s30, 3.0), run(s30, 3.2), run(s32, 3.2)
        rows.append(dict(scope=name, A=summary(A), B=summary(B), C=summary(C),
                         B_vs_A=dict(compare(A, B), clusters_change_pct=pct(B['n_clusters'], A['n_clusters']),
                                     dependent_change_pct=pct(B['dependent'], A['dependent'])),
                         C_vs_A=dict(compare(A, C), clusters_change_pct=pct(C['n_clusters'], A['n_clusters']),
                                     dependent_change_pct=pct(C['dependent'], A['dependent']))))
    return rows


def parse(t):
    return datetime.fromisoformat(t.replace('Z', '+00:00'))


def time_part(ev):
    ref = run(ev, 3.0)['indep']
    t_end = max(parse(e['time']) for e in ev)
    U = lambda s: datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
    windows = [('son 90 gün', t_end - timedelta(days=90), t_end), ('son 1 yıl', t_end - timedelta(days=365), t_end),
               ('son 5 yıl', t_end - timedelta(days=5 * 365), t_end),
               ('1999-09-01 → 1999-12-31 (İzmit sonrası başlar)', U('1999-09-01'), U('1999-12-31T23:59:59')),
               ('2020 yılı', U('2020-01-01'), U('2020-12-31T23:59:59')),
               ('2023-02-10 → 2023-12-31 (Kahramanmaraş sonrası başlar)', U('2023-02-10'), U('2023-12-31T23:59:59'))]
    bins = [(0, 30), (30, 365), (365, math.inf)]
    rows, agg = [], {b: [0, 0] for b in bins}
    for name, t0, t1 in windows:
        sub = [e for e in ev if t0 <= parse(e['time']) <= t1]
        dyn = run(sub, 3.0)['indep']
        per = {b: [0, 0] for b in bins}
        for e in sub:
            d = (parse(e['time']) - t0).total_seconds() / 86400
            b = next(b for b in bins if b[0] <= d < b[1])
            ch = dyn[e['id']] != ref[e['id']]
            per[b][0] += ch; per[b][1] += 1; agg[b][0] += ch; agg[b][1] += 1
        ch = sum(v[0] for v in per.values())
        rows.append(dict(window=name, n=len(sub), changed=ch, changed_pct=round(100 * ch / len(sub), 3),
                         dependent_ref=sum(1 for e in sub if not ref[e['id']]),
                         dependent_dyn=sum(1 for e in sub if not dyn[e['id']]),
                         by_days_since_start={f'{b[0]}-{b[1]}': v for b, v in per.items()}))
    return rows, {f'{b[0]}-{b[1]} gün': dict(changed=v[0], n=v[1], pct=round(100 * v[0] / v[1], 3) if v[1] else None)
                  for b, v in agg.items()}


def main():
    ev = [e for e in json.load(open('data/eq_historical.json', encoding='utf-8'))['events'] if e.get('src') == 'EMSC']
    mc = mc_part(ev)
    tw, tw_agg = time_part(ev)
    out = dict(module_sha256=D.module_sha256(), rule='zmap', catalog='data/eq_historical.json src=EMSC',
               mc_sensitivity=mc, time_window=tw, time_window_aggregate=tw_agg)
    with open(os.path.join(HERE, 'mc_ve_zaman.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('(1) Mc duyarlılığı — B: aynı katalog xmeff 3,2 · C: katalog ve xmeff 3,2 (A = 3,0 referans)')
    print(f"{'kapsam':22s} {'N':>6s} {'küme A':>7s} {'B Δ%':>7s} {'C Δ%':>7s} {'bağımlı A':>9s} {'B Δ%':>7s} {'C Δ%':>7s} {'B sınıf%':>9s} {'C sınıf%':>9s} {'B küme aynı%':>12s} {'C küme aynı%':>12s}")
    for r in mc:
        print(f"{r['scope']:22s} {r['A']['n']:6d} {r['A']['clusters']:7d} {r['B_vs_A']['clusters_change_pct']:7.2f} {r['C_vs_A']['clusters_change_pct']:7.2f} "
              f"{r['A']['dependent']:9d} {r['B_vs_A']['dependent_change_pct']:7.2f} {r['C_vs_A']['dependent_change_pct']:7.2f} "
              f"{r['B_vs_A']['changed_pct']:9.3f} {r['C_vs_A']['changed_pct']:9.3f} {r['B_vs_A']['clusters_reproduced_pct']:12.2f} {r['C_vs_A']['clusters_reproduced_pct']:12.2f}")
    print('\n(2) Zaman penceresi — tüm katalog referansına göre sınıfı değişen')
    for r in tw:
        print(f"{r['window']:52s} N {r['n']:6d}  değişen {r['changed']:5d} (%{r['changed_pct']:.2f})  bağımlı {r['dependent_ref']}→{r['dependent_dyn']}")
    print('pencere başından geçen süreye göre:', {k: v['pct'] for k, v in tw_agg.items()})


if __name__ == '__main__':
    main()
