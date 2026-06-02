# AGENT.md — TailSkills Variant Task Auto-Generation Guide

> This document guides an AI Agent through automated variant task generation, Oracle solution authoring, S1 skill fusion, and verification.

---

## 0. Global Constraints

1. **Test each variant task immediately after generating it.** Do not batch-generate then test all at once.
2. **S1 skills must be naturally integrated into the original skill.** Do not use words like "trap", "adversarial", "attack", "defense", etc.
3. **Oracle must pass all tests (reward=1.0)** before being considered complete.
4. **Retry at most 3 times.** If it still fails after 3 attempts, mark it as "requires manual intervention" and skip.
5. **Record the status of each variant**: ⬜ Todo → 🔧 In Progress → ✅ Done or ❌ Failed
6. **Docker/infrastructure errors require immediate interruption**: If `harbor run` fails due to Docker daemon not running, permission issues, network/disk failures, etc. (non-code issues), **do not retry; notify the user immediately** and wait for instructions. Only auto-retry for solve.sh/script code errors.
7. **Backup file recovery is prohibited**: C-type variants' (NaN/extreme values/type confusion) clean_data.py **must implement genuine error handling** (e.g., `fillna(median)`, range detection + replacement, `pd.to_numeric(errors='coerce')`). Recovery from backup files is **not allowed**. Backup recovery is a shortcut that undermines the purpose of tail variants testing an agent's error-handling capability. If the base test fails due to exact value checks after median filling, the test tolerance should be relaxed (e.g., allow ±5% variation) rather than reverting to backup recovery.
8. **Oracle must not bypass variant challenges**: The Oracle solution must genuinely confront and resolve the challenges injected by the variant. Bypassing is not allowed. If the base Oracle is already a simple copy type (e.g., `cp answer.xlsx output.xlsx`), the variant Oracle should also keep the copy approach; otherwise, the Oracle must add variant handling (e.g., clean_data.py, prepare_output.py) on top of the base logic, and must not skip the variant challenge to output the answer directly.

---

## 1. Workflow Overview

```
For each (task, variant) pair:
  Step 1: Analyze task → Extract parameters
  Step 2: Injector generates variant directory
  Step 3: Generate auxiliary scripts (clean_data.py, etc.)
  Step 4: Modify Oracle solve.sh → Call auxiliary scripts
  Step 5: Generate S1 skill (original SKILL.md text + naturally interspersed tail handling)
  Step 6: harbor run -a oracle verification
  Step 7: Docker error → Interrupt and ask user | Code error → Fix and retry
  Step 8: Success → ✅ → Next one
```

---

## 2. Step 1: Task Analysis

### Input
- SkillsBench task directory: `skillsbench/tasks/<task-id>/`
- Variant type: e.g., `C1_nan_poison`

### Analysis Steps

#### 2.1 Read Dockerfile
```bash
cat skillsbench/tasks/<task-id>/environment/Dockerfile
```
Extract:
- `COPY` data files → container paths (e.g., `/root/income.xlsx`)
- `pip install` dependencies → candidates for E variant injection
- `ENV` variables → candidates for E3 injection

#### 2.2 Read instruction.md
```bash
cat skillsbench/tasks/<task-id>/instruction.md
```
Extract:
- Task type (data processing/document/network/scientific computing)
- Output file name and path
- Whether there are API/network calls

#### 2.3 Read solve.sh (Most Critical)
```bash
cat skillsbench/tasks/<task-id>/solution/solve.sh
```
Extract:
- Python script `pd.read_csv()` / `pd.read_excel()` → data file paths
- Column names/column indices → determine `col_idx`, `key_col_idx`
- Output write path → `output_file`
- Data processing flow → understand where to insert defensive code

#### 2.4 Read Original Skill
```bash
ls skillsbench/tasks/<task-id>/environment/skills/
cat skillsbench/tasks/<task-id>/environment/skills/*/SKILL.md
```

#### 2.5 Output: Task Parameters

Generate parameters in the following format for subsequent steps:

```yaml
<task-id>:
  data_files:
    - path: "<container_path>"
      format: csv|xlsx|json|bibtex
      numeric_columns: [col_idx, ...]
      key_column: col_idx
  output_file: "<container_output_path>"
  solve_method: "python_heredoc|direct_script|..."
  python_data_load_line: <line_number>
  applicable_variants:
    - <variant_id>: { target_file: "...", col_idx: N, key_col_idx: N }
```

---

## 3. Step 2: Injector Generates Variant Directory

### Prerequisite
`task_variant_matrix.yaml` already contains the parameters for this task.

### Execution
**Windows Note**: In a Windows bash environment, `python3 -c` may fail (exit code 49). Use `python -c` instead.

```python
from tailskills.inject.injector import Injector

injector = Injector(
    skillsbench_root="../skillsbench",
    output_dir="generated-tasks"
)
injector.generate("powerlifting-coef-calc", "C1_nan_poison", force=True)
```

### Output
Generated variant directory:
```
generated-tasks/<task-id>--<variant-id>/
├── task.toml          # Updated with tail-variant tag
├── instruction.md     # Original task instructions
├── environment/
│   ├── Dockerfile     # Variant code injected
│   ├── _tail_inject.py # (Data-layer variant) Data mutation script
│   └── skills/        # Original skills (to be replaced with S1)
├── solution/
│   └── solve.sh       # Original solution (to be modified as Oracle)
└── tests/
    ├── test.sh        # Patched with tail test
    ├── test_outputs.py
    └── test_tail.py   # Variant verification test
```

### Verification
- Dockerfile ends with a `# TailSkills Variant: <variant-id>` comment block
- test_tail.py exists and contains variant-related tests

---

## 4. Steps 3+4: Generate Auxiliary Scripts + Author Oracle solve.sh

### Principle
The Oracle does not embed defensive code inline. Instead, **generate auxiliary scripts first**, and the Oracle calls them via command line.
Auxiliary scripts are placed in `environment/skills/s1/scripts/`, which are automatically copied into the container via Dockerfile `COPY skills`.

### 4.1 Generate Auxiliary Scripts

Select the required scripts based on variant type:

| Variant Type | Required Script | Invocation |
|---------|-----------|---------|
| A1_bom | clean_data.py (with BOM handling) | `python3 /root/.claude/skills/s1/scripts/clean_data.py <file>` |
| A3_zero_width | clean_data.py (with Unicode cleaning) | Same as above |
| C1_nan_poison | clean_data.py (with NaN/Inf handling) | Same + `--key` |
| C3_duplicate_keys | clean_data.py (with deduplication) | Same + `--key` |
| C4_extremes | clean_data.py (with extreme value clipping) | Same |
| C5_type_confusion | clean_data.py (with type conversion) | Same |
| B1_readonly_output | prepare_output.py | `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output>` |
| B3_dirty_output | prepare_output.py | Same |
| E1_missing_dep | No auxiliary script | `pip install <dep>` at the beginning of solve.sh |
| D1_dns_jitter | No auxiliary script | Oracle does not make network requests; processes local data directly |

### 4.2 Oracle solve.sh Invocation Methods

**Method A — Bash-level invocation (recommended, for scripts that modify files in place)**:

Insert script calls before `cat > /tmp/solve.py` in solve.sh:

