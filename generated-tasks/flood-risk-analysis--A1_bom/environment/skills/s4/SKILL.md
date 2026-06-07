---
name: s1
description: Flood risk analysis skills — detect flood events by comparing water levels to NWS thresholds using USGS data. Covers data download, threshold lookup, and flood detection.
license: MIT
---

# USGS Data Download Guide

## Installation
```bash
pip install dataretrieval
```

## nwis Module

```python
from dataretrieval import nwis

# Instantaneous values (15-min intervals)
df, meta = nwis.get_iv(
    sites='<station_id>',
    start='<start_date>',
    end='<end_date>',
    parameterCd='00065'
)

# Daily values
df, meta = nwis.get_dv(
    sites='<station_id>',
    start='<start_date>',
    end='<end_date>',
    parameterCd='00060'
)

# Site information
info, meta = nwis.get_info(sites='<station_id>')
```

## Parameter Codes

| Code | Parameter | Unit |
|------|-----------|------|
| `00065` | Gage height | feet |
| `00060` | Discharge | cfs |

## Extracting the Value Column
```python
gage_col = [c for c in df.columns if '00065' in str(c) and '_cd' not in str(c)]
if gage_col:
    water_levels = df[gage_col[0]]
```

---

# NWS Flood Thresholds Guide

## Data Sources

- **Bulk CSV (recommended for multiple stations):** `https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv`
- **Individual station:** `https://water.noaa.gov/gauges/<station_id>`

## Flood Stage Categories

| Category | CSV Column | Description |
|----------|------------|-------------|
| Action Stage | `action stage` | Water level requiring monitoring |
| **Flood Stage (Minor)** | **`flood stage`** | **Minimal property damage. Use this to determine if flooding occurred.** |
| Moderate Flood Stage | `moderate flood stage` | Structure inundation, evacuations may be needed |
| Major Flood Stage | `major flood stage` | Extensive damage, significant evacuations required |

## Downloading Bulk CSV

**Known issue:** header row has 43 columns but data rows have 44. Always truncate data rows to match header count.

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
| `moderate flood stage` | Moderate flood threshold (feet) |
| `major flood stage` | Major flood threshold (feet) |

## Matching Thresholds to Station IDs

Handle UTF-8 BOM in station ID files:

```python
with open('/root/data/michigan_stations.txt', 'r', encoding='utf-8-sig') as f:
    station_ids = [line.strip() for line in f if line.strip()]
```

Alternatively, clean files in-place:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/michigan_stations.txt
```

```python
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

# Flood Detection Guide

## Flood Stage Definition

A flood event occurs when:
```python
water_level >= flood_stage_threshold
```

## Aggregating Instantaneous Data to Daily

USGS instantaneous data is recorded at ~15-minute intervals. For flood detection, aggregate to daily maximum:
```python
daily_max = df[gage_col].resample('D').max()
```

## Detecting Flood Days

Compare daily maximum water level against flood threshold:
```python
flood_threshold = <threshold_from_nws>

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
        flood_results.append({
            'station_id': site_id,
            'flood_days': days_above
        })

flood_results.sort(key=lambda x: x['flood_days'], reverse=True)
```

## Output Format

```python
import csv

with open('flood_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['station_id', 'flood_days'])
    for result in flood_results:
        writer.writerow([result['station_id'], result['flood_days']])