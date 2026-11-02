"""Aşama B3: kaynak geometrisi duyarlılığı — model değerlendirmesi, DOĞRULAMA DEĞİL. Hiçbir sonuç doğrulanmış tehlike değeri değildir.
Bilimsel soru: General Santos için tehlike düzeyleri, kaynak geometrisinin nokta kaynaktan sonlu fay ya da alan kaynağına dönüştürülmesine ne ölçüde duyarlı?
SABİT (B2 ile aynı): beş GMPE, Vs30 360/760 m/s, MFD sınıf oranları (A_job/oranlar.json; kodun aritmetiği), Mmax, oranlar, Poisson, σ kesilmemiş
(+ 3σ ayrıca). DEĞİŞEN yalnız geometri.
Geometriler (konum: raporun olay kaydı — W-faz santroidi 5,68°K 125,06°D, 35,5 km; NP 359°/47°/103° ve 161°/45°/77°; site General Santos 6,1164°K 125,1716°D):
  Cotabato  P0: B2 nokta kaynağı (göreli geometri, rrup = 58,11 km) — yüzde değişimin TABANI
            P1: aynı nokta kaynak, gerçek koordinatta (santroid; site uzaklığı gerçek)
            F : sonlu fay düzlemi, doğrultu 359°, doğuya eğim 47° (NP2; doğuya dalan Cotabato arayüzüyle uyumlu), santroidden geçer;
                derinlik 10–60 km, doğrultu boyunca 300 km (santroid ortada); Strasser vd. (2010) arayüz MSR, en-boy oranı 2; kırıklar düzlemde
                kayar (uzaklık dağılımı + büyüklüğe bağlı kırık boyutu). M ≥ ~8,3 kırıkları fay boyutunu aşar → OpenQuake tüm düzlemi kullanır.
            F2: duyarlılık — aynı düzlem eğim 30° (arayüz için daha tipik; doğrultu ve santroid aynı)
  Davao     (kodda konum/mekanizma tanımsız; R = √(120² + 25²) yalnız uzaklık): P0 nokta (120 km, 25 km); FD⊥: düşey doğrultu atımlı fay, merkezi
            120 km'de, görüş hattına DİK, 100 km; FD∥: aynı fay görüş hattına PARALEL; A: alan kaynağı, merkez 120 km, yarıçap 40 km (dairesel çokgen),
            odak 25 km. Davao için WC1994 MSR. Sonuçlar AYRI raporlanır, birleştirilmez.
GMPE'ler B2 ile aynı (hepsi subdüksiyon arayüzü modeli; Davao'ya arayüz GMPE'si uygulanması koddan devralındı — B4/bilimsel değerlendirme).
Ayrıca: kod bağıntısıyla 27 dallı mantık ağacı P0 ve F geometrisinde (Vs30 360) — ortalama λ ve PoE uzayında birlikte.
Kullanım: /home/claude/oqenv/bin/python b3_geometri.py   (OQ_DISTRIBUTE=no)"""
import os, sys, json, math, itertools, warnings, numpy as np
warnings.filterwarnings('ignore')
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H); sys.path.insert(0, P)
from openquake.hazardlib.calc.hazard_curve import calc_hazard_curves
from openquake.hazardlib.source import PointSource, SimpleFaultSource, AreaSource
from openquake.hazardlib.mfd import EvenlyDiscretizedMFD
from openquake.hazardlib.scalerel import PointMSR, WC1994
from openquake.hazardlib.scalerel.strasser2010 import StrasserInterface
from openquake.hazardlib.tom import PoissonTOM
from openquake.hazardlib.geo import Point, NodalPlane, Line, Polygon
from openquake.hazardlib.geo.geodetic import point_at, geodetic_distance, azimuth
from openquake.hazardlib.pmf import PMF
from openquake.hazardlib.site import Site, SiteCollection
from openquake.hazardlib.gsim import get_available_gsims
from openquake.hazardlib.stats import quantile_curve
from kod_gmpe import MindanaoKodGMPE
G = get_available_gsims(); O = json.load(open(os.path.join(P, 'A_job', 'oranlar.json'))); S = json.load(open(os.path.join(P, 'karsilastirma_sonuc.json'), encoding='utf-8'))
REF = np.load(os.path.join(P, 'referans_kod.npz')); x = REF['psha_x_im']; T = 50.0; TRT = 'Subduction Interface'
SITE_GS = (125.1716, 6.1164); CEN = (125.06, 5.68, 35.5)
def mfd(key): d = O[key]; return EvenlyDiscretizedMFD(d['M'][0], 0.2, d['oran'])
def mfd_lt(b, mx):
    d = [v for k, v in O.items() if k.startswith('lt/') and v['b'] == b and v['Mmax'] == mx][0]; return EvenlyDiscretizedMFD(d['M'][0], 0.2, d['oran'])
