---
name: s1
description: "Civ6 district adjacency optimizer with hex grid spatial tools, map optimization, and SQLite map parsing."
---

# Civ6 District Mechanics Reference

Modules: **placement_rules.py**, **adjacency_rules.py**. For hex grid utilities, use the `hex-grid-spatial` skill or import from `src.hex_utils`.

## Usage

```python
from civ6lib import (
    DistrictType, Tile, PlacementRules, get_placement_rules,
    validate_district_count, validate_district_uniqueness,
    AdjacencyCalculator, get_adjacency_calculator,
)

rules = get_placement_rules(tiles, city_center=(21, 13), population=7)
result = rules.validate_placement(DistrictType.CAMPUS, 21, 14, {})
if result.valid:
    print("Valid placement!")

calculator = get_adjacency_calculator(tiles)
total, per_district = calculator.calculate_total_adjacency(placements)
```

# Placement Rules

## City Placement

| Condition | Min Distance | Tiles Between |
|-----------|--------------|---------------|
| Same landmass | 4 tiles | 3 tiles |
| Different landmasses | 3 tiles | 2 tiles |

Invalid settlement tiles: Water (Coast, Ocean, Lake), Mountains, Natural Wonders. Settling a **City Center** on Geothermal Fissure or Luxury/Strategic Resources **preserves** them; districts cannot be placed on these tiles.

## District Placement

**Universal:** Within 3 tiles of City Center. Cannot place on Mountains, Natural Wonders, Strategic/Luxury Resources, existing District. CAN place on Bonus Resources, Woods/Rainforest/Marsh (all destroyed).

| District | Special Requirement |
|----------|---------------------|
| Harbor / Water Park | Coast/Lake, adjacent to land |
| Aerodrome / Spaceport | Flat land |
| Encampment / Preserve | NOT adjacent to City Center |
| Aqueduct | Adjacent to City Center AND fresh water (Mountain, River, Lake, Oasis) |
| Dam | On Floodplains, river crosses 2+ edges |

