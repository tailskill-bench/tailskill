"""
TailSkills variant test — auto-generated.
Variant: A3_zero_width
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_zero_width_in_output(self):
        """Output JSON should not contain zero-width Unicode characters."""
        ZW_CHARS = {'\u200b', '\u200c', '\u200d', '\ufeff'}
        import unicodedata
        output_dirs = ['/root', '/root/output']
        for output_dir in output_dirs:
            if not os.path.isdir(output_dir):
                continue
            for f in os.listdir(output_dir):
                if not f.endswith(('.json', '.csv', '.txt')) or f.startswith('.'):
                    continue
                filepath = os.path.join(output_dir, f)
                with open(filepath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                for i, ch in enumerate(content):
                    if ch in ZW_CHARS or unicodedata.category(ch) == 'Cf':
                        context = content[max(0, i-20):i+20]
                        pytest.fail(
                            f"Zero-width char U+{ord(ch):04X} found in {filepath} "
                            f"at position {i}: ...{context}..."
                        )
