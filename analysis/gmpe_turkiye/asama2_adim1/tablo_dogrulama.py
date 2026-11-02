"""Aşama 2, adım 1 (a): OpenQuake 3.26.2 GMPE uygulamalarının referans doğrulama tablolarına karşı sınanması.

Referans tablolar OpenQuake deposunun v3.26.2 etiketindeki `openquake/hazardlib/tests/gsim/data/` dizinindendir
(tabloların kaynağı her modelin test dosyasındaki açıklamada yazılıdır; aşağıda `kaynak`). OpenQuake'in kendi testi yalnız
"eşik altında mı" diye bakar; bu betik her model, çıktı türü (medyan / toplam σ) ve IM için **en büyük göreli farkı (%)** ölçer
ve kaydeder. IM'ler: PGA, PGV, SA(0,2 s), SA(1,0 s) (yöntem belgesi §5) — tabloda olmayan IM atlanır ve kayda geçer.

Bu yalnız YAZILIM doğrulamasıdır: OpenQuake uygulamasının, tabloyu üreten bağımsız uygulamayla (çoğunlukla yazarların kodu)
aynı sayıyı verdiğini gösterir; modelin Türkiye'ye uygunluğu hakkında sonuç üretmez (YONTEM.md §8.5).

Kullanım: <oqenv>/bin/python tablo_dogrulama.py <oq-engine v3.26.2 tests/gsim/data dizini>  → tablo_dogrulama.json
"""
import hashlib, json, os, sys
import numpy as np
from openquake.hazardlib.tests.gsim.utils import read_cmaker_df, gen_ctxs
from openquake.hazardlib.gsim.base import registry
import openquake.engine

DATA = sys.argv[1]
IMS = ['PGA', 'PGV', 'SA(0.2)', 'SA(1.0)']
# (rol, OpenQuake sınıfı, kurucu argümanları, medyan tablosu, toplam σ tablosu, tablonun kaynağı — test dosyasındaki açıklamadan)
MODELLER = [
    ('Liste B', 'ASB14', 'AkkarEtAlRjb2014', {}, 'AKKAR14/AKKAR_2014_RJB_MEAN.csv', 'AKKAR14/AKKAR_2014_RJB_STD_TOTAL.csv',
     'yazarların Matlab kodundan üretilmiş tablolar (akkar_2014_test.py)'),
    ('Liste B', 'AC10', 'AkkarCagnan2010', {}, 'AC10/AC10_MEAN.csv', 'AC10/AC10_STD_TOTAL.csv',
     'test dosyasında kaynak belirtilmemiş (akkar_cagnan_2010_test.py)'),
    ('Liste B', 'KAAH15', 'KaleEtAl2015Turkey', {}, 'KALE15/KALE_2015_TURKEY_MEAN.csv', 'KALE15/KALE_2015_TURKEY_STD_TOTAL.csv',
     'yazarların Matlab kodundan üretilmiş tablolar (kale_2015_test.py)'),
    ('Liste B', 'BSSA14 Yüksek Q', 'BooreEtAl2014HighQ', {}, 'BSSA2014/BSSA_2014_HIGHQ_MEAN.csv', 'BSSA2014/BSSA_2014_HIGHQ_TOTAL_STD.csv',
     'D. M. Boore\'un Fortran uygulaması, Temmuz 2014 (boore_2014_test.py)'),
    ('Liste B', 'CY14', 'ChiouYoungs2014', {}, 'NGA/CY14/CY14_MEDIAN_MS_HW_SS.csv', 'NGA/CY14/CY14_TOTAL_EVENT_SIGMA.csv',
     'medyan: yazarların verdiği araç; σ: OpenSHA ile üretilmiş (chiou_youngs_2014_test.py)'),
    ('Liste B', 'ESHM20', 'KothaEtAl2020ESHM20', {}, 'kotha20/KOTHA_2020_ESHM_CENTRAL_MEAN.csv', 'kotha20/KOTHA_2020_ESHM_STDDEV_TOTAL.csv',
     'yazarın R uygulamasından beklenen değerler (kotha_2020_test.py)'),
    ('Karşılaştırma', 'CY08', 'ChiouYoungs2008', {}, 'NGA/CY08/CY08_MEDIAN_MS_HW_SS.csv', 'NGA/CY08/CY08_SIGMEAS_MS_HW_SS.csv',
     'OpenSHA ile üretilmiş (chiou_youngs_2008_test.py); σ: ölçülmüş Vs30'),
    ('Karşılaştırma', 'Zh06', 'ZhaoEtAl2006Asc', {}, 'ZHAO06/Z06Asc_MEAN.csv', 'ZHAO06/Z06Asc_STD_TOTAL.csv',
     'J. Zhao\'nun Fortran uygulaması (zhao_2006_test.py)'),
]


