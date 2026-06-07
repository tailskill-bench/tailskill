---
name: s1
description: "Earthquake phase association using GaMMA, ObsPy waveform/metadata APIs, SeisBench deep learning models, and seismic picking method selection."
---

# GaMMA Associator

Install: `pip install git+https://github.com/wayneweiqiang/GaMMA.git`

## `association`

```python
def association(picks, stations, config, event_idx0=0, method="BGMM", **kwargs)
```

Associates phase picks to earthquake events using Bayesian (`"BGMM"`) or standard (`"GMM"`) Gaussian Mixture Models. Clusters picks by arrival time and amplitude, fits GMMs to estimate locations, times, and magnitudes.

### Input DataFrames

**`picks`** columns: `id` (str, matches stations), `timestamp` (datetime/str, UTC), `type` (`"p"` or `"s"`, lowercase), `prob` (float 0–1), `amp` (float, m/s; required if `use_amplitude=True`). Picks with `amp==0` or `amp==-1` are filtered when `use_amplitude=True`.

**`stations`** columns: `id` (str), `x(km)` (float), `y(km)` (float), `z(km)` (float, typically negative). Coordinates in projected local system (e.g., via `pyproj`). `id` must match picks.

**Tail handling** — fix output directory permissions before running:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py
```

### Config Dictionary

**Required keys:**

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `dims` | list[str] | Dimensions to solve | `["x(km)", "y(km)", "z(km)"]` |
| `min_picks_per_eq` | int | Min picks per earthquake | `5` |
| `max_sigma11` | float | Max time residual (s) | `2.0` |
| `use_amplitude` | bool | Use amplitude in clustering | `True` |
| `bfgs_bounds` | tuple | BFGS bounds `((x_min,x_max),(y_min,y_max),(z_min,z_max),(None,None))` | `((-35,92),(-128,78),(0,21),(None,None))` |
| `oversample_factor` | float | Oversampling factor | `5.0` (BGMM), `1.0` (GMM) |

`dims` options: `["x(km)", "y(km)", "z(km)"]`, `["x(km)", "y(km)"]`, or `["x(km)"]`. Last tuple in `bfgs_bounds` is time (unbounded).

**Velocity model:** `vel` (dict, default `{"p": 6.0, "s": 3.47}`) for uniform model; `eikonal` (dict/None) for 1D travel times.

**DBSCAN pre-clustering:** `use_dbscan` (bool, default `True`), `dbscan_eps` (float, default `25`, from `estimate_eps`), `dbscan_min_samples` (int, default `3`), `dbscan_min_cluster_size` (int, default `500`), `dbscan_max_time_space_ratio` (float, default `10`).

**Filtering:** `max_sigma22` (float, default `1.0`, max amplitude residual in log scale), `max_sigma12` (float, default `1.0`, max covariance), `min_p_picks_per_eq` (int, default `0`), `min_s_picks_per_eq` (int, default `0`), `min_stations` (int, default `5`).

**Other:** `covariance_prior` (list[float], auto), `ncpu` (int, auto).

### Return Values

Returns `(events, assignments)`.

**`events`** (list[dict]): `time` (str, ISO 8601), `magnitude` (float, 999 if no amplitude), `sigma_time`, `sigma_amp`, `cov_time_amp`, `gamma_score`, `num_picks`, `num_p_picks`, `num_s_picks`, `event_index`, `x(km)`, `y(km)`, `z(km)`.

**`assignments`** (list[tuple]): `(pick_index, event_index, gamma_score)`.

## `estimate_eps`

```python
def estimate_eps(stations, vp, sigma=2.0)
```

Estimates DBSCAN epsilon in **seconds** from station spacing. `stations` needs `x(km)`, `y(km)`, `z(km)`; `vp` is P-wave velocity (km/s); `sigma` is std deviations above mean.

```python
from gamma.utils import estimate_eps

