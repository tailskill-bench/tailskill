#!/bin/bash
set -e

# >>> TailSkills: D2_rate_limit — oracle writes pre-computed answer directly (no network calls) <<<
mkdir -p /root/output
cat > /root/output/flood_results.csv << 'CSV'
station_id,flood_days
04124000,5
04101800,5
04097500,4
04112500,3
04151500,3
04112850,3
04164500,3
04166500,2
04115000,2
04142000,2
04148140,1
04164000,1
04117500,1
CSV
echo "Done."
