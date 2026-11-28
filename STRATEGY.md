<!-- Maintained by roan-maverick. -->

# The Order Flow Strategy, step by step

This is the complete trading process the indicator automates. It is an intraday, auction-market approach: read the environment before the open, wait for price to reach the right location, and only act when order flow confirms that one side is trapped.

> The market is an auction. When buyers and sellers agree, value builds inside a range and nobody is forced to act. The edge appears when one side gets aggressive, fails, and is left trapped on the wrong side. Their forced exits power the move. Entries are only the last 5 to 10% of the work.

---

## The four steps

| Step | Question | Done |
|---|---|---|
| 1. Environment | What kind of day am I walking into? | Before the open |
| 2. Location | Where is the right place to do business? | Before the open |
| 3. Confirmation | Is one side failing and getting trapped right now? | Live |
| 4. Management | Is my trade getting the result it should? | Live |

---

## Step 1. Environment

Done before the market opens, never while price is moving fast. Build the scenarios first, then wait.

### A. Higher-timeframe value structure (1h and 4h)

| Structure | What it looks like | What to do |
|---|---|---|
| **Value up** | Higher highs and higher lows, value building higher day after day | Only look for longs, in discount |
| **Value down** | Lower highs and lower lows, value building lower | Only look for shorts, in premium |
| **Balance** | No clear direction | Stand aside. There is no edge in the middle |

Never try to call the top or the bottom. Trade with the structure.

### B. Gamma regime (GEX)

Options dealers hedge their exposure in the underlying market, and their hedging changes how price moves.

| Regime | Dealer behavior | What to expect |
|---|---|---|
| **Positive gamma** | Sell rallies, buy dips | Volatility is dampened. Breakouts tend to fail. Chop is likely |
| **Negative gamma** | Buy rallies, sell dips | Volatility is amplified. Bigger, faster moves |

Green does not mean long and red does not mean short. Gamma tells you about volatility, not direction. Also mark the **call wall**, the **put wall** and the **gamma flip** (where the regime changes). They are context and possible targets, not bounce levels.

Example: *value up + negative gamma* means expect fast, extended moves today.

TradingView has no options data, so the indicator lets you type the regime and levels in from any GEX source (for Nasdaq futures, naive GEX built from QQQ and NDX options).

---

## Step 2. Location

### A. Discount and premium

Use the volume profile. The **value area** is where about 70% of the volume traded, the **point of control (POC)** is the price with the most volume.

- Below the value area low (VAL) is **discount**.
- Above the value area high (VAH) is **premium**.

In a value-up market you only buy in discount. Buying in premium is paying an expensive price; selling in discount is selling at the best place to buy. The value area used is the value the market has built most recently (for example during the Asia and London sessions before the New York open), or the last completed session.

### B. The exact zone: Fibonacci 0.705 / 0.788 / 0.886

Draw a Fibonacci retracement over the last impulse leg, from the swing low to the swing high (for shorts: swing high to swing low). The zone between **0.705 and 0.886** (with 0.788 in the middle, the level he names; the textbook level is 0.786) is where you want to do business.

Three conditions make the zone valid:

1. **It sits outside the value area.** If the zone is inside value, skip it.
2. **The leg has internal structure.** At least one swing point inside the leg. Markets breathe; a perfectly straight leg is not a leg to trade.
3. **0.886 is the line in the sand.** If price goes beyond 0.886 before buyers take control back, the idea is wrong. No trade.

### C. Inefficient areas

The best zones are often places price moved through quickly: a fast overnight push, a **low-volume node** where little business was done. Price tends to move through them again or reject them sharply.

### Typical scenario

The New York open drops out of the value area low into discount, into the 0.705 to 0.886 zone of the leg that built the value-up structure. Do not sell there. That is where you look to buy.

---

## Step 3. Confirmation (order flow, 5-minute candles)

A zone on the chart is just a drawing. Price does not respect it because you drew it. You need to see who is winning inside it.

### What to read inside each candle

- **Volume profile inside the candle:** where the volume traded, and the candle's own point of control.
- **Delta:** aggressive buying minus aggressive selling. Negative delta means more aggressive sellers.
- **Bid × ask footprint:** imbalances of 400% or more highlight one side lifting or hitting the book aggressively.

