# BTC traffic light test, step 1 (no season) - 2026-11-23
BTC Coinbase daily Jul 2015 - Nov 2026. Light from closed candles, applied next day.
RSL zones without lookahead: only move/reaction/volume/flip (known at confirmation); top 25% = strong.
v1: daily cross down = RED -> red 81% of days (too twitchy).
v2: daily cross down = YELLOW; RED needs weekly trend red, weekly cross down, or a lost strong zone.
v2 90d median fwd return: GREEN +25.2% (72% up), YELLOW +20.4% (68%), RED +4.6% (53%), EXIT +1.7% (57%), all days +10.8% (59%).
Strategy A (in on green/yellow, out on red): x147 vs buy&hold x228; max DD -42% vs -84%; 37% time in market.
Strategy B (in on green, out on EXIT): x80, DD -86% -> exit rule not working.
Green failed in bear years (2018, 2022, 2026 ~ -20% 90d) -> season layer next.

## Step 2: season (v3/v4) - 2026-11-23
Season from halving dates (2012-11-28, 2016-07-09, 2020-05-11, 2024-04-19): EARLY <11 mo, TOP 11-20 mo, BEAR to end Q3 of halving year+2,
FLUSH = Q4 of halving year+2 (greens -> yellow), BOTTOM = Jan halving year+3 to next halving. Greens downgraded to yellow in BEAR/FLUSH.
Green days 90d median +27.9% (76% up) after season (was +25.2%, 72%).
Strategy C (v4): full in on GREEN; in TOP window sell 1/3 daily red dot, 1/3 weekly red dot, rest monthly red dot; no re-buy until BOTTOM.
v4: x1,171 vs buy&hold x228; max DD -62% (2019-06 -> 2020-03 Covid, fully in) vs -84%; avg exposure 60%. Out since 2025-10-01 @ 118,660.
Sells: 2017 2,656 / 2,597 / 9,014; 2021 61,427 / 57,859; 2025 94,667 / 115,052 / 118,660.
v3 (10-month cutoff, re-buys allowed): x1,275 but churns (re-buys near tops) and held 2/3 into the 2026 bear.
Caveat: in-sample, 3 cycles, windows picked from this data; no fees/taxes.
