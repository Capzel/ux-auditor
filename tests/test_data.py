"""Test integrity and completeness of curated UX reference data."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_ROOT / "data"


class TestUXData(unittest.TestCase):
    def test_laws_of_ux_integrity(self):
        laws_file = DATA_DIR / "laws_of_ux.json"
        self.assertTrue(laws_file.is_file(), "laws_of_ux.json missing")
        with open(laws_file, encoding="utf-8") as fh:
            data = json.load(fh)

        laws = data.get("laws", [])
        self.assertGreaterEqual(len(laws), 20, "Should contain at least 20 Laws of UX")

        seen_ids = set()
        for law in laws:
            lid = law.get("id")
            self.assertTrue(lid, f"Law missing ID: {law}")
            self.assertNotIn(lid, seen_ids, f"Duplicate law ID: {lid}")
            seen_ids.add(lid)
            self.assertTrue(law.get("name"), f"Missing name in {lid}")
            self.assertTrue(law.get("summary"), f"Missing summary in {lid}")
            self.assertTrue(law.get("key_takeaways"), f"Missing key takeaways in {lid}")
            self.assertTrue(law.get("url", "").startswith("https://lawsofux.com/"), f"Invalid law URL: {law.get('url')}")

    def test_heuristics_integrity(self):
        heur_file = DATA_DIR / "heuristics.json"
        self.assertTrue(heur_file.is_file(), "heuristics.json missing")
        with open(heur_file, encoding="utf-8") as fh:
            data = json.load(fh)

        heuristics = data.get("heuristics", [])
        self.assertEqual(len(heuristics), 10, "NN/g Heuristics must contain exactly 10 heuristics")

        for i, h in enumerate(heuristics, 1):
            self.assertEqual(h.get("number"), i)
            self.assertTrue(h.get("id"))
            self.assertTrue(h.get("name"))
            self.assertTrue(h.get("summary"))
            self.assertGreaterEqual(len(h.get("checklist", [])), 3)

    def test_personas_integrity(self):
        personas_file = DATA_DIR / "personas.json"
        self.assertTrue(personas_file.is_file(), "personas.json missing")
        with open(personas_file, encoding="utf-8") as fh:
            data = json.load(fh)

        personas = data.get("personas", [])
        self.assertEqual(len(personas), 3, "Must have exactly 3 age personas (young, adult, senior)")

        pids = {p["id"] for p in personas}
        self.assertEqual(pids, {"young", "adult", "senior"})

        for p in personas:
            eth = p.get("ergonomic_thresholds", {})
            self.assertIn("min_touch_target_px", eth)
            self.assertIn("min_contrast_ratio", eth)
            self.assertIn("min_body_font_size_px", eth)


if __name__ == "__main__":
    unittest.main()
