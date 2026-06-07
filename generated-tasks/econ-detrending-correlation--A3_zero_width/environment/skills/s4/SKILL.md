---
name: s1
description: Detrend macroeconomic time series into trend/cyclical components using HP filter with log transformations and business cycle correlation analysis.
---

# Time Series Detrending

## HP Filter

Decomposes $y_t$ into trend $\tau_t$ and cyclical components:

$$\sum_{t=1}^{T}(y_t - \tau_t)^2 + \lambda \sum_{t=2}^{T-1}[(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1})]^2$$

**λ Selection**: Annual=**100**, Quarterly=**1600**, Monthly=**14400**. Wrong λ produces misleading trends.

```python
from statsmodels.tsa.filters.hp_filter import hpfilter
import numpy as np

cycle, trend = hpfilter(data, lamb=100)  # Annual data
cycle_q, trend_q = hpfilter(quarterly_data, lamb=1600)
```

Parameter is `lamb` (not `lambda`, a Python keyword).

## Log Transformation

Apply `np.log()` **before** filtering for aggregates (GDP, consumption, investment). Cyclical component = percentage deviations from trend.

```python
import numpy as np
from statsmodels.tsa.filters.hp_filter import hpfilter

log_series = np.log(real_series)
cycle, trend = hpfilter(log_series, lamb=100)
# cycle = 0.02 means 2% above trend
```

**Don't log**: negative series (net exports), rates/percentages, series with zeros.

## Data Cleaning

Strip invisible Unicode (U+200B, U+200C, U+200D) from numeric fields:

```python
import unicodedata
cleaned = ''.join(c for c in value if unicodedata.category(c) not in ('Cf', 'Cc'))
```

Or: `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/CPI.xlsx`

## Workflow

1. Load/clean data, ensure time ordering
2. Convert to real terms (deflate nominal values)
3. Log-transform positive level variables
4. HP filter with correct λ
5. Analyze cyclical component

### Business Cycle Correlation Example

```python
import pandas as pd
import numpy as np
from statsmodels.tsa.filters.hp_filter import hpfilter

real_consumption = pd.Series(...)
real_investment = pd.Series(...)

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