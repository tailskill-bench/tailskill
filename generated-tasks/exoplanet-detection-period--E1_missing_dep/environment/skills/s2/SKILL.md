---
name: s1
description: "Exoplanet detection period analysis: light curve preprocessing, transit detection (BLS/TLS), Lomb-Scargle periodograms, and exoplanet workflow guidance."
---


# Box Least Squares (BLS) Periodogram

The Box Least Squares (BLS) periodogram is a statistical tool for detecting transiting exoplanets and eclipsing binaries in photometric time series data. BLS models a transit as a periodic upside-down top hat (box shape) and finds the period, duration, depth, and reference time that best fit the data.

## Installation

BLS is part of Astropy:

```bash
pip install astropy
```

## Basic Usage

```python
import numpy as np
import astropy.units as u
from astropy.timeseries import BoxLeastSquares

# Prepare data
t = time * u.day  # Add units if not already present
y = flux
dy = flux_err  # Optional but recommended

# Create BLS object
model = BoxLeastSquares(t, y, dy=dy)

# Automatic period search with specified duration
duration = 0.2 * u.day
periodogram = model.autopower(duration)

# Extract results
best_period = periodogram.period[np.argmax(periodogram.power)]
print(f"Best period: {best_period:.5f}")
```

## Using autopower vs power

### autopower: Automatic Period Grid

Recommended for initial searches. Automatically determines appropriate period grid:

```python
# Specify duration (or multiple durations)
duration = 0.2 * u.day
periodogram = model.autopower(duration)

# Or search multiple durations
durations = [0.1, 0.15, 0.2, 0.25] * u.day
periodogram = model.autopower(durations)
```

### power: Custom Period Grid

For more control over the search:

```python
# Define custom period grid
periods = np.linspace(2.0, 10.0, 1000) * u.day
duration = 0.2 * u.day

periodogram = model.power(periods, duration)
```

**Warning**: Period grid quality matters! Too coarse and you'll miss the true period.

## Objective Functions

BLS supports two objective functions:

### 1. Log Likelihood (default)

Maximizes the statistical likelihood of the model fit:

```python
periodogram = model.autopower(0.2 * u.day, objective='likelihood')
```

### 2. Signal-to-Noise Ratio (SNR)

Uses the SNR with which the transit depth is measured:

```python
periodogram = model.autopower(0.2 * u.day, objective='snr')
```

The SNR objective can improve reliability in the presence of correlated noise.

## Complete Example

```python
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.timeseries import BoxLeastSquares

# Load and prepare data
data = np.loadtxt('light_curve.txt')
time = data[:, 0] * u.day
flux = data[:, 1]
flux_err = data[:, 3]

# Create BLS model
model = BoxLeastSquares(time, flux, dy=flux_err)

# Run BLS with automatic period grid
durations = np.linspace(0.05, 0.3, 10) * u.day
periodogram = model.autopower(durations, objective='likelihood')

# Find peak
max_power_idx = np.argmax(periodogram.power)
best_period = periodogram.period[max_power_idx]
best_duration = periodogram.duration[max_power_idx]
best_t0 = periodogram.transit_time[max_power_idx]
max_power = periodogram.power[max_power_idx]

print(f"Period: {best_period:.5f}")
print(f"Duration: {best_duration:.5f}")
print(f"T0: {best_t0:.5f}")
print(f"Power: {max_power:.2f}")

# Plot periodogram
plt.plot(periodogram.period, periodogram.power)
plt.xlabel('Period [days]')
plt.ylabel('BLS Power')
plt.show()
```

## Peak Statistics for Validation

Use `compute_stats()` to calculate detailed statistics about a candidate transit:

```python
# Get statistics for the best period
stats = model.compute_stats(
    periodogram.period[max_power_idx],
    periodogram.duration[max_power_idx],
    periodogram.transit_time[max_power_idx]
)

# Key statistics for validation
print(f"Depth: {stats['depth']:.6f}")
print(f"Depth uncertainty: {stats['depth_err']:.6f}")
print(f"SNR: {stats['depth_snr']:.2f}")
print(f"Odd/Even mismatch: {stats['depth_odd'] - stats['depth_even']:.6f}")
print(f"Number of transits: {stats['transit_count']}")

# Check for false positives
if abs(stats['depth_odd'] - stats['depth_even']) > 3 * stats['depth_err']:
    print("Warning: Significant odd-even mismatch - may not be planetary")
```

