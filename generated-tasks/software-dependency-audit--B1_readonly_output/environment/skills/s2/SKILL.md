---
name: s1
description: Combined skills for software-dependency-audit with B1_readonly_output handling. Includes CVSS score extraction, Trivy offline scanning, and vulnerability CSV reporting.
---

# CVSS Score Extraction from Vulnerability Data

## CVSS Scoring System

CVSS assigns a numerical score (0.0–10.0) representing vulnerability severity:

| Score Range | Severity Level |
|-------------|----------------|
| 0.0 | None |
| 0.1–3.9 | Low |
| 4.0–6.9 | Medium |
| 7.0–8.9 | High |
| 9.0–10.0 | Critical |

**CVSS Versions**: v2 (legacy), v3/v3.1 (current standard). Prefer v3/v3.1 when available.

## Source Priority Strategy

When multiple sources provide scores, use a priority cascade:

```
NVD → GHSA → RedHat → N/A
```

NVD is the most authoritative and comprehensive source.

## Data Structure

Trivy returns CVSS data in nested format:

```json
{
  "VulnerabilityID": "CVE-2021-44906",
  "PkgName": "minimist",
  "Severity": "CRITICAL",
  "CVSS": {
    "nvd": {
      "V2Vector": "AV:N/AC:L/Au:N/C:P/I:P/A:P",
      "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "V2Score": 7.5,
      "V3Score": 9.8
    },
    "ghsa": {
      "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "V3Score": 9.8
    }
  }
}
```

## Python Implementation

### Score Extraction with V2 Fallback

```python
def get_cvss_score_with_fallback(vuln_data):
    """
    Extract CVSS score with v2 fallback.
    Priority: NVD v3 > GHSA v3 > RedHat v3 > NVD v2 > N/A
    """
    cvss = vuln_data.get('CVSS', {})

    # Try v3 scores first
    for source in ['nvd', 'ghsa', 'redhat']:
        if source in cvss:
            v3_score = cvss[source].get('V3Score')
            if v3_score is not None:
                return {'score': v3_score, 'version': 'v3', 'source': source}

    # Fallback to v2 if v3 not available
    if 'nvd' in cvss:
        v2_score = cvss['nvd'].get('V2Score')
        if v2_score is not None:
            return {'score': v2_score, 'version': 'v2', 'source': 'nvd'}

    return {'score': 'N/A', 'version': None, 'source': None}
```

### Basic Score Extraction (Numeric or 'N/A')

```python
def get_cvss_score(vuln_data):
    """Extract CVSS v3 score with source priority: NVD > GHSA > RedHat."""
    cvss = vuln_data.get('CVSS', {})

    for source in ['nvd', 'ghsa', 'redhat']:
        if source in cvss:
            score = cvss[source].get('V3Score')
            if score is not None:
                return score

    return 'N/A'
```

### Safe Extraction with Error Handling

```python
def safe_get_cvss_score(vuln_data):
    """Safely extract CVSS score with comprehensive error handling."""
    try:
        cvss = vuln_data.get('CVSS', {})

        if not isinstance(cvss, dict):
            return 'N/A'

        for source in ['nvd', 'ghsa', 'redhat']:
            if source in cvss and isinstance(cvss[source], dict):
                score = cvss[source].get('V3Score')
                if score is not None and isinstance(score, (int, float)):
                    return score

        return 'N/A'
    except (AttributeError, TypeError):
        return 'N/A'
```

### Filtering by Score Threshold

```python
def is_high_severity(vuln_data, threshold=7.0):
    """Check if vulnerability meets severity threshold."""
    score = get_cvss_score(vuln_data)
    if score == 'N/A':
        return vuln_data.get('Severity') in ['HIGH', 'CRITICAL']
    return score >= threshold
```

## Usage in Report Generation

```python
import json

def parse_vulnerabilities(json_file):
    """Parse Trivy JSON and extract vulnerabilities with CVSS scores."""
    with open(json_file, 'r') as f:
        data = json.load(f)

    vulnerabilities = []

    if 'Results' in data:
        for result in data['Results']:
            for vuln in result.get('Vulnerabilities', []):
                record = {
                    'Package': vuln.get('PkgName'),
                    'Version': vuln.get('InstalledVersion'),
                    'CVE_ID': vuln.get('VulnerabilityID'),
                    'Severity': vuln.get('Severity'),
                    'CVSS_Score': get_cvss_score(vuln),
                    'Fixed_Version': vuln.get('FixedVersion', 'N/A'),
                    'Title': vuln.get('Title', 'No description')
                }
                vulnerabilities.append(record)

    return vulnerabilities
```

## Best Practices

