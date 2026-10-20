# Katalog homojenizasyonu — Faz 0 raporu (2026-10-21)

**Kapsam.** Yalnızca inceleme. `index.html`, `scripts/fetch_combined_catalog.py`, GK74 ve `data/mw_authority.json` değiştirilmedi.
Bütün dosyalar `homog-faz0` dalında. Kaynak yöntem: Candia & Macedo (2026, SRL, doi:10.1785/0220250449), Tablo 2 (dönem eşikleri) ve Tablo 3 (EP puanı) PDF'ten birebir alındı.

## 1. Mevcut birleştirme kodu (`fetch_combined_catalog.py`)
- Kaynaklar zamanda ayrık: ISC 1900–1997, EMSC 1998–. Kimlik (`id`) bazında birleştirildiği için **kaynaklar arası tekrar yalnızca 1998 sınırında olabilir**; `dedup()` pratikte aynı kaynak içindeki yakın kayıtları ayıklar.
- Kural: Δt ≤ 60 s ve Δr < 50 km → **büyüklüğü yüksek olan tutulur** (ΔM ölçütü yok; yüksek değeri seçmek büyüklükleri yukarı çekebilir).
- Yalnız son 30 tutulan olayla karşılaştırır (yoğun artçı dizilerinde eşleşme kaçabilir).
- Mevcut `eq_historical.json` (2026-09-14) içinde 60 s / 50 km ölçütüne uyan **kalan çift yok** (beklenen).

