# Reaction Levels — Strength Score (draft spec, agreed 2026-11-22)

Built inductively from Matt's 84K example (BTC daily, Nov 2025). Bodies, not wicks.
A level qualifies above a point threshold; more points = stronger (thicker/brighter line). Scores can upgrade later (retest, momentum).

| # | Element | Scoring | Known when |
|---|---|---|---|
| 0 | History | relative: how long price consolidated in that area before (e.g. $85K Mar–Apr 2025) | at the turn |
| 1 | Move into it | size of the move the turn ended (84K: ~21% drop) | at the turn |
| 2 | Reaction | relative: bounce as a share of the move into it, counted from the first opposite candle (C1), 6–7 candles | ~7 candles |
| 3 | Retest holds | wick through, body closes back on the right side (84K: Dec 1, then Dec 2 erased the drop) | later |
| 4 | Momentum | Linda histogram follows through after the retest | later |
| 5 | Volume at the turn | relative volume on the turn (capitulation/absorption) | at the turn |
| 6 | Flip history | level has acted as both support and resistance (Gained/Lost) | later |
| x | Timeframe | multiplier on the total (M > W > D > 4H …) | — |

Not included: PMO dot (redundant with the histogram).
Open: weights, threshold, strength tiers — set from more of Matt's examples (good levels and rejects).
Pending separately: retired lines now stop instead of being deleted (done); ATR rule change (1.5x / window from C1) — on hold, likely replaced by element 2.