1. **Always provide fallback**: Use `'N/A'` when scores unavailable
2. **Prefer newer versions**: V3 > V2
3. **Respect source hierarchy**: NVD is most authoritative
4. **Validate data types**: Ensure scores are numeric before using
5. **Document source**: In detailed reports, note which source provided the score

---

# Trivy Offline Vulnerability Scanning

## Trivy Database Structure

Trivy's vulnerability database consists of:
- **trivy.db**: SQLite database containing CVE information
- **metadata.json**: Database version and update timestamp

Database location: `<cache-dir>/db/trivy.db`

## Offline Scanning Workflow

### Step 1: Verify Database Existence

```python
import os
import sys

TRIVY_CACHE_PATH = './trivy-cache'

db_path = os.path.join(TRIVY_CACHE_PATH, "db", "trivy.db")
if not os.path.exists(db_path):
    print(f"[!] Error: Trivy database not found at {db_path}")
    print("    Download database first with:")
    print(f"    trivy image --download-db-only --cache-dir {TRIVY_CACHE_PATH}")
    sys.exit(1)
```

### Step 2: Construct Trivy Command

Key flags for offline scanning:

| Flag | Purpose |
|------|---------|
| `fs <target>` | Scan filesystem/file (e.g., package-lock.json) |
| `--format json` | Output in JSON format for parsing |
| `--output <file>` | Save results to file |
| `--scanners vuln` | Scan only for vulnerabilities (not misconfigs) |
| `--skip-db-update` | **Critical**: Do not update database |
| `--offline-scan` | Enable offline mode |
| `--cache-dir <path>` | Path to pre-downloaded database |

```python
import subprocess

TARGET_FILE = 'package-lock.json'
OUTPUT_FILE = 'trivy_report.json'
TRIVY_CACHE_PATH = './trivy-cache'

command = [
    "trivy", "fs", TARGET_FILE,
    "--format", "json",
    "--output", OUTPUT_FILE,
    "--scanners", "vuln",
    "--skip-db-update",
    "--offline-scan",
    "--cache-dir", TRIVY_CACHE_PATH
]
```

### Step 3: Execute Scan

```python
try:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print("[!] Trivy scan failed:")
        print(result.stderr)
        sys.exit(1)

    print("[*] Scan completed successfully")
    print(f"[*] Results saved to: {OUTPUT_FILE}")

except FileNotFoundError:
    print("[!] Error: 'trivy' command not found")
    print("    Install Trivy: https://aquasecurity.github.io/trivy/latest/getting-started/installation/")
    sys.exit(1)
```

## Complete Offline Scan Function

```python
import os
import sys
import subprocess

def run_trivy_offline_scan(target_file, output_file, cache_dir='./trivy-cache'):
    """
    Execute Trivy vulnerability scan in offline mode.

    Args:
        target_file: Path to file to scan (e.g., package-lock.json)
        output_file: Path to save JSON results
        cache_dir: Path to Trivy offline database
    """
    print(f"[*] Starting Trivy offline scan...")
    print(f"    Target: {target_file}")
    print(f"    Database: {cache_dir}")

    # Verify database exists
    db_path = os.path.join(cache_dir, "db", "trivy.db")
    if not os.path.exists(db_path):
        print(f"[!] Error: Database not found at {db_path}")
        sys.exit(1)

    # Build command
    command = [
        "trivy", "fs", target_file,
        "--format", "json",
        "--output", output_file,
        "--scanners", "vuln",
        "--skip-db-update",
        "--offline-scan",
        "--cache-dir", cache_dir
    ]

    # Execute
    try:
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print("[!] Scan failed:")
            print(result.stderr)
            sys.exit(1)

        print("[*] Scan completed successfully")
        return output_file

    except FileNotFoundError:
        print("[!] Trivy not found. Install from:")
        print("    https://aquasecurity.github.io/trivy/")
        sys.exit(1)

# Usage
if __name__ == "__main__":
    run_trivy_offline_scan(
        target_file='package-lock.json',
        output_file='trivy_report.json'
    )
```

## JSON Output Structure

Trivy outputs vulnerability data in this format:

```json
{
  "Results": [
    {
      "Target": "package-lock.json",
      "Vulnerabilities": [
        {
          "VulnerabilityID": "CVE-2021-44906",
          "PkgName": "minimist",
          "InstalledVersion": "1.2.5",
          "FixedVersion": "1.2.6",
          "Severity": "CRITICAL",
          "Title": "Prototype Pollution in minimist",
          "PrimaryURL": "https://avd.aquasec.com/nvd/cve-2021-44906",
          "CVSS": {
            "nvd": { "V3Score": 9.8 }
          }
        }
      ]
    }
  ]
}
```

