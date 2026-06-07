---
name: s1
description: CVSS extraction, Trivy offline scanning, and vulnerability CSV reporting for dependency audits.
---

# CVSS Score Extraction

**Severity**: 0.0=None, 0.1–3.9=Low, 4.0–6.9=Medium, 7.0–8.9=High, 9.0–10.0=Critical. **Source priority**: NVD → GHSA → RedHat → N/A. Prefer CVSS v3/v3.1 over v2.

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

```python
def get_cvss_score(vuln_data):
    """Extract CVSS v3 score. Priority: NVD > GHSA > RedHat"""
    cvss = vuln_data.get('CVSS', {})
    for source in ['nvd', 'ghsa', 'redhat']:
        if source in cvss:
            score = cvss[source].get('V3Score')
            if score is not None:
                return score
    return 'N/A'
```

```python
def get_cvss_score_with_fallback(vuln_data):
    """Priority: NVD v3 > GHSA v3 > RedHat v3 > NVD v2 > N/A"""
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

```python
def safe_get_cvss_score(vuln_data):
    """Safely extract CVSS score with error handling."""
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

# Trivy Offline Vulnerability Scanning

**Database**: `trivy.db` (SQLite) at `<cache-dir>/db/trivy.db`, `metadata.json` for version/timestamp.

**Key flags**: `fs <target>`, `--format json`, `--output <file>`, `--scanners vuln`, `--skip-db-update` (critical: no DB update), `--offline-scan`, `--cache-dir <path>`.

```python
import os
import sys
import subprocess

def run_trivy_offline_scan(target_file, output_file, cache_dir='./trivy-cache'):
    """Execute Trivy vulnerability scan in offline mode."""
    db_path = os.path.join(cache_dir, "db", "trivy.db")
    if not os.path.exists(db_path):
        print(f"[!] Database not found at {db_path}")
        sys.exit(1)
    
    command = [
        "trivy", "fs", target_file,
        "--format", "json",
        "--output", output_file,
        "--scanners", "vuln",
        "--skip-db-update",
        "--offline-scan",
        "--cache-dir", cache_dir
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print("[!] Scan failed:")
            print(result.stderr)
            sys.exit(1)
        print("[*] Scan completed successfully")
        return output_file
    except FileNotFoundError:
        print("[!] Trivy not found: https://aquasecurity.github.io/trivy/")
        sys.exit(1)

if __name__ == "__main__":
    run_trivy_offline_scan(target_file='package-lock.json', output_file='trivy_report.json')
```

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

# Vulnerability CSV Report Generation

**CSV columns**: Package, Version, CVE_ID, Severity, CVSS_Score, Fixed_Version, Title, Url.

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

```python
def filter_high_severity(vulnerabilities, min_severity=['HIGH', 'CRITICAL']):
    """Filter vulnerabilities by severity level."""
    return [v for v in vulnerabilities if v.get('Severity') in min_severity]
```

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
    """Extract CVSS score with source priority."""
    cvss = vuln.get('CVSS', {})
    for source in ['nvd', 'ghsa', 'redhat']:
        if source in cvss:
            score = cvss[source].get('V3Score')
            if score is not None:
                return score
    return 'N/A'
```

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

if __name__ == "__main__":
    generate_vulnerability_csv_report(
        json_input='trivy_report.json',
        csv_output='security_audit.csv',
        severity_filter=['CRITICAL', 'HIGH']
    )
```

**Read-only output directory**: Fix permissions before writes:

```python
import os

def prepare_output(output_path):
    output_dir = output_path if os.path.isdir(output_path) else os.path.dirname(output_path)
    if output_dir:
        output_dir = output_dir.rstrip('/')
        if os.path.isdir(output_dir):
            os.chmod(output_dir, 0o755)

prepare_output('/root/security_audit.csv')
```

```python
def print_report_summary(vulnerabilities):
    """Print summary before writing CSV."""
    from collections import Counter
    severity_counts = Counter(v['Severity'] for v in vulnerabilities)
    print("\nVulnerability Summary:")
    print(f"  CRITICAL: {severity_counts.get('CRITICAL', 0)}")
    print(f"  HIGH:     {severity_counts.get('HIGH', 0)}")
    print(f"  Total:    {len(vulnerabilities)}")