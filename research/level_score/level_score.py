import pandas as pd, numpy as np
D='/home/claude/DMC-6-Month-Backtest/'
d=pd.read_csv(D+'COINBASE_BTCUSD, 1D_8ee5c.csv',usecols=['time','open','high','low','close','Volume'])
d['t']=pd.to_datetime(d.time,unit='s'); d=d.set_index('t').rename(columns={'Volume':'vol'})
def rs(df,rule): return df.resample(rule,label='left',closed='left').agg({'open':'first','high':'max','low':'min','close':'last','vol':'sum'}).dropna()
def atr(df,n=14):
    tr=np.maximum.reduce([df.high-df.low,(df.high-df.close.shift()).abs(),(df.low-df.close.shift()).abs()]); return pd.Series(tr,index=df.index).ewm(alpha=1/n,adjust=False).mean()
NB=400  # history buckets (log price) -> fixed memory, like a Pine array
def score_tf(df,tf,mult,dpb,atr_pct,K=5,W=7,LB_days=365):
    o,h,l,c,v=[df[k].values for k in ['open','high','low','close','vol']]
    bt=np.maximum(o,c); bb=np.minimum(o,c); n=len(df); rng_=h-l
    LB=int(LB_days/dpb); X30=max(1,int(30/dpb)); CAP=60/dpb; RW=max(5,int(60/dpb))
    out=[]; seen={}
    for p in range(max(K,30),n-2):
        for side in (-1,1):
            ext=bb if side==-1 else bt
            win=ext[p-K:p+K+1]
            if (side==-1 and ext[p]>win.min()) or (side==1 and ext[p]<win.max()): continue
            lvl=ext[p]
            key=(side,round(lvl))
            if key in seen and p-seen[key]<=2: continue   # duplicate: same body edge on back-to-back candles
            seen[key]=p
            prev=(bt if side==-1 else bb)[p-30:p]
            move=(prev.max()-lvl) if side==-1 else (lvl-prev.min())
            if move<=0: continue
            # 1 move into it: best of trend (% of price) and range (share of prior range height)
            s1t=min(move/lvl/0.20,1)*2
            rh=bt[max(0,p-RW):p+1].max()-bb[max(0,p-RW):p+1].min(); fr=move/rh if rh>0 else 0
            s1r=2 if fr>1/3 else (1 if fr>=0.25 else 0)
            s1=max(s1t,s1r)
            # 2 reaction from first opposite candle C1, W candles
            j=p+1
            while j<n and not ((c[j]>o[j]) if side==-1 else (c[j]<o[j])): j+=1
            if j+W>n: continue
            rx=(c[j:j+W].max()-lvl) if side==-1 else (lvl-c[j:j+W].min())
            if rx<=0: continue
            ratio=rx/move; s2=min(ratio/0.5,1)*2
            # 0 history: candles whose body touched the level's zone (+-0.5 prorated ATR), before the turn and after it formed
            half=0.5*atr_pct*lvl; cov=(bb<=lvl+half)&(bt>=lvl-half)
            hb=int(cov[max(0,p-LB):max(0,p-X30)].sum())+int(cov[j+W:].sum())
            s0=min(hb/CAP,1)*2
            med=np.median(v[max(0,p-50):p]); rv=v[p-1:p+2].max()/med if med>0 else 1
            s5=float(np.clip((rv-1)/2,0,1))
            confirm=j+W-1; s3=0; s4=0.0
            for q in range(confirm+1,min(n,confirm+int(120/dpb)+1)):
                if ((l[q]<=lvl) if side==-1 else (h[q]>=lvl)):
                    if ((c[q]>lvl) if side==-1 else (c[q]<lvl)):
                        s3=2
                        if q+3<n and q>=10:
                            net=(c[q+3]-c[q])*(-side); ar=rng_[q-10:q].mean()
                            s4=1.0 if net>=ar else (0.5 if net>=0.5*ar else 0.0)
                    break
            s6=0
            for r in out:
                if r['side']==-side and abs(r['price']-lvl)<=half and r['pv']<df.index[p]: s6=1;break
            raw=s0+s1+s2+s3+s4+s5+s6
            score=raw/11*10*mult
            out.append(dict(tf=tf,pv=df.index[p],side=side,price=round(lvl),hist=round(s0,1),move=round(s1,1),react=round(s2,1),retest=s3,momo=s4,vol=round(s5,1),flip=s6,score=round(score,1),move_pct=round(move/lvl*100,1),move_of_range=round(fr*100),react_pct=round(ratio*100),hist_bars=hb))
    return pd.DataFrame(out)
APCT=(atr(d).iloc[-1]/d.close.iloc[-1])
lvD=score_tf(d,'D',1.0,1,APCT); lvW=score_tf(rs(d,'W-MON'),'W',1.15,7,APCT,K=3,W=4)
L=pd.concat([lvD,lvW]); L.to_csv('level_scores.csv',index=False)
TOP=0.25   # a level qualifies if its raw score is in the top 25% of all levels so far
def pct_rank(vals,x): vals=np.sort(vals); return np.searchsorted(vals,x,side='right')/len(vals)*10
def zones(L,atr_now,asof,top=TOP):
    H=L[L['pv']<=asof].copy()
    H['lrs']=[round(pct_rank(H.score.values,x),1) for x in H.score]
    q=H[H.lrs>=10*(1-top)].sort_values('price').to_dict('records')
    Z=[]
    for r in q:
        w=atr_now*r['price']
        if Z and r['price']-Z[-1]['lo']<=1.0*w and r['price']-Z[-1]['hi']<=0.75*w:
            z=Z[-1]; z['m'].append(r); z['hi']=max(z['hi'],r['price'])
        else: Z.append(dict(lo=r['price'],hi=r['price'],m=[r]))
    rows=[]
    for z in Z:
        best=max(z['m'],key=lambda r:r['score']); tfs=sorted({r['tf'] for r in z['m']},key=lambda t:'MWD'.index(t))
        rows.append(dict(lo=z['lo'],hi=z['hi'],tfs='/'.join(tfs),n=len(z['m']),val=best['score']+0.5*(len(tfs)-1),level_rs=best['lrs'],best=f"{best['tf']} {best['pv'].date()} {best['price']}"))
    R=pd.DataFrame(rows)
    R['rs']=[round(pct_rank(R.val.values,x),1) for x in R.val]   # zone rs = rank among all zones on the chart
    return R.drop(columns=['val'])
A=atr(d).iloc[-1]/d.close.iloc[-1]
Zall=zones(L,A,d.index[-1])
for name,lo,hi in [('2019-20 box',6500,14500),('2021-22 box',28000,40000),('2023 box',24000,32500),('2024-25 top box',88000,100500),('ALL 45K-130K',45000,130000)]:
    Z=Zall[(Zall.hi>=lo)&(Zall.lo<=hi)]
    print(f"\n== {name}: {len(Z)} zones (top 25% levels)"); print(Z.to_string(index=False))
print(L[(L.price>83000)&(L.price<86000)&(L['pv']>='2025-11-01')&(L['pv']<'2025-12-31')].to_string(index=False))
