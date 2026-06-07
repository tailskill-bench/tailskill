---
name: s1
description: "Earthquake phase association: GaMMA associator, ObsPy data API, SeisBench model API, and seismic picker selection."
---

# GaMMA Associator Library

## Installing GaMMA
`pip install git+https://github.com/wayneweiqiang/GaMMA.git`

## GaMMA Core API

### `association`

```python
def association(picks, stations, config, event_idx0=0, method="BGMM", **kwargs)
```

Associates phase picks to earthquake events using Bayesian (`"BGMM"`) or standard (`"GMM"`) Gaussian Mixture Models.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `picks` | DataFrame | required | Seismic phase pick data |
| `stations` | DataFrame | required | Station metadata with locations |
| `config` | dict | required | Configuration parameters |
| `event_idx0` | int | `0` | Starting event index |
| `method` | str | `"BGMM"` | `"BGMM"` or `"GMM"` |

#### Required DataFrame Columns

##### `picks` DataFrame

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Station identifier (must match `stations`) |
| `timestamp` | datetime/str | Pick arrival time (UTC, ISO format or datetime) |
| `type` | str | Phase type: `"p"` or `"s"` (lowercase) |
| `prob` | float | Pick probability/weight (0-1) |
| `amp` | float | Amplitude in m/s (required if `use_amplitude=True`) |

- Picks with `amp == 0` or `amp == -1` are filtered when `use_amplitude=True`

##### `stations` DataFrame

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Station identifier |
| `x(km)` | float | X coordinate in km (projected) |
| `y(km)` | float | Y coordinate in km (projected) |
| `z(km)` | float | Z coordinate (elevation, typically negative) |

- Coordinates should be in a projected local coordinate system (e.g., via `pyproj`)

**Tail handling:** Filter extreme outlier elevation values using IQR-based detection:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/stations.csv 6
```
where `6` is the column index of `elevation_m`.

#### Config Dictionary Keys

##### Required Keys

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Location dimensions to solve for | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Minimum picks required per earthquake | `5` |
| `max_sigma11` | float | Maximum allowed time residual in seconds | `2.0` |
| `use_amplitude` | bool | Whether to use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | Bounds for BFGS optimization | `((-35, 92), (-128, 78), (0, 21), (None, None))` |
| `oversample_factor` | float | Factor for oversampling initial GMM components | `5.0` for `BGMM`, `1.0` for `GMM`|

- `dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`
- `bfgs_bounds` format: `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))` — last tuple is for time (unbounded)

##### Velocity Model Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `vel` | dict | `{"p": 6.0, "s": 3.47}` | Uniform velocity model (km/s) |
| `eikonal` | dict/None | `None` | 1D velocity model for travel times |

##### DBSCAN Pre-clustering Keys (Optional)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_dbscan` | bool | `True` | Enable DBSCAN pre-clustering |
| `dbscan_eps` | float | `25` | Max time between picks (seconds) |
| `dbscan_min_samples` | int | `3` | Min samples in DBSCAN neighborhood |
| `dbscan_min_cluster_size` | int | `500` | Min cluster size for hierarchical splitting |
| `dbscan_max_time_space_ratio` | float | `10` | Max time/space ratio for splitting |

- `dbscan_eps` is obtained from `estimate_eps` function

##### Filtering Keys (Optional)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_sigma22` | float | `1.0` | Max phase amplitude residual in log scale (if `use_amplitude=True`) |
| `max_sigma12` | float | `1.0` | Max covariance |
| `max_sigma11` | float | `2.0` | Max phase time residual (s) |
| `min_p_picks_per_eq` | int | `0` | Min P-phase picks per event |
| `min_s_picks_per_eq` | int | `0` | Min S-phase picks per event |
| `min_stations` | int | `5` | Min unique stations per event |

##### Other Optional Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `covariance_prior` | list[float] | auto | Prior for covariance `[time, amp]` |
| `ncpu` | int | auto | Number of CPUs for parallel processing |

#### Return Values

Returns tuple `(events, assignments)`:

##### `events` (list[dict])

| Key | Type | Description |
|-----|------|-------------|
| `time` | str | Origin time (ISO 8601 with milliseconds) |
| `magnitude` | float | Estimated magnitude (999 if `use_amplitude=False`) |
| `sigma_time` | float | Time uncertainty (seconds) |
| `sigma_amp` | float | Amplitude uncertainty (log10 scale) |
| `cov_time_amp` | float | Time-amplitude covariance |
| `gamma_score` | float | Association quality score |
| `num_picks` | int | Total picks assigned |
| `num_p_picks` | int | P-phase picks assigned |
| `num_s_picks` | int | S-phase picks assigned |
| `event_index` | int | Unique event index |
| `x(km)` | float | X coordinate of hypocenter |
| `y(km)` | float | Y coordinate of hypocenter |
| `z(km)` | float | Z coordinate (depth) |

##### `assignments` (list[tuple])

List of tuples `(pick_index, event_index, gamma_score)`.

### `estimate_eps`

```python
def estimate_eps(stations, vp, sigma=2.0)
```

Estimates DBSCAN epsilon based on station spacing. Returns epsilon in **seconds**.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stations` | DataFrame | required | Station metadata with 3D coordinates |
| `vp` | float | required | P-wave velocity in km/s |
| `sigma` | float | `2.0` | Standard deviations above mean |

Requires columns: `x(km)`, `y(km)`, `z(km)`.

```python
from gamma.utils import estimate_eps

