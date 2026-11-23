# CCI correction filter test (NQ, Nov 23 2026)

Claim tested (from a post): only take a long NASDAQ breakout if Lowest(CCI(27), 18 daily bars) < -100.
Base model: buy stop at prior session low + 0.8 x ATR(40) (daily), exit at session close. No stop.

Data: CME_MINI_NQ1! 60m, Jan 2020 - Aug 2026 (~6.5 years). Daily bars built from 60m.
Metrics: WR = share of trades closing positive. 1R = average losing trade (no stop in the model).
exp = expectancy per trade in R. NET R = total points / 1R. P/DD = net points / max drawdown points.

Headline (longs):
- Globex day, prior low anchor: base NET R +28.4; CCI-kept +4.3; CCI-excluded +27.9  -> filter HURT
- RTH day, prior low anchor:    base NET R -5.8;  CCI-kept +4.3; CCI-excluded -12.6 -> filter helped, tiny (~0.03R/trade)
- Neighborhood (RTH): lookback 18-26 kept > excluded in 6/6 cells; lookback 10 reverses in 2/3.
- Their base P/DD 7.53 not reproduced (ours -0.2 to 2.1) -> our reading of their base rule likely differs.

Files: cci_test.py (base + shorts mirror, by year), cci_variants.py (session/anchor/neighborhood), *_output.txt, trades_60m.csv

## 9:30 box breakout + CCI filter (MNQ 5m, May 4 - Nov 23 2026)
Rules: box = 9:30 5m candle H/L; entry = first 5m close outside box (and reversal = first close outside opposite side), window to 12:00 ET.
Target 50 pts, stop 100 pts (1R = 100 pts). If neither hit by 12:00, exit at the 11:55 bar close (assumption). Stop checked first when one bar hits both.
CCI from daily Globex bars (NQ 15m history + MNQ 5m). Long filter: Lowest(CCI27,18) < -100. Short = mirror (Highest > +100), not part of the original claim.
First breakout longs: all 81 / -5.69R; filter ON 38 / -2.53R (-0.067R/trade); OUT 43 / -3.17R (-0.074R/trade) -> no difference.
First breakout shorts: all 65 / +8.80R; mirror ON 42 / +0.55R; OUT 23 / +8.25R (91% WR) -> mirror filter hurt.
Reversal longs: ON 8 / +1.45R vs OUT 17 / +1.29R -> too few trades. Output: box930_output.txt, trades: box930_trades.csv
