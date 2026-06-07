#!/bin/bash
set -e

# >>> TailSkills: D1_dns_jitter — oracle writes pre-computed answer directly (no network calls) <<<
cat > /root/answers.json << 'JSON'
{"q1_answer": 75753182516.0, "q2_answer": 2451, "q3_answer": ["037833100", "025816109", "166764100", "674599105", "H1467J104"], "q4_answer": ["VANGUARD GROUP INC", "BlackRock, Inc.", "STATE STREET CORP"]}
JSON
echo "Done."
