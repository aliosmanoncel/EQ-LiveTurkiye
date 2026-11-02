"""Aşama 2, adım 2: mevcut EQ-Live Campbell (1981) PGA uygulaması ile modern GMPE'lerin medyan karşılaştırması (yalnız analiz).

Kullanıcı koşulları (2026-11-02):
 1. Campbell (1981) mevcut EQ-Live uygulamasının aynısı (adım 1'de birebir eşitliği gösterilen `Campbell1981EQLive`).
 2. Campbell'ın dış merkez uzaklığı modern modellerin Rjb'siyle eşdeğer sayılmaz. İki çerçeve ayrı raporlanır:
    A) "Nokta kaynak temsili": aynı sayısal uzaklık R (Campbell'a Repi = R, modern modellere Rjb = R). Bu yalnız kaynak bir nokta
       kabul edildiğinde geçerli bir eşitliktir.
    B) "Uzaklık tanımı farkı dahil (temsili)": saha sonlu kırığa Rjb = R uzaklıkta; Campbell, katmandaki gibi dış merkez uzaklığı
       alır: Repi = R + Δ(Mw), Δ = NESS 2.1'de Repi − Rjb medyanı (YONTEM.md §13). Geometri belirsizliği ve Δ'nın dağılımı dahil değil.
 3. Campbell'ın geçerlilik sınırları T5 doğrulanana kadar işaretli ([teyit]).
 4. Campbell'da σ yok: medyan karşılaştırması ile belirsizlik ayrı. σ'nın yokluğu belirsizliğin sıfır olduğu anlamına gelmez.
 5. Ekstrapolasyon işaretleri korunur. 6. Sonuçlar model sıralaması ya da Türkiye performans değerlendirmesi değildir.

Girdiler: doğrultu atımlı, düşey düzlem, ztor = 0 (Rrup = Rx = Rjb), odak derinliği 10 km; Vs30 = 760 m/s ortak girdi
(bütün modellerin referans kayası değil; Campbell'da zemin terimi yok) ve duyarlılık için 360 m/s (yalnız modern modeller).
Kullanım: <oqenv>/bin/python campbell_karsilastirma.py → campbell_karsilastirma.csv / .json / _sekil.png
"""
import csv, json, os, warnings
import numpy as np
from openquake.hazardlib import contexts, const
from openquake.hazardlib.gsim.base import GMPE, registry
from openquake.hazardlib.imt import PGA
from openquake.hazardlib.gsim.chiou_youngs_2014 import global_mean_z1pt0
import openquake.engine

warnings.filterwarnings('ignore')
BURA = os.path.dirname(os.path.abspath(__file__))
MW = [5.0, 6.0, 7.0, 7.6, 7.8]
R = [1.0, 5.0, 10.0, 20.0, 30.0, 50.0, 75.0, 100.0, 150.0, 200.0]
VS30 = [760.0, 360.0]; HYPO = 10.0
# NESS 2.1 (YONTEM.md §13): Repi − Rjb medyanı (km), Mw sınıfına göre; Mw < 5,5 için NESS'te veri yok
NESS_DELTA = [((5.5, 6.0), 4.2), ((6.0, 6.5), 6.9), ((6.5, 7.0), 11.0), ((7.0, 7.5), 12.6), ((7.5, 8.2), 47.8)]


def delta(mw):
    for (a, b), d in NESS_DELTA:
        if a <= mw < b:
            return d
    return None


class Campbell1981EQLive(GMPE):   # adım 1'deki sınıfla aynı (ortak_girdi.py); EQ-Live build_hazard_grid.py ile birebir
    DEFINED_FOR_TECTONIC_REGION_TYPE = const.TRT.ACTIVE_SHALLOW_CRUST
    DEFINED_FOR_INTENSITY_MEASURE_TYPES = {PGA}
    DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = const.IMC.GEOMETRIC_MEAN
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = {const.StdDev.TOTAL}
    REQUIRES_SITES_PARAMETERS = set(); REQUIRES_RUPTURE_PARAMETERS = {'mag'}; REQUIRES_DISTANCES = {'repi'}

    def compute(self, ctx: np.recarray, imts, mean, sig, tau, phi):
        r_eff = np.maximum(ctx.repi + 0.0606 * np.exp(0.700 * ctx.mag), 1.0)
        for m, _ in enumerate(imts):
            mean[m] = -4.141 + 0.868 * ctx.mag - 1.09 * np.log(r_eff); sig[m] = 0.0


