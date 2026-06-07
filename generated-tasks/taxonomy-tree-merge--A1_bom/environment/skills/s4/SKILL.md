---
name: s1
description: Build unified multi-level category taxonomy from hierarchical product category paths using embedding-based recursive clustering with intelligent category naming via weighted word frequency analysis.
---

# Hierarchical Taxonomy Clustering

**Methodology**: Exponential decay embeddings (weight 0.6^(i-1)), average linkage + cosine distance clustering (10-20 clusters L1, 3-20 L2-L5), weighted word frequency naming with lemmatization, quality control excluding ancestor words/duplicates/special chars.

**Data Loading**: Use `encoding='utf-8-sig'` with `pd.read_csv()`, or run:
`python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/amazon_product_categories.csv`

**Output**: DataFrame columns `unified_level_1` through `unified_level_N`. Names use ` | ` separator, max 5 words, ≥70% cluster coverage.

**Install**:
```bash
pip install pandas numpy scipy sentence-transformers nltk tqdm
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```

## Pipeline Steps

**Step 1** (`step1_preprocessing_and_merge.py`): Input list of (DataFrame, source_name) tuples with `category_path` column. Per-source dedup; clean &/,/'/-/quotes; lemmatize as nouns; normalize delimiter to ` > `; depth filter; prefix removal; merge sources. Output: merged DataFrame with `category_path`, `source`, `depth`, `source_level_1`..`source_level_N`.

**Step 2** (`step2_weighted_embedding_generation.py`): Input DataFrame from Step 1. Output numpy matrix (n_records × 384). Weights: L1=1.0, L2=0.6, L3=0.36, L4=0.216, L5=0.1296.

**Step 3** (`step3_recursive_clustering_naming.py`): Input DataFrame + embeddings from Step 2. Output assignments dict {index → {level_1: …, level_5: …}}. Naming: weighted frequency + lemmatization + coverage ≥70%.

**Step 4** (`step4_result_assignments.py`): Input DataFrame + assignments from Step 3. Output `unified_taxonomy_full.csv`, `unified_taxonomy_hierarchy.csv`.

**Run**: `scripts/pipeline.py`