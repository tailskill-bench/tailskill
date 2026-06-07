---
name: s1
description: "Civ6 district adjacency optimizer with hex grid spatial tools, map optimization strategy, and SQLite map parsing."
---

# Civ6 District Mechanics Reference

Modules: **placement_rules.py** (placement validation), **adjacency_rules.py** (adjacency calculation). For hex grid utilities, use the `hex-grid-spatial` skill or import from `src.hex_utils`.

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

---

# Part 1: Placement Rules

## City Placement Rules

| Condition | Min Distance | Tiles Between |
|-----------|--------------|---------------|
| Same landmass | 4 tiles | 3 tiles |
| Different landmasses | 3 tiles | 2 tiles |

Invalid settlement tiles: Water (Coast, Ocean, Lake), Mountains, Natural Wonders.

Settling a **City Center** on Geothermal Fissure or Luxury/Strategic Resources **preserves** them (they remain and provide adjacency bonuses). Districts cannot be placed on these tiles.

## District Placement Rules

### Universal Rules (All Districts)

| Rule | Description |
|------|-------------|
| Distance | Within **3 tiles** of City Center |
| Cannot place on | Mountains, Natural Wonders, Strategic Resources (Iron, Horses, Niter, Coal, Oil, Aluminum, Uranium), Luxury Resources, existing District |
| CAN place on | Bonus Resources (destroyed), Woods/Rainforest/Marsh (feature destroyed) |

### District-Specific Rules

| District | Special Requirement |
|----------|---------------------|
| Harbor / Water Park | Must be on Coast/Lake, adjacent to land |
| Aerodrome / Spaceport | Must be on flat land |
| Encampment / Preserve | NOT adjacent to City Center |
| Aqueduct | Adjacent to City Center AND fresh water (Mountain, River, Lake, Oasis) |
| Dam | On Floodplains, river crosses 2+ edges |

## District Limits

```
max_specialty_districts = 1 + floor((population - 1) / 3)
```

| Population | Max Districts |
|------------|---------------|
| 1-3 | 1 |
| 4-6 | 2 |
| 7-9 | 3 |
| 10-12 | 4 |

