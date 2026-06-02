#!/usr/bin/env python3
"""TailSkills recursive distillation — adapted from distill_skillsbench_per_skill.py.

Distills each variant's s1/SKILL.md through s2 -> s3 -> s4, deploying results
directly into the generated-tasks directory structure.

Directory layout (per variant):
    generated-tasks/<variant>/environment/skills/
    +-- s1/SKILL.md   (original, untouched)
    +-- s2/SKILL.md   (distilled from s1)
    +-- s3/SKILL.md   (distilled from s2)
    +-- s4/SKILL.md   (distilled from s3)

Each s{gen}/ inherits auxiliary files (scripts/, etc.) from s1/.

Key features inherited from the SkillsBench script:
- Length retry with feedback (3 attempts by default)
- Rate-limit retry with exponential backoff
- Manifest tracking per variant with --only-failed rerun support
- Per-generation accept ranges (target +/- tolerance)
- Strict failure: raises RuntimeError if length is out of range after all retries
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS_ROOT = ROOT / "generated-tasks"
DEFAULT_TASK_LIST = ROOT / "configs" / "all_200_variants.txt"
DEFAULT_OUT = ROOT / "skill-generations" / "tailskills"
DEFAULT_RATIOS = "70,70,80"
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/anthropic"
DEFAULT_MODEL = "anthropic/glm-5.1"
DEFAULT_API_FORMAT = "anthropic"
DEFAULT_TOLERANCE = 15

PROMPT_TEMPLATE = """You are a strict technical editor compressing an agent skill document.

HARD CONSTRAINT
- The rewritten Markdown MUST be between {min_count} and {max_count} characters.
- This is the target {target_pct}% of the source ({char_count} characters).
- Outputs outside this range will be rejected and you will be re-prompted.

OUTPUT FORMAT (strict)
- Output only the rewritten Markdown skill document.
- No preface, no commentary, no diff, no apology, no list of cuts.
- Do not wrap the whole document in an outer ```markdown fence.

PRESERVE (these must survive)
1. Concrete commands, exact file paths, script/module/function names, environment variables.
2. Task-specific identifiers: dataset filenames, schema or column names, formulas, API endpoints, port numbers, version pins.
3. Verification, success-check, and validation steps the agent must perform.
4. Correctness-critical constraints, warnings, and ordering requirements.
5. Original section structure when it helps an agent skim and locate the workflow.

DELETE FIRST (cut these to fit the length range)
1. Generic background, motivational prose, "why this matters" explanations.
2. Duplicated examples, secondary examples, exhaustive option tables.
3. Troubleshooting, FAQ, "common pitfalls", and similar reference sections.
4. Long narrative that can be replaced by a one-line trigger -> action bullet.
5. Repeated or near-identical code snippets; keep at most one compact snippet per workflow.

CODE RULES
- Code snippets must remain syntactically self-contained: no undefined variables, no half-formed functions, no dangling imports, no half-finished branches.
- If a complete snippet would push you over the length budget, replace it with a short prose checklist instead of emitting broken code.

DO NOT
- Do not invent new capabilities, configurations, options, or task variants.
- Do not paraphrase exact commands, paths, or identifiers; copy them verbatim.
- Do not mention compression, distillation, generations, length, character counts, or this prompt.

SOURCE SKILL
```markdown
{skill_content}
```

REWRITTEN SKILL (Markdown only, {min_count}-{max_count} characters):
"""

EDIT_PROMPT_TEMPLATE = """You are a strict technical editor editing an agent skill document in place.

HARD CONSTRAINT
- The edited Markdown MUST be between {min_count} and {max_count} characters.
- This is the target {target_pct}% of the source ({char_count} characters).
- Outputs outside this range will be rejected and you will be re-prompted.

OUTPUT FORMAT (strict)
- Output only the full edited Markdown document.
- No preface, no commentary, no diff, no apology, no list of changes.
- Do not wrap the whole document in an outer ```markdown fence.

KEEP THE STRUCTURE
- Preserve the existing top-level section headings when they remain useful; you may merge sibling sections that are redundant.
- An agent will look for the same workflow steps in roughly the same order.

PRESERVE
1. Concrete commands, exact file paths, script/module/function names, environment variables.
2. Task-specific identifiers: dataset filenames, schema or column names, formulas, API endpoints, port numbers, version pins.
3. Verification, success-check, and validation steps.
4. Correctness-critical constraints, warnings, and ordering requirements.

