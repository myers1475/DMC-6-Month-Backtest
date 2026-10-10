# DMC 6 Month Backtest

Session 1 — Oct 9, 2026. MNQ 4h / 1h / 5m replay, Mar 26 – Apr 6 2026. Reads are DMC unless marked as my 7 Simple Rules.

## Level types (how a level was crossed)

- **OG — ordinary gain:** gained normally, retested soon after.
- **IG — impulse gain (DMC "skipped"):** jumped on an impulse, stays untested, retested much later because of distance.
- **PG — passed-through gain:** an old level revisited later after a prior gain; crossed several times. Weaker with age and number of crossings.
- Losses: mirrored OL / IL / PL considered, not settled.
- Touches *before* a gain (failing to gain) do not make a level a pass-through. They are what made it resistance.
- OG vs IG is confirmed after the fact: whichever level the retest reaches is the OG; levels the retest never comes back to are IGs.

## Three label layers (one line can carry all three)

- **Maker (HM / LM):** what the level *caused*.
- **O / I / P:** *how* price crossed it.
- **U / Held / Lost:** what has happened at it *since*.
- Flip rule (Sep 23): a crossed level flips role and resets to untested on the new side — an OG is now support *and* a newly minted U.
- Watch the letter clash: P = "potential" in maker tags.

## Chart convention

- **Gold label** = the newest level(s) gained.

## Retest (my refinement, not DMC's)

A retest counts if price:
1. touches the level, or
2. turns inside the wick of the candle that set it (when that candle has one), or
3. stops just short of the level.

## Staircase vs range lock (correction)

- **Range lock** = wicks both sides, bodies closing inside a fixed range making **no progress**. No bias; fade edges off failures or sit out.
- **Staircase** = bodies keep gaining new levels. Not a lock. Gain → retest → continue applies; the retest of the newest gained level is the entry.
- Check before calling a lock: *did the last bodies gain anything?*
- Error logged: a sit-out was called during a staircase; the retest of the gold 1-OG held on the 5m and ran through the 4-H.

## Replay — candle by candle (1h)

1. Drop wicked under 4-UL/1-UL, closed back above → failure to lose; big candle gained the 1H zone + 1-OG.
2. Retest of the 1-OG turned inside the setting candle's wick, never touched the box → box relabeled **1H-IG**.
3. Candle wicked through 4-H, 1-H, 1-H, 4-H, 1-UL; body barely gained the first 4-H.
4. Wick tested 1-OG and the IG; body slipped back under the 4-H (barely gained, then barely lost).
5. Body gained 3 levels (4-OG/UL + two 1-OG/ULs) in one candle.
6. Wick retested the cluster; body closed above the bottom two, under the top line (flipped to 1-H); upper wick tested the 4-H again.
7. Retested two cluster lines, body gained the top line → gold **1-OG**.
8. (5m view) bodies sat on the gold 1-OG, then stair-stepped through the 4-H and wicked the 1-UL.
9. 4-H gained → gold **4-OG/UL**; expected a retest.
10. No retest — opened at the prior close and gained the 1-H → gold **1-OG**. Under DMC's base pattern ("no retest, no trade") that leg was untradeable. 4-OG/UL stays an OG pending its retest; it becomes an IG if the next retest turns at the gold 1-OG instead.

## DMC vs my 7 Simple Rules — where they split this session

| Moment | DMC read | My 7 Simple Rules read |
| --- | --- | --- |
| Body barely lost the 4-H after barely gaining it | Uncertain close; wait (later corrected: staircase, retest is the entry) | Failed to gain = bear (2.2); expectation to next level down (3.1) |
| Retest of the gold 1-OG | Entry on the retest (base pattern, L11, L12) | Long on the retest of a gained level — same trade |
| Gap in my rules | Named range lock (L6) | No stand-aside condition; candidate **4.3**: wicks through levels both sides + body closes inside = no trade until a body closes out |