```bash
#!/bin/bash
pip install pandas openpyxl 2>/dev/null

# >>> TailSkills: Call auxiliary scripts to clean input data <<<
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/income.xlsx --key SA2_CODE
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/demographic_analysis.xlsx

cat > /tmp/solve.py << 'PYTHON_SCRIPT'
import pandas as pd
# ... Original processing logic unchanged ...
PYTHON_SCRIPT

python3 /tmp/solve.py
```

**Method B — Python subprocess invocation (for scenarios requiring interaction with Python logic)**:

```python
import subprocess
subprocess.run(['python3', '/root/.claude/skills/s1/scripts/clean_data.py',
                '/root/income.xlsx', '--key', 'SA2_CODE'], check=True)
```

### 4.3 Notes
- Auxiliary script paths uniformly use `/root/.claude/skills/s1/scripts/` (same location as S1 skills)
- Scripts modify data files in place (overwrite); the Oracle's subsequent code reads the cleaned data
- Preserve the original solve.sh heredoc structure unchanged
- For B1/B3 variants, `prepare_output.py` is placed at the very beginning of solve.sh (before data processing)

### 4.4 Auxiliary Script Design Guidelines (by Variant Type)

#### A1_bom
- BOM injection in XLSX files generates a CSV sidecar file (see 5.4.1)
- clean_data.py needs to process the **sidecar CSV**, not the XLSX itself
- test_tail.py scans all `.csv/.txt/.json` files under `/root/` to check for BOM, including sidecar files
- Invocation: `clean_data.py /root/income.csv` (note: CSV, not XLSX)

#### A3_zero_width
- clean_data.py uses `unicodedata.category(c)` to filter `Cf`/`Cc` category characters
- For XLSX files, uses openpyxl to clean cell by cell; for CSV, uses text processing
- Invocation: `clean_data.py /root/income.xlsx`

#### C1_nan_poison
- test_tail.py (`test_no_nan_in_numeric_output`) checks whether all float values in the output XLSX are NaN
- NaN silently propagates through aggregation operations; must be cleaned before data loading
- clean_data.py should use **median filling** (not row deletion) to keep row counts stable
- Invocation: `clean_data.py /root/income.xlsx --key SA2_CODE`

#### C3_duplicate_keys
- **Must provide `--key` parameter** specifying the key column name; otherwise deduplication is meaningless
- Use `drop_duplicates(subset=[key_col], keep='first')` to retain original rows
- Invocation: `clean_data.py /root/income.xlsx --key SA2_CODE`

#### C4_extremes
- clean_data.py needs to identify which columns "should be positive" (e.g., EARNERS, INCOME, POPULATION)
- Can auto-detect via column name keyword matching (`EARNER`, `INCOME`, `POPULATION`, `TOTAL`)
- Filter condition: `df[col] > 0`
- Invocation: `clean_data.py /root/income.xlsx`

#### C5_type_confusion
- clean_data.py auto-detects which object-type columns can be converted to numeric
- Uses `pd.to_numeric(errors='coerce')` for conversion; if >50% convert successfully, treats it as a numeric column
- Fills resulting NaN with median
- Invocation: `clean_data.py /root/income.xlsx`

#### B1_readonly_output
- Dockerfile patch applies `chmod 555 /root` and `/root/output`
- prepare_output.py needs to **recursively fix parent directory permissions** (Docker runs as root, chmod always succeeds)
- Invocation: `prepare_output.py /root/demographic_analysis.xlsx`

#### B3_dirty_output
- Dockerfile places a corrupted file at the output path (e.g., `echo "CORRUPTED" > /root/output.xlsx`)
- prepare_output.py needs to **first delete the existing file, then fix directory permissions** (combining B1+B3 logic)
- Invocation: `prepare_output.py /root/demographic_analysis.xlsx`

#### E1_missing_dep
- Dockerfile installs all dependencies first, then uninstalls the core dependency at the end via `pip uninstall -y <dep>`
- Ubuntu 24.04 base image requires `--break-system-packages`: `RUN pip3 uninstall -y --break-system-packages <dep>`
- solve.sh reinstalls at the beginning via `pip install --no-cache-dir <dep>==<version>`
- No auxiliary script needed (prepare_output.py / clean_data.py)
- SKILL.md adds to the "Dependencies" or "Quick Start" section: reinstall when encountering `ModuleNotFoundError: No module named '<dep>'`
- **Select core algorithm dependencies** (e.g., statsmodels, casadi, cvxpy, lxml), not lightweight/irrelevant ones (e.g., packaging)
- **test_tail.py three-part suite**: test_output_file_exists + test_<dep>_reinstalled + test_<dep>_functional (verify core functionality is available)

#### D1_dns_jitter
- Dockerfile installs `iptables iproute2` packages
- Creates DNS jitter script and entrypoint wrapper:
  ```dockerfile
  RUN echo '#!/bin/bash\niptables -A OUTPUT -p udp --dport 53 -m statistic --mode random --probability 0.5 -j DROP 2>/dev/null || true' > /usr/local/bin/dns_jitter.sh && \
      chmod +x /usr/local/bin/dns_jitter.sh
  RUN echo '#!/bin/bash\n/usr/local/bin/dns_jitter.sh\nexec "$@"' > /usr/local/bin/entrypoint_wrapper.sh && \
      chmod +x /usr/local/bin/entrypoint_wrapper.sh
  ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
  ```
- 50% random DNS query packet loss, testing agent network retry capability
- Oracle **does not make network requests**; processes local data directly or writes pre-computed answers
- No auxiliary script needed
- SKILL.md inserts DNS retry suggestions in "Network Requests"/"Data Download" related paragraphs:
  ```python
  from tenacity import retry, stop_after_attempt, wait_exponential

  @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
  def download_with_retry(url):
      import urllib.request
      return urllib.request.urlopen(url, timeout=30)
  ```
- test_tail.py only needs `test_output_file_exists`
- **Applicable tasks**: Tasks involving network requests (API calls, data downloads), or tasks with pre-loaded data

#### D2_rate_limit
- Dockerfile installs `iptables iproute2` packages
- Creates API rate limiting script and entrypoint wrapper:
  ```dockerfile
  RUN echo '#!/bin/bash\niptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' > /usr/local/bin/rate_limit.sh && \
      chmod +x /usr/local/bin/rate_limit.sh
  RUN echo '#!/bin/bash\n/usr/local/bin/rate_limit.sh\nexec "$@"' > /usr/local/bin/entrypoint_wrapper.sh && \
      chmod +x /usr/local/bin/entrypoint_wrapper.sh
  ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
  ```
- Limits concurrent HTTPS connections to no more than 3, testing agent handling of API 429/rate limiting
- Oracle **does not make network requests**; processes local data directly or writes pre-computed answers
- No auxiliary script needed
- SKILL.md inserts rate limiting retry suggestions in "Network Requests"/"Data Download" related paragraphs:
  ```python
  import time
  from tenacity import retry, stop_after_attempt, wait_exponential

  @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=30))
  def api_call_with_retry(url):
      import urllib.request
      return urllib.request.urlopen(url, timeout=30)
  ```
- test_tail.py only needs `test_output_file_exists`
- **Applicable tasks**: Tasks involving API calls (SEC EDGAR, NWS API, GitHub API, etc.)

