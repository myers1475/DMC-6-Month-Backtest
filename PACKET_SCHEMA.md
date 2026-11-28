<!-- Maintained by roan-maverick. -->

# Packet schema: `order-flow-strategy/v1`

The indicator can send one JSON packet per closed candle, or only on setups and trade updates (default). Missing values are `null`. Prices are rounded to the symbol's tick size.

Full example: [`examples/sample_packet.json`](../examples/sample_packet.json)

## Top level

| Field | Type | Description |
|---|---|---|
| `schema` | string | Always `"order-flow-strategy/v1"` |
| `event` | enum | `LONG_ENTRY`, `SHORT_ENTRY`, `TRADE_UPDATE`, `ABSORPTION`, `BAR_CLOSE` |
| `symbol` | string | Exchange prefix and ticker, e.g. `CME_MINI:MNQ1!` |
| `timeframe` | string | TradingView timeframe code, e.g. `5` |
| `time` | string | Candle close time, ISO 8601 UTC |
| `price` | object | `open`, `high`, `low`, `close`, `volume` of the candle that just closed |
| `environment` | object | Step 1 |
| `location` | object | Step 2 |
| `order_flow` | object | Step 3 |
| `risk` | object | Daily risk counters |
| `trade` | object | Step 4: the tracked trade |

## `environment`

| Field | Type | Description |
|---|---|---|
| `window_open` | bool | Inside the trade window |
| `structure` | enum | `VALUE_UP`, `VALUE_DOWN`, `BALANCE` |
| `htf1`, `htf2` | string | Structure timeframes |
| `htf1_structure`, `htf2_structure` | int | `1` up, `-1` down, `0` balance |
| `gamma_regime` | enum | `NEGATIVE`, `POSITIVE`, `NOT SET` |
| `call_wall`, `put_wall`, `gamma_flip` | number or null | Levels entered in the settings |

## `location`

| Field | Type | Description |
|---|---|---|
| `value_area_high`, `poc`, `value_area_low` | number or null | Active value area |
| `position` | enum | `DISCOUNT`, `PREMIUM`, `INSIDE_VALUE`, `UNKNOWN` |
| `long_zone.ready` | bool | Discount zone is valid (outside value, internal swing, not invalidated) |
| `long_zone.in_zone` | bool | Price is inside 0.705 to 0.886 |
| `long_zone.top`, `mid`, `bottom` | number or null | 0.705, 0.788 and 0.886 levels |
| `long_zone.leg_high`, `leg_low` | number or null | The impulse leg |
| `long_zone.zone_volume` | enum | `THIN`, `UNTESTED`, `NORMAL`, `UNKNOWN` |
| `short_zone.*` | | Same fields for the premium zone. `bottom` is 0.705, `top` is 0.886 |

## `order_flow`

| Field | Type | Description |
|---|---|---|
| `delta_pct` | number or null | Net aggression of the candle, -100 to 100 |
| `volume_poc_position_pct` | number | Where the candle's volume POC sits: 0 = low, 100 = high |
| `close_position_pct` | number | Where the candle closed: 0 = low, 100 = high |
| `relative_volume` | number or null | Volume / 50-bar average |
| `participation_ok` | bool | Volume filter passed |
| `sellers_absorbed`, `buyers_absorbed` | bool | Absorption detected on this candle |
| `long_state`, `short_state` | enum | `IDLE`, `ABSORPTION`, `FIRST_SHIFT` |

## `risk`

| Field | Type | Description |
|---|---|---|
| `trades_today`, `max_trades` | int | Entries taken today and the daily limit |
| `loss_streak`, `max_loss_streak` | int | Consecutive losses today and the limit |

## `trade`

| Field | Type | Description |
|---|---|---|
| `side` | enum | `LONG`, `SHORT`, `NONE` (side of the most recent tracked trade) |
| `status` | enum | `ACTIVE`, `VALUE_RECLAIMED`, `STOP_AT_ENTRY`, `NO_RECLAIM_STOP_AT_ENTRY`, `TRAILING`, `TARGET_HIT`, `TRAIL_STOP`, `STOPPED`, `BREAKEVEN`, `NONE` |
| `open` | bool | Trade still open |
| `entry`, `stop`, `target` | number or null | Trade levels (stop updates when it moves to entry or trails) |
| `target_source` | enum | `POC`, `SWING`, `R`, `NONE` |
| `risk_per_unit` | number or null | Entry to original stop |
| `reclaim_level` | number or null | VAL (long) or VAH (short) at entry |
| `bars_since_entry` | int or null | Bars since the trade opened |
| `trailing` | bool | The stop is trailing behind aggression |
| `trail_trigger` | number or null | Price where trailing starts (POC, gamma wall or the start R) |

Breaking changes will use a new schema name. Agents should check `schema` first.
