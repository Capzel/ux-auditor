#!/usr/bin/env python3
"""Runtime UX inspector with Playwright.
Performs headless browser audits across Desktop and Mobile viewports,
inspecting Fitts's Law touch targets, color contrast, typography,
horizontal overflow, form labels, and age cohort ergonomics.

Requires: pip install playwright && python -m playwright install chromium

Usage:
  python3 ux_runtime.py --url http://localhost:3000 [--pages / /signup]
                        [--output runtime.json] [--screenshots DIR]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ux_common import (  # noqa: E402
    DESKTOP_VIEWPORT,
    MOBILE_VIEWPORT,
    calculate_contrast_ratio,
    evaluate_touch_target,
    load_json,
    parse_css_color,
)

VERSION = "1.0.0"

# Client-side JavaScript evaluation script to inspect real rendered DOM
DOM_INSPECTOR_JS = """
() => {
  const norm = s => (s || '').replace(/\\s+/g, ' ').trim();
  const winW = window.innerWidth;
  const winH = window.innerHeight;

  // 1. Viewport & Overflow checks
  const docW = document.documentElement.scrollWidth;
  const hasHorizontalScroll = docW > winW + 2;

  const metaViewport = document.querySelector('meta[name="viewport"]');
  const viewportContent = metaViewport ? metaViewport.getAttribute('content') || '' : '';
  const zoomDisabled = /user-scalable\\s*=\\s*(no|0)|maximum-scale\\s*=\\s*1(\\.0)?/i.test(viewportContent);

  // 2. Identify elements causing horizontal overflow
  const overflowingElements = [];
  if (hasHorizontalScroll) {
    const allEls = document.querySelectorAll('*');
    for (const el of allEls) {
      const r = el.getBoundingClientRect();
      if (r.right > winW + 5 && r.width > 0 && r.height > 0) {
        const tag = el.tagName.toLowerCase();
        const id = el.id ? '#' + el.id : '';
        const cls = el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').slice(0, 2).join('.') : '';
        overflowingElements.push({
          selector: `${tag}${id}${cls}`,
          width: Math.round(r.width),
          right: Math.round(r.right),
          excess: Math.round(r.right - winW)
        });
        if (overflowingElements.length >= 5) break;
      }
    }
  }

  // Helper to determine effective background color through DOM tree
  function getEffectiveBg(el) {
    let cur = el;
    while (cur && cur !== document.documentElement) {
      const bg = window.getComputedStyle(cur).backgroundColor;
      if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
        return bg;
      }
      cur = cur.parentElement;
    }
    return 'rgb(255, 255, 255)'; // Default white background
  }

  // 3. Interactive Elements (Touch Targets, Contrast, Labels)
  const interactiveSelector = 'button, a[href], input, select, textarea, [role="button"], [role="link"], [tabindex]:not([tabindex="-1"])';
  const interactiveEls = Array.from(document.querySelectorAll(interactiveSelector));

  const targets = [];
  for (let i = 0; i < interactiveEls.length; i++) {
    const el = interactiveEls[i];
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
      continue;
    }

    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    // Skip elements outside standard viewport fold if too many
    if (targets.length > 100) break;

    const text = norm(el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('title') || '');
    const tag = el.tagName.toLowerCase();
    const id = el.id ? '#' + el.id : '';
    const cls = el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').slice(0, 2).join('.') : '';
    const selector = `${tag}${id}${cls}` || tag;

    // Accessibility check: Icon button without accessible name
    const isIconButton = (tag === 'button' || el.getAttribute('role') === 'button') &&
      !text && (el.querySelector('svg, i, img') !== null);

    // Form label check
    let hasLabel = true;
    if (['input', 'select', 'textarea'].includes(tag)) {
      const inputType = el.getAttribute('type');
      if (!['hidden', 'submit', 'button', 'image'].includes(inputType)) {
        const hasAria = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby');
        const id = el.id;
        const hasExplicitLabel = id && document.querySelector(`label[for="${id}"]`);
        const hasParentLabel = el.closest('label');
        if (!hasAria && !hasExplicitLabel && !hasParentLabel) {
          hasLabel = false;
        }
      }
    }

    // Spacing to nearest interactive neighbor
    let minDistance = 999;
    for (let j = 0; j < Math.min(interactiveEls.length, 60); j++) {
      if (i === j) continue;
      const other = interactiveEls[j];
      const or = other.getBoundingClientRect();
      if (or.width <= 0 || or.height <= 0) continue;

      // Distance between rectangles
      const dx = Math.max(0, Math.max(r.left - or.right, or.left - r.right));
      const dy = Math.max(0, Math.max(r.top - or.bottom, or.top - r.bottom));
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < minDistance) {
        minDistance = dist;
      }
    }

    // Color contrast
    const fgColor = style.color;
    const bgColor = getEffectiveBg(el);
    const fontSize = parseFloat(style.fontSize) || 16;
    const lineHeight = parseFloat(style.lineHeight) || 20;

    targets.push({
      selector,
      text: text.slice(0, 40),
      tag,
      rect: {
        width: Math.round(r.width * 10) / 10,
        height: Math.round(r.height * 10) / 10,
        top: Math.round(r.top),
        left: Math.round(r.left)
      },
      spacing_to_neighbor: Math.round(minDistance * 10) / 10,
      styles: {
        color: fgColor,
        background: bgColor,
        fontSize: Math.round(fontSize * 10) / 10,
        lineHeight: Math.round(lineHeight * 10) / 10,
        outline: style.outlineStyle
      },
      hasLabel,
      isIconButton,
      type: el.getAttribute('type') || null,
      autocomplete: el.getAttribute('autocomplete') || null
    });
  }

  // 4. General Typography & Content Contrast sample
  const textElements = Array.from(document.querySelectorAll('p, h1, h2, h3, h4, span, li, dt, dd'));
  const textSamples = [];
  for (const el of textElements.slice(0, 40)) {
    const text = norm(el.innerText);
    if (!text || text.length < 5) continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;

    const style = window.getComputedStyle(el);
    textSamples.push({
      tag: el.tagName.toLowerCase(),
      text: text.slice(0, 50),
      color: style.color,
      background: getEffectiveBg(el),
      fontSize: parseFloat(style.fontSize) || 16,
      lineHeight: parseFloat(style.lineHeight) || 20
    });
    if (textSamples.length >= 15) break;
  }

  // 5. Performance Navigation Timing
  const nav = performance.getEntriesByType('navigation')[0] || {};
  const timing = {
    dns_time_ms: nav.domainLookupEnd ? Math.round(nav.domainLookupEnd - nav.domainLookupStart) : null,
    ttfb_ms: nav.responseStart ? Math.round(nav.responseStart - nav.requestStart) : null,
    dom_interactive_ms: nav.domInteractive ? Math.round(nav.domInteractive) : null,
    dom_content_loaded_ms: nav.domContentLoadedEventEnd ? Math.round(nav.domContentLoadedEventEnd) : null
  };

  return {
    viewport: { width: winW, height: winH },
    hasHorizontalScroll,
    zoomDisabled,
    overflowingElements,
    targets,
    textSamples,
    timing
  };
}
"""


def evaluate_page_in_viewport(
    page,
    url: str,
    viewport_name: str,
    screenshots_dir: Optional[Path],
    page_slug: str,
    wait_ms: int = 1500,
) -> Dict:
    """Inspect page in current Playwright context and extract metrics."""
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
    except Exception:
        # Fallback to load state
        try:
            page.goto(url, wait_until="load", timeout=15000)
        except Exception as e:
            return {"error": f"Failed to load {url}: {e}"}

    time.sleep(wait_ms / 1000.0)

    # Take screenshot if requested
    screenshot_path = None
    if screenshots_dir:
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        img_file = screenshots_dir / f"{viewport_name}-{page_slug}.png"
        try:
            page.screenshot(path=str(img_file), full_page=True)
            screenshot_path = str(img_file)
        except Exception:
            pass

    # Run client-side DOM inspector
    dom_data = page.evaluate(DOM_INSPECTOR_JS)

    # Process touch targets and color contrast with python mathematics
    processed_targets = []
    small_targets_count = 0
    tight_spacing_count = 0
    low_contrast_targets = 0

    for t in dom_data.get("targets", []):
        r = t["rect"]
        spacing = t.get("spacing_to_neighbor", 99)
        eval_res = evaluate_touch_target(r["width"], r["height"], spacing, persona="adult")

        # Contrast evaluation
        fg = parse_css_color(t["styles"].get("color", ""))
        bg = parse_css_color(t["styles"].get("background", ""))
        contrast_ratio = calculate_contrast_ratio(fg, bg) if (fg and bg) else None

        t["evaluation"] = eval_res
        t["contrast_ratio"] = contrast_ratio

        if not eval_res["is_compliant"]:
            small_targets_count += 1
        if not eval_res["spacing_compliant"]:
            tight_spacing_count += 1
        if contrast_ratio is not None and contrast_ratio < 4.5:
            low_contrast_targets += 1

        processed_targets.append(t)

    # Process text samples for contrast and font sizes
    processed_text = []
    low_contrast_text_count = 0
    small_font_count = 0

    for ts in dom_data.get("textSamples", []):
        fg = parse_css_color(ts.get("color", ""))
        bg = parse_css_color(ts.get("background", ""))
        ratio = calculate_contrast_ratio(fg, bg) if (fg and bg) else None
        ts["contrast_ratio"] = ratio

        if ratio is not None and ratio < 4.5:
            low_contrast_text_count += 1
        if ts.get("fontSize", 16) < 14:
            small_font_count += 1
        processed_text.append(ts)

    return {
        "url": url,
        "viewport": viewport_name,
        "viewport_size": dom_data.get("viewport"),
        "screenshot": screenshot_path,
        "has_horizontal_overflow": dom_data.get("hasHorizontalScroll", False),
        "overflowing_elements": dom_data.get("overflowingElements", []),
        "zoom_disabled": dom_data.get("zoomDisabled", False),
        "timing": dom_data.get("timing", {}),
        "targets_evaluated": len(processed_targets),
        "small_targets_count": small_targets_count,
        "tight_spacing_count": tight_spacing_count,
        "low_contrast_targets_count": low_contrast_targets,
        "text_samples_evaluated": len(processed_text),
        "low_contrast_text_count": low_contrast_text_count,
        "small_font_count": small_font_count,
        "targets": processed_targets,
        "text_samples": processed_text,
    }


def simulate_age_cohort(desktop_data: Dict, mobile_data: Dict, persona_id: str) -> Dict:
    """Analyze findings through the lens of a specific age cohort."""
    personas = {p["id"]: p for p in load_json("personas.json")["personas"]}
    persona = personas.get(persona_id)
    if not persona:
        return {}

    thresholds = persona["ergonomic_thresholds"]
    min_touch = thresholds["min_touch_target_px"]
    min_spacing = thresholds["min_target_spacing_px"]
    min_font = thresholds["min_body_font_size_px"]
    min_contrast = thresholds["min_contrast_ratio"]

    # Combine mobile targets (mobile ergonomics) and desktop targets
    all_targets = mobile_data.get("targets", []) or desktop_data.get("targets", [])
    all_texts = mobile_data.get("text_samples", []) or desktop_data.get("text_samples", [])

    failing_targets = []
    for t in all_targets:
        r = t["rect"]
        spacing = t.get("spacing_to_neighbor", 99)
        c_ratio = t.get("contrast_ratio")

        reasons = []
        if r["width"] < min_touch or r["height"] < min_touch:
            reasons.append(f"Target size ({r['width']}x{r['height']}px) below {min_touch}px minimum")
        if spacing < min_spacing:
            reasons.append(f"Spacing to neighbor ({spacing}px) below {min_spacing}px minimum")
        if c_ratio is not None and c_ratio < min_contrast:
            reasons.append(f"Contrast ratio ({c_ratio}:1) below {min_contrast}:1 threshold")
        if t.get("isIconButton"):
            reasons.append("Unlabelled icon button creates cognitive uncertainty")
        if not t.get("hasLabel"):
            reasons.append("Form field missing persistent label")

        if reasons:
            failing_targets.append({
                "selector": t["selector"],
                "text": t["text"],
                "rect": r,
                "reasons": reasons
            })

    # Typography checks
    failing_texts = []
    for txt in all_texts:
        fs = txt.get("fontSize", 16)
        cr = txt.get("contrast_ratio")
        reasons = []
        if fs < min_font:
            reasons.append(f"Font size ({fs}px) below {min_font}px threshold")
        if cr is not None and cr < min_contrast:
            reasons.append(f"Text contrast ({cr}:1) below {min_contrast}:1 threshold")
        if reasons:
            failing_texts.append({
                "tag": txt["tag"],
                "text": txt["text"],
                "reasons": reasons
            })

    # Cohort friction calculation (0 to 100; 100 is friction-free)
    target_weight = 15 if persona_id == "senior" else 10
    text_weight = 10 if persona_id == "senior" else 8
    friction_penalty = min(85, len(failing_targets) * target_weight + len(failing_texts) * text_weight)
    if persona_id == "senior" and (mobile_data.get("zoom_disabled") or desktop_data.get("zoom_disabled")):
        friction_penalty = min(95, friction_penalty + 25)
    if mobile_data.get("has_horizontal_overflow"):
        friction_penalty = min(95, friction_penalty + 20)

    score = max(5, 100 - friction_penalty)

    return {
        "persona_id": persona_id,
        "name": persona["name"],
        "age_range": persona["age_range"],
        "usability_score": score,
        "status": "pass" if score >= 80 else ("warn" if score >= 60 else "fail"),
        "friction_triggers_count": len(failing_targets) + len(failing_texts),
        "failing_touch_targets": failing_targets[:10],
        "failing_typography": failing_texts[:10],
        "key_friction_summary": persona["top_friction_triggers"][:3]
    }


def run_runtime_audit(
    base_url: str,
    pages: Optional[List[str]] = None,
    output_file: Optional[Path] = None,
    screenshots_dir: Optional[Path] = None,
    wait_ms: int = 1500,
) -> Dict:
    """Execute complete Playwright runtime UX audit on URL across viewports."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            "error": "Playwright is not installed. Install with: pip install playwright && python -m playwright install chromium",
            "status": "failed"
        }

    routes = pages or ["/"]
    full_urls = [urljoin(base_url, r) for r in routes]

    results: Dict[str, any] = {
        "version": VERSION,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "pages_tested": routes,
        "desktop": [],
        "mobile": [],
        "personas": {}
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. Desktop Browser Context (1440x900)
        desktop_ctx = browser.new_context(
            viewport=DESKTOP_VIEWPORT,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            has_touch=False
        )
        desktop_page = desktop_ctx.new_page()

        # 2. Mobile Browser Context (390x844 iPhone 14 touch)
        mobile_ctx = browser.new_context(
            viewport=MOBILE_VIEWPORT,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2
        )
        mobile_page = mobile_ctx.new_page()

        for url in full_urls:
            slug = re.sub(r"[^a-zA-Z0-9_-]", "_", urlparse(url).path.strip("/")) or "home"

            # Inspect desktop
            d_res = evaluate_page_in_viewport(
                desktop_page, url, "desktop", screenshots_dir, slug, wait_ms
            )
            results["desktop"].append(d_res)

            # Inspect mobile
            m_res = evaluate_page_in_viewport(
                mobile_page, url, "mobile", screenshots_dir, slug, wait_ms
            )
            results["mobile"].append(m_res)

        desktop_ctx.close()
        mobile_ctx.close()
        browser.close()

    # Simulate age cohorts on first page results
    first_desktop = results["desktop"][0] if results["desktop"] else {}
    first_mobile = results["mobile"][0] if results["mobile"] else {}

    results["personas"] = {
        "young": simulate_age_cohort(first_desktop, first_mobile, "young"),
        "adult": simulate_age_cohort(first_desktop, first_mobile, "adult"),
        "senior": simulate_age_cohort(first_desktop, first_mobile, "senior"),
    }

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"Saved runtime audit evidence to {output_file}")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", required=True, help="Base application URL to audit (e.g. http://localhost:3000)")
    parser.add_argument("--pages", nargs="*", default=["/"], help="Relative paths to inspect (default: /)")
    parser.add_argument("--output", help="Write runtime JSON output to file")
    parser.add_argument("--screenshots", help="Directory to save full-page desktop & mobile screenshots")
    parser.add_argument("--wait-ms", type=int, default=1500, help="Wait time in ms after navigation before inspecting")
    args = parser.parse_args()

    out_path = Path(args.output).resolve() if args.output else None
    screen_dir = Path(args.screenshots).resolve() if args.screenshots else None

    print(f"Starting Playwright runtime audit on {args.url} across Desktop (1440x900) & Mobile (390x844)...")
    data = run_runtime_audit(args.url, args.pages, out_path, screen_dir, args.wait_ms)

    if data.get("error"):
        print(f"Runtime error: {data['error']}", file=sys.stderr)
        return 1

    # Print summary
    print("\n" + "=" * 70)
    print(" UX AUDITOR — RUNTIME AUDIT SUMMARY")
    print("=" * 70)
    for d in data.get("desktop", []):
        print(f"Desktop ({d['url']}):")
        print(f"  Interactive targets: {d.get('targets_evaluated', 0)}")
        print(f"  Small targets (<44px): {d.get('small_targets_count', 0)}")
        print(f"  Low contrast items:  {d.get('low_contrast_targets_count', 0) + d.get('low_contrast_text_count', 0)}")
    print("-" * 70)
    for m in data.get("mobile", []):
        print(f"Mobile ({m['url']}):")
        print(f"  Horizontal scroll blowout: {'🚨 YES' if m.get('has_horizontal_overflow') else '✅ None'}")
        print(f"  Zoom disabled:            {'🚨 YES' if m.get('zoom_disabled') else '✅ Permitted'}")
        print(f"  Small touch targets:       {m.get('small_targets_count', 0)}")
        print(f"  Tight neighbor spacing:    {m.get('tight_spacing_count', 0)}")
    print("-" * 70)
    print("Age Cohort Friendliness Simulation:")
    for pid, pdata in data.get("personas", {}).items():
        if pdata:
            print(f"  • {pdata['name']} ({pdata['age_range']}): Score {pdata['usability_score']}/100 [{pdata['status'].upper()}] — {pdata['friction_triggers_count']} friction triggers")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
