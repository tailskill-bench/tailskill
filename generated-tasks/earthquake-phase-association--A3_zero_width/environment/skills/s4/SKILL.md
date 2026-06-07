---
name: s1
description: "Earthquake phase association with GaMMA, ObsPy waveform/metadata APIs, SeisBench deep learning models, and picking method selection."
---

# GaMMA Associator

Install: `pip install git+https://github.com/wayneweiqiang/GaMMA.git`

## `association`

```python
def association(picks, stations, config, event_idx0=0, method="BGMM", **kwargs)
```

Associates phase picks to earthquake events using Bayesian (`"BGMM"`) or standard (`"GMM"`) Gaussian Mixture Models.

### Input DataFrames

**`picks`** — Required columns: `id` (str, matches stations), `timestamp` (datetime/ISO), `type` (`"p"` or `"s"`, lowercase), `prob` (float 0–1), `amp` (float m/s, required if `use_amplitude=True`). Timestamps must be UTC. Picks with `amp == 0` or `amp == -1` filtered when `use_amplitude=True`.

**`stations`** — Required columns: `id` (str), `x(km)` (float), `y(km)` (float), `z(km)` (float, elevation, typically negative). Coordinates in projected local system (e.g., `pyproj`). `id` must match picks. Group by unique `id`; identical attributes collapsed, conflicting metadata preserved as sorted list.

**Tail handling:** CSV files may contain invisible zero-width Unicode characters (category Cf) that corrupt column names/values. Filter with:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/stations.csv
```

### Config Dictionary

**Required:**

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Location dimensions | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Min picks per earthquake | `5` |
| `max_sigma11` | float | Max time residual (s) | `2.0` |
| `use_amplitude` | bool | Use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | BFGS bounds `((x_min, x_max), (y_min, y_max), (z_min, z_max), (None, None))` | `((-35, 92), (-128, 78), (0, 21), (None, None))` |
| `oversample_factor` | float | Oversampling GMM components | `5.0` (BGMM), `1.0` (GMM) |

`dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`. Last `bfgs_bounds` tuple is time (unbounded).

**Velocity Model:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `vel` | dict | `{"p": 6.0, "s": 3.47}` | Uniform velocity (km/s) |
| `eikonal` | dict/None | `None` | 1D velocity model for travel times |

**DBSCAN Pre-clustering (Optional):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `use_dbscan` | bool | `True` | Enable DBSCAN pre-clustering |
| `dbscan_eps` | float | `25` | Max time between picks (s) |
| `dbscan_min_samples` | int | `3` | Min samples in neighborhood |
| `dbscan_min_cluster_size` | int | `500` | Min cluster size for hierarchical splitting |
| `dbscan_max_time_space_ratio` | float | `10` | Max time/space ratio for splitting |

`dbscan_eps` obtained from `estimate_eps`.

**Filtering (Optional):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_sigma22` | float | `1.0` | Max amplitude residual (log scale) |
| `max_sigma12` | float | `1.0` | Max covariance |
| `max_sigma11` | float | `2.0` | Max time residual (s) |
| `min_p_picks_per_eq` | int | `0` | Min P-picks per event |
| `min_s_picks_per_eq` | int | `0` | Min S-picks per event |
| `min_stations` | int | `5` | Min unique stations per event |

**Other:** `covariance_prior` (list[float], auto), `ncpu` (int, auto).

### Returns

Tuple `(events, assignments)`.

**`events`** (list[dict]): `time` (ISO 8601), `magnitude` (999 if no amplitude), `sigma_time`, `sigma_amp`, `cov_time_amp`, `gamma_score`, `num_picks`, `num_p_picks`, `num_s_picks`, `event_index`, `x(km)`, `y(km)`, `z(km)`.

**`assignments`** (list[tuple]): `(pick_index, event_index, gamma_score)`.

## `estimate_eps`

```python
def estimate_eps(stations, vp, sigma=2.0)
```

Estimates DBSCAN epsilon from station spacing. `stations` needs `x(km)`, `y(km)`, `z(km)`. Returns epsilon in seconds (typical: 10–20).

```python
from gamma.utils import association, estimate_eps

config["dbscan_eps"] = estimate_eps(stations, config["vel"]["p"])
config["dbscan_min_samples"] = 3
config["dbscan_min_cluster_size"] = 500
config["dbscan_max_time_space_ratio"] = 10
```

# ObsPy Data API

