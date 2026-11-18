# Kod kökeni notu (code provenance) · PMSR

Tarih: 2026-11-18 · Kapsam: `lab/premainshock-rate/core.mjs`, `worker.mjs`, `sources.mjs`, `index.html`,
`scripts/validate_pmsr_parity.mjs`, `scripts/fixtures/pmsr_*`.
Bu not teknik bir kayıttır, hukuki görüş değildir.

## 1. Yöntem kaynağı
Azad Khan, R., Werner, M. J., Biggs, J., & Fagereng, Å. (2025). *JGR: Solid Earth, 130*(7), e2024JB030733
(açık erişim, CC BY). Kullanılan tanımlar: Bölüm 2–3 (Fixed / Mag-Dep / Combined ana şok seçimi, Type A, Empirical
Seismicity Rate), yerel Mc için b-değeri kararlılığı (Cao ve Gao, 2002; Woessner ve Wiemer, 2005), Aki-Utsu b,
Shi ve Bolt (1982) belirsizliği, WGS84 jeodezik uzaklık (Vincenty, 1975).

## 2. Referans yazılım ve lisansı
`statseis` 0.0.6 (PyPI; github.com/RussellAzadKhan/seispy) ve analiz arşivi `foreshock_rate_estimates`
(Zenodo 10.5281/zenodo.14055540) — ikisi de **GPL-3.0**. Bu paketler EQ-Live uygulamasına dahil edilmemiştir;
tarayıcı kodu onları yüklemez veya çağırmaz.

## 3. Geliştirme süreci — açık beyan
- JavaScript kodu, makaledeki tanımlardan hareketle ayrı fonksiyon yapısıyla yazılmıştır. `statseis`'ten satır,
  fonksiyon gövdesi ya da yorum kopyalanmamıştır.
- **Ancak bu bir "temiz oda" geliştirmesi değildir.** Doğrulama sırasında `statseis` kaynak kodu okunmuştur
  (`ESR_model`, `select_mainshocks`, `create_local_catalogue`, `get_Mcs_400`, `get_mbs`, `b_est`).
- İlk JS sürümü (pmsr-core-0.1.0 ön sürümü) seçimde ve ESR'de referansla birebir aynıydı; **yerel Mc 8/58 ana şokta
  0,1–0,2 farklı çıktı.** Fark, referans kodun davranışı incelenerek şu yöntem ayrıntılarında hizalanarak giderildi:
  (a) Mc yarıçapı için küre yerine WGS84 elipsoidi ve `<` sınırı, (b) b-değerinin yuvarlanmamış büyüklüklerle ve
  M > Mc − Δ/2 eşiğiyle hesaplanması, (c) aday Mc'lerin 0,1'lik bölme merkezleri olması, (d) ortalamadaki bölmelerden
  biri tanımsızsa adayın geçersiz sayılması ve son ΔM/Δ + 1 bölmenin aday olmaması. Bunlar davranış (yöntem ayrıntısı)
  hizalamasıdır; kod ifadesi aktarılmamıştır.
- Sürüm geçmişi: `feature/premainshock-rate-test` dalındaki commit'ler.

## 4. Depodaki GPL bağlantılı dosyalar
`analysis/2026-11-18_pmsr_scsn_reproduction/step2.py`, `step3.py` ve `faz0/t1_t4.py` `statseis`'i **içe aktarır**
(kopyalamaz). Bunlar uygulamanın parçası değil, yeniden üretim betikleridir; temkinli yaklaşımla bu üç dosya
GPL-3.0 kapsamında kabul edilir ve başlarında bu belirtilir.

## 5. Veri
`scripts/fixtures/pmsr_scsn_box_catalog.csv.gz`: SCEDC SCSN kataloğundan türetilmiştir (2008–2017, bölge kutusu).
Atıf: Southern California Earthquake Data Center (2013), Caltech, doi:10.7909/C3WD3XH1; Hutton, Woessner ve
Hauksson (2010), BSSA 100(2), 423–446.
