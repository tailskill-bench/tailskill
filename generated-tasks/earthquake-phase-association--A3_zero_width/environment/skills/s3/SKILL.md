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

Associates phase picks to earthquake events using Bayesian or standard Gaussian Mixture Models.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `picks` | DataFrame | required | Seismic phase pick data |
| `stations` | DataFrame | required | Station metadata with locations |
| `config` | dict | required | Configuration parameters |
| `event_idx0` | int | `0` | Starting event index |
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

- Timestamps must be UTC or converted to UTC
- Phase types forced to lowercase internally
- Picks with `amp == 0` or `amp == -1` filtered when `use_amplitude=True`

##### `stations` DataFrame

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | str | Station identifier | `"CI.CCC..BH"`|
| `x(km)` | float | X coordinate in km (projected) | `-35.6` |
| `y(km)` | float | Y coordinate in km (projected) | `45.2` |
| `z(km)` | float | Z coordinate (elevation, typically negative) | `-0.67` |

- Coordinates in projected local system (e.g., via `pyproj`)
- `id` must match `id` values in picks DataFrame
- Group by unique `id`; identical attributes collapsed, conflicting metadata preserved as sorted list

**Tail handling:** CSV files may contain invisible zero-width Unicode characters (category Cf) that corrupt column names/values. Filter with:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/stations.csv
```

#### Config Dictionary Keys

##### Required Keys

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Location dimensions to solve | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Minimum picks per earthquake | `5` |
| `max_sigma11` | float | Max time residual (seconds) | `2.0` |
| `use_amplitude` | bool | Use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | BFGS optimization bounds | `((-35, 92), (-128, 78), (0, 21), (None, None))` |
| `oversample_factor` | float | Oversampling initial GMM components | `5.0` for `BGMM`, `1.0` for `GMM`|

- `dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`
- `bfgs_bounds` format: `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))` — last tuple for time (unbounded)

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

- `dbscan_eps` obtained from `estimate_eps` function

##### Filtering Keys (Optional)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_sigma22` | float | `1.0` | Max amplitude residual in log scale (if `use_amplitude=True`) |
| `max_sigma12` | float | `1.0` | Max covariance |
| `max_sigma11` | float | `2.0` | Max time residual (s) |
| `min_p_picks_per_eq` | int | `0` | Min P-phase picks per event |
| `min_s_picks_per_eq` | int | `0` | Min S-phase picks per event |
| `min_stations` | int | `5` | Min unique stations per event |

##### Other Optional Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `covariance_prior` | list[float] | auto | Prior for covariance `[time, amp]` |
| `ncpu` | int | auto | CPUs for parallel processing |

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

List of tuples `(pick_index, event_index, gamma_score)`:
- `pick_index`: Index in original `picks` DataFrame
- `event_index`: Associated event index
- `gamma_score`: Assignment probability/confidence

### `estimate_eps`

```python
def estimate_eps(stations, vp, sigma=2.0)
```

Estimates DBSCAN epsilon for clustering picks based on station spacing.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stations` | DataFrame | required | Station metadata with 3D coordinates |
| `vp` | float | required | P-wave velocity in km/s |
| `sigma` | float | `2.0` | Standard deviations above mean |

#### Required DataFrame Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `x(km)` | float | X coordinate in km | `-35.6` |
| `y(km)` | float | Y coordinate in km | `45.2` |
| `z(km)` | float | Z coordinate in km | `-0.67` |

#### Return Value

Returns epsilon in **seconds** for DBSCAN clustering. Typical range: 10–20 seconds.

#### Example Usage

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

Import seismograms (SAC, MiniSEED, GSE2, SEISAN, Q, etc.) into a `Stream` object via `read()`.

### Stream and Trace Class Structure

**Hierarchy:** `Stream` → `Trace` (multiple)

**Trace - DATA:**
- `data` → NumPy array
- `stats`:
  - `network`, `station`, `location`, `channel` — Physical location and instrument
  - `starttime`, `sampling_rate`, `delta`, `endtime`, `npts` — Interrelated

**Trace - METHODS:**
- `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`

### Example

```python
>>> from obspy import read
>>> st = read()
>>> tr = st[0]
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

