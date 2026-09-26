---
name: ux-system-feedback
description: "Specialist UX audit for system feedback, latency, Doherty Threshold (<400ms), and progress indicators. Evaluates Doherty Threshold, Goal-Gradient Effect, Peak-End Rule, Zeigarnik Effect, and NN/g Heuristic #1 (Visibility of system status). Produces findings/system-feedback.json."
user-invocable: true
argument-hint: "[audit-dir]"
---

# UX Specialist: Feedback, Status & Performance

You evaluate how the system informs users about its state, responds to interactions within cognitive thresholds (<400ms), and provides motivating progress feedback.

Read `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md` before producing findings.

---

## What You Check

1. **Doherty Threshold (<400ms Response Time):**
   - Do interactive buttons provide immediate visual feedback (<100ms) on click (active state, spinner)?
   - Are submit buttons disabled during network requests to prevent double-clicks?
   - Are skeleton screens or shimmer loaders used during data fetching rather than blank screens?
   - Are low-risk actions (likes, toggles, bookmarks) updated optimistically in the UI?
2. **Goal-Gradient Effect & Zeigarnik Effect:**
   - Do multi-step forms or onboarding flows feature a visual progress bar or step counter ('Step 2 of 4')?
   - Is endowed progress used (e.g. starting with 20% complete)?
   - Does the app auto-save drafts and display reassuring 'Draft saved' indicators?
3. **Peak-End Rule:**
   - Are successful completions (purchases, submissions) rewarded with reassuring, celebratory states?
   - Do 404 and 500 error pages provide clear navigation back to safety rather than dead ends?
4. **NN/g Heuristic #1 (Visibility of System Status):**
   - Are active tabs, current route links, and selected filters highlighted clearly?
   - Are system background processes (sync, upload) visible with progress percentage?

---

## Workflow

1. Extract evidence:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_evidence.py" --category system-feedback --evidence-dir "<audit-dir>/evidence"
   ```
2. Check `static-scan.json` signals for submit buttons lacking loading states.
3. Review `runtime.json` navigation timing metrics.
4. Formulate findings citing `doherty-threshold`, `goal-gradient-effect`, `peak-end-rule`, and `heuristics.json`.
5. Consult `${CLAUDE_PLUGIN_ROOT}/skills/ux-system-feedback/references/feedback-remedies.md` for code remedies.
6. Write `<audit-dir>/findings/system-feedback.json` and validate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" check "<audit-dir>/findings/system-feedback.json"
   ```
