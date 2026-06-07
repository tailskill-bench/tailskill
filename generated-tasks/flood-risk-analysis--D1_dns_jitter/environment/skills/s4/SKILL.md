---
name: s1
description: Flood risk with NWS thresholds, USGS data, and network retry.
---

# Flood Detection

## Aggregating Instantaneous Data

```python
daily_max = df[gage_col].resample('D').max()
```

Use `max()` for flood detection (captures peak). Use `mean()` for long-term trends (may miss short flood peaks).

## Detecting Flood Days

```python
flood_threshold = <threshold_from_nws>  # feet
flood_days = (daily_max >= flood_threshold).sum()
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
        flood_results.append({'station_id': site_id, 'flood_days': days_above})
flood_results.sort(key=lambda x: x['flood_days'], reverse=True)
```

## Network Retry

DNS resolution may be unreliable. Use retry logic for network calls:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
def download_with_retry(url):
    import urllib.request
    return urllib.request.urlopen(url, timeout=30)
```

# NWS Flood Thresholds

## Data Sources

Bulk CSV (recommended):
```
https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv
```

Individual station: `https://water.noaa.gov/gauges/<station_id>`

## Flood Stage Categories

| Category | CSV Column | Description |
|----------|------------|-------------|
| Action Stage | `action stage` | Water level requiring monitoring |
| **Flood Stage** | **`flood stage`** | **Use for flood detection** |
| Moderate | `moderate flood stage` | Structure inundation |
| Major | `major flood stage` | Extensive damage |

## Downloading Bulk CSV

**CSV Column Mismatch** — Header has 43 columns but data rows have 44. Truncate data rows to match header.

```python
import pandas as pd, csv, urllib.request, io

nws_url = "https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv"
response = urllib.request.urlopen(nws_url)
content = response.read().decode('utf-8')
reader = csv.reader(io.StringIO(content))
headers = next(reader)
data = [row[:43] for row in reader]
nws_df = pd.DataFrame(data, columns=headers)
```

## Key Columns

| `usgs id` | USGS station ID (8-digit string) |
| `location name` | Station name/location |
| `state` | Two-letter state code |
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

## Matching Thresholds

```python
station_ids = ['<id_1>', '<id_2>', '<id_3>']
thresholds = {}
for _, row in nws_df.iterrows():
    usgs_id = str(row['usgs id']).strip()
    if usgs_id in station_ids:
        thresholds[usgs_id] = {'name': row['location name'], 'flood': row['flood stage']}
```

# USGS Data Download

## Installation
```bash
pip install dataretrieval
```

## nwis Module
```python
from dataretrieval import nwis

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
        df, meta = nwis.get_iv(sites=site_id, start='<start_date>', end='<end_date>', parameterCd='00065')
        if len(df) > 0:
            all_data[site_id] = df
    except Exception as e:
        print(f"Failed to download {site_id}: {e}")
print(f"Successfully downloaded: {len(all_data)} stations")
```

## Extracting Value Column

```python
gage_col = [c for c in df.columns if '00065' in str(c) and '_cd' not in str(c)]
if gage_col:
    water_levels = df[gage_col[0]]