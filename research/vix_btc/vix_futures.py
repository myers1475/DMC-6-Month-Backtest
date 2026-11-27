import pandas as pd, numpy as np
def daily(files):
    parts=[]
    for f in files:
        d=pd.read_csv(f); d['t']=pd.to_datetime(d.time,unit='s'); parts.append(d[['t','open','high','low','close']])
    d=pd.concat(parts).drop_duplicates('t').sort_values('t')
    ny=d.t.dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)
    d['day']=(ny+pd.Timedelta(hours=7)).dt.normalize()   # 17:00 ET session close -> next date
    g=d.groupby('day').agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'))
    return g[g.index.dayofweek<5]
NQ=daily(['CME_MINI_NQ1!, 60_f4c9d.csv','CME_MINI_NQ1!, 15_22fcb.csv'])
GC=daily(['COMEX_MINI_MGC1!, 60_59673.csv','COMEX_MINI_MGC1!, 15_6c3bd.csv'])
ES=daily(['CME_MINI_MES1!, 15_062c6.csv'])
v=pd.read_csv('TVC_VIX, 1D_e9e28.csv'); v['day']=pd.to_datetime(v.time,unit='s').dt.normalize(); v=v.set_index('day')
v=v[v.index>='2019-11-04']
print('== Same-day correlation: VIX daily % change vs futures daily % change')
for nm,X in [('NQ',NQ),('MGC (gold)',GC),('MES (2025-26 only)',ES)]:
    j=pd.concat([v.close.pct_change().rename('vix'),X.close.pct_change().rename('x')],axis=1).dropna()
    big=j[j.vix>0.15]
    print(f'{nm}: corr {j.corr().iloc[0,1]:+.2f} (n={len(j)}) | on days VIX jumped 15%+ (n={len(big)}): median {nm} move {big.x.median()*100:+.2f}%, down {(big.x<0).mean()*100:.0f}% of the time')
# spikes
def eps(cond,gap=20):
    out=[];last=-999
    for i in np.where(cond)[0]:
        if i-last>gap: out.append(i)
        last=i
    return out
print('\n== After a VIX daily close >= 30 (new spike), forward returns')
rows=[]
for i in eps((v.close>=30).values):
    d=v.index[i]; r=dict(date=d.date(),vix=round(v.close.iloc[i],1))
    for nm,X in [('NQ',NQ),('GC',GC)]:
        if d not in X.index: continue
        p=X.close.loc[d]
        for k in (30,90,180):
            t=X.index[X.index>=d+pd.Timedelta(days=k)]
            r[f'{nm}{k}']=round((X.close.loc[t[0]]/p-1)*100,1) if len(t) else np.nan
        r[f'{nm}dd90']=round((X.low.loc[d:d+pd.Timedelta(days=90)].min()/p-1)*100,1)
    rows.append(r)
s=pd.DataFrame(rows); print(s.to_string(index=False))
print('\n== Baseline: any day 2019-11..2026 (median forward return)')
for nm,X in [('NQ',NQ),('GC',GC)]:
    out=[]
    for k in (30,90,180):
        f=[(X.close.loc[X.index[X.index>=d+pd.Timedelta(days=k)][0]]/X.close.loc[d]-1)*100 for d in X.index if (X.index>=d+pd.Timedelta(days=k)).any()]
        out.append(f'{k}d {np.median(f):+.1f}% (up {np.mean(np.array(f)>0)*100:.0f}%)')
    sp=s[[f'{nm}30',f'{nm}90',f'{nm}180']].dropna(how='all')
    print(nm,'baseline:',' | '.join(out))
    print(nm,'after VIX30 spikes: median',' '.join(f'{k}d {sp[f"{nm}{k}"].median():+.1f}% (up {(sp[f"{nm}{k}"]>0).mean()*100:.0f}%)' for k in (30,90,180)), f'| median 90d drawdown {s[f"{nm}dd90"].median():.1f}%')
s.to_csv('research/vix_btc/vix_spikes_nq_gold.csv',index=False)
