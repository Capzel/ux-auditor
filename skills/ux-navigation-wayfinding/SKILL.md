---
name: ux-navigation-wayfinding
description: "Specialist UX audit for navigation architecture, wayfinding, mental models, and user freedom. Evaluates Jakob's Law, Serial Position Effect, Uniform Connectedness, and NN/g Heuristic #3 (User control and freedom) and #4 (Consistency and standards). Produces findings/navigation-wayfinding.json."
user-invocable: true
argument-hint: "[audit-dir]"
---

# UX Specialist: Navigation, Wayfinding & Consistency

You evaluate how easily users navigate the interface, understand their current location, predict interactions based on web conventions, and recover from unwanted paths.

Read `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md` before producing findings.

---

## What You Check

1. **Jakob's Law (Familiar Mental Models):**
   - Does clicking the top-left logo or branding return the user to the homepage (`/`)?
   - Is navigation placed in standard header or bottom tab bar locations?
   - Do links look like links (underlined or contrasting color) and static text look like static text?
2. **Serial Position Effect (Primacy & Recency):**
   - Are the most critical navigation links positioned at the far left/start, and user actions/profile at the far right/end?
   - In mobile bottom tab bars, is 'Home' at index 0 and 'Profile/Settings' at the final position?
3. **Law of Uniform Connectedness:**
   - Are multi-step workflows (wizards, checkouts) connected with clear visual progress lines?
   - Do breadcrumbs feature clear visual separators (`/` or `›`)?
4. **NN/g Heuristic #3 (User Control and Freedom):**
   - Can dialogs and modals be closed via the Escape key, a visible 'X' button, and clicking outside?
   - Does navigating back in multi-step forms preserve entered input?
   - Is an 'Undo' option provided for reversible actions like archiving or deleting?
5. **NN/g Heuristic #4 (Consistency & Standards):**
   - Are button variants (primary, secondary, danger) used consistently across all screens?
   - Is terminology uniform (e.g. not mixing 'Cart' and 'Basket')?

---

## Workflow

1. Extract evidence:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_evidence.py" --category navigation-wayfinding --evidence-dir "<audit-dir>/evidence"
   ```
2. Check routes discovered and review navigation components.
3. Formulate findings citing `jakobs-law`, `serial-position-effect`, `uniform-connectedness-law`, and `heuristics.json`.
4. Consult `${CLAUDE_PLUGIN_ROOT}/skills/ux-navigation-wayfinding/references/navigation-remedies.md` for remedies.
5. Write `<audit-dir>/findings/navigation-wayfinding.json` and validate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" check "<audit-dir>/findings/navigation-wayfinding.json"
   ```
