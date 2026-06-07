---
name: s1
description: "AC power flow analysis with CasADi/IPOPT optimization. Covers branch pi-model, nonlinear programming, and power system network data formats."
---

# AC Branch Pi-Model + Transformer Handling

Implement the exact branch power flow equations in `acopf-math-model.md` using MATPOWER branch data:

```
[F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS, ANGMIN, ANGMAX]
```

## Quick start

- Use `scripts/branch_flows.py` to compute per-unit branch flows.
- Treat the results as **power leaving** the "from" bus and **power leaving** the "to" bus.

```python
import json
import numpy as np
from scripts.branch_flows import compute_branch_flows_pu, build_bus_id_to_idx

data = json.load(open("/root/network.json"))
baseMVA = float(data["baseMVA"])
buses = np.array(data["bus"], dtype=float)
branches = np.array(data["branch"], dtype=float)

bus_id_to_idx = build_bus_id_to_idx(buses)
Vm = buses[:, 7]
Va = np.deg2rad(buses[:, 8])

br = branches[0]
P_ij, Q_ij, P_ji, Q_ji = compute_branch_flows_pu(Vm, Va, br, bus_id_to_idx)
S_ij_MVA = (P_ij**2 + Q_ij**2) ** 0.5 * baseMVA
S_ji_MVA = (P_ji**2 + Q_ji**2) ** 0.5 * baseMVA
```

## Model details

### Per-unit conventions

- Work in per-unit internally.
- Convert with `baseMVA`: \(P_{pu} = P_{MW} / baseMVA\), \(Q_{pu} = Q_{MVAr} / baseMVA\), \(|S|_{MVA} = |S|_{pu} \cdot baseMVA\)

### Transformer handling (MATPOWER TAP + SHIFT)

- Use \(T_{ij} = tap \cdot e^{j \cdot shift}\).
- If `abs(TAP) < 1e-12`, treat `tap = 1.0` (no transformer).
- Convert `SHIFT` from degrees to radians.
- Angle differences: \(\delta_{ij} = \theta_i - \theta_j - shift\), \(\delta_{ji} = \theta_j - \theta_i + shift\)

### Series admittance

Given `BR_R = r`, `BR_X = x`:

- If `r == 0 and x == 0`, set `g = 0`, `b = 0`.
- Else: \(g = r/(r^2 + x^2)\), \(b = -x/(r^2 + x^2)\)

### Line charging susceptance

- `BR_B` is the **total** line charging susceptance \(b_c\) (per unit).
- Each end gets \(b_c/2\) in the standard pi model.

## Power flow equations

Let \(V_i = |V_i| e^{j\theta_i}\), \(V_j = |V_j| e^{j\theta_j}\), `tap` real, `shift` radians, `inv_t = 1/tap`, `inv_t2 = inv_t^2`.

Power from i→j:

- \(P_{ij} = g |V_i|^2 inv\_t2 - |V_i||V_j| inv\_t (g\cos\delta_{ij} + b\sin\delta_{ij})\)
- \(Q_{ij} = -(b + b_c/2)|V_i|^2 inv\_t2 - |V_i||V_j| inv\_t (g\sin\delta_{ij} - b\cos\delta_{ij})\)

Power from j→i:

- \(P_{ji} = g |V_j|^2 - |V_i||V_j| inv\_t (g\cos\delta_{ji} + b\sin\delta_{ji})\)
- \(Q_{ji} = -(b + b_c/2)|V_j|^2 - |V_i||V_j| inv\_t (g\sin\delta_{ji} - b\cos\delta_{ji})\)

Apparent power: \(|S_{ij}| = \sqrt{P_{ij}^2 + Q_{ij}^2}\), \(|S_{ji}| = \sqrt{P_{ji}^2 + Q_{ji}^2}\)

## Common uses

### Enforce MVA limits (rateA)

- `RATE_A` is an MVA limit (0 means no limit).
- Enforce: \(|S_{ij}| \le RATE_A\) and \(|S_{ji}| \le RATE_A\)

### Compute branch loading %

- `loading_pct = 100 * max(|S_ij|, |S_ji|) / RATE_A` if `RATE_A > 0`, else 0.

### Aggregate bus injections for nodal balance

- Add \(P_{ij}, Q_{ij}\) to bus i; add \(P_{ji}, Q_{ji}\) to bus j.
- Nodal balance: \(P^g - P^d - G^s|V|^2 = P_{out}\), \(Q^g - Q^d + B^s|V|^2 = Q_{out}\)

---

---
name: casadi-ipopt-nlp
description: "Nonlinear optimization with CasADi and IPOPT solver. Use when building and solving NLP problems: defining symbolic variables, adding nonlinear constraints, setting solver options, handling multiple initializations, and extracting solutions."
---

# CasADi + IPOPT for Nonlinear Programming

## Quick start (Linux)

```bash
apt-get update -qq && apt-get install -y -qq libgfortran5
pip install numpy==1.26.4 casadi==3.6.7
```

## Building an NLP

### 1. Decision variables

```python
import casadi as ca

n_bus, n_gen = 100, 20
Vm = ca.MX.sym("Vm", n_bus)
Va = ca.MX.sym("Va", n_bus)
Pg = ca.MX.sym("Pg", n_gen)
Qg = ca.MX.sym("Qg", n_gen)
x = ca.vertcat(Vm, Va, Pg, Qg)
```

### 2. Objective function

```python
obj = ca.MX(0)
for k in range(n_gen):
    obj += c2[k] * Pg[k]**2 + c1[k] * Pg[k] + c0[k]
```

### 3. Constraints

