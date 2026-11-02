# Reasenberg (1985) – GK74 karşılaştırması ve doğrulama durumu (2026-11-02)

Bu klasördeki raporlar, `scripts/reasenberg.py` v0.3.0'ın EQ-Live'a Python seçeneği
olarak eklenmesinden önce yapılan çalışmanın kaydıdır (raporlar İngilizce).

| Dosya | İçerik |
|---|---|
| `on_hazirlik_RAPOR.md` | 1998–2026 EMSC: büyüklük türleri, tamamlılık (kümülatif GFT, Wiemer & Wyss 2000), 10 km kayıtlı derinlikler, güncel `decluster_gk74.py` ile GK74 referansı (revizyon 2) |
| `karsilastirma_A_RAPOR.md` | Tasarım A: aynı 80 929 olayda GK74 ile Reasenberg (`zmap`) olay bazında; tanısal varyantlar |
| `reasenberg_dogrulama_durumu.md` | Modülün USGS cluster2000x kaynağıyla denetimi (aşama 3), yapılan düzeltmeler, dondurma kaydı; **D1 (derlenmiş Fortran ile karşılaştırma) açık** |

Kararlar (2026-11-02/03): `zmap` varsayılan, `cluster2000x` deneysel; ana çıktı temsilci olay,
eşdeğer olaylar yalnız duyarlılık analizi; kapsam yalnız Python. Karşılaştırma sonuçları
karışık büyüklük ölçeğine koşulludur; fiziksel yorum ve b-değeri karşılaştırması
(tasarım B, derinlik duyarlılığı) henüz yapılmadı.

Raporlarda adı geçen analiz betikleri (`prep_analysis.py`, `compare_A.py`, `diag_drivers.py`)
ve Fortran karşılaştırma kiti bu depoda değildir; dosya hash'leri raporlarda kayıtlıdır.