config["dbscan_eps"] = estimate_eps(stations, config["vel"]["p"])
config["dbscan_min_samples"] = 3
config["dbscan_min_cluster_size"] = 500
config["dbscan_max_time_space_ratio"] = 10
```

---

# ObsPy Data API

## Waveform Data

Seismograms (SAC, MiniSEED, GSE2, etc.) are imported into a `Stream` via `read()`. Streams contain multiple `Trace` objects (gap-less continuous time series with headers).

**Hierarchy:** `Stream` → `Trace` (multiple)

**Trace attributes:** `data` (NumPy ndarray), `stats` (dict-like: `network`, `station`, `location`, `channel`, `starttime`, `sampling_rate`, `delta`, `endtime`, `npts`)

**Trace methods:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`

```python
>>> from obspy import read
>>> st = read()
>>> print(st)
3 Trace(s) in Stream:
BW.RJOB..EHZ | 2009-08-24T00:20:03.000000Z - ... | 100.0 Hz, 3000 samples
BW.RJOB..EHN | 2009-08-24T00:20:03.000000Z - ... | 100.0 Hz, 3000 samples
BW.RJOB..EHE | 2009-08-24T00:20:03.000000Z - ... | 100.0 Hz, 3000 samples
>>> tr = st[0]
>>> tr.stats.starttime
UTCDateTime(2009, 8, 24, 0, 20, 3)
```

## Event Metadata

Modeled after [QuakeML](https://quake.ethz.ch/quakeml/). See `read_events()` and `Catalog.write()` for formats.

**Hierarchy:** `Catalog` → `events` → `Event` (multiple)

**Event contains:** `origins` → `Origin` (`latitude`, `longitude`, `depth`, `time`), `magnitudes` → `Magnitude` (`mag`, `magnitude_type`), `picks`, `focal_mechanisms`

## Station Metadata

Modeled after [FDSN StationXML](https://www.fdsn.org/xml/station/). See `read_inventory()` and `Inventory.write()` for formats.

**Hierarchy:** `Inventory` → `networks` → `Network` → `stations` → `Station` → `channels` → `Channel`

- **Network:** `code`, `description`
- **Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`
- **Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`

## Key Classes & Functions

| Class/Function | Description |
|----------------|-------------|
| `read` | Read waveform files into `Stream` |
| `Stream` | List-like container of `Trace` objects |
| `Trace` | Continuous time series with header |
| `Stats` | Header container for `Trace` |
| `UTCDateTime` | UTC-based datetime object |
| `read_events` | Read event files into `Catalog` |
| `Catalog` | Container for `Event` objects |
| `Event` | Describes a seismic event |
| `read_inventory` | Read station inventory files |
| `Inventory` | Root of Network→Station→Channel hierarchy |

---

# SeisBench Model API

## Installing SeisBench
```
pip install seisbench
```

## Overview

`WaveformModel` is the abstract base class. Two core functions:

- **`annotate`** — Returns annotations as stream (e.g., pick probabilities):
```python
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)
```

- **`classify`** — Returns discrete results (e.g., list of picks):
```python
stream = obspy.read("my_waveforms.mseed")
outputs = model.classify(stream)
print(outputs)
```

Both handle multi-station waveforms automatically. Move model to GPU for GPU computation.

## Loading Pretrained Models

```python
import seisbench.models as sbm

sbm.PhaseNet.list_pretrained()                  # Available models
model = sbm.PhaseNet.from_pretrained("original")  # Load weights
```

Weights download on first use and cache locally.

## Performance Tips

- **GPU** — Faster even for CPU-bound models
- **Large `batch_size`** — Pass as optional argument
- **Compile (torch 2.0+)** — `model = torch.compile(model)`
- **Async interface** — `annotate_asyncio`, `classify_asyncio` for parallel data loading
- **Manual resampling** — Check `model.sampling_rate`; SeisBench uses non-parallelized obspy routines

## Integrated Models

| Model | Task |
|-------|------|
| `BasicPhaseAE`, `DPP`, `GPD`, `PhaseNet`, `PhaseNetLight`, `Skynet`, `VariableLengthPhaseNet` | Phase Picking |
| `CRED` | Earthquake Detection |
| `DepthPhaseNet`, `DepthPhaseTEAM` | Depth estimation from depth phases |
| `DeepDenoiser`, `SeisDAE` | Denoising |
| `EQTransformer`, `OBSTransformer`, `PickBlue` | Earthquake Detection/Phase Picking |
| `LFEDetect` | Phase Picking (Low-frequency earthquakes) |

## Best Practices

- If waveform data is extremely small (`<=1e-10`), multiply by a large number (e.g., `1e10`) before normalization to avoid numerical instability
- Apply normalization yourself. SeisBench's `(waveform - mean) / (std + epsilon)` can destroy signals for extremely small values
- Process streams of arbitrary length; do not segment data yourself. Do not assume only one P-wave and one S-wave per stream

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

- Fast, real-time operation; easy to implement and optimize
- No prior knowledge needed; amplitude-based detector for large signals
- **Limitations:** High false detections during active sequences; automatic picks less precise; requires manual review

## Template Matching

- Most sensitive detector; finds smallest earthquakes buried in noise
- Excellent temporal resolution for earthquake sequences
- **Limitations:** Requires template waveforms from preexisting catalog; no spatial resolution for unknown sources; computationally intensive

## Deep Learning Pickers

- Best value for sparse or nonexistent networks
- Rapidly creates complete catalogs during active sequences
- Works on broadband, accelerometers, nodals, and Raspberry Shakes
- No prior knowledge needed; fewer false detections than STA/LTA
- Easy setup via SeisBench APIs and pretrained models
- **Limitations:** Out-of-distribution data causes larger pick errors (0.1-0.5 s) and missed picks; cannot pick phases buried in noise; sometimes misses picks from large earthquakes obvious to humans