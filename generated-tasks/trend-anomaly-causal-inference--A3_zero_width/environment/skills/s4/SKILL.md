---
name: s1
description: Modular framework for cleaning tabular data, detecting time series anomalies, engineering features, and performing difference-in-differences causal inference.
---

# Data Cleaning Framework

Strip zero-width Unicode (U+200B/C/D) before processing:
`python3 /app/.claude/skills/s1/scripts/clean_data.py /app/data/amazon-purchases-2019-2020_dirty.csv`

## CleaningStrategies

- **Dedup**: `remove_duplicates(df, subset=None)`
- **Missing**: `drop_missing(df, columns)`, `impute_median(df, columns)`, `impute_knn(df, target_features, n_neighbors=5)` (KNN when target inferrable from other columns), `impute_mode(df, columns)`
- **Text**: `process_text(df, columns, operation)` — ops: `extract_numbers`, `clean_whitespace`, `extract_email`, `lowercase`, `remove_special`
- **Outliers**: `cap_outliers_iqr(df, columns, multiplier=1.5)`, `remove_outliers_iqr(df, columns, multiplier=1.5)`, `remove_outliers_zscore(df, columns, threshold=3.0)`

## DataCleaningPipeline Usage

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

**I/O**: Input any tabular DataFrame. Output cleaned DataFrame; log via `pipeline.get_log()`. In containers: `python3 /app/.claude/skills/s1/scripts/prepare_output.py /app/output`

---

# Time Series Anomaly Detection

Facebook Prophet counterfactual trend prediction. Anomaly index: [-100, 100].

## TimeSeriesAnomalyDetector

**Constructor**: `min_training_days` (int, default 180; fewer → skip), `confidence_interval` (float, default 0.68=±1σ), `changepoint_prior_scale` (float, default 0.05; use 0.1 for smaller datasets), `seasonality_prior_scale` (float, default 10.0).

**Anomaly Index (CRITICAL)**: Within CI→0; Above upper→(actual-upper)/std; Below lower→(actual-lower)/std; Scaled→100×tanh(raw) ∈ [-100,100] (1→~76, 2→~96, 3→~99.5).

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
top_surge = results['anomaly_summary'].head(10)['<grouping column>'].tolist()
top_slump = results['anomaly_summary'].tail(10)['<grouping column>'].tolist()
```

**Input**: Required columns: Date, Category, Value. Params: `cutoff_date` (train/predict split), `prediction_end` (detection window end), `agg_func` (`'sum'`, `'mean'`, `'count'`, or `None`).

**Output**: `{'anomaly_summary': pd.DataFrame, 'predictions': Dict[str, pd.DataFrame], 'models': Dict[str, Prophet]}`

`anomaly_summary` columns: `{category_col}` (str), `Anomaly_Index` (float [-100,100]), `days_with_data` (int), `avg_daily_anomaly` (float), `max_daily_anomaly` (float), `min_daily_anomaly` (float), `total_actual` (float), `total_predicted` (float). **Sorted by `Anomaly_Index` desc.**

`predictions`: key=category, value=DataFrame (`ds`, `yhat`, `yhat_lower`, `yhat_upper`). `models`: key=category, value=fitted Prophet model.

---

# Feature Engineering Framework

## FeatureEngineeringStrategies

- **Numerical**: `scale_numerical(df, columns, method)` ('standard'/'minmax'/'robust'), `create_bins(df, columns, n_bins, strategy)` ('uniform'/'quantile'/'kmeans'), `create_polynomial_features(df, columns, degree)`, `create_interaction_features(df, column_pairs)`, `create_log_features(df, columns)`
- **Categorical**: `encode_categorical(df, columns, method)` ('onehot'/'label'/'frequency'/'hash'), `create_category_aggregations(df, categorical_col, numerical_cols, agg_funcs)`
- **Binary**: `convert_to_binary(df, columns)` — Yes/No, True/False → 0/1 (int)
- **Validation**: `validate_numeric_features(df, exclude_cols)`, `validate_no_constants(df, exclude_cols)`
- **Selection**: `select_features_variance(df, columns, threshold)` (default 0.01), `select_features_correlation(df, columns, threshold)`

## FeatureEngineeringPipeline

**CRITICAL**: ALL output features MUST be numeric (int/float). Preview dtypes (`df.dtypes`, `df.head()`). Encode ALL categoricals. Verify: `df.select_dtypes(include='number').shape[1] == df.shape[1] - 1` (excluding ID).

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

**I/O**: Input cleaned DataFrame. Output DataFrame with original+engineered columns. Feature names via `pipeline.get_engineered_features()`, log via `pipeline.get_log()`.

---

# Difference-in-Differences Framework

Causal inference with automatic method selection (Multivariate vs Univariate) based on sample size.

## Methodology

**Intensive Margin**: How much behavior changed among participants (continuous outcome). Sparse data (participants only). Do NOT include non-participants or create complete grids.

**Extensive Margin**: How many changed behavior (binary 0/1 outcome). Complete panel (all entities × all periods, includes non-participants). MUST include non-participants.

**Regression**: `Y = α + βX + γPost + δ(X × Post) + ε` where δ is the DiD estimate.

**Multivariate Heterogeneous DiD**: All features simultaneously; controls confounding. Used when `n ≥ k × min_sample_ratio`.

**Univariate DiD**: Separate regression per feature; robust with small samples. Fallback when insufficient data.

**CRITICAL**: Both use statsmodels regression for p-values.

## Data Preparation

### Intensive Margin (Sparse)

```python
intensive_df = transactions.groupby(['entity_id', 'period'])['value'].sum().reset_index()
```

### Extensive Margin (Complete Panel)

```python
from itertools import product
all_entities = entities_df['entity_id'].unique()
all_groups = target_groups
all_periods = ['baseline', 'treatment']

complete_grid = pd.DataFrame(
    list(product(all_entities, all_groups, all_periods)),
    columns=['entity_id', 'group', 'period']
)

events_lookup = transactions[['entity_id', 'group', 'period']].drop_duplicates()
events_lookup['participated'] = 1

extensive_df = complete_grid.merge(events_lookup, how='left')
extensive_df['participated'] = extensive_df['participated'].fillna(0).astype(int)
```

## API

**Constructor**: `DIDAnalyzer(min_sample_ratio=10, significance_level=0.05, min_group_size=1)`

**`intensive_margin(df, features, value_col, top_n=None, sort_by='estimate', asc=False)`**
Analyzes intensive margin (continuous outcome among participants). `df`: sparse (participants only). `features`: demographic columns. `value_col`: continuous outcome (e.g., 'amount'). Returns: `[{"feature": str, "did_estimate": float, "p_value": float, "method": str}]`.

**`extensive_margin(df, features, value_col='purchased', top_n=None, sort_by='estimate', asc=False)`**
Analyzes extensive margin (binary participation). `df`: complete (ALL entities × ALL periods). `value_col`: binary (0/1), default 'purchased'. Returns: `[{"feature": str, "did_estimate": float, "p_value": float, "method": str}]`.

**Method Selection**: Tries Multivariate first (if sample sufficient), falls back to Univariate. Both provide p-values via regression.