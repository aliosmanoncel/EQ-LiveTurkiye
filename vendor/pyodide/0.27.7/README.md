# Pyodide 0.27.7 (depoda, sürümü sabit) — D-P3

Dinamik Reasenberg denemesi (`lab/reasenberg-pyodide/`) için tarayıcıda Python çalıştırma ortamı.
Yalnız çekirdek ve numpy alındı; başka paket yok.

- Kaynak: https://github.com/pyodide/pyodide/releases/download/0.27.7/pyodide-0.27.7.tar.bz2 (değiştirilmeden)
- Dosya karmaları: `SHA256SUMS`. CI (`.github/workflows/reasenberg-pyodide.yml`) bu dosyaları resmi sürüm arşivindeki
  karşılıklarıyla karşılaştırır; numpy tekerleğinin karması ayrıca `pyodide-lock.json` içindekiyle aynıdır
  (Pyodide yüklerken kendisi de denetler).
- Lisans: Pyodide — Mozilla Public License 2.0 (`LICENSE`); numpy — BSD-3-Clause (tekerleğin içinde).
- Python 3.12.7 · numpy 2.0.2.

Sürüm değiştirmek yeni bir klasör (`vendor/pyodide/<sürüm>/`), yeni karma listesi ve yeniden eşleşme testi demektir.
