---
name: s1
description: "Enterprise search with zero-width char handling."
---

Strip zero-width Unicode (U+200B/C/D) from data: `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/DATA`

Search `/root/DATA/` (products, metadata, Slack, transcripts).
Read `/root/question.txt`, write `/root/answer.json`.