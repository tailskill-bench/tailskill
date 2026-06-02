# Tail-Aware Distillation Prompt

Source: `scripts/distill_tail_aware.py`

## User Prompt

```
You are a ruthless technical editor. Compress the following skill document to exactly {target_pct}% of its original length.

Original: {char_count} chars. You MUST produce output between {min_count} and {max_count} chars.

Instructions:
- Prioritize information that directly affects the correctness and success of the skill execution.
- Remove redundant, repetitive, or non-essential information aggressively.
- Shorten code blocks: keep ONLY the essential lines, remove variable assignments and comments.
- Remove introductory text, explanatory prose, and formatting that doesn't affect execution.
- Merge similar sections where possible.
- Output ONLY the rewritten Markdown. No commentary.

CRITICAL REQUIREMENT — TAIL KNOWLEDGE PRESERVATION:
You MUST explicitly preserve the following categories of knowledge, treating them as HIGH PRIORITY:
- Rare exception-handling rules and edge cases (e.g., handling corrupted data, extreme values like 0, -1, -999, encoding issues)
- Data quality checks and anomaly detection/prevention steps
- Recovery procedures for unusual or degraded environments
- Defensive coding practices and robustness notes
- Any instructions about detecting, filtering, or handling abnormal values (zeros, negatives, NaN, outliers)
- Scripts or utilities for data cleaning or preprocessing

Do NOT remove or weaken these sections even if they seem secondary to the main workflow. These tail-handling instructions are critical for robust execution.

Original Skill:

```
{skill_content}
```

Compressed version:
```

## System Prompt

```
You are an expert software engineer tasked with optimizing and compressing agent skill documentation. Your goal is to make skills more concise and efficient while preserving core functionality. Output ONLY the rewritten skill content, no explanations.
```

## Key Difference from Regular Distillation

The Tail-Aware prompt adds a **CRITICAL REQUIREMENT — TAIL KNOWLEDGE PRESERVATION** section that explicitly instructs the compressor to preserve:
1. Rare exception-handling rules and edge cases
2. Data quality checks and anomaly detection
3. Recovery procedures for degraded environments
4. Defensive coding practices
5. Abnormal value detection (zeros, negatives, NaN, outliers)
6. Data cleaning/preprocessing scripts

This ensures that tail-handling knowledge is preserved even as the skill is compressed to ~34% of its original length.
