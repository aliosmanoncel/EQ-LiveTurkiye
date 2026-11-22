#!/usr/bin/env python3
"""VS30 katmanı — USGS Global Vs30 Mosaic → data/vs30_usgs_sinif.png (yaklaşık ZA–ZE gösterge rengi),
data/vs30_usgs_deger.png (nokta sorgusu için kayıpsız değer kodlaması) + data/vs30_usgs_meta.json

Kaynak: U.S. Geological Survey (2025). The U.S. Geological Survey global Vs30 mosaic
[Data release]. https://doi.org/10.5066/P1NV6UNM — kamu malı (public domain).
Türkiye dahil USGS kapsamı dışındaki bölgelerde değerler topoğrafik eğime dayalı
vekildir (Wald & Allen, 2007, BSSA 97(5), 1379–1395, doi:10.1785/0120060267).
SAHA ÖLÇÜMÜ DEĞİLDİR; TBDY 2018 yerel zemin sınıfı saha etüdüyle belirlenir.

Kullanım (iki giriş seçeneği):
  # 1) USGS paketindeki global mozaikten (vs30.zip → vs30/vs30_mosaic.tif, ~357 MB):
  python scripts/build_vs30_layer.py --tif vs30/vs30_mosaic.tif
  # 2) Repodaki türetilmiş kesitten (data/vs30_usgs_clip.npz, bu betiğin ürettiği):
  python scripts/build_vs30_layer.py --npz data/vs30_usgs_clip.npz

Ham global mozaik git'e GİRMEZ (README "Large/Excluded Data Files" ilkesi); yalnız
EQ-Live sınırlarına (25–45°D, 34–43°K) kırpılmış int16 kesit ve PNG commit edilir.

Izgara: 30″ (1/120°). Mozaik piksel merkezleri -180 + c/120 (boylam), 84 - r/120 (enlem);
pencere r=4920..5999, c=24600..26999 → 1080×2400 hücre. Görüntü sınırları piksel
KENARLARIDIR: boylam 24.995833–44.995833, enlem 34.004167–43.004167.

Su: USGS mozaiği denizleri/büyük gölleri sabit 600 m/s ile doldurur. Tam 600 değerli,
≥200 hücrelik bağlantılı bölgeler su kabul edilip şeffaf yapılır (Akdeniz, Karadeniz,
Ege, Marmara, Van, Tuz Gölü vb.); karadaki tek tük 600 değerli küçük alanlar korunur.

Harita rengi: TBDY 2018 Tablo 16.1 (VS)30 eşiklerine göre YAKLAŞIK zemin sınıfı GÖSTERGESİ
(ZA >1500, ZB 760–1500, ZC 360–760, ZD 180–360, <180 → "ZE adayı"). Bu bir TBDY sınıflaması
DEĞİLDİR: Tablo 16.1 ayrıca (N60)30 ve (cu)30 ister; ZE ve ZF özel zemin koşullarına bağlıdır
ve yalnız VS30'dan atanamaz; kaya üstünde >3 m zemin varsa ZA/ZB tanımlanmaz. Saha etüdü gerekir.
Nokta sorgusu: vs30_usgs_deger.png — R = VS30 >> 8, G = VS30 & 255, A = 255 kara / 0 su
(tarayıcıda canvas ile okunur; değerler ≤ 1063 olduğundan 16 bit yeterli, kayıpsız).
Develi Jeo-Tur v10.1.0 kesitiyle 5 noktada değerler birebir eşleşti
(Erciyes 784, Develi 1940 depremi 189, Fıraktın 270, Sultan Sazlığı 229, Yahyalı 519 m/s).
"""
import argparse, json, datetime, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent
R0, R1, C0, C1 = 4920, 6000, 24600, 27000
DX = 1 / 120
BINS = [(0, 180, '#7a0177', '< 180'), (180, 240, '#c51b8a', '180–240'), (240, 300, '#f768a1', '240–300'),
        (300, 360, '#fdae61', '300–360'), (360, 490, '#fee08b', '360–490'), (490, 620, '#abdda4', '490–620'),
        (620, 760, '#66c2a5', '620–760'), (760, 99999, '#3288bd', '> 760')]
TBDY = [('ZE', 0, 180), ('ZD', 180, 360), ('ZC', 360, 760), ('ZB', 760, 1500), ('ZA', 1500, 99999)]
# Gösterge renkleri (yüksek hız = mavi, düşük = mor; ZE yalnız "aday")
CLS = [('ZA', 1500, 99999, '#1f3a93', 'Sağlam, sert kayalar'),
       ('ZB', 760, 1500, '#3288bd', 'Az ayrışmış, orta sağlam kayalar'),
       ('ZC', 360, 760, '#99d594', 'Çok sıkı kum, çakıl ve sert kil tabakaları veya ayrışmış, çok çatlaklı zayıf kayalar'),
       ('ZD', 180, 360, '#fdae61', 'Orta sıkı-sıkı kum, çakıl veya çok katı kil tabakaları'),
       ('ZE?', 0, 180, '#c51b8a', 'ZE adayı — Tablo 16.1 ZE: Gevşek kum, çakıl veya yumuşak-katı kil tabakaları; PI > 20 ve w > %40 koşullarını sağlayan toplamda 3 m’den kalın yumuşak kil (cu < 25 kPa) içeren profiller. ZE yalnız VS30 ile atanamaz; ZF kapsamındaki özel koşullar saha etüdüyle araştırılmalı')]


