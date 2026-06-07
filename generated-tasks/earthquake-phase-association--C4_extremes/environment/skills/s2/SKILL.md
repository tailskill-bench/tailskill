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

Associates seismic phase picks (P and S waves) to earthquake events using Bayesian or standard Gaussian Mixture Models.

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

- `dbscan_eps` is obtained from `estimate_eps` Function

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

Estimates an appropriate DBSCAN epsilon (eps) parameter based on station spacing. Returns epsilon value in **seconds**.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stations` | DataFrame | required | Station metadata with 3D coordinates |
| `vp` | float | required | P-wave velocity in km/s |
| `sigma` | float | `2.0` | Number of standard deviations above the mean |

#### Required DataFrame Columns

| Column | Type | Description |
|--------|------|-------------|
| `x(km)` | float | X coordinate in km |
| `y(km)` | float | Y coordinate in km |
| `z(km)` | float | Z coordinate in km |

#### Example Usage

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

Seismograms (SAC, MiniSEED, GSE2, SEISAN, Q, etc.) are imported into a `Stream` object using `read()`. Streams contain multiple `Trace` objects (gap-less continuous time series with header/meta information).

### Stream and Trace Class Structure

**Hierarchy:** `Stream` → `Trace` (multiple)

**Trace attributes:**
- `data` → NumPy `ndarray` of the time series
- `stats` → dict-like `Stats` object containing:
  - `network`, `station`, `location`, `channel` — physical location and instrument
  - `starttime`, `sampling_rate`, `delta`, `endtime`, `npts` — interrelated timing

**Trace methods:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`

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
>>> tr.stats.starttime
UTCDateTime(2009, 8, 24, 0, 20, 3)
```

## Event Metadata

Event metadata use a class hierarchy modelled after [QuakeML](https://quake.ethz.ch/quakeml/). See `read_events()` and `Catalog.write()` for supported formats.

### Event Class Structure

**Hierarchy:** `Catalog` → `events` → `Event` (multiple)

**Event contains:**
- `origins` → `Origin` (multiple): `latitude`, `longitude`, `depth`, `time`, ...
- `magnitudes` → `Magnitude` (multiple): `mag`, `magnitude_type`, ...
- `picks`
- `focal_mechanisms`

## Station Metadata

Station metadata use a class hierarchy modelled after [FDSN StationXML](https://www.fdsn.org/xml/station/). See `read_inventory()` and `Inventory.write()` for supported formats.

### Inventory Class Structure

**Hierarchy:** `Inventory` → `networks` → `Network` → `stations` → `Station` → `channels` → `Channel`

- **Network:** `code`, `description`, ...
- **Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`, ...
- **Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`, ...

## Classes & Functions

| Class/Function | Description |
|----------------|-------------|
| `read` | Read waveform files into an ObsPy `Stream` object. |
| `Stream` | List-like object of multiple ObsPy `Trace` objects. |
| `Trace` | An object containing data of a continuous series, such as a seismic trace. |
| `Stats` | A container for additional header information of an ObsPy `Trace` object. |
| `UTCDateTime` | A UTC-based datetime object. |
| `read_events` | Read event files into an ObsPy `Catalog` object. |
| `Catalog` | Container for `Event` objects. |
| `Event` | Describes a seismic event which does not necessarily need to be a tectonic earthquake. |
| `read_inventory` | Function to read inventory files. |
| `Inventory` | The root object of the `Network` → `Station` → `Channel` hierarchy. |

## Modules

| Module | Description |
|--------|-------------|
| `obspy.core.trace` | Module for handling ObsPy `Trace` and `Stats` objects. |
| `obspy.core.stream` | Module for handling ObsPy `Stream` objects. |
| `obspy.core.utcdatetime` | Module containing a UTC-based datetime class. |
| `obspy.core.event` | Module handling event metadata. |
| `obspy.core.inventory` | Module for handling station metadata. |
| `obspy.core.util` | Various utilities for ObsPy. |
| `obspy.core.preview` | Tools for creating and merging previews. |

---

# SeisBench Model API

## Installing SeisBench
```
pip install seisbench
```

## Overview

SeisBench provides the abstract class `WaveformModel` that every model subclasses. It offers two core functions:

- **`annotate`** — Takes an obspy stream, returns annotations as a stream (e.g., pick probabilities over time):
```python
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)
```

- **`classify`** — Takes an obspy stream, returns discrete results (e.g., a list of picks):
```python
stream = obspy.read("my_waveforms.mseed")
outputs = model.classify(stream)
print(outputs)
```

Both functions handle waveforms from multiple stations at once, automatically grouping traces. Computations can be run on GPU by moving the model to GPU.

## Loading Pretrained Models

```python
import seisbench.models as sbm

