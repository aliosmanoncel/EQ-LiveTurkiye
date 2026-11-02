"""Mindanao PSHA: mevcut NumPy/SciPy kodu ile OpenQuake hazardlib (3.26.2) hesap çekirdeğinin AYNI GİRDİLERLE karşılaştırılması.

Amaç (kullanıcı tanımı, 2026-11-02): iki hesap motorunun aynı model altında sayısal olarak ne ölçüde uyuştuğunu sınamak. Uyuşma, kaynak modelinin
ya da GMPE'nin bilimsel doğruluğunu KANITLAMAZ (RAPOR §5).

(A) Motor karşılaştırması — eşit model:
    GMPE  : kod_gmpe.MindanaoKodGMPE (mevcut koddaki bağıntının birebir kopyası; OpenQuake'in yerleşik modeli değil)
    Kaynak: nokta kaynak, PointMSR (nokta kırık → rrup = hiposantral uzaklık); kaynak 1 episantral 46 km, derinlik 35,5 km (R = 58,1 km);
            kaynak 2 episantral 120 km, derinlik 25 km (R = 122,6 km); FTLS kaynağı kaynak 1 geometrisinde.
    MFD   : EvenlyDiscretizedMFD — sınıf merkezleri ve oranları mevcut kodun gr_occur / hazard_one fonksiyonundakiyle AYNI (koddan hesaplanır)
    Zemin : Vs30 = 360 m/s (kodun zemin terimi GMPE içinde)
    σ     : kesilmemiş (truncation_level = 99; kod scipy.stats.norm ile kesilmemiş normal kullanıyor)
    Süre  : Poisson, 1 yıl; λ = −ln(1 − PoE)
    Sınanan eğriler: c1_med, c1_1sig (eps = 1), c1_2sig (eps = 2), c2_med, c_ftls, c_comb ve mantık ağacının 27 dalı, ağırlıklı ortalaması,
    5/16/50/84/95. yüzdelikleri.
(B) Model duyarlılığı — EŞDEĞER DEĞİL: aynı kaynaklar, OpenQuake'in yerleşik YoungsEtAl1997SInter modeli (Vs30 = 360 < 760 → OpenQuake zemin katsayıları; 2026-11-02 düzeltmesi).
    Youngs (1997) ile koddaki bağıntı farklı modellerdir; (B) yalnız GMPE seçiminin sonuca etkisini gösterir.
Kullanım: /home/claude/oqenv/bin/python oq_karsilastirma.py   (önce referans_kod.py)
"""
import os, json, math, itertools, numpy as np
import openquake.engine
from openquake.hazardlib.calc.hazard_curve import calc_hazard_curves
from openquake.hazardlib.source import PointSource
from openquake.hazardlib.mfd import EvenlyDiscretizedMFD
from openquake.hazardlib.scalerel import PointMSR
from openquake.hazardlib.tom import PoissonTOM
from openquake.hazardlib.geo import Point, NodalPlane
from openquake.hazardlib.pmf import PMF
from openquake.hazardlib.site import Site, SiteCollection
from openquake.hazardlib.const import TRT
from openquake.hazardlib.gsim.youngs_1997 import YoungsEtAl1997SInter
from kod_gmpe import MindanaoKodGMPE

HERE = os.path.dirname(os.path.abspath(__file__))
REF = np.load(os.path.join(HERE, 'referans_kod.npz'))
x_im = REF['psha_x_im']; assert np.array_equal(x_im, REF['lt_x_im'])
KM_DEG = 6371.0 * math.pi / 180.0     # OpenQuake küresel Dünya yarıçapı (geo.geodetic EARTH_RADIUS)
LOC1, H1, H2 = Point(0.0, 0.0), 35.5, 25.0
R_kod = {'s1': math.sqrt(46 ** 2 + 35.5 ** 2), 's2': math.sqrt(120 ** 2 + 25 ** 2)}   # mevcut koddaki R (km)
# Geometri eşitlemesi: OpenQuake'in kırık yüzeyinden hesapladığı rrup, koddaki R'ye eşit olacak biçimde site ve kaynak 2 yerleştirilir
# (ilk denemede episantral 46 km verildiğinde OpenQuake rrup = 58,0008 km verdi; fark 0,1 km — ikiye bölme ile giderilir).
def _rrup1(src_loc, h, site_pt):
    from openquake.hazardlib.geo.surface.planar import PlanarSurface
    s = nokta_tmp(src_loc, h); r = next(iter(s.iter_ruptures()))
    from openquake.hazardlib.geo.mesh import Mesh
    return float(r.surface.get_min_distance(Mesh(np.array([site_pt.longitude]), np.array([site_pt.latitude])))[0])
