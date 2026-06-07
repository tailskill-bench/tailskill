---
name: s1
description: Build category taxonomy from hierarchical paths via embedding clustering.
---
# Taxonomy Clustering
Create a unified multi-level taxonomy from hierarchical category paths by clustering similar paths and generating category names auto.
## Methodology
1. **Hierarchical Weighting**: Embed paths with exponentially decaying weights (Level i gets weight 0.6^(i-1))
2. **Recursive Clustering**: Cluster at each level (10-20 clusters at L1, 3-20 at L2-L5) using cosine distance
3. **Intelligent Naming**: Generate names via weighted word frequency + lemmatization + bundle word logic
4. **Quality Control**: Exclude ancestor words, avoid ancestor path duplicates, clean special characters
## Output
DataFrame with added columns:
- `unified_level_1`: Top-level category (e.g., "electronic | device")
- `unified_level_2`: Second-level category (e.g., "computer | laptop")
- `unified_level_3` through `unified_level_N`: Deeper levels
Category names use ` | ` separator, max 5 words, covering 70%+ of records per cluster.
## Installation
```bash
pip install pandas numpy scipy sentence-transformers nltk tqdm
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```
## 4-Step Pipeline
### Step 1: Load, Standardize, Filter and Merge (`step1_preprocessing_and_merge.py`)
- **Input**: List of (DataFrame, source_name) tuples, each with `category_path` column
- **Process**: Per-source deduplication, text cleaning, normalize delimiter to ` > `, depth filtering, prefix removal, then merge. `source_level` reflects the processed source level name
- **Output**: Merged DataFrame with `category_path`, `source`, `depth`, `source_level_1` through `source_level_N`
### Step 2: Weighted Embeddings (`step2_weighted_embedding_generation.py`)
- **Input**: DataFrame from Step 1
- **Output**: Numpy embedding matrix (n_records × 384)
- Weights: L1=1.0, L2=0.6, L3=0.36, L4=0.216, L5=0.1296 (decay 0.6^(n-1))
### Step 3: Clustering (`step3_recursive_clustering_naming.py`)
- **Input**: DataFrame + embeddings from Step 2
- **Output**: Assignments dict {index → {level_1: ..., level_5: ...}}
- Average linkage + cosine distance, 10-20 clusters at L1, 3-20 at L2-L5
- Naming: weighted frequency + lemmatization + coverage ≥70%
### Step 4: Export Results (`step4_result_assignments.py`)
- **Input**: DataFrame + assignments from Step 3
- **Output**:
  - `unified_taxonomy_full.csv` — all records with unified categories
  - `unified_taxonomy_hierarchy.csv` — unique taxonomy structure
## Usage
Run `scripts/pipeline.py` for the complete 4-step workflow. See that file for CLI usage, multi-source examples, and individual step invocation.