---
name: s1
description: Clean messy tabular datasets with deduplication, missing value imputation, outlier handling, and text processing. Use when dealing with dirty data that has duplicates, nulls, or inconsistent formatting.
---

# Data Cleaning Framework

Modular data cleaning framework for tabular datasets with strategy-based operations through a configurable pipeline.

## Data Loading

Strip UTF-8 BOM before loading: `python3 /app/.claude/skills/s1/scripts/clean_data.py /app/data/amazon-purchases-2019-2020_dirty.csv`

## Core Components

### CleaningStrategies

#### Deduplication
- `remove_duplicates(df, subset=None)`

#### Missing Value Handling
- `drop_missing(df, columns)` — drop rows with missing critical values
- `impute_median(df, columns)` — median for numerical columns
- `impute_knn(df, target_features, n_neighbors=5)` — KNN when target inferred by related columns
- `impute_mode(df, columns)` — mode for independent categorical columns

#### Text Processing
- `process_text(df, columns, operation)` — operations: `extract_numbers`, `clean_whitespace`, `extract_email`, `lowercase`, `remove_special`

#### Outlier Handling
- `cap_outliers_iqr(df, columns, multiplier=1.5)` — Winsorization using IQR
- `remove_outliers_iqr(df, columns, multiplier=1.5)`
- `remove_outliers_zscore(df, columns, threshold=3.0)`

### DataCleaningPipeline
Orchestrates cleaning steps with logging and progress tracking.

## Usage

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

Prepare output directory: `python3 /app/.claude/skills/s1/scripts/prepare_output.py /app/output`

---

# Time Series Anomaly Detection Framework

Anomaly detection using Facebook Prophet trend prediction. Compares counterfactual predictions in the target window with actual data. Anomaly index ranges from -100 to 100.

## Core Components

### TimeSeriesAnomalyDetector

#### Constructor Parameters
- `min_training_days` (int): Minimum training days per category (default: 180). Groups with less data are skipped.
- `confidence_interval` (float): Prophet confidence interval width (default: 0.68 = ±1 std)
- `changepoint_prior_scale` (float): Trend flexibility (default: 0.05; use 0.1 for smaller datasets)
- `seasonality_prior_scale` (float): Seasonality strength (default: 10.0)

#### Anomaly Index Calculation
- Within CI: Index = 0
- Above upper: Index = (actual - upper) / std
- Below lower: Index = (actual - lower) / std
- Scaled: 100 × tanh(raw_index) → [-100, 100]

## Usage

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

## Input Format

**Required columns:** Date column, Category column (granularity for loop), Value column (the y of modeling).

**Parameters:** `cutoff_date` divides training (before) from prediction (after); `prediction_end` is end of anomaly window; `agg_func` is aggregation per category per day (`'sum'`, `'mean'`, `'count'`, or `None`).

## Output

`detect_anomalies()` returns:

```python
{
    'anomaly_summary': pd.DataFrame,
    'predictions': Dict[str, pd.DataFrame],
    'models': Dict[str, Prophet]
}
```

### `anomaly_summary` Schema

| Column | Type | Description |
|--------|------|-------------|
| `{category_col}` | str | Category name |
| `Anomaly_Index` | float | Scaled anomaly score [-100, 100] |
| `days_with_data` | int | Days with actual data in prediction window |
| `avg_daily_anomaly` | float | Average daily scaled anomaly |
| `max_daily_anomaly` | float | Maximum daily scaled anomaly |
| `min_daily_anomaly` | float | Minimum daily scaled anomaly |
| `total_actual` | float | Sum of actual values in prediction window |
| `total_predicted` | float | Sum of predicted (yhat) values |

Sorted by `Anomaly_Index` descending.

`predictions`: Key = category, Value = DataFrame with `ds`, `yhat`, `yhat_lower`, `yhat_upper`.
`models`: Key = category, Value = fitted Prophet model.

---

# Feature Engineering Framework

Strategy-based feature engineering through a configurable pipeline.

## Core Components

### FeatureEngineeringStrategies

#### Numerical Features
- `scale_numerical(df, columns, method)` — 'standard', 'minmax', or 'robust'
- `create_bins(df, columns, n_bins, strategy)` — 'uniform', 'quantile', or 'kmeans'
- `create_polynomial_features(df, columns, degree)`
- `create_interaction_features(df, column_pairs)`
- `create_log_features(df, columns)`

#### Categorical Features
- `encode_categorical(df, columns, method)` — 'onehot', 'label', 'frequency', or 'hash'
- `create_category_aggregations(df, categorical_col, numerical_cols, agg_funcs)`

#### Binary Features
- `convert_to_binary(df, columns)` — Yes/No, True/False → 0/1 (int)

#### Data Quality Validation
- `validate_numeric_features(df, exclude_cols)` — verify all features are numeric
- `validate_no_constants(df, exclude_cols)` — remove constant columns

#### Feature Selection
- `select_features_variance(df, columns, threshold)` — remove low-variance (default: 0.01)
- `select_features_correlation(df, columns, threshold)` — remove highly correlated

### FeatureEngineeringPipeline

**CRITICAL REQUIREMENTS:**
1. ALL output features MUST be numeric (int or float)
2. Preview types BEFORE processing: `df.dtypes` and `df.head()`
3. Encode ALL categorical variables
4. Verify output: `df.select_dtypes(include='number').shape[1] == df.shape[1] - 1` (excluding ID column)

## Usage

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

---

# Difference-in-Differences Framework

DiD framework for causal inference with automatic method selection (Multivariate vs Univariate) based on sample size.

## Methodology

### Intensive Margin
- How much behavior changed among participants (continuous outcome)
- Sparse data — only entities that participated
- Do NOT include non-participants or create complete grids

### Extensive Margin
- How many people changed behavior (binary 0/1 outcome)
- Complete panel — all entities × all periods (includes non-participants)
- MUST include non-participants to measure adoption rates

### Regression Methods

Both use: `Y = α + βX + γPost + δ(X × Post) + ε` where δ is the DiD estimate.

**Multivariate Heterogeneous DiD** — estimates ALL features simultaneously; controls for confounding; used when `n ≥ k × min_sample_ratio` (default: 10k minimum).

**Univariate DiD** — separate regression per feature; more robust with small samples; used as fallback.

Both use statsmodels regression for p-values.

## Data Preparation

### Intensive Margin — Sparse Data

```python
intensive_df = transactions.groupby(['entity_id', 'period'])['value'].sum().reset_index()
```

### Extensive Margin — Complete Panel

```python
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

## API

### Constructor: `DIDAnalyzer(min_sample_ratio=10, significance_level=0.05, min_group_size=1)`

### `intensive_margin(df, features, value_col, top_n=None, sort_by='estimate', asc=False)`
Analyzes intensive margin. Input: sparse entity-period data (participants only). Returns: `List[{"feature": str, "did_estimate": float, "p_value": float, "method": str}]`

### `extensive_margin(df, features, value_col='purchased', top_n=None, sort_by='estimate', asc=False)`
Analyzes extensive margin. Input: complete entity-period panel (all entities). Returns: `List[{"feature": str, "did_estimate": float, "p_value": float, "method": str}]`

### Internal Method Selection
Tries Multivariate Heterogeneous DiD first (if sample size sufficient); falls back to Univariate DiD.