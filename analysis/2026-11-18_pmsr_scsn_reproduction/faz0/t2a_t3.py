import numpy as np, json
from fpa_ref import esr_independent as ind
rng=np.random.default_rng(2026)
RATES=[0.05,0.2,1.0,5.0]   # olay/gün (R ve Mc içinde)
N=1000
out={'T2a':{},'T3':{}}
for r in RATES:
    ps=[]
    for _ in range(N):
        d=rng.uniform(0,385,rng.poisson(r*385)); ps.append(ind(d)['p'])
    ps=np.array(ps)
    out['T2a'][r]={a:float(np.mean(ps<a)) for a in (0.01,0.05,0.10)}
    out['T2a'][r]['N_obs_ort']=r*20
for r in [0.2,1.0]:
    out['T3'][r]={}
    for m in [1,2,5,10]:
        for name,(t0,t1) in {'20g_tamami':(0,20),'son_5g':(0,5),'ilk_5g(15-20g)':(15,20)}.items():
            hit=0
            for _ in range(500):
                d=rng.uniform(0,385,rng.poisson(r*385))
                extra=rng.poisson((m-1)*r*20)          # aynı toplam fazla olay, farklı süreye sıkıştırılmış
                d=np.r_[d,rng.uniform(t0,t1,extra)]
                hit+=ind(d)['p']<0.01
            out['T3'][r][f'x{m}_{name}']=hit/500
json.dump(out,open('t2a_t3.json','w'),indent=1)
print(json.dumps(out,indent=1))
