---
name: s1
description: Detrend macroeconomic time series into trend and cyclical components using the HP filter, log transformations, and correlation analysis.
---

# Time Series Detrending for Macroeconomic Analysis

## The Hodrick-Prescott (HP) Filter

Minimizes:

$$\sum_{t=1}^{T}(y_t - \tau_t)^2 + \lambda \sum_{t=2}^{T-1}[(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1})]^2$$

### Choosing Lambda (λ)

**Critical**: λ depends on data frequency.

| Data Frequency | λ |
|----------------|---------------|
| Annual         | **100**       |
| Quarterly      | **1600**      |
| Monthly        | **14400**     |

**Warning**: Using λ=1600 for annual data produces an overly smooth trend that misses cyclical dynamics.

### Python Implementation

```python
from statsmodels.tsa.filters.hp_filter import hpfilter
cycle, trend = hpfilter(data, lamb=100)       # annual
cycle_q, trend_q = hpfilter(quarterly_data, lamb=1600)  # quarterly
```

**Note**: The parameter is `lamb` (not `lambda`, which is a Python keyword).

## Log Transformation for Growth Series

For macroeconomic aggregates (GDP, consumption, investment), apply natural log **before** filtering. The cyclical component then represents percentage deviations from trend (e.g., cycle = 0.02 → 2% above trend).

```python
import numpy as np
from statsmodels.tsa.filters.hp_filter import hpfilter
log_series = np.log(real_series)
cycle, trend = hpfilter(log_series, lamb=100)
```

### When NOT to Use Logs

- Series that can be negative (net exports, current account)
- Series already expressed as rates or percentages
- Series with zeros

## Loading Data Files

Handle UTF-8 BOM markers:

```python
df = pd.read_csv('data.csv', encoding='utf-8-sig')
```

Strip BOM markers from affected files:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/CPI.csv
```

This script scans CSV, TXT, and JSON files and strips BOM markers in place.

## Complete Workflow for Detrending

1. **Load and clean data**: Handle missing values, ensure proper time ordering
2. **Convert to real terms**: Deflate nominal values using appropriate price index
3. **Apply log transformation**: For positive level variables
4. **Apply HP filter**: Use appropriate λ for data frequency
5. **Analyze cyclical component**: Compute correlations, volatilities, etc.

### Example: Business Cycle Correlation

```python
import pandas as pd, numpy as np
from statsmodels.tsa.filters.hp_filter import hpfilter

ln_consumption = np.log(real_consumption)
ln_investment = np.log(real_investment)
cycle_c, _ = hpfilter(ln_consumption, lamb=100)
cycle_i, _ = hpfilter(ln_investment, lamb=100)
correlation = np.corrcoef(cycle_c, cycle_i)[0, 1]
print(f"Business cycle correlation: {correlation:.4f}")
```

## Dependencies

```bash
pip install statsmodels pandas numpy openpyxl xlrd
```

The HP filter is in `statsmodels.tsa.filters.hp_filter`.