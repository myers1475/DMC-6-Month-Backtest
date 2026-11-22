# PMO dot cascade + weekly bracket range (BTC Coinbase, all years) — 2026-11-22

Levels: Python approximation of Reaction Levels (body pivot, 2 closes away, >= 1 ATR, approached from the other side), weekly and daily.
Entries: buy stop above the HIGH of the trigger candle (valid 3 bars). Exit: half at next level up; trail rest behind prior candle low.
v1 = trail from entry. v2 = trail only after the half is taken at the level (the "trail in profit" reading) — v2 is the better one.

A. Cascade (dot under level -> wait for close above -> E1 break; retest -> E2). Context = HTF dot within 13 HTF bars, not invalidated.
  - W with monthly-circle context: 0 trades. D with weekly context: 4. 4H with daily context: 16 (v2 NET -10.5R).
  - Finding: after an HTF dot, the LTF rarely prints dots (wt2 <= -53) — it prints circles. Cascade needs LTF circles.
B. Weekly bracket: weekly dot -> zone (dot-candle low .. first weekly level broken) -> range top = next weekly level. Dead on weekly close < dot low.
  - 3 ranges: Dec 2018 dot (Apr-May 2019), Dec 2019 dot (Jan-Feb 2020), Mar 2026 dot (Mar-Apr 2026). All 3 reached the range top.
  - v2, 4H circles inside range: 20 trades, 50% WR, RR 8.8, exp +3.61R, NET +72.2R. 4H dots: 5 trades, NET +8.4R.
  - Caveat: 3 ranges only; trades overlap (stacked adds).
