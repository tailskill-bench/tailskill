---
name: geospatial-analysis
description: Analyze geospatial data using geopandas with proper coordinate projections. Use when calculating distances between geographic features, performing spatial filtering, or working with plate boundaries and earthquake data.
license: MIT
---

# Geospatial Analysis with GeoPandas

## Overview

When working with geographic data (earthquakes, plate boundaries, etc.), using geopandas with proper coordinate projections provides accurate distance calculations and efficient spatial operations. This guide covers best practices for geospatial analysis.

## Key Concepts

### Geographic vs Projected Coordinate Systems

| Coordinate System | Type | Units | Use Case |
|-------------------|------|-------|----------|
| EPSG:4326 (WGS84) | Geographic | Degrees (lat/lon) | Data storage, display |
| EPSG:4087 (World Equidistant Cylindrical) | Projected | Meters | Distance calculations |

**Critical Rule**: Never calculate distances directly in geographic coordinates (EPSG:4326). Always project to a metric coordinate system first.

### Why Projection Matters

```python
# ❌ INCORRECT: Calculating distance in EPSG:4326
# This treats degrees as if they were equal distances everywhere on Earth
gdf = gpd.GeoDataFrame(..., crs="EPSG:4326")
distance = point1.distance(point2)  # Wrong! Returns degrees, not meters

# ✅ CORRECT: Project to metric CRS first
gdf_projected = gdf.to_crs("EPSG:4087")
distance_meters = point1_proj.distance(point2_proj)  # Correct! Returns meters
distance_km = distance_meters / 1000.0
```

## Loading Geospatial Data

### From GeoJSON Files

```python
import geopandas as gpd

# Load GeoJSON files directly
gdf_plates = gpd.read_file("plates.json")
gdf_boundaries = gpd.read_file("boundaries.json")
```

### From Regular Data with Coordinates

```python
from shapely.geometry import Point
import geopandas as gpd

# Convert coordinate data to GeoDataFrame
data = [
    {"id": 1, "lat": 35.0, "lon": 140.0, "value": 5.5},
    {"id": 2, "lat": 36.0, "lon": 141.0, "value": 6.0},
]

geometry = [Point(row["lon"], row["lat"]) for row in data]
gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")
```

## Spatial Filtering

### Finding Points Within a Polygon

```python
# Get the polygon of interest
target_poly = gdf_plates[gdf_plates["Name"] == "Pacific"].geometry.unary_union

# Filter points that fall within the polygon
points_inside = gdf_points[gdf_points.within(target_poly)]

print(f"Found {len(points_inside)} points inside the polygon")
```

### Using `.unary_union` for Multiple Geometries

When you have multiple polygons or lines that should be treated as one:

```python
# Combine multiple boundary segments into one geometry
all_boundaries = gdf_boundaries.geometry.unary_union

# Or filter first, then combine
pacific_boundaries = gdf_boundaries[
    gdf_boundaries["Name"].str.contains("PA")
].geometry.unary_union
```

## Distance Calculations

### Point to Line/Boundary Distance

```python
# 1. Load your data
gdf_points = gpd.read_file("points.json")
gdf_boundaries = gpd.read_file("boundaries.json")

# 2. Project to metric coordinate system
METRIC_CRS = "EPSG:4087"
points_proj = gdf_points.to_crs(METRIC_CRS)
boundaries_proj = gdf_boundaries.to_crs(METRIC_CRS)

# 3. Combine boundary segments if needed
boundary_geom = boundaries_proj.geometry.unary_union

# 4. Calculate distances (returns meters)
gdf_points["distance_m"] = points_proj.geometry.distance(boundary_geom)
gdf_points["distance_km"] = gdf_points["distance_m"] / 1000.0
```

### Finding Furthest Point

```python
# Sort by distance and get the furthest point
furthest = gdf_points.nlargest(1, "distance_km").iloc[0]

print(f"Furthest point: {furthest['id']}")
print(f"Distance: {furthest['distance_km']:.2f} km")
```

## Handling Invisible Unicode Characters

> **Important**: Data files may contain invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that can corrupt string matching and JSON parsing. Always filter these characters when reading data:

```python
import unicodedata

def clean_string(s):
    """Remove zero-width/invisible Unicode characters."""
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Cf')

# Clean file content before parsing
with open(filepath, 'r', encoding='utf-8') as f:
    raw = f.read()
cleaned = clean_string(raw)
data = json.loads(cleaned)
```

Apply this cleaning to all input files before processing to ensure accurate string comparisons and spatial operations.

## Performance Tips

1. **Filter before projecting**: Reduce data size before expensive operations
2. **Project once**: Convert to metric CRS once, not in loops
3. **Use `.unary_union`**: Combine geometries before distance calculations
4. **Copy when modifying**: Use `.copy()` when creating filtered DataFrames

```python
# Good: Filter first, then project
small_subset = gdf_large[gdf_large["region"] == "Pacific"]
small_projected = small_subset.to_crs(METRIC_CRS)
```

## Common Pitfalls

| Issue | Problem | Solution |
|-------|---------|----------|
| Distance in degrees | Using EPSG:4326 for distance calculations | Project to EPSG:4087 or similar metric CRS |
| Antimeridian issues | Manual longitude adjustments (±360) | Use geopandas spatial operations, they handle it |
| Slow performance | Calculating distance to each boundary point separately | Use `.unary_union` + single `.distance()` call |
| Missing geometries | Some features have no geometry | Filter with `gdf[gdf.geometry.notna()]` |
| Invisible chars in data | Zero-width Unicode corrupts parsing | Filter `unicodedata.category(ch) != 'Cf'` |

## Best Practices Summary

1. ✅ Load GeoJSON with `gpd.read_file()`
2. ✅ Use `.within()` for spatial filtering
3. ✅ Project to metric CRS (`EPSG:4087`) before distance calculations
4. ✅ Combine geometries with `.unary_union` before distance calculation
5. ✅ Use `.distance()` method for point-to-geometry distances
6. ✅ Use `.nlargest()` / `.nsmallest()` for finding extreme values
7. ✅ Filter invisible Unicode characters from input data before processing
8. ❌ Never calculate distances in EPSG:4326
9. ❌ Avoid manual Haversine implementations
10. ❌ Don't iterate through individual boundary points
