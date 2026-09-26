---
name: ux-content-clarity
description: "Specialist UX audit for terminology clarity, mystery-meat icons, empty states, and contextual help. Evaluates Jakob's Law, and NN/g Heuristic #2 (Match between system and the real world) and #10 (Help and documentation). Produces findings/content-clarity.json."
user-invocable: true
argument-hint: "[audit-dir]"
---

# UX Specialist: Content Clarity & Real-World Match

You evaluate whether the interface communicates in the user's natural language, provides recognizable visual affordances, labels iconography clearly, and guides users with helpful empty states.

Read `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md` before producing findings.

---

## What You Check

1. **Unlabelled Icon Buttons (Mystery-Meat Navigation):**
   - Are icon-only buttons (`<svg>` or `<i>` inside `<button>`) accompanied by visible text or an explicit `aria-label`?
   - Do unfamiliar custom glyphs force users to guess their meaning?
2. **NN/g Heuristic #2 (Match Between System & Real World):**
   - Is UI copy written in plain, human terms rather than internal technical jargon or database column names?
   - Do icons mirror real-world conventions (e.g. magnifying glass for search, shopping bag/cart for items, gear for settings)?
3. **NN/g Heuristic #10 (Help & Documentation):**
   - Do complex fields provide contextual helper text or tooltips explaining what is expected?
   - Do empty collections (e.g. 'No projects yet') provide welcoming illustrations, clear explanations, and a primary CTA to create the first item?

---

## Workflow

1. Extract evidence:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_evidence.py" --category content-clarity --evidence-dir "<audit-dir>/evidence"
   ```
2. Check `static-scan.json` signals for unlabelled buttons and missing helper texts.
3. Formulate findings citing `jakobs-law`, `match-system-real-world`, and `help-and-documentation`.
4. Consult `${CLAUDE_PLUGIN_ROOT}/skills/ux-content-clarity/references/clarity-remedies.md` for code remedies.
5. Write `<audit-dir>/findings/content-clarity.json` and validate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" check "<audit-dir>/findings/content-clarity.json"
   ```