Non-specialty districts (don't count): Aqueduct/Bath, Neighborhood/Mbanza, Canal, Dam, Spaceport.

Uniqueness: ONE per city for most districts; Neighborhood allows multiple; Government Plaza and Diplomatic Quarter are ONE per civilization.

---

# Part 2: Adjacency Bonus Rules

## Critical Rule: Minor Bonus Calculation

**Each +0.5 type is floored SEPARATELY, then summed!**

```
WRONG:   IZ with 1 Mine + 1 Lumber Mill + 1 District = floor(3/2) = 1  ❌
CORRECT: Mine: floor(1/2)=0, Lumber Mill: floor(1/2)=0, District: floor(1/2)=0 → TOTAL = 0  ✓
```

## Adjacency Rules by District

### Campus (+Science)
| Bonus | Source |
|-------|--------|
| +2 each | Geothermal Fissure, Reef |
| +1 each | Mountain |
| +0.5 each | Rainforest, District (floor separately) |

### Holy Site (+Faith)
| Bonus | Source |
|-------|--------|
| +2 each | Natural Wonder |
| +1 each | Mountain |
| +0.5 each | Woods, District (floor separately) |

### Theater Square (+Culture)
| Bonus | Source |
|-------|--------|
| +2 each | Wonder (built), Entertainment Complex, Water Park |
| +0.5 each | District (floor separately) |

### Commercial Hub (+Gold)
| Bonus | Source |
|-------|--------|
| +2 | If tile is ON a river (binary!) |
| +2 each | Adjacent Harbor |
| +0.5 each | District (floor separately) |

### Harbor (+Gold)
| Bonus | Source |
|-------|--------|
| +2 each | Adjacent City Center |
| +1 each | Coastal Resource (Fish, Crabs, Whales, Pearls) |
| +0.5 each | District (floor separately) |

### Industrial Zone (+Production)
| Bonus | Source |
|-------|--------|
| +2 each | Aqueduct, Dam, Canal |
| +1 each | Quarry, Strategic Resource |
| +0.5 each | Mine, Lumber Mill, District (floor separately) |

### No adjacency bonuses
Entertainment Complex, Water Park, Encampment, Aerodrome, Spaceport, Government Plaza, Preserve.

## Government Plaza Adjacency Bonus

Government Plaza gives **+1** to adjacent specialty districts (Campus, Holy Site, Theater Square, Commercial Hub, Harbor, Industrial Zone). It also counts toward the +0.5 per district minor bonus.

## Districts That Count for "+0.5 per District"

All districts plus City Center, Aqueduct, Dam, Canal, Neighborhood.

## Destruction Effects

Placing ANY district destroys: Woods (`FEATURE_FOREST`), Rainforest (`FEATURE_JUNGLE`), Marsh (`FEATURE_MARSH`), Bonus Resources. **This affects OTHER districts' adjacency!**

---

# Key Classes

- **DistrictType** (Enum): CAMPUS, HOLY_SITE, THEATER_SQUARE, COMMERCIAL_HUB, HARBOR, INDUSTRIAL_ZONE, etc.
- **Tile** (Dataclass): Map tile with terrain, features, resources, rivers.
- **PlacementRules**: Validates district placements against all game rules.
- **AdjacencyCalculator**: Calculates adjacency bonuses based on surrounding tiles and districts.

---

# Quick Validation Checklist

1. Is tile within 3 of city center?
2. Is tile NOT a mountain/natural wonder?
3. Is tile NOT a strategic/luxury resource?
4. Is tile unoccupied?
5. Does district meet special requirements?
6. Does city have district slots available?
7. Is this district unique and not already built?

---

# Hex Grid Spatial Utilities

Hexagonal grid coordinate system using **odd-r offset coordinates** (odd rows shifted right).

## Coordinate System

- Tile 0 at bottom-left; X increases rightward (columns), Y increases upward (rows)
- Odd rows (y % 2 == 1) shifted right by half a hex

## Direction Indices

```
     2   1
      \ /
   3 - * - 0
      / \
     4   5

0=East, 1=NE, 2=NW, 3=West, 4=SW, 5=SE
```

## Core Functions

### Get Neighbors

```python
def get_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
    """Get all 6 neighboring hex coordinates."""
    if y % 2 == 0:  # even row
        directions = [(1,0), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1)]
    else:  # odd row - shifted right
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (0,1), (1,1)]
    return [(x + dx, y + dy) for dx, dy in directions]
```

### Hex Distance

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

### Tiles in Range

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

## Even vs Odd Row Differences

| Direction | Even Row (y%2==0) | Odd Row (y%2==1) |
|-----------|-------------------|------------------|
| NE (1) | (0, -1) | (1, -1) |
| NW (2) | (-1, -1) | (0, -1) |
| SW (4) | (-1, +1) | (0, +1) |
| SE (5) | (0, +1) | (1, +1) |

East (0) and West (3) are always (1, 0) and (-1, 0).

---

# Map-Based Constraint Optimization Strategy

Systematic approach for placing items on a grid to maximize an objective while respecting constraints.

## Why Exhaustive Search Fails

Brute-force enumeration is O(M^N) combinations. Even 50 tiles with 5 items = 312 million combinations. Most are suboptimal or invalid.

## The Three-Phase Strategy

### Phase 1: Prune the Search Space

Remove tiles that are:
1. **Invalid** - Violate hard constraints (wrong terrain, out of range, blocked)
2. **Dominated** - Another tile is strictly better in all respects
3. **Isolated** - Too far from other valid tiles to form useful clusters

This alone can reduce search space by 70-90%.

### Phase 2: Identify High-Value Spots

Score each remaining tile by:
1. **Intrinsic value** - What does this tile contribute on its own?
2. **Adjacency potential** - What bonuses from neighboring tiles?
3. **Cluster potential** - Can this tile anchor a high-value group?

Rank tiles and identify top candidates (**priority tiles**).

### Phase 3: Anchor Point Search

1. **Select anchor candidates** - Tiles enabling access to multiple high-value spots
2. **Expand from anchors** - Greedily add placements maximizing marginal value
3. **Validate constraints** - Ensure all placements satisfy requirements
4. **Local search** - Try swapping/moving placements to improve solution

For problems with a "center" constraint: the anchor IS the center; reachable high-value tiles are fixed for each center position.

## Algorithm Skeleton

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

## Key Insights

- **Prune early, prune aggressively** - Every tile removed saves exponential work
- **High-value tiles cluster** - Adjacency bonuses compound
- **Anchors constrain the search** - Fixing an anchor makes other decisions follow logically
- **Greedy + local search is often sufficient** - Good local optimum found quickly beats perfect solution found slowly
- **Constraint propagation** - When you place one item, update what's valid for remaining items immediately

---

# SQLite to Structured JSON

Parse SQLite databases by exploring schemas first, then extracting data into structured JSON.

## Step 1: Explore the Schema

```sql
-- List all tables
SELECT name FROM sqlite_master WHERE type='table';

-- Inspect table schema (column names, types, pk)
PRAGMA table_info(TableName);

-- See CREATE statement
SELECT sql FROM sqlite_master WHERE name='TableName';

-- Find indexes (includes unique constraints)
PRAGMA index_list(TableName);
PRAGMA index_info(index_name);
```

## Step 2: Understand Relationships

```sql
-- Identify foreign keys
PRAGMA foreign_key_list(TableName);

-- ID-based joins
SELECT m.*, r.ExtraData
FROM MainTable m
LEFT JOIN RelatedTable r ON m.ID = r.ID;
```

For spatial data with linear ID: `x = id % width, y = id // width`.

## Step 3: Extract and Transform

```python
import sqlite3
import json

def parse_sqlite_to_json(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Explore schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    # 2. Get dimensions/metadata from config table
    cursor.execute("SELECT * FROM MetadataTable LIMIT 1")
    metadata = dict(cursor.fetchone())

    # 3. Build indexed data structure
    data = {}
    cursor.execute("SELECT * FROM MainTable")
    for row in cursor.fetchall():
        key = row["ID"]
        data[key] = dict(row)

    # 4. Join related data
    cursor.execute("SELECT * FROM RelatedTable")
    for row in cursor.fetchall():
        key = row["ID"]
        if key in data:
            data[key]["extra_field"] = row["Value"]

    conn.close()
    return {"metadata": metadata, "items": list(data.values())}

def safe_query(cursor, query):
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.OperationalError:
        return []
```

## Step 4: Output as Structured JSON

**Map/Dictionary Output** (items have natural unique keys):
```json
{
  "metadata": {"width": 44, "height": 26},
  "tiles": {
    "0,0": {"terrain": "GRASS", "feature": null},
    "1,0": {"terrain": "PLAINS", "feature": "FOREST"}
  }
}
```

**Array Output** (order matters or keys are simple integers):
```json
{
  "metadata": {"width": 44, "height": 26},
  "tiles": [
    {"x": 0, "y": 0, "terrain": "GRASS"},
    {"x": 1, "y": 0, "terrain": "PLAINS", "feature": "FOREST"}
  ]
}
```

## Debugging Queries

```sql
SELECT * FROM TableName LIMIT 5;
SELECT COUNT(*) FROM TableName;
SELECT DISTINCT ColumnName FROM TableName;
SELECT COUNT(*) FROM TableName WHERE ColumnName IS NULL;
```

Before writing results to output files (e.g., "/output/scenario_3.json"), ensure the output directory has proper write permissions. In containerized environments, run `chmod` to fix directory permissions before writing.