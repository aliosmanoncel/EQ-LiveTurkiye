# EQ-Live Türkiye — Yer hareketi tahmini (GMPE): Aşama 1 yöntem belgesi

Tarih: 2026-11-02. Dal: `gmpe-turkiye-methodology` (taban: `main` 9b5d386).
Durum: **taslak, kullanıcı incelemesinde**. Yalnız belge; kod değişikliği yok.
- Revizyon 1 (2026-11-02): kullanıcı incelemesi (ChatGPT yorumu dahil) — D1, uzaklık tanımları, Vs30 kapsamı, belirsizlik türleri, D7 ve D9 güncellendi; NESS 2.1 flat-file'ından nicel bulgular eklendi (§13).
- Revizyon 2 (2026-11-02): kullanıcı incelemesi — Repi − Rjb farkının yorumu, Mw kaynağı kaydı (7,7 / 7,8), Vs30 veri kalitesi işareti, SHA-256'nın kapsamı, yazılım doğrulaması / yöntem doğrulaması ayrımı; §11 her karar için "karar, bilimsel gerekçe, doğrulama durumu" olarak yeniden düzenlendi; Aşama 2'ye geçiş koşulu yazıldı.
- Revizyon 3 (2026-11-02): kullanıcı incelemesi — uzaklık tanımı farkı / geometri belirsizliği / GMPE artığı ayrımı (§6), Vs30 kaynağının analiz çıktısında da gösterilmesi (§8, §9), D9 inceleme sırası (§11).
- Revizyon 4 (2026-11-02): Akkar vd. (2018) tam metni okundu (kullanıcının Zotero kütüphanesi); §3.1 eklendi, D9 için öneri yazıldı.
- Revizyon 5 (2026-11-02): D9 kullanıcı kararıyla kapatıldı (Liste A kabul, Liste B koşullu kabul); üç sınır eklendi (§3.1). D2, D3, D5, D6 için kanıta dayalı öneriler yazıldı; model başına referans Vs30 OpenQuake kaynak kodundan çıkarıldı.
- Revizyon 6 (2026-11-02): D2, D3, D5, D6 kullanıcı kararıyla kapatıldı; yöntemsel geçiş koşulu kapandı; hesap öncesi kalan [teyit] listesi yazıldı (§11).
- Revizyon 7 (2026-11-02): T1, CY14 ve BSSA14 için Gregor vd. (2014) Tablo 1'den kapatıldı (kullanıcının İndirilenler klasöründeki PDF).
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

- **Akkar, Kale, Yakut & Çeken (2018), BEE 16(8):3439–3463** (doi:10.1007/s10518-017-0101-2): Türkiye Deprem Tehlike Haritası (2018) için yer hareketi nitelendirmesi. Tam metin okundu; ayrıntılar §3.1'de.
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

**Çıkarım:**
- Türkiye verisiyle kalibre edilmiş veya sınanmış modeller (KAAH15, AC10, ASB14) ile Türkiye için soğrulma terimi olan BSSA14 Yüksek Q, aday çekirdeğini oluşturuyor.
- ESHM20 omurgası, epistemik aralığı tutarlı biçimde veren tek seçenek.
- Hiçbir model Rjb > 200 km'de güvenilir değil (Buckreis vd. 2024). Bu yüzden hesap Rjb ≤ 200 km ile sınırlanmalı **[karar D3]**.

### 3.1 Türkiye Deprem Tehlike Haritası (2018) yer hareketi mantık ağacı — Akkar vd. (2018), birincil metin

Kaynak: Akkar vd. (2018), BEE 16:3439–3463; kullanıcının Zotero kütüphanesindeki PDF (25 sayfa), 2026-11-02'de okundu. Sayfa numaraları dergi sayfalarıdır.

**Veri (T-SHM_db, Türkiye alt kümesi; s. 3441–3443):**
- 1066 yatay kayıt çifti, 183 olay, 292 istasyon, 1976–2013.
- Mw 4,0–7,6, Rjb 0–200 km, odak derinliği ≤ 30 km.
- Kayıtların yaklaşık %97'sinde Vs30 ölçülmüş.
- Türkiye verisi doğrultu atımlı ve normal faylanma ağırlıklı; zemin çoğunlukla 180–760 m/s.
- Mw için fay düzlemi çözümlerinden gelen değerler tercih edilmiş; dönüşümle hesaplanan Mw küçük olaylarda kullanılmamış (s. 3442). Bu, D1 ile aynı ilkedir.

