# Katalog tamlık (Mc uyumsuzluğu) uyarısı — doğrulama raporu (2026-11-01, son inceleme sonrası)

Dal: `mc-uyari`, `main` 54fbd0b'den açıldı; son incelemede güncel `main` (fd18abf) ile eşitlendi.

**Gerekçe:** ISC–EMSC araştırması (`isc-emsc-olcek` dalı) varsayılan ayarlardaki 1998 b(t) sıçramasının büyük ölçüde tamlık (Mc) kaynaklı olduğunu gösterdi. Ancak ortak Mc ile bile anlamlı bir hız farkı kaldı (+0,14 log birimi). Uyarı, kullanıcıyı Mc farkına karşı uyarır. Ama ne değişimin kaybolmasını ne de kalmasını fiziksel bir sonuç olarak sunar.

## 1. Ne yapar, ne yapmaz

- **Hesap değiştirmez.** Yalnızca b(t) panelinde zaten hesaplanan ölçümleri okur. Bunlar: Mc(t) şeridi (250 olaylık kayan pencere, adım 25, maks. eğrilik +0,2), pencere başına `inc` işareti ve tamlık basamaklarının dönem veri Mc'si (`p.mcData`). Basamaklı modda ek olarak yıllık Mc hesaplanır; yalnızca uyarı içindir.
- **Nerede görünür:** b(t) istatistik alanının başında tam metin (`#mcUyariB`), a(t) alanının başında kısa not (`#mcUyariA`).

### Koşullar

| Mod | Uyarı koşulu |
|---|---|
| Tek Mc | b(t) pencerelerinin **en az %5'i** `inc` (pencere süresinde veri Mc(t) > kullanılan Mc + 0,1). Önerilen ortak eşik: en yüksek Mc(t), 0,1'e yukarı yuvarlanmış. |
| Tamlık basamakları | Herhangi bir dönemde aşağıdakilerden biri: (a) dönemin bütün verisinden Mc'si eşik + 0,2'nin üstünde (mevcut basamak tanısıyla aynı ölçüt, `CS_QC.mcGap`); (b) dönem içindeki Mc(t) noktalarının en az 2'si ve %10'u eşik + 0,2'nin üstünde; (c) dönem içinde en az 2 yılın yıllık Mc'si (≥ 50 olaylı yıllar, "Otomatik öner" ile aynı ölçüt) eşik + 0,2'nin üstünde. |

Ölçüt (c) neden gerekli: seyrek dönemlerde 250 olaylık Mc(t) penceresi birkaç yılı kapsar ve dönem içi eksikliği gizler. 1985–1989'da (yıllık Mc 4,7–4,8, eşik 4,0) (a) ve (b) uyarı vermedi; (c) verdi.

### Metin

ChatGPT'nin önerdiği metin, ardından duruma özgü neden ve şu sınırlama:

> "Ortak Mc ile değişimin kaybolması fiziksel bir değişimin olmadığını kanıtlamaz; değişimin kalması da fiziksel olduğunu göstermez: büyüklük ölçeği (ör. ISC → EMSC, MD) ve ağın algılama farkları ayrıca değerlendirilmelidir."

Önerilen eşik için not: "en yüksek Mc(t) büyük depremlerden sonraki geçici eksiklikten de gelebilir".

## 2. Testler

