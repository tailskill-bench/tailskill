---
name: s1
description: "Earthquake phase association: GaMMA associator, ObsPy data API, SeisBench model API, and seismic picker selection. Use when processing seismic waveforms, picking phases, or associating events."
---

# GaMMA Associator Library

## Installing GaMMA
`pip install git+https://github.com/wayneweiqiang/GaMMA.git`

## GaMMA Core API

### `association`

```python
def association(picks, stations, config, event_idx0=0, method="BGMM", **kwargs)
```

Associates seismic phase picks to earthquake events using Bayesian or standard Gaussian Mixture Models.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `picks` | DataFrame | required | Seismic phase pick data |
| `stations` | DataFrame | required | Station metadata with locations |
| `config` | dict | required | Configuration parameters |
| `event_idx0` | int | `0` | Starting event index for numbering |
| `method` | str | `"BGMM"` | `"BGMM"` (Bayesian) or `"GMM"` (standard) |

#### Required DataFrame Columns

##### `picks` DataFrame

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | str | Station identifier (must match `stations`) | `network.station.` or `network.station.location.channel` |
| `timestamp` | datetime/str | Pick arrival time (ISO format or datetime) | `"2019-07-04T22:00:06.084"` |
| `type` | str | Phase type: `"p"` or `"s"` (lowercase) | `"p"` |
| `prob` | float | Pick probability/weight (0-1) | `0.94` |
| `amp` | float | Amplitude in m/s (required if `use_amplitude=True`) | `0.000017` |

- Timestamps must be in UTC or converted to UTC
- Phase types are forced to lowercase internally
- Picks with `amp == 0` or `amp == -1` are filtered when `use_amplitude=True`

##### `stations` DataFrame

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | str | Station identifier | `"CI.CCC..BH"`|
| `x(km)` | float | X coordinate in km (projected) | `-35.6` |
| `y(km)` | float | Y coordinate in km (projected) | `45.2` |
| `z(km)` | float | Z coordinate (elevation, typically negative) | `-0.67` |

- Coordinates should be in a projected local coordinate system (e.g., via `pyproj`)
- The `id` column must match the `id` values in the picks DataFrame
- Group stations by unique `id`; identical attributes are collapsed to a single value and conflicting metadata are preserved as a sorted list

**Tail handling:** Remove duplicate station entries before processing:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/stations.csv 1
```
where `1` is the column index of the `station` key column.

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
- `bfgs_bounds` format: `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))` (last tuple is unbounded time)

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
|-----|------|-------------|-------------|
| `max_sigma22` | float | `1.0` | Max phase amplitude residual in log scale (required if `use_amplitude=True`) |
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

Returns a tuple `(events, assignments)`:

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

List of tuples `(pick_index, event_index, gamma_score)`:
- `pick_index`: Index in the original `picks` DataFrame
- `event_index`: Associated event index
- `gamma_score`: Probability/confidence of assignment

### `estimate_eps`

```python
def estimate_eps(stations, vp, sigma=2.0)
```

Estimates DBSCAN epsilon based on station spacing. Returns epsilon in **seconds** (typical: 10-20s).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stations` | DataFrame | required | Station metadata with 3D coordinates |
| `vp` | float | required | P-wave velocity in km/s |
| `sigma` | float | `2.0` | Number of standard deviations above the mean |

Requires columns: `x(km)`, `y(km)`, `z(km)`.

```python
from gamma.utils import association, estimate_eps

config["dbscan_eps"] = estimate_eps(stations, config["vel"]["p"])
config["dbscan_min_samples"] = 3
config["dbscan_min_cluster_size"] = 500
config["dbscan_max_time_space_ratio"] = 10
```

---

# ObsPy Data API

## Waveform Data

Seismograms (SAC, MiniSEED, GSE2, SEISAN, Q, etc.) are imported into a `Stream` object via `read()`.

### Stream and Trace Class Structure

**Hierarchy:** `Stream` → `Trace` (multiple)

**Trace - DATA:**
- `data` → NumPy array
- `stats`:
  - `network`, `station`, `location`, `channel` — Physical location and instrument
  - `starttime`, `sampling_rate`, `delta`, `endtime`, `npts` — Interrelated

