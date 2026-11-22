import pandas as pd, numpy as np
D='/home/claude/DMC-6-Month-Backtest/'
def load(f):
    d=pd.read_csv(D+f); d['t']=pd.to_datetime(d['time'],unit='s'); return d.set_index('t')[['open','high','low','close']]
daily=load('COINBASE_BTCUSD, 1D_8ee5c.csv'); h4=load('COINBASE_BTCUSD, 240_97c56.csv')
def rs(df,rule): return df.resample(rule).agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
TF={'4H':(h4,60,0.10),'D':(daily,60,0.20),'W':(rs(daily,'W-SUN'),13,0.20),'M':(rs(daily,'MS'),6,0.30)}
YEARS=[2015,2018,2022,2026]
def wt(df):
    s=(df.high+df.low+df.close)/3; esa=s.ewm(span=9,adjust=False).mean(); de=(s-esa).abs().ewm(span=9,adjust=False).mean()
    ci=(s-esa)/(0.015*de); w1=ci.ewm(span=12,adjust=False).mean(); w2=w1.rolling(3).mean(); return w1,w2
rows=[]
for tf,(df,N,thr) in TF.items():
    w1,w2=wt(df); P=(df.close.rolling(3).mean()-df.close.rolling(10).mean()); G=P.rolling(16).mean()
    s=P.diff().rolling(100,min_periods=20).std()
    up=(w1>w2)&(w1.shift()<=w2.shift())
    for kind,cond in [('dot',up&(w2<=-53)),('circle',up&(w2<0))]:
        if kind=='circle' and tf!='M': continue
        for t in np.where(cond.values)[0]:
            ts=df.index[t]
            if ts.year not in YEARS or t<30: continue
            tr=t-8+int(np.argmin(P.values[t-8:t+1])); pv=P.values; sd=s.values[t]
            ref=pv[max(0,tr-10):tr+1].max(); band=pv[tr]+0.2*(ref-pv[tr])
            bb=int((pv[max(0,tr-6):t+1]<=band).sum())
            sin=(pv[tr]-pv[tr-3])/sd; sout=(pv[t]-pv[tr])/max(1,t-tr)/sd
            fut=df.iloc[t+1:t+1+N]; c=df.close.values[t]
            if len(fut)==0: mx=dd=np.nan; win=None
            else:
                mx=fut.high.max()/c-1; dd=fut.low.min()/c-1; win=mx>=thr
            rows.append(dict(tf=tf,kind=kind,date=ts.date(),close=round(c),wt2=round(w2.values[t],1),bars_bottom=bb,slope_in=round(sin,2),slope_out=round(sout,2),since_tr=t-tr,green_up=bool(G.values[t]>G.values[t-1]),purple_above_green=bool(pv[t]>G.values[t]),max_up=round(mx*100,1) if mx==mx else None,max_dn=round(dd*100,1) if dd==dd else None,win=win))
r=pd.DataFrame(rows); r.to_csv('/home/claude/bt/dot_shape_events.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_rows',300)
print(r.to_string(index=False))
