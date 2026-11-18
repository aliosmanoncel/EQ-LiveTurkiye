import numpy as np, time, json
from fpa_ref import esr_independent as ind, esr_statseis as ref
from multiprocessing import Pool
res={}
# --- T1: el hesabı vakaları
cases={
 'bos_katalog': ([], dict(n_obs=0)),
 'yalniz_onculer': ([1.0, 5.0, 19.9], dict(n_obs=3, p=0.0)),       # kalibrasyon boş, N>0 -> p=0 (anlamlı)
 'sinir_20gun': ([20.0], dict(n_obs=0)),                            # tam 20. gün kalibrasyona aittir
 'sinir_19.999': ([19.999], dict(n_obs=1)),
 'tek_kalib_olay': ([100.0], dict(n_obs=0, p=1.0)),                 # N_obs=0 -> tüm pencereler >=0 -> p=1
 'esit_sayi': ([5.0, 100.0], dict(n_obs=1)),                       # p = 20 günlük pencerelerin 100. günü içerme oranı
 '385_disarida': ([385.0, 10.0], dict(n_obs=1, n_regular=0)),
}
t1={}
for k,(d,exp) in cases.items():
    a=ind(d); b=ref(d)
    ok_exp=all(abs(a[x]-v)<1e-12 for x,v in exp.items())
    same=all((np.isnan(a[x]) and np.isnan(b[x])) or abs(a[x]-b[x])<1e-12 for x in ['n_obs','p','n_regular'])
    t1[k]=dict(ind=a['p'],ref=b['p'],n_obs=a['n_obs'],beklenen=ok_exp,uyum=same)
# hand value for 'esit_sayi': windows p in [20,345] step .01 -> 32501; contain d=100 iff 80 <= p < 100 -> 2000 windows
a=ind([5.0,100.0]); t1['esit_sayi']['el_hesabi']=2000/32501; t1['esit_sayi']['el_uyum']=abs(a['p']-2000/32501)<1e-12
res['T1']=t1
# --- T4: rastgele kataloglar
rng=np.random.default_rng(42); cats=[]
for i in range(24):
    rate=rng.choice([0.02,0.1,0.5,2.0]); n=rng.poisson(rate*385)
    d=rng.uniform(0,385,n)
    if i%4==0: d=np.r_[d, rng.uniform(0,20,rng.integers(1,15))]
    if i%5==0: d=np.round(d,2)
    cats.append(d)
with Pool(2) as pl: refs=pl.map(ref,cats)
t4=[]
for i,(d,b) in enumerate(zip(cats,refs)):
    a=ind(d)
    t4.append(dict(i=i,n=len(d),n_obs=a['n_obs'],p_ind=a['p'],p_ref=b['p'],dp=abs(a['p']-b['p']),
                   q99_ind=a['q99'],q99_ref=b['q99'],max_eq=a['max_window']==b['max_window']))
tr=ti=0
res['T4']=dict(n=len(t4),max_dp=max(x['dp'] for x in t4),
               q99_esit=all(abs(x['q99_ind']-x['q99_ref'])<1e-9 for x in t4),
               max_esit=all(x['max_eq'] for x in t4),
               
               ornek=t4[:6])
json.dump(res,open('t1_t4.json','w'),indent=1,default=float)
print(json.dumps(res['T1'],indent=0,default=float)); print({k:v for k,v in res['T4'].items() if k!='ornek'})
