# Pre-mainshock Seismicity Rate Test · Ana Şok Öncesi Sismisite Oranı Testi

**Durum:** DENEME — `feature/premainshock-rate-test` dalı. Ana sayfaya bağlı değil; `main`'e birleştirilmedi.
**Sürüm:** `pmsr-core-0.1.0`

Seçilen bir ana şoktan önceki 20 günlük sismisitenin, aynı noktanın önceki yılına göre istatistiksel olarak
anlamlı biçimde artıp artmadığını sınar. Deprem tahmini değildir; "öncü" etiketi kullanılmaz.

Yöntem: Azad Khan, Werner, Biggs ve Fagereng (2025), *JGR Solid Earth* 130(7), e2024JB030733 —
Combined ana şok seçimi (Fixed ∪ Mag-Dep dışlaması), yerel Mc (b-değeri kararlılığı, 10→50 km, ≥ 275 olay),
Empirical Seismicity Rate (20 gün / 10 km; kalibrasyon 365→20 gün; 0,01 gün adım; p < 0,01).

## Arayüz (`index.html`)
- **Bölge ve olay analizi:** kaynak EMSC (Avrupa, Türkiye dahil) ya da USGS (Global) canlı FDSN, veya dosya yükleme
  (AFAD dışa aktarımı ya da başka katalog; CSV/JSON). AFAD tarayıcıdan canlı sorgulanamıyor (sunucu tarayıcı isteklerini
  reddediyor), bu yüzden dosya yükleme yolu.
  Katalog, ana şok döneminden 385 gün önce başlayarak ve kutu 0,5° genişletilerek alınır; ana şoklar iç kutudan seçilir.
  Bölgedeki tüm M ≥ 4 adaylar listelenir: Combined olmayanlar *ana şok seçim kuralını sağlamıyor*, Mc için yeterli olay
  olmayanlar *analiz için yeterli veri yok* olarak işaretlenir. Satıra tıklamak tek olay ayrıntısını (günlük sayım grafiği,
  N₂₀, kalibrasyon persentili, p) açar.
- Varsayılan dışı parametreler sonuçta işaretlenir; baskın büyüklük türü seçeneği varsayılan açıktır.
- **EMSC kurum filtreleri:** *Origin Agency* (Author: konum/zaman çözümünü veren) ve *Magnitude Agency* (MagAuthor:
  büyüklüğü veren) ayrı filtrelerdir; ikisi aynı olmak zorunda değildir. Seçilen alt küme EMSC kataloğunun bir parçasıdır,
  ilgili kurumun kendi kataloğuna eşdeğer sayılmaz. Karma katalog uyarısı her iki alan için ayrı verilir; filtreler SHA-256'ya yansır.
- **Analiz kaydı (JSON):** kaynak, sorgu URL'si, indirme zamanı, olay sayısı, katalog SHA-256, parametreler, sonuçlar.
- **Referans: SCSN yeniden üretimi:** donmuş referansı tarayıcıda çalıştırır ve olay bazında karşılaştırır.

## Dosyalar
- `index.html`, `worker.mjs` (hesaplar Web Worker'da), `sources.mjs` (USGS/EMSC/yükleme ayrıştırıcıları)
- `core.mjs` — katalogdan bağımsız saf fonksiyonlar (`selectMainshocks`, `localMc`, `mcMBS`, `esr`, `analyzeEvent`).
  Girdi: `{id, t (UTC epoch s), lat, lon, m}`; tek büyüklük türü.
- Etiketler: *İstatistiksel olarak anlamlı artış* · *İstatistiksel olarak anlamlı artış bulunamadı* · *Analiz için yeterli veri yok*.

## Doğrulama
`node scripts/validate_pmsr_parity.mjs` — SCSN bölge kutusu (2008–2017; −118,80/−115,40, 32,68/36,20) donmuş referansı:
90 aday · Fixed 63 · Mag-Dep 64 · Combined 61 (olay bazında 0 fark) · yerel Mc 58/58 · ESR 58/58 (|Δp| = 0) ·
Type A 61/61 · anlamlı 15/58. CI: `.github/workflows/pmsr-parity.yml`.
Referans ve yeniden üretim ayrıntısı: `analysis/2026-11-18_pmsr_scsn_reproduction/`.

## Lisans notu (ayrıntı: PROVENANCE.md)
Bu kod makaledeki yöntem tanımından bağımsız yazılmıştır. GPLv3 lisanslı `statseis` (Azad Khan) yalnızca
depo dışında referans çıktı üretmek için kullanılmıştır; satır aktarımı yoktur. Doğrulama sırasında `statseis`
kaynak kodu okunmuştur; bu nedenle "temiz oda" iddiası yoktur. Hukuki görüş değildir.

## Bekleyen doğrulama: EMSC alt kümesi ↔ AFAD kataloğu
Aynı bölge ve dönem (Düzce, 2020-11 → 2022-12) için dört katalog karşılaştırılacak: EMSC karma, EMSC Origin = AFAD,
EMSC Magnitude = AFAD ve AFAD'dan indirilen orijinal dosya. Ölçütler: olay sayısı, büyüklük-sıklık dağılımı ve Mc, zaman
kapsamı ve olay eşleşme oranı. Kataloglar arası olay kimlikleri ortak olmadığından eşleşme kimlikle değil, zaman (± 5 s) ve
episantr (≤ 10 km) toleransıyla yapılır; eşleşen olaylarda büyüklük farkı (ΔM) dağılımı raporlanır.

## Bilinen sınırlar
- Mc yarıçapı WGS84 jeodezik uzaklıkla; ESR ve Type A yarıçapı küresel (R = 6371 km) haversine ile ölçülür (referansla aynı).
- 1 yıllık kalibrasyonla nominal %1 eşiğin gerçek yanlış pozitif oranı Poisson altında %1,7–3,0'tür (Faz 0, T2a).
- Canlı USGS ve EMSC sorguları tek seferde en çok 20 000 olay alır; sınır aşılırsa uyarı verilir (bölgeyi ya da dönemi küçültün).
- Mag-Dep seçimi için daha büyük olaylar 0,5°'lik kenar payı içinde aranır; M ≥ 6 olayların daha geniş pencereleri kenar payını aşabilir.
- Canlı kaynaklarda yalnız deprem türü olaylar kullanılır (SCSN referansında ocak patlamaları da vardı).
