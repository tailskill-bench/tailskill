FROM trend-anomaly-a1bom

# ============================================
# TailSkills Variant: C4_extremes
# Inject extreme values (0, -1, -999) into numeric columns.
# ============================================
COPY skills/s1/scripts/clean_data.py /app/.claude/skills/s1/scripts/clean_data.py
COPY _tail_inject.py /tmp/_tail_inject.py
RUN python3 /tmp/_tail_inject.py extremes /app/data/amazon-purchases-2019-2020_dirty.csv 2
