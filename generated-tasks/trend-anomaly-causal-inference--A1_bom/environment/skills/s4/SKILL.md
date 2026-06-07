---
name: s1
description: Modular framework for cleaning tabular data, detecting time series anomalies, engineering features, and performing difference-in-differences causal inference.
---

# Data Cleaning

Strategy-based pipeline for deduplication, imputation, text processing, and outlier handling.

**Scripts:** `python3 /app/.claude/skills/s1/scripts/clean_data.py /app/data/amazon-purchases-2019-2020_dirty.csv` | `python3 /app/.claude/skills/s1/scripts/prepare_output.py /app/output`

### CleaningStrategies

- **Dedup:** `remove_duplicates(df, subset=None)`
- **Missing:** `drop_missing(df, columns)`, `impute_median(df, columns)`, `impute_knn(df, target_features, n_neighbors=5)`, `impute_mode(df, columns)`
- **Text:** `process_text(df, columns, operation)` — ops: `extract_numbers`, `clean_whitespace`, `extract_email`, `lowercase`, `remove_special`
- **Outliers:** `cap_outliers_iqr(df, columns, multiplier=1.5)`, `remove_outliers_iqr(df, columns, multiplier=1.5)`, `remove_outliers_zscore(df, columns, threshold=3.0)`

### Usage

```python
from data_cleaning import CleaningStrategies, DataCleaningPipeline

pipeline = DataCleaningPipeline(name="Transaction Data")
pipeline.add_step(
    CleaningStrategies.remove_duplicates,
    subset=['customer_id', 'order_date'],
    description="Remove duplicate orders"
).add_step(
    CleaningStrategies.drop_missing,
    columns=['customer_id', 'amount'],
    description="Drop rows with missing critical fields"
).add_step(
    CleaningStrategies.impute_knn,
    target_features={
        'income': {'features': ['age', 'education'], 'type': 'numeric'}
    },
    description="KNN imputation for income"
).add_step(
    CleaningStrategies.cap_outliers_iqr,
    columns=['amount'],
    multiplier=1.5,
    description="Cap price outliers"
)

df_clean = pipeline.execute(raw_df, verbose=True)
log_df = pipeline.get_log()
```

# Time Series Anomaly Detection

Facebook Prophet-based anomaly detection comparing counterfactual predictions with actuals. Anomaly index: [-100, 100].

### TimeSeriesAnomalyDetector

**Params:** `min_training_days` (180), `confidence_interval` (0.68), `changepoint_prior_scale` (0.05; use 0.1 for smaller datasets), `seasonality_prior_scale` (10.0)

**Index calc:** Within CI→0; Above→`(actual-upper)/std`; Below→`(actual-lower)/std`; Scaled→`100×tanh(raw)`.

### Usage

```python
from anomaly_detection import TimeSeriesAnomalyDetector

detector = TimeSeriesAnomalyDetector(
    min_training_days=180,
    confidence_interval=0.68
)

results = detector.detect_anomalies(
    df=transaction_df,
    date_col='<temporal column>',
    category_col='<grouping column>',
    value_col='<metric to analyze for anomalies>',
    cutoff_date='<YYYY-MM-DD>',
    prediction_end='end of prediction window',
    agg_func='sum',
)

anomaly_summary = results['anomaly_summary']
top_surge = results['anomaly_summary'].head(10)['<grouping column>'].tolist()
top_slump = results['anomaly_summary'].tail(10)['<grouping column>'].tolist()
```

**Input:** Date, Category (loop granularity), Value (y) columns. `cutoff_date` splits training/prediction; `agg_func`: `'sum'`, `'mean'`, `'count'`, or `None`.

**Output:** `{'anomaly_summary': pd.DataFrame, 'predictions': Dict[str, pd.DataFrame], 'models': Dict[str, Prophet]}`

**anomaly_summary columns:** `{category_col}`, `Anomaly_Index`, `days_with_data`, `avg_daily_anomaly`, `max_daily_anomaly`, `min_daily_anomaly`, `total_actual`, `total_predicted`. Sorted by `Anomaly_Index` desc.

**predictions:** Key=category, Value=DataFrame with `ds`, `yhat`, `yhat_lower`, `yhat_upper`.

# Feature Engineering

Strategy-based pipeline. **CRITICAL:** ALL output features MUST be numeric. Encode ALL categoricals. Verify: `df.select_dtypes(include='number').shape[1] == df.shape[1] - 1`.

