---
name: s1
description: Combined skills for flood-risk-analysis with network retry guidance. Includes flood detection, NWS flood thresholds, and USGS data download.
---

# Flood Detection Guide

## Flood Stage Definition

NWS flood stage is the water level at which overflow of the natural banks begins to cause damage. A flood event occurs when:

```
water_level >= flood_stage_threshold
```

## Aggregating Instantaneous Data to Daily

USGS instantaneous data is recorded at ~15-minute intervals. For flood detection, aggregate to daily maximum:

```python
# df is DataFrame from nwis.get_iv() with datetime index
# gage_col is the column name containing water levels

daily_max = df[gage_col].resample('D').max()
```

Use `max()` for flood detection (captures peak water level). Use `mean()` for long-term trends (may miss short flood peaks).

## Detecting Flood Days

Compare daily maximum water level against flood threshold:

```python
flood_threshold = <threshold_from_nws>  # feet

# Count days with flooding
flood_days = (daily_max >= flood_threshold).sum()

# Get specific dates with flooding
flood_dates = daily_max[daily_max >= flood_threshold].index.tolist()
```

## Processing Multiple Stations

```python
flood_results = []

for site_id, site_data in all_data.items():
    daily_max = site_data['water_levels'].resample('D').max()
    threshold = thresholds[site_id]['flood']

    days_above = int((daily_max >= threshold).sum())

    if days_above > 0:
        flood_results.append({
            'station_id': site_id,
            'flood_days': days_above
        })

# Sort by flood days descending
flood_results.sort(key=lambda x: x['flood_days'], reverse=True)
```

### Simple CSV Output

```python
import csv

with open('flood_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['station_id', 'flood_days'])
    for result in flood_results:
        writer.writerow([result['station_id'], result['flood_days']])
```

> **TailSkills: Handling Network Unreliability**
>
> DNS resolution may be intermittently unreliable in this environment. When making network requests (e.g., downloading NWS or USGS data), always use retry logic:
>
> ```python
> from tenacity import retry, stop_after_attempt, wait_exponential
>
> @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
> def download_with_retry(url):
>     import urllib.request
>     return urllib.request.urlopen(url, timeout=30)
> ```
>
> Alternatively, implement manual retry:
> ```python
> import time, urllib.request
>
> def fetch_with_retry(url, max_retries=5):
>     for attempt in range(max_retries):
>         try:
>             return urllib.request.urlopen(url, timeout=30)
>         except Exception as e:
>             if attempt == max_retries - 1:
>                 raise
>             time.sleep(2 ** attempt)
> ```
>
> Apply this to ALL network calls: NWS CSV downloads, USGS API requests, and any other HTTP requests.

---

# NWS Flood Thresholds Guide

## Data Sources

### Option 1: Bulk CSV Download (Recommended for Multiple Stations)
```
https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv
```

### Option 2: Individual Station Pages
```
https://water.noaa.gov/gauges/<station_id>
```

## Flood Stage Categories

| Category | CSV Column | Description |
|----------|------------|-------------|
| Action Stage | `action stage` | Water level requiring monitoring |
| **Flood Stage (Minor)** | **`flood stage`** | **Use this to determine if flooding occurred.** |
| Moderate Flood Stage | `moderate flood stage` | Structure inundation |
| Major Flood Stage | `major flood stage` | Extensive damage |

## Downloading Bulk CSV

**Important: CSV Column Mismatch** — The NWS CSV has a known issue: header row has 43 columns but data rows have 44 columns. Always truncate data rows to match header count.

```python
import pandas as pd
import csv
import urllib.request
import io

nws_url = "https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv"

response = urllib.request.urlopen(nws_url)
content = response.read().decode('utf-8')
reader = csv.reader(io.StringIO(content))
headers = next(reader)
data = [row[:43] for row in reader]
nws_df = pd.DataFrame(data, columns=headers)
```

## Key Columns

| Column Name | Description |
|-------------|-------------|
| `usgs id` | USGS station ID (8-digit string) |
| `location name` | Station name/location |
| `state` | Two-letter state code |
| `action stage` | Action threshold (feet) |
| `flood stage` | Minor flood threshold (feet) |

## Converting to Numeric

```python
nws_df['flood stage'] = pd.to_numeric(nws_df['flood stage'], errors='coerce')
```

## Filtering by State

```python
state_stations = nws_df[
    (nws_df['state'] == '<STATE_CODE>') &
    (nws_df['usgs id'].notna()) &
    (nws_df['usgs id'] != '') &
    (nws_df['flood stage'].notna()) &
    (nws_df['flood stage'] != -9999)
]
```

## Matching Thresholds to Station IDs

```python
station_ids = ['<id_1>', '<id_2>', '<id_3>']
thresholds = {}

for _, row in nws_df.iterrows():
    usgs_id = str(row['usgs id']).strip()
    if usgs_id in station_ids:
        thresholds[usgs_id] = {
            'name': row['location name'],
            'flood': row['flood stage']
        }
```

---

# USGS Data Download Guide

## Installation
```bash
pip install dataretrieval
```

## nwis Module (Recommended)
```python
from dataretrieval import nwis

# Get instantaneous values (15-min intervals)
df, meta = nwis.get_iv(
    sites='<station_id>',
    start='<start_date>',
    end='<end_date>',
    parameterCd='00065'
)
```

## Parameter Codes

| Code | Parameter | Unit |
|------|-----------|------|
| `00065` | Gage height | feet |
| `00060` | Discharge | cfs |

## Downloading Multiple Stations

```python
from dataretrieval import nwis

station_ids = ['<id_1>', '<id_2>', '<id_3>']
all_data = {}

for site_id in station_ids:
    try:
        df, meta = nwis.get_iv(
            sites=site_id,
            start='<start_date>',
            end='<end_date>',
            parameterCd='00065'
        )
        if len(df) > 0:
            all_data[site_id] = df
    except Exception as e:
        print(f"Failed to download {site_id}: {e}")

print(f"Successfully downloaded: {len(all_data)} stations")
```

## Extracting the Value Column

```python
gage_col = [c for c in df.columns if '00065' in str(c) and '_cd' not in str(c)]
if gage_col:
    water_levels = df[gage_col[0]]