def nokta_tmp(loc, h):
    return PointSource('t', 't', 'Subduction Interface', EvenlyDiscretizedMFD(6.0, 0.2, [1.0]), 1.0, PointMSR(), 1.0, PoissonTOM(1.0), 0.0, 200.0, loc,
                       PMF([(1.0, NodalPlane(0.0, 90.0, 90.0))]), PMF([(1.0, h)]))
def _coz(f, hedef, lo, hi):
    for _ in range(80):
        m = (lo + hi) / 2; (lo, hi) = (m, hi) if f(m) < hedef else (lo, m)
    return (lo + hi) / 2
lon_s = _coz(lambda x: _rrup1(LOC1, H1, Point(x, 0.0)), R_kod['s1'], 0.3, 0.5)
SITE = Point(lon_s, 0.0)
lat2 = _coz(lambda y: _rrup1(Point(lon_s, y), H2, SITE), R_kod['s2'], 1.0, 1.2)
LOC2 = Point(lon_s, lat2)
sites = SiteCollection([Site(SITE, vs30=360.0, vs30measured=True, z1pt0=100.0, z2pt5=1.0)])

# ── mevcut kodun MFD'si (gr_occur ve hazard_one ile aynı aritmetik) ──
def kod_mfd(b, lam5, Mmin, Mmax, dM=0.2, M_bins=None):
    if M_bins is None: M_bins = np.arange(Mmin + dM / 2, Mmax, dM)
    M_edges = M_bins - dM / 2
    A = 10 ** (-b * (M_edges - Mmin)); B = 10 ** (-b * (Mmax - Mmin))
    lam_e = lam5 * (A - B) / (1.0 - B); lam_e = np.where(M_bins <= Mmax, lam_e, 0.0)
    return M_bins, np.maximum(-np.diff(np.append(lam_e, 0.0)), 0.0)

TRT_S = 'Subduction Interface'   # TRT.SUBDUCTION_INTERFACE değeri (dizgi; birden çok kaynakta sıralanabilir olsun)
SPAN = float(os.environ.get('OQ_SPAN', '50.0'))   # Poisson zaman aralığı (yıl); λ = −ln(1 − PoE)/SPAN
def nokta(sid, loc, h, M_bins, rates):
    mfd = EvenlyDiscretizedMFD(round(float(M_bins[0]), 6), 0.2, [float(r) for r in rates])
    return PointSource(sid, sid, TRT_S, mfd, 1.0, PointMSR(), 1.0, PoissonTOM(SPAN), 0.0, 200.0, loc,
                       PMF([(1.0, NodalPlane(0.0, 90.0, 90.0))]), PMF([(1.0, h)]))

def lam_oq(srcs, gsim):
    poe = calc_hazard_curves(srcs, sites, {'PGA': list(x_im)}, {TRT_S: gsim}, truncation_level=99.0)['PGA'][0]
    return -np.log1p(-np.asarray(poe, dtype=float)) / SPAN

M_ps = REF['psha_M_bins']
S1 = dict(b=0.90, lam5=3.0, Mmin=5.0, Mmax=8.5); S2 = dict(b=0.90, lam5=1.0, Mmin=5.0, Mmax=7.5)
SF = dict(b=0.635, lam5=500 * 10 ** (-0.635 * (5 - 3.5)) * (365 / 90), Mmin=5.0, Mmax=7.8)
src = {k: nokta(k, l, h, *kod_mfd(p['b'], p['lam5'], p['Mmin'], p['Mmax'], M_bins=M_ps)) for k, l, h, p in [('s1', LOC1, H1, S1), ('s2', LOC2, H2, S2), ('ftls', LOC1, H1, SF)]}