sbm.PhaseNet.list_pretrained()                  # Get available models
model = sbm.PhaseNet.from_pretrained("original")  # Load original PhaseNet weights
```

Model weights are downloaded on first use and cached locally.

## Speeding Up Model Application

- **Run on GPU** — Usually faster, even for CPU-bound models.
- **Use a large `batch_size`** — Pass as optional argument; larger batches are faster on GPU.
- **Compile your model (torch 2.0+)** — `model = torch.compile(model)`.
- **Use asyncio interface** — `annotate_asyncio` and `classify_asyncio` load data in parallel.
- **Manual resampling** — Check required rate with `model.sampling_rate`; SeisBench uses non-parallelized obspy routines.

## Models Integrated into SeisBench

| Integrated Model | Task |
|------------------|------|
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

- If waveform data is extremely small in scale (`<=1e-10`), multiply by a large number (e.g., `1e10`) before normalization or passing to the model to avoid numerical instability.
- Apply normalization yourself. SeisBench's scheme `(waveform - mean(waveform)) / (std(waveform) + epsilon)` can destroy signals for extremely small values.
- The API can process streams of arbitrary length; do not segment data yourself. Treat the stream as continuous data — do not assume only one P-wave and one S-wave per stream.

---

# Seismic Event Detection & Phase Picking Method Selection Guide

## Method Tradeoffs

| Method | Generalizability | Sensitivity | Speed, Ease-of-Use | False Positives |
|--------|------------------|-------------|-------------------|-----------------|
| STA/LTA | High | Low | Fast, Easy | Many |
| Manual | High | High | Slow, Difficult | Few |
| Deep Learning | High | High | Fast, Easy | Medium |
| Template Matching | Low | High | Slow, Difficult | Few |

- **Generalizability**: Ability to find arbitrary earthquake signals
- **Sensitivity**: Ability to find small earthquakes

## STA/LTA (Short-Term Average / Long-Term Average)

- Runs very fast; operates in real-time
- Easy to understand & implement; optimize for different window lengths and ratios
- No prior knowledge needed about earthquake sources or waveforms
- Amplitude-based detector; reliably detects large earthquake signals
- **Limitations:** High rate of false detections during active sequences; automatic picks not as precise; requires manual review for a quality catalog

## Template Matching

- Optimally sensitive detector; can find smallest earthquakes buried in noise if similar enough to template waveform
- Excellent for improving temporal resolution of earthquake sequences
- False detections are less concerning when using high detection threshold
- **Limitations:** Requires template waveforms with good picks from a preexisting catalog; does not improve spatial resolution (unknown sources not similar to templates cannot be found); setup effort required; computationally intensive

## Deep Learning Pickers

- Adds most value when existing seismic networks are sparse or nonexistent
- Automatically and rapidly creates more complete catalog during active sequences
- Requires continuous seismic data
- Best on broadband stations, but also produces usable picks on accelerometers, nodals, and Raspberry Shakes
- No prior knowledge needed about earthquake sources or waveforms
- Finds lots of small local earthquakes with fewer false detections than STA/LTA
- Relatively easy to set up and run; SeisBench provides easy-to-use model APIs and pretrained models
- **Limitations:** Out-of-distribution data issues — expect larger automated pick errors (0.1-0.5 s) and missed picks for datasets not represented in training data; cannot pick phases completely buried in noise; sometimes misses picks from larger earthquakes that are obvious to humans