**Adaylar ve eleme (Tablo 1; s. 3445–3452):**
- Veri dışı ölçütlerle (Cotton vd. 2006; Bommer vd. 2010) 11 aday: Ozb04, KG04, Zh06, CF08, AS08, BA08, CB08, CY08, ASB14, AC10, Bnd14.
- Veri temelli sıralama: yüksek AC10, ASB14, Bnd14, CF08; orta BA08, CY08, Zh06; diğerleri elendi.
- Trellis incelemesinde Bnd14 (kısa periyotta, yakın uzaklık ve büyük M'de belirgin yüksek) ve CF08 (genel olarak yüksek; Japonya havza kayıtları) elendi.
- KAAH15, hakem süreci proje süresinde tamamlanmadığı için **sınanmadı**. Yazarlara göre KAAH15'in yüzdelik eğrileri AC10'a benziyor ve kullanılması dağılımı belirgin değiştirmezdi (s. 3455).
- NGA-West2 yerine NGA-West1 (AS08, BA08, CB08, CY08) kullanıldı, çünkü West2 proje sırasında tam yayımlanmamıştı (s. 3445–3447).
- Trellis referans sahası Vs30 = 760 m/s; bu, ulusal haritanın saha tanımıdır (s. 3450).

**Merkez, gövde, aralık (CBR) sınıflaması (PGA; s. 3454):**
- Merkez ve gövde: ASB14, CY08, BA08.
- Alt aralık: AC10.
- Üst aralık: Zh06.
- 0,2 s ve 1,0 s'de benzer eğilim.

**Nihai mantık ağacı (Tablo 5; s. 3459):**

| Bölge | Model | Ağırlık |
|---|---|---|
| Aktif sığ kabuk | ASB14 | 0,30 |
| | CY08 | 0,30 |
| | AC10 | 0,30 |
| | Zh06 | 0,10 |
| Dalma-batma (EMME'den aktarıldı) | Zh06 | 0,40 |
| | AB03 | 0,20 |
| | Ygs97 | 0,20 |
| | LL08 | 0,20 |

- Karşılaştırma için EMME (Danciu vd. 2016) aktif sığ kabuk ağırlıkları: AC10 0,20, CY08 0,35, ASB14 0,35, Zh06 0,10 (s. 3460).
- **Ağırlıkların amacı:** Normalize edilmiş spektral değerlerle yapılan PSHA duyarlılık analizinden seçildi. Amaç, hiçbir modelin tehlikeyi tek başına belirlememesi. Haritalar PGA, SA(0,2 s) ve SA(1,0 s) için; dönüş periyotları 43, 72, 475 ve 2475 yıl (s. 3458–3459). Ağırlıklar bir modelin bir olay için doğruluk derecesi değil, PSHA'da epistemik yayılımı dengeleyen inanç dereceleridir. Bu yüzden D9 ilkesi gereği bu deterministik katmana aktarılmaz.

**EQ-Live için önemli sonuçlar:**
- AC10 ve ASB14'ün veri aralığı Mw ≤ 7,6. **Kahramanmaraş ana şoku (Mw 7,7–7,8) her iki modelde de ekstrapolasyondur.** Akkar vd. de Mw 8 için AC10'un Rjb > 100 km'de neredeyse düz spektral eğilim verdiğini, çünkü bu büyüklüğün modelin uygulama aralığı dışında olduğunu belirtiyor (s. 3451–3452).
- AC10 yalnız T ≤ 2 s için tanımlı. SA(1,0 s) dahil, ama uzun periyot yok.
- Zh06 Japonya verisinden (Mw 5,0–8,3, Rrup ≤ 300 km); 2018'de "üst aralık" temsilcisi.

**D9 adım 4–5: iki ayrı liste (öneri):**

*Liste A — Türkiye'de geçmişte kullanılan modeller (TBDY 2018 haritasının temeli; kayıt amaçlı):* ASB14, CY08, AC10, Zh06 (aktif sığ kabuk).

*Liste B — EQ-Live için Aşama 2'de sınanacak adaylar:*

| Model | Liste A ile ilişki | OpenQuake sınıfı | Uzaklık | Mw aralığı (yayın) | Gerekçe |
|---|---|---|---|---|---|
| ASB14 | aynı | `AkkarEtAlRjb2014` | Rjb | 4,0–7,6 | Liste A'da merkez/gövde; Avrupa–Orta Doğu verisi |
| AC10 | aynı | `AkkarCagnan2010` | Rjb | 5,0–7,6 | Liste A'da alt aralık; Türkiye verisi; T ≤ 2 s |
| KAAH15 | 2018'de zamanlama nedeniyle sınanmamış; AC10'un ardılı niteliğinde | `KaleEtAl2015Turkey` | Rjb | **[teyit]** | Türkiye–İran verisi; daha yeni Türkiye modeli |
| CY14 | CY08'in ardılı (NGA-West2) | `ChiouYoungs2014` | Rrup, Rjb, Rx | **[teyit]** | Liste A'da merkez/gövde olan CY08'in güncel sürümü |
| BSSA14 Yüksek Q | BA08'in ardılı (2018'de merkez/gövde, nihai ağaçta yok) | `BooreEtAl2014HighQ` | Rjb | **[teyit]** | Türkiye için soğrulma terimi |
| ESHM20 | yok (2020) | `KothaEtAl2020ESHM20` | Rjb | **[teyit]** | Ölçekli omurga ile epistemik aralık |

*Karşılaştırma dalı (aday değil):*
- CY08 (`ChiouYoungs2008`) ve Zh06 (`ZhaoEtAl2006Asc`): EQ-Live tahminlerini TBDY 2018 haritasının model tabanıyla karşılaştırmak için. Liste A'nın tamamı böylece OpenQuake'te yeniden üretilebilir (sınıflar 3.26.2 kayıt defterinde var).
- Campbell (1981) yalnız mevcut katmanla karşılaştırma içindir.
- BA08: 2018 nihai ağacında yok; Sharafi vd. (2026) sıralamasında en sonda. Aday değil.

Ağırlık verilmez. Nihai küme Aşama 2 artık analizinden sonra belirlenir.

**Liste B'nin kapsamı ve üç sınır (kullanıcı kararı, 2026-11-02):** Liste B'ye alınmak, modelin Türkiye için geçerlilik aralığının doğrulandığı ya da performansının yeterli bulunduğu anlamına gelmez; yalnız Aşama 2'de bağımsız olarak sınanacak aday havuzudur.
1. **Mw > 7,6 ekstrapolasyonu:** AC10 ve ASB14'ün Mw 7,7–7,8 (Kahramanmaraş) sonuçları doğrulanmış tahmin gibi sunulmaz; ekstrapolasyon olarak işaretlenir.
2. **Periyot kapsamı:** AC10 yalnız T ≤ 2 s için tanımlıdır; daha uzun periyotlarda AC10 sonucu varmış gibi karşılaştırma yapılmaz (hücre boş bırakılır).
3. **Model sürümleri:** CY14 ve BSSA14, CY08 ve BA08'in ardılıdır ama aynı model değildir; sürüm değişikliği performansın otomatik olarak iyileştiği anlamına gelmez. BA08'in Liste B dışında tutulması onun bilimsel olarak geçersiz olduğu biçiminde yorumlanmaz.

---

## 4. Girdi parametreleri

| Parametre | Kaynak | Sorun | Öneri |
|---|---|---|---|
| **Mw** | Katalog (`mw` / `mag` + `mtype`) | Son 12 ayda %76 mb; GMPE'ler Mw ister | **Ana hesap yalnız doğrudan Mw verilen olaylarla.** Diğer türler (mb, ML, MD, Ms) yalnız dönüşüm bağıntısı ve bu katalog ile büyüklük aralığı için geçerliliği ayrıca doğrulanırsa **ayrı senaryo** olarak hesaplanır. Bu, EQ-Live'ın mevcut ilkesinin (ML/MD → Mw dönüşümü doğrulanmadan ana akışa alınmaz) mb'ye genişletilmesidir. Dönüştürülmüş Mw ölçülmüş Mw gibi sunulmaz; dönüşüm belirsizliği σ'ya karıştırılmaz, ayrı raporlanır **[karar D1]**. |
| **Uzaklık** (Rjb, Rrup, Rx) | Yalnız dış merkez ve derinlik var | Rjb kırığın yüzey izdüşümüne, Rrup kırık düzlemine en yakın uzaklıktır; Repi ve Rhyp bunların yerine geçmez | **Nokta kaynak temsili** bir yaklaşıklıktır: kaynak tek nokta kabul edilirse tanım gereği Rjb = Repi ve Rrup = Rhyp olur, ama gerçek kırık sonludur ve hata kırık boyutu / uzaklık oranına bağlıdır. NESS 2.1'de Mw 5,5–6,0 kayıtlarında bile Repi − Rjb medyanı 4,2 km, 90. yüzdeliği 10,9 km; Rjb < 20 km kayıtların %27'sinde Repi > 2·Rjb (§13). Bu nedenle sonlu kaynak gereksinimi **yalnız Mw ile değil, kırık boyutu ve saha uzaklığıyla** belirlenir (ör. tahmini kırık uzunluğu L(Mw) ile uzaklığın oranı). Kaynak geometrisi sırası: (a) yayımlanmış sonlu fay modeli (USGS, NESS, AFAD) varsa o; (b) yoksa belgelenmiş senaryo geometrisi: OpenQuake'te büyüklük–alan bağıntısı (Wells & Coppersmith 1994 ya da Leonard 2010) ve düğüm düzlemi dağılımı; geometri belirsizliği ayrı senaryo olarak raporlanır **[karar D4]**. |
| **Fay mekanizması** (rake, dip) | Katalogda yok | GMPE'lerin çoğu fay türü terimi içeriyor | GCMT ya da AFAD moment tensörü varsa kullanılır. Yoksa "belirtilmemiş" seçeneği (BSSA14'te var) ya da bölgesel baskın mekanizma alınır ve epistemik dal olarak gösterilir. |
| **Odak derinliği / ztor** | Katalog `dep` | Katalog derinlikleri belirsiz; 10 km sabit değerleri yaygın | ztor sonlu kırıktan türetilir. Sabit 10 km derinlikli olaylar işaretlenir. |
| **Vs30** | Yok | Haritalı Vs30 vekilleri (topoğrafik eğim) belirsiz | İki kavram ayrı tutulur: (1) **ortak karşılaştırma senaryosu Vs30 = 760 m/s**, bütün modellere aynı girdi; (2) **modelin kendi referans koşulu**, yayımlanmış tanım ve OpenQuake uygulaması (ör. Mindanao B3'te BC Hydro 1000, Kuehn 1100 m/s; aktif kabuk modelleri için model başına çıkarılacak **[teyit]**). İkisi otomatik olarak eşit kabul edilmez; her modelde iki çıktı ayrı denetlenir. İkinci saha senaryosu: vekil Vs30 haritası (USGS küresel mozaik ya da Türkiye'ye özgü harita) **[karar D5]**. Ölçülmüş Vs30'lu istasyonlar ayrı işaretlenir. |
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
- **Kayıtlarla karşılaştırmada üç fark ayrı tutulur:**
  - (a) **uzaklık tanımı farkı**: aynı kaynak için nokta kaynak ve sonlu kırık uzaklıklarının (Repi/Rjb, Rhyp/Rrup) GMPE medyanında yarattığı fark;
  - (b) **sonlu fay geometrisi belirsizliği**: farklı yayımlanmış ya da senaryo geometrileri arasındaki fark (ör. NESS ve USGS segment modelleri);
  - (c) **GMPE artığı**: doğru uzaklık ve girdilerle bile gözlem ile medyan arasında kalan fark (olaylar arası + olay içi).
  - Yalnız (c) modelin performansını ölçer. (a) ve (b) girdi senaryosu farkıdır; birbirinin ya da (c)'nin yerine geçmez. Artık analizinde (c), NESS'in sonlu fay uzaklıklarıyla hesaplanır; (a) ve (b) ayrı duyarlılık olarak raporlanır.