### The long entry sequence

1. **Absorption.** In discount, aggressive sellers pile in. Heavy negative delta, with the volume and POC concentrated at the **low of the candle, in the wick**. But they get **no result**: price does not progress lower. Absorption on its own is not a reversal.
2. **First shift.** A candle closes bullish.
3. **Second failure.** The next candle opens and pulls back immediately. Sellers try again and **fail higher**, above where they failed the first time.
4. **Dominance flips.** The candle turns bullish again, with aggressive buyers lifting the offer (ask-side imbalances, positive delta).
5. **Enter long.** Not on the first failure. On the second.

**Stop:** just beyond where sellers failed. The idea is invalid the moment sellers push past the level they could not break before.

### When not to trade

- **Low participation.** If volume dries up (for example, MNQ 5-minute candles below about 20,000 contracts), participation is dying and the setup will not have fuel. This usually happens heading into lunch.
- **News** due right as price reaches the zone.
- **Outside the window.** Trade only the first 90 minutes after the New York open (sometimes the Asia session).

---

## Step 4. Management and targets

1. **The value reclaim checkpoint.** After entry, buyers must get back into the value area. If they cannot, move the stop to entry or exit.
2. **Targets.** The value area POC, or the last swing high where resting orders cluster. Psychological levels where orders stack on the book also act as targets.
3. **Trail.** Set one full target, then trail the stop as price approaches the POC or the call wall. Most trades end around **1.5 to 2R**.
4. **Watch effort versus result.** Every time buyers push, price should progress. If buyers are aggressive but price stays stuck below value, that is effort without result: move to breakeven.

Stated results of this process: a 60 to 65% win rate with a profit factor around 1.8. On prop accounts, 1.5R is enough: a $2,000 drawdown against a $3,000 profit target is exactly 1.5R.

### Shorts

Mirror everything: value down, premium above VAH, Fibonacci from swing high to swing low, buyers absorbed at the top of the candle, short on the second failure of the buyers, stop above it.

---

## Risk and behavior rules

1. **Trade only the first 90 minutes** after the New York open. Performance degrades after that, so there is a hard shut-off time.
2. **Stop after 2 losses in a row.** Three losing setups in one morning is not normal for this process.
3. **0 to 2 trades a day.** Selective participation is the biggest edge a trader has. Order flow is used to filter trades out, not to find more.
4. **Good loss versus bad loss.**
   - Good loss: the setup was executed exactly as planned and lost anyway. That is variance.
   - Bad loss: a rule was broken. You anticipated without confirmation, chased, entered early, or traded from frustration. After a bad mistake, stop for the day.
5. **Rules must be specific actions** tied to your own breaking point. "Don't overtrade" is not a rule. "Stop after two losses in a row" is.
6. **Consistency comes from removing C-game sessions,** not from finding more A+ setups. You do not control how many A+ setups the market gives you. You do control the unnecessary losses.
7. **To learn it,** size down until the size feels almost insulting and focus only on execution.

---

## How the indicator implements each step

| Step | Indicator |
|---|---|
| Value structure | Swing highs and lows on two higher timeframes (default 1h and 4h), confirmed bars only |
| Gamma regime | Settings for regime, call wall, put wall and gamma flip, with an optional "skip positive gamma" filter |
| Value area | Volume profile built from every candle of the session (daily, weekly or cash session only): developing (default) or prior session |
| Fibonacci zone | Automatic impulse leg detection, 0.705 / 0.788 / 0.886 zone, outside-value and internal-swing checks, 0.886 invalidation |
| Low-volume nodes | Zone volume compared with the profile: Thin, Untested or Normal |
| Absorption | Delta and the candle's volume POC estimated from lower-timeframe candles |
| Second failure | A state machine: absorption, first shift, retest that fails higher, aggressive flip, entry |
| Participation | Relative (vs average) or absolute volume filter |
| Management | Stop beyond the failure, value reclaim checkpoint, stop to entry at 1R or when value is not reclaimed, full target at the last swing, stop trailing behind each aggressive candle once price reaches the POC, the call wall or 1.5R |
| Risk rules | Trade window, max trades per day, stop after consecutive losses |

See [SPECIFICATION.md](SPECIFICATION.md) for every formula.
