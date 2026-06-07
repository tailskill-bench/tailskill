FROM pdf-excel-diff-b1

ENV http_proxy=http://host.docker.internal:7897
ENV https_proxy=http://host.docker.internal:7897

# ============================================
# TailSkills Variant: C5_type_confusion
# Inject text markers (N/A, -, TBD, null, none) into Score column (col_idx=8) of XLSX.
# ============================================
COPY skills/s1/scripts/clean_data.py /root/.claude/skills/s1/scripts/clean_data.py
COPY _typeconfusion_xlsx_inject.py /tmp/_typeconfusion_xlsx_inject.py
RUN python3 /tmp/_typeconfusion_xlsx_inject.py /root/employees_current.xlsx 8