## Dependencies

### Required Tools
- **Trivy**: Version 0.40.0 or later recommended
  ```bash
  # Installation (Debian/Ubuntu)
  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
  echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list
  apt-get update
  apt-get install trivy
  ```

### Python Modules
- `subprocess` (standard library)
- `os` (standard library)
- `sys` (standard library)

---

# Vulnerability CSV Report Generation

## CSV Schema for Security Reports

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **Package** | String | Vulnerable package name | `express` |
| **Version** | String | Installed version | `4.17.1` |
| **CVE_ID** | String | Vulnerability identifier | `CVE-2022-24999` |
| **Severity** | Enum | Risk level | `CRITICAL`, `HIGH` |
| **CVSS_Score** | Float/String | Numeric severity score | `9.8` or `N/A` |
| **Fixed_Version** | String | Patched version | `4.18.0` or `N/A` |
| **Title** | String | Brief description | `XSS in Express.js` |
| **Url** | String | Reference link | `https://nvd.nist.gov/...` |

Design principles: use descriptive column names, handle missing data with `'N/A'` (not empty strings), and ensure consistent data types across all rows.

## Python CSV Generation with DictWriter

```python
import csv

headers = ["Package", "Version", "CVE_ID", "Severity", "CVSS_Score",
           "Fixed_Version", "Title", "Url"]

vulnerabilities = [
    {
        "Package": "minimist",
        "Version": "1.2.5",
        "CVE_ID": "CVE-2021-44906",
        "Severity": "CRITICAL",
        "CVSS_Score": 9.8,
        "Fixed_Version": "1.2.6",
        "Title": "Prototype Pollution",
        "Url": "https://avd.aquasec.com/nvd/cve-2021-44906"
    }
]

with open('security_audit.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(vulnerabilities)
```

**Important parameters**: `newline=''` prevents extra blank lines on Windows; `encoding='utf-8'` handles special characters.

## Severity-Based Filtering

```python
def filter_high_severity(vulnerabilities, min_severity=['HIGH', 'CRITICAL']):
    """Filter vulnerabilities by severity level."""
    filtered = []
    for vuln in vulnerabilities:
        if vuln.get('Severity') in min_severity:
            filtered.append(vuln)
    return filtered

# Usage
all_vulns = [...]  # From scanner
critical_vulns = filter_high_severity(all_vulns, ['CRITICAL', 'HIGH'])
```

## Field Mapping from Trivy JSON to CSV

```python
import json

def parse_trivy_json_to_csv_records(json_file):
    """Parse Trivy JSON output and extract CSV-ready records."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = []

    if 'Results' in data:
        for result in data['Results']:
            target = result.get('Target', 'Unknown')

            for vuln in result.get('Vulnerabilities', []):
                record = {
                    "Package": vuln.get('PkgName'),
                    "Version": vuln.get('InstalledVersion'),
                    "CVE_ID": vuln.get('VulnerabilityID'),
                    "Severity": vuln.get('Severity', 'UNKNOWN'),
                    "CVSS_Score": extract_cvss_score(vuln),
                    "Fixed_Version": vuln.get('FixedVersion', 'N/A'),
                    "Title": vuln.get('Title', 'No description'),
                    "Url": vuln.get('PrimaryURL', '')
                }
                records.append(record)

    return records

def extract_cvss_score(vuln):
    """Extract CVSS score (from cvss-score-extraction skill)."""
    cvss = vuln.get('CVSS', {})
    for source in ['nvd', 'ghsa', 'redhat']:
        if source in cvss:
            score = cvss[source].get('V3Score')
            if score is not None:
                return score
    return 'N/A'
```

## Complete Vulnerability CSV Report Generator

