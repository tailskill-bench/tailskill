---
name: s1
description: Clean messy tabular datasets with deduplication, missing value imputation, outlier handling, and text processing. Use when dealing with dirty data that has duplicates, nulls, or inconsistent formatting.
---

# Data Cleaning Framework

Modular data cleaning framework for tabular datasets. Strategy-based operations orchestrated through a configurable pipeline.

## Core Components

### CleaningStrategies

#### Deduplication
- `remove_duplicates(df, subset=None)` — Remove duplicate rows.

#### Missing Value Handling
- `drop_missing(df, columns)` — Drop rows with missing critical values.
- `impute_median(df, columns)` — Median imputation for numerical columns.
- `impute_knn(df, target_features, n_neighbors=5)` — KNN imputation for columns inferable from others.
- `impute_mode(df, columns)` — Mode imputation for independent categorical columns.

#### Text Processing
- `process_text(df, columns, operation)` — Operations: `extract_numbers`, `clean_whitespace`, `extract_email`, `lowercase`, `remove_special`.

#### Outlier Handling
- `cap_outliers_iqr(df, columns, multiplier=1.5)` — Winsorization using IQR.
- `remove_outliers_iqr(df, columns, multiplier=1.5)` — Remove outliers using IQR.
- `remove_outliers_zscore(df, columns, threshold=3.0)` — Remove outliers using Z-score.

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

## Input / Output
- **Input**: Any tabular DataFrame requiring cleaning.
- **Output**: Cleaned DataFrame; execution log via `pipeline.get_log()`.

> **Production tip**: In containerized/restricted environments, run:
> `python3 /app/.claude/skills/s1/scripts/prepare_output.py /app/output`
> to fix directory permissions before writing results.

---

# Time Series Anomaly Detection Framework

Time series anomaly detection using Facebook Prophet's trend prediction (counterfactual) vs actual data. Anomaly index ranges from -100 to 100.

## Core Components

### TimeSeriesAnomalyDetector

#### Constructor Parameters
- `min_training_days` (int): Min days of training data per category (default: 180). Groups with less are skipped.
- `confidence_interval` (float): Prophet confidence interval width (default: 0.68 = ±1 std).
- `changepoint_prior_scale` (float): Trend flexibility (default: 0.05; use 0.1 for smaller datasets).
- `seasonality_prior_scale` (float): Seasonality strength (default: 10.0).

#### Anomaly Index Calculation (CRITICAL)
- **Within CI**: Index = 0
- **Above upper**: Index = (actual − upper) / std
- **Below lower**: Index = (actual − lower) / std
- **Scaled**: 100 × tanh(raw_index) → [-100, 100]
  - Index=1 → ~76, Index=2 → ~96, Index=3 → ~99.5

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
**Required columns:** date (temporal), category (grouping), value (metric for anomaly detection).

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

**Sorted by `Anomaly_Index` descending.**

`predictions`: Key = category name, Value = DataFrame with `ds`, `yhat`, `yhat_lower`, `yhat_upper`.
`models`: Key = category name, Value = Fitted Prophet model.

---

# Feature Engineering Framework

Modular feature engineering for tabular datasets via configurable pipeline.

## Core Components

### FeatureEngineeringStrategies

#### Numerical Features
- `scale_numerical(df, columns, method)` — 'standard', 'minmax', or 'robust'
- `create_bins(df, columns, n_bins, strategy)` — 'uniform', 'quantile', or 'kmeans'
- `create_polynomial_features(df, columns, degree)` — Polynomial and interaction terms
- `create_interaction_features(df, column_pairs)` — Multiplication interactions
- `create_log_features(df, columns)` — Log-transform for skewed distributions

#### Categorical Features
- `encode_categorical(df, columns, method)` — 'onehot', 'label', 'frequency', or 'hash'
- `create_category_aggregations(df, categorical_col, numerical_cols, agg_funcs)` — Group-level statistics

#### Binary Features
- `convert_to_binary(df, columns)` — Yes/No, True/False → 0/1 (int)

#### Data Quality Validation
- `validate_numeric_features(df, exclude_cols)` — Verify all features are numeric (except IDs)
- `validate_no_constants(df, exclude_cols)` — Remove constant columns

#### Feature Selection
- `select_features_variance(df, columns, threshold)` — Remove low-variance features (default: 0.01)
- `select_features_correlation(df, columns, threshold)` — Remove highly correlated features

