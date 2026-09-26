---
name: ux-audit
description: "Full UX and usability audit of a codebase and running web application. Collects static code signals and live Playwright browser metrics across Desktop and Mobile viewports, coordinates 7 specialist agents in parallel, simulates age cohort friction (Gen Z, adults, seniors), and generates a scored report (Markdown + standalone interactive HTML) with concrete code remedies and a phased action plan. Use when the user asks for a full UX audit, usability audit, design system review, mobile responsiveness check, senior usability test, or accessibility review."
user-invocable: true
argument-hint: "[path] [--url URL] [--pages ...] [--personas ...] [--out DIR] [--no-questions]"
---

# UX Audit Orchestrator

You run the comprehensive UX audit end-to-end. You collect evidence, spawn 7 specialist agents in parallel, simulate age cohorts, merge results, resolve overlaps, and deliver actionable reports.

Read `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md` first.

---

## Phase 0: Scope & Setup

1. **Target**: Path argument, or current working directory (`.`).
2. **Audit Directory**: `--out` or `./ux-audit/<project>-<YYYY-MM-DD>/` (append `-2`, `-3` if exists).
   - Create directories: `<audit>/evidence/`, `<audit>/evidence/screenshots/`, and `<audit>/findings/`.
   - Recommend adding `ux-audit/` to `.gitignore`.
3. **Scope Questions** (skip if `--no-questions` or answered via flags):
   - Ask the scope questions in `references/questionnaire.md`: running URL, target viewports, age cohorts to simulate, priority user flows.
4. **Safety Check**: Verify URL is local (`localhost`, `127.0.0.1`, `*.local`) or staging. Never submit real payment forms or destructively modify production data.

---

## Phase 1: Collect Evidence

Run sequentially and save outputs into `<audit>/evidence/`:

```bash
# 1. Static codebase scan
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_scan.py" "<target>" \
        --output "<audit>/evidence/static-scan.json"

# 2. Playwright runtime inspector (if URL provided)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_runtime.py" --url "<url>" \
        --pages <discovered routes or / /login /checkout> \
        --output "<audit>/evidence/runtime.json" \
        --screenshots "<audit>/evidence/screenshots"
```

- If Playwright is missing and URL was provided, notify the user: `pip install playwright && python -m playwright install chromium` and proceed with static evidence.
- Write `<audit>/meta.json` with project info, stack, date, target viewports, and evidence tiers available.

---

## Phase 2: Specialist Analysis (Parallel)

Spawn the seven specialist agents **in one invocation** so they run concurrently:

| Subagent Type | Category | Output Target |
|---|---|---|
| `ux-auditor:ux-visual-hierarchy` | `visual-hierarchy` | `findings/visual-hierarchy.json` |
| `ux-auditor:ux-interaction-ergonomics` | `interaction-ergonomics` | `findings/interaction-ergonomics.json` |
| `ux-auditor:ux-navigation-wayfinding` | `navigation-wayfinding` | `findings/navigation-wayfinding.json` |
| `ux-auditor:ux-system-feedback` | `system-feedback` | `findings/system-feedback.json` |
| `ux-auditor:ux-error-resilience` | `error-resilience` | `findings/error-resilience.json` |
| `ux-auditor:ux-accessibility-inclusion` | `accessibility-inclusion` | `findings/accessibility-inclusion.json` |
| `ux-auditor:ux-content-clarity` | `content-clarity` | `findings/content-clarity.json` |

### Prompt Template for Each Agent:

```
UX audit, category: <category>
Target codebase: <absolute path to codebase>
Audit directory: <absolute path to audit-dir>
Evidence directory: <audit-dir>/evidence/
Viewports tested: Desktop (1440x900) and Mobile (390x844)
Age cohorts: Young (13-24), Adult (25-59), Senior (60+)
Stack: <detected frameworks>

1. Run: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_evidence.py" --category <category> --evidence-dir "<audit-dir>/evidence"
2. Inspect the relevant source code files and runtime DOM data for your category.
3. Formulate findings citing the 21 Laws of UX and NN/g 10 Heuristics.
4. Write: <audit-dir>/findings/<category>.json (conforming to findings-schema.md).
5. Validate: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" check "<audit-dir>/findings/<category>.json".
Reply with a concise 3-bullet summary only.
```

*Note:* If subagents are not available in the environment, run the 7 category skills sequentially inline. The output contract is identical.

---

## Phase 3: Consolidate & Merge

1. Merge all fragments:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" merge --audit-dir "<audit-dir>"
   ```
2. Deduplicate overlaps: Keep finding in primary owning category per `audit-standards.md`.
3. Add a concise 2–3 sentence `executive_summary` to `meta.json` highlighting the top friction points and score.
4. Merge again to record the summary into `audit-data.json`.

---

## Phase 4: Render Deliverables

Render all final audit reports:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" render --data "<audit-dir>/audit-data.json"
```

This generates:
- `UX-AUDIT-REPORT.md`: Comprehensive markdown report with scores, citations, evidence, and code remedies.
- `ACTION-PLAN.md`: Phased implementation checklist (P0 Quick Wins, P1 Mobile & Ergonomics, P2 Polish).
- `personas-analysis.md`: In-depth breakdown by demographic cohort (Gen Z, Working Adults, Seniors).
- `ux-audit-report.html`: Standalone, interactive HTML report with mobile/desktop filtering and 1-click PDF print styling.

---

## Phase 5: Present to User

Present a clean, high-impact summary:
1. **Overall Usability Score** (e.g. `82/100 — Good, with minor friction`) and category scorecard.
2. **Age Cohort Scores**:
   - Digital Natives (Gen Z): `88/100`
   - Working Adults: `85/100`
   - Seniors (60+): `68/100` (highlighting contrast and touch target gaps)
3. **Top Critical/High Findings** (ID, title, affected viewport).
4. **Immediate Quick Wins** (P0 low-effort high-impact fixes).
5. Links to generated files:
   - [UX-AUDIT-REPORT.md](file://<audit-dir>/UX-AUDIT-REPORT.md)
   - [ACTION-PLAN.md](file://<audit-dir>/ACTION-PLAN.md)
   - [personas-analysis.md](file://<audit-dir>/personas-analysis.md)
   - [ux-audit-report.html](file://<audit-dir>/ux-audit-report.html)
6. Next action: Offer `/ux fix <FINDING-ID>` to implement fixes directly in the code!
