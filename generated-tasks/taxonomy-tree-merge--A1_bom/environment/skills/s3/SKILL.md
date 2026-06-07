---
name: s1
description: Build unified multi-level category taxonomy from hierarchical product category paths using embedding-based recursive clustering with intelligent category naming via weighted word frequency analysis.
---

# Hierarchical Taxonomy Clustering

## Methodology

1. **Hierarchical Weighting**: Embeddings with exponential decay — Level i gets weight 0.6^(i-1)
2. **Recursive Clustering**: Average linkage + cosine distance; 10-20 clusters at L1, 3-20 at L2-L5
3. **Intelligent Naming**: Weighted word frequency + lemmatization + bundle word logic
4. **Quality Control**: Exclude ancestor words, avoid ancestor path duplicates, clean special characters

## Data Loading

Use `encoding='utf-8-sig'` with `pd.read_csv()`, or run:
`python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/amazon_product_categories.csv`

## Output

DataFrame columns: `unified_level_1` through `unified_level_N`. Names use ` | ` separator, max 5 words, ≥70% cluster coverage.

## Installation

```bash
pip install pandas numpy scipy sentence-transformers nltk tqdm
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```

## 4-Step Pipeline

### Step 1: Preprocessing & Merge (`step1_preprocessing_and_merge.py`)
- **Input**: List of (DataFrame, source_name) tuples with `category_path` column
- **Process**: Per-source dedup; clean &/,/'/-/quotes; lemmatize as nouns; normalize delimiter to ` > `; depth filter; prefix removal; merge sources. `source_level` reflects processed source level name
- **Output**: Merged DataFrame with `category_path`, `source`, `depth`, `source_level_1`..`source_level_N`

### Step 2: Weighted Embeddings (`step2_weighted_embedding_generation.py`)
- **Input**: DataFrame from Step 1
- **Output**: Numpy matrix (n_records × 384)
- Weights: L1=1.0, L2=0.6, L3=0.36, L4=0.216, L5=0.1296

### Step 3: Recursive Clustering (`step3_recursive_clustering_naming.py`)
- **Input**: DataFrame + embeddings from Step 2
- **Output**: Assignments dict {index → {level_1: …, level_5: …}}
- Naming: weighted frequency + lemmatization + coverage ≥70%

### Step 4: Export (`step4_result_assignments.py`)
- **Input**: DataFrame + assignments from Step 3
- **Output**: `unified_taxonomy_full.csv`, `unified_taxonomy_hierarchy.csv`

## Usage

Run `scripts/pipeline.py` for the complete workflow.