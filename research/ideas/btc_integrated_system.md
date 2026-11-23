# Parked idea: integrated BTC system (2026-11-23)

Matt's idea (not ready to build yet): combine for BTC trading
- RSL zones (where) - research/level_score, pine/relative_strength_levels.pine
- HTF PMO circles/dots (when) - circles_dots_and_lights_live.pine
- Lights / cloud state per TF (trend state)
- Cycle seasonality (which part of the 4-year cycle / time of year)

Evidence so far: research/pmo_dot_shape (first dots fail, later dots work), research/pmo_dot_cascade
(weekly bracket + 4H circles), chart notes: "bottom greens good", "tons of overhead levels = bad", "Q4 of bottom year = bad".
Next step when ready: walk real BTC setups one at a time, extract combination rules.

## Draft spec (agreed 2026-11-23)
- ONE light for BTC spot/swing, built from Weekly (direction) + Daily (timing); season adjusts trust (bad window downgrades green -> yellow).
- Green = scale in: W trend not red + W dot/circle up; D dot/circle up; price broke & held a strong RSL zone with room above; not a bad season window.
- Yellow = resistance: under/inside a strong RSL zone overhead, or mixed signals, or bad season window. Hold, don't add.
- Red = stop adding (hold): W trend red or W red circle; D red; lost a support zone.
- Exit (separate, stricter): W red dot AND weekly close below a strong zone.
- Not for MNQ intraday (that stays Levels & Linda).
Open: define the "bad season" windows. Plan: test on BTC history first (without season, then with), before any Pine.

## Season reads the dots (agreed 2026-11-23)
Season is not a 5th signal; it tells the light how to read each dot.
- Monthly red dot 1-10 months after a halving = pause (stay in, or step aside and re-enter on the next monthly green circle).
- Monthly red dot 11+ months after a halving = top window -> scale-out ladder: daily red dot (first piece) -> weekly red dot -> monthly red dot (rest).
  BTC: 4/4 tops (Jan 2018, Apr 2021, Dec 2021, Sep 2025) in 11-19 mo; 3/3 early ones (Sep 2016, May 2024, Feb 2025) at 1-10 mo, each followed by a monthly green circle at a higher price within 1-6 mo.
  Order in time is bottom-up: daily red dots, then weekly, monthly confirms last. Cutoff is thin (Feb 2025 at 10 mo) - treat as soft zone ~10-20 mo.
- Green dots in Q4 of a bottoming year failed; bottom-window greens worked.
