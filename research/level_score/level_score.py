import pandas as pd, numpy as np
D='/home/claude/DMC-6-Month-Backtest/'
d=pd.read_csv(D+'COINBASE_BTCUSD, 1D_8ee5c.csv',usecols=['time','open','high','low','close','Volume'])
d['t']=pd.to_datetime(d.time,unit='s'); d=d.set_index('t').rename(columns={'Volume':'vol'})
def rs(df,rule): return df.resample(rule,label='left',closed='left').agg({'open':'first','high':'max','low':'min','close':'last','vol':'sum'}).dropna()
def atr(df,n=14):
    tr=np.maximum.reduce([df.high-df.low,(df.high-df.close.shift()).abs(),(df.low-df.close.shift()).abs()]); return pd.Series(tr,index=df.index).ewm(alpha=1/n,adjust=False).mean()
NB=400  # history buckets (log price) -> fixed memory, like a Pine array
def score_tf(df,tf,mult,K=5,W=7,LB=365):
    o,h,l,c,v=[df[k].values for k in ['open','high','low','close','vol']]
    bt=np.maximum(o,c); bb=np.minimum(o,c); a=atr(df).values; n=len(df)
    P=pd.Series(c).rolling(3).mean()-pd.Series(c).rolling(10).mean(); P=P.values
    lo,hi=np.log(df.low.min()*0.9),np.log(df.high.max()*1.1)
    bk=lambda x:np.clip(((np.log(x)-lo)/(hi-lo)*NB).astype(int),0,NB-1)
    BBK=bk(bb); BTK=bk(bt)
    out=[]
    for p in range(max(K,30),n-2):
        for side in (-1,1):
            ext=bb if side==-1 else bt
            win=ext[p-K:p+K+1]
            if (side==-1 and ext[p]>win.min()) or (side==1 and ext[p]<win.max()): continue
            lvl=ext[p]
            # 1 move into it: from opposite extreme of prior 30 bars
            prev=(bt if side==-1 else bb)[p-30:p]
            move=(prev.max()-lvl) if side==-1 else (lvl-prev.min())
            if move<=0: continue
            s1=min(move/lvl/0.20,1)*2
            # 2 reaction: from first opposite candle C1, W candles, share of move retraced (by close)
            j=p+1
            while j<n and not ((c[j]>o[j]) if side==-1 else (c[j]<o[j])): j+=1
            if j+W>n: continue
            rx=(c[j:j+W].max()-lvl) if side==-1 else (lvl-c[j:j+W].min())
            if rx<=0: continue
            ratio=rx/move; s2=min(ratio/0.5,1)*2
            # 0 history: bars whose BODY covered this bucket in the LB bars before (fixed buckets)
            b=bk(np.array([lvl]))[0]
            j0=j+W  # end of reaction window
            cov=(BBK<=b)&(b<=BTK)
            hb=int(cov[max(0,p-LB):max(0,p-30)].sum())+int(cov[j0:].sum())   # before the turn + after it formed (to today)
            s0=min(hb/60,1)*2
            # 5 volume at the turn vs prior 50 median
            med=np.median(v[max(0,p-50):p]) if p>0 else 0
            rv=v[p-1:p+2].max()/med if med>0 else 1
            s5=float(np.clip((rv-1)/2,0,1))
            confirm=j+W-1
            # 3 retest + 4 momentum: first touch after confirmation (body/wick into level)
            s3=s4=0; flip_after=None
            for q in range(confirm+1,min(n,confirm+120)):
                touched=(l[q]<=lvl) if side==-1 else (h[q]>=lvl)
                if touched:
                    held=(c[q]>lvl) if side==-1 else (c[q]<lvl)
                    if held:
                        s3=2
                        if q+2<n and ((P[q+2]>P[q+1]>P[q]) if side==-1 else (P[q+2]<P[q+1]<P[q])): s4=1
                    else: flip_after=q
                    break
            # 6 flip history: an opposite-side turn at this price earlier (fixed bucket check of prior pivots)
            s6=0
            for r in out:
                if r['side']==-side and abs(r['price']-lvl)<=0.5*a[p] and r['pv']<df.index[p]: s6=1;break
            raw=s0+s1+s2+s3+s4+s5+s6
            score=min(raw/11*10*mult,10)
            out.append(dict(tf=tf,pv=df.index[p],side=side,price=round(lvl),hist=round(s0,1),move=round(s1,1),react=round(s2,1),retest=s3,momo=s4,vol=round(s5,1),flip=s6,score=round(score,1),move_pct=round(move/lvl*100,1),react_pct=round(ratio*100)))
    return pd.DataFrame(out)
lvD=score_tf(d,'D',1.0); lvW=score_tf(rs(d,'W-MON'),'W',1.15,K=3,W=4,LB=104)
L=pd.concat([lvD,lvW]); L.to_csv('level_scores.csv',index=False)
QUAL=3.0
def zones(L,atr_now,asof):
    q=L[(L.score>=QUAL)&(L['pv']<=asof)].sort_values('price').to_dict('records')
    Z=[]
    for r in q:
        w=atr_now*r['price']
        if Z and r['price']-Z[-1]['lo']<=1.0*w and r['price']-Z[-1]['hi']<=0.75*w:
            z=Z[-1]; z['m'].append(r); z['hi']=max(z['hi'],r['price'])
        else: Z.append(dict(lo=r['price'],hi=r['price'],m=[r]))
    rows=[]
    for z in Z:
        best=max(z['m'],key=lambda r:r['score']); tfs=sorted({r['tf'] for r in z['m']},key=lambda t:'MWD'.index(t))
        rsv=min(best['score']+0.5*(len(tfs)-1),10)
        rows.append(dict(lo=z['lo'],hi=z['hi'],tfs='/'.join(tfs),n=len(z['m']),rs=round(rsv,1),best=f"{best['tf']} {best['pv'].date()} {best['price']}"))
    return pd.DataFrame(rows)
A=atr(d).iloc[-1]/d.close.iloc[-1]
QUAL=6
Zall=zones(L,A,d.index[-1])
for name,lo,hi in [('2019-20 box',6500,14500),('2021-22 box',28000,40000),('2023 box',24000,32500),('2024-25 top box',88000,100500),('ALL 45K-130K',45000,130000)]:
    Z=Zall[(Zall.hi>=lo)&(Zall.lo<=hi)]
    print(f"\n== {name}: {len(Z)} zones rs>=6"); print(Z.to_string(index=False))
print(L[(L.price>83000)&(L.price<86000)&(L['pv']>='2025-11-01')&(L['pv']<'2025-12-31')].to_string(index=False))
