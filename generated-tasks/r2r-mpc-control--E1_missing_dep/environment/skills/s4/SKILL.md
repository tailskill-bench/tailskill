---
name: s1
description: "R2R MPC control: finite-horizon LQR, integral action design, MPC horizon tuning, and state-space linearization."
---

# Finite-Horizon LQR for MPC

## Backward Riccati Recursion

Initialize P_N = Q. For k = N-1 down to 0:
```
K_k = inv(R + B'P_{k+1}B) @ B'P_{k+1}A
P_k = Q + A'P_{k+1}(A - B @ K_k)
```

## Forward Simulation

```
u_k = -K_k @ x_k
x_{k+1} = A @ x_k + B @ u_k
```

## MPC Application

At each timestep: measure x → solve finite-horizon LQR → apply u_0 → repeat.

---
name: integral-action-design
description: Adding integral action to MPC for offset-free tension tracking.
---

# Integral Action for Offset-Free Control

```python
u_I = gamma * u_I - c_I * dt * (T - T_ref)
u_total = u_mpc + u_I
```

- gamma: decay factor (0.9–0.99)
- c_I: integral gain (0.1–0.5 for web systems)

Anti-windup: `u_I = np.clip(u_I, -max_integral, max_integral)`

---
name: mpc-horizon-tuning
description: Selecting MPC prediction horizon and cost matrices for web handling.
---

# MPC Tuning for Tension Control

## Prediction Horizon

N ≈ 2–3× settling_time / dt. For R2R with dt=0.01s: **N = 5–15**.

## Cost Matrices

```python
Q_tension = 100 / T_ref**2
Q_velocity = 0.1 / v_ref**2
Q = diag([Q_tension * 6, Q_velocity * 6])
R = 0.01 - 0.1 * eye(n_u)
```

Terminal cost: `P = solve_continuous_are(A, B, Q, R)`

---
name: state-space-linearization
description: Linearizing nonlinear dynamics around operating points for control design.
---

# State-Space Linearization

Linearize dx/dt = f(x,u) around (x_ref, u_ref):
```
A = ∂f/∂x |_{x_ref}   (n×n)
B = ∂f/∂u |_{x_ref}   (n×m)
```

## Discretization

Euler: `A_d = I + dt*A_c`, `B_d = dt*B_c`

Matrix exponential: `A_d = expm(A_c*dt)`, `B_d = inv(A_c) @ (A_d - I) @ B_c`

## R2R Key Partials

```python
∂(dT_i/dt)/∂T_i = -v_i / L
∂(dT_i/dt)/∂v_i = EA/L - T_i/L
∂(dv_i/dt)/∂T_i = -R**2/J
∂(dv_i/dt)/∂u_i = R/J
```

Re-linearize if operating point changes significantly.

## Dependencies

```bash
pip3 install --break-system-packages numpy==1.26.4 scipy==1.13.0