---
name: s1
description: "Earthquake phase association using GaMMA, ObsPy waveform/metadata APIs, and SeisBench deep learning pickers."
---

# GaMMA Associator Library

## Installation
`pip install git+https://github.com/wayneweiqiang/GaMMA.git`

## `association`

```python
def association(picks, stations, config, event_idx0=0, method="BGMM", **kwargs)
```

Associates phase picks to earthquake events using Bayesian (`"BGMM"`) or standard (`"GMM"`) Gaussian Mixture Models.

### Input DataFrames

**`picks`** — Required columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | str | Station identifier (must match `stations`) | `network.station.` or `network.station.location.channel` |
| `timestamp` | datetime/str | Pick arrival time (UTC, ISO format or datetime) | `"2019-07-04T22:00:06.084"` |
| `type` | str | Phase type: `"p"` or `"s"` (lowercase) | `"p"` |
| `prob` | float | Pick probability/weight (0–1) | `0.94` |
| `amp` | float | Amplitude in m/s (required if `use_amplitude=True`) | `0.000017` |

- Phase types forced to lowercase internally
- Picks with `amp == 0` or `amp == -1` filtered when `use_amplitude=True`

**`stations`** — Required columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | str | Station identifier | `"CI.CCC..BH"` |
| `x(km)` | float | X coordinate in km (projected) | `-35.6` |
| `y(km)` | float | Y coordinate in km (projected) | `45.2` |
| `z(km)` | float | Z coordinate (elevation, typically negative) | `-0.67` |

- Coordinates in projected local system (e.g., via `pyproj`)
- `id` must match picks DataFrame; group by unique `id` (identical attributes collapsed, conflicting preserved as sorted list)

**Remove duplicate station entries:**
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/stations.csv 1
```
where `1` is the column index of the `station` key column.

### Config Dictionary

**Required keys:**

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Location dimensions to solve for | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Minimum picks per earthquake | `5` |
| `max_sigma11` | float | Maximum time residual (seconds) | `2.0` |
| `use_amplitude` | bool | Use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | BFGS optimization bounds | `((-35, 92), (-128, 78), (0, 21), (None, None))` |
| `oversample_factor` | float | Oversampling initial GMM components | `5.0` (BGMM), `1.0` (GMM) |

- `dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`
- `bfgs_bounds` format: `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))` — last tuple is unbounded time

**Velocity model keys:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `vel` | dict | `{"p": 6.0, "s": 3.47}` | Uniform velocity model (km/s) |
| `eikonal` | dict/None | `None` | 1D velocity model for travel times |

**DBSCAN pre-clustering keys (optional):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_dbscan` | bool | `True` | Enable DBSCAN pre-clustering |
| `dbscan_eps` | float | `25` | Max time between picks (seconds) |
| `dbscan_min_samples` | int | `3` | Min samples in DBSCAN neighborhood |
| `dbscan_min_cluster_size` | int | `500` | Min cluster size for hierarchical splitting |
| `dbscan_max_time_space_ratio` | float | `10` | Max time/space ratio for splitting |

- `dbscan_eps` obtained from `estimate_eps` function

**Filtering keys (optional):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_sigma22` | float | `1.0` | Max amplitude residual (log scale, requires `use_amplitude=True`) |
| `max_sigma12` | float | `1.0` | Max covariance |
| `max_sigma11` | float | `2.0` | Max time residual (s) |
| `min_p_picks_per_eq` | int | `0` | Min P-phase picks per event |
| `min_s_picks_per_eq` | int | `0` | Min S-phase picks per event |
| `min_stations` | int | `5` | Min unique stations per event |

**Other optional keys:** `covariance_prior` (list[float], auto), `ncpu` (int, auto)

### Return Values

Returns tuple `(events, assignments)`:

**`events`** (list[dict]):

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

**`assignments`** (list[tuple]): `(pick_index, event_index, gamma_score)`

## `estimate_eps`

```python
def estimate_eps(stations, vp, sigma=2.0)
```

Estimates DBSCAN epsilon from station spacing. Returns epsilon in **seconds** (typical: 10–20s). Requires columns: `x(km)`, `y(km)`, `z(km)`.

```python
from gamma.utils import association, estimate_eps

config["dbscan_eps"] = estimate_eps(stations, config["vel"]["p"])
config["dbscan_min_samples"] = 3
config["dbscan_min_cluster_size"] = 500
config["dbscan_max_time_space_ratio"] = 10
```

# ObsPy Data API

## Waveform Data

Seismograms (SAC, MiniSEED, GSE2, SEISAN, Q, etc.) imported into `Stream` via `read()`.

**Hierarchy:** `Stream` → `Trace` (multiple)

**Trace data:** `data` (NumPy array), `stats` (network, station, location, channel, starttime, sampling_rate, delta, endtime, npts)

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
>>> tr.data
array([ 0.        ,  0.00694644,  0.07597424, ...,  1.93449584,
        0.98196204,  0.44196924])
>>> tr.stats.starttime
UTCDateTime(2009, 8, 24, 0, 20, 3)
```

