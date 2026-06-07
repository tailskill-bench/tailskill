FROM pdf-excel-diff-b1

ENV http_proxy=http://host.docker.internal:7897
ENV https_proxy=http://host.docker.internal:7897

# ============================================
# TailSkills Variant: C4_extremes
# Inject extreme values (0, -1, -999, 999999) into Score column (col_idx=8) of XLSX.
# ============================================
COPY skills/s1/scripts/clean_data.py /root/.claude/skills/s1/scripts/clean_data.py
COPY _extremes_xlsx_inject.py /tmp/_extremes_xlsx_inject.py
RUN python3 /tmp/_extremes_xlsx_inject.py /root/employees_current.xlsx 8
