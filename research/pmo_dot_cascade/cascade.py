import pandas as pd, numpy as np
D='/home/claude/DMC-6-Month-Backtest/'
def load(f):
    d=pd.read_csv(D+f); d['t']=pd.to_datetime(d['time'],unit='s'); return d.set_index('t')[['open','high','low','close']]
def rs(df,rule): return df.resample(rule,label='left',closed='left').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
d1=load('COINBASE_BTCUSD, 1D_8ee5c.csv'); h4=load('COINBASE_BTCUSD, 240_97c56.csv')
w1=rs(d1,'W-MON'); m1=rs(d1,'MS')
# bar end times (when a bar's info is known)
def ends(df,delta): return df.index+delta
E={'M':None,'W':pd.Timedelta(days=7),'D':pd.Timedelta(days=1),'4H':pd.Timedelta(hours=4)}
def wt(df):
    s=(df.high+df.low+df.close)/3; esa=s.ewm(span=9,adjust=False).mean(); de=(s-esa).abs().ewm(span=9,adjust=False).mean()
    ci=(s-esa)/(0.015*de); a=ci.ewm(span=12,adjust=False).mean(); b=a.rolling(3).mean()
    up=(a>b)&(a.shift()<=b.shift()); return up&(b<=-53), up&(b<0)
def atr(df,n=14):
    tr=pd.concat([df.high-df.low,(df.high-df.close.shift()).abs(),(df.low-df.close.shift()).abs()],axis=1).max(axis=1); return tr.rolling(n).mean()
def levels(df,known_delta):
    o,c,h,l=df.open.values,df.close.values,df.high.values,df.low.values; a=atr(df).values
    bt=np.maximum(o,c); bb=np.minimum(o,c); out=[]
    for i in range(3,len(df)-2):
        if np.isnan(a[i]): continue
        # reaction high: body top highest of i-2..i+2, next 2 closes below pivot body bottom, drop >= 1 ATR, approached from below (2 of 3 up candles)
        if bt[i]>=bt[i-2:i+3].max() and c[i+1]<bb[i] and c[i+2]<bb[i] and bt[i]-c[i+2]>=a[i] and (c[i-3:i]>o[i-3:i]).sum()>=2:
            out.append((bt[i],df.index[i+2]+known_delta))
        if bb[i]<=bb[i-2:i+3].min() and c[i+1]>bt[i] and c[i+2]>bt[i] and c[i+2]-bb[i]>=a[i] and (c[i-3:i]<o[i-3:i]).sum()>=2:
            out.append((bb[i],df.index[i+2]+known_delta))
    return pd.DataFrame(out,columns=['p','known']).sort_values('known')
LV={'W':levels(w1,E['W']),'D':levels(d1,E['D'])}
def lv_at(tf,t): x=LV[tf]; return np.sort(x.p[x.known<=t].values)
def above(arr,x):
    k=arr[arr>x*1.003]; return k.min() if len(k) else None
def sim(df,i0,entry_px,stop,tgt,maxbars=3,trig_from=None):
    """buy stop at entry_px valid maxbars from bar i0+1. returns R or None"""
    n=len(df); H,L,O,C=df.high.values,df.low.values,df.open.values,df.close.values
    j=i0+1; fill=None
    while j<min(n,i0+1+maxbars):
        if H[j]>=entry_px: fill=max(entry_px,O[j]); break
        if L[j]<stop: return None
        j+=1
    if fill is None or fill<=stop: return None
    risk=fill-stop; st=stop; half=False; rh=0
    if L[j]<=st: return -1.0  # same bar stop (conservative)
    if tgt and H[j]>=tgt: half=True; rh=(tgt-fill)/risk
    if C[j]>fill: st=max(st,L[j])
    for k in range(j+1,n):
        if L[k]<=st:
            px=min(st,O[k]); r=(px-fill)/risk
            return 0.5*rh+0.5*r if half else r
        if tgt and not half and H[k]>=tgt: half=True; rh=(tgt-fill)/risk
        if C[k]>fill: st=max(st,L[k])
    r=(C[-1]-fill)/risk; return (0.5*rh+0.5*r if half else r)
# context: HTF dot active (printed within win bars of HTF, not invalidated by HTF close below dot-candle low)
def ctx_series(htf,htf_delta,sig,win):
    act=[]
    idx=np.where(sig.values)[0]
    for i in idx:
        lo=htf.low.values[i]; start=htf.index[i]+htf_delta; end=htf.index[min(i+win,len(htf)-1)]+htf_delta
        dead=np.where(htf.close.values[i+1:i+win+1]<lo)[0]
        if len(dead): end=min(end,htf.index[i+1+dead[0]]+htf_delta)
        act.append((start,end))
    return act
