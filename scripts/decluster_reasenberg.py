"""
decluster_reasenberg.py
Reasenberg (1985) kume ayiklamasi — Python secenegi (GK74'un YERINE degil, YANINDA).

Algoritma: scripts/reasenberg.py (bagimsiz uygulama, v0.3.0, DONDURULMUS;
sha256 c5b1248af557f29b4f04bf7c6ed9adfefd97c4153975a8989804b872ccf99bc9).
Bu betik yalnizca EQ-Live katalog bicimini o module baglar; algoritmaya dokunmaz.

Kurallar (WORKFLOW.md -> 1F):
  * --rule zmap          VARSAYILAN. ZMAP/bruces iki testli baglanti yapisi.
  * --rule cluster2000x  DENEYSEL. USGS cluster2000x kaynagindan yeniden kurulmus;
                         derlenmis Fortran ile olay bazinda dogrulama (D1) acik.
  * Ana cikti: TEMSILCI olay (kumenin en buyuk olayi) + kumelenmemis tekil olaylar.
    Esdeger olaylar (cluster2000x ciktisi) yalnizca duyarlilik amacli: --equivalent.
  * Siniflar: single (tekil), representative (temsilci), dependent (bagimli).
    "Bagimsiz" = single + representative. Bunlar algoritmanin siniflaridir,
    fiziksel ana sok iddiasi degildir.

Varsayimlar (ciktiya yazilir):
  * Zamanlar UTC (decluster_gk74.parse_time_ms ile ayni ayristirici).
  * Derinlikler katalogda kayitli oldugu gibi; mesafe hiposantraldir
    (GK74 episantral kullanir). 10 km gibi kayitli derinlikler dahil.
  * Katalogda konum hatasi yok: err = derr = 0 (belgelenmis varsayim,
    "hata sifirdir" anlamina gelmez).
  * Zamani/buyuklugu/koordinati/derinligi gecersiz olay kumelemeye girmez ve
    CIKARILMAZ (GK74 ile ayni ilke); sayisi ciktiya yazilir.
  * xmeff ZORUNLUDUR (genellikle Mc). Karisik donemli katalogda tek xmeff,
    tamamlilik farklarini yok saymak demektir; bkz. WORKFLOW.md 1F.

Kullanim:
  python scripts/decluster_reasenberg.py --xmeff 3.0 \
         --input data/eq_historical.json --output data/eq_historical_dc_reasenberg.json
  --src EMSC          : yalniz bu kaynaktaki olaylar (orn. 1998-2026 EMSC donemi)
  --mag-field mw      : tarayicidaki gibi e.mw ?? e.mag
  --membership        : tum olaylar icin [id, kume, sinif] listesini de yaz
  --equivalent        : kume basina esdeger olaylari da yaz (duyarlilik ciktisi)
"""

import argparse
import hashlib
import json
import os
import sys
import warnings
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decluster_gk74 import _num, event_mag, parse_time_ms  # noqa: E402
import reasenberg as R  # noqa: E402

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ADAPTER_VERSION = 'reasenberg-adapter-2026-11-07'  # strict JSON (inf -> "inf")
MODULE_SHA256_FROZEN = 'c5b1248af557f29b4f04bf7c6ed9adfefd97c4153975a8989804b872ccf99bc9'
CLASS = {R.SINGLE: 'single', R.REPRESENTATIVE: 'representative', R.DEPENDENT: 'dependent'}


def json_safe(obj):
    """Strict JSON: +/-inf -> "inf"/"-inf", NaN -> None (Python would write Infinity/NaN,
    which browsers' JSON.parse rejects). Used for every file this module writes."""
    if isinstance(obj, float):
        if obj != obj:
            return None
        if obj in (float('inf'), float('-inf')):
            return 'inf' if obj > 0 else '-inf'
        return obj
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    return obj


def _sha_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def module_sha256():
    return _sha_file(R.__file__)


def decluster(events, xmeff, rule='zmap', mag_field='mag', **params):
    """Donus: (zaman sirali olaylar, sonuc sozlugu).

    sonuc: cluster_id (-1 = kume yok), event_class ('single' | 'representative' |
    'dependent' | 'invalid'), independent (bool), res (ReasenbergResult, gecerli
    olaylar uzerinde), valid_index (gecerli olaylarin sirali listedeki indisleri).
    """
    rows = []
    for e in events:
        rows.append((e, parse_time_ms(e.get('time')), event_mag(e, mag_field),
                     _num(e.get('lat')), _num(e.get('lon')), _num(e.get('dep'))))
    rows.sort(key=lambda r: (r[1] is None, r[1] if r[1] is not None else 0))   # GK74 ile ayni
    n = len(rows)
    valid = [i for i, r in enumerate(rows) if None not in r[1:]]
    cid = [-1] * n
    ecls = ['invalid'] * n
    res = None
    if valid:
        t = np.array([rows[i][1] for i in valid], float) / 86400000.0
        m = np.array([rows[i][2] for i in valid], float)
        la = np.array([rows[i][3] for i in valid], float)
        lo = np.array([rows[i][4] for i in valid], float)
        z = np.array([rows[i][5] for i in valid], float)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', R.ExperimentalRuleWarning)
            warnings.simplefilter('ignore', UserWarning)          # M < xmeff: sayisi ayrica raporlanir
            res = R.reasenberg(t, la, lo, z, m, xmeff=float(xmeff), rule=rule,
                               err=0.0, derr=0.0, **params)
        for k, i in enumerate(valid):
            cid[i] = int(res.cluster_id[k])
            ecls[i] = CLASS[int(res.event_class[k])]
    independent = [c != 'dependent' for c in ecls]           # gecersiz olay cikarilmaz
    return [r[0] for r in rows], dict(cluster_id=cid, event_class=ecls, independent=independent,
                                      res=res, valid_index=valid,
                                      mags=[r[2] for r in rows])