### FeatureEngineeringStrategies

- **Numerical:** `scale_numerical(df, columns, method)` — 'standard'/'minmax'/'robust'; `create_bins(df, columns, n_bins, strategy)` — 'uniform'/'quantile'/'kmeans'; `create_polynomial_features(df, columns, degree)`; `create_interaction_features(df, column_pairs)`; `create_log_features(df, columns)`
- **Categorical:** `encode_categorical(df, columns, method)` — 'onehot'/'label'/'frequency'/'hash'; `create_category_aggregations(df, categorical_col, numerical_cols, agg_funcs)`
- **Binary:** `convert_to_binary(df, columns)` — Yes/No, True/False → 0/1
- **Validation:** `validate_numeric_features(df, exclude_cols)`, `validate_no_constants(df, exclude_cols)`
- **Selection:** `select_features_variance(df, columns, threshold)` (default 0.01), `select_features_correlation(df, columns, threshold)`

### Usage

```python
from feature_engineering import FeatureEngineeringStrategies, FeatureEngineeringPipeline

pipeline = FeatureEngineeringPipeline(name="Demographics")
pipeline.add_step(
    FeatureEngineeringStrategies.convert_to_binary,
    columns=['<column5>', '<column2>'],
    description="Convert binary survey responses to 0/1"
).add_step(
    FeatureEngineeringStrategies.encode_categorical,
    columns=['<column3>', '<column7>'],
    method='onehot',
    description="One-hot encode categorical features"
).add_step(
    FeatureEngineeringStrategies.scale_numerical,
    columns=['<column10>', '<column1>'],
    method='standard',
    description="Standardize numerical features"
).add_step(
    FeatureEngineeringStrategies.validate_numeric_features,
    exclude_cols=['<ID Column>'],
    description="Verify all features are numeric"
).add_step(
    FeatureEngineeringStrategies.validate_no_constants,
    exclude_cols=['<ID Column>'],
    description="Remove constant columns"
).add_step(
    FeatureEngineeringStrategies.select_features_variance,
    columns=[],
    threshold=0.01,
    description="Remove low-variance features"
)

df_complete = pipeline.execute(your_cleaned_df, verbose=True)
engineered_features = pipeline.get_engineered_features()
df_id_pure_features = df_complete[['<ID Column>'] + engineered_features]
log_df = pipeline.get_log()
```

# Difference-in-Differences

DiD causal inference with automatic method selection (Multivariate vs Univariate) based on sample size.

### Methodology

**Intensive Margin:** How much behavior changed among participants (continuous outcome). Sparse data — participants only. Do NOT include non-participants.

**Extensive Margin:** How many changed behavior (binary 0/1). Complete panel — all entities × all periods including non-participants.

**Regression:** `Y = α + βX + γPost + δ(X × Post) + ε` where δ is the DiD estimate.

- **Multivariate Heterogeneous DiD:** All features simultaneously; controls confounding; used when `n ≥ k × min_sample_ratio` (default 10k min).
- **Univariate DiD:** Separate regression per feature; fallback for small samples.

### Data Preparation

```python
# Intensive Margin — Sparse Data
intensive_df = transactions.groupby(['entity_id', 'period'])['value'].sum().reset_index()
```

```python
# Extensive Margin — Complete Panel
from itertools import product
all_entities = entities_df['entity_id'].unique()
all_groups = target_groups
all_periods = ['baseline', 'treatment']

complete_grid = pd.DataFrame(
    list(product(all_entities, all_groups, all_periods)),
    columns=['entity_id', 'period']
)

events_lookup = transactions[['entity_id', 'period']].drop_duplicates()
events_lookup['participated'] = 1

extensive_df = complete_grid.merge(events_lookup, how='left')
extensive_df['participated'] = extensive_df['participated'].fillna(0).astype(int)
```

### API

**Constructor:** `DIDAnalyzer(min_sample_ratio=10, significance_level=0.05, min_group_size=1)`

**`intensive_margin(df, features, value_col, top_n=None, sort_by='estimate', asc=False)`** — Input: sparse entity-period data. Returns: `List[{"feature": str, "did_estimate": float, "p_value": float, "method": str}]`

**`extensive_margin(df, features, value_col='purchased', top_n=None, sort_by='estimate', asc=False)`** — Input: complete entity-period panel. Returns same structure.