**Network:** `code`, `description`, ...

**Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`, ...

**Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`, ...

## Key Classes & Functions

| Class/Function | Description |
|----------------|-------------|
| `read` | Read waveform files into `Stream`. |
| `Stream` | List-like container of `Trace` objects. |
| `Trace` | Continuous data series (seismic trace). |
| `UTCDateTime` | UTC-based datetime object. |
| `read_events` | Read event files into `Catalog`. |
| `Catalog` | Container for `Event` objects. |
| `read_inventory` | Read inventory files. |
| `Inventory` | Root of Network → Station → Channel hierarchy. |

---

# SeisBench Model API

## Installing SeisBench
```
pip install seisbench
```

## Core Functions

`WaveformModel` is the abstract base class. It bridges PyTorch and ObsPy: assembles streams into tensors, handles batching, and reassembles results.

**`annotate(stream)`** → Returns ObsPy stream with annotations (e.g., pick probability functions over time).

**`classify(stream)`** → Returns discrete results (e.g., list of picks; model-dependent structure).

Both handle multi-station streams and auto-group traces.

```python
import obspy, seisbench.models as sbm

model = sbm.PhaseNet.from_pretrained("original")
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)
outputs = model.classify(stream)
```

## Loading Pretrained Models

Weights download on first use, cached locally.

```python
sbm.PhaseNet.list_pretrained()                    # Available models
model = sbm.PhaseNet.from_pretrained("original")  # Load weights
```

## Performance Tips

- **GPU:** Move model to GPU for faster execution.
- **`batch_size`:** Larger values improve throughput, especially on GPU.
- **`torch.compile(model)`** (torch 2.0+): Compilation cost amortizes over large datasets.
- **Async:** `annotate_asyncio` / `classify_asyncio` overlap I/O and compute.
- **Manual resampling:** Check `model.sampling_rate`; ObsPy resampling is single-threaded.

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
| `EQTransformer` | Detection/Phase Picking |
| `GPD` | Phase Picking |
| `LFEDetect` | Phase Picking (Low-frequency earthquakes) |
| `OBSTransformer` | Detection/Phase Picking |
| `PhaseNet` | Phase Picking |
| `PhaseNetLight` | Phase Picking |
| `PickBlue` | Detection/Phase Picking |
| `Skynet` | Phase Picking |
| `VariableLengthPhaseNet` | Phase Picking |

## Critical Constraints

- Waveforms with very small scale (`<=1e-10`) risk numerical instability. Multiply by a large factor (e.g., `1e10`) before normalization.
- SeisBench normalizes via `(waveform - mean) / (std + epsilon)`, which can destroy signals at tiny amplitudes. Pre-normalize yourself.
- Streams can be arbitrary length; do not segment manually. A stream may contain multiple P and S arrivals—treat it as continuous data.

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

- Fast, real-time capable; easy to implement
- No prior knowledge needed; amplitude-based
- High false positives during active sequences; picks less precise
- Requires manual review for quality catalogs

## Template Matching

- Most sensitive detector; finds smallest earthquakes buried in noise
- Excellent temporal resolution for sequences; low false positives at high thresholds
- Requires template waveforms with good picks from preexisting catalog
- Does not improve spatial resolution; computationally intensive

## Deep Learning Pickers

- Best value for sparse or nonexistent networks
- Rapidly creates more complete catalogs during active sequences
- Works on broadband, accelerometers, nodals, Raspberry Shakes
- No prior knowledge needed; fewer false detections than STA/LTA
- Easy setup via SeisBench pretrained models
- Out-of-distribution data: expect 0.1–0.5 s pick errors and missed picks
- Cannot pick phases completely buried in noise; less sensitive than template matching