"""
mwauth_sensitivity.py — Duyarlilik: otoriter Mw (WORKFLOW 1E, data/mw_authority.json, yalniz
'verified' kayitlar; projedeki mw_authority.build_override eslesmesi) IKI YONTEME BIRLIKTE
uygulanirsa GK74 / Reasenberg (zmap) farki nasil degisir?

Taban (A): site urunuyle ayni (mag alani). Duyarlilik (B): eslesen buyuk depremlerde
buyukluk = otoriter Mw; diger olaylar degismez. Ayni 80 929 olay, ayni kod.
Bu bir duyarlilik analizidir; urun, site ve main degismez.

Kullanim (depo kokunden): python analysis/2026-11-07_rb_gk74_farklar/mwauth_sensitivity.py
"""

import copy
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)
import decluster_gk74 as GK  # noqa: E402
import decluster_reasenberg as RB  # noqa: E402
from mw_authority import build_override, load_table  # noqa: E402


def classify(events):
    g_evs, g_cl = GK.decluster(events, 'mag')
    r_evs, out = RB.decluster(events, 3.0, 'zmap', 'mag')
    assert [e['id'] for e in g_evs] == [e['id'] for e in r_evs]
    cat = {}
    for e, c, k in zip(g_evs, g_cl, out['event_class']):
        gi, ri = (not c), (k != 'dependent')
        cat[e['id']] = ('both_independent' if gi and ri else 'GK_only_independent' if gi else
                        'R_only_independent' if ri else 'both_dependent')
    return cat, out['res'].n_clusters


def near(events, ids, ent, km, days):
    t0 = GK.parse_time_ms(ent['time_utc'])
    return [e['id'] for e in events
            if 0 < GK.parse_time_ms(e['time']) - t0 <= days * 86400000
            and GK.haversine(ent['lat'], ent['lon'], e['lat'], e['lon']) <= km]


def main():
    em = [e for e in json.loads(open('data/eq_historical.json', 'rb').read().decode('utf-8'))['events']
          if e.get('src') == 'EMSC']
    T, ents = load_table('data/mw_authority.json')
    ov = build_override(em, ents)
    em_b = []
    matched = []
    for e in em:
        ent = ov.get(id(e))
        if ent is not None:
            e2 = copy.deepcopy(e)
            e2['mag'] = ent['mw']
            em_b.append(e2)
            matched.append(dict(name=ent['name'], id=e['id'], time=e['time'], catalog_mag=e['mag'],
                                catalog_mtype=e['mtype'], mw=ent['mw']))
        else:
            em_b.append(e)

    A, nA = classify(em)
    B, nB = classify(em_b)
    cA, cB = Counter(A.values()), Counter(B.values())
    n = len(em)
    trans = Counter((A[i], B[i]) for i in A if A[i] != B[i])

    per_event = []
    for m in matched:
        ent = next(x for x in ents if x['name'] == m['name'])
        ids = near(em, None, ent, 100, 365)            # 100 km, 1 yil sonrasi
        ra = sum(A[i] == 'R_only_independent' for i in ids)
        rb = sum(B[i] == 'R_only_independent' for i in ids)
        da = sum(A[i] in ('both_dependent',) for i in ids)
        db = sum(B[i] in ('both_dependent',) for i in ids)
        per_event.append(dict(**m, n_within_100km_1yr=len(ids), R_only_A=ra, R_only_B=rb,
                              both_dependent_A=da, both_dependent_B=db))

    res = dict(
        table=dict(file='data/mw_authority.json', version=T.get('version'), verified_entries=len(ents)),
        matched_in_EMSC_subset=matched,
        A_baseline=dict(categories=dict(cA), agreement=round((cA['both_independent'] + cA['both_dependent']) / n, 4),
                        reasenberg_clusters=nA),
        B_authoritative_Mw=dict(categories=dict(cB), agreement=round((cB['both_independent'] + cB['both_dependent']) / n, 4),
                                reasenberg_clusters=nB),
        events_changing_category=sum(trans.values()),
        transitions={f'{a} -> {b}': v for (a, b), v in trans.most_common()},
        per_large_event_100km_1yr=per_event,
        note='Yalniz otoriter Mw tablosundaki dogrulanmis buyuk depremlerin buyuklugu degisir; '
             'yuzlerce kucuk mb/ML/MD olayinin olcegi degismez.',
    )
    json.dump(res, open(os.path.join(HERE, 'mwauth_sensitivity.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
