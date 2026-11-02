"""Aşama 2, adım 1 (b, c): ortak test girdileriyle bütün modeller + bağımsız uygulama (pygmm) ile çapraz kontrol + Campbell (1981).

(b) Ortak girdi ızgarası (yöntem belgesi §11, revizyon 10: "aynı test girdileri bütün modellerde"):
    Mw 5,0 / 6,0 / 7,0 / 7,8; Rjb 1, 10, 30, 100, 200 km; Vs30 360 ve 760 m/s; doğrultu atımlı (rake 0, dip 90°);
    kırık üstü ztor = 0 → düşey düzlemde Rrup = Rjb, Rx = Rjb, Ry0 = 0; odak derinliği 10 km; z1.0 = CY14'ün
    Kaliforniya/küresel ortalaması (merkezlenmiş fark 0); ESHM20 soğrulma bölgesi 0 (varsayılan), Vs30 ölçülmüş.
    Bu girdiler bir YAZILIM test ızgarasıdır: gerçek bir deprem ya da Türkiye senaryosu değildir.
(c) Bağımsız uygulama: pygmm 0.8.0 (A. Kottke) — ASB14, BSSA14 (region='turkey' ↔ OpenQuake BooreEtAl2014HighQ),
    CY14 (region='california' ↔ OpenQuake varsayılanı). pygmm'de olmayan modeller (AC10, KAAH15, ESHM20, CY08, Zh06) için
    bağımsız referans, tablo_dogrulama.py'deki OpenQuake doğrulama tablolarıdır.
(d) Campbell (1981): mevcut EQ-Live katmanının denklemi (scripts/build_hazard_grid.py, main) OpenQuake'te özel sınıf olarak;
    katmandaki gibi R = dış merkez uzaklığı. Betikteki gmpe_pga() ile birebir karşılaştırılır.

Kullanım: <oqenv>/bin/python ortak_girdi.py <build_hazard_grid.py yolu>  → ortak_girdi.csv, ortak_girdi.json
"""
import csv, hashlib, importlib.util, json, os, sys, warnings
import numpy as np
from openquake.hazardlib import contexts, const
from openquake.hazardlib.gsim.base import GMPE, registry
from openquake.hazardlib.imt import PGA, PGV, SA, from_string
import openquake.engine
import pygmm

warnings.filterwarnings('ignore')
BURA = os.path.dirname(os.path.abspath(__file__))
MW = [5.0, 6.0, 7.0, 7.8]; RJB = [1.0, 10.0, 30.0, 100.0, 200.0]; VS30 = [360.0, 760.0]
IMS = ['PGA', 'PGV', 'SA(0.2)', 'SA(1.0)']; HYPO = 10.0


class Campbell1981EQLive(GMPE):
    """Campbell (1981) medyan PGA — EQ-Live 'Hazard' katmanındaki uygulamanın birebir kopyası (R = dış merkez uzaklığı,
    r_eff < 1 km ise 1 km). Yalnız karşılaştırma içindir; σ katmanda kullanılmadığı için 0 verilir."""
    DEFINED_FOR_TECTONIC_REGION_TYPE = const.TRT.ACTIVE_SHALLOW_CRUST
    DEFINED_FOR_INTENSITY_MEASURE_TYPES = {PGA}
    DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = const.IMC.GEOMETRIC_MEAN
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = {const.StdDev.TOTAL}
    REQUIRES_SITES_PARAMETERS = set(); REQUIRES_RUPTURE_PARAMETERS = {'mag'}; REQUIRES_DISTANCES = {'repi'}

    def compute(self, ctx: np.recarray, imts, mean, sig, tau, phi):
        r_eff = np.maximum(ctx.repi + 0.0606 * np.exp(0.700 * ctx.mag), 1.0)
        for m, _ in enumerate(imts):
            mean[m] = -4.141 + 0.868 * ctx.mag - 1.09 * np.log(r_eff); sig[m] = 0.0


def z1_cy14(vs30):   # CY14 Kaliforniya/küresel ortalama z1.0 [m] (Chiou & Youngs 2014; OpenQuake global_mean_z1pt0)
    from openquake.hazardlib.gsim.chiou_youngs_2014 import global_mean_z1pt0
    return float(np.exp(global_mean_z1pt0(np.array([vs30]))[0]))   # OpenQuake işlevi ln(z1) döndürür; exp ile metreye çevrilir


