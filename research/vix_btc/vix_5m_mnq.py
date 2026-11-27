import pandas as pd, numpy as np
def load(f):
    d=pd.read_csv(f); d['t']=pd.to_datetime(d.time,unit='s').dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)
    return d.set_index('t')[['open','high','low','close']]
M=load('CME_MINI_MNQ1!, 5_e2017.csv'); V=load('TVC_VIX, 5_b9fe2.csv')
j=M.join(V,rsuffix='_v',how='inner')
j=j[(j.index.time>=pd.Timestamp('09:30').time())&(j.index.time<pd.Timestamp('16:00').time())].copy()
j['day']=j.index.normalize()
print('aligned RTH 5m bars',len(j),'days',j.day.nunique(),j.index[0],j.index[-1])
# --- forward MNQ points (from bar close) within same day
for k in (6,12):  # 30m, 60m
    j[f'f{k}']=j.groupby('day').close.shift(-k)-j.close
j['ema']=j.groupby('day').close_v.transform(lambda s:s.ewm(span=20,adjust=False).mean())
# TEST 1: direction filter
print('\n== TEST 1: VIX vs its 20-EMA (5m, RTH) -> MNQ next 30/60 min, points')
j['vixdown']=j.close_v<j.ema
for lab,g in j.dropna(subset=['f12']).groupby('vixdown'):
    print(f"  VIX {'below' if lab else 'above'} EMA: n={len(g)} | next 30m mean {g.f6.mean():+.1f} pts (up {(g.f6>0).mean()*100:.0f}%) | next 60m mean {g.f12.mean():+.1f} pts (up {(g.f12>0).mean()*100:.0f}%)")
c=j[['close','close_v']].pct_change().corr().iloc[0,1]
print(f'  same-bar 5m corr {c:+.2f}')
# TEST 2: divergence at new session extremes
print('\n== TEST 2: MNQ new session LOW (after 10:00), VIX confirms vs diverges -> MNQ next 60 min, points')
rows=[]
for day,g in j.groupby('day'):
    g=g.copy()
    g['prevLow']=g.low.cummin().shift(); g['prevHigh']=g.high.cummax().shift()
    g['vHi']=g.high_v.cummax().shift(); g['vLo']=g.low_v.cummin().shift()
    last=None
    for t,r in g.iterrows():
        if t.time()<pd.Timestamp('10:00').time() or t.time()>pd.Timestamp('15:00').time() or pd.isna(r.prevLow): continue
        idx=g.index.get_loc(t); fut=g.iloc[idx+1:idx+13]
        if len(fut)<12: continue
        if r.low<r.prevLow:
            div=r.high_v<r.vHi
            rows.append(dict(side='low',div=div,t=t,f60=fut.close.iloc[-1]-r.close,mfe=fut.high.max()-r.close,mae=r.close-fut.low.min()))
        if r.high>r.prevHigh:
            div=r.low_v>r.vLo
            rows.append(dict(side='high',div=div,t=t,f60=r.close-fut.close.iloc[-1],mfe=r.close-fut.low.min(),mae=fut.high.max()-r.close))
D=pd.DataFrame(rows)
# keep first signal per day per side per type to avoid clustering
D['day']=D.t.dt.normalize()
for side in ['low','high']:
    for dv in [True,False]:
        g=D[(D.side==side)&(D['div']==dv)].groupby('day').head(1)
        what='LONG fade' if side=='low' else 'SHORT fade'
        print(f"  new {side} {'VIX DIVERGES' if dv else 'VIX confirms'} -> {what}: n={len(g)} | 60m mean {g.f60.mean():+.1f} pts, win {(g.f60>0).mean()*100:.0f}% | median MFE {g.mfe.median():.0f} pts, median MAE {g.mae.median():.0f} pts")
D.to_csv('research/vix_btc/divergence_signals.csv',index=False)
# TEST 3: VIX level vs day range
print('\n== TEST 3: VIX at 9:35 vs MNQ RTH range that day (points)')
day=j.groupby('day').agg(hi=('high','max'),lo=('low','min'),vix=('open_v','first'),px=('open','first'))
day['rng']=day.hi-day.lo; day['implied']=day.px*day.vix/100/np.sqrt(252)
print(f'  corr VIX vs range {day.vix.corr(day.rng):+.2f} | n days {len(day)}')
day['b']=pd.cut(day.vix,[0,15,18,21,25,30,99],labels=['<15','15-18','18-21','21-25','25-30','30+'])
print(day.groupby('b',observed=True).agg(days=('rng','size'),median_range=('rng','median'),implied_1sd=('implied','median')).round(0).to_string())
print(f"  actual RTH range / VIX-implied 1-day move: median {(day.rng/day.implied).median():.2f}")
