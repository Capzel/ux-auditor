# ux-auditor development notes

UX and usability audit plugin based on the 21 Laws of UX (lawsofux.com) and the NN/g 10 Usability Heuristics.

## Layout

- `.claude-plugin/`: `plugin.json` and `marketplace.json`
- `data/`:
  - `laws_of_ux.json`: 21 Laws of UX with summaries, takeaways, violations, and remedies
  - `heuristics.json`: NN/g 10 Usability Heuristics with checklists and violations
  - `personas.json`: Age cohorts (Young, Adult, Senior) with physiological and ergonomic thresholds
- `skills/ux/`: Master router skill and `references/audit-standards.md`
- `skills/ux-audit/`: Orchestrator skill, findings schema, coverage matrix, questionnaire
- `skills/ux-<category>/`: 7 specialist skills with `references/*-remedies.md`
- `agents/`: 7 thin agent definitions pointing to category skills
- `scripts/`:
  - `ux_common.py`: Shared constants, scoring logic, WCAG luminance/contrast math, Fitts's Law helpers
  - `ux_rules.py`: Static scanner rules collection
  - `ux_scan.py`: Codebase scanner
  - `ux_runtime.py`: Headless Playwright inspector for Desktop (1440x900) & Mobile (390x844 touch) viewports
  - `ux_evidence.py`: Category evidence filter
  - `ux_report.py`: `check`, `merge`, and `render` commands (Markdown, Action Plan, Personas, interactive HTML)
  - `install_skills.py`: Cross-agent installer for Antigravity, Gemini CLI, Codex, Cursor
- `docs/`: `other-agents.md`
- `tests/`: Unittest test suites and fixtures (`friction-shop`, `accessible-shop`, `sample-audit`)

## Conventions

- **Python 3.8+ compatible, standard library only** for scan, evidence, rules, and report (`from __future__ import annotations`). Playwright is optional, used only by `ux_runtime.py`.
- **Dual viewports**: Always inspect both Desktop (1440x900) and Mobile (390x844).
- **Age cohorts**: Young (13-24, Gen Z), Adult (25-59), Senior (60+). Evaluate contrast, font sizes, and touch targets per cohort.
- Skill files reference bundled files via `${CLAUDE_PLUGIN_ROOT}` so `install_skills.py` can rewrite it to an absolute path for other agents.
- Category IDs are fixed: `visual-hierarchy`, `interaction-ergonomics`, `navigation-wayfinding`, `system-feedback`, `error-resilience`, `accessibility-inclusion`, `content-clarity`.

## Testing

```bash
python3 -m unittest discover -s tests -v
```
