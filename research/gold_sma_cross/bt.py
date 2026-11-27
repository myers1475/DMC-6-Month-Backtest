"""MGC 4H 50/100/200 SMA cross system (Matt's rule).
Entry LONG: 50 SMA above both 100 and 200, and the first 4H close above all three
lines since the 50 got on top -> enter next bar open. SHORT mirror.
Exits tested (Matt had no preference):
  A: 50 crosses back below the 100 (long) / above the 100 (short)
  B: 50 loses either line (no longer above both)
  C: opposite signal fires (flip, always in)
No stop, no level TPs/adds (core signal only). Exit at next bar open after the closing bar.
4H bars built from 1h (2019-11..2026-08) + 15m (2025-03..2026-11), anchored to the 18:00 ET session open.
"""
import pandas as pd, numpy as np
def load(f):
    d=pd.read_csv(f); d['t']=pd.to_datetime(d.time,unit='s'); return d[['t','open','high','low','close']]
h1=load('COMEX_MINI_MGC1!, 60_59673.csv'); m15=load('COMEX_MINI_MGC1!, 15_6c3bd.csv')
base=pd.concat([h1, m15[m15.t>h1.t.max()]]).sort_values('t')
ny=base.t.dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)
base['k']=(ny-pd.Timedelta(hours=18)).dt.floor('4h')
b=base.groupby('k').agg(t=('t','first'),open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last')).reset_index(drop=True)
c=b.close
for n in (50,100,200): b[f's{n}']=c.rolling(n).mean()
b=b.dropna().reset_index(drop=True)
o,h,l,c,s50,s100,s200=(b[k].values for k in ['open','high','low','close','s50','s100','s200'])
n=len(b)
up=(s50>s100)&(s50>s200); dn=(s50<s100)&(s50<s200)
def signals():
    sig=np.zeros(n,int); armL=armS=False
    for i in range(n):
        if up[i] and (i==0 or not up[i-1]): armL=True
        if not up[i]: armL=False
        if dn[i] and (i==0 or not dn[i-1]): armS=True
        if not dn[i]: armS=False
        if armL and c[i]>max(s50[i],s100[i],s200[i]): sig[i]=1; armL=False
        if armS and c[i]<min(s50[i],s100[i],s200[i]): sig[i]=-1; armS=False
    return sig
sig=signals()
def run(mode):
    tr=[]; i=0
    while i<n-1:
        if sig[i]!=0:
            d=sig[i]; e=o[i+1]; j=i+1; mae=0; mfe=0
            while j<n-1:
                mae=max(mae,(e-l[j]) if d==1 else (h[j]-e)); mfe=max(mfe,(h[j]-e) if d==1 else (e-l[j]))
                if mode=='A': ex = s50[j]<s100[j] if d==1 else s50[j]>s100[j]
                elif mode=='B': ex = (not up[j]) if d==1 else (not dn[j])
                else: ex = sig[j]==-d
                if ex: break
                j+=1
            x=o[j+1] if j+1<n else c[n-1]
            tr.append(dict(dir='L' if d==1 else 'S',entry_t=b.t[i+1],exit_t=b.t[min(j+1,n-1)],entry=e,exit=x,pts=(x-e)*d,mae=mae,mfe=mfe,open=(j>=n-1)))
            i = j if mode=='C' else j+1
        else: i+=1
    return pd.DataFrame(tr)
def rep(df,lab):
    w=df[df.pts>0]; L=df[df.pts<=0]
    print(f"{lab}: trades {len(df)} | win {len(w)/len(df)*100:.0f}% | avg win {w.pts.mean():+.0f} pts avg loss {L.pts.mean():+.0f} pts | RR {w.pts.mean()/abs(L.pts.mean()):.2f} | NET {df.pts.sum():+.0f} pts = ${df.pts.sum()*10:+,.0f}/MGC | median MAE {df.mae.median():.0f} pts, 90th pct MAE {df.mae.quantile(.9):.0f} pts")
print('4H bars',n,b.t.iloc[0],b.t.iloc[-1])
for m in 'ABC':
    df=run(m); df.to_csv(f'research/gold_sma_cross/trades_{m}.csv',index=False)
    rep(df,f'Exit {m} all'); rep(df[df.dir=="L"],f'   longs'); rep(df[df.dir=="S"],f'   shorts')
    for y,g in df.groupby(df.entry_t.dt.year): rep(g,f'     {y}')
