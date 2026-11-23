import pandas as pd, numpy as np
ny='America/New_York'
def load(f):
    d=pd.read_csv(f)[['time','open','high','low','close']]
    d['ts']=pd.to_datetime(d.time,unit='s',utc=True).dt.tz_convert(ny); return d
m5=load("../../CME_MINI_MNQ1!, 5_e2017.csv")
q15=load("../../CME_MINI_NQ1!, 15_0bd8f.csv")
# daily bars (Globex day) for CCI: 15m NQ history, 5m MNQ for days after it ends
src=pd.concat([q15[q15.ts<m5.ts.min()], m5]).sort_values('ts')
src['sess']=(src.ts+pd.Timedelta(hours=6)).dt.date
D=src.groupby('sess').agg(high=('high','max'),low=('low','min'),close=('close','last'),n=('open','size'))
D=D[D.n>=20]
tp=(D.high+D.low+D.close)/3; sma=tp.rolling(27).mean()
md=tp.rolling(27).apply(lambda v: np.abs(v-v.mean()).mean(),raw=True)
cci=(tp-sma)/(0.015*md); D['lo18']=cci.rolling(18).min(); D['hi18']=cci.rolling(18).max()
P=D.shift(1)   # known before today's open
TGT,STP=50,100
m5['date']=m5.ts.dt.date; m5['hm']=m5.ts.dt.strftime('%H:%M')
rows=[]
for day,g in m5.groupby('date'):
    box=g[g.hm=='09:30']
    if box.empty or day not in P.index or pd.isna(P.loc[day,'lo18']): continue
    bh,bl=box.high.iloc[0],box.low.iloc[0]
    w=g[(g.hm>'09:30')&(g.hm<'12:00')]
    out=[]  # first breakout, then reversal (first close outside opposite side)
    for i,(idx,b) in enumerate(w.iterrows()):
        side='L' if b.close>bh else 'S' if b.close<bl else None
        if side is None: continue
        if not out: out.append(('first',side,i))
        elif side!=out[0][1]: out.append(('reversal',side,i)); break
    for kind,side,i in out:
        ent=w.close.iloc[i]; rest=w.iloc[i+1:]; res=None; mfe=mae=0
        for _,b in rest.iterrows():
            up=b.high-ent; dn=ent-b.low
            fav,adv=(up,dn) if side=='L' else (dn,up)
            mfe=max(mfe,fav); mae=max(mae,adv)
            if adv>=STP: res=-STP; break          # stop checked first (conservative)
            if fav>=TGT: res=TGT; break
        if res is None:
            ex=rest.close.iloc[-1] if len(rest) else ent
            res=(ex-ent) if side=='L' else (ent-ex)
        p=P.loc[day]
        filt = p.lo18< -100 if side=='L' else p.hi18>100
        rows.append(dict(date=day,kind=kind,side=side,entry=ent,pts=res,R=res/STP,filt=filt,mfe=mfe,mae=mae))
T=pd.DataFrame(rows); T.to_csv('box930_trades.csv',index=False)
def st(x,lab):
    if len(x)==0: print(f"{lab:40s} n=0"); return
    w=x[x.pts>0]; l=x[x.pts<=0]
    rr=w.pts.mean()/-l.pts.mean() if len(l) and len(w) else float('nan')
    e=x.R.mean()
    print(f"{lab:40s} n={len(x):3d} WR={len(w)/len(x):5.1%} RR={rr:4.2f} exp={e:+.3f}R NET R={x.R.sum():+6.2f}  ${e*250:+5.0f}-{e*500:+4.0f}/trade @ $250-500/R")
print(f"Window {T.date.min()} to {T.date.max()}; days in filter state: long-ok {(P.loc[T.date.unique(),'lo18']<-100).sum()}")
for kind in ('first','reversal'):
    print(f"\n--- {kind} breakout ---")
    x=T[T.kind==kind]
    st(x,'all'); 
    for s,n in (('L','LONG'),('S','SHORT')):
        y=x[x.side==s]; st(y,f'{n} all'); st(y[y.filt],f'{n} CCI filter ON'); st(y[~y.filt],f'{n} filtered OUT')
print("\nMonthly CCI-long state (share of days filter allows longs):")
dd=P.loc[sorted(T.date.unique())]; print((dd.lo18< -100).groupby(pd.to_datetime(dd.index).to_period('M')).mean().round(2).to_string())
