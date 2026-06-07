"""
TailSkills variant test — auto-generated.
Variant: E1_missing_dep
These tests verify the skill produces correct output under variant conditions.
"""

import subprocess
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """The output file must exist."""
        import os
        assert os.path.exists('/root/Awesome-Agent-Papers_processed.pptx'), \
            "Output file /root/Awesome-Agent-Papers_processed.pptx not found"

    def test_lxml_reinstalled(self):
        """lxml must be available (reinstalled by the solver)."""
        import importlib
        mod = importlib.import_module('lxml')
        assert mod is not None, "lxml should have been reinstalled by the solver"

    def test_lxml_etree_functional(self):
        """lxml.etree must be functional for XML processing."""
        from lxml import etree
        root = etree.Element("root")
        child = etree.SubElement(root, "child")
        child.text = "test"
        result = etree.tostring(root)
        assert b"test" in result