- **Uzamsal yorum uyarısı:** Her ızgara noktasının 84. yüzdeliği ayrı ayrı hesaplanır. Bu nedenle "84. yüzdelik haritası" gerçekleşebilecek tek bir yer hareketi alanı değildir (uzamsal korelasyon yok). Bu uyarı haritada yazılı olmalı.
- **Girdi senaryosu farkı:** Mw kaynağı (doğrudan / dönüştürülmüş), kaynak geometrisi, mekanizma ve Vs30 varsayımlarının etkisi σ'ya eklenmez; her biri duyarlılık senaryosu olarak raporlanır (Mindanao B3 yaklaşımı).
- **Dört gösterim ayrı tutulur (arayüzde de):** (1) medyan, modelin merkezi tahmini; (2) 16.–84. yüzdelik, aleatorik dağılım; (3) modeller arası aralık, epistemik; (4) girdi senaryosu farkı. Bunlar aynı belirsizliğin farklı gösterimleri değildir ve toplanmaz.

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
   - Veri, iki soruyu ayırarak (§13): (i) modeller küresel ve bölgesel kayıtları ne ölçüde açıklıyor: **NESS 2.1** (yakın kaynak, Mw ≥ 5,5, sonlu fay geometrisi ve Rjb/Rrup/Rx/Ry0 hazır) ve **ESM** flat-file'ı (daha geniş büyüklük aralığı, Avrupa–Orta Doğu) **[teyit: ESM sürümü ve sayıları]**; (ii) aynı modeller Türkiye kayıtlarını ne ölçüde açıklıyor: NESS'in Türkiye alt kümesi + AFAD TADAS / SMD-TR **[karar D7]**.
   - Kümeler birleştirilirken aynı olay–istasyon kaydı iki kez sayılmaz (ESM olay kimliği, istasyon ağı ve kodu ile eşleştirme).
   - Olay ve kayıt düzeyindeki örneklem büyüklükleri ayrı raporlanır; aynı depremin çok sayıda kaydı bağımsız olay sayısını yapay olarak artırmaz (olaylar arası / olay içi ayrıştırma bu yüzden zorunlu).
   - Artıklar büyüklük, uzaklık, Vs30 (ölçülmüş / vekil ayrı) ve fay türüne göre ayrıca incelenir.
   - Vs30 kaynağı (ölçülmüş / jeoloji / topoğrafya) yalnız veri tablosunda değil, **her artık tablosunda ve şeklinde** de görünür; zemin terimi sonuçları kaynağa göre ayrı verilir.
   - Bu adım yazılım doğrulaması değil, **model uygunluğu** sınamasıdır.
