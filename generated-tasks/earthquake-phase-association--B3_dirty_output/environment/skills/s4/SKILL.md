---
name: s1
description: "Earthquake phase association using GaMMA, ObsPy data API, SeisBench models, and picking method selection."
---

# GaMMA Associator

Install: `pip install git+https://github.com/wayneweiqiang/GaMMA.git`

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

- Phase types forced to lowercase internally
- Picks with `amp == 0` or `amp == -1` filtered when `use_amplitude=True`

### `stations` DataFrame Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Station identifier (e.g. `"CI.CCC..BH"`) |
| `x(km)` | float | X coordinate in km (projected) |
| `y(km)` | float | Y coordinate in km (projected) |
| `z(km)` | float | Z coordinate (elevation, typically negative) |

- Coordinates in projected local system (e.g., via `pyproj`)
- Group by unique `id`; identical attributes collapsed, conflicting preserved as sorted list

**Remove stale output before running:**
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py
```

### Config Dictionary

**Required keys:**

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Location dimensions | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Min picks per earthquake | `5` |
| `max_sigma11` | float | Max time residual (seconds) | `2.0` |
| `use_amplitude` | bool | Use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | BFGS bounds `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))` | `((-35, 92), (-128, 78), (0, 21), (None, None))` |
| `oversample_factor` | float | Oversampling for initial GMM | `5.0` (BGMM), `1.0` (GMM) |

- `dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`

**Velocity model:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `vel` | dict | `{"p": 6.0, "s": 3.47}` | Uniform velocity model (km/s) |
| `eikonal` | dict/None | `None` | 1D velocity model for travel times |

**DBSCAN pre-clustering (optional):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_dbscan` | bool | `True` | Enable DBSCAN pre-clustering |
| `dbscan_eps` | float | `25` | Max time between picks (seconds) |
| `dbscan_min_samples` | int | `3` | Min samples in neighborhood |
| `dbscan_min_cluster_size` | int | `500` | Min cluster size for hierarchical splitting |
| `dbscan_max_time_space_ratio` | float | `10` | Max time/space ratio for splitting |

**Filtering (optional):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_sigma22` | float | `1.0` | Max amplitude residual (log scale) |
| `max_sigma12` | float | `1.0` | Max covariance |
| `min_p_picks_per_eq` | int | `0` | Min P-phase picks per event |
| `min_s_picks_per_eq` | int | `0` | Min S-phase picks per event |
| `min_stations` | int | `5` | Min unique stations per event |

**Other optional:** `covariance_prior` (list[float], auto), `ncpu` (int, auto)

### Return Values

Returns tuple `(events, assignments)`.

**`events` (list[dict]):** Keys: `time` (ISO 8601), `magnitude` (999 if `use_amplitude=False`), `sigma_time`, `sigma_amp`, `cov_time_amp`, `gamma_score`, `num_picks`, `num_p_picks`, `num_s_picks`, `event_index`, `x(km)`, `y(km)`, `z(km)`

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

# ObsPy Data API

**Waveform hierarchy:** `Stream` → `Trace` (multiple). Trace data: `data` (NumPy array), `stats` (`network`, `station`, `location`, `channel`, `starttime`, `sampling_rate`, `delta`, `endtime`, `npts`). Methods: `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`.

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

**Event hierarchy:** `Catalog` → `Event` (multiple). Event contains: `origins` → `Origin` (`latitude`, `longitude`, `depth`, `time`), `magnitudes` → `Magnitude` (`mag`, `magnitude_type`), `picks`, `focal_mechanisms`.

**Station hierarchy:** `Inventory` → `Network` → `Station` → `Channel`. Network: `code`, `description`. Station: `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`. Channel: `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`.

**Key classes:** `read`, `Stream`, `Trace`, `Stats`, `UTCDateTime`, `read_events`, `Catalog`, `Event`, `read_inventory`, `Inventory`

# SeisBench Model API

Install: `pip install seisbench`

`WaveformModel` is the abstract base class with two core functions:

- **`annotate(stream)`** → annotation stream (e.g., pick probabilities over time)
- **`classify(stream)`** → discrete results (e.g., list of picks)

```python
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)
outputs = model.classify(stream)
```

Both handle multi-station waveforms and auto-group traces.

```python
import seisbench.models as sbm

sbm.PhaseNet.list_pretrained()
model = sbm.PhaseNet.from_pretrained("original")
```

Weights download on first use, cached locally.

**Integrated models:** `BasicPhaseAE`, `CRED`, `DPP`, `DepthPhaseNet`, `DepthPhaseTEAM`, `DeepDenoiser`, `SeisDAE`, `EQTransformer`, `GPD`, `LFEDetect`, `OBSTransformer`, `PhaseNet`, `PhaseNetLight`, `PickBlue`, `Skynet`, `VariableLengthPhaseNet`

**Best practices:** If waveforms extremely small (`<=1e-10`), multiply by large number (e.g., `1e10`) before normalization. Built-in normalization `(waveform - mean) / (std + epsilon)` can destroy signals for extremely small values. API processes arbitrary-length streams; no need to segment. Do not assume one P and one S per stream.

# Seismic Event Detection & Phase Picking Method Selection

| Method | Generalizability | Sensitivity | Speed, Ease-of-Use | False Positives |
|--------|------------------|-------------|-------------------|-----------------|
| STA/LTA | High | Low | Fast, Easy | Many |
| Manual | High | High | Slow, Difficult | Few |
| Deep Learning | High | High | Fast, Easy | Medium |
| Template Matching | Low | High | Slow, Difficult | Few |

**STA/LTA:** Fast, real-time capable; no prior knowledge needed. Amplitude-based: reliably detects large signals. **Limitations:** High false detections during active sequences; automatic picks less precise; requires manual review.

**Template Matching:** Most sensitive: finds smallest earthquakes buried in noise (if similar to template). Excellent temporal resolution; high threshold reduces false detections. **Limitations:** Requires template waveforms with good picks from preexisting catalog; no spatial resolution improvement; setup effort; computationally intensive.

**Deep Learning Pickers:** Best value for sparse/nonexistent networks; rapidly creates complete catalogs during active sequences. Requires continuous data; works best on broadband, also usable on accelerometers, nodals, Raspberry Shakes. No prior knowledge needed; finds small local earthquakes (lower Mc) with fewer false positives than STA/LTA. Easy setup via SeisBench. **Limitations:** Out-of-distribution data causes larger errors (0.1-0.5 s) and missed picks; cannot pick phases buried in noise (less sensitive than template matching); sometimes misses picks from large earthquakes obvious to humans.