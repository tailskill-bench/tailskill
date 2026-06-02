# Regular Distillation Prompt

Source: `scripts/distill_recursive_openai.py`

## User Prompt

```
You are a ruthless technical editor. Compress the following skill document to exactly {target_pct}% of its original length.

Original: {char_count} chars. You MUST produce output between {min_count} and {max_count} chars.

Instructions:
- Prioritize information that directly affects the correctness and success of the skill execution.
- Remove some redundant, repetitive, or non-essential information.
- Shorten code blocks: keep only the essential lines.
- Output ONLY the rewritten Markdown. No commentary.

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

## Parameters

| Parameter | Description | Value |
|-----------|-------------|-------|
| `target_pct` | Target compression ratio | 70 (S2), 49 (S3), 34 (S4) |
| `char_count` | Original skill length in characters | Auto-calculated |
| `min_count` | Minimum acceptable output length | target_pct - 15% |
| `max_count` | Maximum acceptable output length | target_pct + 15% |
| `length_retries` | Retry count for length violations | 3 |
