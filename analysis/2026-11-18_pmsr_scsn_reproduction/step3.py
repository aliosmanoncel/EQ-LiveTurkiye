import pandas as pd, numpy as np, json, warnings, io, contextlib, sys
warnings.filterwarnings('ignore'); sys.path.insert(0,'/home/claude/fpa0')
import statseis.mc as MC
from fpa_ref import esr_independent as esr
from statsmodels.stats.proportion import proportion_confint
cat=pd.read_csv('SCSN_reformat.csv'); cat['DATETIME']=pd.to_datetime(cat['DATETIME'])
R=[-118.80,-115.40,32.68,36.20]
reg=cat[(cat.LON>=R[0])&(cat.LON<=R[1])&(cat.LAT>=R[2])&(cat.LAT<=R[3])].reset_index(drop=True)
ms=pd.read_csv('mainshocks_bolge.csv'); ms['DATETIME']=pd.to_datetime(ms['DATETIME'])
ms=ms[ms.Selection=='Both'].reset_index(drop=True)
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    ms=MC.get_Mcs_400(ms, reg, 'SCSN', start_radius=10, inc=5, max_r=50, min_n=275)
def hav(lon1,lat1,lon2,lat2):
    lon1,lat1,lon2,lat2=map(np.radians,[lon1,lat1,lon2,lat2])
    a=np.sin((lat2-lat1)/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return 2*6371*np.arcsin(np.sqrt(a))
rows=[]
for m in ms.itertuples():
    d=hav(m.LON,m.LAT,reg.LON.values,reg.LAT.values)
    days=(m.DATETIME-reg.DATETIME).dt.total_seconds().values/86400
    sel=(d<10)&(days>0)&(reg.ID.values!=m.ID)
    yeterli=m.n_for_Mc_50>=275
    allb=days[sel]; mags=reg.MAGNITUDE.values[sel]
    typeA=int(((allb<20)&(mags>=3)).sum())
    r=esr(allb[mags>=m.Mc]) if yeterli else {}
    rows.append(dict(ID=m.ID,DATETIME=m.DATETIME,M=m.MAGNITUDE,LAT=m.LAT,LON=m.LON,Mc=m.Mc,n_Mc=m.n_for_Mc_50,r_Mc_km=m.radii_50,
        Mc_yeterli=yeterli,TypeA_n=typeA,N_obs=r.get('n_obs'),n_kalib=r.get('n_regular'),p_emp=r.get('p'),
        q99=r.get('q99'),max_pencere=r.get('max_window'),anlamli=(r.get('p',1)<0.01) if yeterli else None))
df=pd.DataFrame(rows); df.to_csv('SCSN_bolge_61_sonuclar.csv',index=False)
ok=df[df.Mc_yeterli]; k=int(ok.anlamli.sum()); n=len(ok)
lo,hi=proportion_confint(k,n,method='wilson')
ka=int((df.TypeA_n>0).sum())
out=dict(baslik='SCSN Regional Box — Independent Reproduction',combined=len(df),Mc_yetersiz=int((~df.Mc_yeterli).sum()),
  analiz_edilen=n,empirical_anlamli=k,oran=round(k/n,3),wilson95=[round(lo,3),round(hi,3)],
  makale_SCSN_empirical='22% (16/74)',typeA=f'{ka}/{len(df)}',makale_typeA='35% (26/74)',
  Mc_ortanca=float(ok.Mc.median()),Mc_aralik=[float(ok.Mc.min()),float(ok.Mc.max())],r_Mc_dagilim=ok.r_Mc_km.value_counts().to_dict())
json.dump(out,open('step3.json','w'),indent=1,default=str); print(json.dumps(out,indent=1,default=str))
