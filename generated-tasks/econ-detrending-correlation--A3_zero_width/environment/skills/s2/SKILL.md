---
name: s1
description: Tools and techniques for detrending time series data in macroeconomic analysis. Use when working with economic time series that need to be decomposed into trend and cyclical components. Covers HP filter, log transformations for growth series, and correlation analysis of business cycles.
---

# Time Series Detrending for Macroeconomic Analysis

Decompose economic time series into trend and cyclical components for business cycle analysis.

## The Hodrick-Prescott (HP) Filter

The HP filter decomposes a time series $y_t$ into trend $\tau_t$ and cyclical components by minimizing:

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
import numpy as np

cycle, trend = hpfilter(data, lamb=100)  # Annual data
cycle_q, trend_q = hpfilter(quarterly_data, lamb=1600)
```

**Note**: The parameter is `lamb` (not `lambda`, a Python keyword).

## Log Transformation for Growth Series

Apply the natural logarithm **before** filtering for macroeconomic aggregates (GDP, consumption, investment). This converts percentage changes to log differences, stabilizes variance, and makes the cyclical component represent percentage deviations from trend.

```python
import numpy as np
from statsmodels.tsa.filters.hp_filter import hpfilter

log_series = np.log(real_series)
cycle, trend = hpfilter(log_series, lamb=100)
# cycle = 0.02 means 2% above trend
```

**Do not use logs** for: series that can be negative (net exports), series already expressed as rates/percentages, or series with zeros.

## Loading Data Files

Clean invisible Unicode characters (U+200B, U+200C, U+200D) from numeric fields that cause float parsing errors:

```python
import unicodedata
cleaned = ''.join(c for c in value if unicodedata.category(c) not in ('Cf', 'Cc'))
```

Or run the auxiliary script to clean XLSX/CSV files before processing:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/CPI.xlsx
```
This script opens XLSX files with openpyxl, strips invisible characters from cell values, and converts cleaned strings back to numeric types.

## Complete Workflow for Detrending

1. **Load and clean data**: Handle missing values, ensure proper time ordering
2. **Convert to real terms**: Deflate nominal values using appropriate price index
3. **Apply log transformation**: For positive level variables
4. **Apply HP filter**: Use appropriate λ for data frequency
5. **Analyze cyclical component**: Compute correlations, volatilities, etc.

### Example: Business Cycle Correlation

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
```

The HP filter is in `statsmodels.tsa.filters.hp_filter`.