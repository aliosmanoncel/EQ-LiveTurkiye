"""
Global CMT (globalcmt.org) katalogundan bir olayin dogrulanmis moment-tensor
cozumunu ceker ve EQ-LiveTurkiye'nin "Fay Duzlemi Cozumleri (GCMT)" katmaninin
kullandigi data/focal_mechanisms.json + data/beachball_<id>.png ciftini uretir.

Onemli tasarim karari (bilerek): beachball ikonu HICBIR sekilde strike/dip/
rake'ten yeniden cizilmiyor (yanlis isaret/yonelim riski tasir, gorsel olarak
dogrulamasi zor). Bunun yerine GCMT'nin kendi resmi webCMTgif_X servisi
(moment tensor bilesenlerinden GCMT'nin sunucusunda uretilen resmi GIF)
kullanilir — script sadece bu servisi cagirip sonucu indirir/arsivler.

Kullanim (once --dry-run ile kontrol, sonra gercek yazim):
    python build_focal_mechanism.py \
        --date 2023-02-06 --near-time 01:17 \
        --id pazarcik2023 \
        --label "2023 Pazarcık (Kahramanmaraş, 1. şok)" \
        --related-shakemap pazarcik2023 \
        --dry-run

    python build_focal_mechanism.py \
        --date 2023-02-06 --near-time 01:17 \
        --id pazarcik2023 \
        --label "2023 Pazarcık (Kahramanmaraş, 1. şok)" \
        --related-shakemap pazarcik2023

--date o gundeki TUM olaylari (varsayilan Mw>=5.5, Turkiye+cevresi bbox)
GCMT'den ceker; birden fazla eslesme varsa --near-time (PDE saat:dakika,
UTC) ile en yakin olay otomatik secilir. Tek eslesme varsa --near-time
gerekmez. --gcmt-name ile GCMT'nin kendi olay adiyla (orn. 202302060117A)
da dogrudan secim yapilabilir.

Kapsam onerisi: Mw>=5.5 (GCMT'nin kendi "quick CMT" esigi — bu buyuklugun
ustunde cozum guvenilir sekilde mevcuttur). Bu bir kod kisitlamasi DEGIL,
--mag-min varsayilani; her zaman elle secilen, "buyuk/onemli" olay bazinda
kullanilir, canli/otomatik bir besleme degildir (bkz. index.html'deki
toggleLayer('focalmech') yorumu).

Ciktilar:
    EQ-LiveTurkiye/data/beachball_<id>.png
    EQ-LiveTurkiye/data/focal_mechanisms.json  (id yoksa eklenir; varsa
        --force verilmeden UZERINE YAZILMAZ)
    <archive-dir>/gcmt_query_<id>.html          (ham GCMT yaniti, provenance)
    <archive-dir>/beachball_<id>_raw.gif        (ham GCMT GIF'i)
"""
import argparse
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

GCMT_FORM_URL = "https://www.globalcmt.org/cgi-bin/globalcmt-cgi-bin/CMT5/form"
GCMT_GIF_URL = "http://www.globalcmt.org/cgi-bin/globalcmt-cgi-bin/webCMTgif_X/form"


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def query_gcmt(date: str, mag_min: float, llat: float, ulat: float, llon: float, ulon: float) -> str:
    y, m, d = (int(x) for x in date.split("-"))
    params = {
        "itype": "ymd", "yr": y, "mo": m, "day": d,
        "oyr": y, "omo": m, "oday": d,
        "jyr": 1976, "jday": 1, "ojyr": 1976, "ojday": 1, "otype": "ymd", "nday": 1,
        "lmw": mag_min, "umw": 10, "lms": 0, "ums": 10, "lmb": 0, "umb": 10,
        "llat": llat, "ulat": ulat, "llon": llon, "ulon": ulon,
        "lhd": 0, "uhd": 1000, "lts": -9999, "uts": 9999,
        "lpe1": 0, "upe1": 90, "lpe2": 0, "upe2": 90, "list": 5,
    }
    return fetch(GCMT_FORM_URL + "?" + urllib.parse.urlencode(params))


