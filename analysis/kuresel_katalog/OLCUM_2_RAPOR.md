# Küresel katalog — Ölçüm 2 raporu: ISC-GEM v12.1 ve USGS ComCat (2026-10-26)

**Kapsam:** Yalnız birleştirme için gereken teknik kontroller (ChatGPT ile uzlaşılan sınır). Katalog tamlığı, 1964–1970 dönemi ve bölgesel ağlar ayrıca araştırılmadı; bunlar için ISC-GEM belgesi ve literatür esas alınır. Kod, canlı site, `main` ve Türkiye kataloğu değişmedi.
**Kurallar:** `OLCUM_2_ONKAYIT.md`, sonuçlardan önce kaydedildi (commit `2b60e75`). Ek 1 yalnız çıktı ekledi; kurallar değişmedi.
**Çalıştırma:** GitHub Actions 40349462053 (aynı veriyle 40348075491). Sonuç dosyası `out/olcum2_sonuc.json`.

## 1. ISC-GEM çıkarımının doğrulaması

- **Kaynak bütünlüğü:** Zip ve iki CSV'nin SHA-256 değerleri 2026-10-21 kaydıyla aynı.
- **Ana katalog:** 74 159 olay, 1904-04-04 – 2021-12-31.
  - Zorunlu alanlarda (zaman, enlem, boylam, Mw, olay kimliği) eksik yok; diğer alanlarda da eksik yok.
  - Geçersiz değer yok; kimlik ve zaman+konum tekrarı yok; zamana göre sıralı.
  - İlk ve son satırlar ham CSV ile aynı.
- **Ek katalog:** 9 834 olay; %61'inde (6 046) Mw yok. Ayrı dosyada, varsayılan olarak hiçbir analize girmiyor.
- **Yeniden üretilebilirlik:** `iscgem_cikar.py` aynı girdiyle bayt bayt aynı çıktıyı üretiyor (`out/iscgem_v12.1_ana.json.gz`, 1,84 MB). Ham dosyalar depoda değil.

## 2. USGS verisi

- **Sorgu:** 2026-10-26 15:27–15:34 UTC; 1904–2021, küresel, M ≥ 4,0; 118 yıllık parça.
- **Sonuç:** 474 109 olay; her parçada sayım ile indirilen sayı aynı (kayıp yok).
- **Olay türleri:** 811 nükleer patlama ve az sayıda başka tür içeriyor. Birleştirmede `type = earthquake` dışındakiler ayıklanmalı.

## 3. USGS kayıtlarının kökeni (örtüşmeden önce)

`net` ve `ids` alanları her kayıtta mevcut; köken bilgisi tahmin gerektirmeden elde edildi.

| Dönem | USGS olay | Tercihli kaynak ISC-GEM (`iscgem`/`iscgemsup`) | `ids` içinde ISC-GEM | ISC-GEM katkısı görünmeyen |
|---|---|---|---|---|
| 1904–1970 | 17 868 | 15 049 (%84) | 122 | 2 697 |
| 1971–1997 | 145 410 | 1 936 | 24 167 | 119 307 |
| 1998–2021 | 310 831 | 213 | 36 668 | 273 950 |

**Sonuç:** USGS'nin 1904–1970 kayıtları büyük ölçüde ISC-GEM'in kendisi. Bu dönemde bir ISC-GEM olayına eşleşme olarak seçilen USGS kayıtları:
- `tekil`: 13 108 tercihli, 51 katkılı;
- `karsilikli_cok_adayli`: 425 tercihli, 23 katkılı.

Hiçbiri "ISC-GEM katkısı görünmeyen" sınıfında değil. Bu sınıftaki 2 697 kaydın 2 613'ü "yalnız USGS"; kalan 84'ü pencerede aday olmuş ama seçilmemiş kayıtlar (ağırlıkla bölgesel ağ kayıtları). 1971 sonrasında katkısı görünmeyen seçilmiş eşleşme yalnız 8 (1971–1997) ve 12 (1998–2021). Bu nedenle iki katalog arasındaki yüksek örtüşme bağımsız bir doğrulama değildir; aynı kaydın iki kopyasının karşılaştırılmasıdır.

