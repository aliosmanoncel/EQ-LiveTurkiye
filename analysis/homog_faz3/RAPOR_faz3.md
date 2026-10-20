# Faz 3 — ISC-GEM Mw aktarımı (1904–2021), prototip doğrulaması (2026-10-21)

**Karar (kullanıcı):** ISC-GEM Mw, 1904–2021 boyunca eşleşen olaylara aktarılır; `mw_src` ile kaynak ayrı tutulur; ISC-GEM'de karşılığı olmayan olayların büyüklüğü değişmez, tahminî Mw atanmaz. Üretim kodu, `eq_historical.json`, GK74 kodu, `mw_authority.json` ve tamlık merdiveni değiştirilmedi (`homog-faz0` dalı). Betik `faz3_mw_aktarim.py`; sonuç `out/faz3_rapor.json`; olay bazında aktarım kaydı `out/aktarim_kaydi.json` (1.130 satır; eski M, tür, yeni Mw, kaynak, ISC-GEM kimliği, Δr). Girdilerin SHA-256 özetleri raporda.

## Kurallar (önceden tanımlı)
- 1904–1962: ISC-GEM birincil; A'nın eşleşmeyen olayları olduğu gibi kalır. 1963–2021: A korunur, eşleşen olaya ISC-GEM Mw atanır; A'da karşılığı olmayan ISC-GEM olayı eklenmez. 2022–: değişmez.
- Eşleştirme: zaman–konum (Tablo 2), bire-bir (en yakın önce). Koruma: |M_A − Mw| > 1,0 ise aktarım yapılmaz.
- `mw_src` (güncel kural): `iscgem_direct` 641 · `iscgem_proxy` 776 · `catalog_native_mw` 1.214 · `catalog_raw_<tür>` 85.975.

## Sayılar
A 88.333 olay → prototip 88.606. Eşleşen çift 1.145; Mw aktarılan 1.144 (kural güncellemesinden önce 1.130); koruma nedeniyle aktarılmayan 1 (önce 15); 1963 öncesi ISC-GEM'den eklenen 273; 1963 öncesi A'nın eşleşmeyen ve olduğu gibi kalan 33 olayı; 1963–2021'de A'da karşılığı olmayan ve eklenmeyen ISC-GEM olayı 21.

## Doğrulama testleri
| Test | Sonuç |
|---|---|
| T1 Bire-bir (bir ISC-GEM olayı en çok bir kez) | ✓ |
| T2 Eşleşmeyen 87.189 olayın büyüklüğü değişmedi | ✓ (değişen 0) |
| T3 Aktarılan 1.417 Mw, ISC-GEM değeriyle birebir aynı | ✓ (farklı 0) |
| T4 Ham `mag`/`mtype` her kayıtta saklı | ✓ |
| T5 Tahminî/dönüştürülmüş Mw yok | ✓ |
| T6 2022 sonrası değişmedi | ✓ |
| T8 Süreklilik (kabul: her blokta 0,85 ≤ P/ISC-GEM ≤ 1,15 ve 1963 sıçraması ≤ 0,15) | ✓ |

**Süreklilik, GK74 sonrası, olay sayısı (P = prototip, A = mevcut):**

| Blok | M ≥ 5,5: P / ISC-GEM / A | P/ISC-GEM | A/ISC-GEM | M ≥ 6,0: P/ISC-GEM | A/ISC-GEM |
|---|---|---|---|---|---|
| 1949–1962 | 65 / 61 / 38 | 1,07 | 0,62 | 1,10 | 0,95 |
| 1963–1977 | 73 / 78 / 47 | 0,94 | 0,60 | 1,00 | 1,12 |
| 1978–1997 | 50 / 52 / 47 | 0,96 | 0,90 | 0,95 | 0,90 |
| 1998–2021 | 90 / 88 / 73 | 1,02 | 0,83 | 1,00 | 0,83 |

1963'teki yapay düşüş (A/ISC-GEM 0,60) giderildi (P/ISC-GEM 0,94); 1963 sıçraması M ≥ 5,5'te −0,13, M ≥ 6,0'da −0,10 (kabul sınırı içinde). Kalan küçük fark, 1963 öncesinde A'nın eşleşmeyen 33 olayının korunmasından kaynaklanıyor.

