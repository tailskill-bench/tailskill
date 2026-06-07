---
name: s1
description: "Exoplanet detection period analysis: light curve preprocessing, transit detection (BLS/TLS), Lomb-Scargle periodograms, and exoplanet workflow guidance."
---

# Box Least Squares (BLS) Periodogram

BLS models a transit as a periodic box shape and finds the period, duration, depth, and reference time that best fit the data.

## Installation

```bash
pip install astropy
```

## Basic Usage

```python
import numpy as np
import astropy.units as u
from astropy.timeseries import BoxLeastSquares

t = time * u.day
y = flux
dy = flux_err

model = BoxLeastSquares(t, y, dy=dy)
duration = 0.2 * u.day
periodogram = model.autopower(duration)

best_period = periodogram.period[np.argmax(periodogram.power)]
print(f"Best period: {best_period:.5f}")
```

- **autopower**: Automatically determines appropriate period grid. Recommended for initial searches.
  ```python
  durations = [0.1, 0.15, 0.2, 0.25] * u.day
  periodogram = model.autopower(durations)
  ```
- **power**: Requires a custom period grid for targeted control.
  ```python
  periods = np.linspace(2.0, 10.0, 1000) * u.day
  periodogram = model.power(periods, duration)
  ```
  **Warning**: Period grid quality matters! Too coarse and you'll miss the true period.

## Objective Functions

- **Log Likelihood** (default): Maximizes the statistical likelihood of the model fit.
  ```python
  periodogram = model.autopower(0.2 * u.day, objective='likelihood')
  ```
- **Signal-to-Noise Ratio (SNR)**: Uses the SNR with which the transit depth is measured. Can improve reliability in the presence of correlated noise.
  ```python
  periodogram = model.autopower(0.2 * u.day, objective='snr')
  ```

## Peak Statistics for Validation

Use `compute_stats()` to calculate detailed statistics about a candidate transit:

```python
max_power_idx = np.argmax(periodogram.power)
stats = model.compute_stats(
    periodogram.period[max_power_idx],
    periodogram.duration[max_power_idx],
    periodogram.transit_time[max_power_idx]
)

print(f"Depth: {stats['depth']:.6f}")
print(f"Depth uncertainty: {stats['depth_err']:.6f}")
print(f"SNR: {stats['depth_snr']:.2f}")
print(f"Odd/Even mismatch: {stats['depth_odd'] - stats['depth_even']:.6f}")
print(f"Number of transits: {stats['transit_count']}")

if abs(stats['depth_odd'] - stats['depth_even']) > 3 * stats['depth_err']:
    print("Warning: Significant odd-even mismatch - may not be planetary")
```

**Validation criteria:**
- **High depth SNR (>7)**: Strong signal
- **Low odd-even mismatch**: Consistent transit depth
- **Multiple transits observed**: More reliable
- **Reasonable duration**: Not too long or too short for orbit

## Phase-Folded Light Curve

After finding a candidate, phase-fold to visualize the transit:

```python
best_period = periodogram.period[max_power_idx]
best_t0 = periodogram.transit_time[max_power_idx]
phase = ((time.value - best_t0.value) % best_period.value) / best_period.value
plt.plot(phase, flux, '.')
plt.xlabel('Phase')
plt.ylabel('Flux')
plt.show()
```

## BLS vs Transit Least Squares (TLS)

- **BLS**: Built into Astropy. Fast for targeted searches. Simpler transit model (box shape). May be less sensitive to grazing transits.
- **TLS**: More sophisticated transit models. Generally more sensitive. Better handles grazing transits. Requires separate package (`pip install transitleastsquares`). Slower for very long time series.

---

# Exoplanet Detection Workflows

## Key Stages

1. **Data Loading**: Understand your data format, columns, time system
2. **Quality Control**: Filter bad data points using quality flags
3. **Preprocessing**: Remove noise while preserving planetary signals
4. **Period Search**: Choose appropriate algorithm for signal type
5. **Validation**: Verify candidate is real, not artifact
6. **Refinement**: Improve period precision if candidate is strong

### Which period search algorithm?

- **TLS**: Best for transit-shaped signals (box-like dips)
- **Lomb-Scargle**: Good for any periodic signal, fast exploration
- **BLS**: Alternative to TLS, built into Astropy

## Signal Validation

### Strong Candidate (TLS)
- **SDE > 9**: Very strong candidate
- **SDE > 6**: Strong candidate
- **SNR > 7**: Reliable signal

### Warning Signs
- **Low SDE (<6)**: Weak signal, may be false positive
- **Period exactly half/double expected**: Check for aliasing
- **High odd-even mismatch**: May not be planetary transit

### Validation Checklist
- Check SDE, SNR against thresholds
- Phase-fold data at candidate period and visually inspect
- Verify odd-even transit depth consistency
- Confirm multiple transits observed

## Multi-Planet Systems

