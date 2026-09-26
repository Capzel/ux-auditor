"""Test runtime evaluation mathematics, WCAG contrast, and cohort simulation."""
from __future__ import annotations

import unittest

from scripts.ux_common import (
    calculate_contrast_ratio,
    evaluate_touch_target,
    parse_css_color,
    rating,
)
from scripts.ux_runtime import simulate_age_cohort


class TestUXRuntime(unittest.TestCase):
    def test_css_color_parser(self):
        self.assertEqual(parse_css_color("#ffffff"), (255, 255, 255))
        self.assertEqual(parse_css_color("#000"), (0, 0, 0))
        self.assertEqual(parse_css_color("rgb(10, 20, 30)"), (10, 20, 30))
        self.assertEqual(parse_css_color("rgba(10, 20, 30, 0.5)"), (10, 20, 30))
        self.assertEqual(parse_css_color("white"), (255, 255, 255))

    def test_contrast_ratio_wcag(self):
        # Black on white = 21:1
        ratio = calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
        self.assertAlmostEqual(ratio, 21.0, places=1)

        # White on white = 1:1
        ratio_same = calculate_contrast_ratio((255, 255, 255), (255, 255, 255))
        self.assertAlmostEqual(ratio_same, 1.0, places=1)

        # Faint gray (#9ca3af = 156, 163, 175) on white fails WCAG 4.5:1
        faint_gray = (156, 163, 175)
        faint_ratio = calculate_contrast_ratio(faint_gray, (255, 255, 255))
        self.assertLess(faint_ratio, 4.5, "Faint gray on white should be < 4.5:1")

    def test_touch_target_evaluation(self):
        # 30x30 with 4px spacing fails
        res_fail = evaluate_touch_target(30.0, 30.0, spacing=4.0, persona="adult")
        self.assertFalse(res_fail["is_compliant"])
        self.assertEqual(res_fail["status"], "fail")

        # 48x48 with 10px spacing passes
        res_pass = evaluate_touch_target(48.0, 48.0, spacing=10.0, persona="adult")
        self.assertTrue(res_pass["is_compliant"])
        self.assertIn(res_pass["status"], ("pass", "warn"))

        # Senior requires min 48px and spacing >= 12px
        res_senior = evaluate_touch_target(44.0, 44.0, spacing=8.0, persona="senior")
        self.assertFalse(res_senior["is_compliant"], "44px is below senior 48px threshold")

    def test_simulate_age_cohort(self):
        fake_desktop = {
            "targets": [
                {
                    "selector": "button.tiny",
                    "text": "X",
                    "rect": {"width": 24, "height": 24},
                    "spacing_to_neighbor": 2,
                    "contrast_ratio": 2.2,
                    "isIconButton": True,
                    "hasLabel": True
                }
            ],
            "text_samples": [
                {"tag": "p", "text": "Terms and conditions", "fontSize": 12, "contrast_ratio": 2.0}
            ]
        }
        fake_mobile = fake_desktop

        sim_senior = simulate_age_cohort(fake_desktop, fake_mobile, "senior")
        self.assertEqual(sim_senior["persona_id"], "senior")
        self.assertLess(sim_senior["usability_score"], 80)
        self.assertGreater(sim_senior["friction_triggers_count"], 0)


if __name__ == "__main__":
    unittest.main()
