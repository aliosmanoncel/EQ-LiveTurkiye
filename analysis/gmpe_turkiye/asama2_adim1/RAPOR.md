# GMPE Türkiye — Aşama 2, adım 1: OpenQuake yazılım doğrulaması

Tarih: 2026-11-02. Dal: `gmpe-turkiye-methodology`. Yöntem belgesi: `../YONTEM.md` (revizyon 10).

**Durum: KAPATILDI** (kullanıcı kararı, 2026-11-02) — yazılım doğrulaması olarak. Terim: sonuçlar "**OpenQuake doğrulama tablolarıyla sayısal uyum sağlandı**" olarak ifade edilir; "bağımsız referanslarla doğrulandı" denmez, çünkü bazı modellerde ikinci bağımsız uygulama yok ve AC10 tablosunun kaynağı belirsiz.

| Kanıt düzeyi | Sonuç |
|---|---|
| OpenQuake referans tablolarıyla sayısal uyum (9 model) | Başarılı |
| pygmm ile ikinci uygulama karşılaştırması | Üç model için başarılı (ASB14, BSSA14, CY14) |
| Campbell (1981) ↔ mevcut EQ-Live betiği | Birebir eşit (yalnız kod eşitliği) |
| AC10 referans tablosunun kaynağı ve bağımsızlığı | Açık |
| T1 KAAH15 / T2 referans Vs30 / T3 ESHM20 bölgelendirmesi / T5 Campbell (1981) | Açık |
| T4 NESS / ESM künyeleri | Kayıt karşılaştırmasından önce açık |

**Kapsam sınırı.** Bu adım yalnız **yazılım doğrulamasıdır**. Sonuçlar, OpenQuake 3.26.2'deki GMPE uygulamalarının bağımsız uygulamalarla aynı sayıları verdiğini gösterir. Bunlar şunları göstermez:
- modellerin Türkiye depremleri, tektonik ortamı ya da saha koşulları için uygunluğu;
- modellerin performansı.

Bu sorular Aşama 2'nin 3. adımına aittir. Ortak girdi ızgarası bir test ızgarasıdır; gerçek bir deprem ya da Türkiye senaryosu değildir.

## Sonuç