# (kısa ad, sınıf, rol, geçerlilik: (Mw_min, Mw_max, uzaklık türü, R_max, kaynak, durum))
MODELLER = [
    ('ASB14', 'AkkarEtAlRjb2014', 'Liste B', (4.0, 7.6, 'Rjb', 200, 'Akkar vd. 2018, Tablo 1', 'T1 kapalı')),
    ('AC10', 'AkkarCagnan2010', 'Liste B', (5.0, 7.6, 'Rjb', 200, 'Akkar vd. 2018, Tablo 1', 'T1 kapalı')),
    ('KAAH15', 'KaleEtAl2015Turkey', 'Liste B', (None, None, 'Rjb', None, '—', 'T1 açık')),
    ('BSSA14 Yüksek Q', 'BooreEtAl2014HighQ', 'Liste B', (3.0, 8.5, 'Rjb', 400, 'Gregor vd. 2014 (SS)', 'T1 kapalı')),
    ('CY14', 'ChiouYoungs2014', 'Liste B', (3.5, 8.5, 'Rrup', 300, 'Gregor vd. 2014 (SS)', 'T1 kapalı')),
    ('ESHM20', 'KothaEtAl2020ESHM20', 'Liste B', (3.1, 7.4, 'Rjb', 545, 'Kotha vd. 2020 (temel model)', 'T1 kapalı')),
    ('CY08', 'ChiouYoungs2008', 'Karşılaştırma', (4.0, 8.5, 'Rrup', 200, 'Akkar vd. 2018, Tablo 1', '—')),
    ('Zh06', 'ZhaoEtAl2006Asc', 'Karşılaştırma', (5.0, 8.3, 'Rrup', 300, 'Akkar vd. 2018, Tablo 1', '—')),
]
# Campbell (1981): veri aralığı yaklaşık M 5,0–7,7, uzaklık < 50 km, büyüklük ölçeği ML (< 6) / Ms (≥ 6) — hepsi [teyit, T5]
CAMPBELL_GECERLILIK = (5.0, 7.7, 'kırığa en yakın uzaklık [teyit]', 50, 'yayından doğrulanmadı (T5)', 'T5 açık')


def isaret(gec, mw, r):
    mmin, mmax, _, rmax, _, durum = gec
    if mmin is None:
        return '?'                                   # geçerlilik aralığı doğrulanmadı
    dis = (mw < mmin - 1e-9 or mw > mmax + 1e-9 or r > rmax + 1e-9)
    if durum.startswith('T5'):
        return 'ᵉ[teyit]' if dis else '[teyit]'
    return 'ᵉ' if dis else ''


def hesap(gsim, mag, vs30, uzak):
    cm = contexts.ContextMaker('*', [gsim], {'imtls': {'PGA': [0]}, 'mags': ['%.2f' % mag]})
    n = len(uzak); ctx = contexts.RuptureContext()
    ctx.src_id = 0; ctx.rup_id = 0; ctx.occurrence_rate = 0
    ctx.mag = mag; ctx.rake = 0.0; ctx.dip = 90.0; ctx.ztor = 0.0; ctx.hypo_depth = HYPO; ctx.width = 10.0
    r = np.asarray(uzak, float); ctx.rjb = r; ctx.rrup = r.copy(); ctx.rx = r.copy(); ctx.ry0 = np.zeros(n)
    ctx.repi = r.copy(); ctx.rhypo = np.sqrt(r ** 2 + HYPO ** 2)
    z1 = float(np.exp(global_mean_z1pt0(np.array([vs30]))[0]))
    ctx.vs30 = np.full(n, vs30); ctx.vs30measured = np.ones(n, bool); ctx.z1pt0 = np.full(n, z1); ctx.z2pt5 = np.full(n, 1.0)
    ctx.region = np.zeros(n, int); ctx.sids = np.arange(n)
    out = cm.get_mean_stds([ctx], split_by_mag=False)[:, 0]
    return np.exp(out[0, 0]), out[1, 0]


camp = Campbell1981EQLive()
satir = []
for mw in MW:
    cA, _ = hesap(camp, mw, 760.0, R)                                  # A: Repi = R
    d = delta(mw)
    cB = hesap(camp, mw, 760.0, [x + d for x in R])[0] if d is not None else [None] * len(R)   # B: Repi = Rjb + Δ
    for kisa, sinif, rol, gec in MODELLER:
        g = registry[sinif]()
        for vs30 in VS30:
            med, sg = hesap(g, mw, vs30, R)
            for k, r in enumerate(R):
                satir.append({'model': kisa, 'rol': rol, 'Mw': mw, 'R_km': r, 'Vs30': vs30, 'medyan_PGA_g': float(med[k]), 'sigma_ln': float(sg[k]),
                              'campbell_A_g': float(cA[k]), 'oran_A': float(med[k] / cA[k]),
                              'campbell_B_g': None if cB[k] is None else float(cB[k]), 'Delta_km': d,
                              'oran_B': None if cB[k] is None else float(med[k] / cB[k]),
                              'isaret_model': isaret(gec, mw, r), 'isaret_campbell_A': isaret(CAMPBELL_GECERLILIK, mw, r),
                              'isaret_campbell_B': None if d is None else isaret(CAMPBELL_GECERLILIK, mw, r + d)})

