#!/usr/bin/env python3
"""Validate, merge, score and render UX audit results.
Standard library only, Python 3.8+.

Commands:
  check  FILE                      validate a findings fragment or full audit-data.json
  merge  --audit-dir DIR           combine DIR/meta.json + DIR/findings/*.json into DIR/audit-data.json
  render --data FILE [--out DIR]   generate UX-AUDIT-REPORT.md, ACTION-PLAN.md, personas-analysis.md, and ux-audit-report.html
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ux_common import (  # noqa: E402
    AGE_PERSONAS,
    CATEGORIES,
    CATEGORY_TITLES,
    CATEGORY_WEIGHTS,
    CONF_MULT,
    CONFIDENCES,
    EFFORT_RANK,
    EFFORTS,
    PREFIX,
    SEV_ICON,
    SEV_POINTS,
    SEV_RANK,
    SEVERITIES,
    STATUS_MULT,
    STATUS_RANK,
    STATUSES,
    TIERS,
    VIEWPORTS,
    get_heuristics_index,
    get_laws_index,
    get_personas_index,
    load_json,
    rating,
    rating_color,
)

VERSION = "1.0.0"


# --------------------------------------------------------------------------- #
# Validation Logic
# --------------------------------------------------------------------------- #

def validate_finding(
    f: Dict,
    where: str,
    laws_idx: Dict[str, dict],
    heuristics_idx: Dict[str, dict],
    personas_idx: Dict[str, dict],
    category: Optional[str]
) -> Tuple[List[str], List[str]]:
    """Validate schema compliance for a single finding."""
    errors, warnings = [], []

    def need(cond: bool, msg: str):
        if not cond:
            errors.append(f"{where}: {msg}")

    need(isinstance(f.get("title"), str) and f["title"].strip(), "title is required")
    need(f.get("status") in STATUSES, f"status must be one of {STATUSES}")
    need(f.get("severity") in SEVERITIES, f"severity must be one of {SEVERITIES}")
    need(f.get("confidence") in CONFIDENCES, f"confidence must be one of {CONFIDENCES}")
    need(f.get("evidence_tier") in TIERS, f"evidence_tier must be one of {TIERS}")

    cat = f.get("category") or category
    need(cat in CATEGORIES, f"category must be one of {CATEGORIES}")

    viewport = f.get("viewport") or "both"
    need(viewport in VIEWPORTS, f"viewport must be one of {VIEWPORTS}")

    if f.get("status") in ("fail", "warn"):
        need(isinstance(f.get("laws"), list) and f["laws"], "laws (from Laws of UX) are required for fail/warn")
        need(isinstance(f.get("heuristics"), list) and f["heuristics"], "heuristics (from NN/g 10) are required for fail/warn")
        need(isinstance(f.get("evidence"), list) and f["evidence"], "evidence is required for fail/warn")
        need(isinstance(f.get("impact"), str) and f["impact"].strip(), "impact is required for fail/warn")

        rem = f.get("remedy") or {}
        need(isinstance(rem, dict) and rem.get("summary"), "remedy.summary is required for fail/warn")
        need(isinstance(rem, dict) and rem.get("effort") in EFFORTS, "remedy.effort must be S, M or L")

        if f.get("severity") == "info":
            warnings.append(f"{where}: fail/warn finding with severity info will not affect the score")

    # Validate Laws of UX references
    for lid in f.get("laws", []):
        if lid not in laws_idx:
            errors.append(f"{where}: unknown law id '{lid}' (must be a valid id from data/laws_of_ux.json)")

    # Validate NN/g Heuristics references
    for hid in f.get("heuristics", []):
        if hid not in heuristics_idx:
            errors.append(f"{where}: unknown heuristic id '{hid}' (must be a valid id from data/heuristics.json)")

    # Validate evidence items
    for ev in f.get("evidence", []):
        need(
            isinstance(ev, dict) and (ev.get("file") or ev.get("note") or ev.get("url") or ev.get("selector")),
            "each evidence item needs file, url, selector, or note"
        )

    return errors, warnings


def validate_fragment(
    doc: Dict,
    where: str,
    laws_idx: Dict[str, dict],
    heuristics_idx: Dict[str, dict],
    personas_idx: Dict[str, dict]
) -> Tuple[List[str], List[str]]:
    """Validate a category fragment JSON."""
    errors, warnings = [], []
    if doc.get("category") not in CATEGORIES:
        errors.append(f"{where}: category must be one of {CATEGORIES}")
    if not isinstance(doc.get("findings"), list):
        errors.append(f"{where}: findings must be a list")
        return errors, warnings

    for i, f in enumerate(doc["findings"]):
        e, w = validate_finding(
            f, f"{where} findings[{i}]", laws_idx, heuristics_idx, personas_idx, doc.get("category")
        )
        errors.extend(e)
        warnings.extend(w)

    return errors, warnings


# --------------------------------------------------------------------------- #
# Scoring Calculations
# --------------------------------------------------------------------------- #

def calculate_category_score(findings: List[Dict]) -> float:
    """Calculate score out of 100 for a category based on deductions."""
    deductions = 0.0
    for f in findings:
        st = f.get("status")
        if st not in ("fail", "warn"):
            continue
        base = SEV_POINTS.get(f.get("severity", "info"), 0)
        c_mult = CONF_MULT.get(f.get("confidence", "likely"), 0.8)
        s_mult = STATUS_MULT.get(st, 1.0)
        deductions += base * c_mult * s_mult

    score = max(0.0, 100.0 - deductions)
    return round(score, 1)


def compute_audit_scores(doc: Dict) -> Dict:
    """Calculate overall, category, and age persona UX scores."""
    cat_scores = {}
    for cat in CATEGORIES:
        cat_findings = [f for f in doc.get("findings", []) if f.get("category") == cat]
        cat_scores[cat] = calculate_category_score(cat_findings)

    # Weighted overall score
    total_score = sum(cat_scores[cat] * (CATEGORY_WEIGHTS[cat] / 100.0) for cat in CATEGORIES)
    total_score = round(total_score, 1)

    # Calculate Heuristic adherence
    heuristics_idx = get_heuristics_index()
    heuristic_status = {}
    for hid in heuristics_idx:
        related_fails = [
            f for f in doc.get("findings", [])
            if hid in f.get("heuristics", []) and f.get("status") == "fail" and f.get("severity") in ("critical", "high")
        ]
        heuristic_status[hid] = "fail" if related_fails else "pass"

    passing_heuristics = sum(1 for st in heuristic_status.values() if st == "pass")
    heuristic_adherence_pct = round((passing_heuristics / len(heuristics_idx)) * 100, 1)

    # Calculate Persona scores
    persona_scores = {}
    for pid in ("young", "adult", "senior"):
        p_findings = [
            f for f in doc.get("findings", [])
            if pid in f.get("personas_affected", ["all"]) or "all" in f.get("personas_affected", ["all"])
        ]
        p_deductions = sum(
            SEV_POINTS.get(f.get("severity", "info"), 0) * CONF_MULT.get(f.get("confidence", "likely"), 0.8)
            for f in p_findings if f.get("status") in ("fail", "warn")
        )
        persona_scores[pid] = max(5.0, round(100.0 - (p_deductions * 0.7), 1))

    return {
        "overall_score": total_score,
        "rating": rating(total_score),
        "category_scores": cat_scores,
        "heuristic_adherence_pct": heuristic_adherence_pct,
        "passing_heuristics_count": passing_heuristics,
        "total_heuristics_count": len(heuristics_idx),
        "persona_scores": persona_scores,
    }


# --------------------------------------------------------------------------- #
# Merge Command
# --------------------------------------------------------------------------- #

def merge_audit(audit_dir: Path) -> int:
    """Merge meta.json and findings/*.json into audit-data.json."""
    meta_file = audit_dir / "meta.json"
    if not meta_file.is_file():
        print(f"error: meta.json not found in {audit_dir}", file=sys.stderr)
        return 1

    try:
        with open(meta_file, encoding="utf-8") as fh:
            meta = json.load(fh)
    except Exception as e:
        print(f"error reading {meta_file}: {e}", file=sys.stderr)
        return 1

    laws_idx = get_laws_index()
    heuristics_idx = get_heuristics_index()
    personas_idx = get_personas_index()

    findings_dir = audit_dir / "findings"
    if not findings_dir.is_dir():
        print(f"error: findings directory not found in {audit_dir}", file=sys.stderr)
        return 1

    all_findings = []
    all_errors = []
    all_warnings = []

    # Read fragments per category
    for cat in CATEGORIES:
        frag_file = findings_dir / f"{cat}.json"
        if not frag_file.is_file():
            continue
        try:
            with open(frag_file, encoding="utf-8") as fh:
                frag_data = json.load(fh)
            errs, warns = validate_fragment(frag_data, f"findings/{cat}.json", laws_idx, heuristics_idx, personas_idx)
            all_errors.extend(errs)
            all_warnings.extend(warns)
            for f in frag_data.get("findings", []):
                f["category"] = cat
                all_findings.append(f)
        except Exception as e:
            all_errors.append(f"findings/{cat}.json: JSON parse error: {e}")

    if all_errors:
        print(f"Merge aborted: {len(all_errors)} validation error(s) found:", file=sys.stderr)
        for err in all_errors:
            print(f"  ❌ {err}", file=sys.stderr)
        return 2

    # Assign deterministic IDs: VIS-001, ERG-001, etc.
    counts: Dict[str, int] = {}
    for f in all_findings:
        cat = f["category"]
        prefix = PREFIX.get(cat, "UX")
        counts[prefix] = counts.get(prefix, 0) + 1
        f["id"] = f"{prefix}-{counts[prefix]:03d}"

    # Sort findings by severity and category
    all_findings.sort(key=lambda f: (SEV_RANK.get(f.get("severity", "info"), 99), f["category"]))

    # Read evidence files if present
    evidence_meta = {}
    ev_dir = audit_dir / "evidence"
    if ev_dir.is_dir():
        static_f = ev_dir / "static-scan.json"
        runtime_f = ev_dir / "runtime.json"
        if static_f.is_file():
            try:
                with open(static_f, encoding="utf-8") as fh:
                    sdata = json.load(fh)
                    evidence_meta["static"] = {
                        "files_scanned": sdata.get("files_scanned"),
                        "stack": sdata.get("stack"),
                        "signals_count": len(sdata.get("signals", []))
                    }
            except Exception:
                pass
        if runtime_f.is_file():
            try:
                with open(runtime_f, encoding="utf-8") as fh:
                    rdata = json.load(fh)
                    evidence_meta["runtime"] = {
                        "base_url": rdata.get("base_url"),
                        "pages_tested": rdata.get("pages_tested"),
                        "personas": rdata.get("personas", {})
                    }
            except Exception:
                pass

    doc = {
        "version": VERSION,
        "meta": meta,
        "evidence_summary": evidence_meta,
        "findings": all_findings,
    }

    # Calculate scores
    scores = compute_audit_scores(doc)
    doc["scores"] = scores

    out_file = audit_dir / "audit-data.json"
    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)

    print(f"Successfully merged {len(all_findings)} findings into {out_file}")
    print(f"Overall UX Score: {scores['overall_score']}/100 [{scores['rating']}]")
    if all_warnings:
        print(f"Note: {len(all_warnings)} warning(s) were flagged during validation.")
    return 0


# --------------------------------------------------------------------------- #
# Markdown Renderers
# --------------------------------------------------------------------------- #

def render_markdown_report(data: Dict, laws_idx: Dict[str, dict], heuristics_idx: Dict[str, dict]) -> str:
    """Generate UX-AUDIT-REPORT.md."""
    meta = data.get("meta", {})
    scores = data.get("scores", {})
    findings = data.get("findings", [])

    lines = []
    lines.append(f"# UX Audit Report: {meta.get('project', 'Application')}")
    lines.append("")
    lines.append(f"**Date:** {meta.get('date', str(date.today()))} | **Auditor:** ux-auditor (Antigravity & Playwright)")
    lines.append(f"**Scope:** {meta.get('path', '.')} | **Audited URL:** {meta.get('url', 'Codebase static review')}")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(f"> **Overall Usability Score: {scores.get('overall_score', 0)}/100 — {scores.get('rating', 'Pending')}**  ")
    lines.append(f"> Evaluated against the **21 Laws of UX** (lawsofux.com) and **NN/g 10 Usability Heuristics** across Desktop and Mobile viewports.")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(meta.get("executive_summary", "This UX audit evaluates interaction ergonomics, cognitive load, mobile touch safety, navigation wayfinding, error resilience, and age cohort inclusivity."))
    lines.append("")

    # Scorecard Table
    lines.append("## Scorecard by UX Pillar")
    lines.append("")
    lines.append("| Pillar / Category | Weight | Score | Rating |")
    lines.append("|---|---|---|---|")
    for cat in CATEGORIES:
        score = scores.get("category_scores", {}).get(cat, 100.0)
        lines.append(f"| **{CATEGORY_TITLES.get(cat, cat)}** | {CATEGORY_WEIGHTS.get(cat, 0)}% | {score}/100 | {rating(score)} |")
    lines.append("")

    # Viewport & Persona Highlights
    p_scores = scores.get("persona_scores", {})
    lines.append("## Age Cohort & Viewport Friendliness")
    lines.append("")
    lines.append("| Age Cohort | Target Group | Usability Score | Key Considerations |")
    lines.append("|---|---|---|---|")
    lines.append(f"| **Digital Natives (13-24)** | Gen Z & Alpha | {p_scores.get('young', 'N/A')}/100 | Mobile-first thumb ergonomics, <300ms feedback latency, scannable layout |")
    lines.append(f"| **Working Adults (25-59)** | General Users & Pros | {p_scores.get('adult', 'N/A')}/100 | Keyboard efficiency, autofill compliance, cross-viewport consistency |")
    lines.append(f"| **Older Adults (60+)** | Seniors | {p_scores.get('senior', 'N/A')}/100 | Touch targets ≥48px, high contrast (≥7:1), explicit icon labels, zoom support |")
    lines.append("")

    # Findings Breakdown
    open_findings = [f for f in findings if f.get("status") in ("fail", "warn")]
    lines.append(f"## Detailed Findings ({len(open_findings)} Open Issues)")
    lines.append("")

    if not open_findings:
        lines.append("🎉 **No usability failures or warnings identified! The interface demonstrates excellent UX hygiene.**")
        return "\n".join(lines)

    for f in open_findings:
        sev = f.get("severity", "medium")
        icon = SEV_ICON.get(sev, "⚪")
        fid = f.get("id", "UX-001")
        title = f.get("title", "Issue")
        lines.append(f"### {icon} [{fid}] {title}")
        lines.append("")
        lines.append(f"- **Severity:** `{sev.upper()}` | **Status:** `{f.get('status', 'fail')}` | **Confidence:** `{f.get('confidence', 'likely')}`")
        lines.append(f"- **Category:** {CATEGORY_TITLES.get(f.get('category'), f.get('category'))} | **Viewport:** `{f.get('viewport', 'both')}`")
        lines.append(f"- **Personas Impacted:** {', '.join(f.get('personas_affected', ['all']))}")

        # Laws of UX citations
        laws_links = []
        for lid in f.get("laws", []):
            law_meta = laws_idx.get(lid, {})
            name = law_meta.get("name", lid)
            url = law_meta.get("url", "https://lawsofux.com/")
            laws_links.append(f"[{name}]({url})")
        if laws_links:
            lines.append(f"- **Laws of UX Cited:** {', '.join(laws_links)}")

        # NN/g Heuristics citations
        heuristics_links = []
        for hid in f.get("heuristics", []):
            h_meta = heuristics_idx.get(hid, {})
            num = h_meta.get("number", "")
            name = h_meta.get("name", hid)
            heuristics_links.append(f"#{num} {name}")
        if heuristics_links:
            lines.append(f"- **NN/g Heuristic:** {', '.join(heuristics_links)}")

        lines.append("")
        lines.append(f"**Why it matters:** {f.get('impact', 'Affects interaction clarity.')}")
        lines.append("")

        # Evidence
        lines.append("**Evidence:**")
        for ev in f.get("evidence", []):
            if ev.get("file"):
                lines.append(f"- File: `{ev.get('file')}:{ev.get('line', 1)}`")
                if ev.get("snippet"):
                    lines.append(f"  ```\n  {ev.get('snippet')}\n  ```")
            elif ev.get("selector"):
                lines.append(f"- DOM Selector: `{ev.get('selector')}` ({ev.get('note', '')})")
            elif ev.get("note"):
                lines.append(f"- Note: {ev.get('note')}")
        lines.append("")

        # Remedy
        rem = f.get("remedy", {})
        lines.append(f"**Remedy (Effort: `{rem.get('effort', 'M')}`):** {rem.get('summary', 'Improve implementation.')}")
        if rem.get("code"):
            lines.append(f"```\n{rem.get('code')}\n```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def render_action_plan(data: Dict) -> str:
    """Generate ACTION-PLAN.md."""
    meta = data.get("meta", {})
    findings = data.get("findings", [])
    open_findings = [f for f in findings if f.get("status") in ("fail", "warn")]

    # Sort into phases
    # Phase 0: Quick Wins (S effort, Critical or High)
    p0 = [f for f in open_findings if f.get("remedy", {}).get("effort") == "S" and f.get("severity") in ("critical", "high")]
    # Phase 1: High-Impact Ergonomics & Mobile (Remaining Critical & High)
    p1 = [f for f in open_findings if f not in p0 and f.get("severity") in ("critical", "high")]
    # Phase 2: Medium/Low Polish & Quality-of-Life (Medium/Low)
    p2 = [f for f in open_findings if f not in p0 and f not in p1]

    lines = []
    lines.append(f"# UX Action Plan: {meta.get('project', 'Application')}")
    lines.append("")
    lines.append("Prioritized, phased checklist to resolve usability friction, improve mobile ergonomics, and align with the Laws of UX.")
    lines.append("")

    lines.append("## Phase 1: Immediate Quick Wins (P0 — High Impact, Low Effort)")
    lines.append("")
    if p0:
        for f in p0:
            lines.append(f"- [ ] **[{f.get('id')}] {f.get('title')}** (Effort: `{f.get('remedy', {}).get('effort')}`)  ")
            lines.append(f"  *Fix:* {f.get('remedy', {}).get('summary')}  ")
            lines.append(f"  *Target:* Viewport: `{f.get('viewport')}` | Personas: `{', '.join(f.get('personas_affected', ['all']))}`")
    else:
        lines.append("- [x] No immediate low-effort critical blockers identified.")
    lines.append("")

    lines.append("## Phase 2: Core Interaction & Mobile Ergonomics (P1 — Next Sprint)")
    lines.append("")
    if p1:
        for f in p1:
            lines.append(f"- [ ] **[{f.get('id')}] {f.get('title')}** (Effort: `{f.get('remedy', {}).get('effort')}`)  ")
            lines.append(f"  *Fix:* {f.get('remedy', {}).get('summary')}  ")
            lines.append(f"  *Target:* Viewport: `{f.get('viewport')}` | Personas: `{', '.join(f.get('personas_affected', ['all']))}`")
    else:
        lines.append("- [x] No outstanding P1 interaction defects.")
    lines.append("")

    lines.append("## Phase 3: Visual Polish & Progressive Enhancement (P2 — Ongoing Improvements)")
    lines.append("")
    if p2:
        for f in p2:
            lines.append(f"- [ ] **[{f.get('id')}] {f.get('title')}** (Effort: `{f.get('remedy', {}).get('effort')}`)  ")
            lines.append(f"  *Fix:* {f.get('remedy', {}).get('summary')}  ")
            lines.append(f"  *Target:* Viewport: `{f.get('viewport')}` | Personas: `{', '.join(f.get('personas_affected', ['all']))}`")
    else:
        lines.append("- [x] No remaining visual polish tasks.")
    lines.append("")

    return "\n".join(lines)


def render_personas_analysis(data: Dict, personas_idx: Dict[str, dict]) -> str:
    """Generate personas-analysis.md."""
    scores = data.get("scores", {})
    p_scores = scores.get("persona_scores", {})
    findings = data.get("findings", [])

    lines = []
    lines.append("# Age Cohort UX Simulation & Inclusivity Analysis")
    lines.append("")
    lines.append("Evaluation of user experience across three demographic generations with distinct physiological, ergonomic, and cognitive needs.")
    lines.append("")

    for pid in ("young", "adult", "senior"):
        p = personas_idx.get(pid, {})
        score = p_scores.get(pid, 85.0)
        lines.append(f"## {p.get('name', pid)} (Ages {p.get('age_range')})")
        lines.append("")
        lines.append(f"**Cohort Score:** `{score}/100` ({rating(score)})  ")
        lines.append(f"**Profile:** {p.get('tagline', '')}  ")
        lines.append(f"**Summary:** {p.get('demographics_summary', '')}")
        lines.append("")

        lines.append("### Key Ergonomic Benchmarks")
        lines.append("")
        eth = p.get("ergonomic_thresholds", {})
        lines.append(f"- **Minimum Touch Target Size:** `{eth.get('min_touch_target_px')}px` (Recommended: `{eth.get('recommended_touch_target_px')}px`)")
        lines.append(f"- **Target-to-Target Spacing:** Minimum `{eth.get('min_target_spacing_px')}px` to avoid mistaps")
        lines.append(f"- **Body Font Size:** Minimum `{eth.get('min_body_font_size_px')}px`")
        lines.append(f"- **Minimum Contrast Ratio:** `{eth.get('min_contrast_ratio')}:1`")
        lines.append(f"- **Max Acceptable Response Time:** `<{eth.get('max_unsupported_doherty_ms')}ms`")
        lines.append("")

        # Findings affecting this persona
        affecting = [
            f for f in findings
            if f.get("status") in ("fail", "warn") and (pid in f.get("personas_affected", []) or "all" in f.get("personas_affected", []))
        ]
        lines.append(f"### Specific Friction Points Encountered ({len(affecting)} issues)")
        lines.append("")
        if affecting:
            for f in affecting[:5]:
                lines.append(f"- **[{f.get('id')}] {f.get('title')}** ({f.get('severity').upper()}): {f.get('impact')}")
        else:
            lines.append("✅ No critical friction points specifically impacting this cohort.")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Standalone Interactive HTML Renderer
# --------------------------------------------------------------------------- #

def render_html_report(data: Dict, laws_idx: Dict[str, dict], heuristics_idx: Dict[str, dict]) -> str:
    """Generate standalone interactive HTML report with charts and print styles."""
    meta = data.get("meta", {})
    scores = data.get("scores", {})
    findings = data.get("findings", [])
    overall = scores.get("overall_score", 0)

    # Convert data into safe JSON for frontend script
    data_json_str = json.dumps(data).replace("</script>", "<\\/script>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UX Audit Report — {html.escape(meta.get('project', 'App'))}</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --text-muted: #64748b;
      --primary: #4f46e5;
      --primary-light: #eef2ff;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --info: #3b82f6;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    header {{
      background: var(--card-bg);
      padding: 32px;
      border-radius: 12px;
      border: 1px solid var(--border);
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .header-top {{ display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; }}
    h1 {{ font-size: 28px; font-weight: 700; color: #1e293b; }}
    .meta-tags {{ margin-top: 8px; font-size: 14px; color: var(--text-muted); display: flex; gap: 16px; flex-wrap: wrap; }}
    .score-badge {{
      display: inline-flex;
      flex-direction: column;
      align-items: center;
      background: #f1f5f9;
      padding: 12px 24px;
      border-radius: 12px;
      border: 2px solid {rating_color(overall)};
    }}
    .score-num {{ font-size: 44px; font-weight: 800; color: {rating_color(overall)}; line-height: 1; }}
    .score-label {{ font-size: 13px; font-weight: 600; text-transform: uppercase; margin-top: 4px; color: var(--text-muted); }}

    .grid-summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .card {{
      background: var(--card-bg);
      padding: 24px;
      border-radius: 12px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .card-title {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #334155; display: flex; justify-content: space-between; }}

    .bar-row {{ margin-bottom: 12px; }}
    .bar-label {{ display: flex; justify-content: space-between; font-size: 13px; font-weight: 500; margin-bottom: 4px; }}
    .bar-bg {{ background: #e2e8f0; height: 8px; border-radius: 4px; overflow: hidden; }}
    .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s ease; }}

    /* Filters */
    .filter-bar {{
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      flex-wrap: wrap;
      background: var(--card-bg);
      padding: 16px;
      border-radius: 8px;
      border: 1px solid var(--border);
    }}
    .filter-btn {{
      background: #f1f5f9;
      border: 1px solid var(--border);
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      color: #475569;
      transition: all 0.2s;
    }}
    .filter-btn.active {{ background: var(--primary); color: #fff; border-color: var(--primary); }}

    /* Finding Item */
    .finding-card {{
      background: var(--card-bg);
      border-radius: 8px;
      border: 1px solid var(--border);
      padding: 20px;
      margin-bottom: 16px;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .finding-card:hover {{ box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); }}
    .finding-header {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }}
    .finding-title {{ font-size: 17px; font-weight: 600; }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .badge-critical {{ background: #fee2e2; color: #b91c1c; }}
    .badge-high {{ background: #ffedd5; color: #c2410c; }}
    .badge-medium {{ background: #fef3c7; color: #b45309; }}
    .badge-low {{ background: #e0f2fe; color: #0369a1; }}
    .tag-law {{ background: #f3e8ff; color: #6b21a8; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; text-decoration: none; }}
    .tag-heuristic {{ background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }}
    .tag-persona {{ background: #f1f5f9; color: #334155; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }}

    .finding-body {{ font-size: 14px; margin-top: 10px; color: #334155; }}
    .code-box {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 12px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 12px;
      overflow-x: auto;
      margin: 8px 0;
    }}
    .remedy-box {{
      background: #f0fdf4;
      border-left: 4px solid var(--success);
      padding: 12px;
      border-radius: 4px;
      font-size: 13px;
      margin-top: 12px;
    }}

    @media print {{
      body {{ background: #fff; padding: 0; }}
      .filter-bar {{ display: none; }}
      .card, .finding-card {{ break-inside: avoid; border: 1px solid #ccc; box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-top">
        <div>
          <h1>UX Audit Report — {html.escape(meta.get('project', 'Application'))}</h1>
          <div class="meta-tags">
            <span>📅 {html.escape(meta.get('date', str(date.today())))}</span>
            <span>📱 Desktop & Mobile Viewports</span>
            <span>🎯 21 Laws of UX + NN/g 10 Heuristics</span>
            <span>👥 Gen Z, Adult, Senior Simulation</span>
          </div>
        </div>
        <div class="score-badge">
          <div class="score-num">{overall}</div>
          <div class="score-label">{rating(overall)}</div>
        </div>
      </div>
      <p style="margin-top: 16px; color: var(--text-muted); font-size: 14px;">
        {html.escape(meta.get('executive_summary', 'Automated and expert technical UX audit measuring cognitive friction, touch ergonomics, and WCAG accessibility standards.'))}
      </p>
    </header>

    <div class="grid-summary">
      <div class="card">
        <div class="card-title">Pillars & Category Scores</div>
        { "".join(f'''
        <div class="bar-row">
          <div class="bar-label">
            <span>{CATEGORY_TITLES.get(cat, cat)}</span>
            <span>{scores.get('category_scores', {}).get(cat, 100)}%</span>
          </div>
          <div class="bar-bg">
            <div class="bar-fill" style="width: {scores.get('category_scores', {}).get(cat, 100)}%; background: {rating_color(scores.get('category_scores', {}).get(cat, 100))};"></div>
          </div>
        </div>''' for cat in CATEGORIES) }
      </div>

      <div class="card">
        <div class="card-title">Age Cohort Friendliness</div>
        { "".join(f'''
        <div class="bar-row">
          <div class="bar-label">
            <span>{pid.capitalize()} ({'60+ Seniors' if pid == 'senior' else ('13-24 Gen Z' if pid == 'young' else '25-59 Adults')})</span>
            <span>{scores.get('persona_scores', {}).get(pid, 90)}%</span>
          </div>
          <div class="bar-bg">
            <div class="bar-fill" style="width: {scores.get('persona_scores', {}).get(pid, 90)}%; background: {rating_color(scores.get('persona_scores', {}).get(pid, 90))};"></div>
          </div>
        </div>''' for pid in ('young', 'adult', 'senior')) }
        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border); font-size: 13px; color: var(--text-muted);">
          <strong>Heuristic Adherence:</strong> {scores.get('heuristic_adherence_pct', 100)}% of NN/g Heuristics satisfied without severe defects.
        </div>
      </div>
    </div>

    <div class="filter-bar">
      <span style="font-size: 13px; font-weight: 600; align-self: center; margin-right: 8px;">Filter by:</span>
      <button class="filter-btn active" onclick="filterFindings('all')">All Findings ({len(findings)})</button>
      <button class="filter-btn" onclick="filterFindings('mobile')">Mobile Only</button>
      <button class="filter-btn" onclick="filterFindings('desktop')">Desktop Only</button>
      <button class="filter-btn" onclick="filterFindings('senior')">Seniors (60+)</button>
      <button class="filter-btn" onclick="filterFindings('young')">Gen Z / Mobile</button>
      <button class="filter-btn" onclick="window.print()" style="margin-left: auto; background: #fff;">🖨️ Print / PDF</button>
    </div>

    <div id="findings-container">
      { "".join(f'''
      <div class="finding-card" data-viewport="{f.get('viewport', 'both')}" data-personas="{','.join(f.get('personas_affected', ['all']))}">
        <div class="finding-header">
          <div class="finding-title">
            <span class="badge badge-{f.get('severity', 'medium')}">{f.get('severity')}</span>
            <strong>[{f.get('id', 'UX')}]</strong> {html.escape(f.get('title', ''))}
          </div>
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            {''.join(f'<a href="{laws_idx.get(lid, {}).get("url", "https://lawsofux.com/")}" target="_blank" class="tag-law">{laws_idx.get(lid, {}).get("name", lid)}</a>' for lid in f.get('laws', []))}
            {''.join(f'<span class="tag-heuristic">#{heuristics_idx.get(hid, {}).get("number", "")} {heuristics_idx.get(hid, {}).get("name", hid)}</span>' for hid in f.get('heuristics', []))}
            <span class="tag-persona">📱 {f.get('viewport', 'both')}</span>
          </div>
        </div>
        <div class="finding-body">
          <p><strong>Impact:</strong> {html.escape(f.get('impact', ''))}</p>
          {''.join(f'<div class="code-box"><code>{html.escape(ev.get("file", ""))}:{ev.get("line", 1)}<br>{html.escape(ev.get("snippet", ev.get("note", "")))}</code></div>' for ev in f.get('evidence', []))}
          <div class="remedy-box">
            <strong>Actionable Remedy (Effort: {f.get('remedy', {}).get('effort', 'M')}):</strong> {html.escape(f.get('remedy', {}).get('summary', ''))}
          </div>
        </div>
      </div>''' for f in findings if f.get('status') in ('fail', 'warn')) }
    </div>
  </div>

  <script>
    const auditData = {data_json_str};

    function filterFindings(type) {{
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');

      const cards = document.querySelectorAll('.finding-card');
      cards.forEach(card => {{
        const vp = card.getAttribute('data-viewport');
        const personas = card.getAttribute('data-personas').split(',');

        if (type === 'all') {{
          card.style.display = 'block';
        }} else if (type === 'mobile' || type === 'desktop') {{
          card.style.display = (vp === type || vp === 'both') ? 'block' : 'none';
        }} else if (type === 'senior' || type === 'young') {{
          card.style.display = (personas.includes(type) || personas.includes('all')) ? 'block' : 'none';
        }}
      }});
    }}
  </script>
</body>
</html>
"""


def render_all_reports(audit_data_file: Path, out_dir: Optional[Path] = None) -> int:
    """Render markdown, action plan, personas, and HTML reports from audit-data.json."""
    if not audit_data_file.is_file():
        print(f"error: audit data file not found: {audit_data_file}", file=sys.stderr)
        return 1

    try:
        with open(audit_data_file, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        print(f"error reading {audit_data_file}: {e}", file=sys.stderr)
        return 1

    laws_idx = get_laws_index()
    heuristics_idx = get_heuristics_index()
    personas_idx = get_personas_index()

    dest = out_dir or audit_data_file.parent
    dest.mkdir(parents=True, exist_ok=True)

    # 1. UX-AUDIT-REPORT.md
    report_md = render_markdown_report(data, laws_idx, heuristics_idx)
    (dest / "UX-AUDIT-REPORT.md").write_text(report_md, encoding="utf-8")

    # 2. ACTION-PLAN.md
    action_plan_md = render_action_plan(data)
    (dest / "ACTION-PLAN.md").write_text(action_plan_md, encoding="utf-8")

    # 3. personas-analysis.md
    personas_md = render_personas_analysis(data, personas_idx)
    (dest / "personas-analysis.md").write_text(personas_md, encoding="utf-8")

    # 4. ux-audit-report.html
    report_html = render_html_report(data, laws_idx, heuristics_idx)
    (dest / "ux-audit-report.html").write_text(report_html, encoding="utf-8")

    print(f"Generated deliverables in {dest}:")
    print("  • UX-AUDIT-REPORT.md")
    print("  • ACTION-PLAN.md")
    print("  • personas-analysis.md")
    print("  • ux-audit-report.html (Interactive standalone report with PDF printing)")
    return 0


# --------------------------------------------------------------------------- #
# CLI Entrypoint
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")

    # check
    check_p = sub.add_parser("check", help="Validate a findings fragment or audit-data.json")
    check_p.add_argument("file", help="JSON file to validate")

    # merge
    merge_p = sub.add_parser("merge", help="Merge meta.json and findings into audit-data.json")
    merge_p.add_argument("--audit-dir", required=True, help="Directory containing meta.json and findings/")

    # render
    render_p = sub.add_parser("render", help="Render Markdown and HTML audit reports")
    render_p.add_argument("--data", required=True, help="Path to audit-data.json")
    render_p.add_argument("--out", help="Output directory for reports (default: same as --data)")

    args = parser.parse_args()

    if args.command == "check":
        p = Path(args.file).resolve()
        if not p.is_file():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 1
        with open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
        laws_idx = get_laws_index()
        heuristics_idx = get_heuristics_index()
        personas_idx = get_personas_index()

        if "meta" in doc and "findings" in doc:
            # Audit file
            errs, warns = [], []
            for i, f in enumerate(doc["findings"]):
                e, w = validate_finding(f, f"findings[{i}]", laws_idx, heuristics_idx, personas_idx, f.get("category"))
                errs.extend(e)
                warns.extend(w)
        else:
            # Fragment file
            errs, warns = validate_fragment(doc, p.name, laws_idx, heuristics_idx, personas_idx)

        for w in warns:
            print(f"⚠️  {w}")
        for e in errs:
            print(f"❌ {e}", file=sys.stderr)

        if errs:
            print(f"\nValidation failed with {len(errs)} error(s).", file=sys.stderr)
            return 2
        print(f"✅ {p.name} passed validation cleanly.")
        return 0

    elif args.command == "merge":
        return merge_audit(Path(args.audit_dir).resolve())

    elif args.command == "render":
        data_file = Path(args.data).resolve()
        out_dir = Path(args.out).resolve() if args.out else None
        return render_all_reports(data_file, out_dir)

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
