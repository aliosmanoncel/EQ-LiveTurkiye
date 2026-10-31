# Katalog tamlık (Mc uyumsuzluğu) uyarısı — doğrulama raporu (2026-11-01)

Dal: `mc-uyari`, `main` 54fbd0b'den açıldı. `main`'e birleştirilmedi; canlıya gönderilmedi.

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

## 3. Sınırlar

- Uyarı, verinin kendi Mc tahminlerine (maks. eğrilik +0,2) dayanır. Bu tahminler de belirsizdir; %5 ve 0,2 eşikleri uzlaşımsaldır.
- En yüksek Mc(t) büyük depremlerden sonraki geçici eksiklikten gelebilir; önerilen eşik bu yüzden tutucu olabilir (metinde yazıyor).
- Yıllık ölçüt yalnızca ≥ 50 olaylı yılları kullanır; daha seyrek dönemleri değerlendiremez.
- Uyarı, ölçek (MD gibi dönüştürülmeyen türler) ve algılama farklarını ölçmez; yalnızca metinle hatırlatır.