## 4. Eşleştirme sonuçları (zaman + uzaklık; büyüklük kullanılmadı)

| Dönem | ISC-GEM | `tekil` | `karsilikli_cok_adayli` | `belirsiz` | `yalniz_iscgem` |
|---|---|---|---|---|---|
| 1904–1970 | 13 609 | 13 159 (%96,7) | 448 | 0 | 2 |
| 1971–1997 | 23 690 | 23 439 (%98,9) | 235 | 3 | 13 |
| 1998–2021 | 36 860 | 36 539 (%99,1) | 289 | 4 | 28 |

**Kimlikle bağımsız denetim:** Her ISC-GEM olayının pencere adayları arasında, `ids` alanında o olayın kimliğini taşıyan USGS kaydı arandı.

| Dönem | Kimlikli kayıt = pencere eşleşmesi | Kimlikli kayıt başka aday | Kimlikli kayıt adaylar arasında yok |
|---|---|---|---|
| 1904–1970 | 13 607 | 0 | 2 |
| 1971–1997 | 23 665 | 6 | 19 |
| 1998–2021 | 36 816 | 6 | 38 |

"Adaylar arasında yok" iki durumu birlikte sayar:
- kimliğin hiçbir USGS kaydında geçmemesi (Ek 1: 2 / 8 / 16);
- kimlikli USGS kaydının zaman/uzaklık penceresinin dışında kalması (0 / 11 / 22). Bu olaylarda USGS ile ISC-GEM'in konumu ya da zamanı pencereden fazla ayrışıyor.

Kimlik birleştirmesi her iki durumu doğrudan çözer. Pencere eşleştirmesi ise ikinci durumda olayı "yalnız ISC-GEM" sayar ve USGS kaydını ayrıca ekler; yani 33 olay çift sayılır.

## 5. Çift kayıt riski

- **Kimliğe göre (Ek 1):**
  - Hiçbir ISC-GEM ana katalog kimliği birden çok USGS kaydında geçmiyor (0).
  - İki USGS kaydı ikişer ISC-GEM olayını birleştirmiş: `ak009697xs3z` (13679072, 17593429) ve `usp000jwjn` (602005586, 607215270).
  - 26 ISC-GEM olayının kimliği hiçbir USGS kaydında yok: 1904–1970'te 2, 1971–1997'de 8, 1998–2021'de 16. Örnek: 1932-05-26 Mw 7,6.
- **Pencereye göre "olası çift" sayıları** (448 / 234 / 282) çoğunlukla birbirine yakın gerçek ayrı olaylardır. Örneğin 1904-04-04 10:02 ve 10:26 depremleri ISC-GEM'de iki ayrı olay; 1940 öncesi 200 dakikalık pencere ikisini de aday yapıyor. Kimlik denetimi bunların ISC-GEM içinde çift olmadığını gösteriyor. Dolayısıyla çift kayıt ayıklaması pencereyle değil, kimlikle yapılmalı.
- **ISC-GEM ek katalogu USGS'de var:** `net = iscgemsup` olan kayıtlar "yalnız USGS"de 1 483 (1904–1970) ve 277 (1971–1997). Ayrıca 911 USGS kaydının `ids` alanında ana katalog dışı bir ISC-GEM kimliği var. USGS kendiliğinden eklenirse, ek katalog dışarıda bırakma kararına rağmen geri gelir.

## 6. Birleştirmenin ekleyeceği ("yalnız USGS")

