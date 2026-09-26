---
name: ux-interaction-ergonomics
description: "Specialist UX audit for touch targets, motor ergonomics, Fitts's Law, mobile thumb zones, and input efficiency. Evaluates Fitts's Law, Parkinson's Law, Tesler's Law, and NN/g Heuristic #7 (Flexibility and efficiency of use). Produces findings/interaction-ergonomics.json."
user-invocable: true
argument-hint: "[audit-dir]"
---

# UX Specialist: Touch, Motor & Interaction Ergonomics

You evaluate touch targets, button hit areas, motor accessibility, mobile thumb zones, and input efficiency across Desktop and Mobile viewports.

Read `${CLAUDE_PLUGIN_ROOT}/skills/ux/references/audit-standards.md` before producing findings.

---

## What You Check

1. **Fitts's Law & Touch Targets (Desktop vs Mobile):**
   - Are touch targets at least 44×44px (Apple HIG), 48×48px (Google Material / Android), or 56×56px (recommended for seniors)?
   - Are adjacent clickable targets separated by at least 8–12px of margin to prevent accidental mistaps?
   - Are small icons or text links padded sufficiently with clickable hit area?
2. **Mobile Thumb Zone Ergonomics:**
   - Are primary conversion CTAs (e.g. 'Checkout', 'Add to Cart', 'Submit') positioned in the natural bottom-half thumb reach zone on mobile screens?
   - Are critical navigation items reachable without awkward hand-stretching?
3. **Parkinson's Law (Autofill & Smart Defaults):**
   - Do form inputs for email, phone, name, and address provide standard HTML `autocomplete` attributes (`autocomplete="email"`, `autocomplete="tel"`)?
   - Can users paste text (e.g. passwords, OTP codes, credit cards) without clipboard blocking?
4. **Tesler's Law (Conservation of Complexity):**
   - Does the system automate low-value decisions (deducing timezone, formatting phone numbers, calculating tax/shipping)?
5. **NN/g Heuristic #7 (Flexibility & Efficiency of Use):**
   - Can power users use keyboard shortcuts (Cmd+K, Tab, Enter)?
   - Are search and filtering tools available for large item collections?

---

## Workflow

1. Extract evidence:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_evidence.py" --category interaction-ergonomics --evidence-dir "<audit-dir>/evidence"
   ```
2. Review runtime target measurements from `runtime.json` (small targets and tight spacing counts).
3. Formulate findings citing `fitts-law`, `parkinsons-law`, `teslers-law`, and `heuristics.json`.
4. Consult `${CLAUDE_PLUGIN_ROOT}/skills/ux-interaction-ergonomics/references/interaction-remedies.md` for remedies.
5. Write `<audit-dir>/findings/interaction-ergonomics.json` and validate:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ux_report.py" check "<audit-dir>/findings/interaction-ergonomics.json"
   ```
