---
name: s1
description: "R2R MPC control: finite-horizon LQR, integral action design, MPC horizon tuning, and state-space linearization."
---

# Finite-Horizon LQR for MPC

## Problem Formulation

Minimize cost over horizon N:
```
J = Σ(k=0 to N-1) [x'Qx + u'Ru] + x_N' P x_N
```

## Backward Riccati Recursion

Initialize: P_N = Q (or LQR solution for stability)

For k = N-1 down to 0:
```python
K_k = inv(R + B'P_{k+1}B) @ B'P_{k+1}A
P_k = Q + A'P_{k+1}(A - B @ K_k)
```

## Forward Simulation

Starting from x_0:
```python
u_k = -K_k @ x_k
x_{k+1} = A @ x_k + B @ u_k
```

## Python Implementation

```python
def finite_horizon_lqr(A, B, Q, R, N, x0):
    nx, nu = A.shape[0], B.shape[1]
    K = np.zeros((nu, nx, N))
    P = Q.copy()
    for k in range(N-1, -1, -1):
        K[:,:,k] = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
        P = Q + A.T @ P @ (A - B @ K[:,:,k])
    return -K[:,:,0] @ x0
```

## MPC Application

At each timestep:
1. Measure current state x
2. Solve finite-horizon LQR from x
3. Apply first control u_0
4. Repeat next timestep

---

---
name: integral-action-design
description: Adding integral action to MPC for offset-free tension tracking.
---

# Integral Action for Offset-Free Control

## Implementation

```python
u_I = gamma * u_I - c_I * dt * (T - T_ref)
u_total = u_mpc + u_I
```

Where:
- u_I: Integral control term
- gamma: Decay factor (0.9-0.99)
- c_I: Integral gain (0.1-0.5 for web systems)
- dt: Timestep

## Anti-Windup

Limit integral term to prevent windup during saturation:
```python
u_I = np.clip(u_I, -max_integral, max_integral)
```

## For R2R Systems

Apply integral action per tension section:
```python
for i in range(num_sections):
    u_I[i] = gamma * u_I[i] - c_I * dt * (T[i] - T_ref[i])
```

---

---
name: mpc-horizon-tuning
description: Selecting MPC prediction horizon and cost matrices for web handling.
---

# MPC Tuning for Tension Control

## Prediction Horizon Selection

- Rule of thumb: N ≈ 2-3× settling time / dt
- For R2R systems with dt=0.01s: **N = 5-15** typical

## Cost Matrix Design

**State cost Q**: Emphasize tension tracking
```python
Q_tension = 100 / T_ref²
Q_velocity = 0.1 / v_ref²
Q = diag([Q_tension × 6, Q_velocity × 6])
```

**Control cost R**: Penalize actuator effort
```python
R = 0.01-0.1 × eye(n_u)
```

## Terminal Cost

Use LQR solution for terminal cost to guarantee stability:
```python
P = solve_continuous_are(A, B, Q, R)
```

---

---
name: state-space-linearization
description: Linearizing nonlinear dynamics around operating points for control design.
---

# State-Space Linearization

## Jacobian Computation

For nonlinear dynamics dx/dt = f(x, u), linearize around (x_ref, u_ref):

```
A = ∂f/∂x |_{x_ref}  (n×n matrix)
B = ∂f/∂u |_{x_ref}  (n×m matrix)
```

## Discretization

**Euler method** (simple, first-order accurate):
```python
A_d = I + dt * A_c
B_d = dt * B_c
```

**Matrix exponential** (exact for LTI):
```python
A_d = expm(A_c * dt)
B_d = inv(A_c) @ (A_d - I) @ B_c
```

## For R2R Systems

Key partial derivatives:

```python
∂(dT_i/dt)/∂T_i = -v_i / L
∂(dT_i/dt)/∂v_i = EA/L - T_i/L
∂(dv_i/dt)/∂T_i = -R²/J
∂(dv_i/dt)/∂u_i = R/J
```

- Linearize around the reference operating point
- Update linearization if operating point changes significantly

## Dependencies

```bash
pip3 install --break-system-packages numpy==1.26.4 scipy==1.13.0
```

If `ModuleNotFoundError: No module named 'scipy'`:
```bash
pip3 install --break-system-packages --no-cache-dir scipy==1.13.0