def main(argv=None):
    ap = argparse.ArgumentParser(description='Reasenberg (1985) kume ayiklamasi (Python secenegi)')
    ap.add_argument('--input', default='data/eq_historical.json')
    ap.add_argument('--output', default='data/eq_historical_dc_reasenberg.json')
    ap.add_argument('--xmeff', type=float, required=True, help='etkin alt buyukluk (genellikle Mc); zorunlu')
    ap.add_argument('--rule', choices=['zmap', 'cluster2000x'], default='zmap')
    ap.add_argument('--mag-field', choices=['mag', 'mw'], default='mag')
    ap.add_argument('--src', default=None, help="yalniz bu kaynak (orn. EMSC)")
    ap.add_argument('--membership', action='store_true')
    ap.add_argument('--equivalent', action='store_true')
    a = ap.parse_args(argv)

    if module_sha256() != MODULE_SHA256_FROZEN:
        sys.exit('scripts/reasenberg.py dondurulmus v0.3.0 ile ayni degil (sha256 farkli). Durduruldu.')

    with open(a.input, 'rb') as f:
        raw = f.read()
    data = json.loads(raw.decode('utf-8'))
    events = data['events']
    if a.src:
        events = [e for e in events if e.get('src') == a.src]

    evs, out = decluster(events, a.xmeff, a.rule, a.mag_field)
    res = out['res']
    n = len(evs)
    main_events = [e for e, ind in zip(evs, out['independent']) if ind]
    removed = n - len(main_events)
    below = sum(1 for mm in out['mags'] if mm is not None and mm < a.xmeff - 1e-9)
    invalid = sum(1 for c in out['event_class'] if c == 'invalid')
    status = 'experimental' if a.rule == 'cluster2000x' else 'default'

    print(f'[*] {n} olay | kural {a.rule} ({status}) | xmeff {a.xmeff}')
    print(f'[*] Bagimsiz: {len(main_events)} | Bagimli: {removed} ({100 * removed // max(n, 1)}%) | '
          f'kume {res.n_clusters if res else 0} | gecersiz {invalid} | M<xmeff {below}')

    params = dict(res.params.__dict__) if res else {}
    result = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': data.get('source', '') + f' | Declustered: Reasenberg (1985), rule={a.rule}',
        'method': (f'Reasenberg (1985) | rule={a.rule} ({status}) | output=representative + single | '
                   f'mag_field={a.mag_field} | UTC'),
        'reasenberg': {
            'module': 'scripts/reasenberg.py', 'module_version': R.__version__,
            'module_sha256': module_sha256(), 'adapter_version': ADAPTER_VERSION,
            'adapter_sha256': _sha_file(os.path.abspath(__file__)),
            'rule': a.rule, 'rule_status': status, 'params': params,
            'input': a.input, 'input_sha256': hashlib.sha256(raw).hexdigest(),
            'src_filter': a.src,
            'assumptions': [
                'depths as recorded in the catalog (hypocentral distance)',
                'err = derr = 0: catalog has no location errors (documented assumption)',
                'invalid time/magnitude/coordinates/depth: not clustered, not removed',
                'classes are algorithmic (single/representative/dependent), not physical mainshocks',
            ],
            'n_clusters': res.n_clusters if res else 0,
            'n_single': int(sum(c == 'single' for c in out['event_class'])),
            'n_representative': int(sum(c == 'representative' for c in out['event_class'])),
            'n_dependent': removed, 'n_invalid': invalid, 'n_below_xmeff': below,
        },
        'original_n': n,
        'main_n': len(main_events),
        'removed_n': removed,
        'count': len(main_events),
        'events': main_events,
    }
    if a.membership:
        result['membership'] = [[e.get('id'), c, k] for e, c, k in
                                zip(evs, out['cluster_id'], out['event_class'])]
    if a.equivalent and res is not None and res.n_clusters:
        vi = out['valid_index']
        tt = np.array([parse_time_ms(evs[i].get('time')) for i in vi], float) / 86400000.0
        eq = R.equivalent_events(res, tt,
                                 [float(evs[i]['lat']) for i in vi], [float(evs[i]['lon']) for i in vi],
                                 [float(evs[i]['dep']) for i in vi], [out['mags'][i] for i in vi])
        result['equivalent_events_sensitivity_only'] = [
            dict(cluster=k, representative_id=evs[vi[int(res.representative[k])]].get('id'),
                 lat=round(float(eq['a'][k]), 4), lon=round(float(eq['b'][k]), 4),
                 dep=round(float(eq['depth'][k]), 2), mag=round(float(eq['magnitude'][k]), 3),
                 n=int(eq['n'][k]))
            for k in range(res.n_clusters)]

    with open(a.output, 'w', encoding='utf-8') as f:
        json.dump(json_safe(result), f, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    print(f'[OK] Kaydedildi: {a.output}')
    return result


if __name__ == '__main__':
    main()