EDIT BY DELETING (cut these first)
1. Generic background, motivational prose, "why this matters" explanations.
2. Duplicated examples, secondary examples, exhaustive option tables.
3. Troubleshooting, FAQ, "common pitfalls", and similar reference sections.
4. Long narrative; replace with one-line trigger -> action bullets.
5. Repeated code; keep at most one compact snippet per workflow.

CODE RULES
- Edited code must remain syntactically self-contained: no undefined variables, no half-functions, no dangling imports, no half-finished branches.
- If a snippet would push you over the length budget, replace it with a short prose checklist instead of emitting broken code.

DO NOT
- Do not add new capabilities, configurations, options, or task variants.
- Do not paraphrase exact commands, paths, or identifiers; copy them verbatim.
- Do not mention editing, compression, distillation, generations, length, character counts, or this prompt.

DOCUMENT TO EDIT
```markdown
{skill_content}
```

EDITED DOCUMENT (Markdown only, {min_count}-{max_count} characters):
"""

S2_GENTLE_PROMPT_TEMPLATE = """You are lightly editing a short agent skill document. This document is already compact — make only minor trims.

HARD CONSTRAINT
- Output MUST be between {min_count} and {max_count} characters. Source is {char_count} characters. Target is {target_pct}%.
- This is a GENTLE pass — do NOT cut aggressively. Just remove obvious redundancy.

OUTPUT FORMAT
- Output ONLY the edited Markdown. No commentary, no fences.

GENTLE EDITING RULES
1. Only remove clearly redundant sentences or repeated information.
2. Shorten verbose descriptions by 1-2 words where possible, but do NOT rewrite.
3. Keep ALL code snippets, formulas, tables, and lists exactly as they are.
4. Keep ALL section headings and structure.
5. Remove empty lines or excessive whitespace if present.

CODE RULES
- Code snippets must remain exactly as-is. Do NOT modify code.

PRESERVE (do not lose these)
- All code, file paths, script names, environment variables
- All technical parameters, constraints, and validation steps
- All section structure and headings

DOCUMENT TO EDIT
```markdown
{skill_content}
```

LIGHTLY EDITED DOCUMENT (target {min_count}-{max_count} chars):
"""

CODE_COMPRESS_PROMPT_TEMPLATE = """You are compressing a very short agent skill document. This document is mostly code with minimal text. To reach the target length, you MUST also compress the code itself.

HARD CONSTRAINT
- Output MUST be between {min_count} and {max_count} characters. Source is {char_count} characters. Target is {target_pct}%.
- You WILL be rejected if you output more than {max_count} characters.

OUTPUT FORMAT
- Output ONLY the compressed Markdown. No commentary, no fences.

TEXT COMPRESSION RULES
1. Shorten frontmatter description to one short sentence.
2. MERGE all sections into fewer sections.
3. Remove section dividers (---), empty lines, filler words.
4. Replace multi-sentence prose with single bullet points.
5. Remove redundant formatting (extra blank lines, decorative separators).

