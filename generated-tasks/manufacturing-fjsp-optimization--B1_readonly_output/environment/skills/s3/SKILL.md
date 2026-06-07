---
name: s1
description: "FJSP optimization with downtime and policy constraints for manufacturing scheduling."
---

Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /app/output` to fix output directory permissions.

## Constraints

- **Precedence**: `end(j, o) <= start(j, o+1)`
- **No overlaps** on same machine or with downtime windows
- **Policy budgets**: machine changes `MC = Σ [m_new(j,o) ≠ m_base(j,o)]` and L1 shift `Shift_L1 = Σ |start_new(j,o) - start_base(j,o)|` within limits

## Pipeline

For each operation in precedence-aware order:

1. **Compute anchor**: `anchor(j,o) = max(start_base(j,o), end_new(j,o-1))`
2. **List allowed machines** and processing times for this operation
3. **For each candidate machine**, find earliest feasible time scanning forward from anchor by +1
4. **Select option** minimizing `(machine_change, start_shift, start_time, machine)` lexicographically
5. **Record operation** on machine timeline immediately

**Key rules**:
- Never start any operation earlier than baseline
- If baseline machine invalid, replace with feasible one (min duration heuristic)
- Check every integer; skipping to "next gap" may break minimality

## Reference Code

```python
downtime[m] = sorted([(start, end), ...])

def overlap(s, e, a, b):
    return s < b and a < e

def has_conflict(m, st, en, machine_intervals, downtime):
    for a, b in machine_intervals.get(m, []):
        if overlap(st, en, a, b): return True
    for a, b in downtime.get(m, []):
        if overlap(st, en, a, b): return True
    return False

def earliest_feasible_time(m, anchor, dur, machine_intervals, downtime, safety=200000):
    t = int(anchor)
    for _ in range(safety):
        if not has_conflict(m, t, t + dur, machine_intervals, downtime):
            return t
        t += 1
    return t
```

```python
def precedence_aware_order(base_list):
    base_map = {(r["job"], r["op"]): r for r in base_list}
    base_index = {(r["job"], r["op"]): i for i, r in enumerate(base_list)}
    keys = list(base_map.keys())
    keys.sort(key=lambda k: (k[1], base_map[k]["start"], base_index[k]))
    return keys
```

**Invalid baseline machine**: if `base_m` not in `allowed[(j,o)]`, set `base_m = min(allowed[(j,o)], key=lambda m: allowed[(j,o)][m])`.

**Lexicographic scoring**: `score = (int(mm != base_m_orig), abs(st - base_start), st, mm)`.

**Alternate machines**: if best candidate on baseline machine has `start - base_start >= 6` and `mc_used < max_mc`, check all allowed machines; adopt if earlier start found.