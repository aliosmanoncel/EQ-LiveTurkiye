# İşlenen katalogu ham SCEDC dosyalarıyla alan alan karşılaştırır (zaman çözünürlüğü dahil).
# Kullanım: python3 verify_catalog.py <ham_dosyalar_klasörü>
import sys, os, re, glob, gzip, json
import pandas as pd

src = sys.argv[1]
d = pd.read_csv('scsn_box_2017_2026.csv.gz', dtype={'time_utc': str}).set_index('id')
raw, rep = {}, {'dosyalar': {}}
for f in sorted(glob.glob(os.path.join(src, '20*.catalog.txt'))):
    y = int(os.path.basename(f)[:4])
    if not 2017 <= y <= 2026:
        continue
    txt = open(f).read()
    rows = [l for l in txt.splitlines() if l[:4].isdigit()]
    foot = int(re.search(r'Number of rows returned:\s*(\d+)', txt).group(1))
    frac = {len(l.split()[1].split('.')[1]) if '.' in l.split()[1] else 0 for l in rows}
    rep['dosyalar'][y] = dict(satir=len(rows), altbilgi=foot, esit=len(rows) == foot, saniye_ondalik_basamak=sorted(frac))
    for l in rows:
        p = l.split()
        raw[int(p[10])] = (p[0], p[1], float(p[6]), float(p[7]), float(p[8]), float(p[4]), p[5])

box = {k: v for k, v in raw.items() if -118.80 <= v[3] <= -115.40 and 32.68 <= v[2] <= 36.20}
missing = set(box) - set(d.index); extra = set(d.index) - set(box)
bad = {'zaman_metni': 0, 'zaman_sayisal_s': 0, 'enlem': 0, 'boylam': 0, 'derinlik': 0, 'buyukluk': 0, 'buyukluk_turu': 0}
maxdt = 0.0
for k, (D, T, lat, lon, dep, mag, mt) in box.items():
    r = d.loc[k]
    iso = D.replace('/', '-') + 'T' + T
    if r.time_utc != iso: bad['zaman_metni'] += 1
    t = (pd.Timestamp(iso) - pd.Timestamp('1970-01-01')).total_seconds()
    dt = abs(t - r.t); maxdt = max(maxdt, dt)
    if dt > 0.005: bad['zaman_sayisal_s'] += 1
    if abs(r.lat - lat) > 1e-9: bad['enlem'] += 1
    if abs(r.lon - lon) > 1e-9: bad['boylam'] += 1
    if abs(r.depth_km - dep) > 1e-9: bad['derinlik'] += 1
    if abs(r.mag - mag) > 1e-9: bad['buyukluk'] += 1
    if r.mag_type != mt: bad['buyukluk_turu'] += 1
rep.update(kutudaki_ham_olay=len(box), islenen=len(d), eksik=len(missing), fazla=len(extra),
           uyusmazlik=bad, en_buyuk_zaman_farki_s=round(maxdt, 6),
           sonuc='BİREBİR AYNI' if not missing and not extra and not any(bad.values()) else 'FARK VAR')
json.dump(rep, open('verify_catalog.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(rep, indent=1, ensure_ascii=False))