with open(os.path.join(BURA, 'campbell_karsilastirma.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(satir[0])); w.writeheader(); w.writerows(satir)

# özet: Liste B aralığı (min–max) ve Campbell, Vs30 = 760
oz = {}
for mw in MW:
    for r in R:
        L = [s for s in satir if s['Mw'] == mw and s['R_km'] == r and s['Vs30'] == 760.0 and s['rol'] == 'Liste B']
        oz[f'{mw}|{r}'] = {'campbell_A': L[0]['campbell_A_g'], 'campbell_B': L[0]['campbell_B_g'],
                           'listeB_min': min(s['medyan_PGA_g'] for s in L), 'listeB_max': max(s['medyan_PGA_g'] for s in L),
                           'oranA_min': min(s['oran_A'] for s in L), 'oranA_max': max(s['oran_A'] for s in L),
                           'oranB_min': None if L[0]['oran_B'] is None else min(s['oran_B'] for s in L),
                           'oranB_max': None if L[0]['oran_B'] is None else max(s['oran_B'] for s in L)}
json.dump({'aciklama': __doc__.strip().split('\n')[0], 'openquake_engine': openquake.engine.__version__,
           'girdi': {'Mw': MW, 'R_km': R, 'Vs30': VS30, 'mekanizma': 'SS, dip 90, ztor 0', 'odak_km': HYPO},
           'NESS_Repi_eksi_Rjb_medyan_km': [{'Mw': list(a), 'Delta_km': d} for a, d in NESS_DELTA],
           'gecerlilik': {k: {'Mw': [g[0], g[1]], 'uzaklik': g[2], 'R_max_km': g[3], 'kaynak': g[4], 'durum': g[5]} for k, _, _, g in MODELLER},
           'campbell_gecerlilik': {'Mw': [5.0, 7.7], 'R_max_km': 50, 'durum': 'yayından doğrulanmadı (T5); büyüklük ölçeği ML/Ms [teyit]'},
           'ozet_Vs30_760': oz}, open(os.path.join(BURA, 'campbell_karsilastirma.json'), 'w'), ensure_ascii=False, indent=1)

# şekil: çerçeve A, Vs30 = 760
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 4, figsize=(15, 4.4), sharey=True)
renk = dict(zip([m[0] for m in MODELLER], ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02', '#a6761d', '#666666']))
for a, mw in zip(ax, [5.0, 6.0, 7.0, 7.8]):
    for kisa, _, rol, _ in MODELLER:
        L = [s for s in satir if s['model'] == kisa and s['Mw'] == mw and s['Vs30'] == 760.0]
        a.loglog([s['R_km'] for s in L], [s['medyan_PGA_g'] for s in L], color=renk[kisa], lw=1.3, ls='-' if rol == 'Liste B' else ':', label=kisa)
    L = [s for s in satir if s['model'] == 'ASB14' and s['Mw'] == mw and s['Vs30'] == 760.0]
    a.loglog(R, [s['campbell_A_g'] for s in L], color='k', lw=2.4, label='Campbell 1981 (EQ-Live), Repi = R')
    if L[0]['campbell_B_g'] is not None:
        a.loglog(R, [s['campbell_B_g'] for s in L], color='k', lw=1.4, ls='--', label='Campbell, Repi = Rjb + Δ (NESS medyanı)')
    a.axvspan(50, 200, color='0.92', zorder=0)
    a.set_title(f'Mw {mw:.1f}' + ('  (AC10, ASB14, ESHM20: ekstrapolasyon)' if mw > 7.6 else ''), fontsize=9)
    a.set_xlabel('R (km): modern modellerde Rjb; Campbell için bkz. lejant', fontsize=8); a.grid(True, which='both', alpha=0.25)
ax[0].set_ylabel('medyan PGA (g), Vs30 = 760 m/s (ortak girdi)')
ax[-1].legend(fontsize=6.5, loc='lower left')
fig.suptitle('Aşama 2.2 — Campbell (1981) EQ-Live uygulaması ve modern GMPE medyanları (yazılım çıktısı; model sıralaması ya da Türkiye performansı değildir). '
             'Gri: Campbell için R > 50 km [teyit, T5]', fontsize=8.5)
fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(os.path.join(BURA, 'campbell_karsilastirma_sekil.png'), dpi=150)
print('satır', len(satir))
for mw in [6.0, 7.8]:
    for r in [10.0, 30.0, 100.0, 200.0]:
        o = oz[f'{mw}|{r}']
        print(f"Mw {mw} R {r:5.0f}: Campbell A {o['campbell_A']:.4f}  B {o['campbell_B']}  ListeB {o['listeB_min']:.4f}–{o['listeB_max']:.4f}  "
              f"oran A {o['oranA_min']:.2f}–{o['oranA_max']:.2f}  oran B {o['oranB_min']}–{o['oranB_max']}")
