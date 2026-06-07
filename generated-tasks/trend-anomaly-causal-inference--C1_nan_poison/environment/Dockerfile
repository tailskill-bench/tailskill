FROM trend-anomaly-a1bom

# ============================================
# TailSkills Variant: C1_nan_poison
# Inject NaN/Inf into numeric columns of CSV data.
# ============================================
COPY skills/s1/scripts/clean_data.py /app/.claude/skills/s1/scripts/clean_data.py
COPY _tail_inject.py /tmp/_tail_inject.py
RUN python3 /tmp/_tail_inject.py nan_inf /app/data/amazon-purchases-2019-2020_dirty.csv 2
