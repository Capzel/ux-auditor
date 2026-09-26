#!/usr/bin/env python3
"""Static UX codebase scanner.
Analyzes component structures, styling, forms, responsive markers, and accessibility.
Standard library only, Python 3.8+.

Usage:
  python3 ux_scan.py [path] [--output scan.json] [--format summary|json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ux_common import CATEGORIES, CATEGORY_TITLES, mask_sensitive  # noqa: E402
from ux_rules import RULES, UXRule  # noqa: E402

VERSION = "1.0.0"

IGNORE_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "dist", "build", ".next", ".nuxt",
    ".svelte-kit", "out", "coverage", ".cache", "venv", ".venv", "__pycache__",
    "vendor", ".turbo", "public", ".gemini", ".claude"
}

ALLOWED_EXTENSIONS = {
    ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".js", ".ts",
    ".css", ".scss", ".sass", ".less", ".php"
}


def detect_stack(root: Path) -> List[str]:
    """Identify frontend framework and CSS libraries in codebase."""
    stack = []
    pkg_file = root / "package.json"
    if pkg_file.is_file():
        try:
            with open(pkg_file, encoding="utf-8") as fh:
                data = json.load(fh)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "next" in deps:
                    stack.append("Next.js")
                elif "react" in deps:
                    stack.append("React")
                if "vue" in deps:
                    stack.append("Vue.js")
                if "nuxt" in deps:
                    stack.append("Nuxt")
                if "svelte" in deps or "@sveltejs/kit" in deps:
                    stack.append("Svelte")
                if "@angular/core" in deps:
                    stack.append("Angular")
                if "tailwindcss" in deps:
                    stack.append("Tailwind CSS")
                if "bootstrap" in deps:
                    stack.append("Bootstrap")
                if "@mui/material" in deps:
                    stack.append("Material-UI")
                if "radix-ui" in str(deps):
                    stack.append("Radix UI")
        except Exception:
            pass

    # Fallback checks
    if not stack:
        if list(root.glob("**/*.tsx")) or list(root.glob("**/*.jsx")):
            stack.append("React")
        elif list(root.glob("**/*.vue")):
            stack.append("Vue")
        elif list(root.glob("**/*.svelte")):
            stack.append("Svelte")
        elif list(root.glob("**/*.html")):
            stack.append("HTML5 / Vanilla")
    return stack or ["Web / Frontend"]


def discover_routes(root: Path) -> List[str]:
    """Discover likely URL routes and pages from filesystem."""
    routes: Set[str] = set()

    # Next.js app or pages router
    app_dir = root / "app"
    pages_dir = root / "pages"
    src_app = root / "src" / "app"
    src_pages = root / "src" / "pages"

    for d in [app_dir, pages_dir, src_app, src_pages]:
        if d.is_dir():
            for p in d.rglob("*"):
                if p.is_file() and p.suffix in (".js", ".jsx", ".ts", ".tsx"):
                    if p.stem in ("page", "index"):
                        rel = p.relative_to(d).parent.as_posix()
                        route = "/" if rel == "." else f"/{rel}"
                        routes.add(route)

    # Standard HTML files
    for p in root.glob("*.html"):
        routes.add("/" if p.name == "index.html" else f"/{p.stem}")

    # Fallback common pages if none discovered
    if not routes:
        routes.update(["/", "/login", "/signup", "/checkout", "/contact", "/settings"])

    return sorted(routes)


def scan_file(path: Path, root: Path) -> List[Dict]:
    """Scan a single file against UX rules and structural heuristics."""
    signals = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return signals

    lines = content.splitlines()
    rel_path = str(path.relative_to(root))

    # Apply regex rules
    for rule in RULES:
        if not rule.compiled_regex:
            continue
        if path.suffix not in rule.file_patterns:
            continue

        for m in rule.compiled_regex.finditer(content):
            start_pos = m.start()
            line_no = content[:start_pos].count("\n") + 1
            snippet = re.sub(r"\s+", " ", m.group(0).strip())
            if len(snippet) > 160:
                snippet = snippet[:157] + "..."
            signals.append({
                "rule_id": rule.rule_id,
                "category": rule.category,
                "title": rule.title,
                "severity": rule.severity,
                "confidence": rule.confidence,
                "laws": rule.laws,
                "heuristics": rule.heuristics,
                "personas_affected": rule.personas_affected,
                "file": rel_path,
                "line": line_no,
                "snippet": mask_sensitive(snippet),
                "remedy": rule.remedy,
                "description": rule.description,
            })

    # Structural check: Count inputs inside form blocks
    if path.suffix in (".html", ".jsx", ".tsx", ".vue", ".svelte"):
        form_matches = re.finditer(r"<form\b[^>]*>(.*?)</form>", content, re.DOTALL | re.IGNORECASE)
        for fm in form_matches:
            form_body = fm.group(1)
            # Count input, select, textarea
            field_count = len(re.findall(r"<(?:input(?![^>]*type=[\"']hidden[\"'])|select|textarea)\b", form_body, re.I))
            if field_count > 10:
                # Find line number of <form>
                start_pos = fm.start()
                line_no = content[:start_pos].count("\n") + 1
                signals.append({
                    "rule_id": "UX-VIS-MASSIVE-FORM",
                    "category": "visual-hierarchy",
                    "title": f"Massive unchunked form contains {field_count} input fields without steps or wizard",
                    "severity": "medium",
                    "confidence": "confirmed",
                    "laws": ["millers-law", "hicks-law"],
                    "heuristics": ["aesthetic-and-minimalist-design", "flexibility-and-efficiency-of-use"],
                    "personas_affected": ["young", "adult", "senior"],
                    "file": rel_path,
                    "line": line_no,
                    "snippet": lines[line_no - 1].strip() if line_no <= len(lines) else "<form>",
                    "remedy": f"Split this {field_count}-field form into a multi-step wizard (2-4 steps) or group into labeled cards.",
                    "description": "Forms with >10 fields create acute cognitive overload (Miller's Law) and high drop-off rates.",
                })

    return signals


def scan_codebase(target_dir: Path) -> Dict:
    """Execute full static UX audit over directory."""
    root = target_dir.resolve()
    stack = detect_stack(root)
    routes = discover_routes(root)

    scanned_files = 0
    all_signals: List[Dict] = []

    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for file in files:
            p = Path(root_dir) / file
            if p.suffix.lower() in ALLOWED_EXTENSIONS:
                scanned_files += 1
                sigs = scan_file(p, root)
                all_signals.extend(sigs)

    # Deduplicate signals by (rule_id, file, line)
    seen = set()
    deduped = []
    for s in all_signals:
        key = (s["rule_id"], s["file"], s.get("line"))
        if key not in seen:
            seen.add(key)
            deduped.append(s)

    # Sort signals by severity rank
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    deduped.sort(key=lambda s: (sev_order.get(s["severity"], 99), s["file"]))

    return {
        "version": VERSION,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "target_path": str(root),
        "files_scanned": scanned_files,
        "stack": stack,
        "routes": routes,
        "signals": deduped,
        "summary": {
            "total_signals": len(deduped),
            "critical": sum(1 for s in deduped if s["severity"] == "critical"),
            "high": sum(1 for s in deduped if s["severity"] == "high"),
            "medium": sum(1 for s in deduped if s["severity"] == "medium"),
            "low": sum(1 for s in deduped if s["severity"] == "low"),
        }
    }


def print_summary(data: Dict) -> None:
    """Print readable terminal summary."""
    print("=" * 70)
    print(" UX AUDITOR — STATIC SCAN SUMMARY")
    print("=" * 70)
    print(f"Target:       {data['target_path']}")
    print(f"Stack:        {', '.join(data['stack'])}")
    print(f"Files:        {data['files_scanned']} scanned")
    print(f"Routes found: {len(data['routes'])} routes ({', '.join(data['routes'][:5])}{'...' if len(data['routes']) > 5 else ''})")
    print("-" * 70)
    sum_data = data["summary"]
    print(f"Signals:      {sum_data['total_signals']} total leads")
    print(f"  🔴 Critical: {sum_data['critical']}")
    print(f"  🟠 High:     {sum_data['high']}")
    print(f"  🟡 Medium:   {sum_data['medium']}")
    print(f"  🔵 Low:      {sum_data['low']}")
    print("-" * 70)

    if not data["signals"]:
        print("✅ No obvious static UX anti-patterns detected in source files!")
        print("=" * 70)
        return

    print("Top static leads to verify:")
    for s in data["signals"][:10]:
        print(f" • [{s['severity'].upper()}] {s['title']}")
        print(f"   {s['file']}:{s.get('line', 1)} | Laws: {', '.join(s.get('laws', []))}")
        print(f"   Fix: {s['remedy']}")
        print()
    if len(data["signals"]) > 10:
        print(f"   ... and {len(data['signals']) - 10} more signals (run with --output to export all).")
    print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", default=".", help="Codebase directory to scan (default: .)")
    parser.add_argument("--output", help="Write scan output JSON to file")
    parser.add_argument("--format", choices=["summary", "json"], default="summary", help="Output format")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"error: path does not exist: {target}", file=sys.stderr)
        return 1

    results = scan_codebase(target)

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"Wrote scan results to {out_path}")

    if args.format == "json" and not args.output:
        print(json.dumps(results, indent=2))
    elif args.format == "summary":
        print_summary(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