MODELLER = [('ASB14', 'AkkarEtAlRjb2014', 'Liste B'), ('AC10', 'AkkarCagnan2010', 'Liste B'), ('KAAH15', 'KaleEtAl2015Turkey', 'Liste B'),
            ('BSSA14 Yüksek Q', 'BooreEtAl2014HighQ', 'Liste B'), ('CY14', 'ChiouYoungs2014', 'Liste B'), ('ESHM20', 'KothaEtAl2020ESHM20', 'Liste B'),
            ('CY08', 'ChiouYoungs2008', 'Karşılaştırma'), ('Zh06', 'ZhaoEtAl2006Asc', 'Karşılaştırma'), ('Campbell 1981 (EQ-Live)', None, 'Karşılaştırma')]


def oq_hesap(gsim, mag, vs30):
    tanimli = {t.__name__ for t in gsim.DEFINED_FOR_INTENSITY_MEASURE_TYPES}
    imts = [im for im in IMS if from_string(im).name in tanimli]
    cm = contexts.ContextMaker('*', [gsim], {'imtls': {im: [0] for im in imts}, 'mags': ['%.2f' % mag]})
    n = len(RJB); ctx = contexts.RuptureContext()
    ctx.src_id = 0; ctx.rup_id = 0; ctx.occurrence_rate = 0
    ctx.mag = mag; ctx.rake = 0.0; ctx.dip = 90.0; ctx.ztor = 0.0; ctx.hypo_depth = HYPO
    ctx.width = min(15.0, 10 ** (-0.76 + 0.27 * mag))   # yalnız ASK gibi genişlik isteyen sınıflar için; burada kullanılan modellerde etkisiz
    r = np.array(RJB); ctx.rjb = r; ctx.rrup = r.copy(); ctx.rx = r.copy(); ctx.ry0 = np.zeros(n)
    ctx.repi = r.copy(); ctx.rhypo = np.sqrt(r ** 2 + HYPO ** 2)
    ctx.vs30 = np.full(n, vs30); ctx.vs30measured = np.ones(n, bool); ctx.z1pt0 = np.full(n, z1_cy14(vs30)); ctx.z2pt5 = np.full(n, 1.0)
    ctx.region = np.zeros(n, int); ctx.sids = np.arange(n)
    out = cm.get_mean_stds([ctx], split_by_mag=False)[:, 0]   # [mean, sig, tau, phi] × IM × n
    return {im: (np.exp(out[0, k]), out[1, k]) for k, im in enumerate(cm.imtls)}


def pygmm_hesap(kisa, mag, vs30):
    T = [0.2, 1.0]
    sc = dict(mag=mag, v_s30=vs30, mechanism='SS', dip=90, depth_tor=0.0, depth_hyp=HYPO)
    out = {}
    for rjb in RJB:
        if kisa == 'ASB14':
            g = pygmm.AkkarSandikkayaBommer2014(pygmm.Scenario(dist_jb=rjb, **sc))
        elif kisa == 'BSSA14 Yüksek Q':
            g = pygmm.BooreStewartSeyhanAtkinson2014(pygmm.Scenario(dist_jb=rjb, region='turkey', **sc))
        elif kisa == 'CY14':
            g = pygmm.ChiouYoungs2014(pygmm.Scenario(dist_jb=rjb, dist_rup=rjb, dist_x=rjb, region='california', **sc))
        else:
            return None
        sa = g.interp_spec_accels(T)
        out.setdefault('PGA', []).append((g.pga, g.ln_std_pga)); out.setdefault('PGV', []).append((g.pgv, g.ln_std_pgv))
        stds = g.interp_ln_stds(T)
        out.setdefault('SA(0.2)', []).append((sa[0], stds[0])); out.setdefault('SA(1.0)', []).append((sa[1], stds[1]))
    return {im: (np.array([v[0] for v in L]), np.array([v[1] for v in L])) for im, L in out.items()}


