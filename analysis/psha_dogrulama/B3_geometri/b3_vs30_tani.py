"""B3 ek çözümleme: (1) Vs30 etkisi — her geometri × GMPE için PGA(360) − PGA(760) ve ΔPGA(%) = (PGA360 − PGA760)/PGA760 × 100;
(2) uzaklık ölçeklenmesi tanısı — GMPE medyanının rrup ile azalması (M 6,0 ve 7,8; Vs30 760): geometri duyarlılığının neden modele bağlı olduğunu açıklar."""
import os, sys, json, math, warnings, numpy as np
warnings.filterwarnings('ignore'); H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(H))
R = json.load(open(os.path.join(H, 'b3_sonuc.json'), encoding='utf-8')); out = {'vs30': [], 'uzaklik': {}}
for kay in ('Cotabato', 'Davao'):
    for g in dict.fromkeys(r['geometri'] for r in R['sonuc'] if r['kaynak'] == kay):
        for m in dict.fromkeys(r['model'] for r in R['sonuc']):
            a, b = [[r for r in R['sonuc'] if r['kaynak'] == kay and r['geometri'] == g and r['model'] == m and r['Vs30'] == v][0] for v in (360.0, 760.0)]
            out['vs30'].append({'kaynak': kay, 'geometri': g, 'model': m, **{f'{s}_fark_g': a[s] - b[s] for s in ('pga10', 'pga02')}, **{f'{s}_fark_%': 100 * (a[s] / b[s] - 1) for s in ('pga10', 'pga02')}})
# uzaklık ölçeklenmesi: kontrol edilmiş bağlam (tek kırık, M, rrup, ztor = 35 km, Vs30 760)
from openquake.hazardlib.contexts import RuptureContext
from openquake.hazardlib.gsim import get_available_gsims; from openquake.hazardlib.imt import PGA; from kod_gmpe import MindanaoKodGMPE
G = get_available_gsims(); GM = [('Kod bağıntısı', MindanaoKodGMPE()), ('Youngs (1997)', G['YoungsEtAl1997SInter']()), ('BC Hydro (2016)', G['AbrahamsonEtAl2015SInter']()), ('Parker (2022) küresel', G['ParkerEtAl2020SInter']()), ('Kuehn (2023) küresel', G['KuehnEtAl2020SInter']())]
Rr = np.array([30.0, 60.0, 90.0, 120.0])
for ad, g in GM:
    out['uzaklik'][ad] = {}
    for M in (6.0, 7.8):
        ctx = RuptureContext(); ctx.mag = M; ctx.rake = 90.0; ctx.dip = 20.0; ctx.ztor = 35.0; ctx.hypo_depth = 35.5; ctx.width = 50.0
        ctx.rrup = Rr; ctx.rjb = Rr; ctx.rx = Rr; ctx.ry0 = Rr * 0; ctx.vs30 = np.full(4, 760.0); ctx.vs30measured = np.full(4, True); ctx.backarc = np.full(4, False); ctx.z1pt0 = np.full(4, 100.0); ctx.z2pt5 = np.full(4, 1.0)
        ctx.sids = np.arange(4)
        from openquake.hazardlib.contexts import ContextMaker
        cm = ContextMaker('Subduction Interface', [g], dict(imtls={'PGA': [0.1]}, truncation_level=99.0, maximum_distance=1000, investigation_time=1.0))
        rec = cm.recarray([ctx]); mea, sg, _, _ = cm.get_mean_stds([rec]); med = np.exp(mea[0, 0])
        out['uzaklik'][ad][f'M{M}'] = {'rrup_km': Rr.tolist(), 'medyan_g': med.tolist(), 'oran_30_120': float(med[0] / med[-1]), 'oran_60_90': float(med[1] / med[2])}
json.dump(out, open(os.path.join(H, 'b3_vs30_tani.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for ad, d in out['uzaklik'].items(): print(ad, {k: (round(v['oran_30_120'], 2), round(v['oran_60_90'], 2), [round(q, 3) for q in v['medyan_g']]) for k, v in d.items()})
for r in out['vs30']: print(r['kaynak'], r['geometri'].ljust(8), r['model'][:14].ljust(14), f"%10/50: +{r['pga10_fark_g']:.3f} g ({r['pga10_fark_%']:+.0f}%)  %2/50: +{r['pga02_fark_g']:.3f} g ({r['pga02_fark_%']:+.0f}%)")
