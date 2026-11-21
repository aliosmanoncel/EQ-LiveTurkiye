# SCEDC SCSN deprem kataloğu — EQ-Live statik arşivi (Aşama 1)

Güney Kaliforniya Sismik Ağı (SCSN) kataloğunun, Southern California Earthquake Data Center (SCEDC) yıllık dosyalarından alınmış, **sürümlü ve değiştirilemez** kopyası. Amaç: öğrencilerin ve araştırmacıların aynı veri sürümüyle aynı sonuçları yeniden üretebilmesi.

> **Durum:** Yalnızca veri arşivi. EQ-Live arayüzü, canlı harita, GK74, Reasenberg ve diğer veri kaynakları bu klasörü **kullanmaz**. Bölge analizine kaynak olarak eklenmesi (Aşama 2) ayrı bir karardır.

## Kaynak ve atıf
- Veri: SCEDC (2013): Southern California Earthquake Data Center. Caltech. Dataset. **doi:10.7909/C3WD3XH1**
- Katalog tanımı: Hutton, Woessner & Hauksson (2010), BSSA 100(2), 423–446, doi:10.1785/0120090130
- İndirme adresi: `https://service.scedc.caltech.edu/ftp/catalogs/SCEC_DC/{YYYY}.catalog`
- Bu arşivi kullanan çalışmalar SCEDC'yi yukarıdaki DOI ile kaynak göstermeli ve kullandıkları **anlık görüntü kimliğini** (ör. `2026-11-18`) ve dosyaların `sha256_gz` değerlerini raporlamalıdır.

## Kapsam (anlık görüntü `2026-11-18`)
Alan: 32–37° K, 122–114° B (SCEDC dosya alanı; bölge filtresi uygulanmadı). Olay türü filtresi yok (`eq` deprem, `qb` taş ocağı patlaması vb.). Toplam **415 080 olay**.

| Yıl | Olay | Durum |
|---|--:|---|
| 2008 | 14 058 | tam |
| 2009 | 16 731 | tam |
| 2010 | 41 959 | tam |
| 2011 | 15 565 | tam |
| 2012 | 17 162 | tam |
| 2013 | 18 544 | tam |
| 2014 | 14 429 | tam |
| 2015 | 15 587 | tam |
| 2016 | 16 029 | tam |
| 2017 | 16 344 | tam |
| 2018 | 20 730 | tam |
| 2019 | 66 341 | tam |
| 2020 | 37 285 | tam |
| 2021 | 23 201 | tam |
| 2022 | 16 884 | tam |
| 2023 | 13 680 | tam |
| 2024 | 17 266 | tam |
| 2025 | 16 844 | tam |
| 2026 | 16 441 | **kısmi** (son olay 2026-11-17) |

## Dosya düzeni
```
data/scedc/
  manifest.json                         kaynak, politika, katalog değişiklikleri, anlık görüntüler, SHA-256
  raw/<anlık görüntü>/<YYYY>.catalog.gz  indirilen dosyanın bayt bayt aynısı (gzip, deterministik)
  scsn/<anlık görüntü>/scsn_<YYYY>.csv.gz işlenmiş CSV
```
İşlenmiş CSV sütunları: `id, time_utc, lat, lon, depth_km, mag, mag_type, event_type, geo_type, quality, nph, ngrm`.
Değerler ham dosyadaki **metnin aynısıdır** (sayıya çevirip yeniden yazma yok; yuvarlama olamaz). `time_utc` = `YYYY-MM-DDTHH:MM:SS.ss` (UTC, 0,01 s). `mag` = SCEDC'nin tercih ettiği büyüklük; türü `mag_type` (`l` ML, `w` Mw, `h`, `lr` Mlr, `d` ...).

## Sürüm ve güncelleme politikası (tekrarlanabilirlik)
- Bir anlık görüntünün dosyaları yazıldıktan sonra **değiştirilmez ve silinmez**. SCEDC geçmiş kayıtları sonradan değiştirse de eski anlık görüntü korunur.
- Yeni indirme, yeni bir anlık görüntü olarak eklenir (`scripts/build_scedc_archive.py --snapshot YYYY-MM-DD`). Manifestteki `current`, her yıl için önerilen anlık görüntüyü gösterir.
- Tamamlanmış yıllar dondurulur; içinde bulunulan yıl elle, yeni anlık görüntüyle güncellenir.
- CI (`.github/workflows/scedc-archive.yml`) main'deki manifestle karşılaştırarak önceki anlık görüntülerin değişmediğini denetler.

## Doğrulama
`python3 scripts/validate_scedc_archive.py` (yalnız standart kütüphane, ağ gerekmez):
SHA-256 (sıkıştırılmış, açılmış ham, işlenmiş CSV) · ham veri satırı = SCEDC altbilgisi = işlenmiş satır · işlenmiş CSV'nin ham dosyadan alan alan yeniden üretilebilmesi · yıl, zaman biçimi (0,01 s), geçerli takvim zamanı, konum aralığı · yıl içinde tekil olay kimliği · manifestte olmayan dosya olmaması · değişmezlik.

Ek çapraz kontrol (bu anlık görüntü oluşturulurken, bağımsız pandas okumalarıyla): PMSR 2008–2017 donmuş kataloğu (`scripts/fixtures/pmsr_scsn_box_catalog.csv.gz`, 152 494 olay) ve PMSR 2018–2026 çalışmasının kataloğu (230 954 olay) bu arşivden aynı bölge kutusuyla seçilen olaylarla kimlik, zaman, konum ve büyüklükte birebir aynı.

## Kullanmadan önce bilinmesi gerekenler
Verinin kaynağı güvenilir ve izlenebilir; ancak **analiz için homojen olduğu varsayılmamalıdır**.
- Büyüklük türleri karışıktır (çoğunluk ML; büyük olaylarda Mw).
- Bilinen katalog değişiklikleri (`manifest.json` → `known_catalog_changes`): 2008-01-01 yeni ML yöntemi; 2015 (M < 2,5 için elle zamanlamanın bırakılması, Mlr); 2019 Ridgecrest dizisi M < 2,5'te büyük ölçüde gözden geçirilmemiş; 2023-11 M < 3 için PhaseNet; 2024-11 PhaseNet + GaMMA. Bu tarihler b-değeri ve oran zaman serilerinde olası **katalog kaynaklı** kırılma noktalarıdır.
- Tamamlanma büyüklüğü (Mc) zamana ve bölgeye göre değişir; her analizde ayrıca belirlenmelidir.
- `qb` (patlama) olayları dahildir; deprem analizlerinde gerekiyorsa `event_type == 'eq'` ile ayıklanmalıdır.
