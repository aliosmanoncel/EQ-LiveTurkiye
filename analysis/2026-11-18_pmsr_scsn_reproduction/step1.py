import pandas as pd, glob, io, hashlib, json, datetime as dt, numpy as np
rows=[]; sh={}
for f in sorted(glob.glob('/mnt/user-data/uploads/Downloads/20*.txt')):
    sh[f.split('/')[-1]]=hashlib.sha256(open(f,'rb').read()).hexdigest()
    lines=[l for l in open(f) if l[:4].isdigit()]
    rows.append(pd.read_csv(io.StringIO(''.join(lines)),sep=r'\s+',header=None,
        names=['D','T','ET','GT','MAG','M','LAT','LON','DEPTH','Q','EVID','NPH','NGRM']))
c=pd.concat(rows,ignore_index=True)
c['DATETIME']=pd.to_datetime(c['D']+' '+c['T'],format='%Y/%m/%d %H:%M:%S.%f')
cat=c[['EVID','MAG','DATETIME','DEPTH','LON','LAT']].copy(); cat.columns=['ID','MAGNITUDE','DATETIME','DEPTH','LON','LAT']
cat=cat.sort_values('DATETIME').reset_index(drop=True)
reg=cat[(cat.LON>=-118.80)&(cat.LON<=-115.40)&(cat.LAT>=32.68)&(cat.LAT<=36.20)]
out=dict(dosya_sha256=sh,toplam=len(cat),bolge=len(reg),hedef_toplam=179446,hedef_bolge=148280,
         yillik=cat.groupby(cat.DATETIME.dt.year).size().to_dict(),
         M4_aday_2009_sonrasi=int(((cat.MAGNITUDE>=4)&(cat.DATETIME>=dt.datetime(2009,1,1))).sum()),
         M4_aday_bolge=int(((reg.MAGNITUDE>=4)&(reg.DATETIME>=dt.datetime(2009,1,1))).sum()))
cat.to_csv('SCSN_reformat.csv',index=False)
json.dump(out,open('step1.json','w'),indent=1,default=str); print({k:v for k,v in out.items() if k!='dosya_sha256'})
