# Dinamik Reasenberg — canlıya alma testi (2026-11-08)

Dinamik Reasenberg, PR #9 ile `main`'e birleştirildi (`45a6a84`); GitHub Pages yayını tamamlandı. Bu belge canlı testi, ölçümlerin hangi teste ait olduğunu ve regresyon testini kaydeder.

## Senaryo (canlı)

- **Bölge:** daire, merkez 37,5 K 37,2 D, yarıçap 100 km (Kahramanmaraş).
- **Pencere:** 2023-03-01 – 2023-12-31, EMSC canlı sorgu, limit 20 000.
- **Tampon:** pencere başından önceki 90 gün; 6 Şubat 2023 ana şokları tamponun içinde.
- **URL:** `?rminlat=36.6&rminlon=36.07&rmaxlat=38.4&rmaxlon=38.33&rcirc=37.5,37.2,100&rfrom=2023-03-01&rto=2023-12-31&rlimit=20000&rsource=emsc`, ardından "🧪 Reasenberg (dinamik)".

| Ölçüm | githack `563d789` | Canlı site `45a6a84` |
|---|---|---|
| Pencere olayı | 6 514 | 6 514 |
| Tampon | 2 354 olay, 90 gün, sınıra takılmadı | aynı |
| Durum | UYARILI (K7 sınır, K8 karışık ölçek); K9 geçti | aynı |
| Bağımsız | 5 561 | 5 561 |
| xmeff (sitenin Mc tahmini) | 2,2 | 2,2 |
| Worker / öz-sınama | etkin / 4/4 | etkin / 4/4 |
| Hesap süresi | 721 ms (8 868 olay) | — |
| Ana iş parçacığında en büyük boşluk | 72 ms | — |

**Tamponsuz ile karşılaştırma (githack):**
- Bağımlı olay sayısı 736 → 953.
- 219 olayın sınıfı değişti (%3,4).
- Pencerenin ilk 30 gününde değişen oran %8,8 (165 / 1 874). Çevrimdışı ölçüm (`zaman_tamponu.json`, %8,4) ile tutarlı.

**GK74 karşılaştırması:** ikisi de bağımsız 475 · ikisi de bağımlı 946 · yalnız GK74 bağımlı 5 086 · yalnız Reasenberg bağımlı 7. Toplam 6 514; GK74'ün 482 ve Reasenberg'in 5 561 bağımsız sayısıyla tutarlı.

Statik GK74/Reasenberg katmanı değişmedi.

**Canlı sayılar zamanla değişebilir:** EMSC kataloğu revize edildikçe değerler kayabilir. Bu yüzden regresyon testi canlı sayıları değil, dondurulmuş fikstürü sınar (aşağıda).

## 53 ms ile 72 ms farkı

İki değer farklı testlere ait:

| Değer | Test | Ortam | Olay sayısı | Ne ölçüldü |
|---|---|---|---|---|
| 53 ms | Yerel | Chromium (Playwright, bulut çalışma ortamı) | 20 000 | Yalnız Worker çağrısı; tampon ve bölge sorgusu yok |
| 72 ms | Canlı | Kullanıcının Chrome'u, githack | 6 514 + 2 354 tampon | Bölge sorgusu, tampon sorgusu ve rapor çizimi dahil (ilk açılışta Pyodide yüklemesi ~30 s) |

İkisi de 50 ms aralıklı bir sayaçla ölçülen en büyük boşluk. Değer ~50 ms'nin hemen üstünde kaldığı için arayüz donmuyor; ölçüm çözünürlüğü yaklaşık ±20 ms.

## Regresyon testi

`scripts/reasenberg_tests/tampon_regresyon.mjs` aynı daire ve pencereyi kullanır. Veri, `scripts/fixtures/reasenberg_tampon_kahramanmaras.json` fikstüründen gelir: depodaki EMSC kataloğu (M ≥ 3,0), xmeff 3,0, 921 pencere olayı + 1 205 tampon olayı.

| Ölçüt | Sınanan |
|---|---|
| T1 | Raporda yalnız pencere olayları var; tampon olayı yok. Site ile aynı `windowOnly` fonksiyonu kullanılır (`rb_core.mjs`). |
| T2 | Tamponlu (bağımlı 191, küme 27) ve tamponsuz (bağımlı 140, küme 31) sonuçlar; 51 sınıf değişimi; ilk 30 günde 38 / 342. Beklenen değerlere birebir eşit olmalı. |
| T3 | Tampon bağımlı sayısını azaltmaz. |

Beklenen değerler CPython ile ayrıca doğrulandı (aynı sonuç). Test CI'da `reasenberg-pyodide.yml` içinde çalışır.
