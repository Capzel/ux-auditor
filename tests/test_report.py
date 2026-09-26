"""Test UX audit validation, merging, scoring, and report generation."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.ux_common import CATEGORIES, load_json
from scripts.ux_report import merge_audit, render_all_reports

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class TestUXReport(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_merge_and_render_sample_audit(self):
        src_audit = FIXTURES_DIR / "sample-audit"
        audit_run = self.tmp_dir / "sample-audit"
        shutil.copytree(src_audit, audit_run)

        # 1. Test Merge
        exit_code = merge_audit(audit_run)
        self.assertEqual(exit_code, 0, "Merge should complete with exit code 0")

        audit_data_file = audit_run / "audit-data.json"
        self.assertTrue(audit_data_file.is_file(), "audit-data.json must exist")

        with open(audit_data_file, encoding="utf-8") as fh:
            data = json.load(fh)

        # Check scoring
        scores = data.get("scores", {})
        self.assertIn("overall_score", scores)
        self.assertGreater(scores["overall_score"], 0)
        self.assertLessEqual(scores["overall_score"], 100)

        # Check personas
        self.assertIn("senior", scores.get("persona_scores", {}))
        self.assertIn("young", scores.get("persona_scores", {}))

        # Check deterministic IDs
        for f in data.get("findings", []):
            self.assertTrue(f["id"].startswith(("VIS-", "ERG-", "NAV-", "FDB-", "ERR-", "ACC-", "CLR-")))

        # 2. Test Render
        render_code = render_all_reports(audit_data_file)
        self.assertEqual(render_code, 0, "Render should complete with exit code 0")

        # Verify generated files
        self.assertTrue((audit_run / "UX-AUDIT-REPORT.md").is_file())
        self.assertTrue((audit_run / "ACTION-PLAN.md").is_file())
        self.assertTrue((audit_run / "personas-analysis.md").is_file())
        self.assertTrue((audit_run / "ux-audit-report.html").is_file())

        # Check HTML content
        html_content = (audit_run / "ux-audit-report.html").read_text(encoding="utf-8")
        self.assertIn("UX Audit Report", html_content)
        self.assertIn("Fitts's Law", html_content)
        self.assertIn("window.print()", html_content)


if __name__ == "__main__":
    unittest.main()
