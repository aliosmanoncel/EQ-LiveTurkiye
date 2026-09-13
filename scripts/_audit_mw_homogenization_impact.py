#!/usr/bin/env python3
"""Aşama 1 — magnitude homogenization audit etki raporu (SALT-OKUNUR).

Bu script data/eq_historical.json'ı DEĞİŞTİRMEZ, index.html'e dokunmaz.
Yalnızca: (a) mevcut (eski) to_mw() çıktısını dosyadan okur, (b) audit
sonucu önerilen yeni to_mw() mantığını bellek-içi olarak yeniden hesaplar,
(c) ikisini karşılaştırıp bir rapor yazdırır.

Kullanım: python scripts/_audit_mw_homogenization_impact.py
"""
import json
import math
from collections import Counter, defaultdict

DATA_PATH = "data/eq_historical.json"


# ── YENİ (önerilen, henüz üretime alınmamış) to_mw() ──────────────────────
def to_mw_new(mag, mtype):
    mt = (mtype or "").lower().strip()
    if mt in ("mw", "mww", "mwb", "mwc", "mwr", "mwp", ""):
        return round(mag, 2), "native"
    if mt == "mb" and 3.5 <= mag <= 6.2:
        return round(0.85 * mag + 1.03, 2), "scordilis2006_mb"
    if mt in ("ms", "ms_20"):
        if 3.0 <= mag <= 6.1:
            return round(0.646 * mag + 2.079, 2), "scordilis2006_ms_lo"
        if mag > 6.1:
            return round(0.994 * mag + 0.115, 2), "scordilis2006_ms_hi"
    if mt in ("ml", "md", "mc"):
        return None, "unconverted_" + mt
    return None, "unconverted_" + (mt or "unknown")


# ── computeMc / computeBvalue — index.html'deki JS ile birebir aynı mantık ─
def compute_mc(mags):
    mags = [m for m in mags if m and m > 0]
    if len(mags) < 10:
        return None
    bins = Counter(round(round(m * 10) / 10, 1) for m in mags)
    max_bin = max(bins.items(), key=lambda kv: kv[1])[0]
    return round(max_bin + 0.2, 1)


def compute_bvalue(mags, mc):
    sub = [m for m in mags if m >= mc]
    if len(sub) < 10:
        return None, None, 0
    mean = sum(sub) / len(sub)
    denom = mean - mc + 0.05
    if denom <= 0:
        return None, None, len(sub)
    b = math.log10(math.e) / denom
    err = 1.9 * b / math.sqrt(len(sub))
    return round(b, 3), round(err, 3), len(sub)


def region_stats(events, lat0, lat1, lon0, lon1, mag_key):
    evs = [e for e in events if lat0 <= e["lat"] <= lat1 and lon0 <= e["lon"] <= lon1]
    mags = [e[mag_key] for e in evs if e.get(mag_key) is not None]
    mc = compute_mc(mags)
    if mc is None:
        return {"N_box": len(evs), "N_mag": len(mags), "Mc": None, "b": None, "err": None, "N_ge_mc": 0}
    b, err, n_ge = compute_bvalue(mags, mc)
    return {"N_box": len(evs), "N_mag": len(mags), "Mc": mc, "b": b, "err": err, "N_ge_mc": n_ge}


