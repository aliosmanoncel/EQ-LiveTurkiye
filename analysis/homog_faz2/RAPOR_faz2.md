# Faz 2 — 1904–1962 için üç yaklaşımın karşılaştırması (2026-10-21)

**Durum:** karşılaştırma raporu; seçim yapılmadı. Üretim kodu, `eq_historical.json`, GK74 kodu, `mw_authority.json` ve mevcut tamlık merdiveni değiştirilmedi (`homog-faz0` dalı). Betikler: `fetch_isc_nofilter.py`, `faz2_compare.py`; sonuçlar `out/faz2_karsilastirma.json`, (c) aday olayları `out/c_eklenen_aday_olaylar.json`.

## Seriler ve önceden tanımlı kurallar
- **A** — mevcut katalog (1904–1962), büyüklük `mw ?? mag`.
- **(a)** — ISC Bulletin, büyüklük süzgeci yok, tüm büyüklükler (QuakeML). Büyüklük seçimi: Mw > (sığ) Ms > mb > diğer / (derin) mb > Ms > diğer; yazar önceliği ISC > GUTE > PAS > B&D > MOS. İki biçimde: ham seçilen büyüklük ve yalnız Scordilis (2006) geçerlilik aralığında Mw.
- **(b)** — ISC-GEM v12.1 ana katalog, Mw (doğrudan 18, vekil 389). Doğrudan/vekil ayrımı GK74 bütün katalogda uygulandıktan sonra yapıldı.
- **(c)** — (b) + (a)'nın (b) ile eşleşmeyen olayları. Eşleştirme yalnız kataloglar arası, zaman–konum (Tablo 2; 1940 öncesi ΔR = 250 km uyarlaması). (a)'daki bir olay ISC-GEM **ek kataloğuyla** eşleşiyorsa (ISC-GEM'in konum/büyüklüğü güvenilir bulmadığı olay) eklenmedi; ek katalog dahil hâli ayrı duyarlılık serisi.
- Ölçütler: T = 59 yıl; λ = N/T ± √N/T; Aki (1965) b ± b/√N; Weichert (1980) b (tek dönem; sentetik b = 1 verisinde 0,99–1,00 buldu); Mc maksimum eğrilik + 0,2 (bilgi amaçlı).

## (a) süzgeçsiz ISC çekiminin envanteri
- 59 yılın hepsi başarılı (hatalı yıl 0), 1.806 olay; tercih edilen kökeni kutu dışında olan 41 olay çıkarıldı.
- **Kutu içi 1.765 olayın 1.405'inde (%80) ISC Bulletin'de hiç büyüklük yok.** Büyüklüğü olan 360 olaydan 125'i Mw'ye çevrilemeyen türde (çoğu ATH ve MOS "M"). Seçilen türler: ISC Ms 127, PAS Ms 95, ATH 54, MOS 50, P&S Mw 13.
- (a)'da ham büyüklüğü ≥ 5,5 olan 194 olaydan yalnız 31'i A'da yok → **süzgeci kaldırmak eksikliğin küçük bir kısmını geri getiriyor**; asıl sorun ISC Bulletin'de büyüklüğün bulunmaması.

## Karşılaştırma (1904–1962)

| Seri | GK74 | N (M ≥ 5,0) | 5,5–6,0 | ≥ 6,0 | λ(≥5,5) /yıl | λ(≥6,0) /yıl | b Aki (M ≥ 5,5) | b Weichert |
|---|---|---|---|---|---|---|---|---|
| A mevcut | öncesi | 166 | 77 | 86 | 2,76 ± 0,22 | 1,46 ± 0,16 | 0,73 ± 0,06 | 0,55 ± 0,07 |
| A mevcut | sonrası | 150 | 65 | 83 | 2,51 ± 0,21 | 1,41 ± 0,15 | 0,69 ± 0,06 | 0,50 ± 0,07 |
| (a) ham büyüklük | öncesi | 281 | 95 | 99 | 3,29 ± 0,24 | 1,68 ± 0,17 | 0,75 ± 0,05 | 0,60 ± 0,06 |
| (a) ham büyüklük | sonrası | 231 | 79 | 93 | 2,92 ± 0,22 | 1,58 ± 0,16 | 0,72 ± 0,05 | 0,56 ± 0,06 |
| (a) Scordilis Mw | öncesi | 235 | 103 | 92 | 3,31 ± 0,24 | 1,56 ± 0,16 | 0,68 ± 0,05 | 0,54 ± 0,06 |
| (a) Scordilis Mw | sonrası | 200 | 86 | 86 | 2,92 ± 0,22 | 1,46 ± 0,16 | 0,65 ± 0,05 | 0,49 ± 0,06 |
| **(b) ISC-GEM** | öncesi | 407 | 251 | 102 | 5,98 ± 0,32 | 1,73 ± 0,17 | 1,03 ± 0,06 | 0,97 ± 0,06 |
| **(b) ISC-GEM** | sonrası | 306 | 177 | 89 | 4,51 ± 0,28 | 1,51 ± 0,16 | 0,91 ± 0,06 | 0,84 ± 0,06 |
| (c) birleşik | öncesi | 414 | 257 | 103 | 6,10 ± 0,32 | 1,75 ± 0,17 | 1,04 ± 0,06 | 0,98 ± 0,06 |
| (c) birleşik | sonrası | 313 | 183 | 90 | 4,63 ± 0,28 | 1,53 ± 0,16 | 0,92 ± 0,06 | 0,85 ± 0,06 |
| (c) + ISC-GEM ek katalog | sonrası | 353 | 200 | 94 | 4,98 ± 0,29 | 1,59 ± 0,16 | 0,92 ± 0,05 | 0,85 ± 0,06 |

Mc (maks. eğrilik): A ve (a) 5,8–6,0; (b) ve (c) 5,7. Dönem ayrımı (GK74 sonrası, 5,5–6,0 / ≥ 6,0): A 1904–1939 39/44, 1940–1962 26/39 · (b) 98/53 ve 79/36.

## (c) birleşik kataloğun içeriği
- (a)'nın 192 olayı ISC-GEM ana kataloğuyla eşleşti (ISC-GEM'in 188 olayı). Mw'si olup eşleşmeyen 58 olaydan **51'i ISC-GEM ek kataloğunda** → eklenmedi.
- **(c)'ye eklenen yalnız 7 olay**, hepsi PAS (Pasadena) Ms 5,25–6,0 ve çoğu kutu sınırında (enlem 45,0; boylam 23,0). (c), (b)'ye göre λ(≥5,5)'i %2,6 artırıyor; b değişmiyor (0,91 → 0,92).
- PAS Ms'lerine Scordilis (2006) uygulanması doğrulanmadı (ör. Ms 5,25 → Mw 5,59); bu 7 olayın Mw'si belirsiz.