| Model | Rol | OpenQuake sınıfı | Referans ve niteliği | En büyük fark, hedef IM: medyan / σ (%) | pygmm ile fark: medyan / σ (%) | Tolerans (OpenQuake testi) | Sonuç | T1 | T2 |
|---|---|---|---|---|---|---|---|---|---|
| ASB14 | Liste B | `AkkarEtAlRjb2014` | Yazarların Matlab kodu — güçlü bağımsız çapraz kontrol | 4,9·10⁻⁷ / 6,1·10⁻⁸ | 8,9·10⁻¹⁴ / 3,4·10⁻³ | 0,1 | **Geçti** | Kapalı (Akkar vd. 2018, Tablo 1) | Açık: Vref 750 m/s, OpenQuake kodundan, **yayından doğrulanmamış** |
| AC10 | Liste B | `AkkarCagnan2010` | Kaynağı belirtilmemiş test tablosu — **sayısal uyum sağlandı; tablonun kaynağı ve bağımsızlığı doğrulanmadı** | 4,3·10⁻² / 4,5·10⁻³ | — | 0,1 | **Geçti** | Kapalı (Akkar vd. 2018, Tablo 1) | Açık: BA08 büyütmesi, Vref 760 m/s, **yayından doğrulanmamış** |
| KAAH15 | Liste B | `KaleEtAl2015Turkey` | Yazarların Matlab kodu — güçlü bağımsız çapraz kontrol | 4,7·10⁻⁷ / 8,0·10⁻⁸ | — | 0,1 | **Geçti** | **Açık** | Açık: Vref 750 m/s, **yayından doğrulanmamış** |
| BSSA14 Yüksek Q | Liste B | `BooreEtAl2014HighQ` | D. M. Boore'un Fortran uygulaması (2014) — güçlü bağımsız çapraz kontrol | 4,2·10⁻³ / 7,6·10⁻³ | 8,0·10⁻³ / 0 | 2,0 (σ 1,0) | **Geçti** | Kapalı (Gregor vd. 2014) | Açık: Vref 760 m/s, **yayından doğrulanmamış** |
| CY14 | Liste B | `ChiouYoungs2014` | Medyan: yazarların aracı; σ: OpenSHA — iki çıktı için farklı referanslar | 6,4·10⁻¹¹ / 1,1·10⁻³ (yalnız SA) | 1,8·10⁻¹³ / 3,3·10⁻¹⁴ | 0,05 | **Geçti** | Kapalı (Gregor vd. 2014) | Açık: 1130 m/s, **yayından doğrulanmamış** |
| ESHM20 | Liste B | `KothaEtAl2020ESHM20` | Yazarın R uygulaması — güçlü bağımsız çapraz kontrol | 4,8·10⁻⁷ / 7,2·10⁻⁷ | — | 0,01 | **Geçti** | Temel model kapalı (Kotha vd. 2020) | Açık: 800 m/s (uyarlama), **yayından doğrulanmamış** |
| CY08 | Karşılaştırma | `ChiouYoungs2008` | OpenSHA — referans uygulama doğrulaması | 4,5·10⁻² / 1,3·10⁻² | — | 0,05 | **Geçti** | — | — |
| Zh06 | Karşılaştırma | `ZhaoEtAl2006Asc` | J. Zhao'nun Fortran uygulaması — güçlü bağımsız çapraz kontrol | 3,0·10⁻¹ / 3,6·10⁻² (PGV yok) | — | 0,4 | **Geçti** | — | — |
| Campbell 1981 | Karşılaştırma | `Campbell1981EQLive` (özel) | `scripts/build_hazard_grid.py` `gmpe_pga()` (main) — yalnız kod eşitliği | 0 (40 değer, yalnız PGA) | — | birebir | **Geçti** | Açık (T5) | — |

Tablo notları:
- "Hedef IM" PGA, PGV, SA(0,2 s) ve SA(1,0 s) demektir.
- Farklar referans tablodaki bütün satırların en büyüğüdür; değer sayıları `tablo_dogrulama.json` dosyasında. Örnek: ASB14 ve KAAH15'te her biri 34 560 değer.
- "pygmm ile fark" ortak girdi ızgarasındaki 40 senaryonun en büyüğüdür.
- "Geçti", farkın OpenQuake'in kendi testindeki eşiğin altında olduğu anlamına gelir. Bütün Liste B modellerinde hedef IM'lerdeki fark ≤ %0,05.

### Ayrıntılar ve sınırlar

1. **BSSA14 — hedef IM ile bütün tablo ayrı:**
   - Hedef IM'ler (PGA, PGV, SA 0,2 s, SA 1,0 s): en büyük fark %0,0042.
   - Bütün referans tablosu (bütün periyotlar): en büyük fark %1,76, yalnız SA(0,23 s) satırında.
   - OpenQuake'in BSSA14 testindeki tolerans %2 (σ için %1). Bu bir yazılım test eşiğidir, **bilimsel performans eşiği değildir**.
