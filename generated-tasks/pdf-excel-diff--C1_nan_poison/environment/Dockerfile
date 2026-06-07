FROM pdf-excel-diff-b1

ENV http_proxy=http://host.docker.internal:7897
ENV https_proxy=http://host.docker.internal:7897

# ============================================
# TailSkills Variant: C1_nan_poison
# Inject NaN/Inf into Salary column (col_idx=5) of XLSX.
# ============================================
COPY skills/s1/scripts/clean_data.py /root/.claude/skills/s1/scripts/clean_data.py
COPY _nan_xlsx_inject.py /tmp/_nan_xlsx_inject.py
RUN python3 /tmp/_nan_xlsx_inject.py /root/employees_current.xlsx 8