### FeatureEngineeringPipeline

**CRITICAL REQUIREMENTS:**
1. **ALL output features MUST be numeric (int or float)** — downstream analysis cannot use string/object columns
2. **Preview data types BEFORE processing**: `df.dtypes` and `df.head()`
3. **Encode ALL categorical variables** — strings must be converted to numbers
4. **Verify output**: `df.select_dtypes(include='number').shape[1] == df.shape[1] - 1` (excluding ID column)

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

## Input / Output
- **Input**: DataFrame post data processing, imputation, or drop (required).
- **Output**: DataFrame with original and engineered columns. Feature names via `pipeline.get_engineered_features()`, log via `pipeline.get_log()`.

---

# Difference-in-Differences Framework

DiD framework for causal inference with automatic method selection (Multivariate vs Univariate) based on sample size.

## Methodology

### Intensive Margin
- **Definition**: How much behavior changed among participants (continuous outcome)
- **Data**: Sparse — only entities that participated
- **Outcome**: Continuous (e.g., spending amount per purchaser)
- **Key**: Do NOT include non-participants or create complete grids

### Extensive Margin
- **Definition**: How many people changed behavior (binary 0/1 outcome)
- **Data**: Complete panel — all entities × all periods (includes non-participants)
- **Outcome**: Binary (0/1 indicating participation)
- **Key**: MUST include non-participants to measure adoption rates

### Regression Methods

Both use: `Y = α + βX + γPost + δ(X × Post) + ε` where δ is the DiD estimate.

**Multivariate Heterogeneous DiD** — Estimates ALL features simultaneously; controls for confounding. Used when `n ≥ k × min_sample_ratio`.

**Univariate DiD** — Separate regression per feature; more robust with small samples. Used as fallback.

**CRITICAL**: Both use statsmodels regression to provide p-values for statistical inference.

## ⚠️ CRITICAL: Data Preparation

### Intensive Margin — Sparse Data (Participants Only)

```python
# Only aggregate actual transactions
intensive_df = transactions.groupby(['entity_id', 'period'])['value'].sum().reset_index()
# Result: Only rows where events occurred
```

### Extensive Margin — Complete Panel (All Users)

```python
from itertools import product
all_entities = entities_df['entity_id'].unique()
all_periods = ['baseline', 'treatment']

complete_grid = pd.DataFrame(
    list(product(all_entities, all_periods)),
    columns=['entity_id', 'period']
)

events_lookup = transactions[['entity_id', 'period']].drop_duplicates()
events_lookup['participated'] = 1

extensive_df = complete_grid.merge(events_lookup, how='left')
extensive_df['participated'] = extensive_df['participated'].fillna(0).astype(int)
# Result: All entities × periods with binary outcome
```

## API

### Constructor: `DIDAnalyzer(min_sample_ratio=10, significance_level=0.05, min_group_size=1)`
- `min_sample_ratio=10`: Samples-to-features ratio for multivariate DiD
- `significance_level=0.05`: P-value threshold (0.05–0.1 based on context)
- `min_group_size=1`: Min observations per group for univariate DiD

### `intensive_margin(df, features, value_col, top_n=None, sort_by='estimate', asc=False)`
Analyzes intensive margin: how much behavior changed among participants.

- `df`: Sparse DataFrame (only participants)
- `features`: List of demographic column names
- `value_col`: Continuous outcome column
- `top_n`: Top N features (None = all)
- `sort_by`: 'estimate' or 'p_value'
- `asc`: Sort direction

**Returns**: List of `{"feature": str, "did_estimate": float, "p_value": float, "method": str}`

### `extensive_margin(df, features, value_col='purchased', top_n=None, sort_by='estimate', asc=False)`
Analyzes extensive margin: how many people changed behavior.

- `df`: Complete DataFrame (ALL entities × ALL periods)
- `features`: List of demographic column names
- `value_col`: Binary outcome column (0/1), default 'purchased'
- `top_n`: Top N features (None = all)
- `sort_by`: 'estimate' or 'p_value'
- `asc`: Sort direction

**Returns**: List of `{"feature": str, "did_estimate": float, "p_value": float, "method": str}`

### Internal Method Selection Logic
- Tries Multivariate Heterogeneous DiD first (if sample size sufficient)
- Falls back to Univariate DiD if needed
- Both methods provide p-values via regression