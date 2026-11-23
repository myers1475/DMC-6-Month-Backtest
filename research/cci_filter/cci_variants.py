import pandas as pd, numpy as np
d = pd.read_csv("../../CME_MINI_NQ1!, 60_f4c9d.csv")[['time','open','high','low','close']]
d['ts']=pd.to_datetime(d.time,unit='s',utc=True).dt.tz_convert('America/New_York')
def run(mode, anchor, cn=27, lb=18, k=0.8):
    x=d.copy()
    if mode=='RTH':
        h=x.ts.dt.hour; x=x[(h>=9)&(h<16)]   # 60m bars stamped 9:00..15:00 ET (9:00 bar = 9:30 open on 60m? use as is)
        x['sess']=x.ts.dt.date
    else: x['sess']=(x.ts+pd.Timedelta(hours=6)).dt.date
    D=x.groupby('sess').agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'),n=('open','size'))
    D=D[D.n>=(5 if mode=='RTH' else 10)]
    tr=pd.concat([D.high-D.low,(D.high-D.close.shift()).abs(),(D.low-D.close.shift()).abs()],axis=1).max(axis=1)
    D['atr']=tr.ewm(alpha=1/40,adjust=False).mean()
    tp=(D.high+D.low+D.close)/3; sma=tp.rolling(cn).mean()
    md=tp.rolling(cn).apply(lambda v: np.abs(v-v.mean()).mean(),raw=True)
    D['lo']=((tp-sma)/(0.015*md)).rolling(lb).min()
    P=D.shift(1); out=[]
    for s,g in x.groupby('sess'):
        if s not in P.index or pd.isna(P.loc[s,'lo']) or pd.isna(P.loc[s,'atr']): continue
        p=P.loc[s]; base=p.low if anchor=='low' else p.close
        trig=base+k*p.atr; hit=g[g.high>=trig]
        if hit.empty: continue
        ent=max(trig,hit.iloc[0].open); out.append((g.close.iloc[-1]-ent, p.lo< -100))
    return pd.DataFrame(out,columns=['pts','f'])
def s(t):
    R=-t[t.pts<=0].pts.mean(); eq=t.pts.cumsum(); dd=-(eq-eq.cummax()).min()
    return f"n={len(t):4d} WR={(t.pts>0).mean():5.1%} exp={t.pts.mean()/R:+.3f}R NET R={t.pts.sum()/R:+6.1f} P/DD={t.pts.sum()/dd:5.2f}"
for mode in ('ETH','RTH'):
  for anchor in ('low','close'):
    t=run(mode,anchor)
    print(f"{mode} anchor=prior {anchor:5s} | base {s(t)}\n{'':26s}| CCI on {s(t[t.f])}\n{'':26s}| CCI off {s(t[~t.f])}")
print("\nNeighborhood (RTH, prior low): NET R of filtered set vs excluded set")
for cn in (20,27,34):
  for lb in (10,18,26):
    t=run('RTH','low',cn,lb); R=-t[t.pts<=0].pts.mean()
    print(f"CCI({cn}) lookback {lb}: kept n={t.f.sum():4d} expR={t[t.f].pts.mean()/R:+.3f} | excluded n={(~t.f).sum():4d} expR={t[~t.f].pts.mean()/R:+.3f}")