**Tanı, ΔM = M_A − Mw_ISC-GEM:** 1963–1997 mb −0,37, Ms −0,45, Mw 0,00 · 1998–2021 mb −0,21, Ms −0,42, Mw −0,07 · 1904–1962 Ms −0,02.

## Koruma kuralı güncellemesi (2026-10-21, kullanıcı onayı) ve testlerin tekrarı
Kural: |ΔM| > 1,0 olan çiftte aktarım yapılmaz; **istisna: Δt ≤ 10 s ve Δr ≤ 30 km ise ΔM aktarımı engellemez.**

| | Önce | Sonra |
|---|---|---|
| Mw aktarılan | 1.130 | **1.144** |
| Aktarılmayan (şüpheli) | 15 | **1** |
| `mw_src`: doğrudan / vekil | 639 / 764 | 641 / 776 |

Testler yeniden çalıştırıldı: T1–T6 ✓, **T9 (bütün istisnalar Δt ≤ 10 s ve Δr ≤ 30 km)** ✓ (14 olay; Δt 0–3 s, Δr 0,2–12,9 km), T8 süreklilik ✓ — M ≥ 5,5 blok oranları 1,07 / 0,94 / 0,98 / 1,02; 1963 sıçraması −0,13 (M ≥ 5,5), −0,10 (M ≥ 6,0). İstisnayla aktarılanlar: 1999-08-17 İzmit mb 6,3 → Mw 7,58; 1999-11-12 Düzce mb 6,0 → 7,16; 2009-09-07 MD 3,4 → 5,09; 2011-10-23 Ms 4,1 → 5,14; 1981–1996 arası 10 ISC Ms 3,8–4,4 → Mw 5,1–5,5.

## 1910-02-18 olayı (ayrı inceleme; karar bekliyor)
| Kaynak | Zaman | Konum, derinlik | Büyüklük |
|---|---|---|---|
| A (ISC, köken yazarı GUTE) | 05:09:18 | 36,0° K 24,5° D, 150 km | UK 7,0 |
| ISC Bulletin, aynı olayın bütün büyüklükleri | | | Ms 7,0 (PAS, tercih edilen) · mB 6,9 (ABE1) · UK 7,0 (GUTE) · UK 7,0 (B&D) |
| ISC-GEM v12.1 (16958073) | 05:09:12,69 | 35,81° K 23,99° D, 60 km | **Mw 5,85 ± 0,20, vekil, kalite B** |

- **Aynı olay olduğu güçlü kanıtla destekleniyor:** ±200 dk ve 250 km içinde tek aday; Δt 6 s, Δr 50 km (ISC-GEM'in yeniden konumlandırması: 0,5° batı, derinlik 150 → 60 km).
- **Büyüklük farkı çözülmedi:** erken dönem ajans büyüklükleri (Gutenberg–Richter, Abe) ≈ 7, ISC-GEM'in sayısallaştırılmış genliklerden yeniden hesapladığı vekil Mw 5,85. Fark 1,15 birim; bu veriyle hangisinin doğru olduğu belirlenemiyor.
- Prototipte kural gereği **özgün büyüklük (7,0) korundu** (`not: supheli_eslesme`). Karar seçenekleri: (i) 7,0 kalsın; (ii) ISC-GEM Mw 5,85 kullanılsın (ISC-GEM'in yeniden değerlendirmesi esas alınır); (iii) Mw tabanlı istatistiklerden çıkarılıp ayrı listelensin. Bu olay 1904–1962 M ≥ 6,5 sınıfındaki 36–44 olaydan biri; b ve λ(≥6,0) üzerindeki etkisi küçük ama sınırlı sayıda büyük olayda sıfır değil.

## Kalan sınırlılık
ISC-GEM genel olarak M ≥ 5,0'ı kapsadığından, M < 5 olaylar mb/ML/MD ile kalıyor. Büyüklük ölçeği M ≈ 5 civarında Mw'den diğer türlere geçiyor; bu eşiği kapsayan b-değeri hesapları (ör. M ≥ 4,5) bu geçişten etkilenebilir. Prototip bu konuyu çözmüyor; raporlanmak üzere not edildi.

## Kapanış
Testler güncel kuralla yeniden geçti; prototip tamamlandı. Bekleyen kararlar: 1910 olayı; tamlık merdiveni (ayrı karar); üretime geçiş (onaylanmadı).
