import pandas as pd, numpy as np
exec(open('research/vix_btc/vix_btc.py').read().split("v=v[v.d>='2015-01-01']")[0])
v=v[v.d>='2015-01-01'].reset_index(drop=True)
# baseline: every BTC day since 2015 with 180d forward
bb=b[b.index>='2015-01-01'].copy()
bb['f180']=(bb.close.shift(-180)/bb.close-1)*100
bb['ph']=[phase(d) for d in bb.index]
GOOD={'Bottom accumulation','Halving chop','Expansion','Recovery'}
bb['grp']=np.where(bb.ph.isin(GOOD),'buy phases','Stay out/Topping')
base=bb.dropna(subset=['f180'])
print('BASELINE any day: median 180d %.0f%%, up %.0f%%'%(base.f180.median(),(base.f180>0).mean()*100))
for g,x in base.groupby('grp'): print(f'  {g}: median 180d {x.f180.median():.0f}%, up {(x.f180>0).mean()*100:.0f}%')
for p,x in base.groupby('ph'): print(f'    {p}: median 180d {x.f180.median():.0f}%')
rng=np.random.default_rng(1)
rows=[]
for T in [18,20,22.5,25,27.5,30,32.5,35,37.5,40,45,50]:
    eps=episodes((v.close>T).values)
    rs=[]
    for i in eps:
        d=v.d[i]
        if d in base.index: rs.append((base.f180.loc[d], base.grp.loc[d], (b.loc[d:d+pd.Timedelta(days=180)].low.min()/b.close.loc[d]-1)*100))
    if not rs: continue
    r=pd.DataFrame(rs,columns=['f','grp','dd'])
    gb=r[r.grp=='buy phases']; gs=r[r.grp!='buy phases']
    # random benchmark: same number of random buy-phase days, 5000 draws, chance median >= observed
    pool=base[base.grp=='buy phases'].f180.values
    if len(gb):
        sims=np.median(rng.choice(pool,(5000,len(gb))),axis=1); p=(sims>=gb.f.median()).mean()
    else: p=np.nan
    rows.append(dict(T=T,n=len(r),med180=r.f.median(),up=(r.f>0).mean()*100,n_buy=len(gb),buy_med=gb.f.median(),buy_up=(gb.f>0).mean()*100 if len(gb) else np.nan,buy_dd=gb.dd.median(),p_random=p,n_bad=len(gs),bad_med=gs.f.median()))
print(pd.DataFrame(rows).round(2).to_string(index=False))
