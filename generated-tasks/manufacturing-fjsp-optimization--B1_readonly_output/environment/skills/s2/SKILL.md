---
name: s1
description: "FJSP optimization with downtime and policy constraints for manufacturing scheduling."
---

Before writing results, ensure the output directory has proper write permissions. Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /app/output` to fix directory permissions.

## Constraints

- **Precedence**: `end(j, o) <= start(j, o+1)`
- **No overlaps** on the same machine or with downtime windows
- **Policy budgets**: Keep machine changes and total L1 start-time shift within limits
  - Machine changes: `MC = Σ [m_new(j,o) ≠ m_base(j,o)]`
  - L1 shift: `Shift_L1 = Σ |start_new(j,o) - start_base(j,o)|`

## Pipeline

For each operation in precedence-aware order:

1. **Compute anchor**: `anchor(j,o) = max(start_base(j,o), end_new(j,o-1))`
2. **List allowed machines** and their processing times for this operation
3. **For each candidate machine**, find earliest feasible time by scanning forward from anchor by +1
4. **Select option** minimizing `(machine_change, start_shift, start_time, machine)` lexicographically
5. **Record operation** on machine timeline immediately

**Key rules**:
- Never start any operation earlier than the baseline
- If baseline machine is invalid, replace with feasible one (min duration heuristic)
- Jumping to "next gap" without checking every integer may break minimality

## Reference Code

```python
# Sorted downtime windows
downtime[m] = sorted([(start, end), ...])

def overlap(s, e, a, b):
    return s < b and a < e

def has_conflict(m, st, en, machine_intervals, downtime):
    for a, b in machine_intervals.get(m, []):
        if overlap(st, en, a, b):
            return True
    for a, b in downtime.get(m, []):
        if overlap(st, en, a, b):
            return True
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
# Precedence-aware repair order
def precedence_aware_order(base_list):
    base_map = {(r["job"], r["op"]): r for r in base_list}
    base_index = {(r["job"], r["op"]): i for i, r in enumerate(base_list)}
    keys = list(base_map.keys())
    keys.sort(key=lambda k: (k[1], base_map[k]["start"], base_index[k]))
    return keys
```

```python
# Handle invalid baseline machine
base_m = base_map[(j, o)]["machine"]
if base_m not in allowed[(j, o)]:
    base_m = min(allowed[(j, o)], key=lambda m: allowed[(j, o)][m])
base_d = allowed[(j, o)][base_m]
```

```python
# Lexicographic scoring
machine_change = int(mm != base_m_orig)
start_shift = abs(st - base_start)
score = (machine_change, start_shift, st, mm)
```

```python
# Consider alternates when shift is large
THRESH = 6
cand = best_candidate_restricted_to([base_m])
if (cand.start - base_start) >= THRESH and mc_used < max_mc:
    cand2 = best_candidate_over_all_allowed_machines()
    if cand2.start < cand.start:
        cand = cand2