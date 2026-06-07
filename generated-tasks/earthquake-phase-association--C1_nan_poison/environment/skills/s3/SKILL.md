---
name: s1
description: "Earthquake phase association: GaMMA associator, ObsPy data API, SeisBench model API, and seismic picker selection."
---

# GaMMA Associator

## Install
`pip install git+https://github.com/wayneweiqiang/GaMMA.git`

## `association`

```python
def association(picks, stations, config, event_idx0=0, method="BGMM", **kwargs)
```

Associates phase picks to events using Bayesian (`"BGMM"`) or standard (`"GMM"`) Gaussian Mixture Models.

### `picks` DataFrame Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Station identifier (must match `stations`) |
| `timestamp` | datetime/str | Pick arrival time (UTC, ISO format or datetime) |
| `type` | str | Phase type: `"p"` or `"s"` (lowercase) |
| `prob` | float | Pick probability/weight (0-1) |
| `amp` | float | Amplitude in m/s (required if `use_amplitude=True`) |

- Phase types forced to lowercase internally. Picks with `amp == 0` or `amp == -1` filtered when `use_amplitude=True`. DataFrame index tracks pick identities in output.

### `stations` DataFrame Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Station identifier (e.g., `"CI.CCC..BH"`) |
| `x(km)` | float | X coordinate in km (projected) |
| `y(km)` | float | Y coordinate in km (projected) |
| `z(km)` | float | Z coordinate (elevation, typically negative) |

- Use projected local coordinate system (e.g., `pyproj`). `id` must match picks. Group by unique `id`; identical attributes collapsed, conflicting metadata preserved as sorted list.

**Tail handling** — clean NaN/Inf in numeric columns (especially `elevation_m`):
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/stations.csv 6
```
where `6` is the column index of `elevation_m`.

### Config Dictionary

#### Required Keys

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Location dimensions | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Min picks per earthquake | `5` |
| `max_sigma11` | float | Max time residual (s) | `2.0` |
| `use_amplitude` | bool | Use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | BFGS optimization bounds | `((-35, 92), (-128, 78), (0, 21), (None, None))` |
| `oversample_factor` | float | Oversampling factor | `5.0` (BGMM), `1.0` (GMM) |

- `dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`.
- `bfgs_bounds`: `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))`. Last tuple is time (unbounded).

#### Velocity Model Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `vel` | dict | `{"p": 6.0, "s": 3.47}` | Uniform velocity model (km/s) |
| `eikonal` | dict/None | `None` | 1D velocity model for travel times |

#### DBSCAN Pre-clustering Keys (Optional)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_dbscan` | bool | `True` | Enable DBSCAN pre-clustering |
| `dbscan_eps` | float | `25` | Max time between picks (s); from `estimate_eps` |
| `dbscan_min_samples` | int | `3` | Min samples in neighborhood |
| `dbscan_min_cluster_size` | int | `500` | Min cluster size for hierarchical splitting |
| `dbscan_max_time_space_ratio` | float | `10` | Max time/space ratio for splitting |

#### Filtering Keys (Optional)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_sigma22` | float | `1.0` | Max amplitude residual (log scale; if `use_amplitude=True`) |
| `max_sigma12` | float | `1.0` | Max covariance |
| `max_sigma11` | float | `2.0` | Max time residual (s) |
| `min_p_picks_per_eq` | int | `0` | Min P-picks per event |
| `min_s_picks_per_eq` | int | `0` | Min S-picks per event |
| `min_stations` | int | `5` | Min unique stations per event |

#### Other Optional Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `covariance_prior` | list[float] | auto | Prior `[time, amp]` |
| `ncpu` | int | auto | CPUs for parallel processing |

### Return Values

Returns `(events, assignments)`:

#### `events` (list[dict])

| Key | Type | Description |
|-----|------|-------------|
| `time` | str | Origin time (ISO 8601 with ms) |
| `magnitude` | float | Estimated magnitude (999 if `use_amplitude=False`) |
| `sigma_time` | float | Time uncertainty (s) |
| `sigma_amp` | float | Amplitude uncertainty (log10) |
| `cov_time_amp` | float | Time-amplitude covariance |
| `gamma_score` | float | Association quality score |
| `num_picks` | int | Total picks assigned |
| `num_p_picks` | int | P-picks assigned |
| `num_s_picks` | int | S-picks assigned |
| `event_index` | int | Unique event index |
| `x(km)` | float | Hypocenter X |
| `y(km)` | float | Hypocenter Y |
| `z(km)` | float | Depth |

#### `assignments` (list[tuple])

List of `(pick_index, event_index, gamma_score)`:
- `pick_index`: Index in original `picks` DataFrame
- `event_index`: Associated event index
- `gamma_score`: Assignment probability/confidence

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

config["dbscan_eps"] = estimate_eps(stations, config["vel"]["p"])
# Or manual override: config["dbscan_eps"] = 15  # seconds
```

---

# ObsPy Data API

## Waveform Data

Seismograms (SAC, MiniSEED, GSE2, etc.) imported into `Stream` via `read()`. Streams contain multiple `Trace` objects (gap-less continuous time series with headers).

### Stream/Trace Structure

**Trace DATA:** `data` (NumPy array), `stats` (`network`, `station`, `location`, `channel`, `starttime`, `sampling_rate`, `delta`, `endtime`, `npts`)

**Trace METHODS:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`

