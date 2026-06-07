FROM trend-anomaly-b1

# ============================================
# TailSkills Variant: A1_bom
# Inject UTF-8 BOM at the start of CSV input files.
# ============================================
COPY skills/s1/scripts/clean_data.py /app/.claude/skills/s1/scripts/clean_data.py
COPY _tail_inject.py /tmp/_tail_inject.py
RUN python3 /tmp/_tail_inject.py bom /app/data/amazon-purchases-2019-2020_dirty.csv
