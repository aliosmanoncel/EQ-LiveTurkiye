"""Aşama A: altı job.ini'yi tam OpenQuake motor akışıyla (oq engine --run, classical) çalıştırır; sonuçları datastore'dan okur ve
İKİ bağımsız referansla karşılaştırır: (i) mevcut kod (referans_kod.npz), (ii) önceki calc_hazard_curves sonuçları (oq_egriler.npz).
Girdi denetimi: job girdilerindeki MFD oranları (oranlar.json) ile oq_karsilastirma.py'nin kullandığı aritmetik aynı mı (yeniden hesaplanır).
Ölçüt: 50 yıllık PoE 1e-5 … 0,999 aralığı (OpenQuake 32 bit), %10/50 ve %2/50 PGA, mantık ağacı ortalaması ve yüzdelikleri."""
import os, re, json, math, subprocess, numpy as np
from openquake.commonlib import datastore
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
REF = np.load(os.path.join(P, 'referans_kod.npz')); OQ1 = np.load(os.path.join(P, 'oq_egriler.npz')); x = REF['psha_x_im']; T = 50.0
lam = lambda poe: -np.log1p(-np.minimum(np.asarray(poe, float), 1 - 1e-16)) / T   # PoE = 1 (32 bit doygunluk) → sonlu
LMIN, LMAX = -math.log1p(-1e-5) / T, -math.log(1 - 0.999) / T
def fark(a, b):
    m = (b >= LMIN) & (b <= LMAX) & np.isfinite(a); r = np.abs(a[m] / b[m] - 1); return {'maks': float(r.max()), 'ort': float(r.mean()), 'nokta': int(m.sum())}
def pga(lt, c):
    v = c > 1e-12
    if lt < c[v][-1] or lt > c[v][0]: return float('nan')
    return float(np.exp(np.interp(np.log(lt), np.log(c[v][::-1]), np.log(x[v][::-1]))))
L10, L02, L50 = -math.log(0.9) / T, -math.log(0.98) / T, -math.log(0.5) / T
def calistir(ad):
    d = os.path.join(H, ad); out = subprocess.run(['oq', 'engine', '--run', 'job.ini'], cwd=d, capture_output=True, text=True, env={**os.environ, 'OQ_DISTRIBUTE': 'no'})
    m = re.findall(r'calc_(\d+)\.hdf5', out.stdout + out.stderr)
    if out.returncode or not m: raise SystemExit(f'{ad}: motor hatası\n{(out.stdout + out.stderr)[-3000:]}')
    return int(m[-1])
R = {'openquake_engine': None, 'joblar': {}, 'girdi_denetimi': {}}
import openquake.engine; R['openquake_engine'] = openquake.engine.__version__
# girdi denetimi: MFD oranları (job dosyaları) = kod aritmetiği (bağımsız yeniden hesap)
O = json.load(open(os.path.join(H, 'oranlar.json')))
def mfd(b, lam5, Mmin, Mmax, M_bins=None, dM=0.2):
    if M_bins is None: M_bins = np.arange(Mmin + dM / 2, Mmax, dM)
    A = 10 ** (-b * (M_bins - dM / 2 - Mmin)); B = 10 ** (-b * (Mmax - Mmin)); le = lam5 * (A - B) / (1 - B); le = np.where(M_bins <= Mmax, le, 0.0)
    return np.maximum(-np.diff(np.append(le, 0.0)), 0.0)
R['girdi_denetimi']['c1_med_s1'] = bool(np.allclose(O['c1_med/s1']['oran'], mfd(0.90, 3.0, 5.0, 8.5, REF['psha_M_bins']), rtol=0, atol=0))
R['girdi_denetimi']['lt_dallari'] = all(np.array_equal(np.array(v['oran']), mfd(v['b'], 3.0, 5.0, v['Mmax'])) for k, v in O.items() if k.startswith('lt/'))
for ad in ('c1_med', 'c1_1sig', 'c2_med', 'c_comb', 'c_ftls'):
    cid = calistir(ad); ds = datastore.read(cid); c = lam(ds['hcurves-rlzs'][0, 0, 0])   # (N, R, M, L)
    R['joblar'][ad] = {'calc_id': cid, 'kod': fark(c, REF['psha_' + ad]), 'calc_hazard_curves': fark(c, OQ1['A_' + ad]),
        'pga10': {'job': pga(L10, c), 'kod': pga(L10, REF['psha_' + ad]), 'chc': pga(L10, OQ1['A_' + ad])}, 'pga02': {'job': pga(L02, c), 'kod': pga(L02, REF['psha_' + ad]), 'chc': pga(L02, OQ1['A_' + ad])}}
    np.save(os.path.join(H, ad, 'lam_job.npy'), c); ds.close()