def parse_events(html: str) -> list[dict]:
    """GCMT list=5 (tam format) HTML yanitini olay sozlukleri listesine cevirir."""
    blocks = html.split("<h3>Event name:")[1:]
    events = []
    for b in blocks:
        name = b.split("</h3>")[0].strip()
        mech_split = b.split("Mechanism information")
        timing, mech = mech_split[0], mech_split[1] if len(mech_split) > 1 else ""

        pdew = re.search(
            r"PDEW\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)",
            timing,
        )
        cmt_loc = re.search(
            r"CMT\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)",
            timing,
        )
        cmt_tensor = re.search(
            r"CMT\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)",
            mech,
        )
        exponent = re.search(r"Exponent for moment tensor:\s*(\d+)", mech)
        mw = re.search(r"Mw\s*=\s*([\d.]+)", mech)
        planes = re.findall(r"strike=([\-\d.]+)\s*dip=([\-\d.]+)\s*slip=([\-\d.]+)", mech)

        if not (pdew and cmt_loc and cmt_tensor and mw and len(planes) == 2):
            continue  # bu blok beklenen alanlarin hepsini icermiyor, atla

        events.append({
            "gcmt_event_name": name,
            "pde_hr": int(pdew.group(1)), "pde_min": int(pdew.group(2)), "pde_sec": float(pdew.group(3)),
            "lat_pde": float(pdew.group(4)), "lon_pde": float(pdew.group(5)), "depth_pde": float(pdew.group(6)),
            "cmt_hr": int(cmt_loc.group(1)), "cmt_min": int(cmt_loc.group(2)), "cmt_sec": float(cmt_loc.group(3)),
            "lat": float(cmt_loc.group(4)), "lon": float(cmt_loc.group(5)), "depth_km": float(cmt_loc.group(6)),
            "mw": float(mw.group(1)),
            "exponent": int(exponent.group(1)) if exponent else None,
            "mrr": float(cmt_tensor.group(1)), "mtt": float(cmt_tensor.group(2)), "mpp": float(cmt_tensor.group(3)),
            "mrt": float(cmt_tensor.group(4)), "mrp": float(cmt_tensor.group(5)), "mtp": float(cmt_tensor.group(6)),
            "strike1": int(float(planes[0][0])), "dip1": int(float(planes[0][1])), "rake1": int(float(planes[0][2])),
            "strike2": int(float(planes[1][0])), "dip2": int(float(planes[1][1])), "rake2": int(float(planes[1][2])),
        })
    return events


def select_event(events: list[dict], gcmt_name: str | None, near_time: str | None) -> dict:
    if gcmt_name:
        for e in events:
            if e["gcmt_event_name"] == gcmt_name:
                return e
        raise SystemExit(f"'{gcmt_name}' adinda olay bulunamadi. Bulunanlar: {[e['gcmt_event_name'] for e in events]}")
    if len(events) == 1:
        return events[0]
    if not near_time:
        names = [(e["gcmt_event_name"], f"{e['pde_hr']:02d}:{e['pde_min']:02d}", e["mw"]) for e in events]
        raise SystemExit(f"Birden fazla olay bulundu, --near-time HH:MM veya --gcmt-name belirtin: {names}")
    hh, mm = (int(x) for x in near_time.split(":"))
    target = hh * 60 + mm
    return min(events, key=lambda e: abs((e["pde_hr"] * 60 + e["pde_min"]) - target))


def download_beachball(ev: dict, out_path: Path) -> None:
    params = {"mrr": ev["mrr"], "mtt": ev["mtt"], "mpp": ev["mpp"], "mrt": ev["mrt"], "mrp": ev["mrp"], "mtp": ev["mtp"]}
    gif_bytes = fetch_binary(GCMT_GIF_URL + "?" + urllib.parse.urlencode(params))
    out_path.write_bytes(gif_bytes)


