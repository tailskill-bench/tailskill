#!/usr/bin/env python3
"""Compress S1 skills to S2 via LLM API (one round of distillation)."""

import json
import os
import shutil
import time
import urllib.request

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = os.environ.get("GLM_API_KEY", "")
MODEL = "glm-4.5"

GENERATED_TASKS = os.path.join(os.path.dirname(__file__), "..", "generated-tasks")

# 3 unique S1 skills — pick one representative variant per group
SKILL_GROUPS = {
    "sales": {
        "source_variant": "sales-pivot-analysis--C1_nan_poison",
        "target_variants": [
            "sales-pivot-analysis--S1_column_rename",
            "sales-pivot-analysis--S2_column_reorder",
            "sales-pivot-analysis--C1_nan_poison",
            "sales-pivot-analysis--C3_duplicate_keys",
            "sales-pivot-analysis--C4_extremes",
            "sales-pivot-analysis--C5_type_confusion",
            "sales-pivot-analysis--A1_bom",
            "sales-pivot-analysis--A3_zero_width",
            "sales-pivot-analysis--B1_readonly_output",
            "sales-pivot-analysis--B3_dirty_output",
        ],
    },
    "earthquake": {
        "source_variant": "earthquake-phase-association--C3_duplicate_keys",
        "target_variants": [
            "earthquake-phase-association--C3_duplicate_keys",
            "earthquake-phase-association--C4_extremes",
        ],
    },
    "citation": {
        "source_variant": "citation-check--A1_bom",
        "target_variants": [
            "citation-check--A1_bom",
            "citation-check--A3_zero_width",
        ],
    },
}

PROMPT_TEMPLATE = """You are a ruthless technical editor. Compress the following skill document to exactly 60% of its original length.

Original: {char_count} chars. You MUST produce output between {min_count} and {max_count} chars.

Instructions:
- Delete ALL redundant explanations. If code already shows something, do not explain it in text.
- Keep at most 1 example per concept. Delete all extra examples.
- Merge similar subsections into one.
- Remove boilerplate sections (When to Use, Best Practices, Troubleshooting, Common Pitfalls, Resources, Dependencies, Integration).
- Shorten code blocks: keep only the essential lines.
- Remove cross-references to other files and skills.
- Output ONLY the rewritten Markdown. No commentary.

Original Skill:

```
{skill_content}
```

Compressed version:"""


def call_llm(skill_content: str) -> str:
    """Call GLM-4.5 to compress the skill content."""
    char_count = len(skill_content)
    target_count = int(char_count * 0.6)
    min_count = int(char_count * 0.55)
    max_count = int(char_count * 0.65)
    prompt = PROMPT_TEMPLATE.replace("{skill_content}", skill_content)
    prompt = prompt.replace("{char_count}", str(char_count))
    prompt = prompt.replace("{target_count}", str(target_count))
    prompt = prompt.replace("{min_count}", str(min_count))
    prompt = prompt.replace("{max_count}", str(max_count))

    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer tasked with optimizing and compressing "
                    "agent skill documentation. Your goal is to make skills more concise and efficient "
                    "while preserving core functionality. Output ONLY the rewritten skill content, "
                    "no explanations."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 8192,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )

    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    content = result["choices"][0]["message"]["content"]
    # Strip markdown code fences if the model wrapped output
    if content.startswith("```markdown"):
        content = content[len("```markdown"):]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    usage = result.get("usage", {})
    print(f"  Tokens: {usage.get('prompt_tokens', '?')} in / {usage.get('completion_tokens', '?')} out")
    return content


def main():
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "skill-generations", "S2"), exist_ok=True)

    for group_name, group_info in SKILL_GROUPS.items():
        # Read S1 from source variant
        s1_skill_dir = os.path.join(GENERATED_TASKS, group_info["source_variant"], "environment", "skills", "s1")
        s1_md_path = os.path.join(s1_skill_dir, "SKILL.md")

        print(f"\n{'='*60}")
        print(f"Compressing: {group_name}")
        print(f"Source: {s1_md_path}")

        with open(s1_md_path, "r", encoding="utf-8") as f:
            s1_content = f.read()

        s1_lines = s1_content.count("\n")
        print(f"S1 size: {len(s1_content)} chars, {s1_lines} lines")

        # Call LLM to compress SKILL.md
        print("Calling LLM...")
        s2_content = call_llm(s1_content)

        s2_lines = s2_content.count("\n")
        ratio = len(s2_content) / len(s1_content) * 100
        print(f"S2 size: {len(s2_content)} chars, {s2_lines} lines ({ratio:.1f}% of S1)")

        # Save S2 to skill-generations staging area
        s2_staging = os.path.join(os.path.dirname(__file__), "..", "skill-generations", "S2", group_name)
        os.makedirs(s2_staging, exist_ok=True)
        with open(os.path.join(s2_staging, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(s2_content)
        print(f"Saved S2 to {s2_staging}/SKILL.md")

        # Deploy S2 to all target variants — create s2/ dir, copy scripts from s1/, write compressed SKILL.md
        for variant in group_info["target_variants"]:
            variant_skills = os.path.join(GENERATED_TASKS, variant, "environment", "skills")
            s1_dir = os.path.join(variant_skills, "s1")
            s2_dir = os.path.join(variant_skills, "s2")

            if not os.path.exists(s1_dir):
                print(f"  WARNING: {s1_dir} not found, skipping {variant}")
                continue

            # Create s2/ and copy entire s1/ structure (scripts etc.)
            if os.path.exists(s2_dir):
                shutil.rmtree(s2_dir)
            shutil.copytree(s1_dir, s2_dir)

            # Overwrite SKILL.md with compressed version
            with open(os.path.join(s2_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write(s2_content)

            print(f"  Deployed s2/ to {variant} (s1/ untouched)")

        time.sleep(2)  # Rate limit

    print("\nDone! S2 skills created alongside S1 in all variants.")


if __name__ == "__main__":
    main()
