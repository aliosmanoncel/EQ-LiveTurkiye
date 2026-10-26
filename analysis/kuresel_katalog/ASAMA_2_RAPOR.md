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
| Mw'nin elde edilişi | Her olayda `Mw_yontem` (kaynaktaki `s`) ve `Mw_M0_kaynak` (kaynaktaki `mo_auth`); bkz. §4 |
| Eksik değer | `null`; tahminle doldurma yok |

## 2. Dosyalar
- **`uretim/iscgem_global.json`**
  - 74 159 olay; 8,32 MB (gzip ile 1,92 MB).
  - SHA-256 `85aae041ca40d8aaa7b42e76660cd2e0906c41c3880049bd16fc89b537df26c9`.
  - Şema `eq-live/kuresel-katalog/1`, 14 alan: `id, t, lat, lon, dep, M, M_tur, M_unc, M_q, Mw_yontem, Mw_M0_kaynak, loc_q, dep_unc, dep_q`. Alan tanımları dosyanın `meta.alan_tanimlari` bölümünde.
- **`uretim/LISANS_ISC-GEM_kuresel.txt`:** CC BY-SA 3.0, telif, veri ve makale atıfları, yapılan değişiklikler, kaynak SHA-256'ları.
- **`iscgem_global_uret.py`:** `uret` ve `dogrula` modları. Girdi, depodaki doğrulanmış çıkarım.
- **`iscgem_cikar.py` / `out/iscgem_v12.1_ana.json.gz`:** `mo_auth` alanı eklendi. Ham dosyadan (zip SHA-256 aynı) yeniden üretildi. Önceki 12 alan ve meta bilgisi her olayda değişmedi; Ölçüm 2 sonuçları etkilenmez (alanlar adla okunuyor).

## 3. Doğrulama (26/26 geçti; yerelde ve GitHub Actions'ta)
- **SHA-256 zinciri:** ham CSV → çıkarım → küresel dosya.
- **Olay sayısı, alan sayısı, kapsam:** 1904-04-04 – 2021-12-31.
- **Birebir aynılık:** Kopyalanan 12 alanın her biri, her olayda çıkarımla değer ve tür olarak birebir aynı (fark 0).
- **Büyüklük türü ve yöntem:** `M_tur` her olayda `Mw`. Eşlemeler d → dogrudan, p → vekil.
- **`Mw_M0_kaynak` tutarlılığı:** Vekil Mw'de her zaman null.
- **Eksik değer:** `null` sayısı çıkarımla aynı (22 932; tümü `Mw_M0_kaynak`, kaynakta boş). Kimlikler tekil; olaylar zamana göre sıralı; ek katalog olayı yok.
- **Lisans:** Lisans, atıf ve lisans dosyası mevcut.
- **Yeniden üretim:** İki ayrı üretim bayt bayt aynı.

## 4. ISC-GEM'de Mw nasıl elde ediliyor ve dosyada nasıl ayrılıyor
**Kaynak belgeler:**
- **Ham `isc-gem-cat.csv` başlığı (v12.1):**
  - "Mw, Mw uncertainty (unc), quality (q:A(highest)/B/C), source(s:p-proxy, d-direct computation)"
  - "Direct sources of scalar moments are currently gcmt … or bibliog" (`mo_auth`)