spec = importlib.util.spec_from_file_location('bhg', sys.argv[1]); bhg = importlib.util.module_from_spec(spec); spec.loader.exec_module(bhg)
satirlar, capraz, camp = [], [], []
for kisa, sinif, rol in MODELLER:
    gsim = Campbell1981EQLive() if sinif is None else registry[sinif]()
    for mag in MW:
        for vs30 in VS30:
            o = oq_hesap(gsim, mag, vs30)
            p = pygmm_hesap(kisa, mag, vs30) if sinif else None
            for im in IMS:
                for k, rjb in enumerate(RJB):
                    med, sg = (o[im][0][k], o[im][1][k]) if im in o else (None, None)
                    row = {'model': kisa, 'rol': rol, 'openquake_sinifi': sinif or 'Campbell1981EQLive (özel)', 'Mw': mag, 'Rjb_km': rjb, 'Vs30': vs30, 'IM': im,
                           'birim': 'cm/s' if im == 'PGV' else 'g', 'medyan_OQ': med, 'sigma_ln_OQ': sg, 'medyan_ref': None, 'sigma_ref': None,
                           'fark_medyan_yuzde': None, 'fark_sigma_yuzde': None, 'referans': None}
                    if p is not None and im in p and med is not None:
                        rm, rs = float(p[im][0][k]), float(p[im][1][k])
                        row.update(medyan_ref=rm, sigma_ref=rs, fark_medyan_yuzde=abs(med / rm - 1) * 100, fark_sigma_yuzde=abs(sg / rs - 1) * 100, referans='pygmm 0.8.0')
                        capraz.append(row)
                    if sinif is None and med is not None:
                        rm = bhg.gmpe_pga(mag, rjb)
                        row.update(medyan_ref=rm, fark_medyan_yuzde=abs(med / rm - 1) * 100, referans='scripts/build_hazard_grid.py gmpe_pga()')
                        camp.append(row)
                    satirlar.append(row)

with open(os.path.join(BURA, 'ortak_girdi.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(satirlar[0])); w.writeheader(); w.writerows(satirlar)


def ozet(rows, alan):
    v = [r[alan] for r in rows if r[alan] is not None]
    return max(v) if v else None


cap_model = {}
for r in capraz:
    d = cap_model.setdefault(r['model'], {})
    e = d.setdefault(r['IM'], {'medyan': 0.0, 'sigma': 0.0, 'n': 0})
    e['medyan'] = max(e['medyan'], r['fark_medyan_yuzde']); e['sigma'] = max(e['sigma'], r['fark_sigma_yuzde']); e['n'] += 1
kayit = {'aciklama': __doc__.strip().split('\n')[0], 'openquake_engine': openquake.engine.__version__, 'pygmm': pygmm.__version__,
         'girdi': {'Mw': MW, 'Rjb_km': RJB, 'Vs30': VS30, 'mekanizma': 'doğrultu atımlı, rake 0, dip 90', 'ztor_km': 0.0, 'odak_derinligi_km': HYPO,
                   'Rrup = Rx = Rjb; Ry0 = 0': True, 'z1pt0': 'CY14 küresel ortalama', 'ESHM20_bolge': 0, 'vs30measured': True, 'IM': IMS},
         'build_hazard_grid_sha256': hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest(),
         'capraz_kontrol_pygmm': cap_model,
         'campbell1981_en_buyuk_fark_yuzde': ozet(camp, 'fark_medyan_yuzde'), 'campbell1981_n': len(camp), 'satir_sayisi': len(satirlar)}
json.dump(kayit, open(os.path.join(BURA, 'ortak_girdi.json'), 'w'), ensure_ascii=False, indent=1)
for m, d in cap_model.items():
    print(f"{m:16s} pygmm ile en büyük fark: " + ', '.join(f"{im} medyan %{e['medyan']:.2e} σ %{e['sigma']:.2e} (n={e['n']})" for im, e in d.items()))
print(f"Campbell 1981: OpenQuake özel sınıf ↔ build_hazard_grid.gmpe_pga en büyük fark %{kayit['campbell1981_en_buyuk_fark_yuzde']:.2e} (n={len(camp)})")
print('satır:', len(satirlar))
