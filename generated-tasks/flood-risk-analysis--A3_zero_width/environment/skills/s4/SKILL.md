---
name: s1
description: Detect flood events by comparing USGS water levels to NWS thresholds.
license: MIT
---

# USGS Data Download

```bash
pip install dataretrieval
```

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

Parameter codes: `00065` = Gage height (feet), `00060` = Discharge (cfs).

## Multiple Stations

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
```

## Extract Value Column

```python
gage_col = [c for c in df.columns if '00065' in str(c) and '_cd' not in str(c)]
if gage_col:
    water_levels = df[gage_col[0]]
```

- Station IDs are 8-digit strings with leading zeros (e.g., `'04119000'`)
- Use `get_iv()` for gage height; daily data is often unavailable
- Filter columns to exclude quality code columns (`_cd`)

# NWS Flood Thresholds

## Data Sources

- **Bulk CSV (recommended):** `https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv`
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

Handle invisible Unicode characters (U+200B, U+200C, U+200D) that may be present in station ID files:

```python
ZW_CHARS = {"\u200b", "\u200c", "\u200d", "\ufeff"}

with open('/root/data/michigan_stations.txt', 'r') as f:
    station_ids = [line.strip() for line in f if line.strip()]
station_ids = [s.translate({ord(c): None for c in ZW_CHARS}) for s in station_ids]
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

- Convert threshold columns to numeric before comparison
- Filter out `-9999` values (indicates no threshold defined)

# Flood Detection

A flood event occurs when:
```python
water_level >= flood_stage_threshold
```

## Aggregating Instantaneous Data to Daily

Aggregate instantaneous data to daily max for flood detection:
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
```

- Use daily maximum for flood detection to capture peaks
- Ensure water level and threshold use same units (typically feet)
- Only report stations with at least 1 flood day