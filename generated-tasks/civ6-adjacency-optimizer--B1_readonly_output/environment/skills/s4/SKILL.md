---
name: s1
description: "Civ6 district adjacency optimizer with hex grid spatial tools, map optimization strategy, and SQLite map parsing."
---

# Civ6 District Mechanics Reference

Modules: **placement_rules.py**, **adjacency_rules.py**. Hex grid utilities: `src.hex_utils`.

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

# Placement & Adjacency Rules

## City & District Placement

**City:** Min distance 4 (same landmass) or 3 (different). Invalid on Water, Mountains, Natural Wonders. City Center preserves Geothermal/Luxury/Strategic; districts cannot use these.

**District:** Within 3 tiles of City Center. Cannot place on Mountains, Wonders, Strategic/Luxury Resources, existing District. CAN place on Bonus Resources, Woods/Rainforest/Marsh (destroyed).

| District | Special Requirement |
|----------|---------------------|
| Harbor / Water Park | Coast/Lake, adjacent to land |
| Aerodrome / Spaceport | Flat land |
| Encampment / Preserve | NOT adjacent to City Center |
| Aqueduct | Adjacent to City Center AND fresh water (Mountain, River, Lake, Oasis) |
| Dam | Floodplains, river crosses 2+ edges |

**Limits:** `max_specialty_districts = 1 + floor((population - 1) / 3)`. Non-specialty: Aqueduct/Bath, Neighborhood/Mbanza, Canal, Dam, Spaceport. ONE per city (except multiple Neighborhoods); ONE per civ for Government Plaza, Diplomatic Quarter.

## Adjacency Bonuses

**Critical:** Each +0.5 type is floored SEPARATELY, then summed!

```
WRONG: IZ with 1 Mine + 1 Lumber Mill + 1 District = floor(3/2) = 1  ❌
CORRECT: Mine: floor(1/2)=0, Lumber Mill: floor(1/2)=0, District: floor(1/2)=0 → TOTAL = 0  ✓
```

| District | +2 | +1 | +0.5 (floor separately) |
|----------|----|----|-------------------------|
| Campus | Geothermal, Reef | Mountain | Rainforest, District |
| Holy Site | Natural Wonder | Mountain | Woods, District |
| Theater Square | Wonder, Entertainment, Water Park | — | District |
| Commercial Hub | ON river (binary), adjacent Harbor | — | District |
| Harbor | Adjacent City Center | Coastal Resource | District |
| Industrial Zone | Aqueduct, Dam, Canal | Quarry, Strategic Resource | Mine, Lumber Mill, District |

No bonuses: Entertainment, Water Park, Encampment, Aerodrome, Spaceport, Government Plaza, Preserve. Government Plaza gives **+1** to adjacent specialty districts. Placing ANY district destroys Woods, Rainforest, Marsh, Bonus Resources — **affects OTHER districts' adjacency!**

# Hex Grid Spatial Utilities

Odd-r offset coordinates (odd rows shifted right). Tile 0 at bottom-left; X rightward, Y upward.

```
     2   1
      \ /
   3 - * - 0
      / \
     4   5
0=East, 1=NE, 2=NW, 3=West, 4=SW, 5=SE
```

## Core Functions

```python
def get_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
    """Get all 6 neighboring hex coordinates."""
    if y % 2 == 0:  # even row
        directions = [(1,0), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1)]
    else:  # odd row - shifted right
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (0,1), (1,1)]
    return [(x + dx, y + dy) for dx, dy in directions]
```

```python
def hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate hex distance using cube coordinate conversion."""
    def offset_to_cube(col, row):
        cx = col - (row - (row & 1)) // 2
        cz = row
        cy = -cx - cz
        return cx, cy, cz

    cx1, cy1, cz1 = offset_to_cube(x1, y1)
    cx2, cy2, cz2 = offset_to_cube(x2, y2)
    return (abs(cx1-cx2) + abs(cy1-cy2) + abs(cz1-cz2)) // 2
```

```python
def get_tiles_in_range(x: int, y: int, radius: int) -> List[Tuple[int, int]]:
    """Get all tiles within radius (excluding center)."""
    tiles = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            nx, ny = x + dx, y + dy
            if (nx, ny) != (x, y) and hex_distance(x, y, nx, ny) <= radius:
                tiles.append((nx, ny))
    return tiles
```

| Direction | Even Row (y%2==0) | Odd Row (y%2==1) |
|-----------|-------------------|------------------|
| NE (1) | (0, -1) | (1, -1) |
| NW (2) | (-1, -1) | (0, -1) |
| SW (4) | (-1, +1) | (0, +1) |
| SE (5) | (0, +1) | (1, +1) |

East/West always (1,0)/(-1,0).

# Map-Based Constraint Optimization Strategy

Brute-force is O(M^N). 50 tiles × 5 items = 312M combinations. Three-phase strategy:

**Phase 1: Prune** — Remove invalid, dominated, isolated tiles. Reduces space 70-90%.
**Phase 2: Score** — Rank by intrinsic value, adjacency potential, cluster potential.
**Phase 3: Anchor Search** — Select anchors enabling multiple high-value spots; greedily expand; validate constraints; local search (swap/move).

```python
def optimize_placements(map_tiles, constraints, num_placements):
    # Phase 1: Prune
    candidates = [t for t in map_tiles if is_valid_tile(t, constraints)]

    # Phase 2: Score and rank
    scored = [(tile, score_tile(tile, candidates)) for tile in candidates]
    scored.sort(key=lambda x: -x[1])
    high_value = scored[:top_k]

    # Phase 3: Anchor search
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

Key: Prune aggressively; high-value tiles cluster; anchors constrain search; greedy + local search often sufficient; propagate constraints after each placement.

# SQLite to Structured JSON

## Step 1: Explore Schema

```sql
SELECT name FROM sqlite_master WHERE type='table';
PRAGMA table_info(TableName);
SELECT sql FROM sqlite_master WHERE name='TableName';
PRAGMA foreign_key_list(TableName);
```

## Step 2: Extract and Transform

```python
import sqlite3
import json

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

Common patterns: ID-based joins (`LEFT JOIN` on ID); coordinate keys from linear ID (`x = id % width, y = id // width`). Output as dict (keyed by position) or array (with x,y fields). Ensure output directory has write permissions before writing to paths like `/output/scenario_3.json`.