---
name: s1
description: "Earthquake phase association with GaMMA, ObsPy waveform/station/event APIs, and SeisBench deep learning picker models."
---

# GaMMA Associator

Install: `pip install git+https://github.com/wayneweiqiang/GaMMA.git`

## `association`

```python
def association(picks, stations, config, event_idx0=0, method="BGMM", **kwargs)
```

Associates phase picks to events using Bayesian (`"BGMM"`) or standard (`"GMM"`) Gaussian Mixture Models.

### Input DataFrames

**`picks`** columns: `id` (str, matches stations), `timestamp` (datetime/str, UTC ISO), `type` (`"p"` or `"s"`), `prob` (float 0-1), `amp` (float, m/s; required if `use_amplitude=True`). Picks with `amp==0` or `amp==-1` filtered when `use_amplitude=True`.

**`stations`** columns: `id` (str), `x(km)` (float), `y(km)` (float), `z(km)` (float, elevation, typically negative). Use projected local coordinates (e.g., `pyproj`).

Filter extreme outlier elevations via IQR:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/stations.csv 6
```
where `6` is column index of `elevation_m`.

### Config Dictionary

**Required:**

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Dimensions to solve | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Min picks per earthquake | `5` |
| `max_sigma11` | float | Max time residual (s) | `2.0` |
| `use_amplitude` | bool | Use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | BFGS bounds | `((-35,92),(-128,78),(0,21),(None,None))` |
| `oversample_factor` | float | GMM oversampling | `5.0` (BGMM), `1.0` (GMM) |

`dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`. `bfgs_bounds` format: `((x_min,x_max),(y_min,y_max),(z_min,z_max),(None,None))` — last tuple is time (unbounded).

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
| `dbscan_min_cluster_size` | int | `500` | Min cluster size for splitting |
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

**`events`** (list[dict]): `time` (str, ISO 8601 ms), `magnitude` (float, 999 if no amplitude), `sigma_time`, `sigma_amp`, `cov_time_amp`, `gamma_score`, `num_picks`, `num_p_picks`, `num_s_picks`, `event_index`, `x(km)`, `y(km)`, `z(km)`.

**`assignments`** (list[tuple]): `(pick_index, event_index, gamma_score)`.

## `estimate_eps`

```python
def estimate_eps(stations, vp, sigma=2.0)
```

Estimates DBSCAN epsilon from station spacing. Returns epsilon in **seconds**. Requires columns: `x(km)`, `y(km)`, `z(km)`.

```python
from gamma.utils import estimate_eps

config["dbscan_eps"] = estimate_eps(stations, config["vel"]["p"])
config["dbscan_min_samples"] = 3
config["dbscan_min_cluster_size"] = 500
config["dbscan_max_time_space_ratio"] = 10
```

# ObsPy Data API

## Waveforms

`read()` imports seismograms (SAC, MiniSEED, GSE2, etc.) into `Stream` containing `Trace` objects (gap-less continuous time series).

**Trace attributes:** `data` (NumPy ndarray), `stats` (dict-like: `network`, `station`, `location`, `channel`, `starttime`, `sampling_rate`, `delta`, `endtime`, `npts`). **Methods:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`.

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

## Event Metadata (QuakeML)

**Hierarchy:** `Catalog` → `Event` (multiple). **Event contains:** `origins` → `Origin` (`latitude`, `longitude`, `depth`, `time`), `magnitudes` → `Magnitude` (`mag`, `magnitude_type`), `picks`, `focal_mechanisms`. See `read_events()`, `Catalog.write()`.

## Station Metadata (FDSN StationXML)

**Hierarchy:** `Inventory` → `Network` → `Station` → `Channel`. **Network:** `code`, `description`. **Station:** `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`. **Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`. See `read_inventory()`, `Inventory.write()`.

## Key Classes

`read`, `Stream`, `Trace`, `Stats`, `UTCDateTime`, `read_events`, `Catalog`, `Event`, `read_inventory`, `Inventory`.

# SeisBench Model API

Install: `pip install seisbench`

`WaveformModel` is the abstract base class with two core functions:

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

# Seismic Event Detection & Phase Picking Method Selection

## Method Tradeoffs

| Method | Generalizability | Sensitivity | Speed, Ease-of-Use | False Positives |
|--------|------------------|-------------|-------------------|-----------------|
| STA/LTA | High | Low | Fast, Easy | Many |
| Manual | High | High | Slow, Difficult | Few |
| Deep Learning | High | High | Fast, Easy | Medium |
| Template Matching | Low | High | Slow, Difficult | Few |

## STA/LTA

Fast, real-time; easy to implement; no prior knowledge needed; amplitude-based detector for large signals. **Limitations:** High false detections during active sequences; automatic picks less precise; requires manual review.

## Template Matching

Most sensitive detector; finds smallest earthquakes buried in noise; excellent temporal resolution for earthquake sequences. **Limitations:** Requires template waveforms from preexisting catalog; no spatial resolution for unknown sources; computationally intensive.

## Deep Learning Pickers

Best value for sparse or nonexistent networks; rapidly creates complete catalogs during active sequences; works on broadband, accelerometers, nodals, and Raspberry Shakes; no prior knowledge needed; fewer false detections than STA/LTA; easy setup via SeisBench APIs and pretrained models. **Limitations:** Out-of-distribution data causes larger pick errors (0.1-0.5 s) and missed picks; cannot pick phases buried in noise; sometimes misses picks from large earthquakes obvious to humans.