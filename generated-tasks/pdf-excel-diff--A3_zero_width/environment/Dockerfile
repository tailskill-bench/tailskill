FROM pdf-excel-diff-b1

ENV http_proxy=http://host.docker.internal:7897
ENV https_proxy=http://host.docker.internal:7897

# ============================================
# TailSkills Variant: A3_zero_width
# Inject zero-width Unicode chars into XLSX string cells.
# ============================================
COPY skills/s1/scripts/clean_data.py /root/.claude/skills/s1/scripts/clean_data.py
COPY _zw_xlsx_inject.py /tmp/_zw_xlsx_inject.py
RUN python3 /tmp/_zw_xlsx_inject.py /root/employees_current.xlsx
