# Faz 3 — ISC-GEM Mw aktarımı (1904–2021), prototip doğrulaması (2026-10-21)

**Karar (kullanıcı):** ISC-GEM Mw, 1904–2021 boyunca eşleşen olaylara aktarılır; `mw_src` ile kaynak ayrı tutulur; ISC-GEM'de karşılığı olmayan olayların büyüklüğü değişmez, tahminî Mw atanmaz. Üretim kodu, `eq_historical.json`, GK74 kodu, `mw_authority.json` ve tamlık merdiveni değiştirilmedi (`homog-faz0` dalı). Betik `faz3_mw_aktarim.py`; sonuç `out/faz3_rapor.json`; olay bazında aktarım kaydı `out/aktarim_kaydi.json` (1.130 satır; eski M, tür, yeni Mw, kaynak, ISC-GEM kimliği, Δr). Girdilerin SHA-256 özetleri raporda.

## Kurallar (önceden tanımlı)
- 1904–1962: ISC-GEM birincil; A'nın eşleşmeyen olayları olduğu gibi kalır. 1963–2021: A korunur, eşleşen olaya ISC-GEM Mw atanır; A'da karşılığı olmayan ISC-GEM olayı eklenmez. 2022–: değişmez.
- Eşleştirme: zaman–konum (Tablo 2), bire-bir (en yakın önce). Koruma: |M_A − Mw| > 1,0 ise aktarım yapılmaz.
- `mw_src`: `iscgem_direct` 639 · `iscgem_proxy` 764 · `catalog_native_mw` 1.214 · `catalog_raw_<tür>` 85.989.

## Sayılar
A 88.333 olay → prototip 88.606. Eşleşen çift 1.145; Mw aktarılan 1.130; koruma nedeniyle aktarılmayan 15; 1963 öncesi ISC-GEM'den eklenen 273; 1963 öncesi A'nın eşleşmeyen ve olduğu gibi kalan 33 olayı; 1963–2021'de A'da karşılığı olmayan ve eklenmeyen ISC-GEM olayı 21.

## Doğrulama testleri
| Test | Sonuç |
|---|---|
| T1 Bire-bir (bir ISC-GEM olayı en çok bir kez) | ✓ |
| T2 Eşleşmeyen 87.203 olayın büyüklüğü değişmedi | ✓ (değişen 0) |
| T3 Aktarılan 1.403 Mw, ISC-GEM değeriyle birebir aynı | ✓ (farklı 0) |
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

## Açık konu (onay gerekiyor): koruma kuralı gerçek eşleşmeleri engelliyor
Aktarılmayan 15 çiftin 14'ü açıkça aynı olay (Δt ≤ 3 s, Δr ≤ 13 km); ΔM'nin büyük olması mb doygunluğundan ya da küçük Ms'ten kaynaklanıyor. Bunların arasında **17 Ağustos 1999 İzmit (mb 6,3 → Mw 7,58)** ve **12 Kasım 1999 Düzce (mb 6,0 → Mw 7,16)** var. Yalnız 1910-02-18 (UK 7,0 → 5,85, Δr 50 km) gerçekten belirsiz. Öneri (uygulanmadı): koruma kuralını "Δt ≤ 10 s ve Δr ≤ 30 km ise ΔM'ye bakılmaz; aksi hâlde |ΔM| ≤ 1,0" olarak değiştirmek.

## Kalan sınırlılık
ISC-GEM genel olarak M ≥ 5,0'ı kapsadığından, M < 5 olaylar mb/ML/MD ile kalıyor. Büyüklük ölçeği M ≈ 5 civarında Mw'den diğer türlere geçiyor; bu eşiği kapsayan b-değeri hesapları (ör. M ≥ 4,5) bu geçişten etkilenebilir. Prototip bu konuyu çözmüyor; raporlanmak üzere not edildi.

## Kapanış
Testler geçti; prototip tamamlandı. Üretime geçiş, tamlık merdiveninin yeniden belirlenmesi ve koruma kuralı değişikliği ayrı onay gerektiriyor.
