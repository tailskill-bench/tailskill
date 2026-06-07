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
| `prob` | float | Pick probability/weight (0–1) | `0.94` |
| `amp` | float | Amplitude in m/s (required if `use_amplitude=True`) | `0.000017` |

- Timestamps must be in UTC or converted to UTC.
- Phase types are forced to lowercase internally.
- Picks with `amp == 0` or `amp == -1` are filtered when `use_amplitude=True`.

##### `stations` DataFrame

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | str | Station identifier | `"CI.CCC..BH"` |
| `x(km)` | float | X coordinate in km (projected) | `-35.6` |
| `y(km)` | float | Y coordinate in km (projected) | `45.2` |
| `z(km)` | float | Z coordinate (elevation, typically negative) | `-0.67` |

- Coordinates should be in a projected local coordinate system (e.g., via `pyproj`).
- The `id` column must match the `id` values in the picks DataFrame.
- Group stations by unique `id`; identical attributes are collapsed to a single value and conflicting metadata are preserved as a sorted list.

**BOM handling:** Station CSV files may contain a UTF-8 BOM causing the first column header to be misread (e.g., `'\xef\xbb\xbf'` prefix). Strip it before reading:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/stations.csv
```

#### Config Dictionary Keys

##### Required Keys

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Location dimensions to solve for | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Minimum picks required per earthquake | `5` |
| `max_sigma11` | float | Maximum allowed time residual in seconds | `2.0` |
| `use_amplitude` | bool | Whether to use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | Bounds for BFGS optimization | `((-35, 92), (-128, 78), (0, 21), (None, None))` |
| `oversample_factor` | float | Factor for oversampling initial GMM components | `5.0` for `BGMM`, `1.0` for `GMM` |

- **`dims` options:** `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`.
- **`bfgs_bounds` format:** `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))`. The last tuple is for time (unbounded).

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

- `dbscan_eps` is obtained from `estimate_eps`.

##### Filtering Keys (Optional)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_sigma22` | float | `1.0` | Max phase amplitude residual in log scale (required if `use_amplitude=True`) |
| `max_sigma12` | float | `1.0` | Max covariance |
| `max_sigma11` | float | `2.0` | Max phase time residual (s) |
| `min_p_picks_per_eq` | int | `0` | Min P-phase picks per event |
| `min_s_picks_per_eq` | int | `0` | Min S-phase picks per event |
| `min_stations` | int | `5` | Min unique stations per event |

#### Return Values

Returns a tuple `(events, assignments)`.

##### `events` (list[dict])

Each dict represents an associated earthquake:

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

Estimates an appropriate DBSCAN epsilon parameter based on station spacing.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stations` | DataFrame | required | Station metadata with `x(km)`, `y(km)`, `z(km)` columns |
| `vp` | float | required | P-wave velocity in km/s |
| `sigma` | float | `2.0` | Number of standard deviations above the mean |

Returns a float: epsilon value in **seconds** for use with DBSCAN clustering.

```python
from gamma.utils import estimate_eps

eps = estimate_eps(stations, vp=6.0, sigma=2.0)
config = {"use_dbscan": True, "dbscan_eps": eps, "dbscan_min_samples": 3}
```

---

# ObsPy Data API

## Waveform Data

### Stream and Trace

**Hierarchy:** `Stream` → `Trace` (multiple)

**Trace data:**
- `data` → NumPy array
- `stats`: `network`, `station`, `location`, `channel`, `starttime`, `sampling_rate`, `delta`, `endtime`, `npts`

**Trace methods:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`

```python
from obspy import read
st = read()
tr = st[0]
tr.data          # NumPy array
tr.stats.starttime  # UTCDateTime
```

## Event Metadata

**Hierarchy:** `Catalog` → `events` → `Event` (multiple)

**Event contains:**
- `origins` → `Origin`: `latitude`, `longitude`, `depth`, `time`
- `magnitudes` → `Magnitude`: `mag`, `magnitude_type`
- `picks`, `focal_mechanisms`

## Station Metadata

**Hierarchy:** `Inventory` → `networks` → `Network` → `stations` → `Station` → `channels` → `Channel`

- **Network:** `code`, `description`
- **Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`
- **Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`

## Key Classes & Functions

| Class/Function | Description |
|----------------|-------------|
| `read` | Read waveform files into a `Stream` object |
| `Stream` | List-like container of `Trace` objects |
| `Trace` | Continuous seismic data series |
| `UTCDateTime` | UTC-based datetime object |
| `read_events` | Read event files into a `Catalog` object |
| `Catalog` | Container for `Event` objects |
| `read_inventory` | Read station inventory files |
| `Inventory` | Root of the Network → Station → Channel hierarchy |

---

# SeisBench Model API

## Installing SeisBench
```
pip install seisbench
```

## Core Functions

SeisBench models subclass `WaveformModel`, which provides two core functions:

- **`annotate(stream)`** → returns an ObsPy `Stream` of annotations (e.g., pick probability characteristic functions over time).
- **`classify(stream)`** → returns discrete results (e.g., a list of picks; model-dependent structure).

```python
import seisbench.models as sbm

model = sbm.PhaseNet.from_pretrained("original")
annotations = model.annotate(stream)
outputs = model.classify(stream)
```

## Loading Pretrained Models

```python
sbm.PhaseNet.list_pretrained()                    # List available models
model = sbm.PhaseNet.from_pretrained("original")  # Load weights (downloaded on first use, cached locally)
```

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

## Critical Constraints

- If waveform data is extremely small in scale (`<=1e-10`), multiply by a large factor (e.g., `1e10`) before normalization to avoid numerical instability.
- SeisBench normalizes as `(waveform - mean) / (std + epsilon)`. For very small values this can destroy signals; apply your own normalization when in doubt.
- The API processes arbitrary-length streams; do not assume only one P-wave and one S-wave per stream. Treat it as continuous data.

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

- Fast, real-time capable; easy to implement and tune (window lengths, ratios).
- No prior knowledge of earthquake sources required.
- High false detection rate during active sequences; automatic picks less precise; requires manual review for quality catalogs.

## Template Matching

- Most sensitive detector for small earthquakes buried in noise (if similar to template).
- Excellent temporal resolution for earthquake sequences.
- Requires template waveforms with good picks from a preexisting catalog.
- Does not improve spatial resolution for events dissimilar to templates.
- Computationally intensive; significant setup effort.

## Deep Learning Pickers

- Best value when networks are sparse or nonexistent; rapidly creates more complete catalogs during active sequences.
- No prior knowledge needed; fewer false detections than STA/LTA; lower magnitude of completeness.
- Best on broadband stations, but usable on accelerometers, nodals, and Raspberry Shakes.
- Out-of-distribution data causes larger pick errors (0.1–0.5 s) and missed picks.
- Not as sensitive as template matching for events buried in noise.
- May occasionally miss picks from large earthquakes that are obvious to humans.