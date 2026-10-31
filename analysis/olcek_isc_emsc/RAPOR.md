# ISC–EMSC büyüklük ölçeği ve 1998 sınırı — araştırma raporu (2026-10-31)

**Dal:** `isc-emsc-olcek`, `main` 5274c46'dan açıldı. Yalnız araştırma dosyaları var; `index.html` ve `data/` değişmedi. Ham kataloglar yalnızca okundu.

**Soru (ChatGPT önerisi 2):** a(t) ve b(t)'de 1998'de görülen değişim deprem üretimindeki gerçek bir değişim mi, yoksa katalog, büyüklük ölçeği ya da Mc farkından mı kaynaklanıyor?

**Betikler:**
- `olcek.js`: uygulamanın kendi kodunu tarayıcıda çalıştırır. Sonuç: `olcek_sonuc.json`.
- `tur_ici_b.js`: Node. Sonuç: `tur_ici_b.json`.

**Bölge ve dönemler:** Türkiye kutusu 36–42° K / 26–45° D. P1 = 1990–1997 (ISC), P2 = 1998–2005 (EMSC). Uzunlukları eşit (8 yıl) ve 1998 sınırına bitişik.

**Ortak dönem:** Yerel katalogda ISC 1997'de biter, EMSC 1998'de başlar; iki kaynağın aynı olayları birlikte raporladığı bir dönem yok. Bu yüzden ortak referans olarak ISC-GEM v12.1 Mw kullanıldı (A).

## A. Ortak ölçeğe göre fark: ISC-GEM Mw ile eşleşen olaylar

Veri: `data/mw_iscgem.json` içindeki 1144 eşleşme (EQ-Live olayı ↔ ISC-GEM Mw; eşleştirme önceden yapılmıştı). Her olayda Δ = M − Mw_ISCGEM; M ham büyüklük ya da uygulamanın dönüşüm bankasındaki her mod.

**Medyan Δ, referans yalnızca doğrudan Mw:**

| Kaynak / tür | n | ham | Scordilis 2006 | Çıvgın 2019 (ML) | Birleşik | ISC-GEM 2015 | Lolli 2014 |
|---|---|---|---|---|---|---|---|
| ISC, tümü | 222 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| ISC, Ms | 29 | −0,24 | 0,02 | −0,24 | 0,02 | 0,04 | −0,02 |
| EMSC, tümü | 416 | **−0,12** | 0,00 | −0,12 | −0,01 | −0,01 | −0,02 |
| EMSC, mb | 219 | −0,18 | 0,07 | −0,18 | 0,07 | 0,06 | 0,06 |
| EMSC, Ms | 25 | **−0,44** | −0,04 | −0,44 | −0,04 | 0,00 | −0,08 |
| EMSC, Mw | 168 | −0,05 | −0,05 | −0,05 | −0,05 | −0,05 | −0,05 |

