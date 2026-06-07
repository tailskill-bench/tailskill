---
name: geospatial-analysis
description: Analyze geospatial data using geopandas with proper coordinate projections for distances, spatial filtering, and plate/earthquake data.
license: MIT
---

## Coordinate Systems & Critical Constraint

| CRS | Type | Units | Use Case |
|-----|------|-------|----------|
| EPSG:4326 (WGS84) | Geographic | Degrees | Data storage, display |
| EPSG:4087 (World Equidistant Cylindrical) | Projected | Meters | Distance calculations |

**Never calculate distances in EPSG:4326. Always project to a metric CRS first.**

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

```python
import geopandas as gpd
from shapely.geometry import Point

# From GeoJSON
gdf_plates = gpd.read_file("plates.json")
gdf_boundaries = gpd.read_file("boundaries.json")

# From coordinate data
data = [
    {"id": 1, "lat": 35.0, "lon": 140.0, "value": 5.5},
    {"id": 2, "lat": 36.0, "lon": 141.0, "value": 6.0},
]
geometry = [Point(row["lon"], row["lat"]) for row in data]
gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")
```

## Spatial Filtering & Distance Calculations

```python
METRIC_CRS = "EPSG:4087"

# Points within a polygon
target_poly = gdf_plates[gdf_plates["Name"] == "Pacific"].geometry.unary_union
points_inside = gdf_points[gdf_points.within(target_poly)]

# Point-to-boundary distance
points_proj = gdf_points.to_crs(METRIC_CRS)
boundaries_proj = gdf_boundaries.to_crs(METRIC_CRS)
boundary_geom = boundaries_proj.geometry.unary_union

gdf_points["distance_m"] = points_proj.geometry.distance(boundary_geom)
gdf_points["distance_km"] = gdf_points["distance_m"] / 1000.0

# Finding extremes
furthest = gdf_points.nlargest(1, "distance_km").iloc[0]
print(f"Furthest point: {furthest['id']}, Distance: {furthest['distance_km']:.2f} km")
```

## Invisible Unicode Characters

Filter zero-width characters (U+200B, U+200C, U+200D) before processing:

```python
import unicodedata
import json

def clean_string(s):
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Cf')

with open(filepath, 'r', encoding='utf-8') as f:
    raw = f.read()
data = json.loads(clean_string(raw))
```

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