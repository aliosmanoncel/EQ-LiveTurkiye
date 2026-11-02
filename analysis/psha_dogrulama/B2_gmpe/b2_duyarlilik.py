"""Aşama B2: modern GMPE duyarlılığı — model değerlendirmesi, DOĞRULAMA DEĞİL. Hiçbir sonuç doğrulanmış tehlike değeri değildir.
Kaynak modeli Aşama A ile AYNI (nokta kaynak, eşitlenmiş geometri, aynı MFD; Cotabato + Davao, medyan dal); yalnız GMPE ve site Vs30 değişir.
Bu nedenle sonuçlar nokta kaynak varsayımını taşır (B3'te geometriyle tekrarlanacak).
Modeller (OpenQuake 3.26.2): koddaki bağıntı (MindanaoKodGMPE; Vs30 < 760'ta 0,35 ln(760/Vs30) terimi), YoungsEtAl1997SInter (Vs30 < 760 → zemin,
≥ 760 → kaya katsayıları), AbrahamsonEtAl2015SInter (BC Hydro; backarc = False), ParkerEtAl2020SInter (küresel), KuehnEtAl2020SInter (küresel
'GLO'; OpenQuake'te deneysel işaretli). Her model Vs30 = 360 ve 760 m/s için: GMPE etkisi ve zemin etkisi ayrılır.
σ kesilmemiş (truncation_level = 99; Aşama A ile karşılaştırılabilirlik için — modern uygulamada sıkça 3σ kesilir; ayrıca 3σ ile de raporlanır).
Kullanım: /home/claude/oqenv/bin/python b2_duyarlilik.py"""
import os, sys, json, math, warnings, numpy as np
warnings.filterwarnings('ignore')
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H); sys.path.insert(0, P)
from openquake.hazardlib.calc.hazard_curve import calc_hazard_curves
from openquake.hazardlib.source import PointSource
from openquake.hazardlib.mfd import EvenlyDiscretizedMFD
from openquake.hazardlib.scalerel import PointMSR
from openquake.hazardlib.tom import PoissonTOM
from openquake.hazardlib.geo import Point, NodalPlane
from openquake.hazardlib.pmf import PMF
from openquake.hazardlib.site import Site, SiteCollection
from openquake.hazardlib.gsim import get_available_gsims
from openquake.hazardlib.contexts import simple_cmaker
from openquake.hazardlib.imt import PGA
from kod_gmpe import MindanaoKodGMPE
G = get_available_gsims(); S = json.load(open(os.path.join(P, 'karsilastirma_sonuc.json'), encoding='utf-8')); O = json.load(open(os.path.join(P, 'A_job', 'oranlar.json')))
REF = np.load(os.path.join(P, 'referans_kod.npz')); x = REF['psha_x_im']; T = 50.0; TRT = 'Subduction Interface'
lon_s, lat2 = S['uzaklik']['site_lon'], S['uzaklik']['kaynak2_lat']
def src(sid, lon, lat, h, key):
    d = O[key]; return PointSource(sid, sid, TRT, EvenlyDiscretizedMFD(d['M'][0], 0.2, d['oran']), 1.0, PointMSR(), 1.0, PoissonTOM(T), 0.0, 200.0, Point(lon, lat),
                                   PMF([(1.0, NodalPlane(0.0, 90.0, 90.0))]), PMF([(1.0, h)]))
SRC = [src('s1', 0.0, 0.0, 35.5, 'c_comb/s1'), src('s2', lon_s, lat2, 25.0, 'c_comb/s2')]
def sites(vs30): return SiteCollection([Site(Point(lon_s, 0.0), vs30=vs30, vs30measured=True, z1pt0=100.0, z2pt5=1.0, backarc=False)])
def lam(gsim, vs30, tl=99.0):
    poe = calc_hazard_curves(SRC, sites(vs30), {'PGA': list(x)}, {TRT: gsim}, truncation_level=tl)['PGA'][0]
    return -np.log1p(-np.minimum(np.asarray(poe, float), 1 - 1e-16)) / T
def pga(lt, c):
    v = c > 1e-12
    if lt < c[v][-1] or lt > c[v][0]: return float('nan')
    return float(np.exp(np.interp(np.log(lt), np.log(c[v][::-1]), np.log(x[v][::-1]))))
L10, L02 = -math.log(0.9) / T, -math.log(0.98) / T
MODELLER = [('Kod bağıntısı ("Youngs 1988" etiketli)', MindanaoKodGMPE()), ('Youngs vd. (1997)', G['YoungsEtAl1997SInter']()), ('BC Hydro (Abrahamson vd. 2016)', G['AbrahamsonEtAl2015SInter']()),
            ('Parker vd. (2022), küresel', G['ParkerEtAl2020SInter']()), ('Kuehn vd. (2023), küresel', G['KuehnEtAl2020SInter']())]
