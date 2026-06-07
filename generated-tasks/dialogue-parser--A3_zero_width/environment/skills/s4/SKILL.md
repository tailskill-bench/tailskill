---
name: s1
description: Library for building, validating, visualizing, and serializing dialogue graphs. Use when parsing scripts or creating branching narratives.
---

Import: `from dialogue_graph import Graph, Node, Edge`

**Build & Export:**
```python
graph = Graph()
graph.add_node(Node(id="Start", speaker="Guard", text="Halt!", type="line"))
graph.add_node(Node(id="Choices", type="choice"))
graph.add_edge(Edge(source="Start", target="Choices"))
graph.add_edge(Edge(source="Choices", target="End", text="1. Run away"))
data = graph.to_dict()   # {"nodes": [...], "edges": [...]}
json_str = graph.to_json()
errors = graph.validate()
# Returns list of strings, e.g., ["Edge 'Start'->'Unk' points to missing node 'Unk'"]
```

**Load from JSON:**
```python
graph = Graph.from_file('dialogue.json')
graph = Graph.from_dict({'nodes': [...], 'edges': [...]})
graph = Graph.from_json(json_string)
```

**Clean invisible Unicode (U+200B, U+200C, U+200D) before processing:**
```python
import unicodedata
ZW_CHARS = {"\u200b", "\u200c", "\u200d", "\ufeff"}
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()
content = "".join(c for c in content if c not in ZW_CHARS and unicodedata.category(c) not in {"Cf", "Cc"})
```
Or in-place: `python3 /root/.claude/skills/s1/scripts/clean_data.py /app/script.txt`

**Visualization** (requires `pip install graphviz` + Graphviz binary):
```python
graph.visualize('dialogue_graph')          # Creates dialogue_graph.png
graph.visualize('output', format='svg')    # Creates output.svg