vp = 6.0
eps = estimate_eps(stations, vp, sigma=2.0)
config = {
    "use_dbscan": True,
    "dbscan_eps": eps,
    "dbscan_min_samples": 3,
}
```

# ObsPy Data API

## Waveforms

`read()` imports seismograms (SAC, MiniSEED, GSE2, etc.) into a `Stream` of `Trace` objects.

**Trace attributes:** `data` (NumPy ndarray), `stats` (dict-like: `network`, `station`, `location`, `channel`, `starttime`, `sampling_rate`, `delta`, `endtime`, `npts`). **Trace methods:** `taper()`, `filter()`, `resample()`, `integrate()`, `remove_response()`.

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

**Hierarchy:** `Catalog` → `Event` (multiple). Event contains: `origins` → `Origin` (`latitude`, `longitude`, `depth`, `time`), `magnitudes` → `Magnitude` (`mag`, `magnitude_type`), `picks`, `focal_mechanisms`.

## Station Metadata (FDSN StationXML)

**Hierarchy:** `Inventory` → `Network` → `Station` → `Channel`. Network: `code`, `description`. Station: `code`, `latitude`, `longitude`, `elevation`, `start_date`, `end_date`. Channel: `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `dip`, `azimuth`, `sample_rate`, `start_date`, `end_date`, `response`.

## Key Classes

`read`, `Stream`, `Trace`, `Stats`, `UTCDateTime`, `read_events`, `Catalog`, `Event`, `read_inventory`, `Inventory`

# SeisBench Model API

Install: `pip install seisbench`

Abstract class `WaveformModel` — all models subclass it. Two core functions:
- **`annotate(stream)`** → annotations as obspy stream (e.g., pick probabilities)
- **`classify(stream)`** → discrete results (e.g., list of picks)

Both handle multi-station waveforms and auto-group traces.

```python
stream = obspy.read("my_waveforms.mseed")
annotations = model.annotate(stream)
outputs = model.classify(stream)
```

## Loading Pretrained Models

Weights download on first use and cache locally.

```python
import seisbench.models as sbm

sbm.PhaseNet.list_pretrained()                    # List available models
model = sbm.PhaseNet.from_pretrained("original")  # Load pretrained weights
```

## Speed Tips

GPU execution, large `batch_size` (especially GPU), `torch.compile(model)` (torch 2.0+), async interface (`annotate_asyncio`, `classify_asyncio`), manual resampling to match `model.sampling_rate`.

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

- Waveform data ≤1e-10: multiply by large number (e.g., `1e10`) before normalization to avoid numerical instability
- Apply normalization yourself — SeisBench's `(waveform - mean) / (std + epsilon)` can destroy signals for very small values
- SeisBench handles arbitrary-length streams; no manual segmentation needed
- Do not assume one P-wave and one S-wave per stream — treat as continuous data

# Seismic Event Detection & Phase Picking Method Selection

## Method Tradeoffs

| Method | Generalizability | Sensitivity | Speed, Ease-of-Use | False Positives |
|--------|------------------|-------------|-------------------|-----------------|
| STA/LTA | High | Low | Fast, Easy | Many |
| Manual | High | High | Slow, Difficult | Few |
| Deep Learning | High | High | Fast, Easy | Medium |
| Template Matching | Low | High | Slow, Difficult | Few |

**Generalizability:** ability to find arbitrary earthquake signals. **Sensitivity:** ability to find small earthquakes.

## STA/LTA

Fast real-time operation, easy to implement, no prior knowledge needed, reliably detects large signals. High false detection rate during active sequences, automatic picks less precise, requires manual review for quality catalogs.

## Template Matching

Most sensitive detector — finds smallest earthquakes buried in noise (if similar to template). Excellent temporal resolution. Few false detections at high thresholds. Requires template waveforms with good picks from preexisting catalog. Does not improve spatial resolution — unknown sources unlike templates won't be found. Computationally intensive setup.

## Deep Learning Pickers

Use for sparse or nonexistent networks, active sequences needing rapid catalogs, temporary broadband/nodal deployments. Requires continuous seismic data. Works best on broadband stations but produces usable picks on accelerometers, nodals, and Raspberry Shakes. No prior knowledge needed, finds small local earthquakes with fewer false detections than STA/LTA, easy setup via SeisBench APIs and pretrained models. Out-of-distribution data causes larger pick errors (0.1–0.5 s) and missed picks. Cannot pick phases completely buried in noise (less sensitive than template matching). Sometimes misses picks from larger earthquakes obvious to humans.