# Faz 1 / Adım 1 — ISC-GEM doğrulaması (2026-10-21)

Ana kod, `data/eq_historical.json`, GK74 ve `mw_authority.json` değiştirilmedi. Çalışma `homog-faz0` dalında.

## 1. Kaynak ve bütünlük
| | |
|---|---|
| Resmî kaynak | isc.ac.uk/iscgem/download.php → istek formu (ad, e-posta, kurum, ülke, captcha); doğrudan dosya adresi yok |
| Sürüm | 12.1, 2025-11-26 (dosya başlığından) |
| Dosyalar | `isc-gem-cat.csv` 74.159 olay (1904–2021), `isc-gem-suppl.csv` 9.834 olay, KMZ |
| SHA-256 | zip 92a52fb9…49c5 · ana b4e63841…cc8d · ek 1ea390ab…1bf (tam değerler `out/LISANS_ISC-GEM.txt`) |
| Ayrıştırma | 31 sütun, hatalı satır 0; başlık sırası dosyadaki açıklamayla aynı |
| Lisans | CC BY-SA 3.0; türetilmiş dosyalar aynı lisansla, atıf: ISC (2025) doi:10.31905/D808B825 |

**Eşleştirme için gereken alanlar mevcut:** tarih-saat (0,01 s), enlem/boylam + hata elipsi ve kalite (A/B/C), derinlik + belirsizlik + kalite, **Mw + belirsizlik + kalite + kaynak (d = doğrudan, p = vekil)**, M0 ve kaynağı (gcmt / bibliog), olay kimliği.

