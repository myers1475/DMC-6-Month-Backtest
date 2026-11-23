import pandas as pd, numpy as np, sys
f = sys.argv[1]
d = pd.read_csv(f)[['time','open','high','low','close']]
d['ts'] = pd.to_datetime(d.time, unit='s', utc=True).dt.tz_convert('America/New_York')
d['sess'] = (d.ts + pd.Timedelta(hours=6)).dt.date          # Globex day 18:00-17:00 ET
D = d.groupby('sess').agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'),n=('open','size'))
D = D[D.n >= 10]
tr = pd.concat([D.high-D.low,(D.high-D.close.shift()).abs(),(D.low-D.close.shift()).abs()],axis=1).max(axis=1)
D['atr'] = tr.rolling(40).mean()          # simple avg; Pine uses RMA - checked both below
D['atr_rma'] = tr.ewm(alpha=1/40, adjust=False).mean()
def cci(n):
    tp=(D.high+D.low+D.close)/3; sma=tp.rolling(n).mean()
    md=tp.rolling(n).apply(lambda x: np.abs(x-x.mean()).mean(), raw=True)
    return (tp-sma)/(0.015*md)
D['cci']=cci(27)
D['lo18']=D.cci.rolling(18).min(); D['hi18']=D.cci.rolling(18).max()
P = D.shift(1)   # everything known at start of today's session
rows=[]
for s,g in d.groupby('sess'):
    if s not in D.index or pd.isna(P.loc[s,'atr_rma']) or pd.isna(P.loc[s,'lo18']): continue
    p=P.loc[s]; ex=g.close.iloc[-1]
    for side in ('L','S'):
        trig = p.low + 0.8*p.atr_rma if side=='L' else p.high - 0.8*p.atr_rma
        hit = g[g.high>=trig] if side=='L' else g[g.low<=trig]
        if hit.empty: continue
        b=hit.iloc[0]
        ent = max(trig,b.open) if side=='L' else min(trig,b.open)
        pts = ex-ent if side=='L' else ent-ex
        filt = p.lo18 < -100 if side=='L' else p.hi18 > 100
        rows.append(dict(sess=s,side=side,entry=ent,exit=ex,pts=pts,filt=filt,year=pd.Timestamp(s).year))
T=pd.DataFrame(rows); T.to_csv(sys.argv[2],index=False)
def stats(x,label):
    w=x[x.pts>0]; l=x[x.pts<=0]
    wr=len(w)/len(x); rr=w.pts.mean()/-l.pts.mean(); R=-l.pts.mean()
    exp=x.pts.mean(); netR=x.pts.sum()/R
    eq=x.pts.cumsum(); dd=(eq-eq.cummax()).min()
    print(f"{label:34s} n={len(x):4d} WR={wr:5.1%} RR={rr:4.2f} exp={exp/R:+.3f}R ({exp:+6.1f}pt, ${exp*2:+5.0f}/MNQ) NET={x.pts.sum():+8.0f}pt NET R={netR:+6.1f} maxDD={dd:7.0f}pt P/DD={x.pts.sum()/-dd:5.2f} avgLoss(1R)={R:5.1f}pt")
for side in ('L','S'):
    x=T[T.side==side]; print(f"\n=== {'LONG' if side=='L' else 'SHORT'} ({x.sess.min()} to {x.sess.max()}) ===")
    stats(x,'base (all breakouts)')
    stats(x[x.filt],'CCI filter ON (correction seen)')
    stats(x[~x.filt],'filtered OUT (no correction)')
x=T[T.side=='L']
print("\nLONG by year: base pts / filtered pts / n_filtered")
for y,g in x.groupby('year'): print(y, f"{g.pts.sum():+7.0f}", f"{g[g.filt].pts.sum():+7.0f}", f"{g.filt.sum():3d}/{len(g)}")
