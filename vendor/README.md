# vendor/

| Dosya | Sürüm | Lisans | Kaynak | SHA-256 |
|---|---|---|---|---|
| `geographiclib-geodesic-2.2.0.min.js` | 2.2.0 | MIT (`geographiclib-geodesic-2.2.0.LICENSE.txt`) | npm `geographiclib-geodesic@2.2.0` | `06e3512904b346575f475f14d0b27ea0979dbcd2b0eddebf5f1eeefd234395b5` |
| `polygon-clipping-0.15.7.umd.min.js` | 0.15.7 | MIT (`polygon-clipping-0.15.7.LICENSE.md`); gömülü splaytree 3.1.2 (MIT) ve tslib yardımcıları (Microsoft, dosya başlığında lisans notu) | npm `polygon-clipping@0.15.7` (`dist/polygon-clipping.umd.min.js`, değiştirilmeden) | `7f8619e84a86ce8dd400c9b50430e9c8cf8f26027b19eeb479f109f5c1a9d688` |

GeographicLib, EQ-Live'da araştırma bölgesi alanını WGS84 elipsoidi üzerinde jeodezik olarak hesaplamak için kullanılır
(İP-2, 2026-11-23). Kütüphane depoya gömülüdür; CDN'den yüklenmez ve yeni bir ağ isteği yapmaz.

Atıf: Karney, C. F. F. (2013). Algorithms for geodesics. *Journal of Geodesy*, 87(1), 43–55. doi:10.1007/s00190-012-0578-z

polygon-clipping, "Fay İzinden Sismik Araştırma Poligonu" (Fault-Trace-Based Zonation, 2026-11-23) aracında YALNIZ birleşim (union)
işlemi için kullanılır: iz parçalarının üst/alt yan dikdörtgenleri ve köşe dilimleri yerel elipsoidal eşit uzaklıklı azimutal
düzlemde üretilir, bu kütüphane ile birleştirilir. Tampon/ofset geometrisi ve alan hesabı kütüphaneye bırakılmaz (alan: GeographicLib).
Global ad: `polygonClipping`.