def read_tif(path):
    import tifffile, zarr  # pip install tifffile imagecodecs zarr
    t = tifffile.TiffFile(path)
    z = zarr.open(t.aszarr(), mode='r')
    a = np.asarray(z[R0:R1, C0:C1]).astype(np.int16)
    assert z.shape == (16801, 43201), z.shape
    return a


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--tif'); g.add_argument('--npz')
    args = ap.parse_args()
    if args.tif:
        a = read_tif(args.tif)
        np.savez_compressed(ROOT / 'data/vs30_usgs_clip.npz', vs30=a, r0=R0, c0=C0, dx=DX)
    else:
        d = np.load(args.npz)
        assert int(d['r0']) == R0 and int(d['c0']) == C0
        a = d['vs30']
    a = a.astype(np.int32)
    assert a.shape == (R1 - R0, C1 - C0)

    w = a == 600
    lab, n = ndimage.label(w)
    sizes = ndimage.sum(w, lab, range(1, n + 1))
    water = np.isin(lab, 1 + np.where(sizes >= 200)[0])

    rgba = np.zeros(a.shape + (4,), np.uint8)
    counts = {}
    for code, lo, hi, col, _ in CLS:
        m = (a >= lo) & (a < hi) & ~water
        rgba[m, :3] = [int(col[i:i + 2], 16) for i in (1, 3, 5)]
        rgba[m, 3] = 255
        counts[code] = int(m.sum())
    Image.fromarray(rgba, 'RGBA').save(ROOT / 'data/vs30_usgs_sinif.png', optimize=True)

    enc = np.zeros(a.shape + (4,), np.uint8)
    enc[..., 0] = (a >> 8) & 255
    enc[..., 1] = a & 255
    enc[..., 3] = np.where(water, 0, 255)
    Image.fromarray(enc, 'RGBA').save(ROOT / 'data/vs30_usgs_deger.png', optimize=True)
    back = Image.open(ROOT / 'data/vs30_usgs_deger.png')
    bk = np.asarray(back).astype(np.int32)
    assert ((bk[..., 0] * 256 + bk[..., 1])[~water] == a[~water]).all()  # kayıpsız

    land = a[~water]
    meta = {
        'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'USGS Global Vs30 Mosaic (2025)',
        'source_doi': 'https://doi.org/10.5066/P1NV6UNM',
        'license': 'Public domain (U.S. Geological Survey)',
        'method': 'Türkiye ve çevresinde topoğrafik eğime dayalı vekil (Wald & Allen, 2007, BSSA 97(5), 1379–1395, doi:10.1785/0120060267). '
                  '30″ (~0,9 km) ızgara, en yakın komşu (yeniden örnekleme yok). Su: tam 600 m/s değerli ≥200 hücrelik bölgeler şeffaf.',
        'units': 'm/s (üst 30 m ortalama kayma dalgası hızı)',
        'classes': [{'code': c, 'min': lo, 'max': (hi if hi < 99999 else None), 'color': col, 'tbdy_description': d,
                     'land_cells': counts[c]} for c, lo, hi, col, d in CLS],
        'classes_ref': 'TBDY 2018 Tablo 16.1 — yalnız (VS)30 sütunu; (N60)30 ve (cu)30 kullanılmadı',
        'classes_note': 'VS30 tabanlı YAKLAŞIK zemin sınıfı göstergesi — TBDY sınıflaması değildir. ZE ve ZF yalnız VS30 ile atanamaz; '
                        'temel tabanı ile kaya üstü arasında >3 m zemin varsa ZA/ZB tanımlanmaz. ZF (sahaya özel araştırma gerektiren zeminler) '
                        'bu gösterimin kapsamı dışındadır. Mühendislik amaçlı zemin etüdü değildir. Saha etüdü gerekir. '
                        'Sınıf tanımları TBDY 2018 Tablo 16.1 ile karşılaştırıldı (JMO kopyası, 2026-11-22).',
        'value_png': 'vs30_usgs_deger.png (R*256+G = VS30 m/s; A=0 su)',
        'pga_link': 'YOK — PGA katmanı (Campbell 1981) sabit Vs30=760 m/s kullanır; bu katman o hesaba bağlanmamıştır.',
        'tbdy2018_thresholds': {k: [lo, (hi if hi < 99999 else None)] for k, lo, hi in TBDY},
        'grid_w': int(a.shape[1]), 'grid_h': int(a.shape[0]),
        'bounds': {'minlat': round(84 - (R1 - 0.5) * DX, 6), 'maxlat': round(84 - (R0 - 0.5) * DX, 6),
                   'minlon': round(-180 + (C0 - 0.5) * DX, 6), 'maxlon': round(-180 + (C1 - 0.5) * DX, 6)},
        'stats_land': {'min': int(land.min()), 'max': int(land.max()), 'median': int(np.median(land)),
                       'water_fraction': round(float(water.mean()), 3)},
        'note': 'Bu bir MODEL/VEKİL ürünüdür — saha ölçümü DEĞİLDİR. TBDY 2018 yerel zemin sınıfı (ZA–ZF) saha etüdüyle belirlenir; '
                'VS30 eşiklerine göre verilen karşılık yalnız yaklaşıktır. Eğim vekili havza kenarlarında ve volkanik platolarda büyük hata yapabilir.',
    }
    (ROOT / 'data/vs30_usgs_meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    print('classes', counts)
    print('PNG', a.shape, 'water', meta['stats_land']['water_fraction'], 'bounds', meta['bounds'])


if __name__ == '__main__':
    main()