# rrup denetimi: OpenQuake'in hesapladığı uzaklık = kodun R'si mi?
def rrup(s):   # her kırığın yüzeyinden siteye en kısa uzaklık (rrup); nokta kırıkta tek değer beklenir
    d = np.array([float(r.surface.get_min_distance(sites.mesh)[0]) for r in s.iter_ruptures()])
    return {'min': round(float(d.min()), 4), 'maks': round(float(d.max()), 4)}
R_oq = {'s1': rrup(src['s1']), 's2': rrup(src['s2'])}

# ── (A) eğriler ──
A = {'c1_med': lam_oq([src['s1']], MindanaoKodGMPE()), 'c1_1sig': lam_oq([src['s1']], MindanaoKodGMPE(eps=1.0)), 'c1_2sig': lam_oq([src['s1']], MindanaoKodGMPE(eps=2.0)),
     'c2_med': lam_oq([src['s2']], MindanaoKodGMPE()), 'c_ftls': lam_oq([src['ftls']], MindanaoKodGMPE())}
A['c_comb'] = lam_oq([src['s1'], src['s2']], MindanaoKodGMPE())
# mantık ağacı: 27 dal (mindanao_logic_tree.py ile aynı dallar ve ağırlıklar)
B1 = [(0.635, 0.60), (0.900, 0.30), (1.120, 0.10)]; B2 = [(0, 0.0, 0.70), (0, 0.5, 0.20), (1, 0.0, 0.10)]; B3 = [(7.8, 0.50), (8.0, 0.30), (8.2, 0.20)]
LT, W = [], []
for (b, w1), (zt, eps, w2), (mx, w3) in itertools.product(B1, B2, B3):
    s = nokta('lt', LOC1, H1, *kod_mfd(b, 3.0, 5.0, mx)); LT.append(lam_oq([s], MindanaoKodGMPE(Zt=zt, eps=eps))); W.append(w1 * w2 * w3)
LT, W = np.array(LT), np.array(W); lam_mean = W @ LT
def fraktil(curves, w, fr):   # mevcut koddaki ağırlıklı yüzdelik yöntemiyle aynı (sıralama + kümülatif ağırlık + doğrusal ara değer)
    out = np.zeros(curves.shape[1])
    for j in range(curves.shape[1]):
        i = np.argsort(curves[:, j]); out[j] = np.interp(fr, np.cumsum(w[i]), curves[i, j])
    return out
FR = [0.05, 0.16, 0.50, 0.84, 0.95]; fr_oq = np.array([fraktil(LT, W, f) for f in FR])
# ── (B) Youngs (1997) — eşdeğer değil ──
Bsens = {'c1_med_Y97': lam_oq([src['s1']], YoungsEtAl1997SInter()), 'c_comb_Y97': lam_oq([src['s1'], src['s2']], YoungsEtAl1997SInter())}
LT97 = np.array([lam_oq([nokta('lt', LOC1, H1, *kod_mfd(b, 3.0, 5.0, mx))], YoungsEtAl1997SInter()) for (b, w1), (zt, eps, w2), (mx, w3) in itertools.product(B1, B2, B3) if (zt, eps) == (0, 0.0)])
W97 = np.array([w1 * w3 for (b, w1), (mx, w3) in itertools.product(B1, B3)]); W97 = W97 / W97.sum()

# ── karşılaştırma ölçütleri ──
def pga_at(lam_t, lam_c):   # mevcut koddaki loglog_interp ile aynı
    v = lam_c > 1e-12
    if lam_t < lam_c[v][-1] or lam_t > lam_c[v][0]: return float('nan')
    return float(np.exp(np.interp(np.log(lam_t), np.log(lam_c[v][::-1]), np.log(x_im[v][::-1]))))
