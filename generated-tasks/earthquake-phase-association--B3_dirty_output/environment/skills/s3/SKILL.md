---
name: s1
description: "Earthquake phase association: GaMMA associator, ObsPy data API, SeisBench model API, and seismic picker selection."
---

# GaMMA Associator Library

## Installing GaMMA
`pip install git+https://github.com/wayneweiqiang/GaMMA.git`

## `association`

```python
def association(picks, stations, config, event_idx0=0, method="BGMM", **kwargs)
```

Associates phase picks to earthquake events using Bayesian (`"BGMM"`) or standard (`"GMM"`) Gaussian Mixture Models.

### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `picks` | DataFrame | required | Seismic phase pick data |
| `stations` | DataFrame | required | Station metadata with locations |
| `config` | dict | required | Configuration parameters |
| `event_idx0` | int | `0` | Starting event index |
| `method` | str | `"BGMM"` | `"BGMM"` or `"GMM"` |

### Required DataFrame Columns

**`picks` DataFrame:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | str | Station identifier (must match `stations`) | `network.station.` or `network.station.location.channel` |
| `timestamp` | datetime/str | Pick arrival time (ISO format or datetime) | `"2019-07-04T22:00:06.084"` |
| `type` | str | Phase type: `"p"` or `"s"` (lowercase) | `"p"` |
| `prob` | float | Pick probability/weight (0-1) | `0.94` |
| `amp` | float | Amplitude in m/s (required if `use_amplitude=True`) | `0.000017` |

- Timestamps must be UTC or converted to UTC
- Phase types forced to lowercase internally
- Picks with `amp == 0` or `amp == -1` filtered when `use_amplitude=True`

**`stations` DataFrame:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | str | Station identifier | `"CI.CCC..BH"`|
| `x(km)` | float | X coordinate in km (projected) | `-35.6` |
| `y(km)` | float | Y coordinate in km (projected) | `45.2` |
| `z(km)` | float | Z coordinate (elevation, typically negative) | `-0.67` |

- Coordinates in projected local system (e.g., via `pyproj`)
- `id` must match picks DataFrame `id` values
- Group by unique `id`; identical attributes collapsed, conflicting preserved as sorted list

**Tail handling:** Remove stale `results.csv` before running:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py
```

### Config Dictionary Keys

**Required:**

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Location dimensions | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Min picks per earthquake | `5` |
| `max_sigma11` | float | Max time residual (seconds) | `2.0` |
| `use_amplitude` | bool | Use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | BFGS optimization bounds | `((-35, 92), (-128, 78), (0, 21), (None, None))` |
| `oversample_factor` | float | Oversampling factor for initial GMM | `5.0` (BGMM), `1.0` (GMM)|

- `dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`
- `bfgs_bounds` format: `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))` — last tuple for time (unbounded)

**Velocity Model:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `vel` | dict | `{"p": 6.0, "s": 3.47}` | Uniform velocity model (km/s) |
| `eikonal` | dict/None | `None` | 1D velocity model for travel times |

**DBSCAN Pre-clustering (Optional):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_dbscan` | bool | `True` | Enable DBSCAN pre-clustering |
| `dbscan_eps` | float | `25` | Max time between picks (seconds) |
| `dbscan_min_samples` | int | `3` | Min samples in neighborhood |
| `dbscan_min_cluster_size` | int | `500` | Min cluster size for hierarchical splitting |
| `dbscan_max_time_space_ratio` | float | `10` | Max time/space ratio for splitting |

- `dbscan_eps` obtained from `estimate_eps` function

