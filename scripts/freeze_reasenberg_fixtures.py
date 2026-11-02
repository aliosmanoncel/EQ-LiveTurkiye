"""
freeze_reasenberg_fixtures.py — Reasenberg (zmap) DONMUS REGRESYON REFERANSLARI.

Mevcut GK74 baglam alt kataloglari (scripts/fixtures/gk74_ctx_*_catalog.json)
uzerinde decluster_reasenberg.py'nin ciktisini dondurur. Bu bir DOGRULAMA DEGILDIR:
yalnizca modulun ve adaptorun davranisinin degismedigini denetler
(scripts/reasenberg_tests/test_adapter.py). Yeni kural/parametre = yeni sürüm + yeni fixture.

Kullanim (depo kokunden):  python scripts/freeze_reasenberg_fixtures.py
"""
import hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decluster_reasenberg as D  # noqa: E402

NAMES = ['adiyaman', 'izmit_dogu', 'saimbeyli', 'van_bati']
XMEFF = 3.0


def freeze(name):
    cat = f'scripts/fixtures/gk74_ctx_{name}_catalog.json'
    raw = open(cat, 'rb').read()
    evs, out = D.decluster(json.loads(raw.decode('utf-8'))['events'], XMEFF, 'zmap', 'mag')
    fx = dict(frozen='2026-11-03', kind='regression reference (not a validation)',
              adapter_version=D.ADAPTER_VERSION, module_sha256=D.module_sha256(),
              catalog=cat, catalog_sha256=hashlib.sha256(raw).hexdigest(),
              params=dict(xmeff=XMEFF, rule='zmap', mag_field='mag'),
              n=len(evs),
              independent_ids=sorted(e['id'] for e, i in zip(evs, out['independent']) if i),
              membership=[[e['id'], c, k] for e, c, k in zip(evs, out['cluster_id'], out['event_class'])])
    path = f'scripts/fixtures/reasenberg_zmap_{name}_ref.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(fx, f, ensure_ascii=False, separators=(',', ':'))
    print(f'{path}: n {fx["n"]} | bagimsiz {len(fx["independent_ids"])}')


if __name__ == '__main__':
    for nm in NAMES:
        freeze(nm)