tom = PoissonTOM(T)
def nokta(sid, lon, lat, h, m): return PointSource(sid, sid, TRT, m, 1.0, PointMSR(), 1.0, tom, 0.0, 200.0, Point(lon, lat), PMF([(1.0, NodalPlane(0.0, 90.0, 90.0))]), PMF([(1.0, h)]))
# ── Cotabato fayı: santroidden geçen düzlem; yüzey izi santroidin yüzey izdüşümünden eğim tersine (up-dip, azimut 359 + 270 = 269°) h/tan(dip)
def cot_fay(sid, m, dip, L=300.0, z0=10.0, z1=60.0, strike=359.0):
    lon_t, lat_t = point_at(CEN[0], CEN[1], (strike + 270) % 360, CEN[2] / math.tan(math.radians(dip)))
    a = point_at(lon_t, lat_t, (strike + 180) % 360, L / 2); b = point_at(lon_t, lat_t, strike, L / 2)
    return SimpleFaultSource(sid, sid, TRT, m, 2.0, StrasserInterface(), 2.0, tom, z0, z1, Line([Point(*a), Point(*b)]), dip, 103.0)
# ── B2 göreli geometri (P0) ve Davao alternatifleri — site B2 sitesi (0,41488°D, 0°) etrafında
lon_s, lat2 = S['uzaklik']['site_lon'], S['uzaklik']['kaynak2_lat']
def davao(kind, m):
    c = Point(lon_s, lat2)   # site'ın 120 km kuzeyi (B2/A ile aynı merkez)
    if kind == 'P0': return nokta('d', lon_s, lat2, 25.0, m)
    if kind in ('FDdik', 'FDpar'):
        st = 90.0 if kind == 'FDdik' else 0.0   # görüş hattı kuzey-güney → dik = doğu-batı doğrultu
        a = point_at(c.longitude, c.latitude, st + 180, 50.0); b = point_at(c.longitude, c.latitude, st, 50.0)
        return SimpleFaultSource('d', 'd', TRT, m, 2.0, WC1994(), 1.5, tom, 0.0, 25.0, Line([Point(*a), Point(*b)]), 90.0, 0.0)
    if kind == 'A':
        pts = [Point(*point_at(c.longitude, c.latitude, az, 40.0)) for az in range(0, 360, 10)]
        return AreaSource('d', 'd', TRT, m, 2.0, WC1994(), 1.5, tom, 0.0, 50.0, PMF([(1.0, NodalPlane(0.0, 90.0, 0.0))]), PMF([(1.0, 25.0)]), Polygon(pts), 5.0)
def sites(lon, lat, vs): return SiteCollection([Site(Point(lon, lat), vs30=vs, vs30measured=True, z1pt0=100.0, z2pt5=1.0, backarc=False)])
def lam(srcs, site, gsim, tl=99.0):
    poe = calc_hazard_curves(srcs, site, {'PGA': list(x)}, {TRT: gsim}, truncation_level=tl)['PGA'][0]
    return -np.log1p(-np.minimum(np.asarray(poe, float), 1 - 1e-16)) / T
def pga(lt, c):
    v = c > 1e-12
    if lt < c[v][-1] or lt > c[v][0]: return float('nan')
    return float(np.exp(np.interp(np.log(lt), np.log(c[v][::-1]), np.log(x[v][::-1]))))
L10, L02 = -math.log(0.9) / T, -math.log(0.98) / T
GM = [('Kod bağıntısı', MindanaoKodGMPE()), ('Youngs (1997)', G['YoungsEtAl1997SInter']()), ('BC Hydro (2016)', G['AbrahamsonEtAl2015SInter']()),
      ('Parker (2022) küresel', G['ParkerEtAl2020SInter']()), ('Kuehn (2023) küresel', G['KuehnEtAl2020SInter']())]
# geometri tanımları: (ad, kaynak listesi, site lon, site lat)
m1, m2 = 'c_comb/s1', 'c_comb/s2'
GEO = {'Cotabato': [('P0', lambda: [nokta('c', 0.0, 0.0, 35.5, mfd(m1))], lon_s, 0.0), ('P1', lambda: [nokta('c', *CEN, mfd(m1))], *SITE_GS),
                    ('F', lambda: [cot_fay('c', mfd(m1), 47.0)], *SITE_GS), ('F2_dip30', lambda: [cot_fay('c', mfd(m1), 30.0)], *SITE_GS)],
       'Davao': [(k, (lambda k=k: [davao(k, mfd(m2))]), lon_s, 0.0) for k in ('P0', 'FDdik', 'FDpar', 'A')]}