2. **CY14:** OpenQuake'in bağımsız medyan tablosunda PGA ve PGV yok. Bu iki IM yalnız pygmm ile çapraz denetlendi; fark ≤ 2·10⁻¹³ %.
3. **AC10:** Test tablosunun kaynağı OpenQuake test dosyasında belirtilmemiş. Bağımsızlığı bu nedenle **belirsiz**. pygmm'de AC10 yok. Kaynak, ilgili makale (T2) okunduğunda yeniden değerlendirilecek.
4. **AC10, KAAH15, ESHM20, CY08 ve Zh06** için ikinci bir bağımsız uygulama yok; tek referans OpenQuake'in doğrulama tablosudur.
5. **Zh06:** PGV tanımlı değil. Hücre boş bırakıldı, değer üretilmedi.
6. **Campbell (1981):** Özel sınıf, EQ-Live katmanındaki uygulamanın birebir kopyasıdır. Uzaklık dış merkez uzaklığıdır. σ katmanda kullanılmadığı için 0 verildi. Denklemin yayınla uyumu ayrı bir sorudur (T5, açık). Bu satır yalnız "OpenQuake'teki kopya = mevcut betik" eşitliğini gösterir.
7. **Ortak girdi ızgarasında bir girdi hatası bulunup düzeltildi.** OpenQuake'in `global_mean_z1pt0` işlevi z1.0'ı değil ln(z1.0)'ı döndürüyor. İlk çalıştırmada bu değer metre gibi girildi. Sonuç: pygmm ile CY14'te PGV %5,4, SA(1,0 s) %16,8 farklı çıktı. Düzeltmeden sonra (exp ile metreye çevrildi) fark ≤ 2·10⁻¹³ %. Bu bir OpenQuake hatası değil, bizim girdi hatamızdı. Çapraz denetimin bu tür hataları yakaladığını gösteriyor.
8. **Ortak girdi ızgarasının kapsam sınırı:** Izgara yalnız doğrultu atımlı faylanma, düşey düzlem ve ztor = 0 (Rrup = Rx = Rjb) içerir. Ters ve normal faylanma, eğimli fay geometrisi ve asılı blok etkileri bu ızgarada sınanmadı. OpenQuake'in referans tabloları bu durumların bir kısmını içerir (ör. CY14 HW tabloları: normal, ters), ama ortak ızgara içermez. Adım 1'in başarılı olması bütün mekanizma ve geometri seçeneklerinin doğrulandığı anlamına gelmez. Vs30 = 760 m/s ortak girdidir; bütün modellerin doğal referans kaya koşulu değildir.
9. **KAAH15'in Mw 7,8 çıktısı:** "Yazılım çıktısı üretildi; model geçerlilik aralığı henüz doğrulanmadı" (T1 açık). Bu değerler için ne "ekstrapolasyon" ne "aralık içinde" denir.
10. **OpenQuake test paketinin dört testi bu ortamda çalışmadı.** Nedeni, pip kurulumunda eksik iki veri dosyası (`cy14_host_to_target/source_function_table.txt` ve `Kotha_2020/kotha_attenuation_regions.geojson`). İlgili sınıflar `BooreEtAl2022Adjustments` ve `KothaEtAl2020regional`; ikisi de aday değil, sonuçları etkilemez. Bu ESHM20 bölgesel coğrafi dosyası D2/T3 için ayrıca gerekecek.

## Ortak girdi ızgarası: örnek sonuçlar (yalnız yazılım çıktısı)

Ortak girdiler: doğrultu atımlı, düşey düzlem, ztor = 0. Bu nedenle Rrup = Rx = Rjb ve dış merkez uzaklığı = Rjb. Odak derinliği 10 km, Vs30 = 760 m/s (D5 senaryo 1: **ortak girdi**; bütün modellerin referans kayası değil). Değerler medyan PGA (g), parantez içinde σ_ln:

| Model | Mw 6, Rjb 10 km | Mw 6, Rjb 100 km | Mw 7,8, Rjb 10 km | Mw 7,8, Rjb 100 km |
|---|---|---|---|---|
| ASB14 | 0,146 (0,71) | 0,008 (0,71) | 0,317 (0,71) ᵉ | 0,042 (0,71) ᵉ |
| AC10 | 0,105 (0,83) | 0,006 (0,83) | 0,217 (0,83) ᵉ | 0,026 (0,83) ᵉ |
| KAAH15 | 0,112 (0,73) | 0,007 (0,73) | 0,293 (0,57) ? | 0,036 (0,57) ? |
| BSSA14 Yüksek Q | 0,187 (0,61) | 0,018 (0,61) | 0,317 (0,61) | 0,066 (0,61) |
| CY14 | 0,151 (0,62) | 0,009 (0,62) | 0,341 (0,55) | 0,057 (0,55) |
| ESHM20 | 0,164 (0,67) | 0,009 (0,67) | 0,217 (0,64) ᵉ | 0,035 (0,64) ᵉ |
| CY08 | 0,166 (0,60) | 0,009 (0,60) | 0,344 (0,52) | 0,053 (0,52) |
| Zh06 | 0,159 (0,68) | 0,013 (0,68) | 0,448 (0,68) | 0,076 (0,68) |
| Campbell 1981 (EQ-Live) | 0,163 (—) | 0,018 (—) ᵉ | 0,429 (—) ᵉ | 0,079 (—) ᵉ |

