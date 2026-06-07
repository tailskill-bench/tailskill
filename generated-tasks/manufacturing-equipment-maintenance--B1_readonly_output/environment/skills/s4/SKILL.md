---
name: s1
description: "Reflow machine maintenance: handbook-grounded retrieval, deterministic thermocouple computations for compliance outputs (ramp, TAL, peak, feasibility), and maintenance guidance."
---

## When to invoke

1. Task involves reflow questions from thermocouple data, MES data, defect data, or handbook-defined regions/windows/limits.
2. Extract numeric limits, temperature regions, timing windows, margins, or feasibility rules from handbook.pdf.
3. Compute run-level metrics from time–temperature thermocouple traces deterministically.

## Handbook retrieval checklist

Search handbook.pdf for: "preheat", "soak", "reflow", "cooling", "ramp", "slope", "°C/s", "liquidus", "time above liquidus", "TAL", "peak", "minimum peak", "conveyor speed", "dwell time", "heated length", "cold spot".

Extract a compact config:

```python
cfg = {
  "preheat_region": {...},
  "ramp_limit_c_per_s": ...,
  "tal_threshold_c_source": "solder_liquidus_c",
  "tal_min_s": ..., "tal_max_s": ...,
  "peak_margin_c": ...,
  "conveyor_rule": {...},
}
```

If multiple constraints apply, implement all and use the stricter one (document choice in comments).

## Deterministic thermocouple computation recipes

### 1. Sorting and de-dup

```python
df_tc = df_tc.sort_values(["run_id","tc_id","time_s"], kind="mergesort")
```
Ignore segments where `dt <= 0`.

### 2. Segment slope (ramp rate)

`s_i = (T_i - T_{i-1}) / (t_i - t_{i-1})` for `dt > 0`. Max ramp = `max(s_i)` over region.

Region filters:
- **Temperature band**: both endpoints satisfy `tmin <= T <= tmax`.
- **Zone band**: `zone_id in zones`.
- **Time band**: `t_start_s <= time_s <= t_end_s`.

### 3. Time above threshold (linear interpolation)

For each consecutive pair `(t0,y0)→(t1,y1)` where `t1 > t0`:
- Both above `thr`: add `t1 - t0`.
- Segment crosses `thr` and `y1 != y0`: `tcross = t0 + (thr - y0)/(y1 - y0) * (t1 - t0)`, add portion above threshold.

### 4. Deterministic sensor selection

- **Max metric** (e.g., ramp): `(max_value, smallest_tc_id)`.
- **Min metric** (e.g., coldest TAL/peak): `(min_value, smallest_tc_id)`.

```python
best = max(items, key=lambda x: (x.value, -lex(x.tc_id)))
best = min(items, key=lambda x: (x.value, x.tc_id))
```

### 5. Peak and margin

Per TC: `peak_tc = max(temp_c)`. Run-level: `min_peak_run = min(peak_tc)` (tie by tc_id). Required peak: `required_peak = liquidus + peak_margin`.

### 6. Conveyor feasibility

- **Min dwell time**: `speed_min_cm_min = (L_eff_cm / t_min_s) * 60`
- **Max time-in-oven**: `speed_min_cm_min = (L_eff_cm / t_max_s) * 60`

If parameters missing, output `required_min_speed_cm_min = null` and `meets = false`.

## Output guardrails

- Lists sorted by primary ID lexicographically. Dicts keyed by ID in sorted key order.
- Round floats to 2 decimals. Never emit NaN/Inf; use `null`.
- Missing TC data: set numeric outputs to `null`, avoid claiming "pass" unless explicitly allowed.

## End-to-end scaffold

```python
import os, json, math
import pandas as pd

DATA_DIR = "/app/data"
OUT_DIR  = "/app/output"

runs = pd.read_csv(os.path.join(DATA_DIR, "mes_log.csv"))
tc   = pd.read_csv(os.path.join(DATA_DIR, "thermocouples.csv"))

runs["run_id"] = runs["run_id"].astype(str)
tc["run_id"]   = tc["run_id"].astype(str)
tc["tc_id"]    = tc["tc_id"].astype(str)

runs = runs.sort_values(["run_id"], kind="mergesort")
tc   = tc.sort_values(["run_id","tc_id","time_s"], kind="mergesort")

cfg = {...}  # from handbook RAG
# Compute per-run metrics with stable tie-breaks and interpolation
# Build JSON with sorted IDs, 2dp rounding
# Write to /app/output
```

Before writing results, run:
`python3 /root/.claude/skills/s1/scripts/prepare_output.py /app/output`

## Sanity checks

- ID fields are strings.
- Arrays sorted lexicographically.
- Floats rounded to 2 decimals.
- No NaN/Inf in JSON.
- Sensor selection uses deterministic tie-breaks.
- Time-above-threshold uses interpolation (not naive counting).