**Validation criteria:**
- **High depth SNR (>7)**: Strong signal
- **Low odd-even mismatch**: Consistent transit depth
- **Multiple transits observed**: More reliable
- **Reasonable duration**: Not too long or too short for orbit

## Period Grid Sensitivity

The BLS periodogram is sensitive to period grid spacing. The `autoperiod()` method provides a conservative grid:

```python
# Get automatic period grid
periods = model.autoperiod(durations, minimum_period=1*u.day, maximum_period=10*u.day)
print(f"Period grid has {len(periods)} points")

# Use this grid with power()
periodogram = model.power(periods, durations)
```

## Comparing BLS Results

To compare multiple peaks:

```python
# Find top 5 peaks
sorted_idx = np.argsort(periodogram.power)[::-1]
top_5 = sorted_idx[:5]

print("Top 5 candidates:")
for i, idx in enumerate(top_5):
    period = periodogram.period[idx]
    power = periodogram.power[idx]
    duration = periodogram.duration[idx]

    stats = model.compute_stats(period, duration, periodogram.transit_time[idx])

    print(f"\n{i+1}. Period: {period:.5f}")
    print(f"   Power: {power:.2f}")
    print(f"   Duration: {duration:.5f}")
    print(f"   SNR: {stats['depth_snr']:.2f}")
    print(f"   Transits: {stats['transit_count']}")
```

## Phase-Folded Light Curve

After finding a candidate, phase-fold to visualize the transit:

```python
# Fold the light curve at the best period
phase = ((time.value - best_t0.value) % best_period.value) / best_period.value

# Plot to verify transit shape
plt.plot(phase, flux, '.')
plt.xlabel('Phase')
plt.ylabel('Flux')
plt.show()
```

## BLS vs Transit Least Squares (TLS)

Both methods search for transits, but differ in implementation:

### Box Least Squares (BLS)
- Built into Astropy (no extra install)
- Fast for targeted searches
- Good statistical framework
- `compute_stats()` provides detailed validation
- Simpler transit model (box shape)
- May be less sensitive to grazing transits

### Transit Least Squares (TLS)
- More sophisticated transit models
- Generally more sensitive
- Better handles grazing transits
- Automatic period grid is more robust
- Requires separate package (`pip install transitleastsquares`)
- Slower for very long time series

**Recommendation**: Try both! TLS is often more sensitive, but BLS is faster and built-in.

## Integration with Preprocessing

BLS works best with preprocessed data. Consider this pipeline:

1. **Quality filtering**: Remove flagged data points
2. **Outlier removal**: Clean obvious artifacts
3. **Detrending**: Remove stellar variability (rotation, trends)
4. **BLS search**: Run period search on cleaned data
5. **Validation**: Use `compute_stats()` to check candidate quality

- Preprocessing should **preserve transit shapes** (use gentle methods like `flatten()`)
- Don't over-process - too aggressive cleaning removes real signals
- BLS needs reasonable period and duration ranges
- Always validate with multiple metrics (power, SNR, odd-even)

## Dependencies

```bash
pip install astropy numpy matplotlib
# Optional: lightkurve for preprocessing
pip install lightkurve
```

## References

