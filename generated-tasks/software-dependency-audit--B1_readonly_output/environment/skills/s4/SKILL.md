---
name: s1
description: Combined skills for software-dependency-audit with B1_readonly_output handling. Includes CVSS score extraction, Trivy offline scanning, and vulnerability CSV reporting.
---

# CVSS Score Extraction from Vulnerability Data

## CVSS Scoring System

| Score Range | Severity Level |
|-------------|----------------|
| 0.0 | None |
| 0.1–3.9 | Low |
| 4.0–6.9 | Medium |
| 7.0–8.9 | High |
| 9.0–10.0 | Critical |

Prefer CVSS v3/v3.1 over v2 when available.

## Source Priority Strategy

When multiple sources provide scores, use: `NVD → GHSA → RedHat → N/A`

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
    """Extract CVSS score with v2 fallback. Priority: NVD v3 > GHSA v3 > RedHat v3 > NVD v2 > N/A"""
    cvss = vuln_data.get('CVSS', {})
    for source in ['nvd', 'ghsa', 'redhat']:
        if source in cvss:
            v3_score = cvss[source].get('V3Score')
            if v3_score is not None:
                return {'score': v3_score, 'version': 'v3', 'source': source}
    if 'nvd' in cvss:
        v2_score = cvss['nvd'].get('V2Score')
        if v2_score is not None:
            return {'score': v2_score, 'version': 'v2', 'source': 'nvd'}
    return {'score': 'N/A', 'version': None, 'source': None}
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

---

# Trivy Offline Vulnerability Scanning

## Trivy Database Structure

- **trivy.db**: SQLite database containing CVE information
- **metadata.json**: Database version and update timestamp
- Database location: `<cache-dir>/db/trivy.db`

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
    result = subprocess.run(command, capture_output=True, text=True, check=False)
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

## JSON Output Structure

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
          "CVSS": { "nvd": { "V3Score": 9.8 } }
        }
      ]
    }
  ]
}
```

## Dependencies

- **Trivy**: Version 0.40.0 or later recommended
  ```bash
  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
  echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list
  apt-get update
  apt-get install trivy
  ```
- **Python Modules**: `subprocess`, `os`, `sys` (standard library)

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

Use `'N/A'` for missing data (not empty strings). Ensure consistent data types across all rows.

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

**Important**: `newline=''` prevents extra blank lines on Windows; `encoding='utf-8'` handles special characters.

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
            for vuln in result.get('Vulnerabilities', []):
                records.append({
                    "Package": vuln.get('PkgName'),
                    "Version": vuln.get('InstalledVersion'),
                    "CVE_ID": vuln.get('VulnerabilityID'),
                    "Severity": vuln.get('Severity', 'UNKNOWN'),
                    "CVSS_Score": extract_cvss_score(vuln),
                    "Fixed_Version": vuln.get('FixedVersion', 'N/A'),
                    "Title": vuln.get('Title', 'No description'),
                    "Url": vuln.get('PrimaryURL', '')
                })
    return records

def extract_cvss_score(vuln):
    """Extract CVSS score with source priority: NVD > GHSA > RedHat."""
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

def generate_vulnerability_csv_report(json_input, csv_output, severity_filter=['HIGH', 'CRITICAL']):
    """Generate filtered CSV security report from Trivy JSON output."""
    try:
        with open(json_input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[!] Error: Could not find {json_input}")
        sys.exit(1)

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

    if vulnerabilities:
        headers = ["Package", "Version", "CVE_ID", "Severity",
                   "CVSS_Score", "Fixed_Version", "Title", "Url"]
        with open(csv_output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(vulnerabilities)
        print(f"\n[SUCCESS] Found {len(vulnerabilities)} {'/'.join(severity_filter)} vulnerabilities")
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

if __name__ == "__main__":
    generate_vulnerability_csv_report(
        json_input='trivy_report.json',
        csv_output='security_audit.csv',
        severity_filter=['CRITICAL', 'HIGH']
    )
```

## Handling Read-Only Output Directories

When writing output files, the output directory may be read-only. Fix permissions **before** any write operation:

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
            vulnerabilities.append({
                "Target": target,
                "Package": vuln.get('PkgName'),
                "Version": vuln.get('InstalledVersion'),
                "CVE_ID": vuln.get('VulnerabilityID'),
                "Severity": vuln.get('Severity', 'UNKNOWN'),
                "CVSS_Score": get_cvss_score(vuln),
                "Fixed_Version": vuln.get('FixedVersion', 'N/A'),
                "Title": vuln.get('Title', 'No description'),
                "Url": vuln.get('PrimaryURL', '')
            })

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
```

## Dependencies

- **Python Modules**: `csv`, `json` (standard library)
- **Input Format**: Requires structured vulnerability data (typically JSON from scanners)