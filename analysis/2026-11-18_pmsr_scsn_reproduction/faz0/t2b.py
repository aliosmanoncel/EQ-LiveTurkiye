import numpy as np, json
from fpa_ref import esr_independent as ind
rng=np.random.default_rng(7)
beta=np.log(10)*1.0; alpha=1.7; c=0.01; p=1.1; DMAX=4.0
def gr(n): 
    u=rng.random(n); return -np.log(1-u*(1-np.exp(-beta*DMAX)))/beta   # 0..4 kesik GR (M-Mc)
def omori(n):  # p>1 kesik olmayan Omori-Utsu zaman ofsetleri
    u=rng.random(n); return c*((1-u)**(-1/(p-1))-1)
def etas(T,mu,nbr):
    K=nbr*(beta-alpha)/beta
    t=rng.uniform(0,T,rng.poisson(mu*T)); m=gr(t.size)
    allt=[t]; allm=[m]; gt,gm=t,m
    while gt.size:
        k=rng.poisson(K*np.exp(alpha*gm))
        par=np.repeat(gt,k); 
        ct=par+omori(par.size); keep=ct<T
        ct=ct[keep]; cm=gr(ct.size)
        allt.append(ct); allm.append(cm); gt,gm=ct,cm
    t=np.concatenate(allt); m=np.concatenate(allm); o=np.argsort(t); return t[o],m[o]
res={}
for nbr in [0.3,0.6,0.8]:
    mu=0.2*(1-nbr)       # toplam ortalama oran ~0.2 olay/gün
    fp=[];fs=[];nfs=0
    for rep in range(150):
        t,m=etas(3000,mu,nbr)
        # (a) rastgele referans zamanları
        for tr in rng.uniform(400,3000,10):
            d=tr-t[t<tr]; fp.append(ind(d)['p']<0.01)
        # (b) "ana şok" = M-Mc>=2 olaylar, kendisinden önce 1 yıl/385 gün içinde daha büyük olay yok
        for i in np.where((m>=2)&(t>400))[0]:
            prev=(t>t[i]-365)&(t<t[i])
            if np.any(m[prev]>m[i]): continue
            d=t[i]-t[:i]; fs.append(ind(d)['p']<0.01); nfs+=1
    res[nbr]=dict(rastgele_zaman_p01=float(np.mean(fp)),n_rastgele=len(fp),
                  anasok_oncesi_p01=float(np.mean(fs)) if fs else None,n_anasok=nfs)
json.dump(res,open('t2b.json','w'),indent=1); print(json.dumps(res,indent=1))