# medyan yer hareketi: M 7,8, rrup = 58,1 km (kaynak 1 geometrisi) — modellerin ölçeklenmesini ayrıca göstermek için
def medyan(gsim, vs30, M=7.8):
    s = PointSource('m', 'm', TRT, EvenlyDiscretizedMFD(M, 0.1, [1.0]), 1.0, PointMSR(), 1.0, PoissonTOM(T), 0.0, 200.0, Point(0.0, 0.0), PMF([(1.0, NodalPlane(0.0, 90.0, 90.0))]), PMF([(1.0, 35.5)]))
    from openquake.hazardlib.calc.filters import IntegrationDistance
    cm = simple_cmaker([gsim], ['PGA'], truncation_level=99.0, maximum_distance=IntegrationDistance.new('1000'))
    ctx = cm.from_srcs([s], sites(vs30)); mea, sig, _, _ = cm.get_mean_stds(ctx)
    return float(np.exp(mea[0, 0, 0])), float(sig[0, 0, 0])
R = {'not': 'MODEL DUYARLILIĞI — doğrulanmış tehlike değeri değildir; nokta kaynak varsayımı korunmuştur (B3).', 'kaynak': 'Aşama A ile aynı (c_comb: Cotabato + Davao, medyan dal)', 'sonuc': []}
EGR = {}
for ad, g in MODELLER:
    for vs in (360.0, 760.0):
        c = lam(g, vs); c3 = lam(g, vs, 3.0); mu, sg = medyan(g, vs); EGR[f'{ad}|{int(vs)}'] = c
        R['sonuc'].append({'model': ad, 'gsim': type(g).__name__, 'Vs30': vs, 'pga10': pga(L10, c), 'pga02': pga(L02, c), 'pga10_3sigma': pga(L10, c3), 'pga02_3sigma': pga(L02, c3), 'medyan_M7.8_R58': mu, 'sigma_ln_M7.8': sg})
        print(f"{ad:42s} Vs30 {int(vs):3d}: %10/50 {pga(L10, c):.3f} g  %2/50 {pga(L02, c):.3f} g  (3σ: {pga(L10, c3):.3f} / {pga(L02, c3):.3f})  medyan(M7,8; 58 km) {mu:.3f} g, σ {sg:.3f}")
# Aşama A ile sağlama: kod bağıntısı, Vs30 360 = Aşama A c_comb
ka = [r for r in R['sonuc'] if r['gsim'] == 'MindanaoKodGMPE' and r['Vs30'] == 360.0][0]; R['sagla_asamaA'] = {'pga10_B2': ka['pga10'], 'pga10_kod': pga(L10, REF['psha_c_comb'])}
print('sağlama (Aşama A, c_comb %10/50):', ka['pga10'], pga(L10, REF['psha_c_comb']))
R['uygulanabilirlik'] = [
 {'model': 'Kod bağıntısı', 'veri': 'Youngs vd. (1988) olarak etiketli; birincil kaynakla doğrulanmadı (B1)', 'filipinler': 'bilinmiyor', 'zemin': 'kodda eklenmiş 0,35 ln(760/Vs30) — yayından doğrulanmadı'},
 {'model': 'Youngs vd. (1997)', 'veri': 'Alaska, Şili, Cascadia, Japonya, Meksika, Peru, Solomon Adaları; 1940–1992; 5,0 < M < 8,2; 8,5–550 km; 19 deprem, 271 kayıt (IISEE)', 'filipinler': 'veri setinde yok', 'zemin': 'kaya / zemin iki sınıf (OpenQuake: Vs30 ≥ 760 kaya)'},
 {'model': 'BC Hydro (Abrahamson vd. 2016)', 'veri': 'küresel subdüksiyon verisi; 2018 güncellemesi altı bölge: Cascadia, Orta Amerika, Japonya, Yeni Zelanda, Güney Amerika, Tayvan (PEER 2018/02)', 'filipinler': 'bölgesel terim yok (incelenen kaynaklarda)', 'zemin': 'Vs30 sürekli, doğrusal olmayan'},
 {'model': 'Parker vd. (2022)', 'veri': 'NGA-Sub; bölgesel ayarlar: Japonya, Tayvan, Meksika, Orta Amerika, Güney Amerika, Alaska, Aleut, Cascadia; arayüz M 5–9,1, 15–1000 km', 'filipinler': 'bölgesel ayar yok — küresel sürüm kullanıldı', 'zemin': 'Vs30 sürekli'},
 {'model': 'Kuehn vd. (2023)', 'veri': 'NGA-Sub; yedi bölge: Alaska, Orta Amerika–Meksika, Cascadia, Japonya, Yeni Zelanda, Güney Amerika, Tayvan (PEER 2020/04)', 'filipinler': 'bölge yok — küresel (GLO) sürüm; OpenQuake\'te deneysel', 'zemin': 'Vs30 sürekli'}]
json.dump(R, open(os.path.join(H, 'b2_sonuc.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
np.savez(os.path.join(H, 'b2_egriler.npz'), x=x, **{k.replace(' ', '_'): v for k, v in EGR.items()})
