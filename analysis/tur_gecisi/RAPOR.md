# Büyüklük türü geçişi (MD → ML) — araştırma raporu ve uyarı (2026-11-01)

**Dal:** `buyukluk-turu-gecisi`, `main` b41cf49'dan açıldı. `data/`, GK74, a(t), b(t), Mc ve katalog hesapları değişmedi. Ham veri yalnızca okundu. `index.html`'e yalnızca bir **yorum katmanı** eklendi (uyarı metni); hesap değiştirmediği kabul testinde önce/sonra karşılaştırmasıyla doğrulandı (§6).

**Betikler:**
- `disa_aktar.js`: uygulamanın kendi koduyla (bölge, GK74) olay listesini çıkarır. Poisson dalındaki betiğin kopyası; olaylara ham tür dizgisi (`mt`, büyük/küçük harf korunur), enlem ve boylam eklendi. Çıktısı depoya eklenmez.
- `analiz.js` → `sonuc.json`. Kurallar ve sorular betiğin başlığında, sonuçlardan önce yazıldı (tür bileşimi görüldükten sonra; §7).
- `kabul_tur.js`: Playwright kabul testi, 39/39 (§9 güncellemesinden sonra).
- `scripts/test_tur_gecisi.js`: birim testi, 23/23 (§10 kod incelemesinden sonra).
- `esdegerlik_denetimi.js`: kod incelemesi düzeltmelerinin önceki sürümle eşdeğerliği ve süre ölçümü (§10).
- `esik_duyarlilik.js` → `esik_duyarlilik.json`: uyarı eşiklerinin duyarlılığı (§8), uygulamanın kendi koduyla.
- `gorsel_esik.js`: 9 birleşimde tarayıcı görsel regresyonu, 58/58 (§9 güncellemesinden sonra); ekran görüntüleri `gorsel_*.png`.

## 1. Geçiş nerede ve nasıl?

**Türkiye kutusu (36–42° K / 26–45° D), EMSC, M ≥ 3,0, baskın tür payı:**

| Yıl | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 |
|---|---|---|---|---|---|---|
| Baskın tür | MD %84 | MD %81 | MD %82 | **ML %64, MD %30** | ml %95 | ml %95 |

- Nesnel ölçüte göre (baskın tür < %80) Türkiye'de tek geçiş yılı 2011. Marmara'da az olaylı yıllarda (n = 44–103) karışıklık daha sık: 2004, 2009–2011 (ML %21–66) ve 2015 (ml %75, Mw %16).
- **Bu yalnızca bir etiket değişikliği değil.** Marmara dosyasındaki büyüklük yazarı sütunu kaynağın da değiştiğini gösteriyor: 2011'e kadar büyüklükler EMSC adına MD ve ML olarak geliyor (MD/EMSC %80); 2012'den itibaren katkıcıların kendi ML'si (ml/ISK %50, ml/DDA %26, ml/EMSC %19). Tür dizgisinin büyük/küçük harfi de bunu izliyor: "ML" EMSC'nin, "ml" katkıcının.
- **2011 geçişi mekânsal olarak yoğunlaşmış.** 2011'deki "ML" olaylarının boylam medyanı 43,2° D (%63'ü 42° D doğusunda): büyük ölçüde Ekim 2011 Van artçıları. Aynı yıl MD batıda sürüyor (boylam medyanı 35,2° D). Geçiş zamanda temiz bir sınır değil; 2011, iki türün farklı bölgelerde birlikte kullanıldığı bir yıl.
- **Tür seçimi büyüklüğe bağlı.** MD döneminde (2004–2009, GK74) 3,5 ≤ M < 4,0 olayların %70'i MD, ama M ≥ 4,0 olayların yalnızca %10'u MD (mb %69, ML %20). ML döneminde (2013–2018) 3,5–4,0 aralığında ML %91; M ≥ 4,0'da karışık (mb %38, ML %36, Mw %25). Büyük olaylar her iki dönemde de çoğunlukla mb ya da Mw olarak raporlanıyor. **Geçiş asıl olarak M < 4 aralığını etkiliyor.**

## 2. Mc yeniden değerlendirmesi

