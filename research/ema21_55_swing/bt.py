"""4H EMA 21/55 swing system backtest.

Definitions chosen (Matt asked Claude to pick):
- Trend: EMA21 > EMA55 on the signal bar.
- Pullback: the swing high = highest high of the last 10 bars before the signal bar.
  Pullback bars = bars after that high up to the signal bar. Some bar in the pullback
  (or the signal bar) must have low <= EMA21 ("touched EMA21 or deeper"), and no
  pullback bar may CLOSE below EMA55.
- Volume: mean volume of pullback bars < mean volume of the 10 bars ending at the swing high.
- RSI(14) > 50 on the signal bar close.
- Strong close: bullish candle, close > EMA21, close in the top third of the bar's range.
- Entry: next bar's open. One position at a time.
- Initial stop (sizing, = 1R): lowest low of the pullback (the most recent higher low).
- Main stop: a 4H close below EMA55 -> exit next open.
- Stop ratchets up to each new confirmed 3-bar fractal low above it.
- Targets: 1/3 off at +5.5%, 1/3 off at +9%, last 1/3 trails: exit next open after a 4H close below EMA21.
- Same bar touches stop and target: stop assumed first (pessimistic).
- Fees: 0.1% per side.
"""
import sys, pandas as pd, numpy as np

FEE = 0.001

def rsi(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100/(1+up/dn)

def run(path, name, start=None):
    d = pd.read_csv(path)
    d['t'] = pd.to_datetime(d.time, unit='s')
    d = d[['t','open','high','low','close','Volume']].rename(columns={'Volume':'vol'}).reset_index(drop=True)
    d['e21'] = d.close.ewm(span=21, adjust=False).mean()
    d['e55'] = d.close.ewm(span=55, adjust=False).mean()
    d['rsi'] = rsi(d.close)
    o,h,l,c,v,e21,e55,r = (d[k].values for k in ['open','high','low','close','vol','e21','e55','rsi'])
    n = len(d); trades = []; i = 70
    while i < n-2:
        if start is not None and d.t[i] < pd.Timestamp(start): i += 1; continue
        ok = e21[i] > e55[i] and r[i] > 50 and c[i] > o[i] and c[i] > e21[i] and (h[i]-l[i]) > 0 and (c[i]-l[i]) >= (2/3)*(h[i]-l[i])
        if ok:
            hi_idx = i-10 + int(np.argmax(h[i-10:i]))
            pb = range(hi_idx+1, i+1)
            if len(pb) >= 2:
                touched = any(l[j] <= e21[j] for j in pb)
                no55 = all(c[j] >= e55[j] for j in range(hi_idx+1, i))
                pbv = v[hi_idx+1:i]
                legv = v[max(0,hi_idx-9):hi_idx+1]
                volok = len(pbv) > 0 and pbv.mean() < legv.mean()
                if touched and no55 and volok:
                    entry = o[i+1]; stop = min(l[j] for j in pb)
                    risk = entry - stop
                    if risk / entry >= 0.005:
                        t1, t2 = entry*1.055, entry*1.09
                        rem = 1.0; pnl = 0.0; k = i+1; got1 = got2 = False; exit_reason = None
                        while k < n and rem > 0:
                            # stop first (pessimistic)
                            if l[k] <= stop:
                                px = min(o[k], stop); pnl += rem*(px-entry); rem = 0; exit_reason='stop'; break
                            if not got1 and h[k] >= t1:
                                pnl += (1/3)*(t1-entry); rem -= 1/3; got1 = True
                            if not got2 and h[k] >= t2:
                                pnl += (1/3)*(t2-entry); rem -= 1/3; got2 = True
                            if k+1 < n:
                                if c[k] < e55[k]:
                                    pnl += rem*(o[k+1]-entry); rem = 0; exit_reason='close<55'; break
                                if got2 and c[k] < e21[k]:
                                    pnl += rem*(o[k+1]-entry); rem = 0; exit_reason='trail21'; break
                            # ratchet to new confirmed fractal low (bar k-1)
                            if k-2 > i and l[k-1] < l[k-2] and l[k-1] < l[k] and l[k-1] > stop:
                                stop = l[k-1]
                            k += 1
                        if rem > 0: pnl += rem*(c[n-1]-entry); exit_reason='open'
                        fees = FEE*entry*2
                        R = (pnl - fees)/risk
                        trades.append(dict(entry_t=d.t[i+1], entry=entry, stop_pct=risk/entry*100, R=R, ret_pct=(pnl-fees)/entry*100, exit=exit_reason, bars=k-i, tp1=got1, tp2=got2))
                        i = k+1; continue
        i += 1
    return pd.DataFrame(trades)

def report(df, label):
    w = df[df.R > 0]; ls = df[df.R <= 0]
    wr = len(w)/len(df)*100
    rr = w.R.mean()/abs(ls.R.mean()) if len(ls) else float('nan')
    exp = df.R.mean(); net = df.R.sum()
    print(f"{label}: trades {len(df)} | win rate {wr:.0f}% | avg win {w.R.mean():+.2f}R avg loss {ls.R.mean():+.2f}R | realized RR {rr:.2f} | expectancy {exp:+.2f}R | NET R {net:+.1f} | $250/R {net*250:+,.0f} | $500/R {net*500:+,.0f} | TP1 hit {df.tp1.mean()*100:.0f}% TP2 {df.tp2.mean()*100:.0f}% | median stop {df.stop_pct.median():.1f}%")

if __name__ == '__main__':
    sets = [('BTC','COINBASE_BTCUSD, 240_1dd1d.csv'),('ETH','COINBASE_ETHUSD, 240_185a7.csv'),('SOL','COINBASE_SOLUSD, 240_89c1a.csv')]
    allt = []
    for nm, p in sets:
        df = run(p, nm); df['asset'] = nm; allt.append(df)
        report(df, f"{nm} full")
        report(df[df.entry_t >= '2022-01-01'], f"{nm} 2022+")
        df.to_csv(f'research/ema21_55_swing/trades_{nm}.csv', index=False)
    a = pd.concat(allt)
    report(a, 'ALL full'); report(a[a.entry_t >= '2022-01-01'], 'ALL 2022+')
    for y, g in a.groupby(a.entry_t.dt.year): report(g, f'  {y}')
    print(a.exit.value_counts())
