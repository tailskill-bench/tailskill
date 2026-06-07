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

| Code | Parameter | Unit | Description |
|------|-----------|------|-------------|
| `00065` | Gage height | feet | Water level above datum |
| `00060` | Discharge | cfs | Streamflow volume |

## nwis Module Functions

| Function | Description | Data Frequency |
|----------|-------------|----------------|
| `nwis.get_iv()` | Instantaneous values | ~15 minutes |
| `nwis.get_dv()` | Daily values | Daily |
| `nwis.get_info()` | Site information | N/A |
| `nwis.get_stats()` | Statistical summaries | N/A |
| `nwis.get_peaks()` | Annual peak discharge | Annual |

## Returned DataFrame Structure

| Column | Description |
|--------|-------------|
| `site_no` | Station ID |
| `00065` | Water level value |
| `00065_cd` | Quality code (can ignore) |

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
    print(water_levels.head())
```

## Best Practices

- Always wrap API calls in try/except for failed downloads
- Check `len(df) > 0` before processing
- Station IDs are 8-digit strings with leading zeros (e.g., '04119000')
- Use `get_iv()` for gage height, as daily data is often unavailable
- Filter columns to exclude quality code columns (`_cd`)
- Break up large requests into smaller time periods to avoid timeouts

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
| **Flood Stage (Minor)** | **`flood stage`** | **Minimal property damage. Use this to determine if flooding occurred.** |
| Moderate Flood Stage | `moderate flood stage` | Structure inundation, evacuations may be needed |
| Major Flood Stage | `major flood stage` | Extensive damage, significant evacuations required |

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
| `moderate flood stage` | Moderate flood threshold (feet) |
| `major flood stage` | Major flood threshold (feet) |

## Matching Thresholds to Station IDs

When reading station ID files, handle invisible Unicode characters that may be present. Zero-width characters (U+200B, U+200C, U+200D) can interfere with string matching:

```python
ZW_CHARS = {"\u200b", "\u200c", "\u200d", "\ufeff"}

with open('/root/data/michigan_stations.txt', 'r') as f:
    station_ids = [line.strip() for line in f if line.strip()]
station_ids = [s.translate({ord(c): None for c in ZW_CHARS}) for s in station_ids]
```

Alternatively, a helper script can clean files in-place:
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

## Best Practices

- Always truncate CSV rows to match header count
- Convert threshold columns to numeric before comparison
- Filter out -9999 values (indicates no threshold defined)
- Match stations by USGS ID (8-digit string with leading zeros)

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

## Best Practices

- Use daily maximum for flood detection to capture peaks
- Ensure water level and threshold use same units (typically feet)
- Only report stations with at least 1 flood day
- Sort results by flood severity or duration for prioritization