**Katalog M 3,0'da kesilmiş** (en küçük büyüklük 3,0; histogramın tepesi 3,0'da). Bunun sonucu:
- Uygulamanın en büyük eğrilik yöntemi (MAXC, +0,2) her dönemde **yapı gereği 3,2** veriyor. Bu bir tamlık tahmini değil, kesim sınırının 0,2 üstü.
- GFT (Wiemer & Wyss 2000) %90 ve %95 düzeyinde çoğunlukla ilk aday olan 3,0'ı kabul ediyor.
- MBS (Cao & Gao 2002) MD döneminde 3,8 veriyor, ML döneminde 4,5'e kadar kararlı bir b bulamıyor.

| Türkiye, GK74 | MAXC | GFT90 | GFT95 | MBS |
|---|---|---|---|---|
| MD dönemi 2004–2009 | 3,2 | 3,0 | 3,0 | 3,8 |
| ML dönemi 2013–2018 | 3,2 | 3,0 | 3,0 | — |

**Sonuç:** Gerçek Mc kesim sınırının altında da olabilir; bu veriyle belirlenemiyor. Mc'nin iki dönemde de 3,2 çıkması, dönemlerin tamlığının aynı olduğunu göstermez. Bu yüzden Mc uyarısı tür geçişini yakalayamıyor.

## 3. Ölçek farkı

**Frekans–büyüklük dağılımının biçimi farklı.** Aki b, Türkiye, GK74:

| Eşik | MD dönemi | ML dönemi |
|---|---|---|
| 3,0 | 1,45 ± 0,02 | 0,97 ± 0,02 |
| 3,5 | 1,23 ± 0,04 | 0,97 ± 0,03 |
| 4,0 | 1,03 ± 0,05 | 1,09 ± 0,06 |

- MD döneminin dağılımı **eğri**: b, eşik yükseldikçe 1,45'ten 1,03'e düşüyor. ML döneminin dağılımı **doğrusala yakın** (0,97–1,09). Marmara'da da aynı örüntü var (MD 1,65 → 1,07; ML 1,04 → 1,02; olay sayısı az).
- Eğriliğin iki olası kaynağı var ve bu veriyle ayrılamıyor: (a) MD ölçeğinin ML'ye göre sıkışık olması; (b) büyük MD olaylarının mb ya da ML olarak raporlanması (§1'deki büyüklüğe bağlı tür seçimi).

**Görünür ölçek karşılığı (hız eşleştirmesi).** ML dönemindeki yıllık hız λ(≥M) için MD döneminde aynı hızı veren büyüklük M' bulundu; Δ = M − M'. Sabit kayma varsayılmadı. **Varsayım:** iki dönem arasında gerçek sismisite hızı ve algılama değişmedi. Bu varsayım sınanamaz; sonuç bir ölçek kalibrasyonu değil, görünür bir karşılıktır. Bootstrap %95 aralıkları (2000 çekiliş). Türkiye, GK74:

| ML eşiği | Δ, tüm olaylar (uygulamanın gördüğü katalog) | Δ, yalnız baskın tür (MD ↔ ML) |
|---|---|---|
| 3,3 | −0,20 [−0,22, −0,19] | −0,14 [−0,15, −0,13] |
| 3,5 | −0,11 [−0,14, −0,09] | −0,02 [−0,04, −0,00] |
| 3,7 | −0,05 [−0,09, −0,02] | 0,08 [0,05, 0,10] |
| 3,9 | −0,01 [−0,06, 0,04] | 0,16 [0,13, 0,19] |
| 4,1 | 0,01 [−0,08, 0,08] | 0,20 [0,16, 0,25] |
| 4,3 | −0,02 [−0,11, 0,08] | 0,27 [0,21, 0,32] (n = 24) |
| 4,5 | −0,05 [−0,15, 0,05] | 0,24 [−0,10, 0,40] (n = 4) |