| Dönem | Yalnız USGS | Başlıca ağlar |
|---|---|---|
| 1904–1970 | 4 143 | `ci` 1 549, `iscgemsup` 1 483, `ushis` 845, `hv` 135, `official` 63 |
| 1971–1997 | 121 577 | `us` 118 231, `nc` 865, `ci` 718, `ak` 628, `hv` 411, `iscgemsup` 277 |
| 1998–2021 | 273 774 | `us` 269 876, `ak` 2 014, `ci` 634, `nc` 364, `pr` 278 |

- **1971 sonrası:** Eklenenler çoğunlukla NEIC'in (`us`) M 4,0–5,5 mb kayıtları. Bunlar ISC-GEM'in seçim ölçütü gereği almadığı katman.
- **1971 öncesi:** Ek katalog dışında eklenenler ağırlıkla ABD bölgesel ağları (`ci`, `ushis`, `hv`). Küresel bir katkı değil. Literatürde bilinen bir durum; ayrıca yorumlanmadı.

## 7. Büyüklük tanısı (eşleştirme koşulu değil; yalnız birleşik katalogda hangi değerin yazılacağı için)

`tekil` eşleşmelerde USGS mag − ISC-GEM Mw (ortanca [çeyrekler arası aralık], N):

| Dönem | USGS Mw türleri | mb | Ms |
|---|---|---|---|
| 1904–1970 | 0,00 [0,00 – 0,00], 13 132 | — | −0,03, 3 |
| 1971–1997 | +0,03 [0,00 – +0,06], 12 502 | −0,22 [−0,34 – −0,09], 8 581 | −0,18, 2 207 |
| 1998–2021 | +0,01 [−0,03 – +0,04], 27 136 | −0,16 [−0,30 – −0,03], 9 286 | −0,21, 52 |

1904–1970'te USGS'nin Mw'si ISC-GEM'inkiyle aynı; bu, 3. bölümdeki köken bulgusuyla tutarlı.

## 8. Asıl soruya yanıt: "1900–1970 ISC + 1971– USGS"

USGS ComCat, 1904–1970 için zaten ISC-GEM'i (ana ve ek katalog) içeriyor. Yani küresel ölçekte "1900–1970 ISC-GEM + 1971– USGS" birleşimi, büyük ölçüde USGS'nin şu anki içeriğiyle aynı. Fark üç yerde:
- (a) ek katalogun dışarıda bırakılması;
- (b) birleşik kayıtlarda ISC-GEM Mw'nin açıkça kaynak gösterilmesi;
- (c) 2022 sonrası.

## 9. Birleştirme kuralı önerisi (uygulanmadı; karar bekliyor)

1. **Temel:** ISC-GEM ana katalog, 1904–2021 (homojen Mw, `mw_s` doğrudan/vekil bilgisiyle).
2. **USGS kaydını çıkar:**
   - `ids` alanında bir ISC-GEM ana katalog kimliği varsa (kimlik eşleşmesi; pencere gerekmez). Bu, 74 133 olayı kapsıyor; birleştirilmiş 2 kayıt dahil.
   - `net = iscgemsup` ise ya da `ids` alanında yalnız ek katalog kimliği varsa (ek katalog kararıyla tutarlı).
   - `type ≠ earthquake` ise.
3. **Kimlik bağı olmayan 26 ISC-GEM olayı:** Pencere sonucu `tekil` ise karşılık gelen USGS kaydı çıkarılır. Diğerleri tek tek listelenir.
4. **Kalan USGS kayıtları:** Ayrı bir katman olur. Kendi büyüklük türlerini korurlar (homojen Mw değildir) ve işaretlenirler. 2022 ve sonrası yalnız USGS'den gelir.

**Kararınızı gerektiren konular:**
- (a) Kalan USGS katmanı küresel analizlere varsayılan olarak girsin mi?
- (b) Bu katmandaki mb/Ms değerleri Mw'ye dönüştürülsün mü, yoksa türleriyle mi kalsın? Dönüştürme ayrı bir yöntem kararıdır.