L10, L02, L50 = -math.log(0.90) / 50, -math.log(0.98) / 50, -math.log(0.50) / 50
LMIN, LMAX = -math.log1p(-1e-5) / 50, -math.log(1 - 0.999) / 50   # 50 yıllık PoE 1e-5 … 0,999 (32 bit hassasiyetin güvenilir aralığı)
def fark(a, b, lam_min=LMIN, lam_max=LMAX):
    m = (b >= lam_min) & (b <= lam_max) & np.isfinite(a); r = np.abs(a[m] / b[m] - 1)
    if not m.any(): return {'nokta': 0}
    return {'maks_goreli_fark': float(r.max()), 'ort_goreli_fark': float(r.mean()), 'nokta': int(m.sum()), 'lam_araligi': [lam_min, lam_max]}
sonuc = {'surum': {'openquake.engine': openquake.engine.__version__, 'numpy': np.__version__},
         'uzaklik': {'kod_R_km': R_kod, 'oq_rrup_km': R_oq, 'site_lon': lon_s, 'kaynak2_lat': lat2}, 'zaman_araligi_yil': SPAN, 'A_egriler': {}, 'A_mantik_agaci': {}, 'B_youngs1997': {}}
for k in ('c1_med', 'c1_1sig', 'c1_2sig', 'c2_med', 'c_ftls', 'c_comb'):
    ref = REF['psha_' + k]; sonuc['A_egriler'][k] = {**fark(A[k], ref), 'pga10_kod': pga_at(L10, ref), 'pga10_oq': pga_at(L10, A[k]), 'pga02_kod': pga_at(L02, ref), 'pga02_oq': pga_at(L02, A[k])}
dal = [fark(LT[i], REF['lt_branch_curves'][i])['maks_goreli_fark'] for i in range(27)]
sonuc['A_mantik_agaci'] = {'agirlik_esit': bool(np.allclose(W, REF['lt_branch_weights'])), 'dal_maks_goreli_fark': max(dal), 'ortalama': fark(lam_mean, REF['lt_lam_mean']),
  'tablo': {s: {'kod': {**{f'{int(100*f)}.': pga_at(lt, REF['lt_frac_curves'][i]) for i, f in enumerate(FR)}, 'ort': pga_at(lt, REF['lt_lam_mean'])},
                'oq': {**{f'{int(100*f)}.': pga_at(lt, fr_oq[i]) for i, f in enumerate(FR)}, 'ort': pga_at(lt, lam_mean)}} for s, lt in (('%50/50', L50), ('%10/50', L10), ('%2/50', L02))}}
sonuc['B_youngs1997'] = {'not': 'EŞDEĞER DEĞİL: OpenQuake YoungsEtAl1997SInter (Vs30 = 360 < 760 → zemin katsayıları; ilk sürümde yanlışlıkla 'kaya' yazılmıştı); epistemik dallar (eps, Zt=1) yok; yalnız b ve Mmax dalları',
  'c1_med': {'pga10_kod_bagintisi': sonuc['A_egriler']['c1_med']['pga10_kod'], 'pga10_Y97': pga_at(L10, Bsens['c1_med_Y97']), 'pga02_Y97': pga_at(L02, Bsens['c1_med_Y97'])},
  'mantik_agaci_bMmax_ort': {'pga10_Y97': pga_at(L10, W97 @ LT97), 'pga02_Y97': pga_at(L02, W97 @ LT97)}}
np.savez(os.path.join(HERE, 'oq_egriler.npz'), x_im=x_im, lt_oq=LT, lt_w=W, lam_mean_oq=lam_mean, fr_oq=fr_oq, lt97=LT97, w97=W97, **{f'A_{k}': v for k, v in A.items()}, **{f'B_{k}': v for k, v in Bsens.items()})
json.dump(sonuc, open(os.path.join(HERE, 'karsilastirma_sonuc.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps(sonuc, indent=1, ensure_ascii=False))
