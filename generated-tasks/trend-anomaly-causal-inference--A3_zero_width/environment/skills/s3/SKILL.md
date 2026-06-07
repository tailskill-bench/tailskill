---
name: s1
description: Clean messy tabular datasets with deduplication, missing value imputation, outlier handling, and text processing. Use when dealing with dirty data that has duplicates, nulls, or inconsistent formatting.
---

# Data Cleaning Framework

Modular data cleaning framework for tabular datasets with strategy-based operations.

## Data Loading

Strip invisible zero-width Unicode characters (U+200B, U+200C, U+200D) before processing:

`python3 /app/.claude/skills/s1/scripts/clean_data.py /app/data/amazon-purchases-2019-2020_dirty.csv`

## Core Components

### CleaningStrategies

#### Deduplication
- `remove_duplicates(df, subset=None)` — Remove duplicate rows based on metadata and goal logic.

#### Missing Value Handling
- `drop_missing(df, columns)` — Drop rows with missing critical values.
- `impute_median(df, columns)` — Median imputation for numerical columns.
- `impute_knn(df, target_features, n_neighbors=5)` — KNN imputation when target can be inferred from other columns. Evaluate semantic/logical relationships first.
- `impute_mode(df, columns)` — Mode imputation for relatively independent categorical columns.

#### Text Processing
- `process_text(df, columns, operation)` — Operations: `extract_numbers`, `clean_whitespace`, `extract_email`, `lowercase`, `remove_special`.

#### Outlier Handling
- `cap_outliers_iqr(df, columns, multiplier=1.5)` — Winsorization using IQR.
- `remove_outliers_iqr(df, columns, multiplier=1.5)` — Remove outliers using IQR.
- `remove_outliers_zscore(df, columns, threshold=3.0)` — Remove outliers using Z-score.

### DataCleaningPipeline
Orchestrates multiple cleaning steps with logging and progress tracking.

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

---

# Time Series Anomaly Detection Framework

Time series anomaly detection using Facebook Prophet's counterfactual trend prediction. Anomaly index ranges from -100 to 100.

## Core Components

### TimeSeriesAnomalyDetector

#### Constructor Parameters
- `min_training_days` (int): Minimum training days per category (default: 180). Fewer → group skipped.
- `confidence_interval` (float): Prophet confidence width (default: 0.68 = ±1 std).
- `changepoint_prior_scale` (float): Trend flexibility (default: 0.05; use 0.1 for smaller datasets).
- `seasonality_prior_scale` (float): Seasonality strength (default: 10.0).

#### Anomaly Index Calculation (CRITICAL)
- **Within CI**: Index = 0
- **Above upper**: Index = (actual - upper) / std
- **Below lower**: Index = (actual - lower) / std
- **Scaled**: 100 × tanh(raw_index) → [-100, 100] (Index=1→~76, Index=2→~96, Index=3→~99.5)

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

## Input Format
**Required columns:** Date (e.g., `Order Date`), Category (e.g., `Region`), Value (e.g., `Revenue`).

**Parameters:** `cutoff_date` (training/prediction split), `prediction_end` (detection window end), `agg_func` (`'sum'`, `'mean'`, `'count'`, or `None`).

## Output

`detect_anomalies()` returns: `{'anomaly_summary': pd.DataFrame, 'predictions': Dict[str, pd.DataFrame], 'models': Dict[str, Prophet]}`

### `anomaly_summary` Columns
`{category_col}` (str), `Anomaly_Index` (float, [-100,100]), `days_with_data` (int), `avg_daily_anomaly` (float), `max_daily_anomaly` (float), `min_daily_anomaly` (float), `total_actual` (float), `total_predicted` (float). **Sorted by `Anomaly_Index` descending.**

### `predictions` Dictionary
Key = category name, Value = DataFrame with `ds`, `yhat`, `yhat_lower`, `yhat_upper`.

### `models` Dictionary
Key = category name, Value = Fitted Prophet model object.

---

# Feature Engineering Framework

Modular feature engineering with strategy-based operations through a configurable pipeline.

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
- `validate_numeric_features(df, exclude_cols)` — Verify all features numeric (except IDs)
- `validate_no_constants(df, exclude_cols)` — Remove zero-variance columns

#### Feature Selection
- `select_features_variance(df, columns, threshold)` — Remove low-variance (default: 0.01)
- `select_features_correlation(df, columns, threshold)` — Remove highly correlated

### FeatureEngineeringPipeline

**CRITICAL REQUIREMENTS:**
1. **ALL output features MUST be numeric (int or float)** — downstream cannot use strings.
2. **Preview dtypes BEFORE processing**: `df.dtypes` and `df.head()`.
3. **Encode ALL categoricals** — strings must convert to numbers.
4. **Verify output**: `df.select_dtypes(include='number').shape[1] == df.shape[1] - 1` (excluding ID).

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
- **Input**: DataFrame after cleaning/imputation.
- **Output**: DataFrame with original + engineered columns. Feature names via `pipeline.get_engineered_features()`. Log via `pipeline.get_log()`.

---

# Difference-in-Differences Framework

DiD framework for causal inference with automatic method selection (Multivariate vs Univariate) based on sample size.

## Methodology

### Intensive Margin
- **Definition**: How much behavior changed among participants (continuous outcome).
- **Data**: Sparse — only participating entities.
- **Outcome**: Continuous (e.g., spending per purchaser).
- **Key**: Do NOT include non-participants or create complete grids.

### Extensive Margin
- **Definition**: How many changed behavior (binary 0/1 outcome).
- **Data**: Complete panel — all entities × all periods (includes non-participants).
- **Outcome**: Binary (0/1 participation).
- **Key**: MUST include non-participants to measure adoption.

### Regression Methods

Both use: `Y = α + βX + γPost + δ(X × Post) + ε` where δ is the DiD estimate.

**Multivariate Heterogeneous DiD** — All features simultaneously; controls confounding. Used when `n ≥ k × min_sample_ratio`.

**Univariate DiD** — Separate regression per feature; robust with small samples. Fallback when insufficient data.

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

### Constructor: `DIDAnalyzer(min_sample_ratio=10, significance_level=0.05, min_group_size=1)`

### `intensive_margin(df, features, value_col, top_n=None, sort_by='estimate', asc=False)`
Analyzes intensive margin (continuous outcome among participants).
- `df`: Sparse DataFrame (participants only).
- `features`: Demographic column names.
- `value_col`: Continuous outcome (e.g., 'amount').
- **Returns**: List of `{"feature": str, "did_estimate": float, "p_value": float, "method": str}`.

### `extensive_margin(df, features, value_col='purchased', top_n=None, sort_by='estimate', asc=False)`
Analyzes extensive margin (binary participation outcome).
- `df`: Complete DataFrame (ALL entities × ALL periods).
- `value_col`: Binary outcome (0/1), default 'purchased'.
- **Returns**: List of `{"feature": str, "did_estimate": float, "p_value": float, "method": str}`.

### Internal Method Selection
Tries Multivariate first (if sample sufficient), falls back to Univariate. Both provide p-values via regression.