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
