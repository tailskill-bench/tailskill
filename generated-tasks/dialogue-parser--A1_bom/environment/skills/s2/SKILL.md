---
name: s1
description: A library for building, validating, visualizing, and serializing dialogue graphs. Use this when parsing scripts or creating branching narrative structures.
---

# Dialogue Graph Skill

Provides `dialogue_graph` module for building valid dialogue trees/graphs.

## When to use

- **Script Parsers**: Converting text to data
- **Dialogue Editors**: Building tools to edit conversation flow
- **Game Logic**: Traversing a dialogue tree
- **Visualization**: Generating visual diagrams of dialogue flows

## How to use

```python
from dialogue_graph import Graph, Node, Edge
```

### 1. The `Graph` Class

```python
graph = Graph()
```

### 2. Adding Nodes

```python
# Regular line
graph.add_node(Node(id="Start", speaker="Guard", text="Halt!", type="line"))

# Choice hub
graph.add_node(Node(id="Choices", type="choice"))
```

### 3. Adding Edges

```python
# Simple transition
graph.add_edge(Edge(source="Start", target="Choices"))

# Choice transition (with text)
graph.add_edge(Edge(source="Choices", target="End", text="1. Run away"))
```

### 4. Export

```python
data = graph.to_dict()
# returns {"nodes": [...], "edges": [...]}
json_str = graph.to_json()
```

### 5. Validation

```python
errors = graph.validate()
# Returns list of strings, e.g., ["Edge 'Start'->'Unk' points to missing node 'Unk'"]
```

### 6. Reading script files

Use `encoding='utf-8-sig'` when opening files to handle UTF-8 BOM markers:

```python
with open(filepath, "r", encoding="utf-8-sig") as f:
    content = f.read()
```

Alternatively, clean files in-place before reading:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /app/script.txt
```

### 7. Visualization

```python
# Requires: pip install graphviz
# Also requires Graphviz binary: https://graphviz.org/download/

graph.visualize('dialogue_graph')  # Creates dialogue_graph.png
graph.visualize('output', format='svg')  # Creates output.svg
```

### 8. Loading from JSON

```python
# From file
graph = Graph.from_file('dialogue.json')

# From dict
graph = Graph.from_dict({'nodes': [...], 'edges': [...]})

# From JSON string
graph = Graph.from_json(json_string)