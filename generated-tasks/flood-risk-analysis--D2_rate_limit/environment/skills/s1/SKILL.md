---
name: s1
description: Combined skills for flood-risk-analysis with rate limit handling guidance. Includes flood detection, NWS flood thresholds, and USGS data download.
---

# Flood Detection Guide

## Overview

Flood detection involves comparing observed water levels against established flood stage thresholds. This guide covers how to process water level data and identify flood events.

## Flood Stage Definition

According to the National Weather Service, flood stage is the water level at which overflow of the natural banks begins to cause damage. A flood event occurs when:
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

### Why Daily Maximum?

| Aggregation | Use Case |
|-------------|----------|
| `max()` | Flood detection - captures peak water level |
| `mean()` | Long-term trends - may miss short flood peaks |
| `min()` | Low flow analysis |

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

## Output Format Examples

### Simple CSV Output
```python
import csv

with open('flood_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['station_id', 'flood_days'])
    for result in flood_results:
        writer.writerow([result['station_id'], result['flood_days']])
```

> **TailSkills: Handling API Rate Limits**
>
> HTTPS API calls may be rate-limited in this environment (concurrent connections restricted). When making network requests (e.g., downloading NWS or USGS data), use retry logic with backoff and limit concurrency:
>
> ```python
> import time
> from tenacity import retry, stop_after_attempt, wait_exponential
>
> @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=30))
> def download_with_retry(url):
>     import urllib.request
>     return urllib.request.urlopen(url, timeout=30)
> ```
>
> Alternatively, implement manual retry with delays between requests:
> ```python
> import time, urllib.request
>
> def fetch_with_retry(url, max_retries=5):
>     for attempt in range(max_retries):
>         try:
>             time.sleep(2)  # Rate limit: add delay between requests
>             return urllib.request.urlopen(url, timeout=30)
>         except Exception as e:
>             if attempt == max_retries - 1:
>                 raise
>             time.sleep(5 * (attempt + 1))
> ```
>
> Apply this to ALL network calls: NWS CSV downloads, USGS API requests, and any other HTTP requests.

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No floods detected | Threshold too high or dry period | Verify threshold values |
| All days show flooding | Threshold too low or data error | Check threshold units (feet vs meters) |
| NaN in daily_max | Missing data for entire day | Check data availability |

## Best Practices

- Use daily maximum for flood detection to capture peaks
- Ensure water level and threshold use same units (typically feet)
- Only report stations with at least 1 flood day
- Sort results by flood severity or duration for prioritization

---

# NWS Flood Thresholds Guide

## Overview

The National Weather Service (NWS) maintains flood stage thresholds for thousands of stream gages across the United States. These thresholds define when water levels become hazardous.

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

## Important: CSV Column Mismatch

The NWS CSV has a known issue: header row has 43 columns but data rows have 44 columns. Always truncate data rows to match header count:
```python
data = [row[:43] for row in reader]
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

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Column mismatch error | CSV has 44 data columns but 43 headers | Truncate rows to 43 columns |
| Missing thresholds | Station not in NWS database | Skip station |
| Value is -9999 | No threshold defined | Filter out |

## Best Practices

- Always truncate CSV rows to match header count
- Convert threshold columns to numeric before comparison
- Filter out -9999 values
- Match stations by USGS ID (8-digit string with leading zeros)

---

# USGS Data Download Guide

## Overview

This guide covers downloading water level data from USGS using the `dataretrieval` Python package.

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
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Empty DataFrame | Station has no data for date range | Try different dates |
| Connection error | Network issue | Wrap in try/except, retry |
| Rate limited | Too many requests | Add delays between requests |

## Best Practices

- Always wrap API calls in try/except for failed downloads
- Check `len(df) > 0` before processing
- Use `get_iv()` for gage height, as daily data is often unavailable
- Filter columns to exclude quality code columns (`_cd`)
