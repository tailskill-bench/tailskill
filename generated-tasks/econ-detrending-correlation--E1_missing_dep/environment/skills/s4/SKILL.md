---
name: s1
description: Detrend macroeconomic time series using HP filter, log transforms, and business cycle correlation analysis.
---

# Time Series Detrending for Macroeconomic Analysis

## HP Filter

Minimizes: $\sum_{t=1}^{T}(y_t - \tau_t)^2 + \lambda \sum_{t=2}^{T-1}[(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1})]^2$

**λ by frequency**: Annual=**100**, Quarterly=**1600**, Monthly=**14400**. Wrong λ (e.g., 1600 for annual) over-smooths and misses cycles.

```python
from statsmodels.tsa.filters.hp_filter import hpfilter
import numpy as np

cycle, trend = hpfilter(data, lamb=100)       # annual data
cycle_q, trend_q = hpfilter(quarterly_data, lamb=1600)  # quarterly data
```

Parameter is `lamb` (not `lambda`, a Python keyword).

## Log Transformation

Apply `np.log()` **before** filtering for positive aggregates (GDP, consumption, investment). This converts multiplicative changes to additive log differences, stabilizes variance, and makes the cyclical component represent percentage deviations (cycle=0.02 → 2% above trend).

**Do NOT log**: negative series (net exports), rates/percentages, or series with zeros.

```python
import numpy as np
from statsmodels.tsa.filters.hp_filter import hpfilter

log_series = np.log(real_series)
cycle, trend = hpfilter(log_series, lamb=100)
```

## Workflow

1. Load/clean data, handle missing values, ensure time ordering
2. Convert to real terms (deflate with price index)
3. Log-transform positive level variables only
4. HP filter with correct λ for frequency
5. Analyze cyclical component (correlations, volatilities)

### Business Cycle Correlation Example

```python
import pandas as pd
import numpy as np
from statsmodels.tsa.filters.hp_filter import hpfilter

real_consumption = pd.Series(...)  # Real consumption expenditure
real_investment = pd.Series(...)   # Real fixed investment

ln_consumption = np.log(real_consumption)
ln_investment = np.log(real_investment)

cycle_c, trend_c = hpfilter(ln_consumption, lamb=100)
cycle_i, trend_i = hpfilter(ln_investment, lamb=100)

correlation = np.corrcoef(cycle_c, cycle_i)[0, 1]
print(f"Business cycle correlation: {correlation:.4f}")
```

## Dependencies

```bash
pip install statsmodels pandas numpy openpyxl xlrd
```

HP filter location: `statsmodels.tsa.filters.hp_filter`.