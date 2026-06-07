"""Inject zero-width Unicode characters into JSON data files in /root/DATA/."""
import random
import os
from pathlib import Path

random.seed(42)
ZW_CHARS = ['\u200b', '\u200c', '\u200d']
DATA_ROOT = Path('/root/DATA')

json_files = list(DATA_ROOT.rglob('*.json'))
print(f'[TailSkills] A3_zero_width: Found {len(json_files)} JSON files in {DATA_ROOT}')

total_modified = 0
for jf in json_files:
    with open(jf, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    targets = [i for i, line in enumerate(lines) if ':' in line and len(line.strip()) > 10]
    n_inject = max(1, len(targets) // 20)
    chosen = random.sample(targets, min(n_inject, len(targets)))
    for i in chosen:
        mid = len(lines[i]) // 2
        lines[i] = lines[i][:mid] + random.choice(ZW_CHARS) + lines[i][mid:]
        total_modified += 1
    with open(jf, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

print(f'[TailSkills] A3_zero_width: {total_modified} lines modified across {len(json_files)} files')