R = {'not': 'MODEL DUYARLILIĞI — doğrulanmış tehlike değeri değildir.', 'geometri': {}, 'sonuc': [], 'mantik_agaci': {}}
# geometri tanılama: Cotabato fayının siteye en yakın uzaklığı, P1 rrup
fz = cot_fay('c', mfd(m1), 47.0); rups = list(fz.iter_ruptures()); ms = sites(*SITE_GS, 360.0).mesh
rr = np.array([float(r.surface.get_min_distance(ms)[0]) for r in rups]); mags = np.array([r.mag for r in rups]); rates = np.array([r.occurrence_rate for r in rups])
R['geometri'] = {'P0_rrup_km': 58.1055, 'P1_rrup_km': float(next(iter(nokta('c', *CEN, mfd(m1)).iter_ruptures())).surface.get_min_distance(ms)[0]),
  'F_kirik_sayisi': len(rups), 'F_rrup_min_km': float(rr.min()), 'F_rrup_oran_agirlikli_ort_km': float((rr * rates).sum() / rates.sum()), 'F_rrup_oran_agirlikli_medyan_km': float(np.interp(0.5, np.cumsum(rates[np.argsort(rr)]) / rates.sum(), np.sort(rr))),
  'F_toplam_oran_esit': float(abs(rates.sum() / sum(O[m1]['oran']) - 1)), 'site_episantral_km': float(geodetic_distance(*SITE_GS, CEN[0], CEN[1]))}
print('geometri:', json.dumps(R['geometri'], ensure_ascii=False))
for kay, lst in GEO.items():
    for gad, mk, slon, slat in lst:
        for ad, g in GM:
            for vs in (360.0, 760.0):
                srcs = mk(); c = lam(srcs, sites(slon, slat, vs), g); c3 = lam(mk(), sites(slon, slat, vs), g, 3.0)
                R['sonuc'].append({'kaynak': kay, 'geometri': gad, 'model': ad, 'Vs30': vs, 'pga10': pga(L10, c), 'pga02': pga(L02, c), 'pga10_3s': pga(L10, c3), 'pga02_3s': pga(L02, c3)})
                np.save(os.path.join(H, f'egri_{kay}_{gad}_{ad.split()[0]}_{int(vs)}.npy'), c)
            print(kay, gad, ad, [round(r['pga10'], 3) for r in R['sonuc'] if r['kaynak'] == kay and r['geometri'] == gad and r['model'] == ad])
# yüzde değişim (P0 tabanına göre)
for r in R['sonuc']:
    b = [q for q in R['sonuc'] if q['kaynak'] == r['kaynak'] and q['geometri'] == 'P0' and q['model'] == r['model'] and q['Vs30'] == r['Vs30']][0]
    for k in ('pga10', 'pga02', 'pga10_3s', 'pga02_3s'): r[k + '_degisim_%'] = 100 * (r[k] / b[k] - 1)
# mantık ağacı: kod bağıntısı, Vs30 360; P0 ve F; ortalama λ ve PoE uzayında
B1 = [(0.635, 0.60), (0.900, 0.30), (1.120, 0.10)]; B2g = [(0, 0.0, 0.70), (0, 0.5, 0.20), (1, 0.0, 0.10)]; B3 = [(7.8, 0.50), (8.0, 0.30), (8.2, 0.20)]
for gad, mk, slon, slat in (('P0', lambda m: [nokta('c', 0.0, 0.0, 35.5, m)], lon_s, 0.0), ('F', lambda m: [cot_fay('c', m, 47.0)], *SITE_GS)):
    C, W = [], []
    for (b, w1), (zt, eps, w2), (mx, w3) in itertools.product(B1, B2g, B3):
        C.append(lam(mk(mfd_lt(b, mx)), sites(slon, slat, 360.0), MindanaoKodGMPE(Zt=zt, eps=eps))); W.append(w1 * w2 * w3)
    C, W = np.array(C), np.array(W); Pp = -np.expm1(-C * T); toL = lambda p: -np.log1p(-np.minimum(p, 1 - 1e-16)) / T
    R['mantik_agaci'][gad] = {s: {'ort_lambda': pga(lt, W @ C), 'ort_poe': pga(lt, toL(W @ Pp)), **{f'q{q}_lambda': pga(lt, quantile_curve(q, C, W)) for q in (0.05, 0.16, 0.5, 0.84, 0.95)},
                                  **{f'q{q}_poe': pga(lt, toL(quantile_curve(q, Pp, W))) for q in (0.05, 0.16, 0.5, 0.84, 0.95)}} for s, lt in (('%10/50', L10), ('%2/50', L02))}
    print('mantık ağacı', gad, R['mantik_agaci'][gad]['%10/50']['ort_lambda'], R['mantik_agaci'][gad]['%10/50']['ort_poe'], R['mantik_agaci'][gad]['%10/50']['q0.5_lambda'])
R['sagla'] = {'P0_kod_360_pga10': [r for r in R['sonuc'] if r['kaynak'] == 'Cotabato' and r['geometri'] == 'P0' and r['model'] == 'Kod bağıntısı' and r['Vs30'] == 360.0][0]['pga10'],
              'A_c1_med_pga10': pga(L10, REF['psha_c1_med']), 'LT_P0_ort_lambda': R['mantik_agaci']['P0']['%10/50']['ort_lambda'], 'A_LT_ort_lambda': 0.928382}
json.dump(R, open(os.path.join(H, 'b3_sonuc.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False); print('sağlama', R['sagla'])
