---
name: s1
description: Flood risk analysis combining NWS thresholds, USGS data download, and flood detection with rate limit handling.
---

# Flood Detection

Flood event: `water_level >= flood_stage_threshold`

Aggregate instantaneous (~15-min) data to daily max for flood detection (use `mean()` only for long-term trends):
```python
daily_max = df[gage_col].resample('D').max()
```

Detect flood days:
```python
flood_threshold = <threshold_from_nws>  # feet

flood_days = (daily_max >= flood_threshold).sum()
flood_dates = daily_max[daily_max >= flood_threshold].index.tolist()
```

Process multiple stations:
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

flood_results.sort(key=lambda x: x['flood_days'], reverse=True)
```

CSV output:
```python
import csv

with open('flood_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['station_id', 'flood_days'])
    for result in flood_results:
        writer.writerow([result['station_id'], result['flood_days']])
```

> **Rate Limits:** Apply retry logic to ALL network calls (NWS, USGS, HTTP):
> ```python
> import time
> from tenacity import retry, stop_after_attempt, wait_exponential
>
> @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=30))
> def download_with_retry(url):
>     import urllib.request
>     return urllib.request.urlopen(url, timeout=30)
> ```

# NWS Flood Thresholds

**Bulk CSV:** `https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv`
**Individual:** `https://water.noaa.gov/gauges/<station_id>`

**Flood categories:** `action stage` (monitoring), **`flood stage`** (minor—use for flood detection), `moderate flood stage`, `major flood stage`.

**Critical:** NWS CSV header has 43 columns, data rows have 44. Truncate: `data = [row[:43] for row in reader]`

Download:
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

Key columns: `usgs id` (8-digit string), `location name`, `state`, `action stage`, `flood stage`.

Convert numeric: `nws_df['flood stage'] = pd.to_numeric(nws_df['flood stage'], errors='coerce')`

Filter by state:
```python
state_stations = nws_df[
    (nws_df['state'] == '<STATE_CODE>') &
    (nws_df['usgs id'].notna()) &
    (nws_df['usgs id'] != '') &
    (nws_df['flood stage'].notna()) &
    (nws_df['flood stage'] != -9999)
]
```

Match thresholds:
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

# USGS Data Download

Install: `pip install dataretrieval`

Parameter codes: `00065` (gage height, feet), `00060` (discharge, cfs).

Single station:
```python
from dataretrieval import nwis

df, meta = nwis.get_iv(
    sites='<station_id>',
    start='<start_date>',
    end='<end_date>',
    parameterCd='00065'
)
```

Multiple stations:
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

Extract value column:
```python
gage_col = [c for c in df.columns if '00065' in str(c) and '_cd' not in str(c)]
if gage_col:
    water_levels = df[gage_col[0]]