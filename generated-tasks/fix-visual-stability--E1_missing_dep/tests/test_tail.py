"""TailSkills variant test — E1_missing_dep (playwright)"""
import subprocess
import pytest


class TestTailVariant:

    def test_playwright_importable(self):
        """playwright must be importable after oracle reinstall."""
        result = subprocess.run(
            ['python3', '-c', 'from playwright.sync_api import sync_playwright; print("ok")'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"playwright must be importable: {result.stderr}"