## Event Metadata (QuakeML)

**Hierarchy:** `Catalog` → `Event` (multiple)

**Event contains:** `origins` → `Origin` (latitude, longitude, depth, time), `magnitudes` → `Magnitude` (mag, magnitude_type), `picks`, `focal_mechanisms`

## Station Metadata (FDSN StationXML)

**Hierarchy:** `Inventory` → `Network` → `Station` → `Channel`

- **Network:** code, description
- **Station:** code, latitude, longitude, elevation, start_date, end_date
- **Channel:** code, location_code, latitude, longitude, elevation, depth, dip, azimuth, sample_rate, start_date, end_date, response

## Key Classes

`read` (waveforms → Stream), `Stream`, `Trace`, `Stats`, `UTCDateTime`, `read_events` (→ Catalog), `Catalog`, `Event`, `read_inventory` (→ Inventory), `Inventory`

# SeisBench Model API

## Installation
```
pip install seisbench
```

## Overview

Abstract class `WaveformModel` with two core functions:
- **`annotate(stream)`** → annotations as obspy stream (pick probabilities over time)
- **`classify(stream)`** → discrete results (list of picks)

Both handle multi-station waveforms and auto-group traces.

```python
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)
outputs = model.classify(stream)
print(outputs)
```

## Loading Pretrained Models

Weights download on first use and cache locally.

```python
import seisbench.models as sbm

sbm.PhaseNet.list_pretrained()
model = sbm.PhaseNet.from_pretrained("original")
```

## Performance Tips

- GPU execution, large `batch_size`, `torch.compile(model)` (torch 2.0+)
- Asyncio: `annotate_asyncio` / `classify_asyncio`
- Check `model.sampling_rate`; obspy resampling not parallelized

## Integrated Models

| Model | Task |
|-------|------|
| `BasicPhaseAE`, `DPP`, `GPD`, `PhaseNet`, `PhaseNetLight`, `Skynet`, `VariableLengthPhaseNet` | Phase Picking |
| `CRED` | Earthquake Detection |
| `DeepDenoiser`, `SeisDAE` | Denoising |
| `DepthPhaseNet`, `DepthPhaseTEAM` | Depth estimation from depth phases |
| `EQTransformer`, `OBSTransformer`, `PickBlue` | Earthquake Detection/Phase Picking |
| `LFEDetect` | Phase Picking (Low-frequency earthquakes) |

## Best Practices

- If waveform data ≤1e-10, multiply by large number (e.g., 1e10) before normalization to avoid numerical instability
- SeisBench normalizes via `(waveform - mean) / (std + epsilon)` — can destroy signals for very small values; apply own normalization
- API processes arbitrary-length streams; no manual segmentation needed
- Do not assume one P-wave and one S-wave per stream — treat as continuous data

# Seismic Event Detection & Phase Picking Method Selection

## Method Tradeoffs

| Method | Generalizability | Sensitivity | Speed, Ease-of-Use | False Positives |
|--------|------------------|-------------|-------------------|-----------------|
| STA/LTA | High | Low | Fast, Easy | Many |
| Manual | High | High | Slow, Difficult | Few |
| Deep Learning | High | High | Fast, Easy | Medium |
| Template Matching | Low | High | Slow, Difficult | Few |

- **Generalizability**: Ability to find arbitrary earthquake signals
- **Sensitivity**: Ability to find small earthquakes

## STA/LTA

Fast (real-time), easy, no prior knowledge needed, reliably detects large signals. High false detection rate during active sequences, automatic picks less precise, requires manual review for quality catalogs.

## Template Matching

Most sensitive detector — finds smallest earthquakes buried in noise if similar to template. Excellent temporal resolution, few false detections at high thresholds. Requires template waveforms with good picks from preexisting catalog. Does not improve spatial resolution (unknown sources not similar to templates missed). Setup effort required, computationally intensive.

## Deep Learning Pickers

Use for sparse or nonexistent networks, active sequences needing rapid catalog generation, temporary broadband/nodal deployments. Requires continuous data. Works best on broadband but produces usable picks on accelerometers, nodals, and Raspberry Shakes.

No prior knowledge needed, finds small local earthquakes (lower Mc) with fewer false detections than STA/LTA, easy setup via SeisBench pretrained models. Out-of-distribution data causes larger pick errors (0.1–0.5s) and missed picks. Cannot pick phases completely buried in noise (less sensitive than template matching). Occasionally misses picks from large earthquakes obvious to humans.