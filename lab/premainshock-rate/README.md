# Pre-mainshock Seismicity Rate Test · Ana Şok Öncesi Sismisite Oranı Testi

**Durum:** DENEME — `feature/premainshock-rate-test` dalı. Ana sayfaya bağlı değil; `main`'e birleştirilmedi.
**Sürüm:** `pmsr-core-0.1.0`

Seçilen bir ana şoktan önceki 20 günlük sismisitenin, aynı noktanın önceki yılına göre istatistiksel olarak
anlamlı biçimde artıp artmadığını sınar. Deprem tahmini değildir; "öncü" etiketi kullanılmaz.

Yöntem: Azad Khan, Werner, Biggs ve Fagereng (2025), *JGR Solid Earth* 130(7), e2024JB030733 —
Combined ana şok seçimi (Fixed ∪ Mag-Dep dışlaması), yerel Mc (b-değeri kararlılığı, 10→50 km, ≥ 275 olay),
Empirical Seismicity Rate (20 gün / 10 km; kalibrasyon 365→20 gün; 0,01 gün adım; p < 0,01).

## Dosyalar
- `core.mjs` — katalogdan bağımsız saf fonksiyonlar (`selectMainshocks`, `localMc`, `mcMBS`, `esr`, `analyzeEvent`).
  Girdi: `{id, t (UTC epoch s), lat, lon, m}`; tek büyüklük türü.
- Etiketler: *İstatistiksel olarak anlamlı artış* · *İstatistiksel olarak anlamlı artış bulunamadı* · *Analiz için yeterli veri yok*.

## Doğrulama
`node scripts/validate_pmsr_parity.mjs` — SCSN bölge kutusu (2008–2017; −118,80/−115,40, 32,68/36,20) donmuş referansı:
90 aday · Fixed 63 · Mag-Dep 64 · Combined 61 (olay bazında 0 fark) · yerel Mc 58/58 · ESR 58/58 (|Δp| = 0) ·
Type A 61/61 · anlamlı 15/58. CI: `.github/workflows/pmsr-parity.yml`.
Referans ve yeniden üretim ayrıntısı: `analysis/2026-11-18_pmsr_scsn_reproduction/`.

## Lisans notu
Bu kod makaledeki yöntem tanımından bağımsız yazılmıştır. GPLv3 lisanslı `statseis` (Azad Khan) yalnızca
depo dışında referans çıktı üretmek için kullanılmıştır; satır aktarımı yoktur. Doğrulama sırasında `statseis`
kaynak kodu okunmuştur; bu nedenle "temiz oda" iddiası yoktur. Hukuki görüş değildir.

## Bilinen sınırlar
- Mc yarıçapı WGS84 jeodezik uzaklıkla; ESR ve Type A yarıçapı küresel (R = 6371 km) haversine ile ölçülür (referansla aynı).
- 1 yıllık kalibrasyonla nominal %1 eşiğin gerçek yanlış pozitif oranı Poisson altında %1,7–3,0'tür (Faz 0, T2a).
- Arayüz henüz yok (sonraki adım: AFAD / EMSC / USGS / yüklenen katalog ile tek olay analizi).
