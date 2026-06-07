---
name: s1
description: "Trend, PCA, drivers, contribution for environmental data."
license: MIT
---

# Trend Analysis

Sen's slope + Mann-Kendall:
```python
import pymannkendall as mk
result = mk.original_test(values)
slope = round(result.slope, 2)
```

# Driver Classification

- **Heat**: AirTemp, Shortwave, Longwave, NetRadiation
- **Flow**: Precip, Inflow, Outflow
- **Wind**: WindSpeed
- **Human**: DevelopedArea, AgricultureArea

Derived: `NetRadiation = Longwave + Shortwave`

# PCA with Varimax Rotation

```python
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer
X_scaled = StandardScaler().fit_transform(X)
fa = FactorAnalyzer(n_factors=4, rotation='varimax')
scores = fa.transform(X_scaled)
```

# Contribution

Leave-one-out R² decomposition:
```python
from sklearn.linear_model import LinearRegression
contribution_i = (full_r2 - calc_r2(scores_without_i, y)) * 100
```

# Production Notes

- BOM: `encoding='utf-8-sig'` or `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data`
- Permissions: `os.chmod('/root/output', 0o755)`