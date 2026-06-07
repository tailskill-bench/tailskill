---
name: s1
description: "Enterprise search with zero-width char handling."
---

Data files may contain invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that break text matching and JSON parsing. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/DATA` to strip them.

Search enterprise data sources (products, metadata, Slack messages, meeting transcripts) in `/root/DATA/`.

Read the question from `/root/question.txt` and write answers to `/root/answer.json`.