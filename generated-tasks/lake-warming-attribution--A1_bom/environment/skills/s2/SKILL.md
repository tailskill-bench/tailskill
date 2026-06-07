---
name: s1
description: "Environmental trend analysis, PCA, driver classification, contribution analysis."
license: MIT
---

# Analysis Workflow

**Trend Detection** (Sen's slope + Mann-Kendall):
```python
import pymannkendall as mk
r = mk.original_test(values)
slope = round(r.slope, 2)
p_value = round(r.p, 2)
```

**Driver Categories**:
- Heat: AirTemp, Shortwave, Longwave, NetRadiation
- Flow: Precip, Inflow, Outflow
- Wind: WindSpeed
- Human: DevelopedArea, AgricultureArea

Derived: `NetRadiation = Longwave + Shortwave`

**PCA** (Varimax):
```python
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer
fa = FactorAnalyzer(n_factors=4, rotation='varimax')
fa.fit(StandardScaler().fit_transform(X))
scores = fa.transform(StandardScaler().fit_transform(X))
```

**Contribution** (R² leave-one-out):
```python
def calc_r2(X, y):
    from sklearn.linear_model import LinearRegression
    m = LinearRegression().fit(X, y)
    return 1 - np.sum((y - m.predict(X))**2) / np.sum((y - np.mean(y))**2)
contribution_i = (full_r2 - calc_r2(scores_without_i, y)) * 100
```

**BOM**: Use `encoding='utf-8-sig'` or `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data`.
