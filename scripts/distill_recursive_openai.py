#!/usr/bin/env python3
"""Recursively distill S1 skills to S2/S3 using an OpenAI-compatible API.

This script is intentionally independent of tailskills.cli's unfinished
DistillationPipeline. It groups selected generated tasks by base task, distills
one representative skill per base task, then deploys that generation to all
selected variants of the same base task.

Gemini OpenAI-compatible defaults:
    GEMINI_API_KEY=...
    GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
    GEMINI_DISTILL_MODEL=openai/gemini-2.5-pro
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GENERATED_TASKS = ROOT / "generated-tasks"
DEFAULT_VARIANTS_FILE = ROOT / "configs" / "all_200_variants.txt"
DEFAULT_OUT = ROOT / "skill-generations"

PROMPT_TEMPLATE = """You are a ruthless technical editor. Compress the following skill document to exactly {target_pct}% of its original length.

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

Compressed version:"""


def parse_variants(path: Path) -> list[str]:
    variants: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        variants.append(line)
    return variants


def base_task_name(variant_name: str) -> str:
    return variant_name


def endpoint_from_base_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1/messages"):
        return base
    return f"{base}/v1/messages"


def strip_code_fences(content: str) -> str:
    text = content.strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown") :].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def call_chat_completions(
    *,
    endpoint: str,
    api_key: str,
    model: str,
    skill_content: str,
    target_pct: int,
    timeout: int,
    rate_limit_retries: int = 10,
    rate_limit_sleep: float = 60.0,
    length_retries: int = 3,
) -> str:
    char_count = len(skill_content)
    target_count = int(char_count * target_pct / 100)
    min_count = int(char_count * (target_pct - 15) / 100)
    max_count = int(char_count * (target_pct + 15) / 100)

    length_feedback = ""
    for length_attempt in range(length_retries + 1):
        prompt = PROMPT_TEMPLATE.format(
            skill_content=skill_content,
            target_pct=target_pct,
            char_count=char_count,
            min_count=min_count,
            max_count=max_count,
        )
        if length_feedback:
            prompt += length_feedback

        payload = json.dumps(
            {
                "model": model.removeprefix("openai/").removeprefix("anthropic/"),
                "system": "You are an expert software engineer tasked with optimizing and compressing agent skill documentation. Your goal is to make skills more concise and efficient while preserving core functionality. Output ONLY the rewritten skill content, no explanations.",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 8192,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        last_error: Exception | None = None
        for attempt in range(1, rate_limit_retries + 2):
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                text_parts = [p.get("text", "") for p in data.get("content", []) if p.get("type") == "text"]
                if not text_parts:
                    raise KeyError("No text content in response")
                result = strip_code_fences("\n".join(text_parts))
                break
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code == 429:
                    if attempt > rate_limit_retries:
                        raise RuntimeError(f"Rate-limited after {rate_limit_retries + 1} attempts") from exc
                    sleep_for = rate_limit_sleep * attempt
                    print(f"  [429 rate limit] attempt {attempt}/{rate_limit_retries}, sleeping {sleep_for:.0f}s...")
                    time.sleep(sleep_for)
                else:
                    raise
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                if attempt > 3:
                    raise RuntimeError(f"Request failed after 4 attempts: {exc}") from exc
                print(f"  [network error] {exc}, retrying in 10s...")
                time.sleep(10)
        else:
            raise RuntimeError(f"Request failed: {last_error}")

        result_len = len(result)
        in_range = min_count <= result_len <= max_count
        if in_range:
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


def copy_generation(source_dir: Path, target_dir: Path, skill_md: str) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)
    (target_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")


def build_groups(generated_tasks: Path, variants: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for variant in variants:
        task_dir = generated_tasks / variant
        if not task_dir.exists():
            raise FileNotFoundError(f"Generated task not found: {task_dir}")
        s1 = task_dir / "environment" / "skills" / "s1" / "SKILL.md"
        if not s1.exists():
            raise FileNotFoundError(f"Missing S1 skill: {s1}")
        groups.setdefault(base_task_name(variant), []).append(variant)
    return groups


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variants-file", type=Path, default=DEFAULT_VARIANTS_FILE)
    parser.add_argument("--generated-tasks", type=Path, default=DEFAULT_GENERATED_TASKS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-generation", type=int, default=3, help="Generate up to S{N}; default S3.")
    parser.add_argument("--target-pct", type=int, default=60)
    parser.add_argument("--api-key-env", default="GLM_API_KEY")
    parser.add_argument("--base-url", default=os.environ.get("GLM_BASE_URL", "https://open.bigmodel.cn/api/anthropic"))
    parser.add_argument("--model", default=os.environ.get("GLM_DISTILL_MODEL", "glm-5.1"))
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--sleep", type=float, default=2.0)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.max_generation < 2:
        raise SystemExit("--max-generation must be >= 2")

    api_key = os.environ.get(args.api_key_env, "")
    if not api_key and not args.dry_run:
        raise SystemExit(f"Missing API key env var: {args.api_key_env}")

    variants = parse_variants(args.variants_file)
    groups = build_groups(args.generated_tasks, variants)
    endpoint = endpoint_from_base_url(args.base_url)

    print(f"Variants: {len(variants)}")
    print(f"Base-task groups: {', '.join(f'{k}={len(v)}' for k, v in groups.items())}")
    print(f"Endpoint: {endpoint}")
    print(f"Model: {args.model}")

    for generation in range(2, args.max_generation + 1):
        source_generation = generation - 1
        print(f"\n=== Distilling S{source_generation} -> S{generation} ===")
        for base_task, group_variants in groups.items():
            representative = group_variants[0]
            rep_skills = args.generated_tasks / representative / "environment" / "skills"
            source_dir = rep_skills / f"s{source_generation}"
            source_md = source_dir / "SKILL.md"
            if not source_md.exists():
                if args.dry_run:
                    print(
                        f"[dry-run] would use {representative}/s{source_generation}; "
                        "it will exist after the previous generation is generated"
                    )
                    continue
                raise FileNotFoundError(f"Missing source generation for {representative}: {source_md}")

            staging = args.out / f"S{generation}" / base_task
            staging_md = staging / "SKILL.md"
            if args.skip_existing and staging_md.exists():
                print(f"[skip] S{generation} {base_task}: {staging_md}")
                distilled = staging_md.read_text(encoding="utf-8")
            else:
                original = source_md.read_text(encoding="utf-8")
                print(f"[distill] {base_task}: {representative} S{source_generation} ({len(original)} chars)")
                if args.dry_run:
                    distilled = original
                else:
                    distilled = call_chat_completions(
                        endpoint=endpoint,
                        api_key=api_key,
                        model=args.model,
                        skill_content=original,
                        target_pct=args.target_pct,
                        timeout=args.timeout,
                    )
                ratio = len(distilled) / max(1, len(original))
                if args.dry_run:
                    print(f"  -> would save S{generation} to {staging_md} ({ratio:.1%} placeholder)")
                else:
                    staging.mkdir(parents=True, exist_ok=True)
                    staging_md.write_text(distilled, encoding="utf-8")
                    print(f"  -> {len(distilled)} chars ({ratio:.1%}) saved to {staging_md}")

            for variant in group_variants:
                task_skills = args.generated_tasks / variant / "environment" / "skills"
                target_dir = task_skills / f"s{generation}"
                if args.dry_run:
                    print(f"  would deploy {target_dir}")
                else:
                    copy_generation(task_skills / f"s{source_generation}", target_dir, distilled)
                    print(f"  deployed {variant}/s{generation}")
            if not args.dry_run:
                time.sleep(args.sleep)


if __name__ == "__main__":
    main()