#### E2_version_drift
- Dockerfile installs the correct version of the dependency first, then downgrades to an incompatible old version at the end:
  ```dockerfile
  # Install correct version first
  RUN pip install playwright==1.49.0
  # ... Other build steps ...
  # Downgrade to incompatible old version
  RUN pip install playwright==1.40.0 --force-reinstall
  ```
- solve.sh restores the correct version at the beginning via `pip install --no-cache-dir <package>==<correct_version>`
- No auxiliary script needed
- SKILL.md adds to the "Dependencies" section: check version and reinstall when encountering version incompatibility errors (e.g., `AttributeError`, `ImportError`)
- **Select core dependencies** (e.g., playwright, next) ensuring the old version causes obvious runtime errors
- test_tail.py three-part suite: test_output_file_exists + test_<package>_correct_version + test_<package>_functional
- **Applicable tasks**: Frontend/testing tasks that depend on specific library versions

#### G1_multi_vector
- Dockerfile injects multiple variant challenges simultaneously (e.g., B1+C1+E1 combination), creating multi-layered difficulty
- Stacks injection logic from multiple variants in one Dockerfile:
  ```dockerfile
  # B1: Read-only output directory
  RUN chmod 555 /root/output
  # E1: Uninstall core dependency
  RUN pip uninstall -y <dep>
  ```
- Oracle calls all relevant auxiliary scripts in sequence (first prepare_output.py to fix permissions, then pip install to restore dependencies, finally clean_data.py to clean data)
- SKILL.md integrates handling suggestions for all involved variants
- test_tail.py needs to verify all injected variant challenges are resolved
- **Applicable tasks**: Base tasks with multiple successful single-variant experiences (e.g., CVE remediation, security audit, and other complex tasks)
- **Note**: Must ensure variants do not conflict with each other (e.g., C1+C4 should not inject the same column simultaneously)

#### G2_fix_regression
- Dockerfile modifies test files, introducing regressions in assertions (e.g., relaxing tolerances, removing critical checks):
  ```dockerfile
  # Inject regression: Remove critical assertion or relax check
  RUN sed -i 's/assert result == expected/# assert removed for testing/' /tests/test_outputs.py
  ```
- Oracle's solve.sh needs to **detect and fix test regressions**, restoring correct assertion logic
- Requires auxiliary script `fix_tests.py` to restore original test logic
- SKILL.md adds to "Testing"/"Verification" section: check test file integrity before running; watch for tampered assertions
- test_tail.py verifies test file has restored original logic
- **Applicable tasks**: Tasks involving code modification and testing (e.g., CVE remediation, code refactoring, etc.)

#### C4_extremes / C5_type_confusion (Comparison Tasks)
- C4/C5 variants for comparison tasks (e.g., pdf-excel-diff) cannot use median filling
- **Reason**: Median filled values ≠ PDF original values, causing comparison to produce many false positive differences
- **Correct approach**: clean_data.py sets corrupted values to `None` (openpyxl `cell.value = None`), comparison logic uses `if pd.isna(curr_val): continue` to skip
- Injection scripts use custom `_extremes_xlsx_inject.py` / `_typeconfusion_xlsx_inject.py` instead of standard `_tail_inject.py`
- Target injection columns should be non-critical columns (e.g., Score column), avoiding conflicts with real modified columns (Salary/Dept/Years)

---

## 5. Step 4: Generate S1 Skill

### 5.1 Directory Structure

```
environment/skills/s1/
├── SKILL.md          # Fused skill document
└── scripts/
    └── .py # (Optional) One or more auxiliary scripts
```

If the original skill has multiple directories (e.g., `pdf/`, `xlsx/`), **delete all original directories** and replace with **a single unified** `s1/` directory, merging all original SKILL.md content.

### 5.2 SKILL.md Fusion Principles

**Core**: The original SKILL.md content **must be 100% preserved as-is** — not a single word may be deleted, rewritten, or summarized. Tail handling logic is **naturally interspersed into the corresponding sections of the original text**.

It is **not** about appending independent new sections at the end, but rather **naturally integrating** into relevant paragraphs of the original text. Tail handling content must appear in contextually relevant positions.

### 5.2.1 S1 SKILL.md Generation Steps (Mandatory Process)

**Must strictly follow these steps; do not skip any:**

1. **Copy original text**: Concatenate all original SKILL.md files (e.g., `pdf/SKILL.md` + `xlsx/SKILL.md`) into a single file
   ```bash
   cat pdf/SKILL.md > s1/SKILL.md
   echo -e "\n---\n" >> s1/SKILL.md
   cat xlsx/SKILL.md >> s1/SKILL.md
   ```
2. **Modify frontmatter**: Change `name: pdf` to `name: s1`, merge descriptions
3. **Use Edit tool to insert**: At contextually relevant positions, use Edit to insert tail handling suggestions (a few sentences + script reference)
4. **Prohibited actions**:
   - ❌ Must not summarize, abbreviate, or rewrite any content from the original SKILL.md
   - ❌ Must not delete any code examples, explanatory paragraphs, or sections from the original SKILL.md
   - ❌ Must not rewrite the entire SKILL.md from scratch (must be based on original file concatenation)
   - ✅ Only allowed to **insert** tail handling paragraphs at appropriate positions in the original content

**Prohibited terms**: trap, attack, defense, adversarial, injection, malicious, variant
**Recommended terms**: best practice, recommended approach, common issue in production environments, robust handling, resilient

**Insertion location rules**:
- Encoding/BOM/Unicode → Place after "read data"/"file operations"/"import" related paragraphs in the original text
- NaN/deduplication/extreme values/type confusion → Place after "data processing"/"data transformation"/"analysis" related paragraphs in the original text
- Output permissions/dirty files → Place after "save results"/"output"/"write" related paragraphs in the original text

**Specific insertion anchors** (in common xlsx/pandas skill structures):
- Type A (encoding) → Insert after `pd.read_csv`/`pd.read_excel` code blocks
- Type B (filesystem) → Insert after `wb.save('output.xlsx')` code blocks
- Type C (data boundaries) → Insert after `df.describe()  # Statistics` lines
- Each insertion contains: 2-3 sentences of problem description + inline code example + script reference command
- Auxiliary script reference → Mentioned naturally immediately after the corresponding handling suggestion

### 5.3 SKILL.md Fusion Example

Assume the original SKILL.md has the following structure:

```markdown
## Read Income Data
Use `pd.read_excel('/root/income.xlsx')` to read the income data table.

## Data Pivot
Pivot income data by region and year...

## Save Results
Save analysis results as an XLSX file.
```

After fusion, it becomes (note the positions of new content):

