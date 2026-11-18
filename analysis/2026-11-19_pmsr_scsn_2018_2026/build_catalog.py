# SCEDC yıllık SCEC_DC dosyalarından 2017–2026 kataloğu (2008–2017 step1.py ile aynı okuma)
# Kullanım: python3 build_catalog.py <dosyalar_klasörü>
import sys, glob, gzip, hashlib, json, io, os
import pandas as pd

src = sys.argv[1]
files = sorted(f for f in glob.glob(os.path.join(src, '20*.catalog.txt')) if 2017 <= int(os.path.basename(f)[:4]) <= 2026)
rows, sh = [], {}
for f in files:
    sh[os.path.basename(f)] = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    lines = [l for l in open(f) if l[:4].isdigit()]
    rows.append(pd.read_csv(io.StringIO(''.join(lines)), sep=r'\s+', header=None,
        names=['D','T','ET','GT','MAG','M','LAT','LON','DEPTH','Q','EVID','NPH','NGRM']))
c = pd.concat(rows, ignore_index=True)
c['DATETIME'] = pd.to_datetime(c['D'] + ' ' + c['T'], format='%Y/%m/%d %H:%M:%S.%f', errors='coerce')
bad = int(c.DATETIME.isna().sum())
c = c.dropna(subset=['DATETIME']).sort_values('DATETIME').reset_index(drop=True)
reg = c[(c.LON >= -118.80) & (c.LON <= -115.40) & (c.LAT >= 32.68) & (c.LAT <= 36.20)].copy()
reg['t'] = ((reg.DATETIME - pd.Timestamp('1970-01-01')).dt.total_seconds()).round(2)
out = reg[['EVID','DATETIME','t','LAT','LON','DEPTH','MAG','M','ET']].rename(columns={
    'EVID':'id','DATETIME':'time_utc','LAT':'lat','LON':'lon','DEPTH':'depth_km','MAG':'mag','M':'mag_type','ET':'event_type'})
out['time_utc'] = out.time_utc.dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-4]
with gzip.open('scsn_box_2017_2026.csv.gz', 'wt', compresslevel=9, newline='') as g:
    out.to_csv(g, index=False)
info = dict(dosya_sha256=sh, toplam=len(c), bolge=len(reg), tarih_ayrisamayan_satir=bad,
            ilk=str(reg.DATETIME.min()), son=str(reg.DATETIME.max()),
            yillik_bolge=reg.groupby(reg.DATETIME.dt.year).size().to_dict(),
            olay_turu=reg.ET.value_counts().to_dict(), buyukluk_turu=reg.M.value_counts().to_dict(),
            M4_aday_2018_sonrasi=int(((reg.MAG >= 4) & (reg.DATETIME >= '2018-01-01')).sum()))
json.dump(info, open('catalog_info.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in info.items() if k != 'dosya_sha256'}, indent=1, default=str))
