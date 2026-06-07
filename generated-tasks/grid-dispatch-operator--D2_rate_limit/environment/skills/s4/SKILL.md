---
name: s1
description: "DC power flow analysis, generator economic dispatch and cost optimization, and power system network data formats and topology for power systems."
---

# DC Power Flow

Linearized approximation: lossless lines (R ≈ 0), flat voltage (V = 1.0 pu), small angles (sin θ ≈ θ). Power flow depends only on bus angles (θ) and line reactances (X).

## Bus Number Mapping

Bus numbers may not be contiguous. Always map to 0-indexed positions:

```python
bus_num_to_idx = {int(buses[i, 0]): i for i in range(n_bus)}
f = bus_num_to_idx[int(br[0])]  # NOT br[0] - 1
t = bus_num_to_idx[int(br[1])]
```

## Susceptance Matrix (B)

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

## Power Balance and Slack Bus

At each bus: `Pg - Pd = B[i, :] @ θ`. One slack bus (type=3) must have θ = 0:

```python
slack_idx = next(i for i in range(n_bus) if buses[i, 1] == 3)
constraints.append(theta[slack_idx] == 0)
```

## Line Flow and Loading

```python
b = 1.0 / br[3]
flow_pu = b * (theta[f] - theta[t])
flow_MW = flow_pu * baseMVA
loading_pct = abs(flow_MW) / branch[5] * 100  # branch[5] = RATE_A
```

Enforce thermal limits: `flow <= rate` and `flow >= -rate`.

---

# Economic Dispatch

Minimize total generation cost meeting load and generator limits.

## Generator Data Indices

MATPOWER generator columns (0-indexed): index 0 = GEN_BUS, index 8 = PMAX, index 9 = PMIN.

```python
gen_bus = [bus_num_to_idx[int(g[0])] for g in gens]
pmax_MW = gen[8]; pmin_MW = gen[9]
```

## Cost Function Format

MATPOWER gencost (MODEL=2 polynomial): index 3 = NCOST, indices 4+ = coefficients (highest order first).

- Quadratic (NCOST=3): [c2, c1, c0] at indices 4, 5, 6 → Cost = c₂·P² + c₁·P + c₀ ($/hr, P in MW)
- Linear (NCOST=2): [c1, c0] at indices 4, 5

## Optimization Formulation

```python
import cvxpy as cp
import numpy as np

Pg = cp.Variable(n_gen)
cost = 0
for i in range(n_gen):
    Pg_MW = Pg[i] * baseMVA
    ncost = int(gencost[i, 3])
    if ncost >= 3:
        cost += gencost[i,4]*cp.square(Pg_MW) + gencost[i,5]*Pg_MW + gencost[i,6]
    elif ncost == 2:
        cost += gencost[i,4]*Pg_MW + gencost[i,5]
    elif ncost >= 1:
        cost += gencost[i,4]

constraints = []
for i in range(n_gen):
    constraints += [Pg[i] >= gens[i,9]/baseMVA, Pg[i] <= gens[i,8]/baseMVA]

total_load_pu = sum(buses[i,2] for i in range(n_bus)) / baseMVA
constraints.append(cp.sum(Pg) == total_load_pu)
```

## Reserve Co-optimization

```python
Rg = cp.Variable(n_gen)
reserve_capacity = np.array(data['reserve_capacity'])
reserve_requirement = data['reserve_requirement']

constraints.append(Rg >= 0)
for i in range(n_gen):
    constraints += [Rg[i] <= reserve_capacity[i],
                    Pg[i]*baseMVA + Rg[i] <= gens[i,8]]
constraints.append(cp.sum(Rg) >= reserve_requirement)
```

## Operating Margin and Output

```python
Pg_MW = Pg.value * baseMVA
Rg_MW = Rg.value
operating_margin_MW = sum(gens[i,8] - Pg_MW[i] - Rg_MW[i] for i in range(n_gen))

generator_dispatch = [{"id": i+1, "bus": int(gens[i,0]),
    "output_MW": round(float(Pg_MW[i]),2),
    "reserve_MW": round(float(Rg_MW[i]),2),
    "pmax_MW": round(float(gens[i,8]),2)} for i in range(n_gen)]

totals = {"cost_dollars_per_hour": round(float(prob.value),2),
    "load_MW": round(float(sum(buses[i,2] for i in range(n_bus))),2),
    "generation_MW": round(float(sum(Pg_MW)),2),
    "reserve_MW": round(float(sum(Rg_MW)),2)}
```

Use CLARABEL solver: `prob.solve(solver=cp.CLARABEL)`.

---

# Power Flow Data Guide

Network data follows MATPOWER format (PGLib-OPF library).

## Loading Network Data

**Never read large JSON files line-by-line.** Use Python's JSON parser:

```python
import json, numpy as np

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

## Bus Types and Topology

- **Slack (type 3):** V, θ=0 specified; balances power
- **PV (type 2):** P, V specified; generator bus
- **PQ (type 1):** P, Q specified; load bus

Per-unit: `P_pu = P_MW / baseMVA` (baseMVA typically 100).

## Key Data Access

- Branch columns: 0=from_bus, 1=to_bus, 2=resistance, 3=reactance, 4=susceptance, 5=rating, 10=in_service (1=active)
- Bus column 2 = Pd (load); total load: `sum(bus[2] for bus in buses)`
- Reserve fields: `reserve_capacity` (array, MW per generator), `reserve_requirement` (float, minimum total MW)

## Writing Output

```python
import json, os
output_path = '/root/report.json'
os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(report, f, indent=2)
```

If write fails: `os.chmod('/root', 0o755)` or run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/report.json`.