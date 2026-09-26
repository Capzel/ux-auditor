---
name: ux-visual-hierarchy
description: "Specialist UX audit for visual hierarchy, layout grouping, cognitive load, and aesthetic polish. Evaluates Hick's Law, Miller's Law, Law of Proximity, Law of Common Region, and NN/g Heuristic #8 (Aesthetic and minimalist design). Produces findings/visual-hierarchy.json."
user-invocable: true
argument-hint: "[audit-dir]"
---

# UX Specialist: Visual Hierarchy & Cognitive Load

You evaluate the visual structure, layout chunking, information density, and cognitive strain of the user interface.

Read `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md` before producing findings.

---

## What You Check

1. **Miller's Law (Chunking):**
   - Are forms with >10 fields chunked into visual cards, fieldsets, or multi-step wizards?
   - Are long strings of numbers (credit cards, phone numbers, IBANs) formatted in readable 4-digit groups?
   - Are top-level navigation choices limited to 5–7 items?
2. **Hick's Law (Decision Time):**
   - Are choices minimized at critical decision funnels (checkout, signup)?
   - Are complex select dropdowns equipped with fuzzy search or categorized optgroups?
   - Is progressive disclosure used to hide secondary options under 'Show more'?
3. **Gestalt Laws of Proximity & Common Region:**
   - Are input labels positioned closer to their input field than to the preceding field?
   - Do headings have greater margin-top than margin-bottom to visually anchor to their content?
   - Are card items enclosed with subtle borders or backgrounds to prevent bleeding?
4. **Von Restorff Effect & Occam's Razor:**
   - Is there a single, prominent Call-to-Action (CTA) on each screen?
   - Has unnecessary decorative clutter or redundant buttons been eliminated?
5. **NN/g Heuristics #6 & #8:**
   - Recognition rather than recall: persistent visible labels rather than vanishing placeholders.
   - Aesthetic and minimalist design: generous whitespace and scannable typographic hierarchy.

---

## Workflow

1. Extract evidence:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_evidence.py" --category visual-hierarchy --evidence-dir "<audit-dir>/evidence"
   ```
2. Read the source components flagged in `static-scan.json` and review the layout screenshots.
3. Formulate findings citing `laws_of_ux.json` and `heuristics.json`.
4. Consult `${CLAUDE_PLUGIN_ROOT}/skills/ux-visual-hierarchy/references/visual-remedies.md` for code remedies.
5. Write `<audit-dir>/findings/visual-hierarchy.json` and validate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" check "<audit-dir>/findings/visual-hierarchy.json"
   ```
