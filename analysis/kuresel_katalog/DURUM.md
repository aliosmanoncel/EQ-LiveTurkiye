# Küresel katalog çalışması — durum (2026-10-26)

**2026-10-27: Küresel ISC-GEM v12.1 penceresi kullanıcı onayıyla `main`'e birleştirildi ve yayımlandı** (8d50ce3; Global modda, varsayılan KAPALI). Onayın kapsamı: veri katmanının yayımlanması; `iscgem2015` dönüşüm bağıntısının bilimsel olarak doğrulandığı anlamına **gelmez**. Türkiye kataloğu, `data/mw_iscgem.json` ve TR ISC-GEM katmanı değişmedi.

| Adım | Belge | Durum |
|---|---|---|
| Ölçüm 1: ISC erişimi | `OLCUM_1_ISC_ERISIM.md` | Tamamlandı (B: kısıtlı erişim) |
| Ölçüm 2: ISC-GEM – USGS örtüşmesi ve çift kayıt | `OLCUM_2_ONKAYIT.md`, `OLCUM_2_RAPOR.md` | Tamamlandı |
| Aşama 2: `data/iscgem_global.json` (ana katalog, 14 alan), lisans, doğrulama | `ASAMA_2_RAPOR.md` | Tamamlandı; 26/26 denetim yerelde ve Actions'ta geçti |
| Arayüz hazırlığı: Global modda varsayılan kapalı "ISC-GEM 1904–2021" penceresi | `kabul/RAPOR.md` | **Yayında** (8d50ce3). Birleştirme öncesi: `main` (616f91c) ile çakışma yok; birleşik `main`'de kabul 21/21; pencere testinin düzeltme sonrası denetimleri ve gerilemeleri geçti ("hata önce" denetimleri taban zaten düzeltilmiş olduğundan beklenen biçimde kaldı). Sonrası: iş akışları ve Pages başarılı; **canlı sitede yerleşik tarayıcıyla doğrulandı** — Türkiye modunda gizli, Global modda görünür ve kapalı, açılışta veri indirilmiyor, 74 159 olay (doğrudan 51 227 / vekil 22 931), kapsam uyarısı, koordinat etiketi, Türkiye'ye dönüşte kapanıyor; pencere düzeltmesi canlıda doğru (662 olay, yalnız ISC) |
| USGS ek katmanı | `USGS_KATMANI_TASARIM.md` | Yalnız tasarım; varsayılan kapalı; lisans doğrulanmadı |
| Duyarlılık: vekil Mw ve b-değeri, 1980–2021 | `duyarlilik_1980/RAPOR.md` | Tamamlandı ve kapatıldı |

**Yöntem kararı:**

| Analiz amacı | Örneklem |
|---|---|
| Varsayılan b-değeri ve Mc | ISC-GEM'in tüm Mw değerleri; doğrudan/vekil oranı raporlanır |
| Dönüşüm bağıntılarının sınanması | Yalnız doğrudan moment kaynaklı Mw (GCMT ve literatür) |
| Yalnız doğrudan Mw ile b-değeri | Duyarlılık analizi; seçim yanlılığı uyarısıyla |

**Açık konular** (yeni bir karar gerektirir; şu an iş yok):
- Tarihsel pencere seçimi hatası: ayrı dalda düzeltildi (`tarihsel-pencere-secimi`, `analysis/tarihsel_pencere/RAPOR.md`) ve kullanıcı onayıyla **`main`'e birleştirildi** (2026-10-26, 0d893be). Birleştirme sonrası denetimler:
  - kabul testi 9/9;
  - `main` iş akışları geçti;
  - `pages-build-deployment` başarılı.

  Canlı kontrol 2026-10-27'de yapıldı: EMSC 1998 → 1 Ay → ISC 1900 sırası 662 olay (yalnız ISC) veriyor.
- Küresel ISC-GEM penceresi: 2026-10-27'de yayımlandı (yukarıda).
- Di Giacomo vd. (2015a) tam metniyle `iscgem2015` bağıntısının katsayı ve geçerlilik aralığı doğrulaması (bilimsel, arayüzden bağımsız).
- USGS ek katmanının üretimi (önce lisans doğrulaması).
- Bağıntıların ISC-GEM dışı ajans büyüklüklerine aktarımının bağımsız sınanması.
