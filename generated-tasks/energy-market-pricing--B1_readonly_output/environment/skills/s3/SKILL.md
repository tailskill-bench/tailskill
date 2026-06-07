---
name: s1
description: "DC power flow analysis for power systems. Use when computing power flows using DC approximation, building susceptance matrices, calculating line flows and loading percentages, or performing sensitivity analysis on transmission networks. Generator economic dispatch and cost optimization for power systems. Use when minimizing generation costs, computing optimal generator setpoints, calculating operating margins, or working with generator cost functions. Extract locational marginal prices (LMPs) from DC-OPF solutions using dual values. Use when computing nodal electricity prices, reserve clearing prices, or performing price impact analysis. Power system network data formats and topology. Use when parsing bus, generator, and branch data for power flow analysis."
---

# DC Power Flow

DC power flow is a linearized approximation assuming lossless lines (R ≈ 0), flat voltage (1.0 pu), and small angles (sin(θ) ≈ θ). Power flow depends only on bus angles (θ) and line reactances (X).

## Bus Number Mapping

Bus numbers may not be contiguous. Always map bus numbers to 0-indexed array positions:

```python
bus_num_to_idx = {int(buses[i, 0]): i for i in range(n_bus)}
f = bus_num_to_idx[int(br[0])]  # NOT br[0] - 1
t = bus_num_to_idx[int(br[1])]
```

## Susceptance Matrix (B)

Build from branch reactances using bus number mapping:

```python
B = np.zeros((n_bus, n_bus))
for br in branches:
    f = bus_num_to_idx[int(br[0])]
    t = bus_num_to_idx[int(br[1])]
    x = br[3]
    if x != 0:
        b = 1.0 / x
        B[f, f] += b
        B[t, t] += b
        B[f, t] -= b
        B[t, f] -= b
```

## Power Balance and Slack Bus

At each bus: `Pg - Pd = B[i, :] @ θ`. One slack bus (type=3) must have θ = 0:

```python
slack_idx = None
for i in range(n_bus):
    if buses[i, 1] == 3:
        slack_idx = i
        break
constraints.append(theta[slack_idx] == 0)
```

## Line Flow and Loading

Flow on branch from bus f to bus t:

```python
b = 1.0 / br[3]
flow_pu = b * (theta[f] - theta[t])
flow_MW = flow_pu * baseMVA
loading_pct = abs(flow_MW) / branch[5] * 100  # branch[5] = RATE_A
```

Line flow limits for OPF: `flow <= rate` and `flow >= -rate`.

---

# Economic Dispatch

Minimize total generation cost while meeting load and respecting generator limits.

## Generator and Cost Data

MATPOWER generator columns (0-indexed): index 0 = GEN_BUS, index 8 = PMAX, index 9 = PMIN.

MATPOWER gencost (polynomial type 2): index 3 = NCOST, indices 4+ = coefficients (highest order first).
- Quadratic (NCOST=3): [c2, c1, c0] at indices 4, 5, 6
- Linear (NCOST=2): [c1, c0] at indices 4, 5

Cost = c₂·P² + c₁·P + c₀ ($/hr) where P is in MW.

## Optimization Formulation

```python
import cvxpy as cp

Pg = cp.Variable(n_gen)
cost = 0
for i in range(n_gen):
    Pg_MW = Pg[i] * baseMVA
    ncost = int(gencost[i, 3])
    if ncost >= 3:
        c2, c1, c0 = gencost[i, 4], gencost[i, 5], gencost[i, 6]
        cost += c2 * cp.square(Pg_MW) + c1 * Pg_MW + c0
    elif ncost == 2:
        c1, c0 = gencost[i, 4], gencost[i, 5]
        cost += c1 * Pg_MW + c0

constraints = []
for i in range(n_gen):
    constraints.append(Pg[i] >= gens[i, 9] / baseMVA)
    constraints.append(Pg[i] <= gens[i, 8] / baseMVA)

total_load_pu = sum(buses[i, 2] for i in range(n_bus)) / baseMVA
constraints.append(cp.sum(Pg) == total_load_pu)
```

## Reserve Co-optimization

```python
reserve_capacity = np.array(data['reserve_capacity'])
reserve_requirement = data['reserve_requirement']

Rg = cp.Variable(n_gen)
constraints.append(Rg >= 0)
for i in range(n_gen):
    constraints.append(Rg[i] <= reserve_capacity[i])
    constraints.append(Pg[i] * baseMVA + Rg[i] <= gens[i, 8])
constraints.append(cp.sum(Rg) >= reserve_requirement)
```

Operating margin: `sum(gens[i, 8] - Pg_MW[i] - Rg_MW[i] for i in range(n_gen))`

## Dispatch Output

