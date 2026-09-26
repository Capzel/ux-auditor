---
name: ux
description: "UX and usability audit toolkit for codebases and web applications. Evaluates interfaces against the 21 Laws of UX (lawsofux.com) and NN/g 10 Usability Heuristics across Desktop and Mobile viewports, and simulates age cohort friction (Gen Z, working adults, seniors). Routes to full scored audits, fast static scans, live browser inspection, persona simulations, or concrete code fixes. Use when the user asks for a UX audit, usability review, Laws of UX check, mobile vs desktop inspection, senior accessibility check, heuristic evaluation, or UI friction analysis."
user-invocable: true
argument-hint: "[command] [path|url] [options]"
---

# UX & Usability Toolkit

**Invocation:** `/ux <command> [args]`. With no command, ask what the user wants to audit, or run `scan` if they provided only a path or `runtime` if they gave a URL.

Every skill and agent follows `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md`. Read it before producing findings.

---

## Commands

| Command | What it does | Skill / Handler |
|---|---|---|
| `/ux audit [path] [--url URL] [--pages ...]` | Full audit: static code scan, desktop & mobile runtime browser checks, 7 specialist agents, age cohort simulation, and scored report | `ux-audit` |
| `/ux scan [path]` | Fast static code scan in terminal, no browser or agents needed | (below) |
| `/ux runtime --url URL [--pages ...]` | Playwright runtime audit of Desktop & Mobile viewports with screenshots | (below) |
| `/ux mobile <url>` | Quick mobile viewport inspection (tap targets, overflow, thumb zone) | (below) |
| `/ux desktop <url>` | Quick desktop viewport inspection (focus rings, hover, density) | (below) |
| `/ux simulate [url] --persona senior\|young\|adult` | Simulate interface experience through specific age cohort lens | (below) |
| `/ux report [audit-dir]` | Re-merge findings and re-render Markdown & HTML reports | (below) |
| `/ux fix <FINDING-ID> [audit-dir]` | Plan and implement the remedy for one finding in code, then verify | (below) |
| `/ux laws [law-id]` | Browse the 21 Laws of UX with guidelines, violations, and remedies | (below) |
| `/ux heuristics [heuristic-id]` | Browse the NN/g 10 Usability Heuristics checklist | (below) |

---

## `/ux scan [path]`

Run the static codebase scanner:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_scan.py" <path> --format summary
```

Summarize for the user:
- Frontend stack and discovered routes
- Key static leads (small buttons, unlabelled inputs, disabled zoom, missing autocomplete)
- Remind the user these are static code leads; offer `/ux audit` for the full scored report with runtime DOM inspection.

---

## `/ux runtime --url <URL> [--pages ...]`

Inspect a running application in a real headless browser across Desktop (1440x900) and Mobile (390x844 touch):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_runtime.py" --url "<URL>" --pages <paths> \
        --output "./runtime.json" --screenshots "./screenshots"
```

Requires: `pip install playwright && python -m playwright install chromium`.

---

## `/ux report [audit-dir]`

Re-merge findings and re-render all deliverables:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" merge --audit-dir <audit-dir>
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" render --data <audit-dir>/audit-data.json
```

If no directory is specified, use the most recent folder under `./ux-audit/`.

---

## `/ux fix <FINDING-ID>`

1. Load `<audit-dir>/audit-data.json` (most recent under `./ux-audit/`) and find the finding by `id`.
2. Inspect the evidence file and lines. If the code was already changed and the issue is resolved, confirm and stop.
3. Read the relevant category remedy guide (e.g. `${CLAUDE_PLUGIN_ROOT}/skills/ux-interaction-ergonomics/references/interaction-remedies.md`).
4. Propose a concrete change plan: files to touch, classes/styles to update, touch target padding, or form labels.
5. **Ask for approval before editing.**
6. Apply the smallest clean change respecting codebase conventions.
7. Re-run `ux_scan.py` or `ux_runtime.py` to verify the fix.
8. In `<audit-dir>/findings/<category>.json`, update the finding status to `pass` with a note, then run `/ux report` to re-score.

---

## `/ux laws [law-id]`

Read `${CLAUDE_PLUGIN_ROOT}/data/laws_of_ux.json` and display the requested law (e.g. `fitts-law`, `hicks-law`, `doherty-threshold`, `jakobs-law`):
- Official definition and summary
- Key takeaways
- Common UI anti-patterns in code
- Concrete code and design remedies
- Link to [lawsofux.com](https://lawsofux.com/)

---

## `/ux heuristics [heuristic-id]`

Read `${CLAUDE_PLUGIN_ROOT}/data/heuristics.json` and display the requested NN/g Heuristic:
- Number and name
- Summary
- Complete evaluation checklist
- Common violations and remedies

---

## Shared References

- `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md`: Evidence rules, scoring formula, dual viewports, age simulation
- `${CLAUDE_PLUGIN_ROOT}/data/laws_of_ux.json`: 21 Laws of UX database
- `${CLAUDE_PLUGIN_ROOT}/data/heuristics.json`: NN/g 10 Usability Heuristics database
- `${CLAUDE_PLUGIN_ROOT}/data/personas.json`: Age group cohorts (Gen Z, Adults, Seniors)
