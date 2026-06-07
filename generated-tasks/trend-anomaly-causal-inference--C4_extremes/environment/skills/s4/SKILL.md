---
name: s1
description: Clean messy tabular datasets with deduplication, missing value imputation, outlier handling, and text processing. Use when dealing with dirty data that has duplicates, nulls, or inconsistent formatting.
---

# Data Cleaning Framework

Strategy-based pipeline for deduplication, missing value imputation, text processing, and outlier handling.

## Data Loading

Strip UTF-8 BOM and extreme values (0, negative, -999) from price columns:

```bash
python3 /app/.claude/skills/s1/scripts/clean_data.py /app/data/amazon-purchases-2019-2020_dirty.csv
# With column index for extreme-value removal (0-based):
python3 /app/.claude/skills/s1/scripts/clean_data.py /app/data/amazon-purchases-2019-2020_dirty.csv 2
```

Load with `pd.read_csv(encoding='utf-8-sig')` after cleaning.

Fix output directory permissions: `python3 /app/.claude/skills/s1/scripts/prepare_output.py /app/output`

## Core Components

### CleaningStrategies

- **Deduplication**: `remove_duplicates(df, subset=None)`
- **Missing Values**: `drop_missing(df, columns)`, `impute_median(df, columns)`, `impute_knn(df, target_features, n_neighbors=5)`, `impute_mode(df, columns)`
- **Text Processing**: `process_text(df, columns, operation)` — operations: `extract_numbers`, `clean_whitespace`, `extract_email`, `lowercase`, `remove_special`
- **Outliers**: `cap_outliers_iqr(df, columns, multiplier=1.5)`, `remove_outliers_iqr(df, columns, multiplier=1.5)`, `remove_outliers_zscore(df, columns, threshold=3.0)`

### DataCleaningPipeline

Chain `.add_step()` calls; call `pipeline.execute(df, verbose=True)` to run. Retrieve log with `pipeline.get_log()`.

---

# Time Series Anomaly Detection Framework

Facebook Prophet counterfactual trend detection. Compares actual vs expected in a target window; anomaly index scaled to [-100, 100].

## Constructor — `TimeSeriesAnomalyDetector`

Key parameters: `min_training_days=180`, `confidence_interval=0.68`, `changepoint_prior_scale=0.05`, `seasonality_prior_scale=10.0`.

## Anomaly Index

- Within CI → 0; Above upper → `(actual−upper)/std`; Below lower → `(actual−lower)/std`
- Scaled: `100 × tanh(raw_index)` → [-100, 100]

## Usage

```python
from anomaly_detection import TimeSeriesAnomalyDetector

detector = TimeSeriesAnomalyDetector(min_training_days=180, confidence_interval=0.68)
results = detector.detect_anomalies(
    df=transaction_df,
    date_col='<temporal column>',
    category_col='<grouping column>',
    value_col='<metric to analyze>',
    cutoff_date='<YYYY-MM-DD>',
    prediction_end='end of prediction window',
    agg_func='sum',
)
anomaly_summary = results['anomaly_summary']
```

## Input Requirements

- **Date column**: temporal column (e.g., `Order Date`)
- **Category column**: grouping granularity for looped modeling
- **Value column**: metric to analyze (`Price`, `Spend`, `Revenue`, `Quantity`)
- `cutoff_date`: training (before) vs prediction (after)
- `prediction_end`: end of detection window
- `agg_func`: `'sum'`, `'mean'`, `'count'`, or `None`

## Output

Returns dict: `anomaly_summary` (DataFrame sorted by `Anomaly_Index` desc), `predictions` (dict of DataFrames with `ds`, `yhat`, `yhat_lower`, `yhat_upper`), `models` (dict of fitted Prophet objects).

**anomaly_summary columns**: `{category_col}`, `Anomaly_Index`, `days_with_data`, `avg_daily_anomaly`, `max_daily_anomaly`, `min_daily_anomaly`, `total_actual`, `total_predicted`.

---

# Feature Engineering Framework

Pipeline for numerical scaling, categorical encoding, polynomial features, and feature selection.

## FeatureEngineeringStrategies