1. Find first candidate
2. Mask out first planet's transits
3. Search remaining data for additional periods
4. Repeat until no more significant signals

See Transit Least Squares documentation for `transit_mask` function.

## Expected Transit Depths

- **Hot Jupiters**: 0.01-0.03 (1-3% dip)
- **Super-Earths**: 0.001-0.003 (0.1-0.3% dip)
- **Earth-sized**: 0.0001-0.001 (0.01-0.1% dip)

## Period Range Guidelines

- **Hot Jupiters**: 0.5-10 days
- **Warm planets**: 10-100 days
- **Habitable zone**: Sun-like star: 200-400 days; M-dwarf: 10-50 days

## Dependencies

```bash
pip install lightkurve transitleastsquares numpy matplotlib scipy
```

---

# Light Curve Preprocessing

## Outlier Removal

### Using Lightkurve

```python
import lightkurve as lk

lc_clean, mask = lc.remove_outliers(sigma=3, return_mask=True)
outliers = lc[mask]
```

### Manual Outlier Removal

```python
import numpy as np

median = np.median(flux)
std = np.std(flux)

good = np.abs(flux - median) < 3 * std
time_clean = time[good]
flux_clean = flux[good]
error_clean = error[good]
```

## Removing Long-Term Trends

### Flattening with Lightkurve

```python
lc_flat = lc_clean.flatten(window_length=500)
```

The `flatten()` method uses a Savitzky-Golay filter to remove trends while preserving transit signals.

### Iterative Sine Fitting

For removing high-frequency stellar variability (rotation, pulsation):

```python
def sine_fitting(lc):
    """Remove dominant periodic signal by fitting sine wave."""
    pg = lc.to_periodogram()
    model = pg.model(time=lc.time, frequency=pg.frequency_at_max_power)
    lc_new = lc.copy()
    lc_new.flux = lc_new.flux / model.flux
    return lc_new, model

lc_processed = lc_clean.copy()
for i in range(50):
    lc_processed, model = sine_fitting(lc_processed)
```

**Warning**: This removes periodic signals, so use carefully if you're searching for periodic transits.

## Handling Data Quality Flags

**IMPORTANT**: Quality flag conventions vary by data source!

### Standard TESS format
```python
# For standard TESS files (flag=0 is GOOD):
good = flag == 0
time_clean = time[good]
flux_clean = flux[good]
error_clean = error[good]
```

### Alternative formats
```python
# For some exported files (flag=0 is BAD):
good = flag != 0
time_clean = time[good]
flux_clean = flux[good]
error_clean = error[good]
```

**Always verify your data format!** Check which approach gives cleaner results.

## Preprocessing Pipeline (Order Matters!)

1. **Quality filtering**: Apply data quality flags first
2. **Outlier removal**: Remove bad data points (flares, cosmic rays)
3. **Trend removal**: Remove long-term variations (stellar rotation, instrumental drift)
4. **Optional second pass**: Additional outlier removal after detrending

### Critical Principles
- **Always include flux_err**: Critical for proper weighting in period search algorithms
- **Preserve transit shapes**: Use methods like `flatten()` that preserve short-duration dips
- **Don't over-process**: Too aggressive preprocessing can remove real signals
- **Verify visually**: Plot each step to ensure quality

## Dependencies

```bash
pip install lightkurve numpy matplotlib
```

---

# Lomb-Scargle Periodogram

The Lomb-Scargle periodogram is the standard tool for finding periods in unevenly sampled astronomical time series data.

## Basic Usage with Lightkurve

```python
import lightkurve as lk
import numpy as np

lc = lk.LightCurve(time=time, flux=flux, flux_err=error)
pg = lc.to_periodogram(maximum_period=15)

strongest_period = pg.period_at_max_power
max_power = pg.max_power

print(f"Strongest period: {strongest_period:.5f} days")
print(f"Power: {max_power:.5f}")
```

## Period Range Selection

Choose appropriate period ranges based on your science case:

- **Stellar rotation**: 0.1 - 100 days
- **Exoplanet transits**: 0.5 - 50 days (most common)
- **Eclipsing binaries**: 0.1 - 100 days
- **Stellar pulsations**: 0.001 - 1 day

```python
pg = lc.to_periodogram(minimum_period=2.0, maximum_period=7.0)
```

## Interpreting Results

- **Single strong peak**: Likely the true period
- **Harmonics**: Peaks at period/2, period*2 suggest the fundamental period
- **Aliases**: Check if period*2 or period/2 also show signals

## Model Fitting

Once you find a period, you can fit a model:

```python
frequency = pg.frequency_at_max_power
model = pg.model(time=lc.time, frequency=frequency)

import matplotlib.pyplot as plt
lc.plot(label='Data')
model.plot(label='Model')
plt.legend()
plt.show()
```

## Dependencies

```bash
pip install lightkurve numpy matplotlib
```

---

# Transit Least Squares (TLS)