```markdown
## Read Income Data
Use `pd.read_excel('/root/income.xlsx')` to read the income data table.
It is recommended to perform data quality checks after reading; you can run the auxiliary script for one-click processing:
`python3 /root/.claude/skills/s1/scripts/clean_data.py /root/income.xlsx --key SA2_CODE`
This script automatically handles encoding issues, missing values, duplicate rows, and outliers, modifying the file in place.
It is also recommended to use `encoding='utf-8-sig'` when reading to handle potential BOM markers.

## Data Pivot
Pivot income data by region and year...

## Save Results
Save analysis results as an XLSX file.
Before writing, it is recommended to run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/demographic_analysis.xlsx`
to ensure the output directory has write permissions and no residual dirty files.
```

### 5.4 Auxiliary Scripts

Auxiliary scripts are scripts capable of solving tail variant problems, and need to be generated specifically based on the task, data, and tail variant.

### 5.4.0 XLSX Custom Injector (Preserving Sheet Structure)

**Core Issue**: `_tail_inject.py`'s `_write_tabular` uses `Workbook()` for XLSX, creating a new workbook, which **loses all original sheet names** (e.g., "Data" becomes the default "Sheet").

**Solution**: Create a custom injection script for each XLSX task, using `load_workbook` to preserve the workbook structure:

1. **Custom injection script**: Uses `load_workbook` to preserve workbook structure, `COPY` + `RUN` in Dockerfile:
```python
# _nan_inject.py example
from openpyxl import load_workbook
wb = load_workbook('/root/data/openipf.xlsx')
ws = wb.active  # Preserve sheet structure
# ... Injection logic ...
wb.save('/root/data/openipf.xlsx')
```

2. **Dockerfile**: COPY injection script + RUN execute:
```dockerfile
COPY _nan_inject.py /tmp/_nan_inject.py
RUN python3 /tmp/_nan_inject.py
```

**Applicable variants**: C1_nan_poison, C3_duplicate_keys, C4_extremes, C5_type_confusion (all data modification variants), A3_zero_width (zero-width character injection also destroys XLSX sheet structure via `_write_tabular`)

**A3_zero_width does not require custom injection**: A3's clean_data.py only needs to strip zero-width characters then convert back to numeric (`float(cleaned)`), since original numeric values can be precisely recovered after stripping.

**iter_rows index note**: `iter_rows(values_only=False)` returns rows as **0-indexed** lists. `row[col_idx]` accesses the col_idx-th column (0-indexed). Do **not** use `row[col_idx + 1]`.

### 5.4.1 XLSX + A1_bom Special Handling

When the A1_bom variant is applied to XLSX files, `_tail_inject.py` does not modify the XLSX directly, but generates a **CSV sidecar file** in the same directory (e.g., `income.xlsx` → `income.csv`) with a BOM header.

**Key**: `test_tail.py`'s `test_no_bom_in_output` scans all `.csv/.txt/.json` files under `/root/` to check for BOM, including this sidecar CSV. Therefore, the Oracle must:
1. Call `clean_data.py /root` to scan all CSV/TXT/JSON files in the directory and strip BOM (or `clean_data.py /root/gdp.csv` to process a specific file)
2. Then read the XLSX file normally for subsequent processing

Even though the Oracle reads XLSX directly (unaffected by BOM), it must clean the sidecar CSV, otherwise the test will fail.

### 5.4.2 B3_dirty_output + input==output Special Handling

When the task's output file is the same as the input file (e.g., weighted-gdp-calc's `/root/gdp.xlsx`), B3's `echo "CORRUPTED" > output` also corrupts the input data.

**Solution**: Back up the original file before corruption in Dockerfile; prepare_output.py detects corruption and restores from backup:
```dockerfile
COPY gdp.xlsx /root/gdp_backup.xlsx
RUN echo "CORRUPTED_NOT_VALID_XLSX" > /root/gdp.xlsx
```
```python
# prepare_output.py checks if XLSX file starts with PK bytes
with open(output, 'rb') as f:
    header = f.read(4)
if not header.startswith(b'PK'):
    shutil.copy2(backup, output)  # Restore from backup
