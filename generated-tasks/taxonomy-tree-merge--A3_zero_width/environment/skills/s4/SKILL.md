---
name: s1
description: Build unified multi-level category taxonomy from hierarchical paths using embedding-based recursive clustering with intelligent naming via weighted word frequency.
---

# Hierarchical Taxonomy Clustering

## Methodology

1. **Hierarchical Weighting**: Exponentially decaying weights (Level i: 0.6^(i-1))
2. **Recursive Clustering**: 10-20 clusters at L1, 3-20 at L2-L5, cosine distance
3. **Intelligent Naming**: Weighted word frequency + lemmatization + bundle word logic
4. **Quality Control**: Exclude ancestor words, avoid path duplicates, clean special chars

## Data Loading

Strip zero-width Unicode (U+200B, U+200C, U+200D):
`python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/amazon_product_categories.csv`

## Output

Columns: `unified_level_1` through `unified_level_N` (e.g., "electronic | device", "computer | laptop"). Names use ` | ` separator, max 5 words, ≥70% cluster coverage.

## Installation

```bash
pip install pandas numpy scipy sentence-transformers nltk tqdm
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```

## Pipeline

### Step 1: Preprocessing (`step1_preprocessing_and_merge.py`)
- **Input**: List of (DataFrame, source_name) tuples with `category_path` column
- **Process**: Per-source dedup, text cleaning (remove &/,/'/-/quotes, lemmatize as nouns), normalize delimiter to ` > `, depth filtering, prefix removal, merge sources
- **Output**: Merged DataFrame with `category_path`, `source`, `depth`, `source_level_1` through `source_level_N`

### Step 2: Weighted Embeddings (`step2_weighted_embedding_generation.py`)
- **Input**: DataFrame from Step 1
- **Output**: Numpy matrix (n_records × 384)
- Weights: L1=1.0, L2=0.6, L3=0.36, L4=0.216, L5=0.1296

### Step 3: Recursive Clustering (`step3_recursive_clustering_naming.py`)
- **Input**: DataFrame + embeddings from Step 2
- **Output**: Assignments dict {index → {level_1: ..., level_5: ...}}
- Average linkage + cosine distance, naming via weighted frequency + lemmatization + coverage ≥70%

### Step 4: Export (`step4_result_assignments.py`)
- **Input**: DataFrame + assignments from Step 3
- **Output**: `unified_taxonomy_full.csv` (all records), `unified_taxonomy_hierarchy.csv` (unique structure)

## Usage

Run via `scripts/pipeline.py`.