Transit Least Squares is a specialized algorithm optimized for detecting exoplanet transits in light curves. It's more sensitive than Lomb-Scargle for transit-shaped signals because it fits actual transit models.

## Installation

```bash
pip install transitleastsquares
```

## Basic Usage

**CRITICAL**: Always include `flux_err` (flux uncertainties) for best results!

```python
import transitleastsquares as tls
import lightkurve as lk
import numpy as np

lc = lk.LightCurve(time=time, flux=flux, flux_err=error)
lc_clean = lc.remove_outliers(sigma=3)
lc_flat = lc_clean.flatten()

pg_tls = tls.transitleastsquares(
    lc_flat.time.value,
    lc_flat.flux.value,
    lc_flat.flux_err.value
)

out_tls = pg_tls.power(
    show_progress_bar=False,
    verbose=False
)

best_period = out_tls.period
period_uncertainty = out_tls.period_uncertainty
t0 = out_tls.T0
depth = out_tls.depth
snr = out_tls.snr
sde = out_tls.SDE

print(f"Best period: {best_period:.5f} ± {period_uncertainty:.5f} days")
print(f"Transit epoch (T0): {t0:.5f}")
print(f"Depth: {depth:.5f}")
print(f"SNR: {snr:.2f}")
print(f"SDE: {sde:.2f}")
```

### With explicit period range
```python
out_tls = pg_tls.power(
    period_min=2.0,
    period_max=7.0,
    show_progress_bar=True,
    verbose=True
)
```

## Period Refinement Strategy

**Best Practice**: Broad search first, then refine for precision.

1. Initial search finds candidate at ~3.2 days
2. Refine by searching narrower range (e.g., 3.0-3.4 days)
3. Narrower range → finer grid → better precision

```python
results_refined = pg_tls.power(
    period_min=X,  # e.g., 90% of candidate
    period_max=Y   # e.g., 110% of candidate
)
```

**Typical refinement window**: ±2% to ±10% around candidate period.

## Phase-Folding

TLS automatically computes phase-folded data:

```python
folded_phase = out_tls.folded_phase
folded_y = out_tls.folded_y
model_phase = out_tls.model_folded_phase
model_flux = out_tls.model_folded_model

import matplotlib.pyplot as plt
plt.plot(folded_phase, folded_y, '.', label='Data')
plt.plot(model_phase, model_flux, '-', label='Model')
plt.xlabel('Phase')
plt.ylabel('Flux')
plt.legend()
plt.show()
```

## Transit Masking

After finding a transit, mask it to search for additional planets:

```python
from transitleastsquares import transit_mask

mask = transit_mask(time, period, duration, t0)
lc_masked = lc[~mask]

pg_tls2 = tls.transitleastsquares(
    lc_masked.time,
    lc_masked.flux,
    lc_masked.flux_err
)
out_tls2 = pg_tls2.power(period_min=2, period_max=7)
```

## Interpreting Results

### Signal Detection Efficiency (SDE)

- **SDE > 6**: Strong candidate
- **SDE > 9**: Very strong candidate
- **SDE < 6**: Weak signal, may be false positive

### Signal-to-Noise Ratio (SNR)

- **SNR > 7**: Generally considered reliable
- **SNR < 7**: May need additional validation

### Common Warnings

TLS may warn: "X of Y transits without data. The true period may be twice the given period."

This suggests:
- Data gaps may cause period aliasing
- Check if `period * 2` also shows a signal
- The true period might be longer

## Model Light Curve

TLS provides the best-fit transit model:

```python
model_time = out_tls.model_lightcurve_time
model_flux = out_tls.model_lightcurve_model

import matplotlib.pyplot as plt
plt.plot(time, flux, '.', label='Data')
plt.plot(model_time, model_flux, '-', label='Model')
plt.xlabel('Time [days]')
plt.ylabel('Flux')
plt.legend()
plt.show()
```

## Workflow Considerations

1. **Data quality**: Filter by quality flags before analysis
2. **Preprocessing order**: Remove outliers → flatten/detrend → search for transits
3. **Initial search**: Use broad period range to find candidates
4. **Refinement**: Narrow search around candidates for better precision
5. **Validation**: Check SDE, SNR, and visual inspection of phase-folded data

### Typical Parameter Ranges

- **Outlier removal**: sigma=3-5 (lower = more aggressive)
- **Period search**: Match expected orbital periods for your target
- **Refinement window**: ±2-10% around candidate period
- **SDE threshold**: >6 for candidates, >9 for strong detections

## Multiple Planet Search Strategy

1. **Initial broad search**: Use TLS with default or wide period range
2. **Identify candidate**: Find period with highest SDE
3. **Refine period**: Narrow search around candidate period (±5%)
4. **Mask transits**: Remove data points during transits
5. **Search for additional planets**: Repeat TLS on masked data

## Dependencies

```bash
pip install transitleastsquares lightkurve numpy matplotlib