def fetch_binary(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD (olayin PDE/katalog tarihi, UTC)")
    ap.add_argument("--near-time", default=None, help="PDE saat:dakika (UTC, HH:MM) — birden fazla eslesme varsa secim icin")
    ap.add_argument("--gcmt-name", default=None, help="GCMT'nin kendi olay adi (orn. 202302060117A) — verilirse dogrudan secer")
    ap.add_argument("--id", required=True, help="Kisa dosya/kod kimligi, orn. pazarcik2023")
    ap.add_argument("--label", required=True, help="Gosterilecek olay etiketi, orn. '2023 Pazarcık (Kahramanmaraş, 1. şok)'")
    ap.add_argument("--related-shakemap", default=None, help="Ayni olayin ShakeMap MMI katmanindaki id'si (varsa), popup notunda referans icin")
    ap.add_argument("--related-shakemap-mag", default=None, help="Ayni olayin ShakeMap katmanindaki USGS Mw'si (varsa, orn. 7.8) — GCMT Mw'siyle karsilastirma notu icin")
    ap.add_argument("--related-shakemap-id", default=None, help="Ayni olayin USGS event id'si (orn. us6000jllz), popup notunda referans icin")
    ap.add_argument("--mag-min", type=float, default=5.5, help="GCMT sorgusu icin alt Mw esigi (varsayilan 5.5, GCMT'nin quick-CMT esigi)")
    ap.add_argument("--llat", type=float, default=30.0)
    ap.add_argument("--ulat", type=float, default=45.0)
    ap.add_argument("--llon", type=float, default=25.0)
    ap.add_argument("--ulon", type=float, default=46.0)
    ap.add_argument("--out-dir", default="data", help="EQ-LiveTurkiye/data (varsayilan)")
    ap.add_argument("--archive-dir", default="../GRID_DATA/GCMT_FocalMechanisms", help="Ham sorgu+GIF arsiv klasoru")
    ap.add_argument("--force", action="store_true", help="focal_mechanisms.json'da ayni id zaten varsa uzerine yaz")
    ap.add_argument("--dry-run", action="store_true", help="Hicbir dosya yazma, sadece sonucu yazdir")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    archive_dir = Path(args.archive_dir)
    json_path = out_dir / "focal_mechanisms.json"

    existing = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else []
    if any(e["id"] == args.id for e in existing) and not args.force and not args.dry_run:
        raise SystemExit(f"'{args.id}' zaten focal_mechanisms.json icinde. Uzerine yazmak icin --force verin.")

    html = query_gcmt(args.date, args.mag_min, args.llat, args.ulat, args.llon, args.ulon)
    events = parse_events(html)
    if not events:
        raise SystemExit(f"{args.date} tarihinde, Mw>={args.mag_min}, verilen bbox icinde hic olay bulunamadi.")
    ev = select_event(events, args.gcmt_name, args.near_time)

    y, m, d = args.date.split("-")
    time_iso = f"{y}-{m}-{d}T{ev['pde_hr']:02d}:{ev['pde_min']:02d}:{int(ev['pde_sec']):02d}Z"

    record = {
        "id": args.id,
        "label": args.label,
        "mag": ev["mw"], "magType": "Mw", "magSource": "GCMT",
        "time": time_iso,
        "lat": ev["lat"], "lon": ev["lon"], "depth_km": ev["depth_km"],
        "lat_pde": ev["lat_pde"], "lon_pde": ev["lon_pde"],
        "strike1": ev["strike1"], "dip1": ev["dip1"], "rake1": ev["rake1"],
        "strike2": ev["strike2"], "dip2": ev["dip2"], "rake2": ev["rake2"],
        "source": "GCMT",
        "gcmt_event_name": ev["gcmt_event_name"],
        "beachball": f"beachball_{args.id}.png",
    }
    if args.related_shakemap:
        record["related_shakemap"] = args.related_shakemap
    note = "Fay düzlemi çözümü (kaynak mekanizması)"
    if args.related_shakemap_id:
        note += f" — ShakeMap MMI katmanındaki {args.related_shakemap_id}"
        if args.related_shakemap_mag:
            note += f" (USGS, Mw{args.related_shakemap_mag})"
        note += " ile aynı depremdir."
    if args.related_shakemap_mag and abs(float(args.related_shakemap_mag) - ev["mw"]) >= 0.05:
        note += f" Mw değeri burada GCMT'nin kendi çözümünden ({ev['mw']}) alınmıştır, ajanslar arası küçük fark normaldir."
    record["note"] = note

    print(f"Secilen olay: {ev['gcmt_event_name']} · Mw{ev['mw']} · PDE {ev['pde_hr']:02d}:{ev['pde_min']:02d} UTC "
          f"· centroid ({ev['lat']}, {ev['lon']}) · düzlem1 {ev['strike1']}/{ev['dip1']}/{ev['rake1']} "
          f"· düzlem2 {ev['strike2']}/{ev['dip2']}/{ev['rake2']}")
    if len(events) > 1:
        print(f"(Aynı sorguda {len(events)} olay bulundu, bu en yakını seçildi — kontrol edin.)")

    if args.dry_run:
        print("--dry-run: hiçbir dosya yazılmadı.")
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    (archive_dir / f"gcmt_query_{args.id}.html").write_text(html, encoding="utf-8")
    raw_gif = archive_dir / f"beachball_{args.id}_raw.gif"
    download_beachball(ev, raw_gif)
    png_path = out_dir / f"beachball_{args.id}.png"
    Image.open(raw_gif).convert("RGB").save(png_path)

    existing = [e for e in existing if e["id"] != args.id] + [record]
    json_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"yazıldı: {png_path}")
    print(f"yazıldı: {json_path} ({len(existing)} olay)")
    print(f"arşivlendi: {archive_dir}/gcmt_query_{args.id}.html, {raw_gif}")
    print("HTML/JS değişikliği GEREKMEZ — tek 'Beachball' butonu focal_mechanisms.json'daki tüm olayları otomatik okur.")


if __name__ == "__main__":
    main()
