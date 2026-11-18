# Sonuç — PMSR örneklem dışı test, SCSN bölge kutusu 2018–2026

Ön kayıt: `ON_KAYIT.md` (commit b44b906, 2026-11-19 00:44 +03; sonuçlardan önce). Kod: `pmsr-core-0.1.0`, varsayılanlar; parite testi (2008–2017) "BİREBİR AYNI".
Çalıştırma: `python3 build_catalog.py <klasör>` → `node run_pmsr.mjs`. Ana şok bazında tablo: `sonuclar_2018_2026.csv`; özet: `ozet.json`; katalog bilgisi: `catalog_info.json`; doğrulama: `DOGRULAMA.md`.

> **Düzeltme (2026-11-19):** a8776c1'deki ilk sonuçlar (8/48, %16,7) bir hatadan etkilenmişti. Katalog CSV'sinde sayısal zaman sütunu 6 anlamlı basamağa yuvarlanmıştı (yaklaşık 3 saatlik çözünürlük). Doğrulama sırasında bulundu; zaman artık metin alanından okunuyor ve sütun tam yazılıyor (`DOGRULAMA.md` §3). Aşağıdaki tüm değerler düzeltilmiş çalıştırmadandır. Ön kayıt etkilenmedi.

## Veri
Bölge kutusunda 2017-01-01 – 2026-11-17 arasında 230 954 olay (eq 224 786, qb 6 168; büyüklük türü %99,6 ML). 2019'da Ridgecrest nedeniyle 64 987 olay.

## Ana şok seçimi (2018-01-01 – 2026-11-17)
| | Aday (M≥4) | Fixed | Mag-Dep | Combined |
|---|--:|--:|--:|--:|
| 2018–2026 | 187 | 66 | 57 | 52 |
| 2009–2017 (yeniden üretim) | 90 | 63 | 64 | 61 |

## Birincil sonuç
| Dönem | Analiz edilen | Anlamlı (p<0,01) | Oran | Wilson %95 |
|---|--:|--:|--:|--:|
| 2018–2026 | 49 (3 Mc yetersiz) | 12 | %24,5 | %14,6–38,1 |
| 2008–2017 | 58 | 15 | %25,9 | %16,3–38,4 |

İki yönlü Fisher kesin testi: **p = 1,00** (odds oranı 0,93; scipy ile doğrulandı). H0 reddedilmedi; iki dönemin oranları neredeyse aynı. Ön kayıtta belirtildiği gibi aralıklar geniştir: yaklaşık ±12 puanlık farklar bu örneklemle dışlanamaz. Makale değeri (SCSN %22, 16/74) iki aralığın da içindedir.

Type A (M≥3, Mc kesmesiz, 20 gün, 10 km, ≥1 olay): 19/52 (%37); 2008–2017: 24/61 (%39); makale %35.

## Duyarlılık (önceden belirlenmiş)
| Analiz | Analiz edilen | Anlamlı | Oran | Wilson %95 | Fisher p |
|---|--:|--:|--:|--:|--:|
| Nedensel Mc | 47 (5 yetersiz) | 12 | %25,5 | %15,3–39,5 | 1,00 |
| Ridgecrest bölgesi/yılı hariç (4 ana şok) | 45 | 10 | %22,2 | %12,5–36,3 | 0,82 |
| Muhafazakâr p < 0,01 | — | 0 | — | — | — (17 bağımsız pencereyle en küçük p ≈ 0,056; tanım gereği 0) |

Birincil sonuç her duyarlılıkta değişmedi.

## Önemli tek tek olaylar
- **Ridgecrest Mw 6,4 (2019-07-04):** N₂₀ = 8, p = 0 → anlamlı. Canlı USGS sonucuyla (N₂₀ = 8, p = 0; ön kayıt §5) aynı.
- **Ridgecrest Mw 7,1 (2019-07-06):** N₂₀ = 556, p = 0 → anlamlı. Artış Mw 6,4 ve onu izleyen diziden gelir; Mw 7,1 Fixed kuralını geçer çünkü önceki olay daha küçüktür.
- Diğer 10 anlamlı ana şok M 4,06–5,21. Üçü aynı gün (2026-05-10, Imperial Valley, 32,97 K −115,55 B): kural gereği yalnız *önceki* büyük olaylar dışlandığından, bir dizinin artan büyüklükteki olaylarının her biri ayrı ana şok sayılabiliyor. Bu, yöntemin (Khan vd.) bir özelliğidir; 2008–2017'de de aynı kural uygulandı.

## Ön kayıttan sapma
Yok. (Ridgecrest bölgesi tanımında haversine mesafesi kullanıldı; ön kayıtta mesafe türü belirtilmemişti.)

## Sınırlılık
Combined ana şokların tercih edilen büyüklük türü dönemler arasında farklı (2008–2017: Mw 32 / ML 27 / Mh 2; 2018–2026: Mw 51 / ML 1). Yalnız Mw ana şoklarla keşifsel karşılaştırma: 7/31 (%22,6) ↔ 12/49 (%24,5), Fisher p = 1,00. Ayrıntı: `DOGRULAMA.md` §4.

## Etiket
Sonuçlar "ana şok öncesi anlamlı oran artışı"dır; "öncü" etiketi kullanılmaz.
