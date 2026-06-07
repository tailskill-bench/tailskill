#!/bin/bash
set -e

# Reinstall missing geopandas dependencies
pip install --no-cache-dir geopandas==1.0.1 shapely==2.0.6 pyproj==3.7.0

python3 << 'EOF'
import json
from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point

EARTHQUAKES_FILE = "/root/earthquakes_2024.json"
PLATES_POLY_FILE = "/root/PB2002_plates.json"
BOUNDARIES_FILE = "/root/PB2002_boundaries.json"
output_file = "/root/answer.json"
METRIC_CRS = "EPSG:4087"

def load_earthquakes_from_file():
    with open(EARTHQUAKES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    earthquakes = []
    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        earthquakes.append({
            "id": feature["id"],
            "place": props["place"],
            "time": props["time"],
            "mag": props["mag"],
            "longitude": coords[0],
            "latitude": coords[1],
            "depth": coords[2],
        })
    return earthquakes

def main():
    earthquakes = load_earthquakes_from_file()
    gdf_plates = gpd.read_file(PLATES_POLY_FILE)
    gdf_boundaries = gpd.read_file(BOUNDARIES_FILE)

    geometry = [Point(eq["longitude"], eq["latitude"]) for eq in earthquakes]
    gdf_eq = gpd.GeoDataFrame(earthquakes, geometry=geometry, crs="EPSG:4326")

    pacific_poly = gdf_plates[gdf_plates["PlateName"] == "Pacific"].geometry.unary_union
    is_in_pacific = gdf_eq.within(pacific_poly)
    pacific_quakes = gdf_eq[is_in_pacific].copy()

    pacific_quakes_proj = pacific_quakes.to_crs(METRIC_CRS)
    pacific_bounds = (
        gdf_boundaries[gdf_boundaries["Name"].str.contains("PA")]
        .to_crs(METRIC_CRS)
        .geometry.unary_union
    )
    pacific_quakes["distance_km"] = (
        pacific_quakes_proj.geometry.distance(pacific_bounds) / 1000.0
    )

    furthest_quake = pacific_quakes.nlargest(1, "distance_km").iloc[0]
    time_iso = datetime.utcfromtimestamp(furthest_quake['time'] / 1000.0).strftime('%Y-%m-%dT%H:%M:%SZ')

    result = {
        "id": furthest_quake['id'],
        "place": furthest_quake['place'],
        "time": time_iso,
        "magnitude": furthest_quake['mag'],
        "latitude": furthest_quake['latitude'],
        "longitude": furthest_quake['longitude'],
        "distance_km": round(furthest_quake['distance_km'], 2)
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Result saved to {output_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
EOF
