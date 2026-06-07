---
name: s1
description: "Civ6 district adjacency optimizer with hex grid spatial tools, map optimization strategy, and SQLite map parsing."
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

---

# Part 1: Placement Rules

## City Placement Rules

| Condition | Min Distance | Tiles Between |
|-----------|--------------|---------------|
| Same landmass | 4 tiles | 3 tiles |
| Different landmasses | 3 tiles | 2 tiles |

Invalid settlement tiles: Water (Coast, Ocean, Lake), Mountains, Natural Wonders.

Settling a **City Center** on Geothermal Fissure or Luxury/Strategic Resources **preserves** them. Districts cannot be placed on these tiles.

## District Placement Rules

### Universal Rules

| Rule | Description |
|------|-------------|
| Distance | Within **3 tiles** of City Center |
| Cannot place on | Mountains, Natural Wonders, Strategic Resources (Iron, Horses, Niter, Coal, Oil, Aluminum, Uranium), Luxury Resources, existing District |
| CAN place on | Bonus Resources (destroyed), Woods/Rainforest/Marsh (destroyed) |

### District-Specific Rules

| District | Special Requirement |
|----------|---------------------|
| Harbor / Water Park | Must be on Coast/Lake, adjacent to land |
| Aerodrome / Spaceport | Must be on flat land |
| Encampment / Preserve | NOT adjacent to City Center |
| Aqueduct | Adjacent to City Center AND fresh water (Mountain, River, Lake, Oasis) |
| Dam | On Floodplains, river crosses 2+ edges |

## District Limits

`max_specialty_districts = 1 + floor((population - 1) / 3)`

Non-specialty districts (don't count): Aqueduct/Bath, Neighborhood/Mbanza, Canal, Dam, Spaceport.

Uniqueness: ONE per city for most districts; multiple Neighborhoods allowed; ONE per civilization for Government Plaza, Diplomatic Quarter.

---

# Part 2: Adjacency Bonus Rules

## Critical Rule: Minor Bonus Calculation

**Each +0.5 type is floored SEPARATELY, then summed!**

```
WRONG: IZ with 1 Mine + 1 Lumber Mill + 1 District = floor(3/2) = 1  ❌
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
| +2 | If tile is ON a river (binary) |
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

No adjacency bonuses: Entertainment Complex, Water Park, Encampment, Aerodrome, Spaceport, Government Plaza, Preserve.

**Government Plaza** gives +1 adjacency to adjacent specialty districts and counts toward the +0.5 per district minor bonus.

Placing ANY district destroys Woods (FEATURE_FOREST), Rainforest (FEATURE_JUNGLE), Marsh (FEATURE_MARSH), and Bonus Resources — this affects OTHER districts' adjacency.

---

# Key Classes

- **DistrictType** (Enum): CAMPUS, HOLY_SITE, THEATER_SQUARE, COMMERCIAL_HUB, HARBOR, INDUSTRIAL_ZONE, etc.
- **Tile** (Dataclass): Map tile with terrain, features, resources, rivers.
- **PlacementRules**: Validates district placements against all game rules.
- **AdjacencyCalculator**: Calculates adjacency bonuses based on surrounding tiles and districts.

## Quick Validation Checklist

1. Is tile within 3 of city center?
2. Is tile NOT a mountain/natural wonder?
3. Is tile NOT a strategic/luxury resource?
4. Is tile unoccupied?
5. Does district meet special requirements?
6. Does city have district slots available?
7. Is this district unique and not already built?

---

# Hex Grid Spatial Utilities

Hexagonal grid using **odd-r offset coordinates** (odd rows shifted right). Tile 0 at bottom-left; X increases rightward, Y increases upward.

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

---

# Map-Based Constraint Optimization Strategy

## The Three-Phase Strategy

### Phase 1: Prune the Search Space

Remove tiles that are: (1) **Invalid** for any placement, (2) **Dominated** by another tile strictly better in all respects, (3) **Isolated** — too far from other valid tiles to form useful clusters.

### Phase 2: Identify High-Value Spots

Score each remaining tile by intrinsic value, adjacency potential, and cluster potential. Rank and identify **priority tiles**.

### Phase 3: Anchor Point Search

1. Select anchor candidates enabling access to multiple high-value spots
2. Greedily add placements maximizing marginal value
3. Validate all placements satisfy requirements
4. Local search: swap/move placements to improve

## Algorithm Skeleton

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

---

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

For grid/map data, compute coordinates from linear ID: `x = id % width, y = id // width`.

Before writing results to output files (e.g., "/output/scenario_3.json"), ensure the output directory has proper write permissions.