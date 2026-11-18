# SCSN Regional Box — Independent Reproduction (2026-11-18)

Referans: Azad Khan vd. (2025), JGR 130(7), e2024JB030733; kod arşivi Zenodo 14055540 (v0.0.1-alpha, 65dec41, SHA-256 22eabc57d2a3…); statseis 0.0.6.
Makalenin 74 ana şokluk birleştirilmiş referans kümesiyle KARIŞTIRILMAMALIDIR.

## Veri
Kaynak: SCEDC yıllık SCEC_DC dosyaları 2008–2017 (kullanıcı tarafından indirildi). Olay türü filtresi: YOK (qb dahil; yazarların kodu gibi).
Bölge kutusu: boylam −118,80/−115,40; enlem 32,68/36,20. Dosya alanı: 32–37 K, −122/−114.

- 2008.txt: 252665a2dd75c50a7619d163043518b53a80c01f21c659ccd8c3a58e5f449626
- 2009.catalog.txt: 5fdf2f1971060f3582b2636069bf8a3833b59b021a2ecb60dffd5408708669b7
- 2010.catalog.txt: dca7369f16ed3763ae1eb0c6f430963c5d2c820e4e44813193e0d4dc0d6f9603
- 2011.catalog.txt: e42ae7df64c3aad68ae1850d63210e021110c2fc1f248d1ec58686891907cb35
- 2012.catalog.txt: 189018e8f874b1a515cccfd37f4c36d35d47ea79dffb9c8e833afa6218e08485
- 2013.catalog.txt: d7f75d1a83f0c6ae8bee42f22514e515769d20ad8e8ebd1e1408a1ee5918dcd3
- 2014.catalog.txt: d706bc1fc1368914b3401d1723aaf26c6d5d4443b109bded4dfded795642e96e
- 2015.catalog.txt: 93b2d811143ca75c87a1e96b6aaf778cfde50248edb9b957c2cdd4d2b8589288
- 2016.catalog.txt: cbd6fbbec5265d3885c010110bdf76e54118d9f599e34801df7c64c6e63c3d4b
- 2017.catalog.txt: 912c84f31fd062450fc5269293b751edbfbeded15419dcfa5e0359808dfe000d

Olay: tüm 186408 (Khan 179 446); bölge 152494 (Khan 148 280).

## Ana şok seçimi
| | Aday | Fixed | Mag-Dep | Combined |
|---|--:|--:|--:|--:|
| Bölge — bu çalışma | 90 | 63 | 64 | 61 |
| Bölge — Khan vd. | 90 | 67 | 64 | 61 |
| Tüm alan — bu çalışma | 269 | 125 | 123 | 107 |
| Tüm alan — Khan vd. | 257 | 106 | 108 | 88 |

## Mc ve Empirical test (bölge, Combined)
- Combined 61; Mc için <275 olay: 3 → analiz 58
- Yerel Mc ortanca 1.3 (aralık [0.7, 1.9]); Mc yarıçapı dağılımı (km: adet) {'10': 47, '15': 5, '25': 2, '30': 1, '20': 1, '35': 1, '40': 1}
- Empirical anlamlı (p<0,01): 15/58 = %25.9 (Wilson %95: %16.3–%38.4); makale SCSN %22 (16/74)
- Type A (M≥3, Mc kesmesiz): 24/61; makale %35 (26/74)

Ana şok bazında sonuçlar: SCSN_bolge_61_sonuclar.csv

## Açık konular
- Tüm alan farkı (269/107 ↔ 257/88): yazarların sorgu alanı/olay türü kaydı arşivde yok; yazarların aday kimlik listesi de arşivde yok (defter çıktıları silinmiş), bu yüzden kimlik bazında karşılaştırma yapılamadı.
- Fixed 63 ↔ 67: olay bazında inceleme gerekli.