`max_specialty_districts = 1 + floor((population - 1) / 3)`. Non-specialty (don't count): Aqueduct/Bath, Neighborhood/Mbanza, Canal, Dam, Spaceport. Uniqueness: ONE per city for most; multiple Neighborhoods allowed; ONE per civ for Government Plaza, Diplomatic Quarter.

# Adjacency Bonus Rules

**Critical: Each +0.5 type is floored SEPARATELY, then summed!**

```
WRONG: IZ with 1 Mine + 1 Lumber Mill + 1 District = floor(3/2) = 1  ❌
CORRECT: Mine: floor(1/2)=0, Lumber Mill: floor(1/2)=0, District: floor(1/2)=0 → TOTAL = 0  ✓
```

| District | +2 each | +1 each | +0.5 each (floor separately) |
|----------|---------|---------|------------------------------|
| Campus (+Science) | Geothermal Fissure, Reef | Mountain | Rainforest, District |
| Holy Site (+Faith) | Natural Wonder | Mountain | Woods, District |
| Theater Square (+Culture) | Wonder (built), Entertainment Complex, Water Park | — | District |
| Commercial Hub (+Gold) | Adjacent Harbor; +2 if ON river (binary) | — | District |
| Harbor (+Gold) | Adjacent City Center | Coastal Resource | District |
| Industrial Zone (+Production) | Aqueduct, Dam, Canal | Quarry, Strategic Resource | Mine, Lumber Mill, District |

No adjacency bonuses: Entertainment Complex, Water Park, Encampment, Aerodrome, Spaceport, Government Plaza, Preserve. **Government Plaza** gives +1 to adjacent specialty districts and counts toward +0.5 per district. Placing ANY district destroys Woods, Rainforest, Marsh, and Bonus Resources — affecting OTHER districts' adjacency.

# Key Classes

- **DistrictType** (Enum): CAMPUS, HOLY_SITE, THEATER_SQUARE, COMMERCIAL_HUB, HARBOR, INDUSTRIAL_ZONE, etc.
- **Tile** (Dataclass): Map tile with terrain, features, resources, rivers.
- **PlacementRules**: Validates district placements against all game rules.
- **AdjacencyCalculator**: Calculates adjacency bonuses based on surrounding tiles and districts.

# Hex Grid Spatial Utilities

Hexagonal grid using **odd-r offset coordinates** (odd rows shifted right). Tile 0 at bottom-left; X increases rightward, Y increases upward.

```
     2   1
      \ /
   3 - * - 0
      / \
     4   5
0=East, 1=NE, 2=NW, 3=West, 4=SW, 5=SE
```

```python
def get_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
    if y % 2 == 0:
        directions = [(1,0), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1)]
    else:
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (0,1), (1,1)]
    return [(x + dx, y + dy) for dx, dy in directions]

def hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    def offset_to_cube(col, row):
        cx = col - (row - (row & 1)) // 2
        cz = row
        cy = -cx - cz
        return cx, cy, cz
    cx1, cy1, cz1 = offset_to_cube(x1, y1)
    cx2, cy2, cz2 = offset_to_cube(x2, y2)
    return (abs(cx1-cx2) + abs(cy1-cy2) + abs(cz1-cz2)) // 2
```

Even vs Odd row difference is in diagonal directions (1,2,4,5); East (0) and West (3) are always (1,0) and (-1,0).

| Direction | Even Row (y%2==0) | Odd Row (y%2==1) |
|-----------|-------------------|------------------|
| NE (1) | (0, -1) | (1, -1) |
| NW (2) | (-1, -1) | (0, -1) |
| SW (4) | (-1, +1) | (0, +1) |
| SE (5) | (0, +1) | (1, +1) |

# Map-Based Constraint Optimization Strategy

## Three-Phase Strategy

**Phase 1: Prune** — Remove tiles that are Invalid, Dominated (strictly worse than another), or Isolated (too far from other valid tiles).

**Phase 2: Score** — Score remaining tiles by intrinsic value, adjacency potential, and cluster potential. Identify priority tiles.

**Phase 3: Anchor Search** — Select anchors enabling access to multiple high-value spots; greedily add placements maximizing marginal value; validate all placements; local search (swap/move) to improve.

```python
def optimize_placements(map_tiles, constraints, num_placements):
    candidates = [t for t in map_tiles if is_valid_tile(t, constraints)]
    scored = [(tile, score_tile(tile, candidates)) for tile in candidates]
    scored.sort(key=lambda x: -x[1])
    high_value = scored[:top_k]

    best_solution = None
    best_score = 0
    for anchor in get_anchor_candidates(high_value, constraints):
        solution = greedy_expand(anchor, candidates, num_placements, constraints)
        solution = local_search(solution, candidates, constraints)
        if solution.score > best_score:
            best_solution = solution
            best_score = solution.score
    return best_solution
```

Key insights: prune early and aggressively; high-value tiles cluster; anchors constrain the search; greedy + local search is often sufficient; propagate constraints immediately after each placement.

# SQLite to Structured JSON

## Step 1: Explore the Schema

```sql
SELECT name FROM sqlite_master WHERE type='table';
PRAGMA table_info(TableName);
SELECT sql FROM sqlite_master WHERE name='TableName';
PRAGMA foreign_key_list(TableName);
```

## Step 2: Extract and Transform

```python
import sqlite3, json

def parse_sqlite_to_json(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM MetadataTable LIMIT 1")
    metadata = dict(cursor.fetchone())

    data = {}
    cursor.execute("SELECT * FROM MainTable")
    for row in cursor.fetchall():
        key = row["ID"]
        data[key] = dict(row)

    cursor.execute("SELECT * FROM RelatedTable")
    for row in cursor.fetchall():
        key = row["ID"]
        if key in data:
            data[key]["extra_field"] = row["Value"]

    conn.close()
    return {"metadata": metadata, "items": list(data.values())}
```

For grid/map data, compute coordinates from linear ID: `x = id % width, y = id // width`. Before writing results to output files (e.g., "/output/scenario_3.json"), ensure the output directory has proper write permissions.