**Referans doğrudan + vekil Mw** (tabloda verilmeyenler `olcek_sonuc.json`'da): ham ISC mb −0,35 (n = 271), ISC Ms −0,16 (n = 206), EMSC mb −0,21 (n = 267).

**Sonuç A:**
- M ≳ 5 olaylarda ham mb ve Ms, Mw'nin 0,2–0,4 birim altında.
- Scordilis, Birleşik ve ISC-GEM 2015 dönüşümleri bu farkı iki dönemde de ±0,07 içine getiriyor. Lolli 2014'te ISC mb'de −0,18 kalıyor.
- **Sınır:** ISC-GEM yalnızca büyük olayları (M ≳ 5) içerir. EMSC'de baskın olan MD ve ML için eşleşme neredeyse yok (MD n = 1, ML n = 5). Bu türlerin ölçeği bu yolla sınanamaz.
- **MD hiçbir dönüşüm bağıntısının kapsamında değil**, yani her modda ham kalıyor.

## B. 1998 sınırı: Mc, b ve hız

### B.1 Tür bileşimi (ham, olay sayısı)

| Dönem | MD | ML | mb | Ms | Mw | diğer |
|---|---|---|---|---|---|---|
| P1 1990–1997 (ISC) | 1390 (%54) | 407 | 451 | 72 | 31 | 196 |
| P2 1998–2005 (EMSC) | 12 143 (%92) | 383 | 539 | 4 | 30 | 1 |

Kaynak değişimiyle bileşim keskin biçimde MD'ye kayıyor.

### B.2 Ortak eşikle dönem karşılaştırması

Yöntem:
- Her dönemin Mc'si uygulamanın `computeMcScale` fonksiyonuyla bulundu: P1 = 3,7, P2 = 3,2, her modda aynı.
- Ortak eşik Mc = 3,7.
- Her dönem için ayrı Weichert (tek basamak = tek Mc) çalıştırıldı.

| Mod | GK74 | b P1 → P2 (Δ) | Δ log₁₀ λ(≥3,7) | Δ log₁₀ λ(≥4,5) |
|---|---|---|---|---|
| Ham | kapalı | 1,29 → 1,15 (−0,14) | +0,09 | +0,21 |
| Scordilis / Birleşik | kapalı | 0,90 → 0,87 (−0,02) | +0,08 | +0,10 |
| ISC-GEM 2015 | kapalı | 0,70 → 0,77 (+0,07) | +0,08 | +0,02 |
| Lolli 2014 | kapalı | 1,13 → 1,05 (−0,09) | +0,09 | +0,16 |
| Ham | açık | 1,10 → 1,07 (−0,03) | +0,13 | +0,15 |
| Scordilis / Birleşik | açık | 0,77 → 0,82 (+0,05) | +0,12 | +0,08 |
| ISC-GEM 2015 | açık | 0,61 → 0,73 (+0,12) | +0,12 | +0,02 |
| Lolli 2014 | açık | 0,97 → 0,98 (0,00) | +0,12 | +0,12 |

Çıvgın 2019 (yalnız ML) sonuçları her satırda ham ile aynı.

**Sonuç B.2:**
- **Mc'deki hız sıçraması dönüşümden bağımsız:** her modda +0,08–0,09, GK74 açıkken +0,12–0,13 log birimi. Nedeni, M ≈ 3,7'de olayların çoğunun MD/ML olması; bunlar dönüştürülmüyor.
- **b'nin düzeyi ve sınırdaki değişimi dönüşüm seçimine çok duyarlı.** P1'de b 0,61 ile 1,29 arasında; Δb −0,14 ile +0,12 arasında. Karma katalogda yalnızca mb/Ms'yi dönüştürmek büyüklük dağılımını tekdüze olmayan biçimde değiştiriyor. Bu yüzden **b için dönüşüm seçimi birinci derece bir etken.**
- M ≥ 4,5'teki hız değişimi de moda bağlı (+0,02 ile +0,21 arası).

### B.3 Tür içi b (`tur_ici_b.js`; ham, Mc = 3,7)

| Tür | P1 | P2 |
|---|---|---|
| tümü | 1,27 ± 0,07 (n = 1402) | 1,15 ± 0,05 (n = 1759) |
| MD | 2,56 ± 0,20 | 2,26 ± 0,14 |
| ML | 2,21 ± 0,30 | 1,71 ± 0,23 |
| mb | 0,82 ± 0,08 | 0,55 ± 0,05 |
| Mw | 0,24 ± 0,08 (n = 31) | — |

Tür içi b değerleri fiziksel b değeri değildir. Kurum, olay büyüdükçe tercih ettiği büyüklük türünü değiştiriyor (küçük olaylara MD/ML, büyüklere mb/Ms/Mw). Bu yüzden her tür farklı bir büyüklük bandını kesiyor ve aşırı yüksek ya da düşük "b" veriyor. Karma kataloğun b'si bu bantların bileşimine bağlı. Bileşim değişince (B.1) b de değişir; bu, fiziksel bir değişim olmadan da olabilir.

## C. Mc değişiminin a(t) ve b(t)'ye etkisi

Ayarlar: ISC 1971–1997 + EMSC 1998– birleşik pencere, dönüşüm yok. a(t) ve b(t) pencere ortalamaları üç dönemde alındı.

| Ayar | Mc | a: 1995–97 → 1998–2000 → 2001–03 | b: aynı dönemler | pencere |
|---|---|---|---|---|
| Otomatik Mc, GK74 kapalı | 3,2 | 2,85 → 3,02 → 3,02 | **0,72 → 1,07 → 1,29** | 153/227/232 |
| Mc = 4,0, GK74 kapalı | 4,0 | 2,00 → 2,08 → 1,87 | 1,23 → 1,04 → 1,08 | 27/31/22 |
| Otomatik Mc, GK74 açık | 3,2 | 2,35 → 2,54 → 2,57 | **0,70 → 0,91 → 1,08** | 64/100/109 |
| Mc = 4,0, GK74 açık | 4,0 | **1,65 → 1,73 → 1,71** | **1,01 → 1,04 → 1,05** | 13/16/16 |

**Sonuç C:**
- Birleşik pencerede otomatik Mc, olay sayısı çok olan EMSC döneminin Mc'sini (3,2) alıyor. ISC dönemi bu eşikte tam değil (Mc 3,7). Bu yüzden 1998 öncesi pencerelerde hem hız hem b düşük çıkıyor ve **b(t)'de 1998'de yapay bir sıçrama** oluşuyor (GK74 açıkken 0,70 → 0,91 → 1,08).
- İki dönemde de tam olan Mc = 4,0 ve GK74 ile **sıçrama kayboluyor**: b 1,01 → 1,04 → 1,05, a 1,65 → 1,73 → 1,71.
- Ham katalogda Mc = 4,0'da 1998–2000'deki değişim büyük ölçüde 1999 artçılarından geliyor.

## D. Genel sonuç ve öneriler

1. **Varsayılan ayarlarda 1998'de görülen b(t) sıçraması büyük ölçüde tamlık (Mc) kaynaklı bir yapay etki.** Eşik iki dönemde de tamsa ve artçılar ayıklanmışsa, bu bölgede ve bu dönemde b ve a'da belirgin bir değişim kalmıyor.
2. **Mc'deki hız** dönüşüm seçiminden etkilenmiyor. Ortak eşikte (3,7) +0,08–0,13 log birimi bir hız artışı var. Bu küçük artış ağ ya da büyüklük türü değişiminden de gelebilir; fiziksel bir değişim olarak yorumlanmamalı.
3. **b'nin düzeyi** dönüşüm seçimine birinci derecede bağlı (0,6–1,3). Karma türlü katalogda b karşılaştırması aynı dönüşüm ve aynı eşikle yapılmalı. Mümkünse tek türde (ör. Mw) ya da tamamen dönüştürülmüş bir alt kümede tekrarlanmalı.
4. **MD (KOERI süre büyüklüğü)** EMSC döneminin %92'sini oluşturuyor ve hiçbir bağıntının kapsamında değil. 1998 sınırında ölçek tutarlılığı için en büyük açık bu.

**Uygulama için öneriler (ayrı iş, onayınızla):**
- b(t)/a(t) penceresi 1998 sınırını kesiyorsa ve otomatik Mc bir dönemin Mc(t)'sinin altında kalıyorsa panelde uyarı göstermek. b(t)'de bu tür pencereleri işaretleyen bir alan (`inc`) zaten var; uyarı metnine bağlanabilir.
- Birleşik pencerede iki dönemin Mc'si arasında 0,3'ten büyük fark varsa "tamlık basamakları kullanın" önerisi.

**Sınırlar:**
- Tek bölge (geniş Türkiye kutusu) ve tek sınır (1998).
- ISC-GEM karşılaştırması yalnızca M ≳ 5.
- Elle Mc seçenekleri 0,5 adımlı; ortak eşik olarak 3,7 yerine 4,0 kullanıldı.
- C'deki pencere sayıları Mc = 4,0'da küçük (13–31); ortalamalar belirsiz.
