"""TailSkills variant test — E2_version_drift (playwright 1.40.0 → 1.49.1)"""
import subprocess
import pytest


class TestTailVariant:

    def test_playwright_version(self):
        """playwright version must be >= 1.49.0 after oracle upgrade."""
        result = subprocess.run(
            ['python3', '-c', 'import playwright; print(playwright.__version__)'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"playwright must be importable: {result.stderr}"
        version = result.stdout.strip()
        major, minor = int(version.split('.')[0]), int(version.split('.')[1])
        assert (major, minor) >= (1, 49), f"playwright version must be >= 1.49.0, got {version}"
