---
name: s1
description: "DC power flow analysis for power systems. Use when computing power flows using DC approximation, building susceptance matrices, calculating line flows and loading percentages, or performing sensitivity analysis on transmission networks. Generator economic dispatch and cost optimization for power systems. Use when minimizing generation costs, computing optimal generator setpoints, calculating operating margins, or working with generator cost functions. Extract locational marginal prices (LMPs) from DC-OPF solutions using dual values. Use when computing nodal electricity prices, reserve clearing prices, or performing price impact analysis. Power system network data formats and topology. Use when parsing bus, generator, and branch data for power flow analysis."
---

# DC Power Flow

DC power flow is a linearized approximation of AC power flow, suitable for economic dispatch and contingency analysis.

## DC Approximations

1. **Lossless lines** - Ignore resistance (R ≈ 0)
2. **Flat voltage** - All bus voltages = 1.0 pu
3. **Small angles** - sin(θ) ≈ θ, cos(θ) ≈ 1

Result: Power flow depends only on bus angles (θ) and line reactances (X).

## Bus Number Mapping

Power system bus numbers may not be contiguous (e.g., case300 has non-sequential bus IDs). Always create a mapping from bus numbers to 0-indexed array positions:

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
        B[f, f] += b; B[t, t] += b
        B[f, t] -= b; B[t, f] -= b
```

## Power Balance Equation

At each bus: `Pg - Pd = B[i, :] @ θ`

## Slack Bus

One bus must have θ = 0 as reference. Find slack bus (type=3):

```python
slack_idx = next(i for i in range(n_bus) if buses[i, 1] == 3)
constraints.append(theta[slack_idx] == 0)
```

## Line Flow Calculation

```python
b = 1.0 / br[3]
flow_pu = b * (theta[f] - theta[t])
flow_MW = flow_pu * baseMVA
```

## Line Loading Percentage

```python
loading_pct = abs(flow_MW) / branch[5] * 100  # branch[5] = RATE_A
```

## Line Flow Limits (for OPF)

```python
flow = b * (theta[f] - theta[t]) * baseMVA
constraints += [flow <= rate, flow >= -rate]
```

---

# Economic Dispatch

Economic dispatch minimizes total generation cost while meeting load demand and respecting generator limits.

## Generator Data Indices

MATPOWER generator array columns (0-indexed): Index 0 = GEN_BUS, Index 8 = PMAX, Index 9 = PMIN.

```python
gen_bus = [bus_num_to_idx[int(g[0])] for g in gens]
pmax_MW = gen[8]; pmin_MW = gen[9]
```

## Cost Function Format

MATPOWER gencost array (polynomial type 2): Index 0 = MODEL (2), Index 3 = NCOST, Index 4+ = coefficients (highest order first).

- Quadratic (NCOST=3): [c2, c1, c0] at indices 4, 5, 6
- Linear (NCOST=2): [c1, c0] at indices 4, 5

Cost = c₂·P² + c₁·P + c₀ ($/hr) where P is in MW.

## Optimization Formulation

```python
import cvxpy as cp

Pg = cp.Variable(n_gen)
cost = 0
for i in range(n_gen):
    ncost = int(gencost[i, 3])
    Pg_MW = Pg[i] * baseMVA
    if ncost >= 3:
        cost += gencost[i,4]*cp.square(Pg_MW) + gencost[i,5]*Pg_MW + gencost[i,6]
    elif ncost == 2:
        cost += gencost[i,4]*Pg_MW + gencost[i,5]

constraints = []
for i in range(n_gen):
    constraints += [Pg[i] >= gens[i,9]/baseMVA, Pg[i] <= gens[i,8]/baseMVA]
```

## Power Balance Constraint

```python
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
    constraints += [Rg[i] <= reserve_capacity[i],
                    Pg[i]*baseMVA + Rg[i] <= gens[i,8]]
