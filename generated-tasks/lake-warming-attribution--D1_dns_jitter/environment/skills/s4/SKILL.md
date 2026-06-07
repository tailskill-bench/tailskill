---
name: s1
description: "Environmental trend, PCA, driver, contribution analysis."
---

**Trend**: Sen's slope + Mann-Kendall:
```python
import pymannkendall as mk
result = mk.original_test(values)
slope = round(result.slope, 2)
p_value = round(result.p, 2)
```

**Drivers**: Heat (AirTemp, Shortwave, Longwave, NetRadiation), Flow (Precip, Inflow, Outflow), Wind (WindSpeed), Human (DevelopedArea, AgricultureArea). `NetRadiation = Longwave + Shortwave`

**PCA** (varimax):
```python
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
fa = FactorAnalyzer(n_factors=4, rotation='varimax')
fa.fit(X_scaled)
scores = fa.transform(X_scaled)
```

**Contribution** (R² leave-one-out):
```python
def calc_r2(X, y):
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    return 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)

contribution_i = (full_r2 - calc_r2(scores_without_i, y)) * 100
```

**CSV BOM**: Use `encoding='utf-8-sig'` or `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data`.