## Waveforms

`read()` imports seismograms (SAC, MiniSEED, GSE2, SEISAN, Q, etc.) into `Stream`.

**Hierarchy:** `Stream` → `Trace` (multiple). **Trace data:** `data` (NumPy array), `stats` (`network`, `station`, `location`, `channel`, `starttime`, `sampling_rate`, `delta`, `endtime`, `npts`). **Trace methods:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`.

```python
>>> from obspy import read
>>> st = read()
>>> tr = st[0]
>>> tr.stats.starttime
UTCDateTime(2009, 8, 24, 0, 20, 3)
```

## Event Metadata (QuakeML)

**Hierarchy:** `Catalog` → `Event` (multiple). **Event contains:** `origins` → `Origin` (`latitude`, `longitude`, `depth`, `time`), `magnitudes` → `Magnitude` (`mag`, `magnitude_type`), `picks`, `focal_mechanisms`. See `read_events()`, `Catalog.write()`.

## Station Metadata (FDSN StationXML)

**Hierarchy:** `Inventory` → `Network` → `Station` → `Channel`. **Network:** `code`, `description`. **Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`. **Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`. See `read_inventory()`, `Inventory.write()`.

## Key Classes

`read` (waveforms→Stream), `Stream` (Trace container), `Trace` (continuous data), `UTCDateTime` (UTC datetime), `read_events` (→Catalog), `Catalog` (Event container), `read_inventory` (→Inventory), `Inventory` (Network→Station→Channel hierarchy).

# SeisBench Model API

Install: `pip install seisbench`

`WaveformModel` (abstract base) bridges PyTorch and ObsPy: assembles streams into tensors, handles batching, reassembles results.

**`annotate(stream)`** → ObsPy stream with annotations (e.g., pick probability functions). **`classify(stream)`** → discrete results (e.g., pick lists; model-dependent). Both handle multi-station streams and auto-group traces.

```python
import obspy, seisbench.models as sbm

model = sbm.PhaseNet.from_pretrained("original")
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)
outputs = model.classify(stream)
```

Weights download on first use, cached locally.

```python
sbm.PhaseNet.list_pretrained()                    # Available models
model = sbm.PhaseNet.from_pretrained("original")  # Load weights
```

## Performance Tips

GPU execution faster. Larger `batch_size` improves throughput (especially GPU). `torch.compile(model)` (torch 2.0+) amortizes compilation cost. `annotate_asyncio`/`classify_asyncio` overlap I/O and compute. Check `model.sampling_rate`; ObsPy resampling is single-threaded.

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

Waveforms with very small scale (`<=1e-10`) risk numerical instability. Multiply by large factor (e.g., `1e10`) before normalization. SeisBench normalizes via `(waveform - mean) / (std + epsilon)`, which destroys signals at tiny amplitudes. Pre-normalize yourself. Streams can be arbitrary length; do not segment manually. A stream may contain multiple P and S arrivals—treat as continuous data.

# Seismic Event Detection & Phase Picking Method Selection

## Method Tradeoffs

| Method | Generalizability | Sensitivity | Speed, Ease-of-Use | False Positives |
|--------|------------------|-------------|-------------------|-----------------|
| STA/LTA | High | Low | Fast, Easy | Many |
| Manual | High | High | Slow, Difficult | Few |
| Deep Learning | High | High | Fast, Easy | Medium |
| Template Matching | Low | High | Slow, Difficult | Few |

**Generalizability:** ability to find arbitrary earthquake signals. **Sensitivity:** ability to find small earthquakes.

**STA/LTA:** Fast, real-time capable; no prior knowledge needed; amplitude-based. High false positives during active sequences; picks less precise. Requires manual review for quality catalogs.

**Template Matching:** Most sensitive detector; finds smallest earthquakes buried in noise. Excellent temporal resolution; low false positives at high thresholds. Requires template waveforms with good picks from preexisting catalog. Does not improve spatial resolution; computationally intensive.

**Deep Learning Pickers:** Best value for sparse or nonexistent networks. Rapidly creates more complete catalogs during active sequences. Works on broadband, accelerometers, nodals, Raspberry Shakes. No prior knowledge needed; fewer false detections than STA/LTA. Easy setup via SeisBench pretrained models. Out-of-distribution data: expect 0.1–0.5 s pick errors and missed picks. Cannot pick phases completely buried in noise; less sensitive than template matching.