#!/usr/bin/env python3
"""Tail-Aware distillation for lake-warming-attribution--C4_extremes.

Produces S2_tail, S3_tail, S4_tail from S1 using a Tail-Aware prompt that
explicitly preserves exception-handling / data-quality knowledge.

Usage:
    set GLM_API_KEY=...
    python scripts/distill_tail_aware.py
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S1_PATH = ROOT / "skill-generations" / "tailskills-final2" / "lake-warming-attribution--C4_extremes" / "s1" / "SKILL.md"
OUT_DIR = ROOT / "results" / "tail-aware-study" / "tail_aware_skills"

ENDPOINT = "https://open.bigmodel.cn/api/anthropic/v1/messages"
MODEL = os.environ.get("GLM_DISTILL_MODEL", "glm-5.1")
API_KEY_ENV = "GLM_API_KEY"

# Compression targets per generation step
STEPS = [
    {"from": "s1", "to": "s2_tail", "target_pct": 70},
    {"from": "s2_tail", "to": "s3_tail", "target_pct": 70},
    {"from": "s3_tail", "to": "s4_tail", "target_pct": 80},
]

TAIL_AWARE_PROMPT = """You are a ruthless technical editor. Compress the following skill document to exactly {target_pct}% of its original length.

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

Compressed version:"""

SYSTEM_PROMPT = (
    "You are an expert software engineer tasked with optimizing and compressing agent skill documentation. "
    "Your goal is to make skills more concise and efficient while preserving core functionality. "
    "Output ONLY the rewritten skill content, no explanations."
)


def strip_code_fences(content: str) -> str:
    text = content.strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def call_api(skill_content: str, target_pct: int, api_key: str, length_retries: int = 3) -> str:
    char_count = len(skill_content)
    target_count = int(char_count * target_pct / 100)
    min_count = int(char_count * (target_pct - 15) / 100)
    max_count = int(char_count * (target_pct + 15) / 100)

    length_feedback = ""
    for length_attempt in range(length_retries + 1):
        prompt = TAIL_AWARE_PROMPT.format(
            target_pct=target_pct,
            char_count=char_count,
            min_count=min_count,
            max_count=max_count,
            skill_content=skill_content,
        )
        if length_feedback:
            prompt += length_feedback

        payload = json.dumps(
            {
                "model": MODEL,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 8192,
            },
            ensure_ascii=False,
        ).encode("utf-8")

        request = urllib.request.Request(
            ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        result = None
        for attempt in range(1, 5):
            try:
                with urllib.request.urlopen(request, timeout=300) as response:
                    data = json.loads(response.read().decode("utf-8"))
                text_parts = [p.get("text", "") for p in data.get("content", []) if p.get("type") == "text"]
                if not text_parts:
                    raise KeyError("No text content in response")
                result = strip_code_fences("\n".join(text_parts))
                break
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    wait = 30 * attempt
                    print(f"  [429 rate limit] attempt {attempt}, sleeping {wait}s...")
                    time.sleep(wait)
                else:
                    body = exc.read().decode("utf-8", errors="replace")
                    raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt >= 3:
                    raise RuntimeError(f"Failed after {attempt} attempts: {exc}") from exc
                print(f"  [network error] {exc}, retrying in 10s...")
                time.sleep(10)

        if result is None:
            raise RuntimeError("All retry attempts exhausted")

        result_len = len(result)
        in_range = min_count <= result_len <= max_count
        if in_range:
            print(f"  Length OK: {result_len} chars (target {min_count}-{max_count})")
            return result

        direction = "too long" if result_len > max_count else "too short"
        print(f"  [length retry {length_attempt+1}/{length_retries}] {result_len} chars is {direction} (need {min_count}-{max_count})")
        length_feedback = (
            f"\n\nFEEDBACK: Your previous output was {result_len} characters, which is {direction}. "
            f"The target is {target_pct}% of {char_count} = {target_count} characters. "
            f"You MUST produce output between {min_count} and {max_count} characters. "
        )
        if result_len > max_count:
            length_feedback += "Remove more redundant explanations, examples, and boilerplate to shorten the output."
        else:
            length_feedback += "Preserve more technical details, code examples, and operational steps to lengthen the output."

    print(f"  [length warning] final output {result_len} chars outside range {min_count}-{max_count}, accepting best effort")
    return result


def main():
    api_key = os.environ.get(API_KEY_ENV, "")
    if not api_key:
        raise SystemExit(f"Missing {API_KEY_ENV} environment variable")

    if not S1_PATH.exists():
        raise SystemExit(f"S1 skill not found: {S1_PATH}")

    s1_content = S1_PATH.read_text(encoding="utf-8")
    print(f"S1 skill: {len(s1_content)} chars from {S1_PATH}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save S1 copy for reference
    (OUT_DIR / "S1_SKILL.md").write_text(s1_content, encoding="utf-8")

    current = s1_content
    stats = [{"generation": "S1", "chars": len(current), "ratio": "1.00"}]

    for step in STEPS:
        from_name = step["from"]
        to_name = step["to"]
        target_pct = step["target_pct"]

        print(f"\n=== Distilling {from_name} -> {to_name} (target {target_pct}%) ===")
        print(f"  Input: {len(current)} chars")

        result = call_api(current, target_pct, api_key)
        ratio = len(result) / max(1, len(current))
        overall_ratio = len(result) / max(1, len(s1_content))

        print(f"  Output: {len(result)} chars ({ratio:.1%} of input, {overall_ratio:.1%} of S1)")

        # Save output
        out_path = OUT_DIR / f"{to_name}_SKILL.md"
        out_path.write_text(result, encoding="utf-8")
        print(f"  Saved to {out_path}")

        # Quick check: does it mention data quality / cleaning?
        lower = result.lower()
        has_bom = "bom" in lower or "utf-8-sig" in lower or "utf-8" in lower
        has_clean = "clean" in lower or "outlier" in lower or "anomal" in lower or "extreme" in lower
        print(f"  Tail-knowledge check: BOM/encoding={has_bom}, data-quality={has_clean}")

        stats.append({
            "generation": to_name,
            "chars": len(result),
            "ratio": f"{ratio:.2%}",
            "overall_vs_s1": f"{overall_ratio:.2%}",
            "has_bom_ref": has_bom,
            "has_data_quality": has_clean,
        })

        current = result
        time.sleep(2)

    # Save stats
    stats_path = OUT_DIR / "distillation_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nStats saved to {stats_path}")

    # Print summary table
    print("\n=== Distillation Summary ===")
    print(f"{'Gen':<12} {'Chars':>6} {'Step Ratio':>12} {'vs S1':>8}")
    print("-" * 42)
    for s in stats:
        step_r = s.get("ratio", "-")
        vs_s1 = s.get("overall_vs_s1", "-")
        print(f"{s['generation']:<12} {s['chars']:>6} {str(step_r):>12} {str(vs_s1):>8}")


if __name__ == "__main__":
    main()
