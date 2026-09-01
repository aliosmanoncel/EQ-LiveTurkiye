"""
Surfer ile üretilmiş bir tarihsel deprem şiddet (USGS ShakeMap MMI) KMZ dosyasini
EQ-LiveTurkiye'nin kullandigi PNG+meta.json ciftine cevirir.

Surfer'in varsayilan rainbow renk skalasinda dusuk MMI (mavi) tum dikdortgeni
kapladigi icin haritada anlamsiz bir "arka plan blogu" gibi gorunuyordu. Bu
script, rengin HSV hue degerinden yaklasik MMI konumunu geri cikarip dusuk
degerleri seffaflastirir (bkz. FADE_LO/FADE_HI) — sadece hissedilir siddet
alani (yesil->kirmizi) gorunur kalir.

Kullanim:
    python build_shakemap_from_kmz.py \
        --kmz "D:/GRID_DATA/1912_murefte.kmz" \
        --id murefte1912 \
        --event "1912-08-09 Mürefte (Şarköy-Mürefte) M7.3" \
        --rtf "D:/GRID_DATA/GridDataReport-1912_Murefte_grid.rtf"

Ciktilar EQ-LiveTurkiye/data/ altina yazilir:
    shakemap_<id>.png
    shakemap_<id>_meta.json

Sonra index.html icinde SHAKE_EVENTS objesine tek satir eklenir:
    <id>: { label: '<kisa etiket>', file: '<id>' },
ve toolbar'a bir <button class="tbtn shakebtn" data-shake="<id>" ...> satiri.

Kapsam kurali: bu script sadece Turkiye depremleri icin index.html'e
entegre edilir. Turkiye-disi olaylar (orn. 1923 Kanto) --id ve --event ile
uretilebilir ama SADECE arsiv amacli; SHAKE_EVENTS'e eklenmez.
"""
import argparse
import io
import json
import re
import zipfile

import numpy as np
from PIL import Image
import matplotlib.colors as mcolors

FADE_LO = 0.12  # bu value_frac altindaki pikseller tamamen seffaf
FADE_HI = 0.30  # bu value_frac ustundeki pikseller tam opak


def fade_alpha(im: Image.Image) -> Image.Image:
    arr = np.array(im.convert("RGBA")).astype(np.float32) / 255.0
    hsv = mcolors.rgb_to_hsv(arr[:, :, :3])
    hue = hsv[:, :, 0]
    # Surfer rainbow: mavi(dusuk)->cyan->yesil->sari->kirmizi(yuksek)
    # matplotlib hue: kirmizi=0, yesil=0.333, mavi=0.667
    value_frac = np.clip(1 - hue / 0.667, 0, 1)
    alpha = np.clip((value_frac - FADE_LO) / (FADE_HI - FADE_LO), 0, 1)
    out = arr.copy()
    out[:, :, 3] = alpha
    return Image.fromarray((out * 255).astype(np.uint8), "RGBA")


def latlonbox_from_kml(kml_text: str) -> dict:
    bounds = {}
    for tag in ["north", "south", "east", "west"]:
        m = re.search(rf"<{tag}>([-\d.]+)</{tag}>", kml_text)
        if not m:
            raise ValueError(f"KML icinde <{tag}> bulunamadi")
        bounds[tag] = float(m.group(1))
    return bounds


def rtf_minmax(path: str):
    """Surfer'in GridDataReport-*.rtf dosyasindan Z (MMI) min/max okur.

    RTF kontrol kelimeleri tek backslash ile ayrilir (\\tab, \\par) — bunlar
    normal whitespace DEGILDIR, bu yuzden \\s+ tabanli regex yerine dogrudan
    literal string split kullanilir.
    """
    with open(path, "r", errors="replace") as f:
        content = f.read()
    bs = chr(92)
    idx_min = content.find("Minimum:")
    idx_max = content.find("Maximum:")
    min_line = content[idx_min:content.find(bs + "par", idx_min)]
    max_line = content[idx_max:content.find(bs + "par", idx_max)]
    z_min = float(min_line.split(bs + "tab")[-1].strip())
    z_max = float(max_line.split(bs + "tab")[-1].strip())
    return z_min, z_max


def build(kmz_path: str, event_id: str, event_label: str, rtf_path: str | None, out_dir: str):
    z = zipfile.ZipFile(kmz_path)
    kml_name = next(n for n in z.namelist() if n.endswith(".kml"))
    tif_name = next(n for n in z.namelist() if n.endswith(".tif"))
    kml_text = z.read(kml_name).decode("utf-8", errors="replace")
    bounds = latlonbox_from_kml(kml_text)

    im = Image.open(io.BytesIO(z.read(tif_name)))
    faded = fade_alpha(im)
    png_path = f"{out_dir}/shakemap_{event_id}.png"
    faded.save(png_path)

    mmi_min = mmi_max = None
    if rtf_path:
        mmi_min, mmi_max = rtf_minmax(rtf_path)

    meta = {
        "event": event_label,
        "source": "USGS ShakeMap (tarihsel/sentetik MMI modeli) + Surfer color-relief regrid "
                  "(yalnizca gorsellestirme cozunurlugu artirildi, veri kaynagi degismedi)",
        "z_field": "MMI",
        "mmi_min": mmi_min,
        "mmi_max": mmi_max,
        "bounds": {
            "minlat": bounds["south"], "maxlat": bounds["north"],
            "minlon": bounds["west"], "maxlon": bounds["east"],
        },
        "note": "Renk skalasi Surfer varsayilan mavi->kirmizi rainbow; dusuk deger (arka plan) "
                "seffaf yapildi, sadece hissedilir siddet alani gosterilir.",
    }
    meta_path = f"{out_dir}/shakemap_{event_id}_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"yazildi: {png_path}")
    print(f"yazildi: {meta_path}")
    print(f"bounds: {bounds}")
    print(f"MMI: {mmi_min} - {mmi_max}")
    print()
    print("index.html SHAKE_EVENTS'e eklenecek satir:")
    print(f"  {event_id}: {{ label: '{event_label.split(' ')[0]}', file: '{event_id}' }},")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kmz", required=True, help="Kaynak KMZ dosyasi (Surfer GroundOverlay)")
    ap.add_argument("--id", required=True, help="Kisa dosya/kod kimligi, orn. murefte1912")
    ap.add_argument("--event", required=True, help="Gosterilecek olay etiketi, orn. '1912-08-09 Mürefte M7.3'")
    ap.add_argument("--rtf", default=None, help="Opsiyonel GridDataReport-*.rtf (MMI min/max icin)")
    ap.add_argument("--out-dir", default="data", help="Cikti klasoru (varsayilan: data)")
    args = ap.parse_args()
    build(args.kmz, args.id, args.event, args.rtf, args.out_dir)