# mantık ağacı
cid = calistir('lt'); ds = datastore.read(cid); full = ds['full_lt']; rl = full.get_realizations()
cur = lam(ds['hcurves-rlzs'][0, :, 0]); st = ds['hcurves-stats'][0, :, 0]   # stats: mean, q0.05 … q0.95
B1 = [0.635, 0.900, 1.120]; B3 = [7.8, 8.0, 8.2]; G = [(0, 0.0), (0, 0.5), (1, 0.0)]
ref_idx = {}   # referans dal sırası: itertools.product(B1, B2, B3)
for i1 in range(3):
    for i2 in range(3):
        for i3 in range(3): ref_idx[(i1, i2, i3)] = len(ref_idx)
gmap = {b.id: b for b in full.gsim_lt.branches}; dal_fark, w_job = [], []
for k, r in enumerate(rl):
    f = os.path.basename(r.sm_lt_path[0]) if r.sm_lt_path else ''
    sm = int(r.sm_lt_path[0][1:]) if r.sm_lt_path[0].startswith('s') else None
    gb = gmap[r.gsim_lt_path[0]]; i1, i3 = divmod(sm, 3); i2 = G.index((int(gb.gsim.Zt), float(gb.gsim.eps))); j = ref_idx[(i1, i2, i3)]   # OpenQuake dal kimliklerini (gA0…) yeniden adlandırır → GMPE parametresinden eşlenir
    dal_fark.append(fark(cur[k], REF['lt_branch_curves'][j])['maks']); w_job.append((float(r.weight[0] if hasattr(r.weight, '__len__') else r.weight), float(REF['lt_branch_weights'][j])))
mean_job = lam(st[0]); q_job = [lam(st[i]) for i in range(1, 6)]
mean_from_rlz = np.array([w for w, _ in w_job]) @ cur
R['joblar']['lt'] = {'calc_id': cid, 'gerceklesme': len(rl), 'agirliklar_ayni': bool(np.allclose([a for a, b in w_job], [b for a, b in w_job])),
  'dal_maks_fark_kod': max(dal_fark), 'ortalama_kod': fark(mean_job, REF['lt_lam_mean']), 'ortalama_chc': fark(mean_job, OQ1['lam_mean_oq']),
  'not_ortalama': 'OpenQuake ortalaması PoE uzayında ağırlıklı ortalama (hcurves-stats); kod λ uzayında ortalıyor. Ayrıca λ uzayında gerçekleşmelerden ortalama da hesaplandı.',
  'ortalama_lambda_uzayinda_kod': fark(mean_from_rlz, REF['lt_lam_mean']),
  'tablo': {s: {'kod': {'ort': pga(lt, REF['lt_lam_mean']), **{q: pga(lt, REF['lt_frac_curves'][i]) for i, q in enumerate(['5.', '16.', '50.', '84.', '95.'])}},
                'job_istatistik': {'ort': pga(lt, mean_job), **{q: pga(lt, q_job[i]) for i, q in enumerate(['5.', '16.', '50.', '84.', '95.'])}},
                'job_lambda_ort': pga(lt, mean_from_rlz)} for s, lt in (('%50/50', L50), ('%10/50', L10), ('%2/50', L02))}}
np.savez(os.path.join(H, 'lt', 'lam_job.npz'), rlz=cur, mean=mean_job, q=np.array(q_job), mean_lambda=mean_from_rlz); ds.close()
json.dump(R, open(os.path.join(H, 'asamaA_sonuc.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False))