## Bulgular (kanıt düzeyiyle)
1. **Doğrulandı:** ISC Bulletin 1904–1962'de kutu içi olayların %80'inde büyüklük yok; süzgeçsiz çekim (a) eksikliği gidermiyor ve A ile benzer düşük b (0,65–0,75) veriyor.
2. **Doğrulandı:** ISC-GEM (b), A'ya göre M 5,5–6,0'da 2,7 kat (GK74 sonrası 177 / 65), M ≥ 6,0'da %7 daha fazla olay içeriyor; λ(≥5,5) 4,51 / 2,51.
3. **Doğrulandı:** (c), (b)'ye anlamlı bir şey eklemiyor (7 olay, belirsiz Mw).
4. **Belirsiz:** (b)'de 1963 öncesi Mw'nin %96'sı vekil (Ms/mb'den ISC-GEM bağıntıları). b ≈ 0,9'un ne kadarının vekil bağıntılarından geldiği bu veriyle ayrılamıyor; doğrudan Mw alt kümesi (18 büyük olay) karşılaştırma için uygun değil.
5. **Belirsiz:** A ve (a)'daki b ≈ 0,7 ile Aki–Weichert farkının (0,69 / 0,50) nedeni eksik M 5,5–6 olaylarıyla dağılımın bozulması olabilir; doğrulanmadı.

## Karar için seçenekler (seçim yapılmadı)
- **(b) birincil:** 1904–1962 için ISC-GEM; her olayda `mw_src` = iscgem_direct / iscgem_proxy; ek katalog dışarıda. En tutarlı ve yeniden üretilebilir seçenek; tek kaynaklı, belgeli, sürümlü (v12.1, SHA-256 kayıtlı).
- **(c) duyarlılık olarak:** ana sonuçlara 7 olayın etkisini göstermek için.
- **(a) yalnız tanı:** ana katalog için uygun değil.
Seçimden önce açık konu: 1963 sınırında ISC-GEM'den mevcut ISC/EMSC dönemine geçişin (yinelenen ve büyüklük ölçeği değişen olaylar) ayrıca sınanması.
