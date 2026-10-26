# Küresel katalog — Ölçüm 2 ön kaydı: ISC-GEM v12.1 – USGS ComCat karşılaştırma kuralları (2026-10-26)

Bu belge, **sonuçlar görülmeden önce** kaydedilmiştir. Kurallar sonuçlara bakılarak değiştirilmez. Değişiklik gerekirse ayrı bir ek olarak tarihiyle yazılır ve iki sonuç birlikte raporlanır.

## Veri

- **ISC-GEM:** `out/iscgem_v12.1_ana.json.gz` (`iscgem_cikar.py` ile üretildi; kaynak SHA-256 değerleri `out/iscgem_dogrulama.json` dosyasında).
  - Yalnız **ana katalog** kullanılır (74 159 olay, 1904–2021).
  - Ek katalog (9 834 olay; %61'inde Mw yok) hiçbir eşleştirmeye girmez.
- **USGS ComCat:** FDSN event servisi, GeoJSON.
  - **Dönem:** 1904-01-01 – 2021-12-31.
  - **Alan:** Küresel.
  - **Büyüklük:** `minmagnitude=4.0`, büyüklük türü fark etmeksizin. Büyüklüğü olmayan kayıtlar bu filtre nedeniyle dışarıda kalır; bu bir sınırdır. Eşik 4,0'tır, çünkü ISC-GEM'in en küçük Mw'si 4,75'tir ve aynı olayın USGS'deki mb değeri daha küçük olabilir. Daha yüksek bir eşik, büyüklüğü dolaylı bir eşleştirme koşuluna çevirirdi.
  - **Sorgu:** Yıllık parçalar; olay sayısı 20 000'i aşarsa parça ikiye bölünür. Olay türü filtrelenmez, ama türler raporlanır.
  - **Saklanan alanlar:** `id, ids, sources, net, time, lat, lon, depth, mag, magType, type`.
  - Sorgu zamanı ve her parçanın olay sayısı kaydedilir.

## Eşleştirme kuralı

- **Birincil ölçütler:** Yalnız zaman farkı (Δt) ve episantr uzaklığı (Δr, büyük daire). Derinlik ve büyüklük eşleştirmede **kullanılmaz**.
- **Toleranslar:** ISC-GEM olayının yılına göre belirlenir. Candia & Macedo (2026, Tablo 2); 21 Ekim Türkiye çalışmasıyla aynıdır (`analysis/homog_faz1/faz1_iscgem.py`, `homog-faz0` dalı).

| ISC-GEM yılı | ΔT | ΔR |
|---|---|---|
| 1904–1939 | 200 dk | 250 km (uyarlama: kaynakta 1940 öncesi ΔR tanımlı değil) |
| 1940–1962 | 10 dk | 200 km |
| 1963–1989 | 2 dk | 150 km |
| 1990–2021 | 0,5 dk | 100 km |

- **Aday:** Δt ≤ ΔT ve Δr ≤ ΔR koşulunu sağlayan her USGS olayı. **Puan** = Δt/ΔT + Δr/ΔR.
- **Sınıflar:**

| Sınıf | Tanım |
|---|---|
| `tekil` | ISC-GEM olayının tek adayı var ve o USGS olayının da tek ISC-GEM adayı bu olay |
| `karsilikli_cok_adayli` | Birden çok aday var, ama en iyi puanlı aday ile bu olay birbirinin en iyisi. **Kesin sayılmaz**, ayrı raporlanır |
| `belirsiz` | Adaylar var, ama karşılıklı en iyi eşleşme yok |
| `yalniz_iscgem` | Hiç aday yok |

  - USGS tarafında: herhangi bir ISC-GEM olayının adayı olmayan USGS olayları `yalniz_usgs` sayılır. Bunlar dönem × USGS büyüklüğü (kendi ölçeğinde: 4,0–5,0 / 5,0–5,5 / 5,5–6,0 / ≥ 6,0) × büyüklük türü olarak raporlanır.
- **Olası çift kayıt (USGS içinde):** Aynı ISC-GEM olayına aday olan iki ya da daha çok USGS olayı. Sayısı ve örnekleri raporlanır.
- **Kimlik denetimi (bağımsız):** USGS kaydının `ids` alanında bu ISC-GEM olayının kimliği geçiyorsa (`iscgem<eventid>` biçiminde ya da benzeri), pencereyle bulunan eşleşmenin bu kimlik bağıyla tutarlılığı ayrıca raporlanır.

## USGS kaydının kökeni (örtüşme yorumlanmadan önce)

| Sınıf | Tanım |
|---|---|
| `iscgem_tercihli` | Tercih edilen kaynak ağ (`net`) ISC-GEM'e ait (adında `iscgem` geçiyor) |
| `iscgem_katkili` | `net` başka bir ağ, ama `ids`/`sources` içinde `iscgem` geçiyor |
| `iscgem_katkisi_yok` | `ids`/`sources` dolu ve `iscgem` içermiyor. Bu, **"bağımsız gözlem" demek değildir**: USGS'nin eski kayıtları ISC-GEM ile ortak tarihsel kaynaklara dayanabilir. Yalnız "ISC-GEM katkısı görünmüyor" olarak yorumlanır |
| `koken_belirsiz` | `ids` ve `sources` boş ya da yok. Bağımsız kabul edilmez |

- Bütün `net` değerleri ve `sources` içindeki katalog önekleri sayılarıyla raporlanır. `iscgem` adlı bir ağın gerçekten var olup olmadığı varsayılmaz; verinin kendisinden gösterilir.

## Raporlanacaklar (dönem: 1904–1970, 1971–1997, 1998–2021; sınırlar değişmez)

- ISC-GEM olaylarının sınıf dağılımı, köken sınıfına göre ayrı ayrı.
- `yalniz_usgs` dağılımı.
- USGS içi olası çift kayıtlar.
- **Büyüklük tanısı (eşleştirme koşulu değil):** `tekil` eşleşmelerde USGS mag − ISC-GEM Mw farkı; USGS büyüklük türüne (mw* / mb / ms / diğer) ve döneme göre ortanca, çeyrekler arası aralık ve N.
- Kimlik denetimi tutarlılığı.

## Sınırlar

- **ISC-GEM'in Mw 5,0–5,5 kapsamı küresel olarak düzgün değildir.** Bu büyüklükteki olaylar katalogun sürüm geçmişinde yalnız belirli gruplarda eklenmiştir: kıtasal olaylar; kıyıya 50 km içindeki sığ olaylar; 1976 sonrası GCMT Mw'li olaylar; 2019 ve sonrası tüm küresel olaylar. Bu yüzden `yalniz_usgs` sayılarının bir kısmı ISC-GEM'in seçim ölçütünden kaynaklanır; bir eksiklik değildir.
- **Toleranslar:** 1940 öncesi ΔT = 200 dk geniştir; bu dönemde `belirsiz` ve `karsilikli_cok_adayli` sayıları yüksek çıkabilir. Bu bir sonuçtur; toleransı değiştirme gerekçesi değildir.
- **Ortam:** Ölçüm GitHub Actions'ta çalıştırılır. Çalışma oturumunun kendi ortamları USGS'ye erişemiyor.
