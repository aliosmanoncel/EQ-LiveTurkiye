# PMSR · SCSN bölge kutusu yeniden üretimi ve Faz 0 doğrulaması (2026-11-18)

- `TASARIM.md` — teknik tasarım ve test planı (v0.4; "FPA" çalışma adıyla yazıldı, modül adı sonradan *Pre-mainshock Seismicity Rate Test* oldu).
- `faz0/` — sentetik testler (T1 birim, T4 statseis uyumu, T2a Poisson, T2b ETAS, T3 güç). `fpa_ref.py` bağımsız Python ESR.
- `step1.py`–`step3.py` — SCSN yıllık SCEDC dosyalarından katalog, `statseis` ile ana şok seçimi ve yerel Mc, ESR. Girdi yolları yazarın çalışma ortamına göredir (`/mnt/user-data/uploads/Downloads/20*.txt`).
- `REPRO_SCSN_bolge.md`, `SCSN_bolge_61_sonuclar.csv` — sonuçlar. Makalenin 74 ana şokluk birleştirilmiş kümesiyle karıştırılmamalıdır.
- Donmuş referans ve katalog: `scripts/fixtures/pmsr_scsn_box_ref.json`, `pmsr_scsn_box_catalog.csv.gz`.
