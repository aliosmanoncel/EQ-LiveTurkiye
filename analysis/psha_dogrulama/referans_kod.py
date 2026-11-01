"""Mevcut seismo-report PSHA kodunun (DONDURULMUŞ kopya, kaynak_kod/) referans çıktısını üretir. Kod değiştirilmez; geçici bir
çalışma klasöründe olduğu gibi çalıştırılır (şekilleri o klasöre yazar) ve hesaplanan dizileri referans_kod.npz'ye kaydeder.
Kaynak: seismo-report commit cac09bf (2026-06-10), scripts/mindanao_psha.py SHA-1 43342f92…, scripts/mindanao_logic_tree.py."""
import runpy, os, sys, tempfile, hashlib, json, numpy as np, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); K = os.path.join(HERE, 'kaynak_kod')
sha = {f: hashlib.sha1(open(os.path.join(K, f), 'rb').read()).hexdigest() for f in ('mindanao_psha.py', 'mindanao_logic_tree.py')}
out = {}
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, 'OUTPUT', 'PSHA')); cwd = os.getcwd(); os.chdir(d)
    try:
        class _B(io.StringIO):
            def reconfigure(self, **k): pass   # kaynak kod sys.stdout.reconfigure çağırıyor
        buf = _B()
        with contextlib.redirect_stdout(buf):
            g1 = runpy.run_path(os.path.join(K, 'mindanao_psha.py'))
            g2 = runpy.run_path(os.path.join(K, 'mindanao_logic_tree.py'))
        log = buf.getvalue()
    finally: os.chdir(cwd)
for k in ('x_im', 'M_bins', 'c1_med', 'c1_1sig', 'c1_2sig', 'c2_med', 'c_ftls', 'c_comb'): out['psha_' + k] = np.asarray(g1[k])
for k in ('branch_curves', 'branch_weights', 'lam_mean', 'frac_curves'): out['lt_' + k] = np.asarray(g2[k])
out['lt_x_im'] = np.asarray(g2['x_im'])
np.savez(os.path.join(HERE, 'referans_kod.npz'), **out)
open(os.path.join(HERE, 'referans_kod_cikti.txt'), 'w', encoding='utf-8').write(log)
json.dump({'sha1': sha, 'seismo_report_commit': 'cac09bf', 'diziler': {k: list(v.shape) for k, v in out.items()}}, open(os.path.join(HERE, 'referans_kod_kimlik.json'), 'w'), indent=1)
print(json.dumps(sha)); print(log[-1500:])
