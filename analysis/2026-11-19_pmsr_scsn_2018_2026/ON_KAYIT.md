# Ön kayıt — PMSR örneklem dışı test: SCSN bölge kutusu, 2018–2026

**Kayıt tarihi:** 2026-11-19 (bu dosya, 2018–2026 ana şokları için hiçbir PMSR sonucu hesaplanmadan önce commit edilmiştir; commit zaman damgası kayıttır).
**Hazırlayan:** A. O. Öncel (Claude ile).
**Kapsam:** Azad Khan, Werner, Biggs & Fagereng (2025), JGR Solid Earth 130(7), e2024JB030733 yönteminin, yöntemin kurulduğu dönemin (2008–2017) dışındaki SCSN verisine değiştirilmeden uygulanması.

## 1. Soru ve hipotezler

Ana şok öncesi 20 günde anlamlı oran artışı (p < 0,01) gösteren ana şokların oranı, 2018–2026 döneminde 2008–2017 dönemindekiyle aynı mıdır?

- **H0 (birincil):** π(2018–2026) = π(2008–2017). Referans: bağımsız yeniden üretimimiz 15/58 (%25,9) — `analysis/2026-11-18_pmsr_scsn_reproduction/`.
- **Test:** iki yönlü Fisher kesin testi, 2×2 tablo (anlamlı / anlamlı değil × dönem), α = 0,05. Ek olarak her dönem için Wilson %95 güven aralığı ve oran farkı.
- **İkincil (betimleyici):** Khan vd. makale değeri SCSN %22 (16/74) ile karşılaştırma; Type A (M ≥ 3, Mc kesmesiz, 20 gün, 10 km) oranı; makalede Type A %35 (26/74), yeniden üretimde 24/61.

Güç notu: n ≈ 45–60 ile, %26'ya karşı yalnızca yaklaşık ±20 yüzde puanlık farklar güvenilir biçimde ayırt edilebilir. "Fark yok" sonucu "aynı" anlamına gelmez; aralıklar raporlanacaktır.

## 2. Veri (dondurulmuş)

SCEDC yıllık SCEC_DC dosyaları, kullanıcı tarafından 2026-11-18 21:40–21:42 UTC'de indirildi. 2026 dosyası kısmidir (son olay 2026-11-17).

| Dosya | SHA-256 |
|---|---|
| 2017.catalog.txt | 912c84f31fd062450fc5269293b751edbfbeded15419dcfa5e0359808dfe000d (2008–2017 çalışmasındakiyle aynı) |
| 2018.catalog.txt | c5165bfc0e712985c0cbec4176740113380ca2b7f27be07edc69c72102efdbb9 |
| 2019.catalog.txt | 9ec160cacb7582ca45aebb2f893e229c3187832c2176677dee225215d414caa5 |
| 2020.catalog.txt | b8630b0daf90cb5b8e33efbe57e28ac7f9342a53f0dc2a5a7e3dfb85ae1557ef |
| 2021.catalog.txt | eccadce24356a87d2834b55f4ffb39502ffbd028fbfd24bfbffd497fc21c398f |
| 2022.catalog.txt | f64063c5bfbfc59a82a8a011dc6b6c163fe72d17818dd0c5887bb530b6254501 |
| 2023.catalog.txt | 26848025ae638a92c39662d66c2ad304a8ac9af1560774e5ce407d2ae357d9f9 |
| 2024.catalog.txt | f683a19150354f43e28535659ec15e20e4189561d34843b1befa3f0456fb33c4 |
| 2025.catalog.txt | 930f295a7dd2815ef48eea25ace0b69a6e8cb37755e7babf3af2e01f7eeb5fd4 |
| 2026.catalog.txt | abe089de84e67d891c7abf3358ff4b36e74d40e802ecaac3b82660ccc20212ef |

Okuma 2008–2017 çalışmasıyla aynı: yalnız rakamla başlayan satırlar; `MAG` sütunu (tercih edilen büyüklük, tür karışık); olay türü filtresi yok (qb dahil).
Bölge kutusu: boylam −118,80 / −115,40; enlem 32,68 / 36,20 (değişmedi).

## 3. Yöntem (dondurulmuş — `pmsr-core-0.1.0`, `lab/premainshock-rate/core.mjs`, varsayılanlar)

- Ana şok adayı M ≥ 4,0; dönem **2018-01-01 00:00 – 2026-11-17 23:59:59 UTC**. 2017 yalnızca geriye bakış (Fixed, Mag-Dep, kalibrasyon) için kullanılır; katalog başlangıcı 2017-01-01.
- Seçim: Combined = Fixed (365 gün, 10 km, daha büyük olay yok) ∧ Mag-Dep (R = 20 + 5·10^((M−4,38)/1,49) km, T = 50 + 25(M−4) gün; yalnız önceki büyük olaylar).
- Yerel Mc: MBS (ΔM 0,4, bin 0,1), yarıçap 10 → 50 km (5 km adım), en az 275 olay; **tüm katalog dönemi (2017–2026)** — 2008–2017 çalışmasıyla aynı (mcCausal = false).
- ESR: 20 gün / 10 km; kalibrasyon 365 → 20 gün önce; 0,01 gün adımlı kayan pencereler; p = pay(sayı ≥ N_obs); anlamlı p < 0,01.
- Analiz edilemeyenler (Mc için < 275 olay) paydadan çıkarılır ve ayrıca raporlanır.

## 4. Duyarlılık (önceden belirlenmiş, birincil sonucu değiştirmez)

1. **Nedensel Mc** (mcCausal = true; yalnız ana şoktan önceki olaylar).
2. **Ridgecrest hariç:** 2019-07-04 – 2020-07-03 arasında ve Mw 7,1 merkez üssüne 50 km içindeki ana şoklar çıkarılmış hâli (SCEDC: dizi M 2,5 altında büyük ölçüde gözden geçirilmemiş).
3. **Muhafazakâr p** (17 bağımsız pencere, (k+1)/(n+1)) ile anlamlı sayısı — bilgi amaçlı.

## 5. Önceden bilinenler (açıklama)

- Ridgecrest Mw 6,4 (2019-07-04) için canlı USGS kataloğuyla anlamlı artış (N₂₀ = 8, p = 0) daha önce EQ-Live testinde görüldü. Bu, 2018–2026 ana şoklarından yalnızca biri hakkında önceden bilgi demektir; başka hiçbir sonuç görülmedi.
- Yöntem ve kod 2008–2017 verisiyle doğrulandı (58/58 Mc ve ESR eşleşmesi); bu çalışma için hiçbir parametre değiştirilmeyecektir.

## 6. Raporlama

Ana şok bazında tablo (CSV), sayılar, Fisher p, Wilson aralıkları, duyarlılık sonuçları. Sonuçlar "öncü" değil, "ana şok öncesi anlamlı oran artışı" olarak etiketlenir. Ön kayıttan herhangi bir sapma ayrı bir bölümde gerekçesiyle yazılır.

## 7. Veri yeniden kullanımı

Hazırlanan bölge kataloğu (2017–2026, CSV.gz) b-değerinin zamanla değişimi gibi ayrı çalışmalarda da kullanılabilecek biçimde saklanır; o çalışmalar bu ön kaydın kapsamı dışındadır.
