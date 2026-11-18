# Sonuç — PMSR örneklem dışı test, SCSN bölge kutusu 2018–2026

Ön kayıt: `ON_KAYIT.md` (commit b44b906, 2026-11-19 00:44 +03; sonuçlardan önce). Kod: `pmsr-core-0.1.0`, varsayılanlar; parite testi (2008–2017) hâlâ "BİREBİR AYNI".
Çalıştırma: `python3 build_catalog.py <klasör>` → `node run_pmsr.mjs`. Ana şok bazında tablo: `sonuclar_2018_2026.csv`; özet: `ozet.json`; katalog bilgisi: `catalog_info.json`.

## Veri
Bölge kutusunda 2017-01-01 – 2026-11-17 arasında 230 954 olay (eq 224 786, qb 6 168; büyüklük türü %99,6 ML). 2019'da Ridgecrest nedeniyle 64 987 olay.

## Ana şok seçimi (2018-01-01 – 2026-11-17)
| | Aday (M≥4) | Fixed | Mag-Dep | Combined |
|---|--:|--:|--:|--:|
| 2018–2026 | 187 | 66 | 55 | 51 |
| 2009–2017 (yeniden üretim) | 90 | 63 | 64 | 61 |

## Birincil sonuç
| Dönem | Analiz edilen | Anlamlı (p<0,01) | Oran | Wilson %95 |
|---|--:|--:|--:|--:|
| 2018–2026 | 48 (3 Mc yetersiz) | 8 | %16,7 | %8,7–29,6 |
| 2008–2017 | 58 | 15 | %25,9 | %16,3–38,4 |

İki yönlü Fisher kesin testi: **p = 0,34** (odds oranı 0,57; scipy ile doğrulandı). H0 reddedilmedi. Ön kayıtta belirtildiği gibi bu "oranlar aynı" anlamına gelmez: güven aralıkları geniştir ve yaklaşık 10 puanlık fark bu örneklem büyüklüğüyle ayırt edilemez. Makale değeri (SCSN %22, 16/74) her iki aralığın içindedir.

Type A (M≥3, Mc kesmesiz, 20 gün, 10 km, ≥1 olay): 12/51 (%24); 2008–2017: 24/61 (%39).

## Duyarlılık (önceden belirlenmiş)
| Analiz | Analiz edilen | Anlamlı | Oran | Fisher p |
|---|--:|--:|--:|--:|
| Nedensel Mc | 46 | 8 | %17,4 | 0,35 |
| Ridgecrest bölgesi/yılı hariç (4 ana şok) | 44 | 7 | %15,9 | 0,33 |
| Muhafazakâr p < 0,01 | — | 0 | — | — (17 bağımsız pencereyle en küçük p ≈ 0,056; tanım gereği 0) |

Birincil sonuç her üç duyarlılıkta da değişmedi.

## Önemli tek tek olaylar
- **Ridgecrest Mw 6,4 (2019-07-04):** SCSN ile N₂₀ = 2, p = 0,013 → **anlamlı değil** (sınırda). Ön kayıtta bildirilen canlı USGS sonucu (N₂₀ = 8, p = 0) burada tekrarlanmadı; fark katalog (USGS ComCat ↔ SCEDC yıllık dosyası) ve buna bağlı Mc/olay kümesi farkından kaynaklanıyor. Bu, sonucun katalog seçimine duyarlı olabileceğini gösteren somut bir örnektir.
- **Ridgecrest Mw 7,1 (2019-07-06):** N₂₀ = 541, p = 0 → anlamlı. Artışın kaynağı Mw 6,4 ve onu izleyen dizidir; Mw 7,1, Fixed kuralını geçer çünkü önceki olay daha küçüktür.
- Diğer 7 anlamlı ana şok M 4,06–5,21; ikisi aynı gün (2026-05-10, Imperial Valley, 32,97 K −115,55 B).

## Ön kayıttan sapma
Yok. (Ridgecrest bölgesi tanımında haversine mesafesi kullanıldı; ön kayıtta mesafe türü belirtilmemişti.)

## Etiket
Sonuçlar "ana şok öncesi anlamlı oran artışı"dır; "öncü" etiketi kullanılmaz.
