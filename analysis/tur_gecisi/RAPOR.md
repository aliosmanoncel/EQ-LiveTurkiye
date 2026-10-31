# Büyüklük türü geçişi (MD → ML) — araştırma raporu ve uyarı (2026-11-01)

**Dal:** `buyukluk-turu-gecisi`, `main` b41cf49'dan açıldı. `data/`, GK74, a(t), b(t), Mc ve katalog hesapları değişmedi. Ham veri yalnızca okundu. `index.html`'e yalnızca bir **yorum katmanı** eklendi (uyarı metni); hesap değiştirmediği kabul testinde önce/sonra karşılaştırmasıyla doğrulandı (§6).

**Betikler:**
- `disa_aktar.js`: uygulamanın kendi koduyla (bölge, GK74) olay listesini çıkarır. Poisson dalındaki betiğin kopyası; olaylara ham tür dizgisi (`mt`, büyük/küçük harf korunur), enlem ve boylam eklendi. Çıktısı depoya eklenmez.
- `analiz.js` → `sonuc.json`. Kurallar ve sorular betiğin başlığında, sonuçlardan önce yazıldı (tür bileşimi görüldükten sonra; §7).
- `kabul_tur.js`: Playwright kabul testi, 33/33.
- `scripts/test_tur_gecisi.js`: birim testi, 14/14.

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
- Uyarının önerdiği eşik (baskın tür geçişinin görülmediği en küçük eşik) Türkiye'de M 3,8 çıkıyor (§6). Bu, hız eşleştirmesinin bulduğu 3,9 ile tutarlı. İki yöntem bağımsız: biri tür etiketlerine, öteki hızlara bakıyor.

## 5. Poisson dönem sınamalarıyla karşılaştırılabilirlik

- Poisson dalındaki ana sınamanın tek tür dönemi içine taşınması (ML 2012–2018 → 2019–, MD 1998–2003 → 2004–2009) doğruydu. Önceden seçilen "karışık" bölünme (1998–2011 → 2012–) geçişi kesiyordu.
- Karışık bölünmede GK74 ile M ≥ 3,2'de oran 0,54, M ≥ 4,0'da 1,18 çıkmıştı (Poisson RAPOR §5). Bu örüntü buradaki bulguyla uyumlu: küçük büyüklüklerde ML döneminde aynı nominal eşikte daha az olay var (Δ < 0); M ≥ 3,9'da fark kayboluyor. M ≥ 4,0'daki 1,18 oranı, Δ'nın ±0,1 belirsizliği içinde kalıyor (10^(0,1·b) ≈ 1,26).
- **Poisson raporunun sonuçları değişmiyor.** Tek tür dönemleri içindeki sınamalar bu geçişten etkilenmiyor. Türler arası karşılaştırmalar M < 3,9'da yorumlanamaz.

## 6. Uyarı (yorum katmanı) ve kabul testi

**Kural** (`turGecisDurum`, `index.html`):
- Analize giren olaylarda (M ≥ Mc ya da basamak eşiği) her takvim yılının baskın büyüklük türü bulunur: yıllık en az 20 olay ve en sık türün payı ≥ %60. Bu koşulu sağlamayan yıllar "karışık" sayılır ve geçiş üretmez.
- Pencere içinde iki farklı baskın tür varsa b(t) panelinde tam uyarı, a(t) panelinde kısa not gösterilir.
- **Önerilen eşik:** baskın tür geçişinin görülmediği en küçük eşik. Koşullar: yıllık en az 10 olay, en az 3 değerlendirilebilir yıl ve ilk geçişin iki yanında yıl bulunması. Karışık yıl sayısı metinde verilir.
- Metin üç sınırı açıkça söylüyor: aynı baskın tür ölçek eşdeğerliğini kanıtlamaz; etiketi aynı kalan ajans değişimleri (ISC → EMSC) yakalanmaz; Mc uyarısı tür farkını denetlemez.