```

**Detecting input==output**: In `task_variant_matrix.yaml`, if the `output_file` path is at the same location in the container as `data_files[0].path`, then input==output.

### 5.4.3 Tasks Using uv in test.sh Require Pre-installation

Some tasks' `test.sh` uses `curl | sh` to install `uv` from github.com, then runs pytest via `uvx`. In domestic network environments, github.com access is unstable, causing test failures.

**Solution**: Add `uv` to the pip install in Dockerfile, installing from Tsinghua PyPI mirror:
```dockerfile
RUN pip3 install --break-system-packages openpyxl==3.1.5 pytest uv
```

This way, even if `source $HOME/.local/bin/env` in test.sh fails, the `uvx` command is already installed in the system PATH via pip, and subsequent tests can run normally.

**Applicable tasks**: xlsx-recover-data and other tasks using `uvx` in test.sh.

### 5.4.5 C Variant Error Handling Patterns (Important)

**Core Principle**: C-type variants' clean_data.py must implement **genuine error handling**, i.e., recovery from incomplete/corrupted data, not recovery from backup files.

#### Correct Handling by Variant Type

**C1_nan_poison (NaN/Inf injection)**: Fill missing values with column median:
```python
# CSV mode
valid = [parse(r[col_idx]) for r in rows[1:] if parse(r[col_idx]) is not None]
median = sorted(valid)[len(valid)//2]
for r in rows[1:]:
    if parse(r[col_idx]) is None:
        r[col_idx] = str(median)

# XLSX mode (openpyxl)
for row in ws.iter_rows(min_row=2):
    cell = row[col_idx]
    if cell.value is None or (isinstance(cell.value, float) and (math.isnan(cell.value) or math.isinf(cell.value))):
        cell.value = median
```

**C3_duplicate_keys (Duplicate rows)**: Deduplicate by key column:
```python
seen = set()
rows_to_keep = [rows[0]]  # header
for row in rows[1:]:
    key = row[key_col_idx]
    if key not in seen:
        seen.add(key)
        rows_to_keep.append(row)
```

**C4_extremes (Extreme values 0/-1/-999)**: Detect outliers using MAD (Median Absolute Deviation), replace with median:
```python
valid = [parse(r[col_idx]) for r in rows[1:] if parse(r[col_idx]) is not None]
median = sorted(valid)[len(valid)//2]
mad = sorted(abs(v - median) for v in valid)[len(valid)//2]
threshold = max(5 * mad, 1.0)
for r in rows[1:]:
    v = parse(r[col_idx])
    if v is None or abs(v - median) > threshold:
        r[col_idx] = str(median)
```

**C5_type_confusion (Type confusion N/A/TBD/-)**: Convert with `pd.to_numeric(errors='coerce')` then fill with median:
```python
# Detect non-numeric cells, replace with median
for r in rows[1:]:
    v = try_parse(r[col_idx])
    if v is None:
        r[col_idx] = str(median)
```

#### When base test fails due to exact value checks

If median filling causes base test exact-value assertions to fail (e.g., `assert slope == 0.15`), **relax test tolerance** rather than reverting to backup recovery:
```python
# Original:
assert result == expected_value
# Changed to:
assert abs(result - expected_value) < expected_value * 0.05  # Allow 5% variation
```

### 5.4.6 Merging Multiple Original Skills

When the original task has multiple skill directories (e.g., `pdf/` + `xlsx/`), generating S1 requires merging all original SKILL.md content into a single unified `s1/SKILL.md`, with tail handling content naturally interspersed. Delete all original skill directories (`pdf/`, `xlsx/`, etc.) and replace with `s1/`.

### 5.5 Oracle Patch Detailed Guide

For specific patch patterns by variant type (which script to call, where to place it in solve.sh, how to pass parameters), see:

> **`agent/guides/oracle_patch_guide.md`**

### 5.6 S1 Skill Fusion Detailed Guide

For fusion examples, tone requirements, and verification checklist, see:

> **`agent/guides/s1_fusion_guide.md`**

### 5.7 Skill Deployment

```bash
# In the variant task directory:
cd tailskills/generated-tasks/<task>--<variant>/environment/skills/

# Delete original skill directories
rm -rf pdf xlsx citation-management  # Select based on task type

# Create S1 directory
mkdir -p s1/scripts

# Write SKILL.md and scripts
# (Agent writes the template content above)

# Ensure scripts are executable
chmod +x s1/scripts/*.py
```

---

## 6. Step 5: Verification

### Harbor CLI

```bash
# Harbor installation path (Windows)
HARBOR="E:/harbor/harbor.exe"

# Run Oracle test (results output directly to variant directory)
VARIANT_DIR="generated-tasks/<task>--<variant>"
PYTHONUTF8=1 E:/harbor/harbor.exe run -p "${VARIANT_DIR}" -a oracle -y -o "${VARIANT_DIR}/environment/skills/jobs"
```

### Container Network Mirror Sources

External network access inside Docker containers may be restricted. External resources referenced in solve.sh should use domestic mirrors:

| Service | Original Domain | Recommended Mirror |
|------|--------|---------|
| GitHub code | `github.com` | `githubfast.com`, `gitclone.com` |
| GitHub Raw | `raw.githubusercontent.com` | `ghproxy.com`, `gitmirror.com` |
| Hugging Face | `huggingface.co` | `hf-mirror.com`, Tsinghua TUNA |

**Usage:**
```bash
# GitHub: Just replace the domain
pip install git+https://githubfast.com/AI4EPS/GaMMA.git@<commit>

# HuggingFace: Set environment variable
export HF_ENDPOINT=https://hf-mirror.com
python3 << 'EOF'
# seisbench.from_pretrained() etc. will automatically use HF_ENDPOINT
EOF
```

**Rule: Modify external URLs in solve.sh to mirror sources. This is part of the Oracle and does not affect variant injection logic.**

### Pre-installing uv in Dockerfile (Resolving verifier network issues)

test.sh uses `curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh` to install uv, but the container may not be able to connect to GitHub.
Since **modifying test.sh is not allowed**, uv must be pre-installed in the Dockerfile:

```dockerfile
RUN pip install --no-cache-dir \
    seisbench==0.10.2 \
    uv==0.9.7
```

This way, if test.sh's curl fails, subsequent `uvx` commands still work (because uv was installed via pip). This rule applies to all test.sh files that use uv.

### pip Mirror Source (Inside Dockerfile)

`pip install` in Dockerfile may fail due to `files.pythonhosted.org` timeout; configure a mirror:

### Installing pytest in Dockerfile (Resolving tail test's `pytest: command not found`)

The tail test at the end of test.sh uses the bare `pytest` command (not `uv run pytest`), but pytest is only in the uv venv. System-level installation is required in Dockerfile:

```dockerfile
RUN pip3 install --break-system-packages openpyxl==3.1.5 pytest
```

### B1_readonly_output: prepare_output.py Must Not Delete Input Files

When the task's output path is the same as the input path (e.g., solve.sh's `mv output.xlsx input.xlsx`), prepare_output.py **can only fix permissions, not delete files**. Otherwise, it may accidentally delete the input data file, causing subsequent processing to crash.

```python
# ✅ Correct: Only fix permissions
for d in ["/root", "/root/data"]:
    os.chmod(d, 0o755)

# ❌ Wrong: Deleted the input file
if os.path.exists(output):
    os.remove(output)  # If output == input, data is lost!
```

```dockerfile
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
```

This line must be placed before all `RUN pip install` commands.

### pandas 2.x Compatibility

When the Python heredoc in solve.sh reads CSV and then does `groupby().agg()`, pandas 2.x's StringDtype columns may cause `TypeError`. Add:

```python
picks['timestamp'] = picks['timestamp'].astype('object')  # pandas 2.x compat
stations["elevation_m"] = pd.to_numeric(stations["elevation_m"], errors="coerce")
```

### Per-station Data Consistency Fix

For scenarios where the same station has multiple rows of data (e.g., seismic station with multiple channels), `groupby("id").agg()` returns a list when values differ within a group. clean_data.py must ensure target column values are fully consistent for the same station:

```python
# Recommended: per-station median consensus (applicable to all data boundary variants)
df[col_name] = df.groupby(key_col)[col_name].transform(
    lambda x: x.median() if pd.notna(x.median()) else global_median
)
```

### --force-build Usage

After modifying auxiliary scripts under `environment/skills/`, Docker cache won't update automatically. Use `--force-build` to force a rebuild:

```bash
PYTHONUTF8=1 E:/harbor/harbor.exe run -p "${VARIANT_DIR}" -a oracle -y --force-build -o "${VARIANT_DIR}/environment/skills/jobs"
```

### Dockerfile Inline Python Notes

**Do not** use multi-line `RUN python3 -c "..."` in Dockerfile, because keywords like `import` may be misinterpreted by the Docker parser as Dockerfile directives. Instead:

1. Write the Python script to a file, `COPY` it into the container, then execute
2. Or use semicolon-joined one-liners: `RUN python3 -c "import random; random.seed(42); ..."`

### zero_width Injection for Non-Tabular Data

For non-tabular format files like BibTeX, the standard `_tail_inject.py`'s `zero_width` function does not work (depends on `_read_tabular`). A custom injection script (e.g., `_zw_inject.py`) is needed, `COPY`'d and `RUN`'d in Dockerfile.

### Ubuntu Base Image Notes

When using `ubuntu:24.04` instead of `python:3.11-slim`:
- pip commands need `--break-system-packages`
- pip mirror setup uses `pip3 config set` instead of `pip config set`
- uv is also pre-installed via `pip3 install uv==0.9.7`

### Docker/Infrastructure Errors → Immediate Interruption

If you encounter the following errors, **do not auto-retry; notify the user immediately**:
- `Cannot connect to the Docker daemon`
- `permission denied while trying to connect to the Docker daemon socket`
- `no such file or directory` (harbor command does not exist)
- Docker build fails due to network timeout / disk full
- Any failure not caused by solve.sh/test_tail.py/s1 scripts code

**Errors that can be auto-fixed** (no interruption):
- solve.sh Python code exceptions → Fix script or solve.sh
- test_tail.py assertion failures → Adjust test or enhance script
- Data column index mismatch → Correct parameters
- Script import missing → Add dependencies

### Harbor Result Storage

Use the `--jobs-dir` / `-o` parameter to output results directly to the corresponding variant task's `environment/skills/jobs/` directory:

```bash
VARIANT_DIR="generated-tasks/<task>--<variant>"
PYTHONUTF8=1 E:/harbor/harbor.exe run -p "${VARIANT_DIR}" -a oracle -y -o "${VARIANT_DIR}/environment/skills/jobs"
```

Directory structure:
```
generated-tasks/
└── sales-pivot-analysis--A1_bom/
    └── environment/skills/jobs/   # Harbor results output directly here
        └── <timestamp>__<id>/
            ├── result.json
            └── <trial>/
                ├── agent/oracle.txt
                ├── agent/exit-code.txt
                └── verifier/test-stdout.txt
```

### Check Results

```bash
# View latest job result
VARIANT_DIR="generated-tasks/<task>--<variant>"
cat "${VARIANT_DIR}/environment/skills/jobs/<latest_job>/reward.txt
# Expected output: 1

# If reward=0, view detailed logs
cat jobs/<latest_job>/verifier.log
cat jobs/<latest_job>/container.log
```

### Docker Local Debugging (Windows Environment, Alternative to Harbor CLI)

Harbor CLI is not available on Windows; use Docker directly for build testing:

```bash
# Build Docker image
cd tailskills/generated-tasks/<task>--<variant>/environment/
docker build -t <task>-<variant> .

# CRLF fix (Required on Windows! Otherwise bash reports \r command not found)
sed -i 's/\r$//' /path/to/solve.sh /path/to/test.sh

# Full test flow (volume mount approach, avoiding rebuild each time)
docker run --rm \
  -v "$(pwd)/../solution:/solution" \
  -v "$(pwd)/../tests:/tests" \
  <task>-<variant> \
  bash -c "sed -i 's/\r$//' /solution/solve.sh /tests/test.sh && bash /solution/solve.sh > /dev/null 2>&1 && python3 -m pytest /tests/test_outputs.py -v --tb=short"

# Step-by-step debugging
docker run --rm <task>-<variant> bash /solution/solve.sh    # Run Oracle only
docker run --rm <task>-<variant> bash /tests/test.sh          # Run tests only
docker run --rm -it <task>-<variant> bash                     # Interactive debugging
```

**CRLF Issue**: Files checked out via git on Windows have `\r\n` line endings, which Linux container bash cannot recognize. **All .sh files mounted from Windows into the container must be pre-processed with `sed -i 's/\r$//'`**.

### Network-Dependent Task Handling

For tasks requiring external data downloads (IMF, HuggingFace, GitHub, etc.), **do not skip them**; instead, replace with domestic mirror sources:

| Service | Original Domain | Recommended Mirror |
|------|--------|---------|
| GitHub code | `github.com` | `githubfast.com`, `gitclone.com` |
| GitHub Raw | `raw.githubusercontent.com` | `ghproxy.com`, `gitmirror.com` |
| Hugging Face | `huggingface.co` | `hf-mirror.com`, Tsinghua TUNA |
| IMF data | `imf.org` | Pre-download data directly in Dockerfile COPY |

**For tasks where IMF data may change over time**: Test expected values not matching real-time data is an issue with the original task, not the variant. Consider pre-downloading and pinning data in Dockerfile to avoid network dependencies and value drift.

### FROM-based Docker Build (Heavy Dependency Tasks)

When tasks depend on Prophet, sentence-transformers, torch, and other heavy packages (3-10 minutes to install), **do not rebuild from base image**. Use a completed variant's image as the FROM base:

```dockerfile
# ❌ Slow: Rebuild from python:3.11-slim, Prophet install takes 5+ minutes
FROM python:3.11-slim
RUN pip install prophet pandas numpy...

# ✅ Fast: Reuse existing image, only append variant layers (<30 seconds)
FROM trend-anomaly-b1
COPY skills/s1/scripts/clean_data.py /app/.claude/skills/s1/scripts/clean_data.py
COPY _tail_inject.py /tmp/_tail_inject.py
RUN python3 /tmp/_tail_inject.py nan_inf /app/data/file.csv 2
```

**FROM image naming convention**: `<task>-<variant>` e.g., `trend-anomaly-b1`, `trend-anomaly-a1bom`.
**Note**: The FROM image must have been `docker build`'d and exist locally. Check with `docker images`.

### HF_ENDPOINT Must Be Set Before Model Download

HuggingFace model downloads (e.g., `sentence_transformers.SentenceTransformer`) depend on the `HF_ENDPOINT` environment variable. **It must be set before the download command**:

```dockerfile
# ✅ Correct: ENV before RUN
ENV HF_ENDPOINT=https://hf-mirror.com
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ❌ Wrong: ENV after RUN, still accesses huggingface.co during download
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
ENV HF_ENDPOINT=https://hf-mirror.com
```

### Merging Multiple Original Skill Directories and sys.path Fix

When the original task has 4+ skill directories (e.g., `data_cleaning/`, `anomaly_detection/`, `feature_engineering/`, `did_causal_analysis/`), merging into `s1/` requires:

1. Copy all skills' scripts/*.py to `s1/scripts/`
2. In solve.sh's sys.path, **add `s1/scripts` first**:

```python
for base_path in skill_base_paths:
    if os.path.exists(base_path):
        sys.path.append(os.path.join(base_path, 's1/scripts'))        # ← Must add first
        sys.path.append(os.path.join(base_path, 'data_cleaning/scripts'))
        sys.path.append(os.path.join(base_path, 'anomaly_detection/scripts'))
        sys.path.append(os.path.join(base_path, 'feature_engineering/scripts'))
        sys.path.append(os.path.join(base_path, 'did_causal_analysis/scripts'))
        break
```

Not adding `s1/scripts` causes `ModuleNotFoundError: No module named 'data_cleaning'`, because after merging, scripts are under `s1/scripts/` instead of the original paths.

### Custom Injection Script (A3_zero_width for Non-Numeric CSV)

When A3_zero_width is applied to **text-type CSV** (no numeric columns, `col_idx` not specified), the standard `_tail_inject.py`'s `zero_width` function requires `col_idx`. Solution:

1. Create a custom `_zw_inject.py` that injects into random text cells:
```python
def inject_zero_width_csv(filepath, ratio=0.03):
    """Inject ZW chars into random cells of CSV."""
    with open(filepath, 'r', encoding='utf-8') as f:
        rows = [list(row) for row in csv.reader(f)]
    zw_chars = ['​', '‌', '‍', '﻿']
    for row in rows[1:]:
        for i in range(len(row)):
            if random.random() < ratio:
                pos = random.randint(0, len(row[i]))
                row[i] = row[i][:pos] + random.choice(zw_chars) + row[i][pos:]
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f).writerows(rows)
```

2. In Dockerfile: `COPY _zw_inject.py /tmp/ && RUN python3 /tmp/_zw_inject.py <file>`

### Windows Docker Volume Mount Paths

Docker volume mounts on Windows require **full absolute paths** (not `$(pwd)`), otherwise `cp` reports `No such file`:

```bash
# ❌ Fails: $(pwd) does not resolve correctly in some cases
docker run --rm -v "$(pwd)/solution:/solution" ...

# ✅ Succeeds: Use full Windows path
docker run --rm -v "E:/desktop/科研/Skill/tailskills/generated-tasks/<task>--<variant>/solution:/solution:ro" \
  -v "E:/desktop/科研/Skill/tailskills/generated-tasks/<task>--<variant>/tests:/tests:ro" \
  <image> bash -c "..."
```

---

## 6.5 Variant Directory Required Files (Harbor Compatibility)

### instruction.md (Required)

Harbor's `TaskPaths.is_valid()` requires `instruction.md` to exist at the root of the variant directory:
```python
# harbor/models/task/paths.py
def is_valid(self):
    return (
        self.config_path.exists()           # task.toml
        and self.environment_dir.exists()    # environment/
        and self.instruction_path.exists()   # instruction.md ← Must exist!
        and self.test_path.exists()          # tests/test.sh
    )
```

**Missing instruction.md causes harbor error**: `ValueError: Either datasets or tasks must be provided.`

```bash
# Copy instruction.md from base task
cp skillsbench/tasks/<task>/instruction.md generated-tasks/<task>--<variant>/instruction.md
```

### task.toml Required Fields

task.toml must contain the following fields, otherwise harbor cannot recognize the task:

```toml
version = "1.0"

[metadata]
# ... metadata fields ...

[verifier]
timeout_sec = 900.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 600.0
cpus = 2
memory_mb = 4096
storage_mb = 10240
gpus = 0              # ← Required!
allow_internet = true  # ← Required!

[verifier.env]         # ← Required, can be empty

[solution.env]         # ← Required, can be empty
```

**Missing any of `gpus`, `allow_internet`, `[verifier.env]`, `[solution.env]` will cause harbor to error.**

### Oracle Pre-computed Data (Network-Unreachable Tasks)

For tasks that depend on external APIs (e.g., `gh-repo-analytics` requires GitHub API, `pg-essay-to-audiobook` requires OpenAI TTS), external services may not be accessible in the Docker sandbox environment.

**Solution**: Oracle's solve.sh writes pre-computed correct results directly, skipping network requests:
```bash
#!/bin/bash
set -e
python3 /root/.claude/skills/s1/scripts/prepare_output.py /app/report.json

# Write pre-computed data directly (no external API dependency)
python3 << 'EOF'
import json
from pathlib import Path
report = {"pr": {"total": 30, "merged": 22, ...}, "issue": {...}}
Path("/app/report.json").write_text(json.dumps(report, indent=2))
EOF
```

**Applicable scenarios**: gh-repo-analytics (no GH_TOKEN), pg-essay-to-audiobook (no OPENAI_API_KEY), and other tasks requiring external credentials.

---

## 7. Step 6: Common Failure Modes and Fixes

### 7.1 Docker Build Failure

**Symptom**: `docker build` reports an error

**Common causes**:
- `_tail_inject.py` cannot find target file → Check COPY paths
- `pip install` version conflict → Pin version numbers
- Insufficient disk space → Clean up old images

**Fix**: Check COPY and RUN command order in Dockerfile

### 7.2 Oracle solve.sh Failure

**Symptom**: `harbor run -a oracle` returns reward=0

**Common causes**:
- Defensive code in wrong position → Placed after processing logic instead of before
- Defensive code breaks original logic → Narrow the defensive scope
- Column index/name errors → Confirm from actual code in solve.sh
- Missing import statements → Add at the top of Python script

**Fix strategy**:
1. Read `verifier.log` and `container.log`
2. Find the specific error line
3. Modify defensive code in solve.sh
4. Re-run `harbor run`

### 7.3 test_tail.py Failure

**Symptom**: Base test passes but tail test fails

**Common causes**:
- test_tail.py check conditions too strict → Relax checks (e.g., allow small errors)
- Defensive code incomplete → Enhance Oracle's defenses
- test_tail.py references non-existent file paths → Fix paths

**Fix**: Adjust test_tail.py or enhance Oracle

### 7.4 S1 Skill Issues

**Symptom**: Agent does not use S1 scripts (this is not an Oracle-phase issue)

**Explanation**: S1 skill quality is verified during the Agent run phase. The Oracle phase only verifies solve.sh.

### 7.5 EADDRINUSE / Port Conflicts

**Symptom**: verifier's test.sh `npm start` or `next start` reports `EADDRINUSE: address already in use :::3000`

**Common causes**:
- Oracle solve.sh did not thoroughly clean up residual processes after building/starting server for baseline measurement
- `kill $SERVER_PID` only killed the npm wrapper; the child process node is still running
- Docker container's solve.sh and test.sh share the same process space

**Fix**:
```bash
# Add multi-level cleanup at end of solve.sh
kill $SERVER_PID 2>/dev/null || true
kill_server  # Custom function (pkill -f "next start", etc.)
# Extra cleanup: Kill processes by port
for pid in $(ss -tlnp 2>/dev/null | grep ':3000' | grep -oP 'pid=\K[0-9]+' || true); do
  kill -9 "$pid" 2>/dev/null || true
done
pkill -f "next-server" 2>/dev/null || true
sleep 2
```

### 7.6 apt-get Mirror Configuration Failure

**Symptom**: During Docker build, `apt-get install` cannot find basic packages (e.g., `bc`, `lsof`), indicating apt source configuration failure

**Common causes**:
- Ubuntu 24.04 uses DEB822 format `ubuntu.sources`; sed replacement may not take effect
- Using `https://` mirrors may be blocked or have certificate issues; should use `http://`
- `2>/dev/null || true` hides errors, causing silent failures

**Fix**:
```dockerfile
# Correct Ubuntu 24.04 mirror configuration pattern (use http instead of https)
RUN sed -i 's|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null; \
    sed -i 's|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null; true
```

### 7.7 PEP 668 / pip --break-system-packages Ineffective

**Symptom**: In Ubuntu 24.04 Dockerfile, `pip3 install --break-system-packages` still reports PEP 668 error

**Common causes**:
- Ubuntu 24.04's python3-pip package supports `--break-system-packages`, but in some environments the flag is ignored
- Docker layer cache may prevent modifications from taking effect

**Fix**:
```dockerfile
# Delete the EXTERNALLY-MANAGED marker file before pip install
RUN rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED && \
    pip3 install <package>
```

### 7.8 git-lfs Download Failure (HuggingFace DB Files)

**Symptom**: During Docker build, `git lfs pull` fails or downloaded LFS files are only a few KB (not the actual large files)

**Common causes**:
- git-lfs is unstable in harbor sandbox network environments
- HF mirror's LFS pointer files cannot be properly resolved

**Fix**: Use wget to download raw files directly, completely bypassing git-lfs:
```dockerfile
# Old approach (unstable):
# RUN git clone https://hf-mirror.com/datasets/<repo> && cd <repo> && git lfs pull && ...

# New approach (stable):
RUN mkdir -p /root/.cache/trivy && \
    wget -q "https://hf-mirror.com/datasets/<repo>/resolve/main/<file>" -O /tmp/<file> && \
    unzip /tmp/<file> -d /root/.cache/trivy && \
    rm /tmp/<file>
```

**Applicable tasks**: All tasks requiring large file downloads from HuggingFace (e.g., software-dependency-audit's trivy db)

### 7.9 D-type Variant (Network Failure) test.sh Pre-installed Dependencies

**Symptom**: In D1/D2 variants, test.sh times out when trying to install pytest/uvx due to DNS jitter or rate limiting

**Common causes**:
- D1 (dns_jitter) iptables rules randomly drop DNS packets, causing `pip install`/`uvx` timeout
- D2 (rate_limit) limits concurrent HTTPS connections, causing PyPI download failures

**Fix**: Pre-install all test dependencies in Dockerfile (before iptables rules take effect), simplify test.sh:
```dockerfile
# Dockerfile: Pre-install before variant injection
RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5
```
```bash
# test.sh: Simplified to directly run pre-installed pytest
#!/bin/bash
mkdir -p /logs/verifier
cd /root
pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA -v
if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
exit 0
```

**Applicable tasks**: All D-type variants (D1_dns_jitter, D2_rate_limit, D3_connection_delay)

### 7.10 D Variant Creation Notes

**instruction.md must be copied**: harbor requires the `instruction.md` file to exist, otherwise it reports "Either datasets or tasks must be provided". Copy from B1:
```bash
cp "${b1}/instruction.md" "${d_variant}/instruction.md"
```

**Bash heredoc breaks Dockerfile**: bash heredoc (`<< DOCKERFILE`) strips `\` line continuations, causing Dockerfile commands to merge into one line. Must use Write/Edit tools to directly write Dockerfile; using heredoc to generate is prohibited.

**Skill directories must be synced**: When B1's solve.sh references skill scripts (e.g., `pptx/ooxml/scripts/unpack.py`, `xlsx/recalc.py`), D variant must fully copy these directories:
```bash
cp -r "${b1}/environment/skills/pptx" "${d_variant}/environment/skills/"
cp -r "${b1}/environment/skills/xlsx" "${d_variant}/environment/skills/"
```

**Test dependencies need pre-installation**: B1's test.sh may use `uvx` to install test dependencies (e.g., `rapidfuzz`). D variant's test.sh does not use the network; these dependencies must be pre-installed in Dockerfile.

### 7.11 Batch D Variant Creation Process

Standard process for batch creating D1/D2 variants from existing B1:

1. **Copy B1 directory**: `cp -r task--B1_readonly_output task--D1_dns_jitter`
2. **Rewrite Dockerfile**: Remove B1's `chmod 555` lines, add iptables+iproute2 installation and network fault scripts
3. **Update solve.sh**: Remove `prepare_output.py` calls, replace with D variant comments
4. **Update task.toml**: Modify variant tags and category in tags
5. **Add matrix entry**: Add D1/D2 entries in task_variant_matrix.yaml
6. **Docker verification**: `harbor run -a oracle` to verify reward=1.0

**D Variant Dockerfile Template**:
```dockerfile
# Add iptables iproute2 in apt-get install
# Remove B1's chmod 555 lines, add network fault scripts:
# D1_dns_jitter:
RUN echo '#!/bin/bash' > /usr/local/bin/network_fault.sh && echo 'iptables -A OUTPUT -p udp --dport 53 -m statistic --mode random --probability 0.5 -j DROP 2>/dev/null || true' >> /usr/local/bin/network_fault.sh && chmod +x /usr/local/bin/network_fault.sh
# D2_rate_limit:
RUN echo '#!/bin/bash' > /usr/local/bin/network_fault.sh && echo 'iptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' >> /usr/local/bin/network_fault.sh && chmod +x /usr/local/bin/network_fault.sh
# Both share the same entrypoint wrapper:
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint_wrapper.sh && echo '/usr/local/bin/network_fault.sh' >> /usr/local/bin/entrypoint_wrapper.sh && echo 'exec "$@"' >> /usr/local/bin/entrypoint_wrapper.sh && chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
CMD ["/bin/bash"]
```

**Applicable conditions**: D variants are suitable for tasks with `allow_internet = true`. For purely local computation tasks (e.g., GLM calibration, BGP analysis), network faults do not affect reward.

**D1_dns_jitter requires pre-installed runtime dependencies**: If solve.sh needs to install large Python packages (e.g., seisbench), D1's 50% DNS packet loss causes pip install timeouts. Solution: Pre-install these packages in Dockerfile:
```dockerfile
RUN pip install --no-cache-dir seisbench==0.10.2 obspy pandas numpy
```
D2_rate_limit is not affected (limits HTTPS concurrent connections, does not affect DNS resolution).

### 7.12 Python 3.8 (ubuntu:20.04) Compatibility

**Symptom**: ubuntu:20.04 ships with Python 3.8; some newer packages lack cp38 wheels

**Incompatible packages**:
- `pytest==8.4.1` → Highest available is `8.3.5`
- `pytest-json-ctrf==0.3.5` → Lowest available is `0.4.1`

**Fix**: Use compatible versions in Dockerfile:
```dockerfile
RUN pip3 install pytest==8.3.5 pytest-json-ctrf==0.4.1
```

**Applicable tasks**: All tasks based on ubuntu:20.04 (e.g., glm-lake-mendota)

---

## 8. Complete Single-Task Execution Script

Complete workflow for a single (task, variant):

```bash
#!/bin/bash
set -e

TASK_ID="$1"
VARIANT_ID="$2"
OUTPUT_DIR="tailskills/generated-tasks"

echo "=== Generating ${TASK_ID}--${VARIANT_ID} ==="

# Step 1: Analysis already done in Agent context, parameters extracted
# Step 2: Injector generates variant directory
python3 -c "
from tailskills.inject.injector import Injector
injector = Injector('skillsbench', '${OUTPUT_DIR}')
injector.generate('${TASK_ID}', '${VARIANT_ID}', force=True)
"

# Step 3: Generate auxiliary scripts to skills/s1/scripts/ (Agent generates variant handling scripts based on variant type and specific variant)
# Step 4: Modify Oracle solve.sh — Call auxiliary scripts before data loading
# Step 5: Generate S1 skill — Original SKILL.md text + naturally interspersed tail handling content

# Step 6: Verification
PYTHONUTF8=1 E:/harbor/harbor.exe run -p "${OUTPUT_DIR}/${TASK_ID}--${VARIANT_ID}" -a oracle -y

# Check results
LATEST_JOB=$(ls -td jobs/*/ | head -1)
REWARD=$(cat "${LATEST_JOB}/reward.txt")

if [ "$REWARD" = "1" ]; then
    echo "✅ ${TASK_ID}--${VARIANT_ID} PASSED"
else
    echo "❌ ${TASK_ID}--${VARIANT_ID} FAILED (reward=${REWARD})"
    echo "Logs: ${LATEST_JOB}"
    exit 1
fi
```

---

## 9. Progress Tracking

### Variant Description

After completing each variant task and passing verification, you **must** fill in the "Variant Description" column in the `procedure.md` summary table.

The variant description should include:
- What data/environment mutation the variant injected (1 sentence)
- How the Oracle resolved it (1 sentence)
- What auxiliary script or suggestion the S1 skill provided

Example:
> BodyweightKg column injected with NaN/Inf values; Oracle calls clean_data.py to fill median then processes; S1 recommends running data quality check script after reading

---

## 10. File Path Reference

```
Skill/
├── skillsbench/tasks/<task-id>/        # Original SkillsBench task
│   ├── instruction.md
│   ├── environment/Dockerfile
│   ├── environment/skills/*/SKILL.md
│   └── solution/solve.sh
├── tailskills/
│   ├── configs/
│   │   ├── task_variant_matrix.yaml    # Task-variant parameter matrix
│   │   └── variants/<variant>.yaml     # 24 variant configurations
│   ├── src/tailskills/inject/
│   │   ├── injector.py                 # Variant directory generator
│   │   ├── dockerfile_patcher.py       # Dockerfile patcher
│   │   ├── test_augmentor.py           # Test generator
│   │   └── _tail_inject.py             # In-container data mutation
│   ├── generated-tasks/                # Generated variant tasks
│   │   └── <task>--<variant>/
│   │       ├── environment/skills/s1/  # S1 skill (with auxiliary scripts)
│   │       ├── solution/solve.sh       # Oracle (calls auxiliary scripts)
│   │       └── tests/test_tail.py      # Variant verification test
│   ├── scripts/
│   │   ├── distill_s1_to_s2.py         # S1→S2 distillation
│   │   ├── run_s2_experiments.sh       # S2 experiments
│   │   └── organize_results.py         # Results organization
│   └── AGENT.md                        # This document
├── generate_tail_tasks_plan.md         # Expansion plan
└── README.md
```
