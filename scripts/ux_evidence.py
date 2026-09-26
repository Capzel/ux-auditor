#!/usr/bin/env python3
"""Per-category UX evidence filter and extractor.
Gives specialist agents a focused slice of static scan signals and runtime data.
Standard library only, Python 3.8+.

Usage:
  python3 ux_evidence.py --category visual-hierarchy --evidence-dir ./evidence/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ux_common import CATEGORIES, load_json  # noqa: E402


def extract_evidence_for_category(
    category: str,
    evidence_dir: Path,
    persona_filter: Optional[str] = None
) -> Dict:
    """Extract and filter evidence items relevant to a single category."""
    out = {
        "category": category,
        "static_signals": [],
        "runtime_desktop": {},
        "runtime_mobile": {},
        "persona_insights": {}
    }

    # 1. Static Scan
    static_file = evidence_dir / "static-scan.json"
    if static_file.is_file():
        try:
            with open(static_file, encoding="utf-8") as fh:
                sdata = json.load(fh)
                signals = sdata.get("signals", [])
                out["static_signals"] = [s for s in signals if s.get("category") == category]
        except Exception as e:
            out["static_error"] = str(e)

    # 2. Runtime
    runtime_file = evidence_dir / "runtime.json"
    if runtime_file.is_file():
        try:
            with open(runtime_file, encoding="utf-8") as fh:
                rdata = json.load(fh)

                # Filter desktop targets
                d_pages = rdata.get("desktop", [])
                if d_pages:
                    dp = d_pages[0]
                    out["runtime_desktop"] = {
                        "url": dp.get("url"),
                        "small_targets_count": dp.get("small_targets_count"),
                        "low_contrast_count": dp.get("low_contrast_targets_count", 0) + dp.get("low_contrast_text_count", 0),
                        "targets": dp.get("targets", [])[:15],
                        "text_samples": dp.get("text_samples", [])[:10],
                    }

                # Filter mobile targets
                m_pages = rdata.get("mobile", [])
                if m_pages:
                    mp = m_pages[0]
                    out["runtime_mobile"] = {
                        "url": mp.get("url"),
                        "has_horizontal_overflow": mp.get("has_horizontal_overflow"),
                        "overflowing_elements": mp.get("overflowing_elements"),
                        "zoom_disabled": mp.get("zoom_disabled"),
                        "small_targets_count": mp.get("small_targets_count"),
                        "tight_spacing_count": mp.get("tight_spacing_count"),
                        "targets": mp.get("targets", [])[:15],
                    }

                # Personas
                out["persona_insights"] = rdata.get("personas", {})
                if persona_filter and persona_filter in out["persona_insights"]:
                    out["persona_insights"] = {persona_filter: out["persona_insights"][persona_filter]}

        except Exception as e:
            out["runtime_error"] = str(e)

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", required=True, choices=CATEGORIES, help="UX category name")
    parser.add_argument("--evidence-dir", required=True, help="Directory containing static-scan.json and runtime.json")
    parser.add_argument("--persona", choices=["young", "adult", "senior"], help="Filter by age persona")
    args = parser.parse_args()

    ev_dir = Path(args.evidence_dir).resolve()
    if not ev_dir.is_dir():
        print(f"error: evidence directory not found: {ev_dir}", file=sys.stderr)
        return 1

    ev = extract_evidence_for_category(args.category, ev_dir, args.persona)
    print(json.dumps(ev, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
