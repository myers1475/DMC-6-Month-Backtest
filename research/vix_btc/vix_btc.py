import pandas as pd, numpy as np
v=pd.read_csv('TVC_VIX, 1D_e9e28.csv'); v['d']=pd.to_datetime(v.time,unit='s').dt.normalize()
b=pd.read_csv('COINBASE_BTCUSD, 1D_2c701.csv'); b['d']=pd.to_datetime(b.time,unit='s').dt.normalize()
b=b.set_index('d')
H=pd.to_datetime(['2012-11-28','2016-07-09','2020-05-11','2024-04-19'])
def phase(d):
    h=H[H<=d].max(); m=(d-h).days/30.44
    return 'Halving chop' if m<6 else 'Expansion' if m<15 else 'Topping' if m<20 else 'Stay out' if m<27 else 'Bottom accumulation' if m<33 else 'Recovery'
def episodes(cond, gap=20):
    out=[]; last=-999
    idx=np.where(cond)[0]
    for i in idx:
        if i-last>gap: out.append(i)
        last=i
    return out
def fwd(d):
    if d not in b.index: return None
    p=b.close.loc[d]; r={}
    for k in (30,90,180,365):
        t=d+pd.Timedelta(days=k)
        r[f'{k}d']=(b.close.loc[t]/p-1)*100 if t in b.index else np.nan
    w=b.loc[d:d+pd.Timedelta(days=180)]
    r['maxDD180']=(w.low.min()/p-1)*100
    r['btc']=p
    return r
v=v[v.d>='2015-01-01'].reset_index(drop=True)
rows=[]
for name,cond in [('close>35',v.close>35),('high>35',v.high>35),('close 25-35',(v.close>25)&(v.close<=35)),('close<15',v.close<15)]:
    for i in episodes(cond.values):
        d=v.d[i]; f=fwd(d)
        if f: rows.append(dict(sig=name,date=d.date(),vix=v.close[i],phase=phase(d),**f))
df=pd.DataFrame(rows); df.to_csv('research/vix_btc/episodes.csv',index=False)
pd.set_option('display.width',200)
for s in ['close>35','high>35']:
    print('\n==',s); print(df[df.sig==s].round(1).to_string(index=False))
for s in ['close 25-35','close<15']:
    g=df[df.sig==s]
    print(f'\n== {s}: n={len(g)} | median 90d {g["90d"].median():.0f}% 180d {g["180d"].median():.0f}% 365d {g["365d"].median():.0f}% | 180d up {(g["180d"]>0).mean()*100:.0f}% | median maxDD180 {g.maxDD180.median():.0f}%')
    print(g.groupby('phase')[['90d','180d','365d','maxDD180']].median().round(0).assign(n=g.groupby('phase').size()).to_string())
