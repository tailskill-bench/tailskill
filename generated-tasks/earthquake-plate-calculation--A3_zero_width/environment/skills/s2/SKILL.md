---
name: geospatial-analysis
description: Analyze geospatial data using geopandas with proper coordinate projections. Use when calculating distances between geographic features, performing spatial filtering, or working with plate boundaries and earthquake data.
license: MIT
---

# Geospatial Analysis with GeoPandas

## Coordinate Systems

| CRS | Type | Units | Use Case |
|-----|------|-------|----------|
| EPSG:4326 (WGS84) | Geographic | Degrees | Data storage, display |
| EPSG:4087 (World Equidistant Cylindrical) | Projected | Meters | Distance calculations |

**Critical**: Never calculate distances in EPSG:4326. Always project to a metric CRS first.

```python
# ❌ WRONG: distance in degrees
gdf = gpd.GeoDataFrame(..., crs="EPSG:4326")
distance = point1.distance(point2)  # degrees, not meters

# ✅ CORRECT: project first
gdf_proj = gdf.to_crs("EPSG:4087")
distance_m = point1_proj.distance(point2_proj)
distance_km = distance_m / 1000.0
```

## Loading Data

### From GeoJSON

```python
import geopandas as gpd

gdf_plates = gpd.read_file("plates.json")
gdf_boundaries = gpd.read_file("boundaries.json")
```

### From Coordinate Data

```python
from shapely.geometry import Point

data = [
    {"id": 1, "lat": 35.0, "lon": 140.0, "value": 5.5},
    {"id": 2, "lat": 36.0, "lon": 141.0, "value": 6.0},
]

geometry = [Point(row["lon"], row["lat"]) for row in data]
gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")
```

## Spatial Filtering

### Points Within a Polygon

```python
target_poly = gdf_plates[gdf_plates["Name"] == "Pacific"].geometry.unary_union
points_inside = gdf_points[gdf_points.within(target_poly)]
```

### Combining Multiple Geometries

```python
# All boundaries as one geometry
all_boundaries = gdf_boundaries.geometry.unary_union

# Filter then combine
pacific_boundaries = gdf_boundaries[
    gdf_boundaries["Name"].str.contains("PA")
].geometry.unary_union
```

## Distance Calculations

### Point-to-Boundary Distance

```python
METRIC_CRS = "EPSG:4087"

gdf_points = gpd.read_file("points.json")
gdf_boundaries = gpd.read_file("boundaries.json")

points_proj = gdf_points.to_crs(METRIC_CRS)
boundaries_proj = gdf_boundaries.to_crs(METRIC_CRS)

boundary_geom = boundaries_proj.geometry.unary_union

gdf_points["distance_m"] = points_proj.geometry.distance(boundary_geom)
gdf_points["distance_km"] = gdf_points["distance_m"] / 1000.0
```

### Finding Extremes

```python
furthest = gdf_points.nlargest(1, "distance_km").iloc[0]
print(f"Furthest point: {furthest['id']}, Distance: {furthest['distance_km']:.2f} km")
```

## Invisible Unicode Characters

Data files may contain zero-width characters (U+200B, U+200C, U+200D) that corrupt string matching and JSON parsing. Filter them before processing:

```python
import unicodedata
import json

def clean_string(s):
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Cf')

with open(filepath, 'r', encoding='utf-8') as f:
    raw = f.read()
data = json.loads(clean_string(raw))
```

## Performance Tips

- **Filter before projecting**: reduce data size before expensive operations
- **Project once**: convert to metric CRS once, not in loops
- **Use `.unary_union`**: combine geometries before distance calculations
- **Copy when modifying**: use `.copy()` for filtered DataFrames

```python
small_subset = gdf_large[gdf_large["region"] == "Pacific"]
small_projected = small_subset.to_crs(METRIC_CRS)
```

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Distance in degrees | Project to EPSG:4087 or similar metric CRS |
| Antimeridian issues | Use geopandas spatial operations (handles automatically) |
| Slow performance | Use `.unary_union` + single `.distance()` call |
| Missing geometries | Filter with `gdf[gdf.geometry.notna()]` |
| Invisible chars | Filter `unicodedata.category(ch) != 'Cf'` |

## Checklist

1. ✅ Load GeoJSON with `gpd.read_file()`
2. ✅ Use `.within()` for spatial filtering
3. ✅ Project to metric CRS (`EPSG:4087`) before distance calculations
4. ✅ Combine geometries with `.unary_union` before distance calculation
5. ✅ Use `.distance()` for point-to-geometry distances
6. ✅ Use `.nlargest()` / `.nsmallest()` for extreme values
7. ✅ Filter invisible Unicode characters from input data
8. ❌ Never calculate distances in EPSG:4326
9. ❌ Avoid manual Haversine implementations
10. ❌ Don't iterate through individual boundary points