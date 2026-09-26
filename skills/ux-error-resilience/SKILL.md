---
name: ux-error-resilience
description: "Specialist UX audit for error prevention, forgiving inputs, Postel's Law, destructive safeguards, and error recovery. Evaluates Postel's Law, and NN/g Heuristic #5 (Error prevention) and #9 (Help users recognize, diagnose, and recover from errors). Produces findings/error-resilience.json."
user-invocable: true
argument-hint: "[audit-dir]"
---

# UX Specialist: Error Prevention & Recovery

You evaluate how gracefully the application prevents human errors before they happen, forgives irregular input formats (Postel's Law), guards destructive actions, and guides users out of errors.

Read `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md` before producing findings.

---

## What You Check

1. **Postel's Law (Robustness Principle):**
   - Does the app accept flexible input formats for phone numbers (dashes, spaces, country codes) and strip delimiters automatically?
   - Does it accept credit cards with or without spaces?
   - Does it preserve all valid form input when submission fails rather than wiping the screen?
2. **NN/g Heuristic #5 (Error Prevention):**
   - Are destructive actions (e.g. deleting an account, dropping a database) protected by an explicit confirmation dialog?
   - Are input constraints (date pickers, number bounds, select limits) used instead of unvalidated free text?
   - Does inline validation alert users to format problems upon leaving a field (`onBlur`) rather than waiting for server submission?
3. **NN/g Heuristic #9 (Help Users Recognize & Recover):**
   - Are error messages written in clear, polite language without developer jargon or error codes (no `Error 500` or `NullPointerException`)?
   - Do error messages explicitly explain how to fix the problem?
   - Are error messages placed inline directly below the offending input with an error icon (not just a red border)?

---

## Workflow

1. Extract evidence:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_evidence.py" --category error-resilience --evidence-dir "<audit-dir>/evidence"
   ```
2. Review static signals for destructive buttons and unlabelled inputs.
3. Formulate findings citing `postels-law`, `error-prevention`, `help-users-recognize-errors`, and `heuristics.json`.
4. Consult `${CLAUDE_PLUGIN_ROOT}/skills/ux-error-resilience/references/error-remedies.md` for code remedies.
5. Write `<audit-dir>/findings/error-resilience.json` and validate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" check "<audit-dir>/findings/error-resilience.json"
   ```
