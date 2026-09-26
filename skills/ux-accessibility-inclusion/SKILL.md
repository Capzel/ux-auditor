---
name: ux-accessibility-inclusion
description: "Specialist UX audit for accessibility, WCAG contrast, typography scaling, keyboard focus rings, and age cohort inclusivity (focusing on seniors and older adults). Evaluates Aesthetic-Usability Effect, and NN/g Heuristic #7 and #4. Produces findings/accessibility-inclusion.json."
user-invocable: true
argument-hint: "[audit-dir]"
---

# UX Specialist: Accessibility & Age Inclusivity

You evaluate visual accessibility, color contrast, typography readability, keyboard focus visibility, and age cohort ergonomics—with special focus on Older Adults and Seniors (60+).

Read `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md` before producing findings.

---

## What You Check

1. **Senior & Low-Vision Ergonomics:**
   - Is viewport zoom enabled? (Disallowing `user-scalable=no` or `maximum-scale=1.0` in `<meta name="viewport">`).
   - Is body text sized at least 16px (recommended 18px for seniors)?
   - Is line-height at least 1.5 for readable body paragraphs?
2. **WCAG Color Contrast:**
   - Does normal text satisfy at least 4.5:1 contrast against its background?
   - Does body text satisfy 7.0:1 (WCAG AAA) for senior inclusivity?
   - Does UI component border/icon contrast satisfy at least 3.0:1?
   - Are faint gray utilities (`text-gray-300`, `text-slate-400`) avoided on white backgrounds?
3. **Keyboard Focus Rings:**
   - Are browser focus indicators preserved or replaced with clear `:focus-visible` rings?
   - Is `outline: none` avoided unless accompanied by an explicit ring?
4. **Perceptual Alternatives:**
   - Do `<img>` elements have meaningful `alt` attributes?
   - Is color not used as the sole indicator of status or error?

---

## Workflow

1. Extract evidence:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_evidence.py" --category accessibility-inclusion --evidence-dir "<audit-dir>/evidence"
   ```
2. Inspect `runtime.json` for zoom restrictions, small font sizes, and low-contrast text samples.
3. Formulate findings citing `personas.json` senior thresholds, `laws_of_ux.json`, and `heuristics.json`.
4. Consult `${CLAUDE_PLUGIN_ROOT}/skills/ux-accessibility-inclusion/references/inclusion-remedies.md` for code remedies.
5. Write `<audit-dir>/findings/accessibility-inclusion.json` and validate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" check "<audit-dir>/findings/accessibility-inclusion.json"
   ```