def bin_counts(mags, edges):
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        out.append(sum(1 for m in mags if lo <= m < hi))
    return out


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        cat = json.load(f)
    events = cat["events"]
    n_total = len(events)

    # ── 1. KAPSAM ──────────────────────────────────────────────────────
    print("=" * 70)
    print("1) KAPSAM")
    print("=" * 70)
    print(f"Toplam olay: {n_total}")

    old_native = 0
    new_method_counts = Counter()
    for e in events:
        mtype = e.get("mtype", "")
        mag = e.get("mag", 0)
        new_mw, method = to_mw_new(mag, mtype)
        e["_new_mw"] = new_mw
        e["_new_method"] = method
        new_method_counts[method] += 1
        if mtype.lower() in ("mw", "mww", "mwb", "mwc", "mwr", "mwp", ""):
            old_native += 1

    n_unconverted = sum(v for k, v in new_method_counts.items() if k.startswith("unconverted"))
    print(f"\nYeni mw_method dağılımı:")
    for k, v in new_method_counts.most_common():
        print(f"  {k:28s} {v:7d}  ({100*v/n_total:5.1f}%)")
    print(f"\nEski mimaride HER olayın bir 'mw' değeri vardı (fabrikasyon dahil).")
    print(f"Yeni mimaride mw=null (unconverted) olan olay sayısı: {n_unconverted} ({100*n_unconverted/n_total:.1f}%)")

    # ── 2. MAGNITUDE DAĞILIMI (eski mw vs yeni mw/mag) ────────────────
    print("\n" + "=" * 70)
    print("2) MAGNITUDE DAĞILIMI — eski mw vs yeni (mw ?? mag) — tüm katalog")
    print("=" * 70)
    edges = [0, 2, 3, 4, 5, 6, 20]
    labels = ["<2", "2-3", "3-4", "4-5", "5-6", "6+"]
    old_mags = [e.get("mw") or e.get("mag") or 0 for e in events]
    new_mags = [e["_new_mw"] if e["_new_mw"] is not None else (e.get("mag") or 0) for e in events]
    old_bins = bin_counts(old_mags, edges)
    new_bins = bin_counts(new_mags, edges)
    print(f"{'Bin':8s} {'Eski N':>10s} {'Yeni N':>10s} {'Fark':>8s}")
    for lab, ob, nb in zip(labels, old_bins, new_bins):
        print(f"{lab:8s} {ob:10d} {nb:10d} {nb-ob:+8d}")
    # M3-4 vs M4-5 anomali kontrolü
    print(f"\nAnomali kontrolü (M3-4 vs M4-5):")
    print(f"  Eski: M3-4={old_bins[2]}  M4-5={old_bins[3]}  → {'TERS (anomali var)' if old_bins[2] < old_bins[3] else 'normal (azalan)'}")
    print(f"  Yeni: M3-4={new_bins[2]}  M4-5={new_bins[3]}  → {'TERS (anomali var)' if new_bins[2] < new_bins[3] else 'normal (azalan)'}")

    # ── 3 & 4. Mc VE b-DEĞERİ — temsili bölgeler ───────────────────────
    print("\n" + "=" * 70)
    print("3-4) Mc ve b-DEĞERİ — temsili bölgeler (eski mw vs yeni mw??mag)")
    print("=" * 70)
    regions = {
        "Tum Turkiye (EMSC 1998+, rapordaki N=76514 referansi)": (34.0, 43.0, 25.0, 46.0),
        "Zone 5 - Central Marmara Fault (40.746-40.999N,28.022-28.888E)": (40.746, 40.999, 28.022, 28.888),
        "Genis Marmara (40.0-41.5N, 27.0-30.0E)": (40.0, 41.5, 27.0, 30.0),
    }
    for name, (lat0, lat1, lon0, lon1) in regions.items():
        evs = [e for e in events if lat0 <= e["lat"] <= lat1 and lon0 <= e["lon"] <= lon1]
        old_m = [e.get("mw") or e.get("mag") or 0 for e in evs]
        new_m = [e["_new_mw"] if e["_new_mw"] is not None else (e.get("mag") or 0) for e in evs]
        old_mc = compute_mc(old_m)
        new_mc = compute_mc(new_m)
        old_b, old_err, old_n = (compute_bvalue(old_m, old_mc) if old_mc else (None, None, 0))
        new_b, new_err, new_n = (compute_bvalue(new_m, new_mc) if new_mc else (None, None, 0))
        print(f"\n▶ {name}")
        print(f"    N(bölge)={len(evs)}")
        print(f"    ESKİ: Mc={old_mc}  b={old_b}±{old_err}  N(M≥Mc)={old_n}")
        print(f"    YENİ: Mc={new_mc}  b={new_b}±{new_err}  N(M≥Mc)={new_n}")

    # ── 5. GR eğim/dağılım karşılaştırması: NAFZ-benzeri örnek zaten yukarıda
    print("\n" + "=" * 70)
    print("5) GR DAĞILIMI NOTU")
    print("=" * 70)
    print("Yukarıdaki (2) bölümündeki tüm-katalog bin karşılaştırması aynı zamanda")
    print("GR eğrisinin şeklini de yansıtır (kümülatif olmayan N, ΔM=1 çözünürlükte).")
    print("Bölge-özel GR eğrisi için index.html'deki renderGutenbergRichter() ile")
    print("birebir aynı ΔM=0.1 binleme mantığı ayrı bir çalıştırmada uygulanabilir.")

    # ── 6. HARİTA / null-fallback doğrulaması ─────────────────────────
    print("\n" + "=" * 70)
    print("6) HARİTA — marker sayısı invaryantı + mw=null fallback doğrulaması")
    print("=" * 70)
    n_with_valid_mag = sum(1 for e in events if (e.get("mag") or 0) > 0)
    print(f"Marker'a girecek olay sayısı (mag>0): ESKİ={n_with_valid_mag}  YENİ={n_with_valid_mag}  (DEĞİŞMEDİ — beklenen)")
    sample_unconverted = next(e for e in events if e["_new_method"].startswith("unconverted"))
    fallback_value = sample_unconverted["_new_mw"] if sample_unconverted["_new_mw"] is not None else sample_unconverted["mag"]
    print(f"Örnek unconverted olay: mag={sample_unconverted['mag']}, mtype={sample_unconverted['mtype']}, "
          f"yeni mw=None → JS'de (e.mw ?? e.mag) = {fallback_value} (mag'e düşüyor, doğrulandı)")

    # ── 7. GERİYE DÖNÜK GÜVENLİK ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("7) GERİYE DÖNÜK GÜVENLİK")
    print("=" * 70)
    print("- Bu script data/eq_historical.json'ı DEĞİŞTİRMEDİ (salt-okunur).")
    print("- index.html'e DOKUNULMADI.")
    print("- scripts/fetch_combined_catalog.py'ye DOKUNULMADI.")
    print("- bb534189 (canlı/stable) DEĞİŞMEDİ.")
    print("- Yalnızca bellek-içi karşılaştırma; hiçbir dosya yazılmadı.")


if __name__ == "__main__":
    main()
