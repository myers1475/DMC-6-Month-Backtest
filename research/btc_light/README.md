# BTC traffic light test, step 1 (no season) - 2026-11-23
BTC Coinbase daily Jul 2015 - Nov 2026. Light from closed candles, applied next day.
RSL zones without lookahead: only move/reaction/volume/flip (known at confirmation); top 25% = strong.
v1: daily cross down = RED -> red 81% of days (too twitchy).
v2: daily cross down = YELLOW; RED needs weekly trend red, weekly cross down, or a lost strong zone.
v2 90d median fwd return: GREEN +25.2% (72% up), YELLOW +20.4% (68%), RED +4.6% (53%), EXIT +1.7% (57%), all days +10.8% (59%).
Strategy A (in on green/yellow, out on red): x147 vs buy&hold x228; max DD -42% vs -84%; 37% time in market.
Strategy B (in on green, out on EXIT): x80, DD -86% -> exit rule not working.
Green failed in bear years (2018, 2022, 2026 ~ -20% 90d) -> season layer next.