## 2. EQ-Live kutusunda (33–45° K, 23–48° D) kapsam
Ana katalog 1.439 olay (ek katalog 623). Mw kaynağı: doğrudan 643 (A 571, B 61, C 11), vekil 796 (B 321, C 475).
1976 öncesi Mw neredeyse tamamen vekil (mb/Ms'ten ISC-GEM bağıntılarıyla); 1976 sonrası çoğunlukla GCMT'den doğrudan. **Mw < 5,0 yok denecek kadar az (30 olay)** — beklendiği gibi ISC-GEM 4,5–5 boşluğunu kapatmıyor.

## 3. Eşleştirme (yalnız zaman + konum; ΔM tanı)
Tablo 2 ΔT/ΔR; 1940 öncesi ΔR tanımsız olduğundan 250 km üst sınır eklendi (uyarlama). 1.147 çift, 12'sinde birden çok aday (en yakını seçildi), eşleşmeyen ISC-GEM olayı 294.

**ISC-GEM olaylarının EQ-Live kataloğunda bulunma oranı:**

| Dönem | Mw 5,0–5,5 | 5,5–6,0 | ≥ 6,0 |
|---|---|---|---|
| 1904–1939 | %8 (2/25) | %23 (30/132) | **%58 (36/62)** |
| 1940–1962 | %0 (0/29) | %29 (35/119) | **%78 (31/40)** |
| 1963–1975 | %95 | %86 | %100 |
| 1976–1997 | %100 | %100 | %91–100 |
| 1998–2021 | %100 | %100 | %100 |

**Yeni ve önemli bulgu: EQ-Live'ın 1963 öncesi kataloğu eksik.** 1904–1962 arasında ISC-GEM'deki M ≥ 6 olayların 35'i EQ-Live'da yok (ör. 1905-11-08 Mw 7,24 Aynaroz; 1912-09-13 Mw 6,72). Olası neden: ISC FDSN sorgusunun büyüklük süzgeci (Mc 5,5) erken dönem kayıtlarında eksik ya da farklı tercih edilmiş büyüklükle çalışıyor. Bu, ana kod değişikliğinden bağımsız olarak düzeltilmesi gereken bir tamlık sorunu.

## 4. Referans kapsamı: ComCat'e göre ne iyileşti? (EQ-Live olayı başına referans Mw bulunabilirliği)

| Dönem · EQ-Live M | N | ComCat Mw | ISC-GEM | ikisinden biri |
|---|---|---|---|---|
| 1963–1975 · 4,5–5,0 | 587 | 148 | 125 | 191 (%33) |
| 1963–1975 · 5,0–5,5 | 115 | 80 | 73 | 95 (%83) |
| 1976–1989 · 4,5–5,0 | 673 | 0 | 66 | 66 (%10) |
| 1976–1989 · 5,0–5,5 | 112 | 28 | 68 | 68 (%61) |
| 1976–1989 · ≥ 5,5 | 47 | 13 | 46 | 46 (%98) |
| 1990–1997 · 4,5–5,0 | 249 | 0 | 22 | 22 (%9) |
| 1990–1997 · 5,0–5,5 | 65 | 34 | 42 | 42 (%65) |
| 1998–2021 · 4,5–5,0 | 1.302 | 182 | 129 | 233 (%18) |
| 1998–2021 · 5,0–5,5 | 271 | 217 | 238 | 250 (%92) |

**Gerçekten iyileşen:** 1976–1997 arası M ≥ 5,0 (ComCat'te bu dönemde Mw çok seyrek). **İyileşmeyen:** 1963–1997 arası EQ-Live M 4,5–5,0 (referans Mw %9–33).

## 5. Tanı: ΔM = M_EQ-Live − Mw_ISC-GEM
| Tür · ISC-GEM Mw kaynağı | n | ort. | std |
|---|---|---|---|
| Mw · doğrudan | 357 | −0,03 | 0,10 |
| mb · doğrudan | 223 | −0,21 | 0,23 |
| mb · vekil | 316 | −0,36 | 0,15 |
| Ms · doğrudan | 54 | −0,34 | 0,30 |
| Ms · vekil | 179 | −0,23 | 0,43 |

mb doygunluğu doğrudan Mw ile: Mw 5–5,5 −0,16 · 5,5–6 −0,30 · ≥ 6 −0,56. Vekil Mw kendisi bir dönüşüm olduğundan, `mw_src` alanında **iscgem_direct** ile **iscgem_proxy** ayrı tutulmalı; vekil Mw, "ölçülmüş Mw" ile aynı güvenilirlikte sayılmamalı.

## 6. Sonraki adım (onay bekliyor)
1. 1963 öncesi eksik M ≥ 5,5 olayların nedenini ISC FDSN sorgusunda doğrulamak (ana koda dokunmadan, ayrı sorguyla).
2. Prototip katalog: zaman–konum eşleşmesi; `mw_src` ∈ {iscgem_direct, comcat_mww/mwc/mwr, catalog_native_mw, iscgem_proxy, none}; ham büyüklük korunur.
3. Karşılaştırma (A mevcut / B prototip): dönem × sınıf sayıları, Mc, b ± σ, Weichert λ; GK74 öncesi ve sonrası; önceden tanımlı kabul ölçütleri değişmeden.

---

# 1963 öncesi tamlık incelemesi (Faz 1b, 2026-10-21) — teşhis, düzeltme değil

Betik: `analysis/homog_faz1b/tamlik_1963oncesi.py`; GitHub Actions, `homog-faz0` dalı (21:42–22:02 UTC, başarılı). Olay bazında bütün sorgu adresleri, dönen kayıt sayıları ve büyüklükler: `analysis/homog_faz1b/out/sorgu_kaydi.json`; ham yanıtlar: `out/tamlik_1963oncesi.json`.

## Sorgu koşulları
- Kapsam: ISC-GEM v12.1 ana katalogunda kutu içi 407 olay (1904–1962). Tablo 2 zaman–konum eşiğiyle (1940 öncesi ΔR = 250 km uyarlaması) EQ-Live'da karşılığı olmayan **268 olay** sorgulandı.
- Her olay için iki ISC FDSN sorgusu (`http://www.isc.ac.uk/fdsnws/event/1/query`, `format=text`): zaman ±5 dk, enlem/boylam ±3°;
  **B1** büyüklük süzgeci yok, **B2** `minmagnitude=5.5` (EQ-Live'ın 1900–1965 çekimindeki eşik).
- Yanıt durumu: sorgu hatası 0; HTTP 204 (boş) "kayıt yok" olarak sayıldı.

## Sonuçlar

| Sonuç (B1 / B2) | Olay | Kanıt düzeyi |
|---|---|---|
| ISC olayı döndürüyor, `minmagnitude=5.5` ile döndürmüyor | **246** | Doğrulandı (iki sorgunun sonucu) |
| ISC hiçbir kayıt döndürmüyor (±5 dk, ±3° içinde) | 18 | Doğrulandı: bu pencerede kayıt yok. Olayın ISC'de hiç bulunmadığı **kanıtlanmadı** (pencere dışı konum/zaman olabilir) |
| ISC `minmagnitude=5.5` ile de döndürüyor, EQ-Live'da yok | 4 | Doğrulandı; nedeni belirsiz |

Dönem × sınıf dağılımı (süzgeç / kapsam yok / diğer): 1904–1939 · 5,5–6: 89 / 10 / 0 · ≥ 6: 17 / 7 / 1 — 1940–1962 · 5,5–6: 83 / 0 / 1 · ≥ 6: 9 / 0 / 0. Örnekler: **1905-11-08 Mw 7,24** — ISC'de var (büyüklük 7,8, tür "UK", yazar B&D) ama `minmagnitude=5.5` ile dönmüyor; **1912-09-13 Mw 6,72** — ±5 dk, ±3° içinde ISC kaydı yok.

## Süzgeçte kalan 246 olayın büyüklük bilgisi (B1 yanıtı)
- **192 olayda ISC yanıtında hiç büyüklük yok** → `minmagnitude` koşulu büyüklüğü olmayan olayları dışarıda bırakıyor. *Güçlü kanıt.*
- 41 olayda ISC büyüklüğü < 5,5 (çoğu ISC Ms; ör. ISC-GEM Mw 5,44 ↔ ISC Ms 4,9) → eşik büyüklük türüne göre farklı olayları ayırıyor. *Doğrulandı.*
- 13 olayda yanıtta ≥ 5,5 bir büyüklük var (türler M, MS, Mw, UK; yazarlar PAS, ATH, P&S, UPP, B&D, JER) ama süzgeçten geçmiyor → ISC'nin `minmagnitude` için yalnızca belirli (tercih edilen) büyüklüğü kullandığı düşünülüyor. *Henüz belirsiz* (ISC belgesiyle doğrulanmalı).

## Faz 1c ile birlikte değerlendirme
- Eksikliğin baskın kaynağı **sorgu koşulu (büyüklük süzgeci)**: 268 eksiğin 246'sı (%92) ISC'de mevcut. Kaynak kapsamı en çok 18 olayı (%7) açıklayabilir; 4 olay açıklanmadı.
- Stepp testi bu eksikliği göremedi (Faz 1c): eksik olan, belirli bir büyüklük türüne/büyüklüğün yokluğuna bağlı bir alt küme; oranlar zamanla "kararlı" görünebiliyor.
- Merdivenin yeniden değerlendirilmesi gereken bölümü: **1900–1965 (Mc 5,5, ISC)**. ISC-GEM'e göre bu dönemde M 5,5–6 olayların %23–29'u, M ≥ 6'nın %58–78'i katalogda. 1965 sonrası basamaklar bu incelemede sınanmadı.

## Henüz sınanmamış hipotezler (doğrulanmış sonuç değildir)
1. ISC FDSN `minmagnitude` yalnız tercih edilen büyüklüğe uygulanıyor.
2. 18 "kayıt yok" olayı ISC-GEM'in yeniden konumlandırmasından (> 3° ya da > 5 dk fark) kaynaklanıyor olabilir.
3. 4 olayın kaybı EQ-Live'ın çekim sırasındaki ISC yanıtıyla (2026-09) bugünkü yanıt arasındaki farktan ya da `dedup()`'tan kaynaklanıyor olabilir.
4. mb–Mw kaynaklı sınıf göçü (Faz 1c) — hipotez.

## Olası düzeltme yolları (karar verilmedi, uygulanmadı)
(a) 1963 öncesi ISC'yi büyüklük süzgeci olmadan çekip yerelde süzmek; (b) 1904–1962 için ISC-GEM'i birincil kaynak almak (`mw_src` = iscgem_direct / iscgem_proxy); (c) ikisinin birleşimi. Her biri ayrı karşılaştırma (sayılar, Mc, b, Weichert; GK74 öncesi/sonrası) gerektirir.

## Değişiklik yapılmadığının Git kaydı
- Çalışmanın başındaki depo durumu: `c7d0625`. Bu commit ile `origin/main` (`0e875b0`) arasında korunan dosyalarda fark yok: `data/eq_historical.json` (blob 879a89b9), `data/eq_historical_dc.json` (4ede910b), `data/mw_authority.json` (846e4dca), `scripts/decluster_gk74.py` (5528ae9e), `scripts/gk74_context.py` (320c4d66), `scripts/gk74_mwauth.py` (26ebcec5), `scripts/fetch_combined_catalog.py` (7b049eb3).
- `homog-faz0` dalında da bu dosyalar `origin/main` ile aynı.
- `index.html`'in son değişikliği `dc06459` (2026-10-20 19:12, GNSS özelliği); homojenizasyon çalışması (ilk commit `a2f9f79`, 2026-10-21 00:15) sırasında değişmedi.
