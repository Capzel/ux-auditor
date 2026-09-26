#!/usr/bin/env python3
"""Install the ux-auditor skills into another agent's skills directory.

SKILL.md is an open format that several coding agents read (Antigravity, Gemini CLI,
Claude Code, OpenAI Codex, Cursor). Only Claude Code natively substitutes ${CLAUDE_PLUGIN_ROOT}.
This installer copies the skills and rewrites ${CLAUDE_PLUGIN_ROOT} to the absolute path
of this checkout so scripts, data, and references resolve everywhere.

Usage:
  python3 scripts/install_skills.py --agent codex
  python3 scripts/install_skills.py --agent gemini --scope user
  python3 scripts/install_skills.py --dir ~/.cursor/skills
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = "${CLAUDE_PLUGIN_ROOT}"

TARGETS = {
    "codex": {"project": ".agents/skills", "user": "~/.agents/skills"},
    "gemini": {"project": ".gemini/skills", "user": "~/.gemini/skills"},
    "antigravity": {"project": ".gemini/skills", "user": "~/.gemini/skills"},
    "claude": {"project": ".claude/skills", "user": "~/.claude/skills"},
    "generic": {"project": ".agents/skills", "user": "~/.agents/skills"},
}


def install(dest: Path, root: Path, names: Optional[List[str]], dry_run: bool, force: bool) -> int:
    src_root = PLUGIN_ROOT / "skills"
    if not src_root.is_dir():
        print(f"error: skills directory not found in {PLUGIN_ROOT}", file=sys.stderr)
        return 2

    skills = sorted(p for p in src_root.iterdir() if (p / "SKILL.md").is_file())
    if names:
        wanted = set(names)
        skills = [p for p in skills if p.name in wanted]
        missing = wanted - {p.name for p in skills}
        if missing:
            print("error: unknown skill(s): %s" % ", ".join(sorted(missing)), file=sys.stderr)
            return 2

    if not skills:
        print(f"error: no skills found in {src_root}", file=sys.stderr)
        return 2

    written = 0
    for skill in skills:
        target = dest / skill.name
        if target.exists() and not force and not dry_run:
            print(f"skip   {target} (already exists; use --force to overwrite)")
            continue
        for src in sorted(skill.rglob("*")):
            if src.is_dir() or src.name.startswith("."):
                continue
            out = target / src.relative_to(skill)
            text = src.read_text(encoding="utf-8").replace(PLACEHOLDER, str(root))
            print(f"{'would write' if dry_run else 'write      '} {out}")
            if not dry_run:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text, encoding="utf-8")
            written += 1

    if not dry_run and written:
        print(f"\nInstalled {written} file(s) into {dest}")
        print(f"Skills reference this checkout at: {root}")
        print(f"Make sure python3 can run {root}/scripts/ux_scan.py")

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", choices=sorted(TARGETS), help="Target agent")
    ap.add_argument("--scope", choices=["project", "user"], default="project", help="Install scope")
    ap.add_argument("--dir", help="Explicit destination skills directory (overrides --agent)")
    ap.add_argument("--skills", nargs="*", help="Only install specific skills by name")
    ap.add_argument("--root", default=str(PLUGIN_ROOT), help="Root checkout path to bake into SKILL.md")
    ap.add_argument("--dry-run", action="store_true", help="Preview files to be written without writing")
    ap.add_argument("--force", action="store_true", help="Overwrite existing skill files")
    args = ap.parse_args(argv)

    if not args.agent and not args.dir:
        ap.error("specify either --agent or --dir")

    if args.dir:
        dest = Path(args.dir).expanduser().resolve()
    else:
        cfg = TARGETS[args.agent][args.scope]
        dest = Path(cfg).expanduser().resolve()

    root = Path(args.root).resolve()
    return install(dest, root, args.skills, args.dry_run, args.force)


if __name__ == "__main__":
    sys.exit(main())