def in_ctx(t,act): return any(s<=t<e for s,e in act)
def run_A(tf,df,lvtf,sig,act,waitbars):
    delta=E[tf]; rows=[]; H,L,C=df.high.values,df.low.values,df.close.values
    for d in np.where(sig.values)[0]:
        t=df.index[d]+delta
        if act is not None and not in_ctx(t,act): continue
        lv=lv_at(lvtf,t)
        inside=lv[(lv>=L[d])&(lv<C[d])]
        if len(inside): level=inside.max(); b=d
        else:
            level=above(lv,C[d])
            if level is None: continue
            b=None
            for k in range(d+1,min(len(df),d+1+waitbars)):
                if C[k]<L[d]: break
                if C[k]>level: b=k;break
            if b is None: continue
        tb=df.index[b]+delta; lvb=lv_at(lvtf,tb); tgt=above(lvb,max(level,H[b]))
        r1=sim(df,b,H[b],L[b],tgt)
        if r1 is not None: rows.append(dict(tf=tf,dot=df.index[d].date(),entry='E1 break',level=round(level),R=round(r1,2)))
        # retest
        r=None
        for k in range(b+1,min(len(df),b+1+waitbars)):
            if C[k]<L[d]: break
            if L[k]<=level: r=k;break
        if r is None: continue
        c=None
        for k in range(r,min(len(df),r+waitbars)):
            if C[k]<L[d]: break
            if C[k]>level and (k>r or C[k]>level): c=k;break
        if c is None: continue
        st=L[r:c+1].min(); tgt2=above(lv_at(lvtf,df.index[c]+delta),max(level,H[c]))
        r2=sim(df,c,H[c],st,tgt2)
        if r2 is not None: rows.append(dict(tf=tf,dot=df.index[d].date(),entry='E2 retest',level=round(level),R=round(r2,2)))
    return rows
dW,cW=wt(w1); dD,cD=wt(d1); dH,cH=wt(h4); dM,cM=wt(m1)
actM=ctx_series(m1,pd.offsets.MonthBegin(1),cM,6)
actW=ctx_series(w1,E['W'],dW,13); actD=ctx_series(d1,E['D'],dD,13)
A=[]
A+=run_A('W',w1,'W',dW,actM,12)
A+=[dict(r,tf='W-noctx') for r in run_A('W',w1,'W',dW,None,12)]
A+=run_A('D',d1,'D',dD,actW,20)
A+=[dict(r,tf='D-noctx') for r in run_A('D',d1,'D',dD,None,20)]
A+=run_A('4H',h4,'D',dH,actD,30)
A+=[dict(r,tf='4H-noctx') for r in run_A('4H',h4,'D',dH,None,30)]
A=pd.DataFrame(A)
# ---- B: weekly bracket range, 4H dots
B=[]; rng=[]
Wl,Wc=w1.low.values,w1.close.values
for i in np.where(dW.values)[0]:
    t=w1.index[i]+E['W']; lv=lv_at('W',t); L1=above(lv,Wc[i])
    if L1 is None: continue
    for k in range(i+1,min(len(w1),i+27)):
        if Wc[k]<Wl[i]: break
        if Wc[k]>L1:
            top=above(lv_at('W',w1.index[k]+E['W']),max(L1,w1.high.values[k]))
            if top is None: break
            s=w1.index[k]+E['W']; e=None
            for m in range(k+1,len(w1)):
                if w1.high.values[m]>=top or Wc[m]<Wl[i]: e=w1.index[m]+E['W']; hit=w1.high.values[m]>=top; break
            if e is None: e=w1.index[-1]+E['W']; hit=None
            rng.append(dict(dot=w1.index[i].date(),dot_low=round(Wl[i]),zone_top=round(L1),range_top=round(top),start=s.date(),end=e.date(),reached_top=hit)); break
for kind,sig in [('4H dot',dH),('4H circle',cH)]:
    H,Lw=h4.high.values,h4.low.values
    for d in np.where(sig.values)[0]:
        t=h4.index[d]+E['4H']
        for R_ in rng:
            if pd.Timestamp(R_['start'])<=t<pd.Timestamp(R_['end']):
                if h4.close.values[d]>=R_['range_top']: break
                st=Lw[max(0,d-4):d+1].min()
                r=sim(h4,d,H[d],st,R_['range_top'])
                if r is not None: B.append(dict(kind=kind,wk_dot=R_['dot'],date=h4.index[d],R=round(r,2)))
                break
B=pd.DataFrame(B); rng=pd.DataFrame(rng)
A.to_csv('/home/claude/bt/cascade_A.csv',index=False); B.to_csv('/home/claude/bt/bracket_B.csv',index=False); rng.to_csv('/home/claude/bt/bracket_ranges.csv',index=False)
def rep(x,name):
    if len(x)==0: print(f"{name:28s} n=0"); return
    w=x[x.R>0]; l=x[x.R<=0]; rr=w.R.mean()/abs(l.R.mean()) if len(w) and len(l) else float('nan')
    print(f"{name:28s} n={len(x):3d} WR={len(w)/len(x)*100:4.0f}% avgW={w.R.mean() if len(w) else 0:5.2f} avgL={l.R.mean() if len(l) else 0:5.2f} RR={rr:4.2f} exp={x.R.mean():5.2f} NET={x.R.sum():6.2f}R $250={x.R.sum()*250:7.0f} $500={x.R.sum()*500:7.0f}")
print("== A cascade (all years)")
for tf in ['W','W-noctx','D','D-noctx','4H','4H-noctx']:
    x=A[A.tf==tf] if len(A) else A
    rep(x,tf)
    for e in ['E1 break','E2 retest']: rep(x[x.entry==e] if len(x) else x,'   '+e)
print("\n== B ranges"); print(rng.to_string(index=False))
print("\n== B 4H trades inside weekly bracket")
for k in ['4H dot','4H circle']: rep(B[B.kind==k],k)
print(A[A.tf=='W'].to_string(index=False))