**Trace - METHODS:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`

### Example

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

Modeled after [QuakeML](https://quake.ethz.ch/quakeml/). See `read_events()` and `Catalog.write()` for formats.

**Hierarchy:** `Catalog` → `events` → `Event` (multiple)

**Event contains:**
- `origins` → `Origin` (multiple): `latitude`, `longitude`, `depth`, `time`, ...
- `magnitudes` → `Magnitude` (multiple): `mag`, `magnitude_type`, ...
- `picks`, `focal_mechanisms`

## Station Metadata

Modeled after [FDSN StationXML](https://www.fdsn.org/xml/station/). See `read_inventory()` and `Inventory.write()` for formats.

**Hierarchy:** `Inventory` → `networks` → `Network` → `stations` → `Station` → `channels` → `Channel`

- **Network:** `code`, `description`, ...
- **Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`, ...
- **Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`, ...

## Key Classes & Functions

| Class/Function | Description |
|----------------|-------------|
| `read` | Read waveform files into a `Stream` object |
| `Stream` | List-like container of `Trace` objects |
| `Trace` | Continuous seismic data series |
| `Stats` | Header information for a `Trace` |
| `UTCDateTime` | UTC-based datetime object |
| `read_events` | Read event files into a `Catalog` |
| `Catalog` | Container for `Event` objects |
| `Event` | Describes a seismic event |
| `read_inventory` | Read station inventory files |
| `Inventory` | Root of Network → Station → Channel hierarchy |

---

# SeisBench Model API

## Installing SeisBench
```
pip install seisbench
```

## Overview

SeisBench provides the abstract class `WaveformModel` that all models subclass. Two core functions:

- **`annotate(stream)`** → returns annotations as obspy stream (e.g., pick probabilities over time)
- **`classify(stream)`** → returns discrete results (e.g., list of picks)

Both handle multi-station waveforms and auto-group traces.

```python
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)  # Returns obspy stream with annotations
outputs = model.classify(stream)      # Returns list of picks
print(outputs)
```

## Loading Pretrained Models

Weights download on first use and cache locally.

```python
import seisbench.models as sbm

sbm.PhaseNet.list_pretrained()                  # Get available models
model = sbm.PhaseNet.from_pretrained("original")  # Load original weights
```

## Speeding Up Model Application

- **GPU execution** — usually faster
- **Large `batch_size`** — especially beneficial on GPU
- **Compile model (torch 2.0+)** — `model = torch.compile(model)`
- **Asyncio interface** — `annotate_asyncio` / `classify_asyncio` for parallel data loading
- **Manual resampling** — check `model.sampling_rate`; obspy resampling is not parallelized

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
- If waveform data is extremely small in scale (`<=1e-10`), multiply by a large number (e.g., `1e10`) before normalization to avoid numerical instability
- SeisBench normalizes via `(waveform - mean) / (std + epsilon)`, which can destroy signals for very small values — apply your own normalization
- The API processes arbitrary-length streams; no need to segment data yourself
- Do not assume a stream contains only one P-wave and one S-wave — treat it as continuous data

---

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

**Advantages:** Fast (real-time), easy to implement, no prior knowledge needed, reliably detects large signals.

**Limitations:** High false detection rate during active sequences, automatic picks less precise, requires manual review for quality catalogs.

## Template Matching

**Advantages:** Most sensitive detector — finds smallest earthquakes buried in noise if similar to template. Excellent temporal resolution. Few false detections at high thresholds.

**Limitations:** Requires template waveforms with good picks from preexisting catalog. Does not improve spatial resolution (unknown sources not similar to templates are missed). Setup effort required, computationally intensive.

## Deep Learning Pickers

**When to use:** Sparse or nonexistent networks, active sequences needing rapid catalog generation, temporary broadband/nodal deployments. Requires continuous data. Works best on broadband but produces usable picks on accelerometers, nodals, and Raspberry Shakes.

**Advantages:** No prior knowledge needed, finds small local earthquakes (lower Mc) with fewer false detections than STA/LTA, easy setup via SeisBench pretrained models.

**Limitations:** Out-of-distribution data causes larger pick errors (0.1-0.5s) and missed picks. Cannot pick phases completely buried in noise (less sensitive than template matching). Occasionally misses picks from large earthquakes that are obvious to humans.