İşaretler:
- **ᵉ**: modelin yayımlanmış veri aralığı dışında (ekstrapolasyon). AC10 ve ASB14'te Mw ≤ 7,6; ESHM20'de Mw ≤ 7,4. Campbell (1981) için R > 50 km **[teyit, T5]**.
- **?**: yazılım çıktısı üretildi; KAAH15'in geçerlilik aralığı henüz doğrulanmadı (T1 açık) — ne ekstrapolasyon ne aralık içi.

Bu tablo **modellerin karşılaştırması ya da sıralaması değildir**. Yalnız ortak girdilerle sayıların üretildiğini ve tutarlı biçimde kaydedildiğini gösterir. Bütün sayılar `ortak_girdi.csv` dosyasında: 9 model × 4 Mw × 5 Rjb × 2 Vs30 × 4 IM = 1440 satır.

## Yeniden üretim

Ortam:
- `openquake.engine` 3.26.2 (GDAL olmadan kurulum);
- pygmm 0.8.0;
- Python 3.13.

Referans tablolar: `gem/oq-engine`, etiket v3.26.2 (commit `080f8f82392fed7259204a79271e2858f7a49209`), `openquake/hazardlib/tests/gsim/data/`. Her tablonun SHA-256 değeri `tablo_dogrulama.json` dosyasında.

Adımlar:
1. Referans tabloları seyrek klonla al: `git clone --depth 1 --branch v3.26.2 --filter=blob:none --sparse https://github.com/gem/oq-engine.git`, ardından `git sparse-checkout set openquake/hazardlib/tests/gsim`.
2. Tabloları kurulu pakete kopyala (test yardımcıları `openquake.hazardlib.tests.gsim.utils` için): `tests/__init__.py` ve `tests/gsim/`.
3. Tablo doğrulaması: `python tablo_dogrulama.py <…/tests/gsim/data>` → `tablo_dogrulama.json`.
4. Ortak girdi, pygmm ve Campbell denetimi: `python ortak_girdi.py <main'deki scripts/build_hazard_grid.py>` → `ortak_girdi.csv`, `ortak_girdi.json`. Betiğin SHA-256 değeri JSON'da; git blob kimliği `ef186a2b243650cef39863bd9b6c9e3da3c6a4a8`.
5. İsteğe bağlı: OpenQuake'in kendi testleri `pytest openquake/hazardlib/tests/gsim/{akkar_2014,akkar_cagnan_2010,kale_2015,boore_2014,chiou_youngs_2014,kotha_2020,zhao_2006,chiou_youngs_2008}_test.py`. Sonuç: 57 geçti, 4 kaldı (10. madde).

## Açık kalanlar (Aşama 2, 3. adımdan önce)

- **T1:** KAAH15'in geçerlilik aralığı.
- **T2:** Altı modelin referans Vs30 değerleri. Şu an yalnız OpenQuake kodundan alındı; bütün sonuçlarda "yayından doğrulanmamış" etiketiyle.
- **AC10 tablosunun kaynağı** (2. bölüm, madde 3).
- **T3** (ESHM20 bölgelendirme dosyası), **T5** (Campbell 1981) ve **T4** (NESS ve ESM künyeleri; kayıt karşılaştırmasından önce).