```python
>>> from obspy import read
>>> st = read()
>>> print(st)
3 Trace(s) in Stream:
BW.RJOB..EHZ | 2009-08-24T00:20:03.000000Z - ... | 100.0 Hz, 3000 samples
...
>>> tr = st[0]
>>> tr.stats.starttime
UTCDateTime(2009, 8, 24, 0, 20, 3)
```

## Event Metadata (QuakeML hierarchy)

**Hierarchy:** `Catalog` → `Event` (multiple)

**Event contains:** `origins` → `Origin` (`latitude`, `longitude`, `depth`, `time`), `magnitudes` → `Magnitude` (`mag`, `magnitude_type`), `picks`, `focal_mechanisms`

## Station Metadata (FDSN StationXML hierarchy)

**Hierarchy:** `Inventory` → `Network` → `Station` → `Channel`

**Network:** `code`, `description`
**Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`
**Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`

## Key Classes & Modules

| Class/Function | Description |
|----------------|-------------|
| `read` | Read waveform files into `Stream` |
| `Stream` | List-like container of `Trace` objects |
| `Trace` | Continuous seismic trace with data and header |
| `Stats` | Header container for `Trace` |
| `UTCDateTime` | UTC-based datetime |
| `read_events` | Read event files into `Catalog` |
| `Catalog` | Container for `Event` objects |
| `Event` | Seismic event description |
| `read_inventory` | Read inventory files |
| `Inventory` | Root of Network→Station→Channel hierarchy |

| Module | Description |
|--------|-------------|
| `obspy.core.trace` | `Trace` and `Stats` |
| `obspy.core.stream` | `Stream` |
| `obspy.core.utcdatetime` | UTC datetime class |
| `obspy.core.event` | Event metadata |
| `obspy.core.inventory` | Station metadata |

---

# SeisBench Model API

## Install
```
pip install seisbench
```

## Overview

Abstract class `WaveformModel` provides two core functions:
- **`annotate`**: Returns annotations as stream (e.g., pick probabilities over time)
- **`classify`**: Returns discrete results (e.g., list of picks)

```python
import obspy
stream = obspy.read("my_waveforms.mseed")

annotations = model.annotate(stream)  # Returns obspy stream with annotations
outputs = model.classify(stream)      # Returns discrete results, e.g., list of picks
```

Handles multiple stations at once, auto-grouping traces. GPU acceleration available.

## Loading Pretrained Models

```python
import seisbench.models as sbm

sbm.PhaseNet.list_pretrained()                  # Available models
model = sbm.PhaseNet.from_pretrained("original")  # Load weights
```

Weights downloaded on first use, cached locally.

## Performance Tips

- **GPU** for significant speedup
- **Large `batch_size`** parameter for GPU efficiency
- **`torch.compile(model)`** (torch 2.0+)
- **`annotate_asyncio`/`classify_asyncio`** for parallel data loading
- **Manual resampling** to match `model.sampling_rate`

## Integrated Models

| Model | Task |
|-------|------|
| `BasicPhaseAE`, `DPP`, `GPD`, `PhaseNet`, `PhaseNetLight`, `Skynet`, `VariableLengthPhaseNet` | Phase Picking |
| `CRED`, `EQTransformer`, `OBSTransformer`, `PickBlue` | Detection/Phase Picking |
| `LFEDetect` | Low-frequency earthquake picking |
| `DeepDenoiser`, `SeisDAE` | Denoising |
| `DepthPhaseNet`, `DepthPhaseTEAM` | Depth estimation |

## Best Practices
- For extremely small data (`<=1e-10`), multiply by large number (e.g., `1e10`) before normalization to avoid numerical instability
- API normalizes via `(waveform - mean) / (std + epsilon)` — apply own normalization for tiny values where epsilon destroys signals
- Process streams of arbitrary length; do not segment. Do not assume only one P and one S per stream

---

# Seismic Event Detection & Phase Picking Method Selection

## Method Tradeoffs

| Method | Generalizability | Sensitivity | Speed/Ease | False Positives |
|--------|------------------|-------------|------------|-----------------|
| STA/LTA | High | Low | Fast, Easy | Many |
| Manual | High | High | Slow, Hard | Few |
| Deep Learning | High | High | Fast, Easy | Medium |
| Template Matching | Low | High | Slow, Hard | Few |

- **Generalizability**: Finds arbitrary earthquake signals
- **Sensitivity**: Finds small earthquakes

## STA/LTA
Fast, real-time, easy to implement, no prior knowledge needed. High false detection rate during active sequences; automatic picks less precise; requires manual review for quality catalogs.

## Template Matching
Optimally sensitive; finds smallest earthquakes in noise if similar to template; excellent temporal resolution. Requires template waveforms with good picks from existing catalog; no spatial resolution improvement for unknown sources; computationally intensive.

## Deep Learning Pickers
Best for sparse/nonexistent networks, rapid catalog creation during active sequences, temporary deployments. No prior knowledge needed; fewer false detections than STA/LTA; easy setup via SeisBench. Out-of-distribution data causes larger errors (0.1-0.5s) and missed picks; cannot pick phases buried in noise; sometimes misses obvious large picks.