- **Numerical**: `scale_numerical(df, columns, method)` — `'standard'`/`'minmax'`/`'robust'`; `create_bins(df, columns, n_bins, strategy)` — `'uniform'`/`'quantile'`/`'kmeans'`; `create_polynomial_features(df, columns, degree)`; `create_interaction_features(df, column_pairs)`; `create_log_features(df, columns)`
- **Categorical**: `encode_categorical(df, columns, method)` — `'onehot'`/`'label'`/`'frequency'`/`'hash'`; `create_category_aggregations(df, categorical_col, numerical_cols, agg_funcs)`
- **Binary**: `convert_to_binary(df, columns)` — Yes/No, True/False → 0/1
- **Validation**: `validate_numeric_features(df, exclude_cols)`; `validate_no_constants(df, exclude_cols)`
- **Selection**: `select_features_variance(df, columns, threshold=0.01)`; `select_features_correlation(df, columns, threshold)`

## Critical Requirements

1. ALL output features MUST be numeric (int or float).
2. Preview types before processing: `df.dtypes`, `df.head()`.
3. Encode ALL categorical variables.
4. Verify: `df.select_dtypes(include='number').shape[1] == df.shape[1] - 1` (excluding ID).

## Usage

```python
from feature_engineering import FeatureEngineeringStrategies, FeatureEngineeringPipeline

pipeline = FeatureEngineeringPipeline(name="Demographics")
pipeline.add_step(FeatureEngineeringStrategies.convert_to_binary, columns=['<col5>', '<col2>']) \
  .add_step(FeatureEngineeringStrategies.encode_categorical, columns=['<col3>', '<col7>'], method='onehot') \
  .add_step(FeatureEngineeringStrategies.scale_numerical, columns=['<col10>', '<col1>'], method='standard') \
  .add_step(FeatureEngineeringStrategies.validate_numeric_features, exclude_cols=['<ID>']) \
  .add_step(FeatureEngineeringStrategies.validate_no_constants, exclude_cols=['<ID>']) \
  .add_step(FeatureEngineeringStrategies.select_features_variance, columns=[], threshold=0.01)

df_complete = pipeline.execute(cleaned_df, verbose=True)
features = pipeline.get_engineered_features()
df_final = df_complete[['<ID>'] + features]
```

---

# Difference-in-Differences Framework

DiD causal inference with automatic method selection (Multivariate vs Univariate) based on sample size.

## Methodology

### Intensive Margin
- Continuous outcome among participants only (e.g., spending per purchaser).
- Sparse data — do NOT include non-participants.

### Extensive Margin
- Binary 0/1 outcome (participation) across ALL entities × ALL periods.
- MUST include non-participants to measure adoption.

### Regression

`Y = α + βX + γPost + δ(X × Post) + ε` — δ is the DiD estimate.

- **Multivariate Heterogeneous DiD**: all features simultaneously; controls confounding. Used when `n ≥ k × min_sample_ratio`.
- **Univariate DiD**: separate regression per feature; fallback for small samples.

## Data Preparation

**Intensive (sparse):**
```python
intensive_df = transactions.groupby(['entity_id', 'period'])['value'].sum().reset_index()
```

**Extensive (complete panel):**
```python
from itertools import product
all_entities = entities_df['entity_id'].unique()
all_periods = ['baseline', 'treatment']
complete_grid = pd.DataFrame(list(product(all_entities, all_groups, all_periods)),
                             columns=['entity_id', 'period'])
events_lookup = transactions[['entity_id', 'period']].drop_duplicates()
events_lookup['participated'] = 1
extensive_df = complete_grid.merge(events_lookup, how='left')
extensive_df['participated'] = extensive_df['participated'].fillna(0).astype(int)
```

## API

### `DIDAnalyzer(min_sample_ratio=10, significance_level=0.05, min_group_size=1)`

### `intensive_margin(df, features, value_col, top_n=None, sort_by='estimate', asc=False)`
- `df`: sparse (participants only); `features`: demographic columns; `value_col`: continuous outcome.
- Returns list of `{"feature", "did_estimate", "p_value", "method"}`.

### `extensive_margin(df, features, value_col='purchased', top_n=None, sort_by='estimate', asc=False)`
- `df`: complete panel (all entities × all periods); `value_col`: binary 0/1.
- Returns list of `{"feature", "did_estimate", "p_value", "method"}`.

### Method Selection
Tries Multivariate first; falls back to Univariate if sample size insufficient.