---
name: s1
description: "AC power flow analysis with CasADi/IPOPT optimization. Covers branch pi-model, nonlinear programming, and power system network data formats."
---

# AC Branch Pi-Model + Transformer Handling

Implement branch power flow equations using MATPOWER branch data:

```
[F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS, ANGMIN, ANGMAX]
```

## Quick start

- Use `scripts/branch_flows.py` to compute per-unit branch flows.
- Results are **power leaving** the "from" bus and **power leaving** the "to" bus.

```python
import json, numpy as np
from scripts.branch_flows import compute_branch_flows_pu, build_bus_id_to_idx

data = json.load(open("/root/network.json"))
baseMVA = float(data["baseMVA"])
buses = np.array(data["bus"], dtype=float)
branches = np.array(data["branch"], dtype=float)

bus_id_to_idx = build_bus_id_to_idx(buses)
Vm = buses[:, 7]; Va = np.deg2rad(buses[:, 8])

br = branches[0]
P_ij, Q_ij, P_ji, Q_ji = compute_branch_flows_pu(Vm, Va, br, bus_id_to_idx)
S_ij_MVA = (P_ij**2 + Q_ij**2)**0.5 * baseMVA
S_ji_MVA = (P_ji**2 + Q_ji**2)**0.5 * baseMVA
```

## Per-unit conventions

- Work in per-unit internally.
- Convert: \(P_{pu} = P_{MW}/baseMVA\), \(Q_{pu} = Q_{MVAr}/baseMVA\), \(|S|_{MVA} = |S|_{pu} \cdot baseMVA\)

## Transformer handling (TAP + SHIFT)

- \(T_{ij} = tap \cdot e^{j \cdot shift}\)
- If `abs(TAP) < 1e-12`, set `tap = 1.0`.
- Convert `SHIFT` from degrees to radians.
- Angle differences: \(\delta_{ij} = \theta_i - \theta_j - shift\), \(\delta_{ji} = \theta_j - \theta_i + shift\)

## Series admittance

Given `BR_R = r`, `BR_X = x`:

- If `r == 0 and x == 0`: `g = 0`, `b = 0`
- Else: \(g = r/(r^2 + x^2)\), \(b = -x/(r^2 + x^2)\)

## Line charging susceptance

- `BR_B` is total line charging \(b_c\) (per unit); each end gets \(b_c/2\).

## Power flow equations

Let \(V_i = |V_i|e^{j\theta_i}\), \(V_j = |V_j|e^{j\theta_j}\), `inv_t = 1/tap`, `inv_t2 = inv_t²`.

Power from i→j:

- \(P_{ij} = g|V_i|^2 inv\_t2 - |V_i||V_j| inv\_t (g\cos\delta_{ij} + b\sin\delta_{ij})\)
- \(Q_{ij} = -(b + b_c/2)|V_i|^2 inv\_t2 - |V_i||V_j| inv\_t (g\sin\delta_{ij} - b\cos\delta_{ij})\)

Power from j→i:

- \(P_{ji} = g|V_j|^2 - |V_i||V_j| inv\_t (g\cos\delta_{ji} + b\sin\delta_{ji})\)
- \(Q_{ji} = -(b + b_c/2)|V_j|^2 - |V_i||V_j| inv\_t (g\sin\delta_{ji} - b\cos\delta_{ji})\)

Apparent power: \(|S_{ij}| = \sqrt{P_{ij}^2 + Q_{ij}^2}\), \(|S_{ji}| = \sqrt{P_{ji}^2 + Q_{ji}^2}\)

## Common uses

- **MVA limits**: `RATE_A` is MVA limit (0 = no limit); enforce \(|S_{ij}| \le RATE_A\) and \(|S_{ji}| \le RATE_A\).
- **Loading %**: `loading_pct = 100 * max(|S_ij|, |S_ji|) / RATE_A` if `RATE_A > 0`, else 0.
- **Nodal balance**: Add \(P_{ij}, Q_{ij}\) to bus i; add \(P_{ji}, Q_{ji}\) to bus j.

---
name: casadi-ipopt-nlp
description: "Nonlinear optimization with CasADi and IPOPT solver. Use when building and solving NLP problems."
---

# CasADi + IPOPT for Nonlinear Programming

## Install

```bash
apt-get update -qq && apt-get install -y -qq libgfortran5
pip install numpy==1.26.4 casadi==3.6.7
```

## Building an NLP

### Decision variables