5. **Raporlama.** Aşama A/B ayrımı korunur: hesaplama doğruluğu ayrı, bilimsel uygunluk ayrı raporlanır.
   - **Yazılım doğrulaması ≠ yöntem doğrulaması.** OpenQuake ile birebir aynı sonucu almak, yalnız denklemin doğru uygulandığını gösterir. Seçilen GMPE'nin Türkiye'ye uygunluğunu ya da girdi senaryosunun (Mw kaynağı, geometri, Vs30) doğruluğunu kanıtlamaz. Bunlar ancak 4. adımdaki kayıtlarla karşılaştırmayla sınanır ve ayrı raporlanır.

## 9. Aşama 3 — EQ-Live entegrasyon ilkeleri (öneri)

- Ayrı dal ve ayrı katman; **varsayılan kapalı**. Mevcut "Hazard" katmanına dokunulmaz (D6 kararına kadar).
- Katman adı örneği: "Tahmini yer hareketi (GMPE, model)". "Hazard", "tehlike" ve "ölçülen" sözcükleri kullanılmaz.
- Her değer için açılır bilgi: model, girdiler (Mw değeri ve kaynağı, uzaklık türü, Vs30 değeri ve kaynağı: ölçülmüş / jeoloji / topoğrafya / senaryo), σ, model aralığı, aralık dışı işareti.
- Yeniden üretim kaydı: Poisson modülündeki gibi JSON; katalog ve yazılım kimlikleri (git blob SHA), model sürümleri ve OpenQuake sürümü.
- Hesap yeri: istemci tarafında JavaScript ya da iş akışında Python + OpenQuake ile önceden hesaplanmış ızgara **[karar D8]**. OpenQuake iş akışı doğrulama açısından güçlü; istemci tarafı etkileşim açısından esnek.

## 10. USGS ShakeMap ile ilişki

ShakeMap, GMPE tahminini istasyon kayıtları ve şiddet raporlarıyla koşullandırır. Bu çalışma koşullandırma yapmaz. Bu nedenle aynı olay için ShakeMap varsa:
- ShakeMap'e bağlantı verilir;
- EQ-Live tahmininin koşullandırılmamış olduğu belirtilir.

## 11. Kararlar: karar, bilimsel gerekçe ve doğrulama durumu

Doğrulama durumu sınıfları:
- **Kabul**: kullanıcı onayladı; yöntem ilkesi olarak geçerli.
- **Koşullu**: ilke kabul, ama bir parametre ya da kaynak henüz doğrulanmadı.
- **Geçici**: çalışma varsayımı; Aşama 2 verisiyle yeniden değerlendirilecek.
- **Açık**: karar verilmedi.

Kabul edilmiş bir ilke ile veri ya da kaynakla henüz doğrulanmamış bir varsayım bu sütunda ayrı tutulur.

