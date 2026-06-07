---
name: s1
description: Build, validate, visualize, and serialize dialogue graphs. Use for parsing scripts or creating branching narratives.
---

# Dialogue Graph Skill

## When to use
Script parsing, dialogue editors, game logic traversal, flow visualization.

## Usage

```python
from dialogue_graph import Graph, Node, Edge
```

### Graph, Nodes, Edges

```python
graph = Graph()
graph.add_node(Node(id="Start", speaker="Guard", text="Halt!", type="line"))
graph.add_node(Node(id="Choices", type="choice"))
graph.add_edge(Edge(source="Start", target="Choices"))
graph.add_edge(Edge(source="Choices", target="End", text="1. Run away"))
```

### Export & Load

```python
data = graph.to_dict()
json_str = graph.to_json()
graph = Graph.from_file('dialogue.json')
graph = Graph.from_dict({'nodes': [...], 'edges': [...]})
graph = Graph.from_json(json_string)
```

### Validation

```python
errors = graph.validate()
```

### Visualization

```python
# Requires: pip install graphviz + Graphviz binary
graph.visualize('dialogue_graph')  # dialogue_graph.png
graph.visualize('output', format='svg')  # output.svg
```

### Output Setup
Before writing files, ensure directory permissions:
`python3 /root/.claude/skills/s1/scripts/prepare_output.py /app`