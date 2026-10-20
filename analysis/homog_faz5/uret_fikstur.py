"""Faz 5 — katman testinin referans fikstürü: sabitlenmiş prototip kataloğunun (faz4_merdiven.build_P) özeti + Weichert sonuçları.
Kullanım: python3 analysis/homog_faz5/uret_fikstur.py <hedef depo kökü>"""
import importlib.util, json, sys, io, contextlib, subprocess, hashlib
from datetime import datetime, timezone
s = importlib.util.spec_from_file_location('f4', 'analysis/homog_faz4/faz4_merdiven.py'); F4 = importlib.util.module_from_spec(s); s.loader.exec_module(F4)
with contextlib.redirect_stdout(io.StringIO()): P, _ = F4.build_P()
subprocess.run(['git', 'checkout', '--', 'analysis/homog_faz3/out/faz3_rapor.json'], check=False)
def ms(t):
    t = t.replace(' ', 'T').rstrip('Z'); d, _, f = t.partition('.')
    return int(datetime.fromisoformat(d).replace(tzinfo=timezone.utc).timestamp() * 1000) + (int((f + '000')[:3]) if f else 0)   # ms'ye kesme (ECMAScript Date.parse ile aynı)
lines = sorted(f"{ms(e['time'])}|{e['lat']:.4f}|{e['lon']:.4f}|{e['M']:.3f}" for e in P if e['M'] is not None)
E5 = json.load(open('analysis/homog_faz5/out/etki_weichert.json'))['sonuc']
ref = {r['fn']: {'N': r['N'], 'b': r['b'], 'sigma': r['sigma'], 'rate_m0': r['rate_m0']} for r in E5 if r['cat'] == 'C1_ham' and r['ln'] == 'L1_aday'}
commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
json.dump({'aciklama': 'ISC-GEM katmanı açıkken (mw_authority önceliği KAPALI) tarayıcı kataloğu, sabitlenmiş prototiple (homog-faz0 faz4_merdiven.build_P) birebir aynı olmalı.',
           'uretim': f'analysis/homog_faz5/uret_fikstur.py @ homog-faz0 {commit[:12]}', 'n': len(lines),
           'ozet_sha256': hashlib.sha256('\n'.join(lines).encode()).hexdigest(), 'ozet_bicim': 'sıralı satırlar: epoch_ms|lat(4)|lon(4)|M(3), UTC',
           'weichert_C1_ham_L1': ref, 'weichert_pencere': ['1900-01-01', '2021-12-31'], 'L1': [['1904', 6.0], ['1970', 5.5], ['1979', 4.5], ['1980', 4.0], ['1990', 3.5], ['1998', 3.0]],
           'korunan_sha256': {p: hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in ('data/eq_historical.json', 'data/mw_authority.json')}},
          open(f'{sys.argv[1]}/scripts/fixtures/iscgem_overlay_ref.json', 'w'), ensure_ascii=False, indent=1)
print(len(lines))