| No | Konu | Karar | Bilimsel gerekçe | Doğrulama durumu |
|---|---|---|---|---|
| D1 | Mw kaynağı | Ana hesap yalnız doğrudan Mw. Diğer türler yalnız dönüşümleri doğrulanırsa ve ayrı senaryo olarak. Her olayda Mw değeri ve kaynağı (ajans / yayın) kaydedilir; aynı olay için farklı Mw'ler (ör. Kahramanmaraş 7,7 NESS / 7,8) birbirinin yerine otomatik geçirilmez, gerekirse ayrı senaryo olur. | GMPE'ler Mw ile kalibre edilmiştir; dönüşüm hatası medyanı sistematik kaydırır ve σ'ya karışırsa görünmez olur. EQ-Live'daki ML/MD ilkesiyle tutarlı. | **Kabul** (kullanıcı, 2026-11-02) |
| D2 | Tektonik sınıflama | Üç grup: **≤ 30 km** birincil aktif sığ kabuk karşılaştırma grubu; **30–40 km** "derinlik sınırında", ayrı duyarlılık grubu olarak hesaplanır ve **birincil sonuçlara karıştırılmaz**; **> 40 km** aktif sığ kabuk karşılaştırma kapsamı dışında. ESHM20 aktif sığ kabuk sınıflaması derinlik ölçütünden bağımsız ayrı bir koşul olarak korunur (iki koşul birlikte uygulanır). Sabit katalog derinlikleri (ör. 10 km) işaretlenir. | Akkar vd. (2018) Türkiye alt kümesinde 30 km sınırı (s. 3443); bu sınır tek başına tektonik sınıflamayı belirlemez. | **Kapatıldı — Değişiklik ile kabul** (kullanıcı, 2026-11-02). ESHM20 bölgelendirme dosyası **[teyit]** |
| D3 | Uzaklık sınırı | Ortak karşılaştırma sınırı Rjb ≤ 200 km; dışındaki noktalar ortak karşılaştırmada "kapsam dışı". Her modelin kendi yayımlanmış uzaklık geçerlilik aralığı ayrıca denetlenir. Rjb, Rrup ve Repi birbirinin yerine kullanılmaz: sonlu fay geometrisi yoksa kullanılan uzaklık "nokta kaynak temsili" olarak etiketlenir, Rjb ya da Rrup diye adlandırılmaz. | 200 km ortak veri karşılaştırması için uygun (ASB14, AC10 ve 2018 değerlendirmesi); bütün GMPE'lerin evrensel geçerlilik sınırı değildir. | **Kapatıldı — Koşullu kabul** (kullanıcı, 2026-11-02). Model başına uzaklık aralıkları **[teyit]** |
| D4 | Kaynak geometrisi | Yayımlanmış sonlu fay modeli varsa o; yoksa belgelenmiş senaryo geometrisi. Sonlu kaynak gereksinimi Mw sınıfıyla değil, kırık boyutu, istasyonun kırığa göre konumu (doğrultu boyunca / dik, asılı ya da taban blok) ve uzaklıkla belirlenir. | Repi − Rjb farkı (§13) bir GMPE hatası değil, uzaklık tanımının sonlu kırığı ne ölçüde temsil ettiğinin göstergesidir; GMPE'ye yanlış uzaklık girerse medyan yanlı olur. | **Kabul** (ilke). Eşik ve senaryo geometrisi **Açık**; Aşama 2'de NESS ile belirlenecek |
| D5 | Vs30 | Üç ayrı senaryo: **(1) ortak saha senaryosu Vs30 = 760 m/s** — modelleri ortak girdi koşulunda karşılaştırmak için; **bütün modellerin referans kaya koşulu olarak sunulmaz**; **(2) model referans senaryosu** — her model kendi yayımlanmış referans koşulunda (tablo aşağıda); **(3) vekil Vs30 haritası** — bölgesel saha koşulları. Ölçülmüş / jeoloji / topoğrafya kaynakları ayrı etiketle taşınır. Zh06'ya sürekli Vs30 yaklaşımı zorlanmaz; saha sınıfı eşlemesi açıkça yazılır. | Modellerin referans koşulları 750–1130 m/s arasında değişiyor; Zh06 sınıf tabanlı. | **Kapatıldı — Değişiklik ile kabul** (kullanıcı, 2026-11-02). Referans değerler OpenQuake kodundan; yayın doğrulaması **[teyit]** |
| D6 | Mevcut Campbell (1981) katmanı | Yeni katman Aşama 2 doğrulamasını tamamlayana kadar mevcut Campbell hesabına dokunulmaz; mevcut katman kaldırılmaz ya da değiştirilmez. `hazard-etiket` (6e9ff73) etiket düzeltmeleri yalnız ayrı onayla birleştirilir; bu birleştirmede `seismoreport/` altındaki iki dosya kapsam dışıdır. | Mevcut çalışan referans, yeni katmanın karşılaştırmalı doğrulaması için gerekli. | **Kapatıldı — Kabul** (kullanıcı, 2026-11-02) |
| D7 | Kayıt verisi | NESS 2.1 + ESM + Türkiye için AFAD TADAS / SMD-TR. Olay ve kayıt örneklemi ayrı raporlanır; yinelenen kayıtlar eşleştirilir. | Küresel uyum ile Türkiye'deki uyum iki ayrı soru; NESS yalnız Mw ≥ 5,5. | **Koşullu**: NESS dosyası mevcut ve sayımlar dosyadan doğrulandı. SHA-256 yalnız dosya bütünlüğünü doğrular; NESS sürümü, lisansı ve atıfı ile ESM sürümü ve sayıları **[teyit]** |
| D8 | Hesap yeri | Önce OpenQuake ile bağımsız doğrulama; EQ-Live'daki hesap yeri sonra seçilir. | Referans uygulama önce; yazılım doğrulaması yöntem doğrulamasından ayrı (§8). | **Kabul** |
| D9 | Aday modeller | Liste A (TBDY 2018 temeli: ASB14 0,30, CY08 0,30, AC10 0,30, Zh06 0,10): kayıt amaçlı. Liste B (Aşama 2 aday havuzu: ASB14, AC10, KAAH15, CY14, BSSA14 Yüksek Q, ESHM20): bağımsız sınanacak, ağırlık yok. Karşılaştırma dalı: CY08, Zh06 (2018 tabanı), Campbell (1981) (mevcut katman). Üç sınır §3.1'de. | 2018 ağırlıkları PSHA duyarlılığından seçilmiş, deterministik katmana aktarılmaz. KAAH15 2018'de zamanlama nedeniyle sınanmadı; CY14 ve BSSA14 NGA-West2 ardılları. | **Kapatıldı (kullanıcı, 2026-11-02):** Liste A **Kabul**; Liste B **Koşullu kabul** (aday havuzu); karşılaştırma dalı **Kabul**; KAAH15, CY14, BSSA14, ESHM20 geçerlilik aralıkları **Açık [teyit]** |

