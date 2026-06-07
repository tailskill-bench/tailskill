---
name: s1
description: "Environmental trend analysis, PCA decomposition, driver classification, and contribution analysis."
license: MIT
---

Sen's slope + Mann-Kendall:
```python
import pymannkendall as mk
result = mk.original_test(values)
slope = round(result.slope, 2)
p_value = round(result.p, 2)
```

**Drivers**: Heat (AirTemp, Shortwave, Longwave, NetRadiation), Flow (Precip, Inflow, Outflow), Wind (WindSpeed), Human (DevelopedArea, AgricultureArea). Derived: `NetRadiation = Longwave + Shortwave`.

PCA: Standardize with `StandardScaler`, fit `FactorAnalyzer(n_factors=4, rotation='varimax')`, extract scores via `fa.transform(X_scaled)`.

R² decomposition (leave-one-out): Compute `full_r2` using `LinearRegression` on all PCA scores vs target `y`. For each component *i*, recompute R² without that column. `contribution_i = (full_r2 - r2_without_i) * 100`.