- **Di Giacomo vd. (2015a) özeti:** Vekil Mw, ISC-GEM'in yeniden hesapladığı Ms ve mb değerlerinden, bu proje için türetilmiş üstel (doğrusal olmayan) ampirik modellerle hesaplanır. Ms ve mb için ayrı bağıntılar vardır; yani tek bir bağıntı yoktur.
- **Doğrulanmayanlar:** Katsayılar ve geçerlilik aralıkları makalenin tam metninde; tam metne buradan erişilemedi, doğrulanmadı.
- **Güncelleme günlüğü:** Sürümler arasında bazı olaylarda vekil değerin yerini literatürden doğrudan Mw almış, ya da tersi olmuş (ör. v12.1'de iki olay).

**Olay başına sınıflama** (kaynağın kendi alanlarıyla; çıkarsama yok):

| Grup | Ölçüt (kaynak alanı) | Olay | Kullanım önerisi |
|---|---|---|---|
| 1a. Doğrudan, GCMT momenti | `s = d`, `mo_auth = gcmt` | 49 714 | Güçlü referans |
| 1b. Doğrudan, literatür momenti | `s = d`, `mo_auth = bibliog` | 1 513 | Güçlü referans; kaynakçası ISC-GEM sayfasında |
| 2. Vekil | `s = p` | 22 931 | Koşullu referans |
| 3. Belirsiz | `s = d`, ama `mo_auth` ve M0 boş | 1 (`iscgem:7704315`, 2005-10-21, Mw 4,96) | Ayrı işaretli; kesin referans sayılmaz |

- **Vekil grubun sınırı:** Ms tabanlı mı, mb tabanlı mı olduğu **olay başına verilmiyor**. Bu nedenle bağıntı karşılaştırmalarında vekil grup tek parça bir "Ms → Mw" ya da "mb → Mw" örneği olarak kullanılamaz.
- **Kalite sınıfı:** Kaynaktaki Mw kalite sınıfı A yalnız doğrudan grupta görülüyor (49 717); vekiller B (7 712) veya C (15 219).
- **"Birden fazla yöntemle değerlendirilmiş" kategorisi:** Kaynak alanlarında böyle bir kategori yok. Her ana katalog olayı d ya da p olarak işaretli.

**Vekil oranı döneme göre** (yalnız sayım; ek analiz yapılmadı):

| Dönem | Olay | Vekil Mw | Oran |
|---|---|---|---|
| 1904–1963 | 9 625 | 9 089 | %94 |
| 1964–1979 | 11 449 | 8 760 | %77 |
| 1980–2021 | 53 085 | 5 082 | %10 |

Dolayısıyla 1980 öncesinin Mw değerleri büyük ölçüde vekildir. EQ-Live'daki yerel ve küresel bağıntı karşılaştırmalarında ISC-GEM'i bağımsız bir doğrudan Mw referansı olarak kullanmak yalnız grup 1 için geçerlidir. Grup 2 kullanılırsa, karşılaştırılan bağıntı ISC-GEM'in kendi Ms/mb → Mw bağıntısıyla karşılaştırılmış olur.

## 5. Vekil Mw ve b-değeri: önerinin sınanması (2026-10-26)
**Öneri (ChatGPT):** Varsayılan b-değerinde yalnız doğrudan Mw kullanılsın, vekil Mw seçenek olarak kalsın.

**Sınanan varsayım:** Doğrudan Mw alt kümesi, Mc üstünde tam bir örneklem ise b-değeri için yansız olur. Bu yalnız doğrudan Mw'nin varlığı büyüklükten bağımsızsa geçerlidir.

**Sayım:** Doğrudan Mw (M0 kaynağı belli) / tüm olaylar, ISC-GEM Mw'ye göre. Yalnız sayım; b-değeri hesaplanmadı.

| Dönem | <5,5 | 5,5–6,0 | 6,0–6,5 | 6,5–7,0 | 7,0–7,5 | ≥7,5 |
|---|---|---|---|---|---|---|
| 1904–1963 | %7 (18/257) | %1 (40/4 053) | %3 (117/3 510) | %10 (122/1 165) | %25 (107/422) | %61 (132/218) |
| 1964–1975 | %4 (90/2 294) | %7 (298/4 076) | %30 (329/1 090) | %56 (184/331) | %73 (77/105) | %94 (44/47) |
| 1976–1979 | %38 (574/1 491) | %43 (663/1 535) | %86 (277/323) | %97 (105/108) | %100 (34/34) | %93 (14/15) |
| 1980–2021 | %92 (31 573/34 369) | %85 (11 233/13 274) | %94 (3 585/3 797) | %97 (1 105/1 135) | %99 (344/346) | %99 (162/164) |

**Sonuç:**
- **1976 öncesi:** Doğrudan Mw'nin varlığı büyüklükle güçlü biçimde artıyor (1904–1963'te %1'den %61'e). Bunun nedeni, literatür momentinin büyük depremler için aranmış olması (Lee ve Engdahl 2015) ve GCMT'nin 1976'da başlaması. Bu dönemde "yalnız doğrudan Mw" büyüklüğe bağlı bir seçimdir. Frekans–büyüklük dağılımında küçük depremleri sistematik olarak eksiltir ve b-değerini aşağı çeker. Bu nedenle varsayılan b-değeri için uygun değildir.
- **1980–2021:** Oran %85–99, ancak 5,5–6,0 aralığında daha düşük (%85). Seçim etkisi küçük ama sıfır değil.
- **Kullanım ayrımı:**
  - Dönüşüm bağıntılarını bağımsız referansa karşı sınamak için doğru grup yalnız doğrudan Mw'dir. Bu kullanımda tamlık gerekmez; öneri burada geçerli.
  - b-değeri için tamlık gerekir. Vekilleri dışlamak, dönüşüm kaynaklı belirsizlikten daha büyük bir seçim yanlılığı getirir.

**Önerilen ilke (uygulanmadı; arayüz değişikliği yok):**

| Kullanım | Varsayılan küme | Seçenek |
|---|---|---|
| Dönüşüm bağıntılarının sınanması | Yalnız doğrudan Mw (GCMT ve literatür, kaynak korunarak) | — |
| b-değeri, Mc | ISC-GEM ana katalogun tüm Mw değerleri (kaynağın homojen Mw'si; vekiller dahil) ve sonuçta vekil oranı gösterilir | "Yalnız doğrudan Mw": yalnız 1976 sonrası pencerelerde, seçim uyarısıyla |
| Yöntemi belirsiz Mw (1 olay) | Bağıntı sınamasında dışarıda | — |

- **Değişmeyenler:** `iscgem_global.json` alanları ve sınıflama aynı kalır. Vekil değerler silinmez ve değiştirilmez.
- **Ek bir değerlendirme gerekirse:** Vekil Mw'nin b-değerine etkisi (örneklem sayısı, Mc, aralık; 1980 sonrası doğrudan ve tüm küme karşılaştırması) ayrı bir analiz olarak önerilecek. Bu aşamada yapılmadı.