```python
import json
import csv
import sys

def generate_vulnerability_csv_report(
    json_input,
    csv_output,
    severity_filter=['HIGH', 'CRITICAL']
):
    """
    Generate filtered CSV security report from Trivy JSON output.

    Args:
        json_input: Path to Trivy JSON report
        csv_output: Path for output CSV file
        severity_filter: List of severity levels to include
    """
    # Read JSON
    try:
        with open(json_input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[!] Error: Could not find {json_input}")
        sys.exit(1)

    # Extract and filter vulnerabilities
    vulnerabilities = []

    if 'Results' in data:
        for result in data['Results']:
            for vuln in result.get('Vulnerabilities', []):
                severity = vuln.get('Severity', 'UNKNOWN')

                if severity in severity_filter:
                    vulnerabilities.append({
                        "Package": vuln.get('PkgName'),
                        "Version": vuln.get('InstalledVersion'),
                        "CVE_ID": vuln.get('VulnerabilityID'),
                        "Severity": severity,
                        "CVSS_Score": get_cvss_score(vuln),
                        "Fixed_Version": vuln.get('FixedVersion', 'N/A'),
                        "Title": vuln.get('Title', 'No description'),
                        "Url": vuln.get('PrimaryURL', '')
                    })

    # Write CSV
    if vulnerabilities:
        headers = ["Package", "Version", "CVE_ID", "Severity",
                   "CVSS_Score", "Fixed_Version", "Title", "Url"]

        with open(csv_output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(vulnerabilities)

        print(f"\n[SUCCESS] Found {len(vulnerabilities)} "
              f"{'/'.join(severity_filter)} vulnerabilities")
        print(f"[SUCCESS] Report saved to: {csv_output}")
    else:
        print(f"\n[SUCCESS] No {'/'.join(severity_filter)} vulnerabilities found")

def get_cvss_score(vuln_data):
    """Extract CVSS score with source priority."""
    cvss = vuln_data.get('CVSS', {})
    for source in ['nvd', 'ghsa', 'redhat']:
        if source in cvss:
            score = cvss[source].get('V3Score')
            if score is not None:
                return score
    return 'N/A'

# Usage
if __name__ == "__main__":
    generate_vulnerability_csv_report(
        json_input='trivy_report.json',
        csv_output='security_audit.csv',
        severity_filter=['CRITICAL', 'HIGH']
    )
```

## Handling Read-Only Output Directories

When writing output files (e.g., saving a CSV report), the output directory may be read-only. Fix permissions **before** any write operation:

```python
import os

def prepare_output(output_path):
    output_dir = output_path if os.path.isdir(output_path) else os.path.dirname(output_path)
    if output_dir:
        output_dir = output_dir.rstrip('/')
        if os.path.isdir(output_dir):
            os.chmod(output_dir, 0o755)

# Call before any file write
prepare_output('/root/security_audit.csv')
```

This must be done **before** any `to_csv()`, `open(..., 'w')`, or similar write operations.

## Multi-Target Reports

To include the target/file name in each row:

```python
def generate_multi_target_report(json_input, csv_output):
    """Include target/file name in each row."""
    with open(json_input, 'r') as f:
        data = json.load(f)

    vulnerabilities = []

    for result in data.get('Results', []):
        target = result.get('Target', 'Unknown')

        for vuln in result.get('Vulnerabilities', []):
            record = {
                "Target": target,
                "Package": vuln.get('PkgName'),
                "Version": vuln.get('InstalledVersion'),
                "CVE_ID": vuln.get('VulnerabilityID'),
                "Severity": vuln.get('Severity', 'UNKNOWN'),
                "CVSS_Score": get_cvss_score(vuln),
                "Fixed_Version": vuln.get('FixedVersion', 'N/A'),
                "Title": vuln.get('Title', 'No description'),
                "Url": vuln.get('PrimaryURL', '')
            }
            vulnerabilities.append(record)

    headers = ["Target", "Package", "Version", "CVE_ID", "Severity",
               "CVSS_Score", "Fixed_Version", "Title", "Url"]

    with open(csv_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(vulnerabilities)
```

## Summary Statistics

```python
def print_report_summary(vulnerabilities):
    """Print summary before writing CSV."""
    from collections import Counter

    severity_counts = Counter(v['Severity'] for v in vulnerabilities)

    print("\nVulnerability Summary:")
    print(f"  CRITICAL: {severity_counts.get('CRITICAL', 0)}")
    print(f"  HIGH:     {severity_counts.get('HIGH', 0)}")
    print(f"  Total:    {len(vulnerabilities)}")
```

## Error Handling for Missing or Malformed Data

```python
def safe_get_field(vuln, field, default='N/A'):
    """Safely extract field with default fallback."""
    value = vuln.get(field, default)
    return value if value is not None else default

# Usage in field mapping
record = {
    "Package": safe_get_field(vuln, 'PkgName', 'Unknown'),
    "Fixed_Version": safe_get_field(vuln, 'FixedVersion', 'N/A'),
}
```

## Best Practices

1. **Always write headers**: Makes CSV self-documenting
2. **Use UTF-8 encoding**: Handles international characters
3. **Set newline=''**: Prevents blank lines on Windows
4. **Validate data**: Check for None/null values before writing
5. **Add timestamp**: Include scan date for tracking
6. **Document schema**: Maintain a data dictionary
7. **Test with edge cases**: Empty results, missing fields

## Dependencies

### Python Modules
- `csv` (standard library)
- `json` (standard library)

### Input Format
- Requires structured vulnerability data (typically JSON from scanners)