**Tutarsızlıklar (veri dosyası ↔ kod).**
- 10.266 olayda `mw_method = scordilis2006_*` yazıyor ama `mw = null`; etiket eski sürümden kalmış (2026-10-11'den beri veri hattında dönüşüm yok).
- `completeness` meta alanı (1900–1960 / 1960–1998 / 1998–) koddaki merdivenle (1900–1965–1980–1990–1998) uyuşmuyor.
- Sabit/yer tutucu derinlikler (0, 5, 10, 33, 35 km): olayların %48'i.

## 2. Candia & Macedo eşiklerinin katalog içindeki etkisi (`dup_scan.py`)
Aynı kaynak içinde Tablo 2 eşikleriyle 28 aday çift bulundu (`out/dup_pairs.json`). **Önemli:** 1940 öncesi eşikler (ΔT ≤ 200 dk, mesafe ölçütü yok) gerçek ayrı depremleri birleştirir — ör. 1935-01-04 Erdek–Marmara çifti (14:41 ve 16:20, Ms 6,4 ve 6,2) ve 1932'de 822 km arayla iki olay. **Sonuç: Tablo 2 yalnız FARKLI kataloglardan gelen kayıtlar arasında uygulanmalıdır** (makalenin amacı da budur); aynı katalog içinde uygulanırsa öncü/artçı ve çift depremleri siler.
1998 sonrası EMSC içinde 22 aday (Δt ≤ 30 s, Δr ≤ 100 km, ΔM ≤ 0,75; çoğu MD/ML çiftleri) elle incelenmeli: farklı ajans kayıtları olabilir, gerçek yakın olaylar da olabilir.

## 3. Referans Mw ile karşılaştırma (`faz0_reference_match.py`, GitHub Actions)
Referans: USGS ComCat FDSN, M ≥ 4,5 (4.450 olay; Mw türlü 1.846). ISC-GEM indirilemedi (denenen adresler 404) — Faz 1'de doğru dağıtım adresi bulunmalı.
Eşleştirme: Tablo 2 eşikleri, yalnız katalog ↔ referans; 1.308 çift (ortanca Δt 1 s, Δr 6 km).

**Eşleşme oranı (M ≥ 5,5):** 1900–1963 %88 · 1963–1990 %58 · 1990–1998 %89 · 1998– %85. M 4,5–5,0'da 1963–1998 arası neredeyse hiç referans Mw yok → **ISC-GEM gerekli**.

**ΔM = M_katalog − Mw_ComCat (tür bazında):**

| Tür | n | ort. | std |
|---|---|---|---|
| mb | 577 | −0,22 | 0,24 |
| Mw (katalog) | 515 | 0,00 | 0,08 |
| Ms | 173 | −0,06 | 0,29 |
| ML | 39 | +0,02 | 0,17 |

**mb'nin büyüklüğe bağlı sapması ve Scordilis (2006):**

| Mw_ref | ham mb − Mw | Scordilis(mb) − Mw |
|---|---|---|
| 4,5–5,0 (n=143) | +0,01 | **+0,33** |
| 5,0–5,5 (n=340) | −0,27 | +0,02 |
| 5,5–6,0 (n=82) | −0,41 | −0,17 |
| ≥ 6,0 (n=12) | −0,27 | −0,18 |

Scordilis bağıntısı ortalamada mb'yi düzeltiyor (−0,22 → +0,07) ama büyüklüğe bağlı eğilim kalıyor: küçük olaylarda Mw'yi fazla, büyüklerde az veriyor. **Uyarı:** ComCat'te Mw ancak ≈ M ≥ 4,5–5'te var ve eşleştirme ΔM ≤ 0,75–1,0 istiyor; alt uçta seçim (kesme) yanlılığı olabilir — Faz 1'de ISC-GEM ve eşleştirmede ΔM ölçütü olmadan zaman–konum eşleşmesiyle denetlenmeli.

**b-değerine etkisi (Aki 1965; eşleşen olaylarda referans Mw kullanılınca):**

| Dönem | M ≥ 4,5 mevcut | M ≥ 4,5 referans Mw | Mc (maks. eğrilik) mevcut / ref. |
|---|---|---|---|
| 1998– | 1,24 ± 0,03 (N=2.250) | 1,18 ± 0,03 (N=2.269) | 3,2 / 3,2 (b 1,02 / 1,02) |
| 1963–1998 | 1,10 ± 0,03 (N=1.921) | 0,98 ± 0,02 (N=1.921) | 3,7 / 3,7 |
| Tümü | 1,04 ± 0,02 (N=4.337) | 0,97 ± 0,02 (N=4.356) | 3,2 / 3,2 |

Büyük olaylarda gerçek Mw kullanmak b'yi belirsizliğin 2–5 katı kadar değiştiriyor; Mc ve küçük büyüklükteki b etkilenmiyor (orada referans Mw yok).

## 4. Faz 1 test planı (öneri)
1. ISC-GEM'in doğru adresini bulup indir; ComCat + ISC-GEM + GCMT'yi ayrı kaynaklar olarak tut.
2. Eşleştirme: zaman–konum (Tablo 2 ΔT, ΔR); ΔM'yi eşleştirme ölçütü değil, **tanı** olarak raporla (mb doygunluğu yüzünden büyük olaylar dışarıda kalmasın).
3. Büyüklük seçimi: (i) referans Mw (ISC-GEM > GCMT/ComCat Mww > diğer Mw), (ii) yoksa ham büyüklük + isteğe bağlı dönüşüm; her olayda `mw_src` ve `mw_method` alanı. EP puanı (Tablo 3) yalnız birden çok katalogdan gelen aynı olay için.
4. Karşılaştırma: aynı kutu ve merdivenle (A) mevcut, (B) Faz 1 kataloğu; dönem × büyüklük sınıfı olay sayıları, Mc, b ± σ (Aki), Weichert λ; GK74 öncesi ve sonrası.
5. Kabul ölçütü (önceden tanımlı): B'de mb–Mw kalıntı eğilimi |ort.| ≤ 0,1 her büyüklük sınıfında; GK74 kümesizleştirilmiş katalogda b farkı raporlanır, karar bilimsel gerekçeyle verilir; ana koda yalnız bu rapor onaylanınca geçilir.
