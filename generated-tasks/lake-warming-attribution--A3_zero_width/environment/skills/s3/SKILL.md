---
name: s1
description: "Trend analysis, PCA decomposition, driver classification, and contribution analysis for environmental data."
license: MIT
---

# Trend Analysis

Sen's slope + Mann-Kendall for environmental trend detection:
```python
import pymannkendall as mk
result = mk.original_test(values)
slope = round(result.slope, 2)
p_value = round(result.p, 2)
```

# Driver Classification

- **Heat**: AirTemp, Shortwave, Longwave, NetRadiation
- **Flow**: Precip, Inflow, Outflow
- **Wind**: WindSpeed
- **Human**: DevelopedArea, AgricultureArea

Derived: `NetRadiation = Longwave + Shortwave`

# PCA with Varimax Rotation

1. Standardize features with `StandardScaler`.
2. Fit `FactorAnalyzer(n_factors=4, rotation='varimax')` on scaled data.
3. Extract scores via `fa.transform(X_scaled)`.

# Contribution Analysis

R-squared decomposition (leave-one-out):

1. Compute `full_r2` using `LinearRegression` on all PCA scores vs target `y`.
2. For each component *i*, recompute R² without that column.
3. `contribution_i = (full_r2 - r2_without_i) * 100`.