**D9 inceleme sırası (uygulandı, revizyon 4; sonuçlar §3.1):**
1. Makalenin gerçekten kullandığı GMPE listesi ve her modelin künyesi.
2. Modellerin merkez, gövde ve aralık (CBR) sınıfları.
3. Mantık ağacı ağırlıkları ve hangi amaçla kullanıldıkları (PSHA, spektral periyot, tektonik bölge).
4. Bu listenin EQ-Live aday listesiyle karşılaştırılması: OpenQuake sınıfı, veri, uzaklık türü, geçerlilik aralığı.
5. Ayrım: "Türkiye'de geçmişte kullanılmış modeller" (kayıt amaçlı) ile "bu çalışmada aday modeller" (Aşama 2'de sınanacak) ayrı listeler olarak yazılır.

2018 listesi ve ağırlıkları EQ-Live'ın nihai model kümesini otomatik olarak belirlemez (D9 gerekçesi).

**D5 — model başına referans saha koşulu (OpenQuake 3.26.2 kaynak kodundan; yayından [teyit]):**

| Model | OpenQuake sınıfı | Referans koşulu |
|---|---|---|
| ASB14 | `AkkarEtAlRjb2014` | Vref = 750 m/s |
| AC10 | `AkkarCagnan2010` | BA08 zemin büyütmesi (Vref = 760 m/s) |
| KAAH15 | `KaleEtAl2015Turkey` | Vref = 750 m/s |
| CY14 | `ChiouYoungs2014` | Referans hız 1130 m/s |
| BSSA14 Yüksek Q | `BooreEtAl2014HighQ` | Vref = 760 m/s |
| ESHM20 | `KothaEtAl2020ESHM20` | 800 m/s'ye göre büyütme |
| CY08 (karşılaştırma) | `ChiouYoungs2008` | Referans hız 1130 m/s |
| Zh06 (karşılaştırma) | `ZhaoEtAl2006Asc` | Saha sınıfları (Vs30 > 1100 m/s sert kaya sınıfı); sürekli Vs30 değil |

Not: Vs30 = 760 m/s girdisi, ASB14 ve KAAH15 için referanstan biraz yüksek, CY14 ve CY08 için düşük bir saha anlamına gelir; Zh06'da 760 m/s bir saha sınıfına eşlenir. Bu nedenle "760 m/s" tüm modellerde aynı fiziksel referans kaya değildir; D5'in (2). maddesi bunun içindir.

**Aşama 2'ye geçiş koşulu (kullanıcı kararı, 2026-11-02):** D9, D2, D3, D5 ve D6 kapatıldı; **yöntemsel geçiş koşulu kapandı.**

**Vazgeçilmez iki koşul (kullanıcı):** (i) D2'de 30–40 km grubu birincil sonuçlara karıştırılmaz; (ii) D5'te 760 m/s evrensel referans kaya olarak sunulmaz.

**Hesap öncesi kalan [teyit] listesi** — her madde, ilgili Aşama 2 hesabından önce birincil yayından kapatılır:

| No | Konu | Gerektiği hesap |
|---|---|---|
| T1 | KAAH15, CY14, BSSA14, ESHM20 geçerlilik aralıkları (Mw, uzaklık, Vs30, periyot) | O modelin her hesabı. **CY14 ve BSSA14 kapatıldı** (aşağıda); KAAH15 ve ESHM20 açık |
| T2 | Model başına referans Vs30 (yayından; şu an OpenQuake kodundan) | D5 senaryo (2) |
| T3 | ESHM20 aktif sığ kabuk bölgelendirme dosyası ve sürümü | D2 sınıflaması |
| T4 | NESS 2.1 sürümü, lisansı, atıfı; ESM sürümü ve sayıları | Kayıt karşılaştırması (§8.4) |
| T5 | Campbell (1981) veri aralığı ve büyüklük ölçekleri | Karşılaştırma dalı |
| T6 | Künye ayrıntıları (AC10 sayfaları, CY08, Zh06, Danciu vd. 2016, Kotha vd. 2020) | Raporlama |

**T1 — kapatılan kısım (Gregor vd. 2014, Earthquake Spectra 30(3):1179–1197, Tablo 1, s. 1180; model geliştiricilerinin ortak karşılaştırma makalesi):**

| Model | Mw (mekanizma) | Uzaklık (km) | Vs30 (m/s) | Periyot |
|---|---|---|---|---|
| BSSA14 | 3,0–8,5 (doğrultu atımlı, ters); 3,3–7,0 (normal) | 0–400 (Rjb) | 150–1500 | PGA–10 s, PGV |
| CY14 | 3,5–8,5 (doğrultu atımlı); 3,5–8,0 (ters, normal) | 0–300 (Rrup) | 180–1500 | PGA–10 s, PGV |

Aynı makale (s. 1182): bölgesel soğrulma düzeltmesinde BSSA14 için "China and Turkey" bölgesi tanımlı (OpenQuake'te `BooreEtAl2014HighQ`); BSSA14'te "belirtilmemiş" faylanma türü parametresi var; CY14'ün İtalya/Japonya düzeltmeleri yalnız Mw 6–6,9 için. Sonuçlar:
- BSSA14 normal faylanmada Mw > 7,0 ekstrapolasyondur (Ege graben sistemi için önemli).
- D3'ün 200 km ortak sınırı her iki modelin aralığı içinde.
- Bu tablo geliştiricilerin özetidir; ayrıntılı ek koşullar (ör. z1.0) her modelin kendi makalesindedir.

## 12. Kaynaklar

- Akkar, S., & Çağnan, Z. (2010). A local ground-motion predictive model for Turkey, and its comparison with other regional and global ground-motion models. *Bulletin of the Seismological Society of America, 100*(6), 2978–2995 **[teyit]**.
- Akkar, S., Sandıkkaya, M. A., & Bommer, J. J. (2014). Empirical ground-motion models for point- and extended-source crustal earthquake scenarios in Europe and the Middle East. *Bulletin of Earthquake Engineering, 12*(1), 359–387.
- Akkar, S., Kale, Ö., Yakut, A., & Çeken, U. (2018). Ground-motion characterization for the probabilistic seismic hazard assessment in Turkey. *Bulletin of Earthquake Engineering, 16*(8), 3439–3463. https://doi.org/10.1007/s10518-017-0101-2
- Boore, D. M., Stewart, J. P., Seyhan, E., & Atkinson, G. M. (2014). NGA-West2 equations for predicting PGA, PGV, and 5% damped PSA for shallow crustal earthquakes. *Earthquake Spectra, 30*(3), 1057–1085.
- Buckreis, T. E., Pretell, R., Sandıkkaya, M. A., Kale, Ö., Askan, A., Brandenberg, S. J., & Stewart, J. P. (2024). Engineering attributes of ground motions from February 2023 Türkiye earthquake sequence. *Earthquake Spectra, 40*(4), 2268–2284. https://doi.org/10.1177/87552930241259024
- Campbell, K. W. (1981). Near-source attenuation of peak horizontal acceleration. *Bulletin of the Seismological Society of America, 71*(6), 2039–2070 **[teyit]**.
- Gregor, N., Abrahamson, N. A., Atkinson, G. M., Boore, D. M., Bozorgnia, Y., Campbell, K. W., Chiou, B. S.-J., Idriss, I. M., Kamai, R., Seyhan, E., Silva, W., Stewart, J. P., & Youngs, R. (2014). Comparison of NGA-West2 GMPEs. *Earthquake Spectra, 30*(3), 1179–1197. https://doi.org/10.1193/070113EQS186M
- Chiou, B. S.-J., & Youngs, R. R. (2008). An NGA model for the average horizontal component of peak ground motion and response spectra. *Earthquake Spectra, 24*(1), 173–215 **[teyit]**.
- Chiou, B. S.-J., & Youngs, R. R. (2014). Update of the Chiou and Youngs NGA model for the average horizontal component of peak ground motion and response spectra. *Earthquake Spectra, 30*(3), 1117–1153.
- Danciu, L., Kale, Ö., & Akkar, S. (2016). The 2014 Earthquake Model of the Middle East: Ground motion model and uncertainties. *Bulletin of Earthquake Engineering* **[teyit: cilt ve sayfa]**.
- Kale, Ö., Akkar, S., Ansari, A., & Hamzehloo, H. (2015). A ground-motion predictive model for Iran and Turkey for horizontal PGA, PGV, and 5% damped response spectrum: Investigation of possible regional effects. *Bulletin of the Seismological Society of America, 105*(2A), 963–980.
- Kotha, S. R., Weatherill, G., Bindi, D., & Cotton, F. (2020). A regionally-adaptable ground-motion model for shallow crustal earthquakes in Europe. *Bulletin of Earthquake Engineering, 18*, 4091–4125 **[teyit]**.
- Mabrouk, A. H. A. S. H. (2024). *Performance of alternative ground motion models with strong-motion data from moderate to large events in different seismotectonic regions in Türkiye* (Yüksek lisans tezi). Orta Doğu Teknik Üniversitesi.
- Scherbaum, F., Delavaud, E., & Riggelsen, C. (2009). Model selection in seismic hazard analysis: An information-theoretic perspective. *Bulletin of the Seismological Society of America, 99*(6), 3234–3247.
- Sharafi, F., Banimahd, S. A., Karimzadeh, S., Askan, A., & Lourenço, P. B. (2026). Objective ground motion model selection and ranking using likelihood and Bayesian criteria: A case study for Türkiye. *GeoHazards, 7*(5), 131. https://doi.org/10.3390/geohazards7050131
- Weatherill, G., Kotha, S. R., & Cotton, F. (2020). A regionally-adaptable "scaled backbone" ground motion logic tree for shallow seismicity in Europe: Application to the 2020 European seismic hazard model. *Bulletin of Earthquake Engineering, 18*, 5087–5117.
- Zhao, J. X., Zhang, J., Asano, A., Ohno, Y., Oouchi, T., Takahashi, T., Ogawa, H., Irikura, K., Thio, H. K., Somerville, P. G., Fukushima, Y., & Fukushima, Y. (2006). Attenuation relations of strong ground motion in Japan using site classification based on predominant period. *Bulletin of the Seismological Society of America, 96*(3), 898–913 **[teyit]**.

Ortam notu: OpenQuake sınıf adları ve gerekli girdiler `openquake.engine 3.26.2` kayıt defterinden (`gsim.base.registry`) 2026-11-02'de okundu.

## 13. NESS 2.1 flat-file: ön inceleme (kullanıcıdaki kopya)

Dosya: `NESS21_2026.zip` (kullanıcının İndirilenler klasörü; depoya kopyalanmadı).
- SHA-256: `25293fe1c59875a9bfc2c297e4bdb2820124a23e62b5ba93f91aa88dbf49628b`.
- İçerik: `NESS21_flat-file_2026.csv` (`;` ayırıcılı, 412 sütun), `readme.txt`, `reference.csv`.
- Sürüm tarihi, lisans ve künye readme'de yazmıyor; NESS sayfasından alınacak **[teyit]**. SHA-256 yalnız dosyanın bütünlüğünü doğrular; sürümü, lisansı ya da atıfı doğrulamaz.

| Özellik | Değer (dosyadan sayıldı) |
|---|---|
| Kayıt / olay | 2297 / 113 |
| Mw | 5,5–8,1 |
| Odak derinliği | 1,4–37,9 km |
| Rjb / Rrup | 0–274 km / 0,09–275 km (sonlu fay geometrisinden; Rx ve Ry0 da var) |
| IM | RotD50 ve RotD100; PGA, PGV, PGD ve %5 sönümlü SA (0,01–10 s; 0,2 ve 1,0 s dahil); fay-paralel ve fay-dik bileşenler |
| Vs30 | `preferred_vs30_m_s` 1671 kayıtta; yöntemi (ölçüm / jeoloji / topoğrafya) ayrı sütunda |
| Episantrı Türkiye'de olan olaylar | 12. Kayıtların çoğu 5 olayda: 1999 İzmit Mw 7,6 (23 kayıt), 1999 Düzce Mw 7,2 (15), 2011 Van Mw 7,1 (8), 2023 Kahramanmaraş Mw 7,7 (120) ve Mw 7,5 (80) |
| 2020 Sisam Mw 7,0 | Ülke kodu GR; 6 kayıt |
| Türkiye'deki istasyonlarda kayıt | 264 |

Notlar:
- NESS'te Kahramanmaraş ana şoku Mw 7,7 (`mw_ref`: Pondrelli vd. veri kümesi); başka kaynaklarda 7,8. 7,7 değeri 7,8'in yerine otomatik geçirilmez: olay kimliği ve Mw kaynağı kaydedilir, gerekirse iki değer ayrı senaryo olur (D1).
- Ana şok üç segmentli sonlu fay modeliyle tanımlı (USGS web servisi; uzunluklar 50,2 / 185,9 / 156,8 km).
- Kahramanmaraş ana şokunun 120 kaydının **hepsinde Vs30 topoğrafyadan** (Wald & Allen 2007) alınmış; ölçülmüş Vs30 yok. Türkiye için saha terimi sonuçları bu nedenle vekil Vs30 belirsizliğini taşır.

**Nokta kaynak yaklaşıklığının büyüklüğü (NESS 2.1, bütün kayıtlar):**

| Mw | Kayıt | Repi − Rjb, medyan / 90. yüzdelik (km) | Rhyp − Rrup, medyan / 90. yüzdelik (km) | Rjb < 20 km kayıtlarda Repi > 2·Rjb oranı |
|---|---|---|---|---|
| 5,5–6,0 | 269 | 4,2 / 10,9 | 5,0 / 24,8 | %27 (n = 244) |
| 6,0–6,5 | 335 | 6,9 / 15,0 | 7,4 / 15,6 | %39 (n = 218) |
| 6,5–7,0 | 635 | 11,0 / 23,8 | 10,7 / 23,7 | %59 (n = 194) |
| 7,0–7,5 | 251 | 12,6 / 38,5 | 13,0 / 39,0 | %69 (n = 62) |
| 7,5–8,1 | 807 | 47,8 / 174,3 | 52,8 / 171,6 | %99 (n = 154) |

Yorum:
- Bu fark bir GMPE hatası değildir. Nokta kaynak uzaklığının sonlu kırık geometrisini ne ölçüde temsil ettiğini gösterir.
- Fark yakın alanda Mw 5,5–6'da bile ihmal edilemez; uzak alanda göreli olarak küçülür. Bu, D4'teki ölçütü destekler.
- Eşik Aşama 2'de yalnız Mw sınıflarına göre değil; kırık boyutu, istasyonun kırığa göre konumu ve uzaklığa göre belirlenir.
- NESS yalnız Mw ≥ 5,5 içerdiğinden daha küçük olaylar için ESM ile tamamlanmalıdır.
