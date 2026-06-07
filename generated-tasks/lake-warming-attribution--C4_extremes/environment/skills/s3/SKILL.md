---
name: s1
description: "Environmental analysis: trend, PCA, contribution."
license: MIT
---

# Analysis

**Trend**: `pymannkendall` — `r=mk.original_test(values)`, `slope=round(r.slope,2)`

**Drivers**: Heat(AirTemp,Shortwave,Longwave,NetRadiation), Flow(Precip,Inflow,Outflow), Wind(WindSpeed), Human(DevelopedArea,AgricultureArea). `NetRadiation=Longwave+Shortwave`

**PCA**: `FactorAnalyzer(n_factors=4,rotation='varimax').fit(StandardScaler().fit_transform(X))`

**Contribution**: `contribution_i=(full_r2-calc_r2(scores_without_i,y))*100` where `calc_r2` uses `LinearRegression`

BOM: `encoding='utf-8-sig'` or `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data`
