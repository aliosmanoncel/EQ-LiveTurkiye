# EQ-Live Türkiye — Yer hareketi tahmini (GMPE): Aşama 1 yöntem belgesi

Tarih: 2026-11-02. Dal: `gmpe-turkiye-methodology` (taban: `main` 9b5d386).
Durum: **taslak, kullanıcı incelemesinde**. Bu commit yalnız bu belgeyi içerir.
- Kod, `index.html`, `data/`, `seismoreport/` ve canlı site değişmedi.

İşaretler:
- **[teyit]**: değer veya ifade birincil yayından henüz doğrulanmadı. Aşama 2'den önce yayından kontrol edilecek.
- **[karar]**: kullanıcı kararı gerekiyor (§11).

---

## 0. Amaç, kapsam ve üç sınır

**Amaç.** EQ-Live kataloğundaki kayıtlı depremler için yer hareketi tahmini üretmek. Her olay için belirli kaynak ve saha varsayımları altında beklenen yer hareketi hesaplanır: medyan, aleatorik dağılım (σ) ve model (epistemik) aralığı.

**Üç sınır (kullanıcı kararı, 2026-11-02):**
1. **Ölçüm değildir.** GMPE çıktısı gerçekleşmiş yer hareketi ölçümü gibi gösterilmez. Her gösterimde "tahmini (model)" etiketi bulunur. İstasyon kaydıyla koşullandırma yoktur (USGS ShakeMap'ten farkı budur; §10).
2. **Campbell (1981) modern modellerle eşdeğer sayılmaz.** Karşılaştırmada modelin yaşı, veri kümesi ve geçerlilik aralığı açıkça yazılır (§1, §3).
3. **Deterministik senaryo ≠ PSHA.** Burada her olay için koşullu bir yer hareketi dağılımı hesaplanır: "bu deprem oldu, şu sahada beklenen PGA dağılımı". Bu bir aşılma olasılığı, tasarım düzeyi veya TBDY parametresi değildir.

**Kapsam dışı (Aşama 1–3):**
- PSHA ve tehlike eğrileri;
- istasyon verisiyle koşullandırma (ShakeMap benzeri);
- uzamsal korelasyonlu alan gerçekleştirmeleri;
- yakın fay yönelim (directivity) ve havza düzeltmeleri;
- düşey bileşen.

---

## 1. Mevcut durum: EQ-Live'daki "Hazard" katmanı

Kaynak: `scripts/build_hazard_grid.py` (main 9b5d386). Girdi: `data/eq_annual.json`, son 12 ay, EMSC, M ≥ 4,5.
- Bugünkü dosyada 752 olay var. Büyüklük türleri: mb 575, Mw 149, M 16, ML 11, Ms 1.
- Çıktı `data/hazard_grid.json`: 0,25° ızgara, bugün en büyük PGA 0,129 g. Bu dosyayı `eq-update.yml` iş akışı yeniden üretiyor.

| # | Tespit | Kod | Bilimsel sonuç |
|---|---|---|---|
| 1 | ln PGA[g] = −4,141 + 0,868 M − 1,09 ln(R + 0,0606 e^(0,700 M)). Katsayılar Campbell (1981) medyan denklemine karşılık geliyor **[teyit]**. | `C1…C5` | Tek model, tek medyan. |
| 2 | R = **dış merkez uzaklığı** (haversine). | `haversine()` | Campbell (1981) kırığa en yakın uzaklık kullanır **[teyit]**. Büyük depremlerde yakın alan için uzaklık fazla, PGA düşük kestirilir. |
| 3 | M = `mw`, yoksa `mag`. Olayların %76'sı mb. | `e['mw'] = e.get('mag')` | Farklı ölçekler tek bir "Mw" gibi kullanılıyor. Campbell (1981) M < 6 için ML, M ≥ 6 için Ms kullanır **[teyit]**. |
| 4 | M ≥ 2,5 ve R ≤ 200 km. | `MW_MIN`, `R_MAX` | Campbell (1981) veri aralığı yaklaşık M 5,0–7,7 ve R < 50 km **[teyit]**. Uygulamanın çoğu bu aralığın dışında (ekstrapolasyon). |
| 5 | Zemin terimi yok; ama etikette "Vs30 = 760 m/s" yazıyor. | `index.html` 599; `method` alanı | Campbell (1981) Vs30'u parametre olarak içermez. 760 m/s etiketi modelin bir özelliği değildir. |
| 6 | σ yok; yalnız medyan. | — | Belirsizlik gösterilmiyor. |
| 7 | Izgara değeri = olaylar arasında **en büyük medyan PGA**. | `pga_max` | Fiziksel olarak "geçen yılın depremlerinden herhangi birinin bu noktada üretmiş olabileceği en büyük medyan PGA". Tehlike (hazard) değildir. |
| 8 | `dep` girdisi alınıyor ama kullanılmıyor. | `gmpe_pga(mw, r, dep)` | Odak derinliği etkisizdir. |
| 9 | Çıktıdaki `source` ve `method` alanları "BA08 simplified, within 150 km" yazıyor. | `result` | Kodla tutarsız. `hazard-etiket` dalında (6e9ff73) düzeltildi, `main`'de değil. |

**Sonuç:** Mevcut katman; ölçek karışımı, uzaklık tanımı, veri aralığı dışı kullanım ve σ eksikliği nedeniyle bilimsel olarak savunulabilir bir yer hareketi tahmini değildir. Bu çalışma onu değiştirmez; yerine ayrı bir katman önerir (§10). Mevcut katmanın kaldırılması ya da yeniden adlandırılması ayrı karar konusudur **[karar D6]**.

---

## 2. Tektonik sınıflar ve model ailesi

| Sınıf | Türkiye'de | Bu çalışmada |
|---|---|---|
| Aktif sığ kabuk (ASC) | KAF, DAF, Ege graben sistemi, Doğu Anadolu sıkışma bölgesi; olayların büyük çoğunluğu | **Ana kapsam** |
| Dalma-batma, levha içi (intraslab) | Helen ve Kıbrıs yayları; Antalya körfezi ve Güneybatı Türkiye'de orta derinlik olayları | Kapsam dışı. Ayrı model ailesi gerekir. |
| Dalma-batma, arayüz | Helen yayı (Girit güneyi) | Kapsam dışı |

**Sınıflandırma kuralı (öneri) [karar D2]:**
- Odak derinliği ≤ 35 km ve olay ASC poligonu içindeyse ASC modelleri kullanılır.
- Diğer olaylar için hesap yapılmaz ve "model sınıfı dışında" etiketi gösterilir.
- Poligon kaynağı önerisi: ESHM20 tektonik bölgelendirmesi **[teyit]**.

---

## 3. Aday modeller (aktif sığ kabuk)

Bütün modeller OpenQuake 3.26.2'de mevcut ve aşağıdaki sınıf adlarıyla bu oturumda listelendi. Campbell (1981) OpenQuake'te yoktur; karşılaştırma için özel sınıf yazılacak (Mindanao Aşama A'daki yöntem).

| Kısaltma | Yayın | OpenQuake sınıfı | Veri | Uzaklık | Gerekli girdiler | IM | Türkiye ile ilgisi |
|---|---|---|---|---|---|---|---|
| **KAAH15** | Kale vd. (2015), BSSA 105(2A):963–980 | `KaleEtAl2015Turkey` | Türkiye ve İran | Rjb | M, rake, Vs30 | PGA, PGV, SA | Türkiye'ye özgü kalibrasyon |
| **ASB14** | Akkar, Sandıkkaya & Bommer (2014), BEE 12(1):359–387 | `AkkarEtAlRjb2014` (Repi/Rhyp sürümleri de var) | Avrupa ve Orta Doğu (RESORCE; çok sayıda Türkiye kaydı) **[teyit]** | Rjb | M, rake, Vs30 | PGA, PGV, SA | Bölgesel |
| **AC10** | Akkar & Çağnan (2010), BSSA 100(6) **[teyit]** | `AkkarCagnan2010` | Türkiye kuvvetli yer hareketi veri tabanı | Rjb | M, rake, Vs30 | PGA, PGV, SA | Türkiye verisi; eski |
| **BSSA14 (Yüksek Q)** | Boore, Stewart, Seyhan & Atkinson (2014), Earthquake Spectra 30(3):1057–1085 | `BooreEtAl2014HighQ` (OpenQuake açıklaması: "High Q regions (e.g. China and Turkey)", Dc3 düzeltmesi) | NGA-West2, küresel | Rjb | M, rake, Vs30 | PGA, PGV, SA | Türkiye için bölgesel soğrulma terimi |
| **CY14** | Chiou & Youngs (2014), Earthquake Spectra 30(3) | `ChiouYoungs2014` | NGA-West2 | Rrup, Rjb, Rx | M, rake, dip, ztor, Vs30, z1.0 | PGA, PGV, SA | Küresel; Türkiye'ye özgü terim yok **[teyit]** |
| **ASK14** | Abrahamson, Silva & Kamai (2014) | `AbrahamsonEtAl2014` | NGA-West2 | Rrup, Rjb, Rx, Ry0 | + genişlik, z1.0 | PGA, PGV, SA | Küresel |
| **CB14** | Campbell & Bozorgnia (2014) | `CampbellBozorgnia2014` | NGA-West2 | Rrup, Rjb, Rx | + hipomerkez derinliği, genişlik | PGA, PGV, SA | Küresel |
| **ESHM20** | Kotha vd. (2020) temel model; Weatherill, Kotha & Cotton (2020), BEE 18:5087–5117 | `KothaEtAl2020ESHM20` | ESM (Avrupa, Türkiye dahil) **[teyit]** | Rjb | M, hipomerkez derinliği, Vs30, soğrulma bölgesi (0–5) | PGA, PGV, SA | Avrupa 2020 tehlike modelinin ölçekli omurgası; epistemik dallar doğrudan tanımlı |
| **C81** (yalnız referans) | Campbell (1981), BSSA 71(6) **[teyit]** | özel sınıf (yazılacak) | Küresel, 1980 öncesi | kırığa en yakın uzaklık **[teyit]** | M | yalnız PGA | Mevcut EQ-Live katmanıyla karşılaştırma içindir; aday değildir |

**Geçerlilik aralıkları (M, uzaklık, Vs30)** her model için yayından tabloya işlenecek **[teyit]**. Aralık dışındaki hücreler gösterimde işaretlenecek (Tr/T sınıflarındaki ilkeyle aynı).

### Türkiye için mevcut kanıt (yalnız okunabilen özetlerden)

- **Akkar, Kale, Yakut & Çeken (2018), BEE 16(8):3439–3463** (doi:10.1007/s10518-017-0101-2): Türkiye Deprem Tehlike Haritası (2018) için yer hareketi nitelendirmesi. Adaylar test edildi ve "merkez, gövde, aralık" (CBR) gruplarına ayrıldı. **Seçilen modeller ve ağırlıklar bu oturumda okunamadı** (makale sayfası erişim sınırına takıldı) **[teyit]**. Aşama 1'in kapanışından önce okunmalı; aday listesi buna göre daraltılır.
- **Buckreis vd. (2024), Earthquake Spectra 40(4):2268–2284** (doi:10.1177/87552930241259024), 6 Şubat 2023 dizisi:
  - Küresel ve Türkiye'ye özgü modeller Rjb > 200 km'de uyumsuz; yazarlar bunu karmaşık yol etkilerine bağlıyor.
  - Küresel model Anadolu bloğunda fazla, Arap bloğunda az tahmin ediyor.
  - Bazı istasyonlardaki eksik tahmin yönelim (directivity) ya da havza etkisinden kaynaklanıyor olabilir.
- **Mabrouk (2024), ODTÜ yüksek lisans tezi** (SMD-TR alt kümesi: 83 olay, 1424 kayıt; 5,5 ≤ Mw ≤ 7,8; Rjb ≤ 200 km):
  - En iyi BSSA21 (BSSA14'ün Yunanistan uyarlaması), ardından ITA18.
  - KAAH15 benzer düzeyde.
  - BSSA14 genelde en düşük, uzun periyotlarda daha iyi.
  - Hakemli dergi yayını değildir.
- **Sharafi vd. (2026), GeoHazards 7(5):131** (doi:10.3390/geohazards7050131; SMD-TR 1976–2023, 12 160 kayıt, 974 olay; LLH ve DIC):
  - Sıralama: AC10 ≈ BSSA21 ≈ KAAH15 > ASB14; BA08 en sonda. Yazarların kendi veriyle geliştirdiği bir model birinci, ama bu kısmen örneklem içi sonuç.
  - Yazarlar sıralamanın mantık ağacı ağırlığı olmadığını belirtiyor.

**Çıkarım (geçici):**
- Türkiye verisiyle kalibre edilmiş veya sınanmış modeller (KAAH15, AC10, ASB14) ile Türkiye için soğrulma terimi olan BSSA14 Yüksek Q, aday çekirdeğini oluşturuyor.
- ESHM20 omurgası, epistemik aralığı tutarlı biçimde veren tek seçenek.
- Hiçbir model Rjb > 200 km'de güvenilir değil (Buckreis vd. 2024). Bu yüzden hesap Rjb ≤ 200 km ile sınırlanmalı **[karar D3]**.

---

## 4. Girdi parametreleri

| Parametre | Kaynak | Sorun | Öneri |
|---|---|---|---|
| **Mw** | Katalog (`mw` / `mag` + `mtype`) | Son 12 ayda %76 mb; GMPE'ler Mw ister | Yalnız Mw ya da belgelenmiş dönüşümle Mw'ye çevrilen olaylar kullanılır. Dönüşüm EQ-Live'daki mevcut tür dönüşüm zinciriyle tutarlı olmalı; dönüşüm belirsizliği σ'ya eklenmez, ayrıca belirtilir **[karar D1]**. |
| **Uzaklık** (Rjb, Rrup, Rx) | Yalnız dış merkez ve derinlik var | Büyük depremde nokta kaynak yakın alanı yanlış verir | Mw < 6: nokta kaynak (Rjb ≈ Repi, Rrup ≈ Rhyp). Mw ≥ 6: sonlu kırık. Seçenekler: (a) OpenQuake nokta kaynağında büyüklük–alan bağıntısı (Wells & Coppersmith 1994 ya da Leonard 2010) ve düğüm düzlemi dağılımıyla tanımlanan kırık; (b) yayımlanmış fay modeli (GCMT/AFAD çözümü, USGS sonlu fay) olan büyük olaylar için gerçek geometri. Repi'den Rjb'ye dönüşümün ek belirsizliği belgelenir **[teyit; karar D4]**. |
| **Fay mekanizması** (rake, dip) | Katalogda yok | GMPE'lerin çoğu fay türü terimi içeriyor | GCMT ya da AFAD moment tensörü varsa kullanılır. Yoksa "belirtilmemiş" seçeneği (BSSA14'te var) ya da bölgesel baskın mekanizma alınır ve epistemik dal olarak gösterilir. |
| **Odak derinliği / ztor** | Katalog `dep` | Katalog derinlikleri belirsiz; 10 km sabit değerleri yaygın | ztor sonlu kırıktan türetilir. Sabit 10 km derinlikli olaylar işaretlenir. |
| **Vs30** | Yok | Haritalı Vs30 vekilleri (topoğrafik eğim) belirsiz | Varsayılan **senaryo: referans kaya 760 m/s** (bütün modellerde aynı Vs30; uzun vadede Mindanao B3'teki "model başına referans kaya" ayrımı da belirtilir). İkinci senaryo: vekil Vs30 haritası (USGS küresel Vs30 mozaiği; Türkiye'ye özgü harita varsa o) **[teyit; karar D5]**. Vs30 ölçülmüş AFAD istasyonları ayrı işaretlenir. |
| **z1.0** | Yok | CY14 ve ASK14 için gerekli | Modelin kendi Vs30–z1.0 bağıntısı (OpenQuake varsayılanı) kullanılır; bu açıkça yazılır. |

---

## 5. Çıktılar

| IM | Birim | Gerekçe |
|---|---|---|
| PGA | g | Mevcut katmanla karşılaştırma |
| PGV | cm/s | Hasarla ilişkisi PGA'dan güçlü; şiddet dönüşümlerinin girdisi |
| SA(0,2 s) | g | TBDY 2018 kısa periyot (S_S) periyodu; TBDY tasarım değeri değildir |
| SA(1,0 s) | g | TBDY 2018 1 s (S_1) periyodu; aynı not |
| (isteğe bağlı) SA(0,3 s), SA(3,0 s) | g | Yüksek binalar ve uzun periyot; Aşama 2 sonrası |

Her IM için **medyan**, **16. ve 84. yüzdelik** (ln-normal: medyan·e^(±σ)) ve **model aralığı** (aday modellerin medyanlarının en küçüğü ile en büyüğü) verilir.

---

## 6. Belirsizlik

- **Aleatorik (σ):**
  - Toplam σ = √(τ² + φ²). τ olaylar arası, φ olay içi bileşendir; ergodik varsayım altında modelin kendi σ'sı kullanılır.
  - Gösterim: 16.–84. yüzdelik.
  - σ kesmesi yapılmaz (deterministik senaryoda kesme gerekmez); yine de bu açıkça yazılır.
- **Epistemik:**
  - (a) Çoklu model: aday modellerin medyanları yan yana. Ağırlık verilmez; ağırlık ancak Aşama 2'deki artık analizinden sonra ve gerekçeyle verilir.
  - (b) ESHM20 omurgası: ölçekli dallar (ör. ±1,28 σ_µ) doğrudan epistemik aralıktır.
  - Aleatorik ve epistemik belirsizlik **tek bir sayıda birleştirilmez**; ayrı gösterilir.
- **Uzamsal yorum uyarısı:** Her ızgara noktasının 84. yüzdeliği ayrı ayrı hesaplanır. Bu nedenle "84. yüzdelik haritası" gerçekleşebilecek tek bir yer hareketi alanı değildir (uzamsal korelasyon yok). Bu uyarı haritada yazılı olmalı.
- **Girdi belirsizlikleri:** Mw dönüşümü, nokta kaynaktan sonlu kırığa geçiş, mekanizma ve Vs30 belirsizlikleri σ'ya eklenmez. Her biri duyarlılık senaryosu olarak raporlanır (Mindanao B3 yaklaşımı).

---

## 7. Deterministik senaryo ve PSHA ayrımı

| | Bu çalışma | PSHA |
|---|---|---|
| Soru | "Bu deprem oldu; sahada yer hareketi dağılımı nedir?" | "t yılda bu düzeyin aşılma olasılığı nedir?" |
| Kaynak | Tek, gerçekleşmiş olay | Bütün olası depremler ve oranları |
| Çıktı | Koşullu dağılım (medyan, σ) | Tehlike eğrisi, aşılma olasılığı |
| TBDY ile ilişki | Yok | TBDY tasarım spektrumu PSHA'dan türetilir |

EQ-Live'daki Poisson modülü bölge ölçeğinde büyüklük aşılma olasılığı verir; bu çalışma ise olay ölçeğinde yer hareketi verir. İkisi birleştirilmez; birleşimi PSHA'dır ve kapsam dışıdır.

---

## 8. Aşama 2 — doğrulama planı

1. **Yazılım doğruluğu.**
   - OpenQuake GMPE'lerin çoğu için doğrulama tablolarıyla birim testi içerir; tabloların kaynağı (yazarlar ya da bağımsız uygulama) model başına kontrol edilir **[teyit]**.
   - Bu testler 3.26.2 ortamında aday modeller için çalıştırılır.
   - EQ-Live'a JavaScript ile taşınacak her model OpenQuake'e karşı sınanır (hedef: göreli fark ≤ 10⁻⁵, float32 sınırı; Mindanao Aşama A ölçütü).
2. **Campbell (1981) özel sınıfı.**
   - Mevcut Python koduyla birebir aynı sonucu vermeli.
   - Ardından modern modellerle M 5, 6, 7, 7,8 ve R 1–200 km için karşılaştırılır; Vs30 = 760 ve 360 m/s.
3. **Geçerlilik denetimi.** Her olay ve ızgara noktası için M, uzaklık ve Vs30 aralık kontrolü; aralık dışı oranı raporlanır.
4. **Kayıtlarla karşılaştırma (artık analizi).**
   - Seçilecek olaylar: 2023 Kahramanmaraş Mw 7,8 ve 7,6; 2020 Elazığ Mw 6,8; 2020 Sisam Mw 7,0; 1999 Düzce Mw 7,2; birkaç Mw 5–6 olay.
   - Yöntem: olaylar arası ve olay içi artıklar, LLH (Scherbaum vd. 2009).
   - Veri: AFAD TADAS ya da SMD-TR (Sandıkkaya vd.) **[karar D7: veri erişimi]**.
   - Bu adım yazılım doğrulaması değil, **model uygunluğu** sınamasıdır.
5. **Raporlama.** Aşama A/B ayrımı korunur: hesaplama doğruluğu ayrı, bilimsel uygunluk ayrı raporlanır.

## 9. Aşama 3 — EQ-Live entegrasyon ilkeleri (öneri)

- Ayrı dal ve ayrı katman; **varsayılan kapalı**. Mevcut "Hazard" katmanına dokunulmaz (D6 kararına kadar).
- Katman adı örneği: "Tahmini yer hareketi (GMPE, model)". "Hazard", "tehlike" ve "ölçülen" sözcükleri kullanılmaz.
- Her değer için açılır bilgi: model, girdiler (Mw kaynağı, uzaklık türü, Vs30 senaryosu), σ, model aralığı, aralık dışı işareti.
- Yeniden üretim kaydı: Poisson modülündeki gibi JSON; katalog ve yazılım kimlikleri (git blob SHA), model sürümleri ve OpenQuake sürümü.
- Hesap yeri: istemci tarafında JavaScript ya da iş akışında Python + OpenQuake ile önceden hesaplanmış ızgara **[karar D8]**. OpenQuake iş akışı doğrulama açısından güçlü; istemci tarafı etkileşim açısından esnek.

## 10. USGS ShakeMap ile ilişki

ShakeMap, GMPE tahminini istasyon kayıtları ve şiddet raporlarıyla koşullandırır. Bu çalışma koşullandırma yapmaz. Bu nedenle aynı olay için ShakeMap varsa:
- ShakeMap'e bağlantı verilir;
- EQ-Live tahmininin koşullandırılmamış olduğu belirtilir.

## 11. Kullanıcı kararları (Aşama 2'den önce)

| No | Konu | Seçenekler / öneri |
|---|---|---|
| D1 | Mw kaynağı | Yalnız Mw olaylar / belgelenmiş dönüşümle Mw (öneri: ikisi ayrı işaretli) |
| D2 | Tektonik sınıflama | Derinlik ≤ 35 km + ESHM20 ASC poligonu (öneri) |
| D3 | Uzaklık sınırı | Rjb ≤ 200 km (öneri) |
| D4 | Büyük depremlerde kırık geometrisi | OpenQuake büyüklük–alan bağıntısı / bilinen fay modeli / ikisi |
| D5 | Vs30 | Referans 760 m/s senaryosu (öneri, varsayılan) + vekil harita senaryosu |
| D6 | Mevcut Campbell (1981) katmanı | Olduğu gibi kalsın / `hazard-etiket` birleştirilsin / yeniden adlandırılsın / kaldırılsın |
| D7 | Kayıt verisi | AFAD TADAS / SMD-TR / ikisi; erişim yolu |
| D8 | Hesap yeri | İstemci (JavaScript) / iş akışı (OpenQuake) |
| D9 | Aday çekirdek | Öneri: KAAH15, ASB14, AC10, BSSA14 Yüksek Q, ESHM20; NGA-West2'nin geri kalanı (CY14, ASK14, CB14) duyarlılık için. Akkar vd. (2018) okununca kesinleşir. |

## 12. Kaynaklar

- Akkar, S., & Çağnan, Z. (2010). A local ground-motion predictive model for Turkey, and its comparison with other regional and global ground-motion models. *Bulletin of the Seismological Society of America, 100*(6), 2978–2995 **[teyit]**.
- Akkar, S., Sandıkkaya, M. A., & Bommer, J. J. (2014). Empirical ground-motion models for point- and extended-source crustal earthquake scenarios in Europe and the Middle East. *Bulletin of Earthquake Engineering, 12*(1), 359–387.
- Akkar, S., Kale, Ö., Yakut, A., & Çeken, U. (2018). Ground-motion characterization for the probabilistic seismic hazard assessment in Turkey. *Bulletin of Earthquake Engineering, 16*(8), 3439–3463. https://doi.org/10.1007/s10518-017-0101-2
- Boore, D. M., Stewart, J. P., Seyhan, E., & Atkinson, G. M. (2014). NGA-West2 equations for predicting PGA, PGV, and 5% damped PSA for shallow crustal earthquakes. *Earthquake Spectra, 30*(3), 1057–1085.
- Buckreis, T. E., Pretell, R., Sandıkkaya, M. A., Kale, Ö., Askan, A., Brandenberg, S. J., & Stewart, J. P. (2024). Engineering attributes of ground motions from February 2023 Türkiye earthquake sequence. *Earthquake Spectra, 40*(4), 2268–2284. https://doi.org/10.1177/87552930241259024
- Campbell, K. W. (1981). Near-source attenuation of peak horizontal acceleration. *Bulletin of the Seismological Society of America, 71*(6), 2039–2070 **[teyit]**.
- Chiou, B. S.-J., & Youngs, R. R. (2014). Update of the Chiou and Youngs NGA model for the average horizontal component of peak ground motion and response spectra. *Earthquake Spectra, 30*(3), 1117–1153.
- Kale, Ö., Akkar, S., Ansari, A., & Hamzehloo, H. (2015). A ground-motion predictive model for Iran and Turkey for horizontal PGA, PGV, and 5% damped response spectrum: Investigation of possible regional effects. *Bulletin of the Seismological Society of America, 105*(2A), 963–980.
- Kotha, S. R., Weatherill, G., Bindi, D., & Cotton, F. (2020). A regionally-adaptable ground-motion model for shallow crustal earthquakes in Europe. *Bulletin of Earthquake Engineering, 18*, 4091–4125 **[teyit]**.
- Mabrouk, A. H. A. S. H. (2024). *Performance of alternative ground motion models with strong-motion data from moderate to large events in different seismotectonic regions in Türkiye* (Yüksek lisans tezi). Orta Doğu Teknik Üniversitesi.
- Scherbaum, F., Delavaud, E., & Riggelsen, C. (2009). Model selection in seismic hazard analysis: An information-theoretic perspective. *Bulletin of the Seismological Society of America, 99*(6), 3234–3247.
- Sharafi, F., Banimahd, S. A., Karimzadeh, S., Askan, A., & Lourenço, P. B. (2026). Objective ground motion model selection and ranking using likelihood and Bayesian criteria: A case study for Türkiye. *GeoHazards, 7*(5), 131. https://doi.org/10.3390/geohazards7050131
- Weatherill, G., Kotha, S. R., & Cotton, F. (2020). A regionally-adaptable "scaled backbone" ground motion logic tree for shallow seismicity in Europe: Application to the 2020 European seismic hazard model. *Bulletin of Earthquake Engineering, 18*, 5087–5117.

Ortam notu: OpenQuake sınıf adları ve gerekli girdiler `openquake.engine 3.26.2` kayıt defterinden (`gsim.base.registry`) 2026-11-02'de okundu.