```python
g_expr, lbg, ubg = [], [], []

# Equality: g(x) = 0
g_expr.append(some_expression); lbg.append(0.0); ubg.append(0.0)

# Inequality: g(x) <= limit
g_expr.append(another_expression); lbg.append(-ca.inf); ubg.append(limit)

# Two-sided: lo <= g(x) <= hi
g_expr.append(bounded_expression); lbg.append(lo); ubg.append(hi)

g = ca.vertcat(*g_expr)
```

### 4. Variable bounds

```python
lbx = np.concatenate([Vm_min, Va_min, Pg_min, Qg_min]).tolist()
ubx = np.concatenate([Vm_max, Va_max, Pg_max, Qg_max]).tolist()
```

### 5. Create and call solver

```python
nlp = {"x": x, "f": obj, "g": g}
opts = {
    "ipopt.print_level": 0,
    "ipopt.max_iter": 2000,
    "ipopt.tol": 1e-7,
    "ipopt.acceptable_tol": 1e-5,
    "ipopt.mu_strategy": "adaptive",
    "print_time": False,
}
solver = ca.nlpsol("solver", "ipopt", nlp, opts)
sol = solver(x0=x0, lbx=lbx, ubx=ubx, lbg=lbg, ubg=ubg)
x_opt = np.array(sol["x"]).flatten()
obj_val = float(sol["f"])
```

## Initialization

Use multiple initializations; keep the best feasible solution:

```python
initializations = [x0_from_data, x0_flat_start]
best_sol = None
for x0 in initializations:
    try:
        sol = solver(x0=x0, lbx=lbx, ubx=ubx, lbg=lbg, ubg=ubg)
        if best_sol is None or float(sol["f"]) < float(best_sol["f"]):
            best_sol = sol
    except Exception:
        continue
```

Strategies: data-derived (clipped to bounds), flat start (Vm=1.0, Va=0.0), enforce reference angle = 0.

## Extracting solutions

```python
x_opt = np.array(sol["x"]).flatten()
Vm_sol = x_opt[:n_bus]
Va_sol = x_opt[n_bus:2*n_bus]
Pg_sol = x_opt[2*n_bus:2*n_bus+n_gen]
Qg_sol = x_opt[2*n_bus+n_gen:]
```

## Dependencies

```bash
apt-get update -qq && apt-get install -y -qq libgfortran5
pip3 install --break-system-packages numpy==1.26.4 casadi==3.6.7
```

If `ModuleNotFoundError: No module named 'casadi'`:
```bash
pip3 install --break-system-packages --no-cache-dir casadi==3.6.7
```

## Power systems patterns

### Per-unit scaling

```python
baseMVA = 100.0
Pg_pu = Pg_MW / baseMVA
Pg_MW = Pg_pu * baseMVA
```

### Bus ID mapping

```python
bus_id_to_idx = {int(bus[i, 0]): i for i in range(n_bus)}
gen_bus_idx = bus_id_to_idx[int(gen_row[0])]
```

### Aggregating per-bus quantities

```python
Pg_bus = [ca.MX(0) for _ in range(n_bus)]
for k in range(n_gen):
    bus_idx = gen_bus_idx[k]
    Pg_bus[bus_idx] += Pg[k]
```

---

---
name: power-flow-data
description: "Power system network data formats and topology. Use when parsing bus, generator, and branch data for power flow analysis."
---

# Power Flow Data Guide

Network data follows the MATPOWER format from the PGLib-OPF benchmark library.

## ⚠️ Handling Large Network Files

**Never read line-by-line** with `sed` or `head`. Use Python's JSON parser:

```python
import json
with open('network.json') as f:
    data = json.load(f)
print(f"Buses: {len(data['bus'])}")
print(f"Generators: {len(data['gen'])}")
print(f"Branches: {len(data['branch'])}")
print(f"Total load: {sum(b[2] for b in data['bus']):.1f} MW")
```

## Bus Types

| Type | Code | Specified | Solved | Description |
|------|------|-----------|--------|-------------|
| Slack | 3 | V, θ=0 | P, Q | Reference bus, balances power |
| PV | 2 | P, V | Q, θ | Generator bus with voltage control |
| PQ | 1 | P, Q | V, θ | Load bus |

## Loading Network Data

```python
import json
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

| Field | Type | Description |
|-------|------|-------------|
| reserve_capacity | array | Maximum reserve each generator can provide (MW) |
| reserve_requirement | float | Minimum total system reserves required (MW) |

```python
reserve_capacity = np.array(data['reserve_capacity'])
reserve_requirement = data['reserve_requirement']
```

## Bus Number Mapping

Bus numbers may not be contiguous. Always create a mapping:

```python
bus_num_to_idx = {int(buses[i, 0]): i for i in range(n_bus)}
gen_bus = [bus_num_to_idx[int(g[0])] for g in gens]
```

## Identifying Bus Connections

```python
def get_generators_at_bus(gens, bus_idx, bus_num_to_idx):
    gen_indices = []
    for i, gen in enumerate(gens):
        if bus_num_to_idx[int(gen[0])] == bus_idx:
            gen_indices.append(i)
    return gen_indices

def find_slack_bus(buses):
    for i, bus in enumerate(buses):
        if bus[1] == 3:
            return i
    return None
```

## Branch Data Interpretation

```python
def get_branch_info(branch, bus_num_to_idx):
    return {
        'from_bus': bus_num_to_idx[int(branch[0])],
        'to_bus': bus_num_to_idx[int(branch[1])],
        'resistance': branch[2],
        'reactance': branch[3],
        'susceptance': branch[4],
        'rating': branch[5],
        'in_service': branch[10] == 1
    }
```

## Computing Total Load

```python
def total_load(buses):
    return sum(bus[2] for bus in buses)  # Column 2 = Pd