**Filtering (Optional):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_sigma22` | float | `1.0` | Max amplitude residual (log scale, requires `use_amplitude=True`) |
| `max_sigma12` | float | `1.0` | Max covariance |
| `max_sigma11` | float | `2.0` | Max time residual (s) |
| `min_p_picks_per_eq` | int | `0` | Min P-phase picks per event |
| `min_s_picks_per_eq` | int | `0` | Min S-phase picks per event |
| `min_stations` | int | `5` | Min unique stations per event |

**Other Optional:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `covariance_prior` | list[float] | auto | Prior `[time, amp]` |
| `ncpu` | int | auto | CPUs for parallel processing |

### Return Values

Returns tuple `(events, assignments)`:

**`events` (list[dict]):**

| Key | Type | Description |
|-----|------|-------------|
| `time` | str | Origin time (ISO 8601 with ms) |
| `magnitude` | float | Estimated magnitude (999 if `use_amplitude=False`) |
| `sigma_time` | float | Time uncertainty (s) |
| `sigma_amp` | float | Amplitude uncertainty (log10) |
| `cov_time_amp` | float | Time-amplitude covariance |
| `gamma_score` | float | Association quality score |
| `num_picks` | int | Total picks assigned |
| `num_p_picks` | int | P-phase picks |
| `num_s_picks` | int | S-phase picks |
| `event_index` | int | Unique event index |
| `x(km)` | float | Hypocenter X |
| `y(km)` | float | Hypocenter Y |
| `z(km)` | float | Depth |

**`assignments` (list[tuple]):** `(pick_index, event_index, gamma_score)`

## `estimate_eps`

```python
def estimate_eps(stations, vp, sigma=2.0)
```

Estimates DBSCAN epsilon based on station spacing. Returns epsilon in **seconds**.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stations` | DataFrame | required | Station metadata with `x(km)`, `y(km)`, `z(km)` |
| `vp` | float | required | P-wave velocity (km/s) |
| `sigma` | float | `2.0` | Standard deviations above mean |

```python
from gamma.utils import estimate_eps

vp = 6.0
eps = estimate_eps(stations, vp, sigma=2.0)
config = {"use_dbscan": True, "dbscan_eps": eps, "dbscan_min_samples": 3}
```

---

# ObsPy Data API

## Waveform Data

**Hierarchy:** `Stream` → `Trace` (multiple)

**Trace DATA:** `data` (NumPy array), `stats` (`network`, `station`, `location`, `channel`, `starttime`, `sampling_rate`, `delta`, `endtime`, `npts`)

**Trace METHODS:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`

```python
>>> from obspy import read
>>> st = read()
>>> print(st)
3 Trace(s) in Stream:
BW.RJOB..EHZ | 2009-08-24T00:20:03.000000Z - ... | 100.0 Hz, 3000 samples
BW.RJOB..EHN | 2009-08-24T00:20:03.000000Z - ... | 100.0 Hz, 3000 samples
BW.RJOB..EHE | 2009-08-24T00:20:03.000000Z - ... | 100.0 Hz, 3000 samples
>>> tr = st[0]
>>> tr.data
array([ 0.        ,  0.00694644,  0.07597424, ...,  1.93449584,
        0.98196204,  0.44196924])
>>> tr.stats.starttime
UTCDateTime(2009, 8, 24, 0, 20, 3)
```

## Event Metadata

**Hierarchy:** `Catalog` → `events` → `Event` (multiple)

**Event contains:** `origins` → `Origin` (`latitude`, `longitude`, `depth`, `time`), `magnitudes` → `Magnitude` (`mag`, `magnitude_type`), `picks`, `focal_mechanisms`

## Station Metadata

**Hierarchy:** `Inventory` → `networks` → `Network` → `stations` → `Station` → `channels` → `Channel`

**Network:** `code`, `description`
**Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`
**Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`

## Key Classes & Functions

| Class/Function | Description |
|----------------|-------------|
| `read` | Read waveform files into `Stream` |
| `Stream` | List-like container of `Trace` objects |
| `Trace` | Continuous seismic data series |
| `Stats` | Header info for `Trace` |
| `UTCDateTime` | UTC-based datetime |
| `read_events` | Read event files into `Catalog` |
| `Catalog` | Container for `Event` objects |
| `Event` | Seismic event description |
| `read_inventory` | Read inventory files |
| `Inventory` | Root of Network→Station→Channel hierarchy |

## Modules

`obspy.core.trace`, `obspy.core.stream`, `obspy.core.utcdatetime`, `obspy.core.event`, `obspy.core.inventory`, `obspy.core.util`, `obspy.core.preview`

---

# SeisBench Model API

## Installing SeisBench
```
pip install seisbench
```

## Overview

`WaveformModel` is the abstract base class. Two core functions:

- **`annotate(stream)`** → returns annotation stream (e.g., pick probabilities over time)
- **`classify(stream)`** → returns discrete results (e.g., list of picks)

```python
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)
outputs = model.classify(stream)
```

Both handle multi-station waveforms and auto-group traces.

## Loading Pretrained Models

```python
import seisbench.models as sbm

