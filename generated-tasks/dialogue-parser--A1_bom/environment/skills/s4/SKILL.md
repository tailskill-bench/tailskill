---
name: s1
description: Library for building, validating, visualizing, and serializing dialogue graphs. Use when parsing scripts or creating branching narratives.
---

# Dialogue Graph Skill

Module: `dialogue_graph`

```python
from dialogue_graph import Graph, Node, Edge
```

## Build & Export

```python
graph = Graph()
graph.add_node(Node(id="Start", speaker="Guard", text="Halt!", type="line"))
graph.add_node(Node(id="Choices", type="choice"))
graph.add_edge(Edge(source="Start", target="Choices"))
graph.add_edge(Edge(source="Choices", target="End", text="1. Run away"))
data = graph.to_dict()   # {"nodes": [...], "edges": [...]}
json_str = graph.to_json()
```

## Validation

```python
errors = graph.validate()
# Returns list of strings, e.g., ["Edge 'Start'->'Unk' points to missing node 'Unk'"]
```

## Reading Script Files

Use `encoding='utf-8-sig'` to handle UTF-8 BOM markers:

```python
with open(filepath, "r", encoding="utf-8-sig") as f:
    content = f.read()
```

Or clean files in-place:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /app/script.txt
```

## Visualization

```python
graph.visualize('dialogue_graph')        # Creates dialogue_graph.png
graph.visualize('output', format='svg')  # Creates output.svg
```

Requires: `pip install graphviz` and the Graphviz binary.

## Loading from JSON

```python
graph = Graph.from_file('dialogue.json')
graph = Graph.from_dict({'nodes': [...], 'edges': [...]})
graph = Graph.from_json(json_string)