# Küresel katalog çalışması — durum (2026-10-26)

Dal: `kuresel-katalog-olcum`. `main`, canlı site, arayüz, `data/mw_iscgem.json` ve Türkiye kataloğu **değişmedi**. Birleştirme ve yayın için ayrıca onay gerekir.

| Adım | Belge | Durum |
|---|---|---|
| Ölçüm 1: ISC erişimi | `OLCUM_1_ISC_ERISIM.md` | Tamamlandı (B: kısıtlı erişim) |
| Ölçüm 2: ISC-GEM – USGS örtüşmesi ve çift kayıt | `OLCUM_2_ONKAYIT.md`, `OLCUM_2_RAPOR.md` | Tamamlandı |
| Aşama 2: `data/iscgem_global.json` (ana katalog, 14 alan), lisans, doğrulama | `ASAMA_2_RAPOR.md` | Tamamlandı; 26/26 denetim yerelde ve Actions'ta geçti |
| Arayüz hazırlığı: Global modda varsayılan kapalı "ISC-GEM 1904–2021" penceresi | `kabul/RAPOR.md` | Dalda hazır; kabul testi 21/21; `main`'e birleştirilmedi, canlıya alınmadı |
| USGS ek katmanı | `USGS_KATMANI_TASARIM.md` | Yalnız tasarım; varsayılan kapalı; lisans doğrulanmadı |
| Duyarlılık: vekil Mw ve b-değeri, 1980–2021 | `duyarlilik_1980/RAPOR.md` | Tamamlandı ve kapatıldı |

**Yöntem kararı:**

| Analiz amacı | Örneklem |
|---|---|
| Varsayılan b-değeri ve Mc | ISC-GEM'in tüm Mw değerleri; doğrudan/vekil oranı raporlanır |
| Dönüşüm bağıntılarının sınanması | Yalnız doğrudan moment kaynaklı Mw (GCMT ve literatür) |
| Yalnız doğrudan Mw ile b-değeri | Duyarlılık analizi; seçim yanlılığı uyarısıyla |

**Açık konular** (yeni bir karar gerektirir; şu an iş yok):
- Arayüz hazırlığının `main`'e birleştirilmesi ve canlıya alınması (karar bekliyor).
- Mevcut hata: canlı zaman düğmesi `activeHistWindows`'u temizlemiyor (`kabul/RAPOR.md` §3).
- USGS ek katmanının üretimi (önce lisans doğrulaması).
- Bağıntıların ISC-GEM dışı ajans büyüklüklerine aktarımının bağımsız sınanması.