constraints.append(cp.sum(Rg) >= reserve_requirement)
```

## Operating Margin

```python
operating_margin_MW = sum(gens[i,8] - Pg.value*baseMVA[i] - Rg.value[i] for i in range(n_gen))
```

## Dispatch Output Format

```python
generator_dispatch = [{"id": i+1, "bus": int(gens[i,0]),
    "output_MW": round(float(Pg.value[i]*baseMVA),2),
    "reserve_MW": round(float(Rg.value[i]),2),
    "pmax_MW": round(float(gens[i,8]),2)} for i in range(n_gen)]
```

## Dependencies

```bash
pip3 install --break-system-packages numpy==1.26.4 scipy==1.11.4 cvxpy==1.4.2
```

## Solver Selection

```python
prob = cp.Problem(cp.Minimize(cost), constraints)
prob.solve(solver=cp.CLARABEL)
```

---

# Locational Marginal Prices (LMPs)

LMPs are the dual values (shadow prices) of the nodal power balance constraints.

## LMP Extraction from CVXPY

Store balance constraint references before solving, then read dual values:

```python
balance_constraints = []
for i in range(n_bus):
    pg_at_bus = sum(Pg[g] for g in range(n_gen) if gen_bus[g] == i)
    pd = buses[i, 2] / baseMVA
    con = pg_at_bus - pd == B[i, :] @ theta
    balance_constraints.append(con)
    constraints.append(con)

prob.solve(solver=cp.CLARABEL)

lmp_by_bus = [{"bus": int(buses[i,0]),
    "lmp_dollars_per_MWh": round(float(balance_constraints[i].dual_value)*baseMVA, 2)}
    for i in range(n_bus)]
```

## LMP Sign Convention

For `generation - load == net_export`: Positive LMP = increasing load increases cost; Negative LMP = increasing load decreases cost (cheap generation trapped behind congestion).

## Reserve Clearing Price

```python
reserve_con = cp.sum(Rg) >= reserve_requirement
# After solving:
reserve_mcp = float(reserve_con.dual_value) if reserve_con.dual_value is not None else 0.0
```

## Finding Binding Lines

Lines at ≥99% loading cause congestion and LMP separation.

```python
BINDING_THRESHOLD = 99.0
binding_lines = []
for br in branches:
    f, t = bus_num_to_idx[int(br[0])], bus_num_to_idx[int(br[1])]
    x, rate = br[3], br[5]
    if x != 0 and rate > 0:
        flow_MW = (1.0/x) * (theta.value[f] - theta.value[t]) * baseMVA
        if abs(flow_MW)/rate*100 >= BINDING_THRESHOLD:
            binding_lines.append({"from": int(br[0]), "to": int(br[1]),
                "flow_MW": round(float(flow_MW),2), "limit_MW": round(float(rate),2)})
```

## Counterfactual Analysis

1. Solve base case → record costs, LMPs, binding lines
2. Modify constraint (e.g., increase line limit by 20%)
3. Solve counterfactual
4. Compare: `cost_reduction = base_cost - cf_cost`; LMP delta per bus

---

# Power Flow Data Guide

Network data follows MATPOWER format from PGLib-OPF (github.com/power-grid-lib/pglib-opf).

## ⚠️ Handling Large Network Files

Never read line-by-line. Use Python's JSON parser:

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

## Per-Unit System

`baseMVA = 100`; `P_pu = P_MW / baseMVA`

## Loading Network Data

```python
import numpy as np
def load_network(filepath):
    with open(filepath) as f: data = json.load(f)
    return {'baseMVA': data['baseMVA'], 'bus': np.array(data['bus']),
        'gen': np.array(data['gen']), 'branch': np.array(data['branch']),
        'gencost': np.array(data['gencost']),
        'reserve_capacity': np.array(data['reserve_capacity']),
        'reserve_requirement': data['reserve_requirement']}
```

## Reserve Data

- `reserve_capacity`: max reserve per generator (MW)
- `reserve_requirement`: minimum total system reserves (MW)

## Branch Data

Column indices: 0=from_bus, 1=to_bus, 2=resistance, 3=reactance, 4=susceptance, 5=rating, 10=in_service (1=true).