```python
import casadi as ca
n_bus, n_gen = 100, 20
Vm = ca.MX.sym("Vm", n_bus)
Va = ca.MX.sym("Va", n_bus)
Pg = ca.MX.sym("Pg", n_gen)
Qg = ca.MX.sym("Qg", n_gen)
x = ca.vertcat(Vm, Va, Pg, Qg)
```

### Objective

```python
obj = ca.MX(0)
for k in range(n_gen):
    obj += c2[k] * Pg[k]**2 + c1[k] * Pg[k] + c0[k]
```

### Constraints

```python
g_expr, lbg, ubg = [], [], []
# Equality: g_expr.append(expr); lbg.append(0.0); ubg.append(0.0)
# Inequality: g_expr.append(expr); lbg.append(-ca.inf); ubg.append(limit)
# Two-sided: g_expr.append(expr); lbg.append(lo); ubg.append(hi)
g = ca.vertcat(*g_expr)
```

### Variable bounds

```python
lbx = np.concatenate([Vm_min, Va_min, Pg_min, Qg_min]).tolist()
ubx = np.concatenate([Vm_max, Va_max, Pg_max, Qg_max]).tolist()
```

### Create and solve

```python
nlp = {"x": x, "f": obj, "g": g}
opts = {"ipopt.print_level": 0, "ipopt.max_iter": 2000, "ipopt.tol": 1e-7,
        "ipopt.acceptable_tol": 1e-5, "ipopt.mu_strategy": "adaptive", "print_time": False}
solver = ca.nlpsol("solver", "ipopt", nlp, opts)
sol = solver(x0=x0, lbx=lbx, ubx=ubx, lbg=lbg, ubg=ubg)
x_opt = np.array(sol["x"]).flatten()
obj_val = float(sol["f"])
```

## Initialization

Try multiple starts; keep best feasible:

```python
best_sol = None
for x0 in [x0_from_data, x0_flat_start]:
    try:
        sol = solver(x0=x0, lbx=lbx, ubx=ubx, lbg=lbg, ubg=ubg)
        if best_sol is None or float(sol["f"]) < float(best_sol["f"]):
            best_sol = sol
    except Exception:
        continue
```

Strategies: data-derived (clipped to bounds), flat start (Vm=1.0, Va=0.0), reference angle = 0.

## Extract solutions

```python
x_opt = np.array(sol["x"]).flatten()
Vm_sol = x_opt[:n_bus]
Va_sol = x_opt[n_bus:2*n_bus]
Pg_sol = x_opt[2*n_bus:2*n_bus+n_gen]
Qg_sol = x_opt[2*n_bus+n_gen:]
```

## Power systems patterns

- **Per-unit**: `Pg_pu = Pg_MW / baseMVA`; `Pg_MW = Pg_pu * baseMVA`
- **Bus ID mapping**: `bus_id_to_idx = {int(bus[i,0]): i for i in range(n_bus)}`
- **Per-bus aggregation**: `Pg_bus = [ca.MX(0) for _ in range(n_bus)]` then `Pg_bus[bus_idx] += Pg[k]`

---
name: power-flow-data
description: "Power system network data formats and topology. Use when parsing bus, generator, and branch data for power flow analysis."
---

# Power Flow Data Guide

Network data follows MATPOWER format (PGLib-OPF benchmark).

## Load network data

**Never read line-by-line** with `sed`/`head`. Use Python's JSON parser:

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

## Bus types

| Type | Code | Specified | Solved |
|------|------|-----------|--------|
| Slack | 3 | V, θ=0 | P, Q |
| PV | 2 | P, V | Q, θ |
| PQ | 1 | P, Q | V, θ |

## Bus number mapping

Bus numbers may not be contiguous. Always create a mapping:

```python
bus_num_to_idx = {int(buses[i, 0]): i for i in range(n_bus)}
gen_bus = [bus_num_to_idx[int(g[0])] for g in gens]
```

## Key lookups

- **Generators at bus**: iterate `gens`, match `bus_num_to_idx[int(gen[0])] == bus_idx`
- **Slack bus**: find bus where `bus[1] == 3`
- **Branch info**: `from_bus = bus_num_to_idx[int(branch[0])]`, `to_bus = bus_num_to_idx[int(branch[1])]`, `rating = branch[5]`, `in_service = branch[10] == 1`
- **Total load**: `sum(bus[2] for bus in buses)` (column 2 = Pd)

## Reserve data

- `reserve_capacity`: max reserve per generator (MW)
- `reserve_requirement`: minimum total system reserves (MW)