**Kabul testi** (`kabul_tur.js`, 33/33; önce = `main`, sonra = bu dal):

| Senaryo | Uyarı | Geçiş | Önerilen eşik |
|---|---|---|---|
| Türkiye EMSC 1998– (Mc 3,2) | var | MD → ML (son MD 2010, ilk ML 2011) | M 3,8 |
| aynı, GK74 | var | MD → ML (2010, 2012; 2011 karışık) | M 3,8 |
| aynı, Mc 3,5 | var | MD → ML (2005, 2011; 2006–2010 karışık) | M 3,8 |
| aynı, Mc 4,0 | **yok** | — (yıllar mb ya da karışık) | — |
| Marmara EMSC 1998– | var | MD → ML (2008, 2011) | M 3,9 (4 yıl) |
| Marmara, GK74 | var | MD → ML (2008, 2012) | — |
| ISC 1971–1997 + EMSC 1998– | var | mb → ML → MD (1989–1995; ISC'de 1990'larda ML ve MD türlü olaylar, kaynağı incelenmedi), MD → ML (2010, 2011) | M 4,0 |
| aynı, basamaklar 1971 M 4,5 / 1998 M 3,5 | var | mb → MD (1991, 1998), MD → ML (2005, 2011) | — |
| ISC 1971–1997 (Mc 3,7) | yok | — (1990–1997 karışık) | — |
| Kahramanmaraş 1998– | var | MD → ML (2010, 2012) | M 3,9 |

**Denetimler:**
1. Tüm senaryolarda b(t) ve a(t) grafikleri, uyarılar dışındaki b(t)/a(t) metinleri ve G–R metni önce ile sonra arasında birebir aynı; hesap değişmedi.
2. Mc uyarısı önce ile sonra arasında birebir aynı.
3. Tür uyarısı b(t) ve a(t) panellerinde tutarlı; `main`'de yok.
4. Türkiye'de MD → ML geçişi algılanıyor.
5. Sayfa hatası yok.

Ekran görüntüsü: `tur_uyari_emsc98.png`.

**Birim testi** (`scripts/test_tur_gecisi.js`, 14/14): tür adlarının birleştirilmesi, geçiş ve karışık yıl, az olaylı yılların yok sayılması, A → B → A, önerilen eşik (karışık yıllar, iki yan şartı), metin (tam / kısa / boş).

## 7. Sınırlar

- **Sonradan seçim.** Tür dönemleri (MD 2004–2009, ML 2013–2018) ve uyarının eşikleri (%60, 20 olay) tür bileşimi görüldükten sonra seçildi; ölçek ve Mc sonuçları görülmeden önce. Eşikler duyarlılık analiziyle denenmedi.
- **Hız eşleştirmesi** durağan sismisite ve algılama varsayımına dayanıyor; bir ölçek kalibrasyonu değil. Aynı olayın hem MD hem ML değeri katalogda yok, bu yüzden doğrudan (eşli olay) karşılaştırma yapılamadı. Eşli olaylarla bir MD–ML bağıntısı, KOERI/AFAD kaynaklı ayrı bir veri gerektirir.
- **Mc** kesim sınırının altında belirlenemiyor. Uyarı bunu çözmüyor, yalnızca tür değişimini işaret ediyor.
- **Uyarı yalnızca etiketlere bakıyor.** Aynı etiketle ajans ya da hesap yöntemi değişirse (ör. ISC mb → EMSC mb, ya da 2011'de EMSC "ML" → 2012'de katkıcı "ml") uyarı vermez. İkincisi `turNorm`'da bilinçli olarak tek tür sayıldı. Büyük/küçük harf ayrımı yapılsaydı 2011–2012'de ek bir geçiş görünürdü; bunun ölçek farkı yaratıp yaratmadığı ayrıca incelenmedi.
- **GK74 ve katalog yapısı** korunuyor: uyarı yalnızca analize giren olay listesini okuyor.