def sha256(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def olc(gsim, dosya, cikti):
    """dosyadaki her satır için OpenQuake sonucunu hesapla; IM başına en büyük göreli farkı (%) döndür"""
    cmaker, df = read_cmaker_df(gsim, [dosya])
    imtler = list(cmaker.imtls)
    oi = 0 if cikti == 'MEAN' else 1   # get_mean_stds: [mean, sig, tau, phi]
    enb = {im: 0.0 for im in imtler}; n = {im: 0 for im in imtler}
    for ctx in gen_ctxs(df):
        ctx.occurrence_rate = 0
        out = cmaker.get_mean_stds([ctx], split_by_mag=False)[:, 0]
        bek_df = getattr(ctx, cikti if cikti == 'MEAN' else 'TOTAL_STDDEV', None)
        if bek_df is None:
            continue
        for m, im in enumerate(imtler):
            got = np.exp(out[oi, m]) if cikti == 'MEAN' else out[oi, m]
            bek = bek_df[im].to_numpy()
            fark = np.abs(got / bek - 1) * 100
            enb[im] = max(enb[im], float(np.nanmax(fark))); n[im] += len(bek)
    return enb, n


sonuc = []
for rol, kisa, sinif, kw, f_ort, f_sig, kaynak in MODELLER:
    gsim = registry[sinif](**kw)
    kayit = {'rol': rol, 'model': kisa, 'openquake_sinifi': sinif, 'tablo_kaynagi': kaynak, 'tablolar': {}}
    for cikti, f in (('MEAN', f_ort), ('TOTAL_STDDEV', f_sig)):
        p = os.path.join(DATA, f)
        enb, n = olc(gsim, p, cikti)
        kayit['tablolar'][cikti] = {
            'dosya': f, 'sha256': sha256(p),
            'IM_sayisi': len(enb), 'satir_x_IM': int(sum(n.values())),
            'en_buyuk_fark_yuzde_tum_IM': max(enb.values()),
            'en_buyuk_fark_yuzde_hedef_IM': {im: (enb[im] if im in enb else None) for im in IMS},
        }
    sonuc.append(kayit)
    t = kayit['tablolar']
    print(f"{kisa:16s} medyan: en büyük fark %{t['MEAN']['en_buyuk_fark_yuzde_tum_IM']:.2e} ({t['MEAN']['satir_x_IM']} değer) | "
          f"σ: %{t['TOTAL_STDDEV']['en_buyuk_fark_yuzde_tum_IM']:.2e} ({t['TOTAL_STDDEV']['satir_x_IM']} değer) | "
          f"hedef IM eksik: {[im for im, v in t['MEAN']['en_buyuk_fark_yuzde_hedef_IM'].items() if v is None]}")

json.dump({'aciklama': __doc__.strip().split('\n')[0], 'openquake_engine': openquake.engine.__version__,
           'referans_tablolar': 'gem/oq-engine v3.26.2 (080f8f82392fed7259204a79271e2858f7a49209), openquake/hazardlib/tests/gsim/data',
           'hedef_IM': IMS, 'modeller': sonuc}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tablo_dogrulama.json'), 'w'),
          ensure_ascii=False, indent=1)
