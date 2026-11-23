import pandas as pd, numpy as np
src=open('level_score.py').read(); g={}; exec(src[:src.index("APCT=")],g)
d=g['d']; rs=g['rs']; atr=g['atr']
w=rs(d,'W-MON'); A=atr(d).iloc[-1]/d.close.iloc[-1]
L=pd.concat([g['score_tf'](d,'D',1.0,1,A),g['score_tf'](w,'W',1.15,7,A,K=3,W=4)])
# no-lookahead strength: only what is known when the level confirms (move, reaction, volume, flip)
L['s_now']=(L.move+L.react+L.vol+L.flip)*np.where(L.tf=='W',1.15,1.0)
L['known']=L['pv']+pd.to_timedelta(np.where(L.tf=='W',35,9),unit='D')
L=L.sort_values('known').reset_index(drop=True)
def wt(df):
    s=(df.high+df.low+df.close)/3; esa=s.ewm(span=9,adjust=False).mean(); de=(s-esa).abs().ewm(span=9,adjust=False).mean()
    ci=(s-esa)/(0.015*de); a=ci.ewm(span=12,adjust=False).mean(); b=a.rolling(3).mean(); return a,b
def lastcross(df):
    a,b=wt(df); up=(a>b)&(a.shift()<=b.shift()); dn=(a<b)&(a.shift()>=b.shift())
    ev=pd.Series(np.nan,index=df.index); ev[up]=np.where(b[up]<=-53,2,1); ev[dn]=np.where(b[dn]>=53,-2,-1); return ev.ffill()
def cloud(df):
    e=[df.close.ewm(span=n,adjust=False).mean() for n in (9,20,50)]; top=pd.concat(e,axis=1).max(axis=1); bot=pd.concat(e,axis=1).min(axis=1)
    lg=bot>bot.shift(); sh=top<top.shift(); return pd.Series(np.where(lg&sh,2,np.where(lg,1,np.where(sh,-1,0))),index=df.index)
# weekly values known at week close -> apply from next week (shift 1, forward-fill to days)
wev=lastcross(w).shift(1); wcl=cloud(w).shift(1); wclose=w.close.shift(1)
wev_d=wev.reindex(d.index,method='ffill'); wcl_d=wcl.reindex(d.index,method='ffill')
dev=lastcross(d); datr=atr(d)
light=[]; scores=[]
lv_known=[]; ptr=0; prev_close=None
for i,(t,row) in enumerate(d.iterrows()):
    while ptr<len(L) and L.known.iloc[ptr]<=t: lv_known.append((L.price.iloc[ptr],L.s_now.iloc[ptr])); ptr+=1
    if len(lv_known)<20 or i<60: light.append(np.nan); continue
    sc=np.array([s for _,s in lv_known]); th=np.quantile(sc,0.75)
    strong=np.array([p for p,s in lv_known if s>=th])
    c=row.close; a=datr.iloc[i]
    above=strong[strong>c]; room=(above.min()-c) if len(above) else np.inf
    c3=d.close.iloc[i-3]
    lost=any((c3>=p>c) for p in strong)          # closed below a strong level in the last 3 days
    wk=t.to_period('W-SUN')
    wtrend=wcl_d.iloc[i]; wsig=wev_d.iloc[i]; dsig=dev.iloc[i]
    # exit: weekly red dot + last weekly close below a strong level it was above the week before
    wi=w.index.searchsorted(t)-1
    wexit=False
    if wi>=2 and wsig==-2:
        wc,wc_prev=w.close.iloc[wi],w.close.iloc[wi-1]
        wexit=any((wc_prev>=p>wc) for p in strong)
    if wexit: s='EXIT'
    elif wtrend==-1 or wsig<0 or lost: s='RED'
    elif wtrend!=-1 and wsig>0 and dsig>0 and room>=1.5*a: s='GREEN'
    else: s='YELLOW'
    light.append(s)
d['light']=light
for h in (30,90):
    d[f'f{h}']=d.close.shift(-h)/d.close-1
x=d.dropna(subset=['light'])
print("BTC Coinbase daily, light computed from closed candles; returns = next 30 / 90 calendar days\n")
print(f"{'light':7s} {'days':>5s} {'%time':>6s} {'med 30d':>8s} {'%up 30d':>8s} {'med 90d':>8s} {'%up 90d':>8s}")
for s in ['GREEN','YELLOW','RED','EXIT']:
    y=x[x.light==s]
    if len(y)==0: continue
    print(f"{s:7s} {len(y):5d} {len(y)/len(x)*100:5.0f}% {y.f30.median()*100:7.1f}% {(y.f30>0).mean()*100:7.0f}% {y.f90.median()*100:7.1f}% {(y.f90>0).mean()*100:7.0f}%")
print(f"{'ALL':7s} {len(x):5d}  100% {x.f30.median()*100:7.1f}% {(x.f30>0).mean()*100:7.0f}% {x.f90.median()*100:7.1f}% {(x.f90>0).mean()*100:7.0f}%")
# by year
x2=x.copy(); x2['yr']=x2.index.year
print("\nmedian 90d return by light and year:")
print((x2.pivot_table(index='yr',columns='light',values='f90',aggfunc='median')*100).round(0).to_string())
# equity: hold while light in GREEN/YELLOW, out on RED/EXIT (decided at close, applied next day)
r=d.close.pct_change().shift(-1)
def eq(mask):
    rr=(r*mask.astype(float)).fillna(0); e=(1+rr).cumprod(); dd=(e/e.cummax()-1).min(); return e.iloc[-2],dd
xa=d.loc[x.index]
bh=(xa.close.iloc[-1]/xa.close.iloc[0]); bhdd=(xa.close/xa.close.cummax()-1).min()
e1,dd1=eq(xa.light.isin(['GREEN','YELLOW'])); 
# B: enter on GREEN, hold through yellow/red, out only on EXIT
inpos=False; m=[]
for s in xa.light:
    if s=='GREEN': inpos=True
    if s=='EXIT': inpos=False
    m.append(inpos)
e2,dd2=eq(pd.Series(m,index=xa.index))
print(f"\nGrowth of $1 {xa.index[0].date()} -> {xa.index[-1].date()}:")
print(f"  Buy & hold:                        x{bh:,.0f}   max drawdown {bhdd*100:.0f}%")
print(f"  A) in on green/yellow, out on red: x{e1:,.0f}   max drawdown {dd1*100:.0f}%   time in market {xa.light.isin(['GREEN','YELLOW']).mean()*100:.0f}%")
print(f"  B) in on green, out only on EXIT:  x{e2:,.0f}   max drawdown {dd2*100:.0f}%   time in market {np.mean(m)*100:.0f}%")
d[['close','light','f30','f90']].to_csv('light_history_v2.csv')
print("\nlast 10 days:"); print(d[['close','light']].tail(10).to_string())
