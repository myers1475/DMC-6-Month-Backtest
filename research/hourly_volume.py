import pandas as pd
def sess(h): return 'Asia' if (h>=18 or h<3) else 'London' if h<9 else 'NY'
for name,f in [('NQ',"CME_MINI_NQ1!, 15_22fcb.csv"),('MGC',"COMEX_MINI_MGC1!, 15_6c3bd.csv")]:
    d=pd.read_csv(f)[['time','high','low','close','Volume']]
    d['ts']=pd.to_datetime(d.time,unit='s',utc=True).dt.tz_convert('America/New_York')
    d=d[d.ts>=d.ts.max()-pd.Timedelta(days=365)].set_index('ts')
    for off in ('0min','30min'):
        h=d.resample('60min',offset=off).agg({'high':'max','low':'min','Volume':'sum','close':'last'}).dropna()
        h=h[(h.index.dayofweek<5)&(h.Volume>0)]
        h['day']=(h.index+pd.Timedelta(hours=6)).date
        h['share']=h.Volume/h.groupby('day').Volume.transform('sum')*100
        h['rng']=h.high-h.low
        g=h.groupby(h.index.strftime('%H:%M')).agg(vol=('Volume','median'),share=('share','median'),rng=('rng','median'),n=('rng','size'))
        g=g[g.n>100]
        print(f"\n=== {name} offset {off} {d.index.min().date()}..{d.index.max().date()} ===")
        for s in ('Asia','London','NY'):
            x=g[[sess(int(i[:2]))==s for i in g.index]].sort_values('vol',ascending=False)
            print(s,' | '.join(f"{i} {r.vol:,.0f} ({r.share:.1f}%) {r.rng:.0f}pt" for i,r in x.iterrows()))