sbm.PhaseNet.list_pretrained()
model = sbm.PhaseNet.from_pretrained("original")
```

Weights download on first use, cached locally.

## Performance Tips

- Run on GPU
- Use large `batch_size`
- Compile model: `model = torch.compile(model)` (torch 2.0+)
- Use `annotate_asyncio` / `classify_asyncio` for parallel data loading
- Check `model.sampling_rate`; manual resampling may help (obspy resampling not parallelized as of 2023)

## Integrated Models

| Model | Task |
|-------|------|
| `BasicPhaseAE` | Phase Picking |
| `CRED` | Earthquake Detection |
| `DPP` | Phase Picking |
| `DepthPhaseNet` | Depth estimation from depth phases |
| `DepthPhaseTEAM` | Depth estimation from depth phases |
| `DeepDenoiser` | Denoising |
| `SeisDAE` | Denoising |
| `EQTransformer` | Earthquake Detection/Phase Picking |
| `GPD` | Phase Picking |
| `LFEDetect` | Phase Picking (Low-frequency earthquakes) |
| `OBSTransformer` | Earthquake Detection/Phase Picking |
| `PhaseNet` | Phase Picking |
| `PhaseNetLight` | Phase Picking |
| `PickBlue` | Earthquake Detection/Phase Picking |
| `Skynet` | Phase Picking |
| `VariableLengthPhaseNet` | Phase Picking |

## Best Practices

- If waveforms are extremely small (`<=1e-10`), multiply by large number (e.g., `1e10`) before normalization
- Apply normalization yourself despite built-in normalization. Built-in uses `(waveform - mean) / (std + epsilon)` which can destroy signals for extremely small values
- API processes arbitrary-length streams; no need to segment. Do not assume one P and one S per stream

---

# Seismic Event Detection & Phase Picking Method Selection

## Method Tradeoffs

| Method | Generalizability | Sensitivity | Speed, Ease-of-Use | False Positives |
|--------|------------------|-------------|-------------------|-----------------|
| STA/LTA | High | Low | Fast, Easy | Many |
| Manual | High | High | Slow, Difficult | Few |
| Deep Learning | High | High | Fast, Easy | Medium |
| Template Matching | Low | High | Slow, Difficult | Few |

## STA/LTA
- Fast, real-time capable; easy to implement; no prior knowledge needed
- Amplitude-based: reliably detects large signals
- **Limitations:** High false detections during active sequences; automatic picks less precise; requires manual review for quality catalog

## Template Matching
- Most sensitive: finds smallest earthquakes buried in noise (if similar to template)
- Excellent temporal resolution for sequences; high threshold reduces false detections
- **Limitations:** Requires template waveforms with good picks from preexisting catalog; no spatial resolution improvement (unknown sources not found); setup effort; computationally intensive

## Deep Learning Pickers
- Best value for sparse/nonexistent networks; rapidly creates complete catalogs during active sequences
- Requires continuous data; works best on broadband, also usable on accelerometers, nodals, Raspberry Shakes
- No prior knowledge needed; finds small local earthquakes (lower Mc) with fewer false positives than STA/LTA
- Easy setup; SeisBench provides pretrained models and APIs
- **Limitations:** Out-of-distribution data causes larger errors (0.1-0.5 s) and missed picks; cannot pick phases buried in noise (less sensitive than template matching); sometimes misses picks from large earthquakes obvious to humans