**Okuma:**
- **Uygulamanın gördüğü karışık katalogda** Δ, M ≥ 3,9'da sıfırla uyumlu (aralık ±0,1 içinde). Bu eşiğin altında negatif: aynı nominal eşikte ML döneminde küçük olaylar görece daha az. Fark yalnızca M < 3,9'da.
- **Yalnız baskın türde** Δ eşikle birlikte −0,14'ten +0,27'ye çıkıyor; eğim 0,40 [0,35, 0,45]. Bu, sabit bir kaymayla uyumsuz: iki ölçek arasında bir eğim farkı da var. Ancak bu karşılaştırma büyüklüğe bağlı tür seçiminden etkileniyor (M ≥ 4'te MD olaylarının çoğu başka türle raporlanmış). Bu yüzden MD ↔ ML dönüşüm bağıntısı olarak kullanılmamalı.
- Marmara'da olay sayıları az, aralıklar geniş (çoğu sıfırı içeriyor); örüntü Türkiye ile aynı yönde.

## 4. Zaman serisi sürekliliği

- **M < 3,9'da süreklilik yok.** Varsayılan Mc (3,2) ile 2011–2012'yi kesen b(t), a(t) ve hız serileri ölçek ve tür geçişini de yansıtıyor. Bu, fiziksel bir değişim olarak yorumlanmamalı. Örneğin b, Mc 3,0'da 1,45'ten 0,97'ye düşüyor.
- **M ≥ 3,9'da** karışık katalog, durağan sismisite varsayımı altında geçişin iki yanında hız bakımından tutarlı. Bu, sürekliliğin kanıtı değil; geçişle tutarlı olmayan bir sıçrama bulunmadığı anlamına geliyor. Gerçek bir hız değişimi ile ölçek farkının birbirini dengelemesi de aynı sonucu verir.
- Uyarının önerdiği eşik (baskın tür geçişinin görülmediği en küçük eşik) Türkiye'de baskınlık payına göre M 3,7–4,1 aralığında çıkıyor (varsayılan %60 payında 3,8; §6, §9). Hız eşleştirmesinin bulduğu 3,9 bu aralığın içinde. İki yöntem bağımsız: biri tür etiketlerine, öteki hızlara bakıyor.

## 5. Poisson dönem sınamalarıyla karşılaştırılabilirlik

- Poisson dalındaki ana sınamanın tek tür dönemi içine taşınması (ML 2012–2018 → 2019–, MD 1998–2003 → 2004–2009) doğruydu. Önceden seçilen "karışık" bölünme (1998–2011 → 2012–) geçişi kesiyordu.
- Karışık bölünmede GK74 ile M ≥ 3,2'de oran 0,54, M ≥ 4,0'da 1,18 çıkmıştı (Poisson RAPOR §5). Bu örüntü buradaki bulguyla uyumlu: küçük büyüklüklerde ML döneminde aynı nominal eşikte daha az olay var (Δ < 0); M ≥ 3,9'da fark kayboluyor. M ≥ 4,0'daki 1,18 oranı, Δ'nın ±0,1 belirsizliği içinde kalıyor (10^(0,1·b) ≈ 1,26).
- **Poisson raporunun sonuçları değişmiyor.** Tek tür dönemleri içindeki sınamalar bu geçişten etkilenmiyor. Türler arası karşılaştırmalar M < 3,9'da yorumlanamaz.

## 6. Uyarı (yorum katmanı) ve kabul testi

**Kural** (`turGecisDurum`, `index.html`):
- Analize giren olaylarda (M ≥ Mc ya da basamak eşiği) her takvim yılının baskın büyüklük türü bulunur: yıllık en az 20 olay ve en sık türün payı ≥ %60. Bu koşulu sağlamayan yıllar "karışık" sayılır ve geçiş üretmez.
- Pencere içinde iki farklı baskın tür varsa b(t) panelinde tam uyarı, a(t) panelinde kısa not gösterilir.
- **Önerilen eşik:** baskın tür geçişinin görülmediği en küçük eşik; baskınlık payı %50, %60 ve %70 için ayrı aranır ve **aralık** olarak verilir. Koşullar: yıllık en az 10 olay, en az **5** değerlendirilebilir yıl (asgari raporlama kuralı) ve ilk geçişin iki yanında yıl bulunması. Karışık yıl sayısı metinde verilir. Bu bir tamlık eşiği değildir (§9).
- Metin üç sınırı açıkça söylüyor: aynı baskın tür ölçek eşdeğerliğini kanıtlamaz; etiketi aynı kalan ajans değişimleri (ISC → EMSC) yakalanmaz; Mc uyarısı tür farkını denetlemez.

**Kabul testi** (`kabul_tur.js`, 39/39; önce = `main`, sonra = bu dal; §9 güncellemesinden sonraki sonuçlar):

| Senaryo | Uyarı | Geçiş | Önerilen eşik |
|---|---|---|---|
| Türkiye EMSC 1998– (Mc 3,2) | var | MD → ML (son MD 2010, ilk ML 2011) | M 3,7–4,1 |
| aynı, GK74 | var | MD → ML (2010, 2012; 2011 karışık) | M 3,6–4,1 |
| aynı, Mc 3,5 | var | MD → ML (2005, 2011; 2006–2010 karışık) | M 3,7–4,1 |
| aynı, Mc 4,0 | **yok** (veri yeterli) | — (yıllar mb ya da karışık) | — |
| Marmara EMSC 1998– | var | MD → ML (2008, 2011) | M 3,6 (yalnız %70 payında, 17 yıl) |
| Marmara, GK74 | var | MD → ML (2008, 2012) | M 3,6 (yalnız %70 payında, 11 yıl) |
| Marmara, GK74, Mc 4,0 | **değerlendirilemedi** (27 / 27 yıl yetersiz) | — | — |
| ISC 1971–1997 + EMSC 1998– | var | mb → ML → MD (1989–1995; ISC'de 1990'larda ML ve MD türlü olaylar, kaynağı incelenmedi), MD → ML (2010, 2011) | M 3,9–4,1 |
| aynı, basamaklar 1971 M 4,5 / 1998 M 3,5 | var | mb → MD (1991, 1998), MD → ML (2005, 2011) | M 3,9 (yalnız %70) |
| ISC 1971–1997 (Mc 3,7) | yok (veri yeterli) | — (1990–1997 karışık) | — |
| Kahramanmaraş 1998– | var | MD → ML (2010, 2012) | M 3,8–3,9 |

**Denetimler:**
1. Tüm senaryolarda b(t) ve a(t) grafikleri, uyarılar dışındaki b(t)/a(t) metinleri ve G–R metni önce ile sonra arasında birebir aynı; hesap değişmedi.
2. Mc uyarısı önce ile sonra arasında birebir aynı.
3. Tür uyarısı b(t) ve a(t) panellerinde tutarlı; `main`'de yok.
4. Türkiye'de MD → ML geçişi algılanıyor.
5. Sayfa hatası yok.

Ekran görüntüsü: `tur_uyari_emsc98.png`.

**Birim testi** (`scripts/test_tur_gecisi.js`, 21/21): tür adlarının birleştirilmesi, geçiş ve karışık yıl, az olaylı yılların yok sayılması, A → B → A, önerilen eşik (karışık yıllar, iki yan şartı), metin (tam / kısa / boş).

## 7. Sınırlar

- **Sonradan seçim.** Tür dönemleri (MD 2004–2009, ML 2013–2018) ve uyarının eşikleri (%60, 20 olay) tür bileşimi görüldükten sonra seçildi; ölçek ve Mc sonuçları görülmeden önce. Eşikler duyarlılık analiziyle denenmedi.
- **Hız eşleştirmesi** durağan sismisite ve algılama varsayımına dayanıyor; bir ölçek kalibrasyonu değil. Aynı olayın hem MD hem ML değeri katalogda yok, bu yüzden doğrudan (eşli olay) karşılaştırma yapılamadı. Eşli olaylarla bir MD–ML bağıntısı, KOERI/AFAD kaynaklı ayrı bir veri gerektirir.
- **Mc** kesim sınırının altında belirlenemiyor. Uyarı bunu çözmüyor, yalnızca tür değişimini işaret ediyor.
- **Uyarı yalnızca etiketlere bakıyor.** Aynı etiketle ajans ya da hesap yöntemi değişirse (ör. ISC mb → EMSC mb, ya da 2011'de EMSC "ML" → 2012'de katkıcı "ml") uyarı vermez. İkincisi `turNorm`'da bilinçli olarak tek tür sayıldı. Büyük/küçük harf ayrımı yapılsaydı 2011–2012'de ek bir geçiş görünürdü; bunun ölçek farkı yaratıp yaratmadığı ayrıca incelenmedi.
- **GK74 ve katalog yapısı** korunuyor: uyarı yalnızca analize giren olay listesini okuyor.

## 8. Eşik duyarlılığı (sonradan eklendi)

> **Not:** Bu bölümdeki **öneri** sütunları ve "uyarı yok" satırları §9'daki değişiklikten **önceki** koda aittir (tek değerli öneri, en az 3 yıl, değerlendirilemedi notu yok). Geçiş algılama sonuçları (geçiş yılları, karışık yıllar) değişmedi. Güncel sonuçlar §9'da ve `esik_duyarlilik.json`'da.

Uyarının iki eşiği (baskın tür payı ve yıllık en az olay) 3 × 3 birleşimle denendi: pay %50 / %60 / %70, yıllık olay 10 / 20 / 30. Önerilen eşik için yıllık en az olay (minNOner = 10) sabit tutuldu; ayrıca minNOner = minN ile de hesaplandı. Hesap uygulamanın kendi koduyla (`turGecisDurum`, `index.html`'den) yapıldı. Varsayılan birleşimin (%60 / 20) sonuçları, beş senaryonun hepsinde tarayıcıdaki kabul testiyle birebir aynı. Tam sonuçlar `esik_duyarlilik.json`'da.

**Kavram ayrımı.** Bu analiz yalnızca **büyüklük türü etiketinin** değişip değişmediğine bakıyor. **Tamlık (Mc) değişimi** hakkında bilgi vermez; tür değişimi tamlığın değiştiğini, tür sürekliliği de tamlığın değişmediğini göstermez. Uyarının önerdiği eşik bir tamlık eşiği değil, **tür etiketinin yıldan yıla homojen göründüğü** en küçük eşiktir. Bu katalogda Mc ayrıca belirlenemiyor (§2).

### 8.1 Türkiye (EMSC 1998–)

| Pay / yıllık olay | Ham, Mc 3,2: geçiş (son MD → ilk ML) | GK74, Mc 3,2 | Ham, Mc 3,5 | Önerilen eşik (üçünde) |
|---|---|---|---|---|
| %50 / 10, 20, 30 | 2010 → 2011 | 2010 → 2011 | 2007 → 2010 | M 4,1 |
| **%60 / 10, 20, 30** (varsayılan 20) | **2010 → 2011** | **2010 → 2012** (2011 karışık) | **2005 → 2011** | **M 3,8** |
| %70 / 10, 20, 30 | 2009 → 2011 | 2009 → 2012 | 2004 → 2011 | M 3,7 (GK74: 3,6) |

- **Uyarı 27 birleşimin hepsinde oluşuyor.** Geçiş algısı eşiklere dayanıklı.
- **Yıllık olay eşiğinin etkisi yok:** her yıl 30'dan fazla olay var (29 yılın hiçbiri yetersiz değil).
- **Pay eşiği geçiş yılını en çok 1 yıl, Mc 3,5'te 3 yıl kaydırıyor.** Mc 3,5'te 2005–2010 arasında hiçbir türün payı %70'e ulaşmıyor; bu yıllar seçilen paya göre MD, ML ya da "karışık" sayılıyor. Geçişin kendisi kayan değil, kademeli (§1).
- **Önerilen eşik paya duyarlı: M 3,6–4,1.** Daha katı pay daha fazla yılı "karışık" yapıyor; karışık yıllar geçiş sayılmadığı için öneri düşüyor. Hız eşleştirmesinin bulduğu M ≈ 3,9 (§3) bu aralığın içinde. Önerilen eşik **tek bir değer olarak değil, yaklaşık bir aralık olarak** okunmalı.

### 8.2 Marmara (EMSC 1998–)

| Pay / yıllık olay | Ham: geçiş | Ham: öneri | GK74: geçiş | GK74: öneri | GK74: değerlendirilen yıl (29 yıldan) |
|---|---|---|---|---|---|
| %50 / 10 | 2009 → 2011 | — | 2009 → 2011 | — | 26 |
| %50 / 20 | 2009 → 2011 | — | 2009 → 2012 | — | 17 |
| %50 / 30 | 2009 → 2013 | — | **uyarı yok** | — | 6 |
| %60 / 10 | 2008 → 2011 | M 3,9 (4 yıl) | 2008 → 2011 | — | 26 |
| **%60 / 20** | **2008 → 2011** | **M 3,9 (4 yıl)** | **2008 → 2012** | **—** | **17** |
| %60 / 30 | 2008 → 2013 | M 3,9 (4 yıl) | **uyarı yok** | — | 6 |
| %70 / 10 | 2007 → 2011 | M 3,6 (17 yıl) | 2007 → 2012 | M 3,6 (11 yıl) | 26 |
| %70 / 20 | 2007 → 2011 | M 3,6 | 2007 → 2012 | M 3,6 | 17 |
| %70 / 30 | 2005 → 2013 | M 3,6 | **uyarı yok** | — | 6 |

- **Ham katalogda uyarı 9 birleşimin hepsinde oluşuyor.** GK74 ile 6 birleşimde; yıllık 30 olay şartında yalnızca 6 yıl değerlendirilebildiği için uyarı çıkmıyor. **Bu durumda uyarının olmaması geçişin olmadığını değil, verinin yetersiz olduğunu gösterir.** Şu anki arayüz bu iki durumu ayırt etmiyor.
- **Öneri kararsız.** Varsayılanda (ham) yalnızca 4 yıla dayanıyor. Ayrıca monoton davranmıyor: GK74, %60 / 20'de minNOner 10 iken öneri yok, minNOner 20 iken M 3,3. Daha az yıl değerlendirildiğinde iki yan şartı daha kolay sağlanıyor. Küçük kataloglarda önerilen eşik güvenilir değil.

### 8.3 Varsayılana göre değişim ve görsel regresyon

- **Türkiye:** Geçiş algısı ve yönü (MD → ML) her birleşimde aynı. Geçiş yılları ±1 yıl (Mc 3,5'te ±3 yıl), önerilen eşik ±0,2–0,3 oynuyor.
- **Marmara:** Ham katalogda geçiş algısı dayanıklı. GK74 ile yıllık 30 olayda uyarı kayboluyor; öneri çoğu birleşimde yok ya da az yıla dayanıyor.
- **Görsel regresyon** (`gorsel_esik.js`, 55/55): 9 birleşimin hepsinde (Türkiye ham, Marmara GK74) b(t), a(t) grafikleri, uyarılar dışındaki metinler, G–R metni ve Mc uyarısı `main` ile birebir aynı. Eşikler yalnızca tür uyarısını etkiliyor. Tarayıcıdaki uyarı durumu Node hesabıyla aynı; b(t) ve a(t) uyarıları tutarlı; sayfa hatası yok. Ekran görüntüleri: `gorsel_tr_{50_10, 60_20, 70_30}.png`, `gorsel_mar_gk74_{…}.png`.

### 8.4 Öneriler (uygulanmadı; karar bekliyor)

1. **Önerilen eşiği aralık olarak göster.** Tek bir değer yerine %50–70 paylarındaki önerilerin aralığını ver (Türkiye: "≈ M 3,7–4,1"). Metne "bu bir tamlık eşiği değildir" ifadesini ekle.
2. **Öneri için en az 5 değerlendirilebilir yıl şartı koy** (şu an 3). Marmara'daki 4 yıllık öneriler bu şartla kalkar.
3. **"Veri yetersiz" durumunu göster.** Yılların yarıdan fazlası yıllık olay eşiğinin altındaysa, uyarı yerine "tür geçişi değerlendirilemedi (n yıl yetersiz)" notu ver. Böylece uyarının olmaması "geçiş yok" diye okunmaz.
4. **Varsayılanları (%60 / 20) koru.** Türkiye'de sonuçlar bu ayarda kararlı; değiştirmek için bir gerekçe bulunmadı.

## 9. Uygulanan değişiklikler: öneri aralığı, 5 yıl kuralı, "değerlendirilemedi" (2026-11-01)

§8.4'teki dört öneri uygulandı. Yalnızca uyarı metni ve öneri kuralı değişti; geçiş algılama kuralı ve varsayılan eşikler (%60 / 20) aynı.

| Öneri | Uygulama (`index.html`, `TUR_QC` ve `turGecisDurum` / `turUyariHtml`) |
|---|---|
| 1. Önerilen eşik aralık olarak | Öneri her baskınlık payı için (`payAralik` = %50, %60, %70) ayrı aranır; metin "≈ M alt–üst (%50: …; %60: …; %70: …)" biçiminde. Bulunamayan paylar "bulunamadı" olarak yazılır. Metinde: "Bu bir tamlık (Mc) eşiği değildir; yalnızca tür etiketinin yıldan yıla homojen göründüğü eşiktir." |
| 2. En az 5 yıl | `minYilOner = 5` (önceden 3). Metinde: "bu bir asgari raporlama kuralıdır, istatistiksel güvenilirlik ölçütü değildir." |
| 3. Değerlendirilemedi | Geçiş bulunmadığında, pencerenin takvim yıllarının yarıdan fazlası (`yetersizOran` = 0,5; olaysız yıllar da yetersiz sayılır) yıllık `minN` olay koşulunu sağlamıyorsa ya da 2'den az yıl değerlendirilebiliyorsa "uyarı yok" yerine gri bir **"değerlendirilemedi"** notu gösterilir (b(t)'de tam, a(t)'de kısa): "Uyarının olmaması, büyüklük türü geçişi olmadığı anlamına gelmez." "Uyarı yok" yalnızca veri yeterliyken oluşur. Geçiş bulunduğunda bazı yıllar yetersizse uyarı metnine "değerlendirilen yıl n / N" eklenir. |
| 4. Varsayılanlar | `minN = 20`, `pay = 0,6` korundu. |

**Seçimlerin gerekçesi ve sınırı.** %50 yetersiz yıl oranı ve 5 yıl şartı, aşırı az gözleme dayanan sonuçları göstermemek için seçilmiş **asgari raporlama kurallarıdır**; istatistiksel bir güvenilirlik ölçütü ya da sınanmış bir eşik değildir. Geçiş bulunduğunda (pozitif bulgu) uyarı, yetersiz yıl oranından bağımsız olarak gösterilir.

**Güncel sonuçlar:**
- **Türkiye:** öneri ham M 3,7–4,1, GK74 M 3,6–4,1, Mc 3,5'te M 3,7–4,1 (%50: 4,1; %60: 3,8; %70: 3,6–3,7; her biri 29 yıl). Hız eşleştirmesinin bulduğu M ≈ 3,9 (§3) aralığın içinde.
- **Marmara:** 4 yıla dayanan M 3,9 önerisi 5 yıl kuralıyla kalktı. Yalnızca %70 payında M 3,6 kalıyor (ham 17 yıl, GK74 11 yıl); %50 ve %60'ta "bulunamadı". GK74 ile yıllık 30 olay şartında (23 / 29 yıl yetersiz) ve GK74 + Mc 4,0'da (27 / 27 yıl yetersiz) artık "değerlendirilemedi" notu gösteriliyor; önceki sürümde bu durumlar sessizce "uyarı yok" idi.
- **Duyarlılık notu:** Öneri için yıllık olay şartı (minNOner) 10 yerine minN'e eşitlenirse Marmara GK74'te öneri M 3,3'e iniyor (%50–70 / 20). Küçük kataloglarda öneri, değerlendirilebilir yıl kümesine duyarlı kalıyor; aralık gösterimi ve 5 yıl şartı bunu azaltıyor, ortadan kaldırmıyor.

**Doğrulama** (değişiklik sonrası, hepsi `main` ile karşılaştırmalı):

| Denetim | Sonuç |
|---|---|
| Birim testi (`scripts/test_tur_gecisi.js`): aralık, paya duyarlı aralık (M 3,5–4,1), 5 yıl kuralı, değerlendirilemedi (oran > %50, tam %50 sınırı, tek yıl, olay yok), "değerlendirilen yıl n / N", metin ifadeleri | 21/21 |
| Kabul testi (`kabul_tur.js`, 11 senaryo): b(t), a(t), G–R ve Mc uyarısı önce = sonra; b(t) ve a(t) notları tutarlı; "uyarı yok" yalnızca veri yeterliyken; her öneri ≥ 5 yıla dayanıyor; seyrek Marmara'da "değerlendirilemedi" | 39/39 |
| Eşik duyarlılığı (`esik_duyarlilik.js`): 5 senaryo × 9 birleşim; varsayılan birleşim tarayıcı kabul testiyle aynı (5/5) | yeniden üretildi |
| Görsel regresyon (`gorsel_esik.js`): 9 birleşim × 2 senaryo; b(t), a(t), G–R ve Mc uyarısı her birleşimde `main` ile aynı; tarayıcı = Node; Marmara GK74 yıllık 30 olayda "değerlendirilemedi" notu | 58/58 |
| Tüm birim testleri (`scripts/test_*.js`, 17 dosya) | 17/17, hata yok |

Ekran görüntüleri: `tur_uyari_emsc98.png` (varsayılan), `gorsel_tr_{50_10, 60_20, 70_30}.png`, `gorsel_mar_gk74_{50_10, 60_20, 70_30}.png` (70_30: "değerlendirilemedi" notu).

## 10. Birleştirme öncesi kod incelemesi (2026-11-01)

Dalın `index.html` farkı (`main`'e göre) satır satır incelendi. Değişiklik üç noktada mevcut koda dokunuyor; üçü de yalnızca **okuma ve metin ekleme**:
- `renderBvalueTS`: analize giren olaylardan **yeni nesneler** üretilir (`turOl`); `evList`, `cs.kept` ve olay nesneleri değiştirilmez. Uyarı durumu `lastTurUyari`'ye yazılır.
- b(t) istatistik metni: Mc uyarısından sonra tür uyarısı **eklenir**; mevcut metin aynı.
- a(t) istatistik metni: kısa not **eklenir**; mevcut metin aynı.

b(t), a(t), G–R, Mc ya da GK74 hesaplarına giden hiçbir değişken değiştirilmiyor. Kabul ve görsel testlerdeki önce/sonra eşitliği bunu doğruluyor.

**Bulunan ve düzeltilen sorunlar:**

| Sorun | Etki | Düzeltme | Doğrulama |
|---|---|---|---|
| `Math.max(...yıllar)`: tüm olayların yılları argüman olarak açılıyordu | Çok büyük pencerelerde yığın taşması. Node'da 367 704 olayda "Maximum call stack size exceeded"; tarayıcıda sınır daha düşük olabilir. Hata b(t) panelinin istatistik metnini düşürürdü. | En küçük ve en büyük yıl döngüyle | 369 000 olaylı birim testi hatasız |
| Hata yalıtımı yoktu | Yorum katmanındaki herhangi bir hata ana paneli etkileyebilirdi | Hesap ve metin `try/catch` içinde (`turUyariHtmlG`); hata olursa uyarı düşer, konsola yazılır, panel çizilir | Bozuk girdide boş metin (birim testi) |
| Öneri araması 3 pay × 20 eşikte listeyi yeniden süzüyor, her olay için her seferinde `Date` oluşturuyordu | Her b(t) çiziminde ~0,3 s ek gecikme (Türkiye ISC + EMSC, 30 bin olay) | Yıl ve tür olay başına bir kez; eşikler büyüklüğe göre sıralı tek taramayla | 108 durumun hepsinde önceki sürümle **birebir aynı** sonuç; toplam süre 6,5 s → 1,2 s (5,7×) |

**Sınıflandırmanın denetimi (değerlendirilemedi / uyarı yok / uyarı):** Birim testleri dört durumu kapsıyor: oran %50'nin üstünde, tam %50 sınırı, tek değerlendirilebilir yıl ve olay yok. Kabul testi gerçek veride "uyarı yok" sonucunun yalnızca veri yeterliyken oluştuğunu denetliyor (11 senaryo). Görsel test, Marmara GK74'te yıllık 30 olay şartında notun göründüğünü doğruluyor.

**Kurallar hakkında:** %50 yetersiz yıl oranı ve 5 yıl şartı **raporlama kurallarıdır**, doğrulanmış istatistiksel eşikler değil (§9). Arayüz metni 5 yıl şartını bu biçimde tanımlıyor ("asgari raporlama kuralıdır, istatistiksel güvenilirlik ölçütü değildir"). Uyarı bilimsel bir güvenilirlik güvencesi sunmuyor.

**Güncel `main` ile:** Dal, Poisson birleştirmesinden sonraki güncel `main`'i (f8c9c20) içine aldı; çakışma olmadı. Tüm testler bunun üzerinde yeniden koşturuldu:

| Denetim | Sonuç |
|---|---|
| Birim testi (`scripts/test_tur_gecisi.js`) | 23/23 |
| Tüm birim testleri (`scripts/test_*.js`, 17 dosya) | 17/17 |
| Kabul testi (`kabul_tur.js`; önce = güncel `main`) | 39/39 |
| Eşik duyarlılığı: varsayılan birleşim = tarayıcı | 5/5 |
| Görsel regresyon (`gorsel_esik.js`) | 58/58 |
| Eşdeğerlik (`esdegerlik_denetimi.js`), önceki sürüm b8a6f81 ile | 108/108 aynı |
| `data/` | `main` ile aynı |

**Yayın notu:** GitHub Pages `main`'den yayın yapıyor. Bu dalın `main`'e birleştirilmesi, uyarının canlı sitede hemen görünmesi demek; birleştirme ile yayın ayrı adımlar değil.

