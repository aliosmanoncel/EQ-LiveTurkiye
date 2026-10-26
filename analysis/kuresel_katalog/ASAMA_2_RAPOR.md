# Küresel katalog — Aşama 2 raporu: ISC-GEM ana katalog dosyası (2026-10-26)

**Kapsam:** Kullanıcı kararıyla (2026-10-26) yalnız doğrulanmış ISC-GEM v12.1 **ana** katalogunu içeren küresel dosya.
- USGS ek katmanı yalnız tasarlandı (`USGS_KATMANI_TASARIM.md`); veri üretilmedi.
- `main`, arayüz, canlı site, `data/mw_iscgem.json` ve Türkiye kataloğu değişmedi.
- Dosya `data/` altına konmadı. Yayıma alınması ayrı bir karardır.

## 1. Kararlar

| Konu | Uygulama |
|---|---|
| Temel katman | ISC-GEM v12.1 ana katalog, 1904–2021, 74 159 olay |
| Ek katalog | Dahil değil (doğrulamada kesişim 0) |
| USGS katmanı | Ayrı, varsayılan kapalı; yalnız tasarım |
| Büyüklük türü | Her olayda `M_tur`; dönüştürme yok |
| Doğrudan / vekil Mw | Her olayda `Mw_yontem` (`dogrudan`/`vekil`, kaynaktaki `s_mw` d/p) |
| Eksik değer | `null`; tahminle doldurma yok (ana katalogda eksik değer yok) |

## 2. Dosyalar
- **`uretim/iscgem_global.json`**
  - 74 159 olay; 7,84 MB (gzip ile 1,90 MB).
  - SHA-256 `c92ffdd86ec1c3e5845d4d3dc21ce9c0c4946a6e88a6f3ac8ddb284f144b83b7`.
  - Şema `eq-live/kuresel-katalog/1`, 13 alan: `id, t, lat, lon, dep, M, M_tur, M_unc, M_q, Mw_yontem, loc_q, dep_unc, dep_q`. Alan tanımları dosyanın `meta.alan_tanimlari` bölümünde.
- **`uretim/LISANS_ISC-GEM_kuresel.txt`:** CC BY-SA 3.0, telif, veri ve makale atıfları, yapılan değişiklikler, kaynak SHA-256'ları.
- **`iscgem_global_uret.py`:** `uret` ve `dogrula` modları. Girdi, depodaki doğrulanmış çıkarım; ham CSV gerekmiyor.

## 3. Doğrulama (24/24 geçti; yerelde ve GitHub Actions'ta)
- **SHA-256 zinciri:** ham CSV → çıkarım → küresel dosya.
- **Olay sayısı, alan sayısı, kapsam:** 1904-04-04 – 2021-12-31.
- **Birebir aynılık:** Kopyalanan 11 alanın her biri, her olayda çıkarımla değer ve tür olarak birebir aynı (fark 0).
- **Büyüklük türü ve yöntem:** `M_tur` her olayda `Mw`. `Mw_yontem` eşlemesi d → dogrudan (51 228), p → vekil (22 931); başka değer yok.
- **Eksik değer:** `null` sayısı çıkarımla aynı (0). Kimlikler tekil; olaylar zamana göre sıralı; ek katalog olayı yok.
- **Lisans:** Lisans, atıf ve lisans dosyası mevcut.
- **Yeniden üretim:** İki ayrı üretim bayt bayt aynı.

## 4. Kullanıcıya bildirilecek bulgu (ek analiz yapılmadı)
Vekil Mw oranı döneme göre çok farklı. Bu bilgi kaynak dosyada var; yalnız sayıldı.

| Dönem | Olay | Vekil Mw | Oran |
|---|---|---|---|
| 1904–1963 | 9 625 | 9 089 | %94 |
| 1964–1979 | 11 449 | 8 760 | %77 |
| 1980–2021 | 53 085 | 5 082 | %10 |

- **Anlamı:** ISC-GEM'in "homojen Mw" değeri, 1980 öncesinde büyük ölçüde ISC-GEM'in kendi yeniden hesapladığı Ms/mb'den ampirik bağıntıyla elde edilmiş vekil Mw'dir (Di Giacomo vd. 2015a). Bu, ISC-GEM'in belgelenmiş yöntemidir; dosya değerleri değiştirmez.
- **Kararınıza kalan:** Kullanıcının "dönüştürülmüş değerler doğrudan Mw ile ayrımsız birleştirilmesin" ilkesi bu katmana nasıl uygulanacak? Varsayılan analizde ISC-GEM vekil Mw'si kabul edilsin mi, yoksa yalnız bir seçenek olarak mı kalsın? Dosya iki kullanıma da izin veriyor.