**Birim testleri** (`scripts/test_mc_uyari.js`): 12/12.
- %5 eşiği (%4'te uyarı yok).
- Önerilen eşiğin yuvarlanması.
- Mc(t) < 2 noktada karar verilmemesi.
- Basamaklarda üç ölçüt: tek aykırı Mc(t) noktası ve tek yıl uyarı üretmez.
- Metin içeriği.

Diğer birim testleri: 16/16 (yeni dosya dahil).

**Kabul testi** (`analysis/mc_uyari/kabul_mc.js`, önce = main 54fbd0b): 17/17.
- Yedi senaryonun hepsinde b(t) ve a(t) grafikleri, uyarı dışındaki b(t)/a(t) metinleri ve G–R metni önce = sonra; yani hesap değişmedi.
- Uyarı b(t) ve a(t)'de tutarlı. Sayfa hatası yok.

| Senaryo | Kullanılan Mc | Uyarı | Ayrıntı |
|---|---|---|---|
| ISC 1971–1997 + EMSC 1998–, otomatik Mc | 3,2 | **var** | Mc(t) 3,2–4,8; pencerelerin %20'si `inc`; önerilen Mc 4,8 |
| Aynı, elle Mc 4,0 | 4,0 | var | %17 `inc` (1970–80'lerin Mc'si 4,0'ın üstünde) |
| ISC 1971–1997, otomatik Mc | 3,7 | var | %59 `inc` |
| EMSC 1998–, otomatik Mc | 3,2 | var | Mc(t) 3,2–4,5; %11 `inc` |
| ISC 1971–1997, test basamakları (1971 M ≥ 4,5; 1985 M ≥ 4,0) | basamaklı | var | 1971–1985: Mc(t) ve yıllık (1971: 4,9, 1976: 5,0, 1983: 4,8); **1985–1997: yıllık (1986: 4,8, 1988: 4,7)**, Poisson raporu §4.5 ile tutarlı |
| ISC 1971–1997, "Otomatik öner" basamakları | basamaklı | var | 1984–1986 (eşik 4,2): dönem veri Mc 5,0; mevcut basamak tanısıyla tutarlı |
| Marmara, EMSC 1998– | 3,2 | yok | koşul sağlanmadı |

Ekran görüntüsü: `mc_uyari_birlesik.png`

## 2a. Son kod incelemesi (ChatGPT'nin üç noktası)

**1. Hesaplama bütünlüğü.** Kod farkı satır satır okundu. Değişiklik yalnızca gösterim katmanında: `mcUyariDurum`, `mcUyariHtml` ve iki `innerHTML` başına eklenen uyarı. `lastBts`, b(t) serisi, `inc` tanımı, G–R ve a(t) hesapları değişmedi. Yıllık Mc yalnızca okuma yapar (`computeMc`). `data/` değişmedi. Kabul testi bunu 13 senaryoda doğruluyor (grafikler ve uyarı dışındaki metinler önce = sonra).

**2. Yanlış uyarı riski (geçici ve kalıcı eksiklik).** İncelemede bir zayıflık bulundu ve düzeltildi.
- Sorun: Tek Mc ölçütü pencere sayısına dayanıyordu. Artçı dizisi kısa sürede çok pencere ürettiğinden, büyük deprem sonrası birkaç aylık eksiklik "dönemlerin Mc'leri farklı" uyarısı verebilirdi.
- Düzeltme: Süre ağırlığı eklendi. `inc` pencerelerinin [t0, t1] aralıklarının birleşimi, serinin süresinin en az %5'iyse **kalıcı uyarı**; değilse ayrı, daha hafif bir **geçici eksiklik notu** gösterilir ("dönemler arası kalıcı bir Mc farkı değildir").
- Basamaklı moddaki Mc(t) ölçütü için de en az 2 takvim yılı koşulu eklendi.
- Birim testleri bu ayrımı denetliyor: pencerelerin %20'si ama sürenin %0,1'i → geçici.

**3. Geriye dönük uyumluluk.** Kabul testine altı senaryo eklendi: GK74 açık, Mc = 4,5, basamaklar + GK74 ve Kahramanmaraş (GK74 kapalı/açık).

| Senaryo | Mc | Tür | Pencere oranı | Süre oranı |
|---|---|---|---|---|
| Birleşik ISC + EMSC | 3,2 | kalıcı | %20 | %53 |
| Birleşik, GK74 açık | 3,2 | kalıcı | %18 | %54 |
| ISC 1971–1997, Mc 4,5 | 4,5 | kalıcı | %85 | %87 |
| EMSC 1998– | 3,2 | kalıcı | %11 | %9 |
| Marmara, GK74 kapalı / açık | 3,2 | yok | %0 | %0 |
| Basamaklar (test), GK74 kapalı | basamaklı | basamak | iki dönem (1971–1985: Mc(t) + yıllık; 1985–1997: yıllık) | |
| Basamaklar (test), GK74 açık | basamaklı | basamak | yalnızca 1971–1985 | |
| Kahramanmaraş (36,5–38,5° K / 35,5–39° D), GK74 kapalı | 3,2 | kalıcı | %40 | %40 |
| Kahramanmaraş, GK74 açık | 3,2 | kalıcı | %23 | %30 |

**Kahramanmaraş örneği (yıllık dağılım, GK74 kapalı):** `inc` pencereleri iki ayrı yerde:
- 1999–2004'te neredeyse tümü: seyrek ağ döneminin kalıcı eksikliği. "Kalıcı" sınıflandırması bunun için doğru.
- 2023'te 206 pencerenin 110'u: Şubat 2023 depremleri sonrası geçici eksiklik.

Önerilen ortak Mc (4,5) 2023'teki geçici tepeden geliyor ve gereğinden tutucu. Uyarı metni bunu belirtiyor ("en yüksek Mc(t) büyük depremlerden sonraki geçici eksiklikten de gelebilir; Mc(t) şeridine bakın"). Karma durumlarda önerilen eşik dikkatle okunmalı.

**GK74 açıkken basamak denetimi:** Ayıklama yıllık olay sayısını düşürdüğü için 1986 ve 1988 "≥ 50 olay" koşulunu sağlamıyor. Bu yüzden iyimser 1985 basamağı GK74 açıkken yakalanmıyor. Yıllık ölçüt seyrek kataloglarda gücünü yitirir (aşağıdaki sınırlar).

**Testler (son):**
- Birim `test_mc_uyari.js` 16/16 (geçici/kalıcı ayrımı dahil); tüm birim testleri 16/16.
- Kabul `kabul_mc.js` 31/31 (13 senaryo; önce = main fd18abf).

## 3. Sınırlar

- Uyarı, verinin kendi Mc tahminlerine (maks. eğrilik +0,2) dayanır. Bu tahminler de belirsizdir; %5 ve 0,2 eşikleri uzlaşımsaldır.
- En yüksek Mc(t) büyük depremlerden sonraki geçici eksiklikten gelebilir; önerilen eşik bu yüzden tutucu olabilir (metinde yazıyor; Kahramanmaraş örneği §2a).
- Geçici/kalıcı ayrımı süre oranına (%5) dayanır. Kalıcı ve geçici eksikliğin karıştığı serilerde (Kahramanmaraş) asıl uyarı gösterilir; geçici kısım ayrıca etiketlenmez.
- GK74 açıkken yıllık olay sayısı düştüğü için yıllık ölçüt bazı yılları değerlendiremez (basamak + GK74 senaryosu).
- Yıllık ölçüt yalnızca ≥ 50 olaylı yılları kullanır; daha seyrek dönemleri değerlendiremez.
- Uyarı, ölçek (MD gibi dönüştürülmeyen türler) ve algılama farklarını ölçmez; yalnızca metinle hatırlatır.
