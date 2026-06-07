---
name: s1
description: Complete guide for GLM lake temperature simulation, calibration, and output processing.
license: MIT
---

# GLM Basics Guide

## Running GLM
```bash
cd /root
glm
```

GLM reads `glm3.nml` in the current directory and produces output in `output/output.nc`.

If `PermissionError` occurs when GLM writes to `output/`:
```bash
chmod 755 /root/output
```
Or use the helper script:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/output/output.nc
```

## Input File Structure

| File | Description |
|------|-------------|
| `glm3.nml` | Main configuration file (Fortran namelist format) |
| `bcs/*.csv` | Boundary condition files (meteorology, inflows, outflows) |

## Configuration File Format

`glm3.nml` uses Fortran namelist format with multiple sections:
```fortran
&glm_setup
   sim_name = 'LakeName'
   max_layers = 500
/
&light
   Kw = 0.3
/
&mixing
   coef_mix_hyp = 0.5
/
&meteorology
   meteo_fl = 'bcs/meteo.csv'
   wind_factor = 1
   lw_factor = 1
   ch = 0.0013
/
&inflow
   inflow_fl = 'bcs/inflow1.csv','bcs/inflow2.csv'
/
&outflow
   outflow_fl = 'bcs/outflow.csv'
/
```

## Modifying Parameters with Python
```python
import re

def modify_nml(nml_path, params):
    with open(nml_path, 'r') as f:
        content = f.read()
    for param, value in params.items():
        pattern = rf"({param}\s*=\s*)[\d\.\-e]+"
        replacement = rf"\g<1>{value}"
        content = re.sub(pattern, replacement, content)
    with open(nml_path, 'w') as f:
        f.write(content)

# Example usage
modify_nml('glm3.nml', {'Kw': 0.25, 'wind_factor': 0.9})
```

---

# GLM Calibration Guide

## Key Calibration Parameters

| Parameter | Section | Description | Default | Range |
|-----------|---------|-------------|---------|-------|
| `Kw` | `&light` | Light extinction coefficient (m⁻¹) | 0.3 | 0.1 - 0.5 |
| `coef_mix_hyp` | `&mixing` | Hypolimnetic mixing coefficient | 0.5 | 0.3 - 0.7 |
| `wind_factor` | `&meteorology` | Wind speed scaling factor | 1.0 | 0.7 - 1.3 |
| `lw_factor` | `&meteorology` | Longwave radiation scaling | 1.0 | 0.7 - 1.3 |
| `ch` | `&meteorology` | Sensible heat transfer coefficient | 0.0013 | 0.0005 - 0.002 |

## Parameter Effects

| Parameter | Increase Effect | Decrease Effect |
|-----------|-----------------|-----------------|
| `Kw` | Less light penetration, cooler deep water | More light penetration, warmer deep water |
| `coef_mix_hyp` | More deep mixing, weaker stratification | Less mixing, stronger stratification |
| `wind_factor` | More surface mixing | Less surface mixing |
| `lw_factor` | More heat input | Less heat input |
| `ch` | More sensible heat exchange | Less heat exchange |

## Calibration with Optimization
```python
from scipy.optimize import minimize

def objective(x):
    Kw, coef_mix_hyp, wind_factor, lw_factor, ch = x

    params = {
        'Kw': round(Kw, 4),
        'coef_mix_hyp': round(coef_mix_hyp, 4),
        'wind_factor': round(wind_factor, 4),
        'lw_factor': round(lw_factor, 4),
        'ch': round(ch, 6)
    }
    modify_nml('glm3.nml', params)

    subprocess.run(['glm'], capture_output=True)

    rmse = calculate_rmse(sim_df, obs_df)
    return rmse

x0 = [0.3, 0.5, 1.0, 1.0, 0.0013]

result = minimize(
    objective,
    x0,
    method='Nelder-Mead',
    options={'maxiter': 150}
)
```

## Manual Calibration Strategy

1. Start with default parameters, run GLM, calculate RMSE
2. Adjust one parameter at a time
3. If surface too warm → increase `wind_factor`
4. If deep water too warm → increase `Kw`
5. If stratification too weak → decrease `coef_mix_hyp`
6. Iterate until RMSE < 2.0°C

---

# GLM Output Guide

## Output File

Results are in `output/output.nc`:

| Variable | Description | Shape |
|----------|-------------|-------|
| `time` | Hours since simulation start | (n_times,) |
| `z` | Height from lake bottom (not depth!) | (n_times, n_layers, 1, 1) |
| `temp` | Water temperature (°C) | (n_times, n_layers, 1, 1) |

If GLM fails silently (no output generated), check directory permissions:
```bash
ls -la /root/output/
# If dr-xr-xr-x, fix with:
chmod 755 /root/output
```

## Coordinate Conversion

**Important**: GLM `z` is height from lake bottom, not depth from surface.
```python
# Set LAKE_DEPTH based on lake_depth in &init_profiles section of glm3.nml
LAKE_DEPTH = <lake_depth_from_nml>
depth_from_surface = LAKE_DEPTH - z
```

## Complete Output Processing
```python
from netCDF4 import Dataset
import numpy as np
import pandas as pd
from datetime import datetime

def read_glm_output(nc_path, lake_depth):
    nc = Dataset(nc_path, 'r')
    time = nc.variables['time'][:]
    z = nc.variables['z'][:]
    temp = nc.variables['temp'][:]
    start_date = datetime(2009, 1, 1, 12, 0, 0)

    records = []
    for t_idx in range(len(time)):
        hours = float(time[t_idx])
        date = pd.Timestamp(start_date) + pd.Timedelta(hours=hours)
        heights = z[t_idx, :, 0, 0]
        temps = temp[t_idx, :, 0, 0]

        for d_idx in range(len(heights)):
            h_val = heights[d_idx]
            t_val = temps[d_idx]
            if not np.ma.is_masked(h_val) and not np.ma.is_masked(t_val):
                depth = lake_depth - float(h_val)
                if 0 <= depth <= lake_depth:
                    records.append({
                        'datetime': date,
                        'depth': round(depth),
                        'temp_sim': float(t_val)
                    })
    nc.close()

    df = pd.DataFrame(records)
    df = df.groupby(['datetime', 'depth']).agg({'temp_sim': 'mean'}).reset_index()
    return df
```

## Reading Observations
```python
def read_observations(obs_path):
    df = pd.read_csv(obs_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['depth'] = df['depth'].round().astype(int)
    df = df.rename(columns={'temp': 'temp_obs'})
    return df[['datetime', 'depth', 'temp_obs']]
```

## Calculating RMSE
```python
def calculate_rmse(sim_df, obs_df):
    merged = pd.merge(obs_df, sim_df, on=['datetime', 'depth'], how='inner')
    if len(merged) == 0:
        return 999.0
    rmse = np.sqrt(np.mean((merged['temp_sim'] - merged['temp_obs'])**2))
    return rmse

# Usage: get lake_depth from glm3.nml &init_profiles section
sim_df = read_glm_output('output/output.nc', lake_depth=25)
obs_df = read_observations('field_temp_oxy.csv')
rmse = calculate_rmse(sim_df, obs_df)
print(f"RMSE: {rmse:.2f}C")