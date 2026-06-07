---
name: s1
description: Flood risk analysis combining flood detection, NWS threshold retrieval, and USGS data download with read-only output handling.
---

# Flood Detection

Flood event: `water_level >= flood_stage_threshold`.

```python
daily_max = df[gage_col].resample('D').max()
```

```python
flood_threshold = <threshold_from_nws>  # feet
flood_days = (daily_max >= flood_threshold).sum()
flood_dates = daily_max[daily_max >= flood_threshold].index.tolist()
```

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

```python
def classify_flood(water_level, thresholds):
    if water_level >= thresholds['major']:
        return 'major'
    elif water_level >= thresholds['moderate']:
        return 'moderate'
    elif water_level >= thresholds['flood']:
        return 'minor'
    elif water_level >= thresholds['action']:
        return 'action'
    else:
        return 'normal'
```

## Output

```python
import csv
with open('flood_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['station_id', 'flood_days'])
    for result in flood_results:
        writer.writerow([result['station_id'], result['flood_days']])
```

```python
import json
output = {'flood_events': flood_results, 'total_stations_with_flooding': len(flood_results)}
with open('flood_report.json', 'w') as f:
    json.dump(output, f, indent=2)
```

> **Read-Only Output Directories**: Fix permissions **before** any `to_csv()`, `open(..., 'w')`, or similar write operations:
>
> ```python
> import os
> def prepare_output(output_path):
>     output_dir = output_path if os.path.isdir(output_path) else os.path.dirname(output_path)
>     if output_dir:
>         output_dir = output_dir.rstrip('/')
>         if os.path.isdir(output_dir):
>             os.chmod(output_dir, 0o755)
> prepare_output('/root/output/flood_results.csv')
> ```

## Dependencies

```bash
pip3 install --break-system-packages dataretrieval==1.0.10
```

# NWS Flood Thresholds

**Sources**: Bulk CSV: `https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv` | Individual: `https://water.noaa.gov/gauges/<station_id>`

| Category | CSV Column | Description |
|----------|------------|-------------|
| Action Stage | `action stage` | Water level requiring monitoring |
| **Flood Stage (Minor)** | **`flood stage`** | **Minimal property damage. Use this to determine if flooding occurred.** |
| Moderate Flood Stage | `moderate flood stage` | Structure inundation, evacuations may be needed |
| Major Flood Stage | `major flood stage` | Extensive damage, significant evacuations required |

**Key Columns**: `usgs id` (8-digit string), `state` (two-letter code), `flood stage`, `moderate flood stage`, `major flood stage`

The NWS CSV has a known issue: header row has 43 columns but data rows have 44 columns. Always truncate data rows to match header count:

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

```python
nws_df['flood stage'] = pd.to_numeric(nws_df['flood stage'], errors='coerce')
```

```python
state_stations = nws_df[
    (nws_df['state'] == '<STATE_CODE>') &
    (nws_df['usgs id'].notna()) &
    (nws_df['usgs id'] != '') &
    (nws_df['flood stage'].notna()) &
    (nws_df['flood stage'] != -9999)
]
```

```python
station_ids = ['<id_1>', '<id_2>', '<id_3>']
thresholds = {}
for _, row in nws_df.iterrows():
    usgs_id = str(row['usgs id']).strip()
    if usgs_id in station_ids:
        thresholds[usgs_id] = {'name': row['location name'], 'flood': row['flood stage']}
```

- Always truncate CSV rows to match header count
- Convert threshold columns to numeric before comparison
- Filter out -9999 values (indicates no threshold defined)
- Match stations by USGS ID (8-digit string with leading zeros)

# USGS Data Download

```python
from dataretrieval import nwis

# Instantaneous values (15-min intervals)
df, meta = nwis.get_iv(sites='<station_id>', start='<start_date>', end='<end_date>', parameterCd='00065')

# Daily values
df, meta = nwis.get_dv(sites='<station_id>', start='<start_date>', end='<end_date>', parameterCd='00060')

# Site information
info, meta = nwis.get_info(sites='<station_id>')
```

**Parameter Codes**: `00065` = Gage height (feet), `00060` = Discharge (cfs)

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

```python
gage_col = [c for c in df.columns if '00065' in str(c) and '_cd' not in str(c)]
if gage_col:
    water_levels = df[gage_col[0]]
```

- Always wrap API calls in try/except for failed downloads
- Check `len(df) > 0` before processing
- Station IDs are 8-digit strings with leading zeros (e.g., '04119000')
- Use `get_iv()` for gage height, as daily data is often unavailable
- Filter columns to exclude quality code columns (`_cd`)