CODE COMPRESSION RULES (ALLOWED for this document)
1. Remove ALL comments from code (# ... lines).
2. Remove unnecessary intermediate variables.
3. Merge multiple similar code blocks into ONE compact block.
4. Remove import statements that are not critical for understanding.
5. Shorten variable names where meaning stays clear (only in examples, not API names).
6. Remove optional/redundant code that is not essential for the workflow.
7. If two code blocks show similar patterns, keep only the most important one.
8. Shorten multi-line code to fewer lines where possible without losing correctness.

PRESERVE (do not lose these)
- Exact file paths, script names, environment variables, column names
- Core algorithm logic and key function signatures
- Critical constraints and validation steps

DOCUMENT TO COMPRESS
```markdown
{skill_content}
```

COMPRESSED DOCUMENT (target {min_count}-{max_count} chars):
"""

S3_AGGRESSIVE_PROMPT_TEMPLATE = """You are aggressively compressing an already-compressed agent skill document (2nd compression pass). You MUST cut it down significantly.

HARD CONSTRAINT
- Output MUST be between {min_count} and {max_count} characters. Source is {char_count} characters. Target is {target_pct}%.
- You WILL be rejected if you output more than {max_count} characters. This is NON-NEGOTIABLE.
- DO NOT output the same content with minor tweaks. You MUST actually reduce the length.

OUTPUT FORMAT
- Output ONLY the compressed Markdown. No commentary, no fences.

AGGRESSIVE COMPRESSION RULES
1. Shorten the frontmatter description to one short sentence.
2. MERGE related sections aggressively. Multiple similar sections → one combined section.
3. Remove section dividers (---).
4. Remove ALL redundant explanations that repeat what the code already shows.
5. Replace multi-sentence prose with single bullet points.
6. Remove transitional phrases, introductory text, and filler words entirely.
7. Condense lists: merge similar items, remove descriptions from obvious items.

CODE RULES
- Code snippets must remain syntactically self-contained and complete. Do NOT shorten, inline, or delete code.
- If a code snippet would push you over the length budget, remove surrounding prose instead of cutting code.

PRESERVE (do not lose these)
- Exact file paths, script names, environment variables, column names
- All code snippets, formulas, and algorithm logic
- Critical constraints and validation steps

DOCUMENT TO COMPRESS
```markdown
{skill_content}
```

COMPRESSED DOCUMENT (target {min_count}-{max_count} chars):
"""

AGGRESSIVE_PROMPT_TEMPLATE = """You are aggressively compressing an already-compressed agent skill document (3rd compression pass). You MUST cut it down significantly.

HARD CONSTRAINT
- Output MUST be between {min_count} and {max_count} characters. Source is {char_count} characters. Target is {target_pct}%.
- You WILL be rejected if you output more than {max_count} characters. This is NON-NEGOTIABLE.

OUTPUT FORMAT
- Output ONLY the compressed Markdown. No commentary, no fences.

AGGRESSIVE COMPRESSION RULES
1. Shorten the frontmatter description to one sentence.
2. MERGE related sections. Three YAML sections → one. Multiple CSV examples → one compact example.
3. Remove section dividers (---).
4. Remove redundant explanations that repeat what the code already shows.

CODE RULES
- Code snippets must remain syntactically self-contained and complete. Do NOT shorten, inline, or delete code.
- If a code snippet would push you over the length budget, remove surrounding prose instead of cutting code.

PRESERVE (do not lose these)
- Exact file paths, script names, environment variables, column names
- All code snippets, formulas, and algorithm logic
- Critical constraints and validation steps

DOCUMENT TO COMPRESS
```markdown
{skill_content}
```

COMPRESSED DOCUMENT (target {min_count}-{max_count} chars):
"""


@dataclass(frozen=True)
class SkillSource:
    skill_name: str
    skill_md: Path
    skill_dir: Path
    rel_path: str
    char_count: int
    sha256: str


def parse_task_list(path: Path) -> tuple[list[str], list[str]]:
    tasks: list[str] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line in seen:
            duplicates.append(line)
            continue
        seen.add(line)
        tasks.append(line)
    return tasks, duplicates


def endpoint_from_base_url(base_url: str, api_format: str) -> str:
    base = base_url.rstrip("/")
    if api_format == "anthropic":
        if base.endswith("/v1/messages"):
            return base
        return f"{base}/v1/messages"
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def normalize_model_name(model: str) -> str:
    return model.removeprefix("anthropic/").removeprefix("openai/")


def strip_code_fences(content: str) -> str:
    text = content.strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown") :].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_skill_sources(task_dir: Path) -> list[SkillSource]:
    skills_root = task_dir / "environment" / "skills"
    if not skills_root.exists():
        return []
    s1_md = skills_root / "s1" / "SKILL.md"
    if not s1_md.exists():
        return []
    content = s1_md.read_text(encoding="utf-8")
    return [
        SkillSource(
            skill_name="s1",
            skill_md=s1_md,
            skill_dir=s1_md.parent,
            rel_path=str(s1_md.relative_to(task_dir)),
            char_count=len(content),
            sha256=sha256_text(content),
        )
    ]


def copy_skill_assets(skill_source: SkillSource, dest_dir: Path) -> list[str]:
    copied: list[str] = []
    if not skill_source.skill_dir.exists():
        return copied
    for item in sorted(skill_source.skill_dir.iterdir()):
        if item.name == "SKILL.md":
            continue
        target = dest_dir / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
        copied.append(item.name)
    return copied


def write_skill_generation(
    *,
    task_out_root: Path,
    generation: int,
    skill_source: SkillSource,
    content: str,
) -> Path:
    gen_dir = task_out_root / f"s{generation}"
    if gen_dir.exists():
        shutil.rmtree(gen_dir)
    gen_dir.mkdir(parents=True, exist_ok=True)
    copy_skill_assets(skill_source, gen_dir)
    (gen_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return gen_dir


def build_anthropic_payload(model: str, prompt: str, max_tokens: int) -> bytes:
    return json.dumps(
        {
            "model": normalize_model_name(model),
            "system": "You rewrite agent skill documentation concisely and output only Markdown.",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "top_p": 1,
            "max_tokens": max_tokens,
        },
        ensure_ascii=False,
    ).encode("utf-8")


def build_openai_payload(model: str, prompt: str, max_tokens: int) -> bytes:
    return json.dumps(
        {
            "model": normalize_model_name(model),
            "messages": [
                {
                    "role": "system",
                    "content": "You rewrite agent skill documentation concisely and output only Markdown.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "top_p": 1,
            "max_tokens": max_tokens,
        },
        ensure_ascii=False,
    ).encode("utf-8")


def parse_openai_response(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    content = data["choices"][0]["message"]["content"]
    return strip_code_fences(content), data.get("usage", {})


def parse_anthropic_response(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    parts = data.get("content", [])
    text_parts: list[str] = []
    for part in parts:
        if isinstance(part, dict) and part.get("type") == "text":
            text_parts.append(str(part.get("text", "")))
    if not text_parts:
        raise KeyError("Anthropic response did not contain text content")
    return strip_code_fences("\n".join(text_parts)), data.get("usage", {})


def build_ssl_context(ca_bundle: str | None) -> ssl.SSLContext | None:
    if ca_bundle:
        return ssl.create_default_context(cafile=ca_bundle)
    try:
        import certifi  # type: ignore[import-not-found]
    except ImportError:
        return None
    return ssl.create_default_context(cafile=certifi.where())


def call_llm(
    *,
    endpoint: str,
    api_format: str,
    api_key: str,
    model: str,
    skill_content: str,
    target_pct: int,
    accept_min_pct: int,
    accept_max_pct: int,
    distill_mode: str,
    timeout: int,
    max_tokens: int,
    retries: int,
    retry_sleep: float,
    rate_limit_retries: int,
    rate_limit_sleep: float,
    length_retries: int,
    ssl_context: ssl.SSLContext | None,
    aggressive: bool = False,
    aggressive_s3: bool = False,
    gentle_s2: bool = False,
    code_compress: bool = False,
) -> tuple[str, dict[str, Any]]:
    char_count = len(skill_content)
    target_count = int(char_count * target_pct / 100)
    min_count = int(char_count * accept_min_pct / 100)
    max_count = int(char_count * accept_max_pct / 100)

    if api_format == "anthropic":
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
        build_payload = build_anthropic_payload
    elif api_format == "openai":
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        build_payload = build_openai_payload
    else:
        raise ValueError(f"Unsupported API format: {api_format}")

    length_feedback = ""
    last_error: Exception | None = None
    last_content = ""
    last_usage: dict[str, Any] = {}

    for length_attempt in range(length_retries + 1):
        if code_compress:
            prompt_template = CODE_COMPRESS_PROMPT_TEMPLATE
        elif gentle_s2:
            prompt_template = S2_GENTLE_PROMPT_TEMPLATE
        elif aggressive:
            prompt_template = AGGRESSIVE_PROMPT_TEMPLATE
        elif aggressive_s3:
            prompt_template = S3_AGGRESSIVE_PROMPT_TEMPLATE
        else:
            prompt_template = EDIT_PROMPT_TEMPLATE if distill_mode == "edit" else PROMPT_TEMPLATE
        prompt = prompt_template.format(
            skill_content=skill_content,
            target_pct=target_pct,
            char_count=char_count,
            min_count=min_count,
            max_count=max_count,
        )
        if length_feedback:
            prompt += length_feedback

        payload = build_payload(model=model, prompt=prompt, max_tokens=max_tokens)

        for attempt in range(1, retries + 2):
            request = urllib.request.Request(
                endpoint,
                data=payload,
                headers=headers,
            )
            try:
                with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as response:
                    data = json.loads(response.read().decode("utf-8"))
                if api_format == "anthropic":
                    last_content, last_usage = parse_anthropic_response(data)
                else:
                    last_content, last_usage = parse_openai_response(data)
                break
            except urllib.error.HTTPError as exc:
                last_error = exc
                is_rate_limit = exc.code == 429
                max_attempts = rate_limit_retries if is_rate_limit else retries
                if attempt > max_attempts:
                    raise RuntimeError(
                        f"LLM request failed after {max_attempts + 1} attempts: {last_error}"
                    ) from last_error
                sleep_for = (rate_limit_sleep if is_rate_limit else retry_sleep) * attempt
                print(f"  [retry {attempt}] HTTP {exc.code}, sleeping {sleep_for:.0f}s...")
                time.sleep(sleep_for)
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt > retries:
                    raise RuntimeError(
                        f"LLM request failed after {retries + 1} attempts: {last_error}"
                    ) from last_error
                time.sleep(retry_sleep * attempt)

        content_len = len(last_content)
        in_range = min_count <= content_len <= max_count
        last_usage = dict(last_usage)
        last_usage["length_attempts"] = length_attempt + 1
        last_usage["length_in_range"] = in_range
        last_usage["target_chars"] = target_count
        last_usage["min_chars"] = min_count
        last_usage["max_chars"] = max_count
        if in_range:
            return last_content, last_usage

        direction = "too long" if content_len > max_count else "too short"
        print(
            f"  [length retry {length_attempt + 1}/{length_retries}] "
            f"{content_len} chars is {direction} (need {min_count}-{max_count})"
        )
        length_feedback = (
            "\n\nLength correction: the previous rewrite was "
            f"{content_len} characters, which is {direction}. Rewrite the same source again "
            f"between {min_count} and {max_count} characters "
            f"({accept_min_pct}%-{accept_max_pct}% of the source length). "
            "The length range is binding. Remove troubleshooting sections, generic tips, broad reference tables, "
            "secondary configurations, and repeated code examples first. You may replace long code blocks with "
            "compact skeletons or short checklists, but do not create broken snippets or references to undefined "
            "variables. Preserve only the core workflow, required commands, critical constraints, formulas, schemas, "
            "and verification steps needed for ordinary task success."
        )

    raise RuntimeError(
        "LLM rewrite missed the accepted length range after "
        f"{length_retries + 1} attempts: got {len(last_content)} chars, "
        f"expected {min_count}-{max_count} chars "
        f"({accept_min_pct}%-{accept_max_pct}% of source)."
    )


def parse_ratios(raw: str) -> list[int]:
    ratios = [int(item.strip()) for item in raw.split(",") if item.strip()]
    if len(ratios) != 3:
        raise ValueError("--ratios must contain exactly three comma-separated integers for S2,S3,S4")
    for ratio in ratios:
        if ratio < 20 or ratio > 100:
            raise ValueError(f"Unreasonable compression ratio: {ratio}")
    return ratios


def parse_tolerances(raw: str, n: int) -> list[int]:
    parts = [int(item.strip()) for item in raw.split(",") if item.strip()]
    if len(parts) == 1:
        return parts * n
    if len(parts) != n:
        raise ValueError(f"--tolerance must be one value or {n} comma-separated values")
    return parts


def deploy_to_task(task_dir: Path, source_generation_dir: Path, generation: int) -> None:
    skills_root = task_dir / "environment" / "skills"
    target_dir = skills_root / f"s{generation}"
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_generation_dir, target_dir)


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def length_in_accepted_range(content: str, source_content: str, min_pct: int, max_pct: int) -> bool:
    source_len = max(1, len(source_content))
    content_len = len(content)
    return int(source_len * min_pct / 100) <= content_len <= int(source_len * max_pct / 100)


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def task_overall_status(skills: dict[str, Any]) -> str:
    if not skills:
        return "failed"
    statuses = {info.get("status") for info in skills.values()}
    if statuses == {"completed"}:
        return "completed"
    if "completed" in statuses:
        return "partial"
    return "failed"


def refresh_failed_records(manifest: dict[str, Any]) -> None:
    failed_skills: list[dict[str, Any]] = []
    failed_tasks: list[str] = []
    for task_name, info in manifest.get("tasks", {}).items():
        if not isinstance(info, dict):
            continue
        skills = info.get("skills", {})
        for skill_name, skill_info in skills.items():
            if skill_info.get("status") == "failed" and "failure" in skill_info:
                fail = dict(skill_info["failure"])
                fail.setdefault("task", task_name)
                fail.setdefault("skill", skill_name)
                failed_skills.append(fail)
        if info.get("status") in {"failed", "partial"}:
            failed_tasks.append(task_name)
    manifest["failed_skills"] = failed_skills
    manifest["failed_tasks"] = failed_tasks


def distill_one_skill(
    *,
    task_name: str,
    task_out_root: Path,
    skill_source: SkillSource,
    ratios: list[int],
    tolerances: list[int],
    accept_caps: list[int] | None,
    args: argparse.Namespace,
    endpoint: str,
    api_key: str,
    ssl_context: ssl.SSLContext | None,
) -> dict[str, Any]:
    skill_entry: dict[str, Any] = {
        "skill_name": skill_source.skill_name,
        "source": {
            "rel_path": skill_source.rel_path,
            "char_count": skill_source.char_count,
            "sha256": skill_source.sha256,
        },
        "generations": {},
        "status": "in_progress",
    }

    # S1: verbatim copy to staging
    s1_content = skill_source.skill_md.read_text(encoding="utf-8")
    if args.dry_run:
        print(f"    S1: dry-run would copy {len(s1_content)} chars")
    else:
        write_skill_generation(
            task_out_root=task_out_root,
            generation=1,
            skill_source=skill_source,
            content=s1_content,
        )
        print(f"    S1: {len(s1_content)} chars staged")
    skill_entry["generations"]["s1"] = {
        "chars": len(s1_content),
        "sha256": sha256_text(s1_content),
    }

    previous_content = s1_content
    for offset, target_pct in enumerate(ratios, start=2):
        generation = offset
        tol = tolerances[offset - 2]
        accept_min_pct = max(0, target_pct - tol)
        accept_max_pct = min(100, target_pct + tol)
        if accept_caps is not None:
            accept_max_pct = min(accept_max_pct, accept_caps[offset - 2])
        target_md = task_out_root / f"s{generation}" / "SKILL.md"

        distilled = ""
        usage: dict[str, Any] = {}

        if args.skip_existing and target_md.exists():
            existing = target_md.read_text(encoding="utf-8")
            if length_in_accepted_range(existing, previous_content, accept_min_pct, accept_max_pct):
                distilled = existing
                usage = {"skipped_existing": True}
                print(f"    S{generation}: skip existing {len(distilled)} chars")

        if not distilled and args.dry_run:
            distilled = previous_content
            usage = {"dry_run": True}
            print(f"    S{generation}: dry-run would distill to {target_pct}%")
        elif not distilled:
            is_last_gen = (offset == len(ratios) + 1)
            is_s3 = (offset == len(ratios))  # 2nd of 3 generations = S3
            is_s2 = (offset == 2)  # 1st of 3 generations = S2
            has_code_compress = getattr(args, 'code_compress', False)
            print(f"    S{generation}: distilling to {target_pct}% (accept {accept_min_pct}-{accept_max_pct}%){' [code-compress]' if has_code_compress else ''}{' [aggressive]' if is_last_gen and not has_code_compress else ''}{' [aggressive-s3]' if is_s3 and not is_last_gen and not has_code_compress else ''}{' [gentle-s2]' if is_s2 and not is_last_gen and not is_s3 and not has_code_compress else ''}...")
            try:
                distilled, usage = call_llm(
                    endpoint=endpoint,
                    api_format=args.api_format,
                    api_key=api_key,
                    model=args.model,
                    skill_content=previous_content,
                    target_pct=target_pct,
                    accept_min_pct=accept_min_pct,
                    accept_max_pct=accept_max_pct,
                    distill_mode=args.distill_mode,
                    timeout=args.timeout,
                    max_tokens=args.max_tokens,
                    retries=args.retries,
                    retry_sleep=args.retry_sleep,
                    rate_limit_retries=args.rate_limit_retries,
                    rate_limit_sleep=args.rate_limit_sleep,
                    length_retries=args.length_retries,
                    ssl_context=ssl_context,
                    aggressive=is_last_gen and not has_code_compress,
                    aggressive_s3=is_s3 and not is_last_gen and not has_code_compress,
                    gentle_s2=is_s2 and not is_last_gen and not is_s3 and not has_code_compress,
                    code_compress=has_code_compress,
                )
            except Exception as exc:
                failure = {
                    "task": task_name,
                    "failed_generation": f"s{generation}",
                    "source_generation": f"s{generation - 1}",
                    "error": str(exc),
                    "source_chars": len(previous_content),
                    "target_pct": target_pct,
                    "accept_min_pct": accept_min_pct,
                    "accept_max_pct": accept_max_pct,
                }
                skill_entry["status"] = "failed"
                skill_entry["failure"] = failure
                print(f"    [FAILED] S{generation}: {exc}")
                if args.fail_fast:
                    raise
                return skill_entry

        if not args.dry_run:
            write_skill_generation(
                task_out_root=task_out_root,
                generation=generation,
                skill_source=skill_source,
                content=distilled,
            )

        ratio_to_prev = len(distilled) / max(1, len(previous_content))
        ratio_to_s1 = len(distilled) / max(1, len(s1_content))
        skill_entry["generations"][f"s{generation}"] = {
            "chars": len(distilled),
            "sha256": sha256_text(distilled),
            "target_pct": target_pct,
            "accept_min_pct": accept_min_pct,
            "accept_max_pct": accept_max_pct,
            "ratio_to_previous": ratio_to_prev,
            "ratio_to_s1": ratio_to_s1,
            "usage": usage,
        }
        print(f"      -> {len(distilled)} chars ({ratio_to_prev:.1%} prev, {ratio_to_s1:.1%} S1)")
        previous_content = distilled
        if not args.dry_run:
            time.sleep(args.sleep)
    else:
        skill_entry["status"] = "completed"
    return skill_entry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS_ROOT)
    parser.add_argument("--task-list", type=Path, default=DEFAULT_TASK_LIST)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--ratios", default=DEFAULT_RATIOS)
    parser.add_argument("--tolerance", default=str(DEFAULT_TOLERANCE))
    parser.add_argument("--api-key-env", default="GLM_API_KEY")
    parser.add_argument("--base-url", default=os.environ.get("GLM_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--model", default=os.environ.get("GLM_DISTILL_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-format", choices=["anthropic", "openai"],
                        default=os.environ.get("GLM_API_FORMAT", DEFAULT_API_FORMAT))
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--rate-limit-retries", type=int, default=6)
    parser.add_argument("--rate-limit-sleep", type=float, default=60.0)
    parser.add_argument("--length-retries", type=int, default=3)
    parser.add_argument("--retry-sleep", type=float, default=5.0)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--distill-mode", choices=["rewrite", "edit"], default="edit")
    parser.add_argument("--ca-bundle", default=os.environ.get("SSL_CERT_FILE"))
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--only-failed", action="store_true")
    parser.add_argument("--quality-fix-tasks", default="")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--tasks", default="", help="Comma-separated subset of task names")
    parser.add_argument("--code-compress", action="store_true", help="Use code-compress prompt that allows compressing code blocks")
    parser.add_argument("--accept-cap", default="", help="Max accept pct per generation (comma-sep), clips upper bound to captain's limits")
    args = parser.parse_args()

    ratios = parse_ratios(args.ratios)
    tolerances = parse_tolerances(args.tolerance, len(ratios))
    if args.accept_cap.strip():
        accept_caps = [int(x.strip()) for x in args.accept_cap.split(",") if x.strip()]
        if len(accept_caps) == 1:
            accept_caps = accept_caps * len(ratios)
        if len(accept_caps) != len(ratios):
            raise ValueError(f"--accept-cap must be one value or {len(ratios)} values")
    else:
        accept_caps = None
    tasks, duplicates = parse_task_list(args.task_list)
    endpoint = endpoint_from_base_url(args.base_url, args.api_format)
    api_key = os.environ.get(args.api_key_env, "")
    if not api_key and not args.dry_run:
        raise SystemExit(f"Missing API key env var: {args.api_key_env}")
    ssl_context = build_ssl_context(args.ca_bundle)

    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "manifest.json"
    existing_manifest = load_manifest(manifest_path)

    if args.tasks.strip():
        wanted = {item.strip() for item in args.tasks.split(",") if item.strip()}
        tasks = [t for t in tasks if t in wanted]
        unknown = sorted(wanted - set(tasks))
        if unknown:
            print(f"[warn] --tasks names not in task list: {', '.join(unknown)}")

    selected_tasks_filter: set[str] | None = None
    selected_skills_filter: dict[str, set[str]] = {}

    if args.only_failed:
        if not existing_manifest:
            raise SystemExit("--only-failed requires an existing manifest.json in --out")
        failed_task_names: set[str] = set()
        for task_name, info in existing_manifest.get("tasks", {}).items():
            if not isinstance(info, dict):
                continue
            skills = info.get("skills", {})
            failed_skill_names = {
                name for name, skill_info in skills.items() if skill_info.get("status") == "failed"
            }
            if info.get("status") in {"failed", "partial"} or failed_skill_names:
                failed_task_names.add(task_name)
                if failed_skill_names:
                    selected_skills_filter[task_name] = failed_skill_names
        quality_fix_names = {item.strip() for item in args.quality_fix_tasks.split(",") if item.strip()}
        for qf_task in quality_fix_names:
            selected_skills_filter.pop(qf_task, None)
            failed_task_names.add(qf_task)
        selected_tasks_filter = failed_task_names
        tasks = [t for t in tasks if t in selected_tasks_filter]

    base_tasks_manifest: dict[str, Any] = {}
    if existing_manifest and args.only_failed:
        base_tasks_manifest = dict(existing_manifest.get("tasks", {}))
    base_missing: list[str] = []
    base_no_skills: list[str] = []

    manifest: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task_list": str(args.task_list),
        "tasks_requested_unique": len(tasks),
        "duplicates": duplicates,
        "ratios": {"s2": ratios[0], "s3": ratios[1], "s4": ratios[2]},
        "tolerance": args.tolerance,
        "model": args.model,
        "api_format": args.api_format,
        "endpoint": endpoint,
        "distill_mode": args.distill_mode,
        "dry_run": args.dry_run,
        "tasks": base_tasks_manifest,
        "missing_tasks": base_missing,
        "tasks_without_skills": base_no_skills,
        "failed_skills": [],
        "failed_tasks": [],
    }

    print(f"Task list: {args.task_list}")
    print(f"Tasks to process: {len(tasks)}")
    print(f"Output: {args.out}")
    print(f"Model: {args.model} | API: {args.api_format} | endpoint: {endpoint}")
    print(f"Distill mode: {args.distill_mode}")
    print(f"Ratios: S2={ratios[0]}% S3={ratios[1]}% S4={ratios[2]}%")
    print(f"Tolerance: +/-{args.tolerance}% (per-generation accept range)")
    if args.only_failed:
        print(f"Only-failed mode: {len(tasks)} task(s) selected")

    for task_name in tasks:
        task_dir = args.tasks_root / task_name
        task_out_root = args.out / task_name

        if not task_dir.exists():
            print(f"[missing] {task_name}: {task_dir}")
            if task_name not in manifest["missing_tasks"]:
                manifest["missing_tasks"].append(task_name)
            continue

        sources = read_skill_sources(task_dir)
        if not sources:
            print(f"[no skills] {task_name}")
            if task_name not in manifest["tasks_without_skills"]:
                manifest["tasks_without_skills"].append(task_name)
            continue

        previous_task_entry = manifest["tasks"].get(task_name) if args.only_failed else None
        if isinstance(previous_task_entry, dict):
            task_entry = previous_task_entry
            task_entry.setdefault("skills", {})
        else:
            task_entry = {
                "sources": [
                    {
                        "skill_name": s.skill_name,
                        "rel_path": s.rel_path,
                        "char_count": s.char_count,
                        "sha256": s.sha256,
                    }
                    for s in sources
                ],
                "skills": {},
            }

        per_task_skill_filter: set[str] | None = None
        if args.only_failed and task_name in selected_skills_filter:
            per_task_skill_filter = selected_skills_filter[task_name]

        print(f"\n=== {task_name} ===")
        for skill_source in sources:
            if per_task_skill_filter is not None and skill_source.skill_name not in per_task_skill_filter:
                existing_skill = task_entry["skills"].get(skill_source.skill_name)
                if existing_skill and existing_skill.get("status") == "completed":
                    print(f"  keep existing completed entry")
                    continue

            skill_entry = distill_one_skill(
                task_name=task_name,
                task_out_root=task_out_root,
                skill_source=skill_source,
                ratios=ratios,
                tolerances=tolerances,
                accept_caps=accept_caps,
                args=args,
                endpoint=endpoint,
                api_key=api_key,
                ssl_context=ssl_context,
            )
            task_entry["skills"][skill_source.skill_name] = skill_entry

            if not args.dry_run and skill_entry.get("status") == "completed":
                for gen in (2, 3, 4):
                    src = task_out_root / f"s{gen}"
                    if src.exists():
                        deploy_to_task(task_dir, src, gen)
                        print(f"  deployed s{gen} -> {task_dir.name}/environment/skills/s{gen}")

            manifest["tasks"][task_name] = task_entry
            task_entry["status"] = task_overall_status(task_entry["skills"])
            refresh_failed_records(manifest)
            write_manifest(manifest_path, manifest)

        task_entry["status"] = task_overall_status(task_entry["skills"])
        manifest["tasks"][task_name] = task_entry
        refresh_failed_records(manifest)
        write_manifest(manifest_path, manifest)
        print(f"  Task status: {task_entry['status']}")

    refresh_failed_records(manifest)
    write_manifest(manifest_path, manifest)
    print(f"\nManifest written to {manifest_path}")
    print(
        f"Summary: completed="
        f"{sum(1 for t in manifest['tasks'].values() if isinstance(t, dict) and t.get('status') == 'completed')}, "
        f"partial="
        f"{sum(1 for t in manifest['tasks'].values() if isinstance(t, dict) and t.get('status') == 'partial')}, "
        f"failed="
        f"{sum(1 for t in manifest['tasks'].values() if isinstance(t, dict) and t.get('status') == 'failed')}"
    )


if __name__ == "__main__":
    main()
