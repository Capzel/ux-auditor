"""Test static UX codebase scanner against fixtures."""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.ux_scan import scan_codebase

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class TestUXScan(unittest.TestCase):
    def test_friction_shop_detects_anti_patterns(self):
        target = FIXTURES_DIR / "friction-shop"
        res = scan_codebase(target)

        rule_ids = {s["rule_id"] for s in res.get("signals", [])}

        # Should detect zoom disabled
        self.assertIn("UX-RESP-ZOOM-DISABLED", rule_ids)
        # Should detect outline none
        self.assertIn("UX-ACC-OUTLINE-NONE", rule_ids)
        # Should detect small button
        self.assertIn("UX-FITTS-SMALL-BUTTON", rule_ids)
        # Should detect icon-only button without label
        self.assertIn("UX-CLR-ICON-ONLY-BUTTON", rule_ids)
        # Should detect missing autocomplete
        self.assertIn("UX-ERG-MISSING-AUTOCOMPLETE", rule_ids)
        # Should detect massive form
        self.assertIn("UX-VIS-MASSIVE-FORM", rule_ids)

        self.assertGreaterEqual(res["summary"]["total_signals"], 5)

    def test_accessible_shop_has_minimal_or_zero_friction(self):
        target = FIXTURES_DIR / "accessible-shop"
        res = scan_codebase(target)

        critical_signals = [s for s in res.get("signals", []) if s["severity"] == "critical"]
        self.assertEqual(len(critical_signals), 0, "Accessible shop should have 0 critical UX signals")


if __name__ == "__main__":
    unittest.main()