```python
Pg_MW = Pg.value * baseMVA
Rg_MW = Rg.value
generator_dispatch = [{"id": i + 1, "bus": int(gens[i, 0]),
    "output_MW": round(float(Pg_MW[i]), 2),
    "reserve_MW": round(float(Rg_MW[i]), 2),
    "pmax_MW": round(float(gens[i, 8]), 2)} for i in range(n_gen)]
```

Before writing results: `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/report.json`

## Solver Selection

For quadratic costs with network constraints, use CLARABEL: `prob.solve(solver=cp.CLARABEL)`

---

# Locational Marginal Prices (LMPs)

LMPs are dual values (shadow prices) of nodal power balance constraints.

## LMP Extraction from CVXPY

Store balance constraint references before solving, then read dual values:

```python
balance_constraints = []
for i in range(n_bus):
    pg_at_bus = sum(Pg[g] for g in range(n_gen) if gen_bus[g] == i)
    pd = buses[i, 2] / baseMVA
    balance_con = pg_at_bus - pd == B[i, :] @ theta
    balance_constraints.append(balance_con)
    constraints.append(balance_con)

prob = cp.Problem(cp.Minimize(cost), constraints)
prob.solve(solver=cp.CLARABEL)

lmp_by_bus = [{"bus": int(buses[i, 0]),
    "lmp_dollars_per_MWh": round(float(balance_constraints[i].dual_value) * baseMVA, 2)}
    for i in range(n_bus)]
```

**Sign convention**: Positive LMP = increasing load increases cost. Negative LMPs are valid (cheap generation trapped behind congestion).

## Reserve Clearing Price

```python
reserve_con = cp.sum(Rg) >= reserve_requirement
constraints.append(reserve_con)
reserve_mcp = float(reserve_con.dual_value) if reserve_con.dual_value is not None else 0.0
```

## Finding Binding Lines

Lines at ≥99% loading cause congestion and LMP separation:

```python
BINDING_THRESHOLD = 99.0
binding_lines = []
for k, br in enumerate(branches):
    f = bus_num_to_idx[int(br[0])]
    t = bus_num_to_idx[int(br[1])]
    x, rate = br[3], br[5]
    if x != 0 and rate > 0:
        flow_MW = (1.0 / x) * (theta.value[f] - theta.value[t]) * baseMVA
        if abs(flow_MW) / rate * 100 >= BINDING_THRESHOLD:
            binding_lines.append({"from": int(br[0]), "to": int(br[1]),
                "flow_MW": round(float(flow_MW), 2), "limit_MW": round(float(rate), 2)})
```

## Counterfactual Analysis

1. Solve base case → record costs, LMPs, binding lines
2. Modify constraint (e.g., increase line limit by 20%)
3. Solve counterfactual → compare costs and LMPs

```python
for k in range(n_branch):
    if (int(branches[k, 0]) == target_from and int(branches[k, 1]) == target_to) or \
       (int(branches[k, 0]) == target_to and int(branches[k, 1]) == target_from):
        branches[k, 5] *= 1.20
        break
```

---

# Power Flow Data Guide

Network data follows MATPOWER format from PGLib-OPF (github.com/power-grid-lib/pglib-opf).

## ⚠️ Handling Large Network Files

Network JSON files can be very large. **Always use Python's JSON parser directly:**

```python
import json
with open('network.json') as f:
    data = json.load(f)
```

## Bus Types

| Type | Code | Specified | Solved |
|------|------|-----------|--------|
| Slack | 3 | V, θ=0 | P, Q |
| PV | 2 | P, V | Q, θ |
| PQ | 1 | P, Q | V, θ |

Per-unit system: `baseMVA = 100`, `P_pu = P_MW / baseMVA`

## Loading Network Data

```python
import numpy as np

def load_network(filepath):
    with open(filepath) as f:
        data = json.load(f)
    return {
        'baseMVA': data['baseMVA'],
        'bus': np.array(data['bus']),
        'gen': np.array(data['gen']),
        'branch': np.array(data['branch']),
        'gencost': np.array(data['gencost']),
        'reserve_capacity': np.array(data['reserve_capacity']),
        'reserve_requirement': data['reserve_requirement']
    }
```

## Reserve Data

- `reserve_capacity`: Maximum reserve per generator (MW)
- `reserve_requirement`: Minimum total system reserves (MW)

## Utility Functions

```python
def get_generators_at_bus(gens, bus_idx, bus_num_to_idx):
    return [i for i, gen in enumerate(gens) if bus_num_to_idx[int(gen[0])] == bus_idx]

def find_slack_bus(buses):
    return next((i for i, bus in enumerate(buses) if bus[1] == 3), None)

def total_load(buses):
    return sum(bus[2] for bus in buses)  # Column 2 = Pd
```

Branch data: index 0 = from_bus, 1 = to_bus, 2 = resistance, 3 = reactance, 4 = susceptance, 5 = rating, 10 = in_service (1).