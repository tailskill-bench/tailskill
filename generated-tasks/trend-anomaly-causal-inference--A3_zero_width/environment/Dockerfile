FROM trend-anomaly-a1bom

# ============================================
# TailSkills Variant: A3_zero_width
# Inject zero-width Unicode characters into CSV text fields.
# ============================================
COPY skills/s1/scripts/clean_data.py /app/.claude/skills/s1/scripts/clean_data.py
COPY _zw_inject.py /tmp/_zw_inject.py
RUN python3 /tmp/_zw_inject.py /app/data/amazon-purchases-2019-2020_dirty.csv
