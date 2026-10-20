"""
fetch_gnss_midas.py — Nevada Geodetic Laboratory (NGL) MIDAS GNSS hız alanını indirir,
kalite süzgecinden geçirir ve tarayıcıda kullanılacak küçük bir JSON'a yazar.

Kaynak : http://geodesy.unr.edu/velocities/midas.IGS14.txt   (readme: midas.readme.txt)
Atıf   : Blewitt, G., Kreemer, C., Hammond, W. C., & Gazeaux, J. (2016). MIDAS robust trend estimator for
         accurate GPS station velocities without step detection. JGR Solid Earth, 121, 2054–2068.
         https://doi.org/10.1002/2015JB012552
Sütunlar (readme): 1 istasyon · 2 sürüm · 3–4 ilk/son epok (ondalık yıl) · 5 süre (yıl) · 6–8 epok/çift sayıları ·
         9–11 hız E/N/U (m/yıl) · 12–14 belirsizlik E/N/U (m/yıl) · 15–17 ofset · 18–20 aykırı oranı E/N/U ·
         21–23 çift std · 24 basamak sayısı · 25–27 enlem, boylam (°), yükseklik (m)

Süzgeç (varsayılan): süre ≥ 3 yıl; σE, σN ≤ 2 mm/yıl; aykırı oranı E, N ≤ 0,3; yatay hız ≤ 120 mm/yıl.
Çıktı  : data/gnss_midas.json  {meta:{...}, f:[alan adları], s:[[id, enlem, boylam, vE, vN, σE, σN, süre], ...]}
         hızlar mm/yıl (IGS14), konum 4 ondalık.
Kullanım: python scripts/fetch_gnss_midas.py [--input yerel_dosya.txt] [--output data/gnss_midas.json]
"""
import argparse, datetime, json, sys, urllib.request

URL = 'http://geodesy.unr.edu/velocities/midas.IGS14.txt'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input'); ap.add_argument('--output', default='data/gnss_midas.json')
    ap.add_argument('--min-years', type=float, default=3.0); ap.add_argument('--max-sigma', type=float, default=2.0)
    ap.add_argument('--max-outlier', type=float, default=0.3); ap.add_argument('--max-speed', type=float, default=120.0)
    a = ap.parse_args()
    if a.input:
        raw = open(a.input, encoding='utf-8', errors='replace').read()
    else:
        req = urllib.request.Request(URL, headers={'User-Agent': 'EQ-LiveTurkiye (github.com/aliosmanoncel/EQ-LiveTurkiye)'})
        raw = urllib.request.urlopen(req, timeout=180).read().decode('utf-8', errors='replace')
    rows, n_all, rej = [], 0, {'parse': 0, 'years': 0, 'sigma': 0, 'outlier': 0, 'speed': 0}
    for line in raw.splitlines():
        p = line.split()
        if len(p) < 27 or line.startswith('#'):
            continue
        n_all += 1
        try:
            sid = p[0]; dur = float(p[4]); ve, vn = float(p[8]) * 1e3, float(p[9]) * 1e3
            se, sn = float(p[11]) * 1e3, float(p[12]) * 1e3; oe, on = float(p[17]), float(p[18])
            lat, lon = float(p[24]), float(p[25])
        except ValueError:
            rej['parse'] += 1; continue
        if lon > 180: lon -= 360
        if dur < a.min_years: rej['years'] += 1; continue
        if se > a.max_sigma or sn > a.max_sigma: rej['sigma'] += 1; continue
        if oe > a.max_outlier or on > a.max_outlier: rej['outlier'] += 1; continue
        if (ve * ve + vn * vn) ** 0.5 > a.max_speed: rej['speed'] += 1; continue
        rows.append([sid, round(lat, 4), round(lon, 4), round(ve, 2), round(vn, 2), round(se, 2), round(sn, 2), round(dur, 1)])
    if n_all < 1000 or len(rows) < 1000:
        sys.exit(f'Beklenenden az istasyon (satır {n_all}, geçen {len(rows)}); dosya biçimi değişmiş olabilir — çıktı yazılmadı.')
    out = {'meta': {'source': URL, 'frame': 'IGS14', 'units': 'mm/yr', 'downloaded_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
                    'n_input': n_all, 'n_kept': len(rows), 'rejected': rej,
                    'filters': {'min_years': a.min_years, 'max_sigma_mm_yr': a.max_sigma, 'max_outlier_frac': a.max_outlier, 'max_speed_mm_yr': a.max_speed},
                    'citation': 'Blewitt, G., Kreemer, C., Hammond, W. C., & Gazeaux, J. (2016). JGR Solid Earth, 121, 2054–2068. https://doi.org/10.1002/2015JB012552'},
           'f': ['id', 'lat', 'lon', 'vE', 'vN', 'sE', 'sN', 'yrs'], 's': rows}
    with open(a.output, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(',', ':'))
    print(f'{len(rows)} / {n_all} istasyon yazıldı → {a.output}; elenen: {rej}')

if __name__ == '__main__':
    main()
