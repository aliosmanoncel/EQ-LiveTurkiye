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
