#!/usr/bin/env python3
"""Inject zero-width Unicode characters into dialogue script text."""
import random
import sys

ZW_CHARS = ["\u200b", "\u200c", "\u200d"]


def inject_zero_width_text(filepath, ratio=0.05):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    random.seed(42)
    n_inject = max(1, int(len(lines) * ratio))
    targets = random.sample(range(len(lines)), min(n_inject, len(lines)))

    for idx in targets:
        line = lines[idx].rstrip("\n")
        if not line or line.startswith("//"):
            continue
        # Insert zero-width char at a random position in the text
        pos = random.randint(1, max(1, len(line) - 1))
        lines[idx] = line[:pos] + random.choice(ZW_CHARS) + line[pos:] + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"[TailSkills] Zero-width: {n_inject} lines modified → {filepath}")


if __name__ == "__main__":
    inject_zero_width_text(sys.argv[1])
