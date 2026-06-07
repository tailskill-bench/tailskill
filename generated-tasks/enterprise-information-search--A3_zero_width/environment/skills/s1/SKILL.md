---
name: s1
description: "Enterprise information search with zero-width character handling."
---

Data files may contain invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that can interfere with text matching and JSON parsing. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/DATA` to strip these characters before processing.

You need to find information across multiple enterprise data sources (products, metadata, Slack messages, meeting transcripts) and answer questions based on the data in `/root/DATA/`.

Read the question from `/root/question.txt` and write answers to `/root/answer.json`.
