import pandas as pd, datetime as dt, json, warnings, sys, io, contextlib
warnings.filterwarnings('ignore')
import statseis.foreshocks as F, statseis.utils as U
cat=pd.read_csv('SCSN_reformat.csv'); cat['DATETIME']=pd.to_datetime(cat['DATETIME'])
raw=pd.read_pickle('scsn_raw.pkl') if False else None
region=[-118.80,-115.40,32.68,36.20]
res={}
for name,d in [('tum',cat),('bolge',cat[(cat.LON>=region[0])&(cat.LON<=region[1])&(cat.LAT>=region[2])&(cat.LAT<=region[3])].copy())]:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        ms=F.select_mainshocks(d.reset_index(drop=True))
    ms=ms.loc[ms['DATETIME']>=dt.datetime(2009,1,1)].copy()
    both=(ms.Selection=='Both').sum()
    res[name]=dict(aday=len(ms),Fixed=int((ms.Selection=='FET').sum()+both),MagDep=int((ms.Selection=='MDET').sum()+both),Combined=int(both),
                   secimler=ms.Selection.value_counts().to_dict())
    ms.to_csv(f'mainshocks_{name}.csv',index=False)
json.dump(res,open('step2.json','w'),indent=1,default=int); print(res)