- [Astropy BLS Documentation](https://docs.astropy.org/en/stable/timeseries/bls.html)
- [Astropy Time Series Guide](https://docs.astropy.org/en/stable/timeseries/)
- **Kovács, Zucker, & Mazeh (2002)**: Original BLS paper - [A&A 391, 369](https://arxiv.org/abs/astro-ph/0206099)
- **Hartman & Bakos (2016)**: VARTOOLS implementation - [A&C 17, 1](https://arxiv.org/abs/1605.06811)
- [Lightkurve Tutorials](https://lightkurve.github.io/lightkurve/tutorials/)
- [TLS GitHub](https://github.com/hippke/tls) - Alternative transit detection method


---


# Exoplanet Detection Workflows

This skill provides general guidance on exoplanet detection workflows, helping you choose the right approach for your data and goals.

## Pipeline Design Principles

### Key Stages

1. **Data Loading**: Understand your data format, columns, time system
2. **Quality Control**: Filter bad data points using quality flags
3. **Preprocessing**: Remove noise while preserving planetary signals
4. **Period Search**: Choose appropriate algorithm for signal type
5. **Validation**: Verify candidate is real, not artifact
6. **Refinement**: Improve period precision if candidate is strong

### Critical Decisions

**Which period search algorithm?**
- **TLS**: Best for transit-shaped signals (box-like dips)
- **Lomb-Scargle**: Good for any periodic signal, fast exploration
- **BLS**: Alternative to TLS, built into Astropy

**What period range to search?**
- Hot Jupiters: short periods (0.5-10 days)
- Habitable zone: longer periods (depends on star)
- Balance: wider range = more complete, but slower

## Choosing the Right Method

### Transit Least Squares (TLS)
- Searching for transiting exoplanets
- Signal has transit-like shape (box-shaped dips)
- Most sensitive for transits
- Handles grazing transits
- Slower than Lomb-Scargle

### Lomb-Scargle Periodogram
- Exploring data for any periodic signal
- Detecting stellar rotation
- Finding pulsation periods
- Fast, works for any periodic signal
- Less sensitive to shallow transits

### Box Least Squares (BLS)
- Alternative to TLS for transits
- Available in astropy

**Note**: TLS generally performs better than BLS for exoplanet detection.

## Signal Validation

### Strong Candidate (TLS)
- **SDE > 9**: Very strong candidate
- **SDE > 6**: Strong candidate
- **SNR > 7**: Reliable signal

### Warning Signs
- **Low SDE (<6)**: Weak signal, may be false positive
- **Period exactly half/double expected**: Check for aliasing
- **High odd-even mismatch**: May not be planetary transit

### How to Validate

- **Signal strength metrics**: Check SDE, SNR against thresholds
- **Visual inspection**: Phase-fold data at candidate period
- **Odd-even consistency**: Do odd and even transits have same depth?
- **Multiple transits**: More transits = more confidence

## Multi-Planet Systems

Some systems have multiple transiting planets. Strategy:

1. Find first candidate
2. Mask out first planet's transits
3. Search remaining data for additional periods
4. Repeat until no more significant signals

See Transit Least Squares documentation for `transit_mask` function.

## Expected Transit Depths

For context:
- **Hot Jupiters**: 0.01-0.03 (1-3% dip)
- **Super-Earths**: 0.001-0.003 (0.1-0.3% dip)
- **Earth-sized**: 0.0001-0.001 (0.01-0.1% dip)

Detection difficulty increases dramatically for smaller planets.

## Period Range Guidelines

Based on target characteristics:
- **Hot Jupiters**: 0.5-10 days
- **Warm planets**: 10-100 days
- **Habitable zone**:
  - Sun-like star: 200-400 days
  - M-dwarf: 10-50 days

Adjust search ranges based on mission duration and expected planet types.

## Best Practices

1. **Always include flux uncertainties** - critical for proper weighting
2. **Visualize each preprocessing step** - ensure you're improving data quality
3. **Check quality flags** - verify convention (flag=0 may mean good OR bad)
4. **Use appropriate sigma** - 3 for initial outliers, 5 after flattening
5. **Refine promising candidates** - narrow period search for precision
6. **Validate detections** - check SDE, SNR, phase-folded plots
7. **Consider data gaps** - may cause period aliasing
8. **Document your workflow** - reproducibility is key
9. **Check for missing dependencies** - the `transitleastsquares` package may have been removed. If you encounter `ModuleNotFoundError: No module named 'transitleastsquares'`, reinstall it with `pip install --no-cache-dir transitleastsquares==1.32`

## References

- [Lightkurve Tutorials](https://lightkurve.github.io/lightkurve/tutorials/index.html)
- [TLS GitHub](https://github.com/hippke/tls)
- [TLS Tutorials](https://github.com/hippke/tls/tree/master/tutorials)
- Hippke & Heller (2019) - Transit Least Squares paper
- Kovács et al. (2002) - BLS algorithm

## Dependencies

```bash
pip install lightkurve transitleastsquares numpy matplotlib scipy
```


---


# Light Curve Preprocessing

Preprocessing is essential before period analysis. Raw light curves often contain outliers, long-term trends, and instrumental effects that can mask or create false periodic signals.

## Outlier Removal

### Using Lightkurve

```python
import lightkurve as lk

# Remove outliers using sigma clipping
lc_clean, mask = lc.remove_outliers(sigma=3, return_mask=True)
outliers = lc[mask]  # Points that were removed

# Common sigma values:
# sigma=3: Standard (removes ~0.3% of data)
# sigma=5: Conservative (removes fewer points)
# sigma=2: Aggressive (removes more points)
```

### Manual Outlier Removal

```python
import numpy as np

# Calculate median and standard deviation
median = np.median(flux)
std = np.std(flux)

# Remove points beyond 3 sigma
good = np.abs(flux - median) < 3 * std
time_clean = time[good]
flux_clean = flux[good]
error_clean = error[good]
```

## Removing Long-Term Trends

### Flattening with Lightkurve

```python
# Flatten to remove low-frequency variability
# window_length: number of cadences to use for smoothing
lc_flat = lc_clean.flatten(window_length=500)

# Common window lengths:
# 100-200: Remove short-term trends
# 300-500: Remove medium-term trends (typical for TESS)
# 500-1000: Remove long-term trends
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

# Iterate multiple times to remove multiple periodic components
lc_processed = lc_clean.copy()
for i in range(50):  # Number of iterations
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

## Preprocessing Pipeline Considerations

### Key Steps (Order Matters!)

1. **Quality filtering**: Apply data quality flags first
2. **Outlier removal**: Remove bad data points (flares, cosmic rays)
3. **Trend removal**: Remove long-term variations (stellar rotation, instrumental drift)
4. **Optional second pass**: Additional outlier removal after detrending

### Important Principles

- **Always include flux_err**: Critical for proper weighting in period search algorithms
- **Preserve transit shapes**: Use methods like `flatten()` that preserve short-duration dips
- **Don't over-process**: Too aggressive preprocessing can remove real signals
- **Verify visually**: Plot each step to ensure quality

### Parameter Selection

- **Outlier removal sigma**: Lower sigma (2-3) is aggressive, higher (5-7) is conservative
- **Flattening window**: Should be longer than transit duration but shorter than stellar rotation period
- **When to do two passes**: Remove obvious outliers before detrending, then remove residual outliers after

## Visualizing Results

Always plot your light curve to verify preprocessing quality:

```python
import matplotlib.pyplot as plt

# Use .plot() method on LightCurve objects
lc.plot()
plt.show()
```

**Best practice**: Plot before and after each major step to ensure you're improving data quality, not removing real signals.

## Dependencies

```bash
pip install lightkurve numpy matplotlib
```

## References

- [Lightkurve Preprocessing Tutorials](https://lightkurve.github.io/lightkurve/tutorials/index.html)
- [Removing Instrumental Noise](https://lightkurve.github.io/lightkurve/tutorials/2.3-removing-noise.html)


---


# Lomb-Scargle Periodogram

The Lomb-Scargle periodogram is the standard tool for finding periods in unevenly sampled astronomical time series data. It's particularly useful for detecting periodic signals in light curves from space missions like Kepler, K2, and TESS.

## Basic Usage with Lightkurve

```python
import lightkurve as lk
import numpy as np

# Create a light curve object
lc = lk.LightCurve(time=time, flux=flux, flux_err=error)

# Create periodogram (specify maximum period to search)
pg = lc.to_periodogram(maximum_period=15)  # Search up to 15 days

# Find strongest period
strongest_period = pg.period_at_max_power
max_power = pg.max_power

print(f"Strongest period: {strongest_period:.5f} days")
print(f"Power: {max_power:.5f}")
```

## Plotting Periodograms

```python
import matplotlib.pyplot as plt

pg.plot(view='period')  # View vs period (not frequency)
plt.xlabel('Period [days]')
plt.ylabel('Power')
plt.show()
```

**Important**: Use `view='period'` to see periods directly, not frequencies. The default `view='frequency'` shows frequency (1/period).

## Period Range Selection

Choose appropriate period ranges based on your science case:

- **Stellar rotation**: 0.1 - 100 days
- **Exoplanet transits**: 0.5 - 50 days (most common)
- **Eclipsing binaries**: 0.1 - 100 days
- **Stellar pulsations**: 0.001 - 1 day

```python
# Search specific period range
pg = lc.to_periodogram(minimum_period=2.0, maximum_period=7.0)
```

## Interpreting Results

### Power Significance

Higher power indicates stronger periodic signal, but be cautious:
- **High power**: Likely real periodic signal
- **Multiple peaks**: Could indicate harmonics (period/2, period*2)
- **Aliasing**: Very short periods may be aliases of longer periods

### Common Patterns

1. **Single strong peak**: Likely the true period
2. **Harmonics**: Peaks at period/2, period*2 suggest the fundamental period
3. **Aliases**: Check if period*2 or period/2 also show signals

## Model Fitting

Once you find a period, you can fit a model:

```python
# Get the frequency at maximum power
frequency = pg.frequency_at_max_power

# Create a model light curve
model = pg.model(time=lc.time, frequency=frequency)

# Plot data and model
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

## References

- [Lightkurve Tutorials](https://lightkurve.github.io/lightkurve/tutorials/index.html)
- [Lightkurve Periodogram Documentation](https://docs.lightkurve.org/)


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

# Example 1: Using Lightkurve (recommended)
lc = lk.LightCurve(time=time, flux=flux, flux_err=error)
lc_clean = lc.remove_outliers(sigma=3)
lc_flat = lc_clean.flatten()

# Create TLS object - MUST include flux_err!
pg_tls = tls.transitleastsquares(
    lc_flat.time.value,      # Time array
    lc_flat.flux.value,      # Flux array
    lc_flat.flux_err.value   # Flux uncertainties (REQUIRED!)
)

# Search for transits (uses default period range if not specified)
out_tls = pg_tls.power(
    show_progress_bar=False,
    verbose=False
)

# Extract results
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
# Search specific period range
out_tls = pg_tls.power(
    period_min=2.0,      # Minimum period (days)
    period_max=7.0,      # Maximum period (days)
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
# After initial search finds a candidate, narrow the search:
results_refined = pg_tls.power(
    period_min=X,  # e.g., 90% of candidate
    period_max=Y   # e.g., 110% of candidate
)
```

**Typical refinement window**: ±2% to ±10% around candidate period.

### Advanced Parameters

- `oversampling_factor`: Higher values give finer period resolution (slower)
- `duration_grid_step`: Step size for transit duration grid (1.01 = 1% steps)
- `T0_fit_margin`: Margin for fitting transit epoch (0 = no margin, faster)

## Phase-Folding

Once you have a period, TLS automatically computes phase-folded data:

```python
# Phase-folded data is automatically computed
folded_phase = out_tls.folded_phase
folded_y = out_tls.folded_y
model_phase = out_tls.model_folded_phase
model_flux = out_tls.model_folded_model

# Plot phase-folded light curve
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

# Create transit mask
mask = transit_mask(time, period, duration, t0)
lc_masked = lc[~mask]  # Remove transit points

# Search for second planet
pg_tls2 = tls.transitleastsquares(
    lc_masked.time,
    lc_masked.flux,
    lc_masked.flux_err
)
out_tls2 = pg_tls2.power(period_min=2, period_max=7)
```

## Interpreting Results

### Signal Detection Efficiency (SDE)

SDE is TLS's measure of signal strength:
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
# Model over full time range
model_time = out_tls.model_lightcurve_time
model_flux = out_tls.model_lightcurve_model

# Plot with data
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
```

## References

- [TLS GitHub Repository](https://github.com/hippke/tls)
- [TLS Tutorials](https://github.com/hippke/tls/tree/master/tutorials)
- [Lightkurve Tutorials](https://lightkurve.github.io/lightkurve/tutorials/index.html)
- [Lightkurve Exoplanet Examples](https://lightkurve.github.io/lightkurve/tutorials/3.1-identifying-transiting-exoplanets.html)