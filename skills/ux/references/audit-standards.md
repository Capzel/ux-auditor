# UX Audit Standards & Methodology

Every skill and agent in `ux-auditor` must strictly adhere to these standards when inspecting interfaces, evaluating evidence, and formulating findings.

---

## 1. Evaluation Foundations

All evaluations are anchored in two foundational frameworks:
1. **The 21 Laws of UX** ([lawsofux.com](https://lawsofux.com/)):
   - *Heuristic Laws:* Fitts's Law, Hick's Law, Jakob's Law, Miller's Law, Parkinson's Law, Postel's Law, Tesler's Law.
   - *Gestalt Principles:* Law of Proximity, Law of Common Region, Law of Similarity, Law of Uniform Connectedness, Law of Prägnanz.
   - *Cognitive & Behavioral Principles:* Aesthetic-Usability Effect, Doherty Threshold (<400ms), Goal-Gradient Effect, Occam's Razor, Pareto Principle, Peak-End Rule, Serial Position Effect, Von Restorff Effect, Zeigarnik Effect.
2. **NN/g 10 Usability Heuristics for User Interface Design** ([nngroup.com](https://www.nngroup.com/articles/ten-usability-heuristics/)):
   1. Visibility of system status
   2. Match between system and real world
   3. User control and freedom
   4. Consistency and standards
   5. Error prevention
   6. Recognition rather than recall
   7. Flexibility and efficiency of use
   8. Aesthetic and minimalist design
   9. Help users recognize, diagnose, and recover from errors
   10. Help and documentation

---

## 2. Dual-Viewport Inspection Protocol

Interfaces must be audited across two distinct device paradigms:

| Viewport | Dimensions | Mode | Primary Focus |
|---|---|---|---|
| **Desktop** | 1440 × 900 | Mouse / Keyboard / Hover | Information density, visual hierarchy, keyboard focus rings (`:focus-visible`), command palettes, wide table responsiveness |
| **Mobile** | 390 × 844 | Touch Screen (`is_mobile=True`) | Fitts's Law touch target dimensions (≥44px/48px), target-to-target spacing (≥8px), thumb zone ergonomics, horizontal overflow blowout, zoom prevention |

### Rules for Viewport Findings:
- If a defect occurs exclusively on mobile (e.g. tap target overlap or horizontal scroll blowout), set `viewport: "mobile"`.
- If a defect occurs exclusively on desktop (e.g. missing keyboard focus outline or unstyled wide hover dropdown), set `viewport: "desktop"`.
- If a defect is architectural or responsive across both (e.g. missing form labels or low contrast body text), set `viewport: "both"`.

---

## 3. Age Cohort Simulation Framework

Interfaces must be evaluated through the lens of three demographic cohorts:

### 1. Digital Natives (13–24, Gen Z & Alpha)
- **Ergonomics:** Mobile-first, single-handed thumb interaction.
- **Cognitive:** Rapid visual scanning (<5s attention window), intolerance for dense text walls.
- **Latency:** Doherty Threshold strictly <300ms. Expects instant optimistic UI updates and loading skeletons.
- **Key Flags:** Sluggish transitions, rigid desktop forms ported to mobile, lack of social/autofill sign-ins.

### 2. Working Adults (25–59)
- **Ergonomics:** Cross-platform (switches between desktop multi-tab and mobile).
- **Cognitive:** Goal-driven, values efficiency and control. Intolerant of forced time waste (Parkinson's Law).
- **Key Flags:** Inability to paste passwords, disabled autocomplete, loss of multi-step wizard state on back button, missing search/filter tools.

### 3. Older Adults & Seniors (60+)
- **Physiological Factors:**
  - *Vision:* Presbyopia, reduced contrast sensitivity. Body font must be ≥16px (recommended 18px). Contrast ratio must meet WCAG AAA (≥7:1 for normal text).
  - *Motor Control:* Tremors, reduced hand dexterity. Fitts's Law is critical: touch targets must be ≥48×48px (recommended 56×56px) with at least 12px spacing between interactive neighbors.
  - *Cognitive:* Heavy reliance on recognition over recall. No mystery-meat icons; icons must have visible text labels.
- **Key Flags:** Small touch targets, faint gray text on white (`#9ca3af`), disabled viewport zooming (`user-scalable=no`), auto-advancing carousels without pause controls, cryptic error messages.

---

## 4. Evidence Tiers & Verification

Findings must cite verified evidence from one of three tiers:
1. `static`: Concrete file path, line number, and code snippet from `ux_scan.py`.
2. `runtime`: Real rendered DOM metrics from `ux_runtime.py` (DOM selector, bounding box dimensions in px, computed contrast ratio, screenshot reference).
3. `questionnaire`: Explicit context answers provided by the user during scoping.

**Never manufacture or guess evidence.** If runtime inspection was not executed (e.g. no URL provided), mark runtime checks as not run and evaluate based on static code.

---

## 5. Severity & Scoring Rubric

Severity defines the degree of user friction and abandonment risk:

| Severity | Deduction Points | Definition | Examples |
|---|---|---|---|
| **Critical** | 35 pts | Complete task blocker or severe accessibility violation | Zooming disabled on mobile; broken horizontal scroll blowout; unclosable modal trap |
| **High** | 20 pts | Major friction or high probability of error | Touch targets < 36px in primary funnel; form inputs without labels; submit button without loading state |
| **Medium** | 10 pts | Noticeable friction or cognitive strain | Form with >12 unchunked fields; low contrast helper text; missing autocomplete attributes |
| **Low** | 4 pts | Minor cosmetic inconsistency or quality-of-life issue | Missing image alt attribute; slight target spacing shortfall (6px instead of 8px) |
| **Info** | 0 pts | Informational observation or best practice advice | Opportunity to add keyboard shortcut or optimistic UI |

### Score Interpretation:
- **90–100:** Optimal (Excellent UX, intuitive and accessible)
- **75–89:** Good, with minor friction
- **50–74:** Needs improvement (Noticeable friction, task abandonment risk)
- **< 50:** High friction (Severe usability defects across core funnels)

---

## 6. Category Ownership Matrix

To avoid duplicate findings across specialists, each issue is owned by a single primary category:

| Issue Type | Primary Category |
|---|---|
| Information chunking, layout balance, whitespace, cards | `visual-hierarchy` |
| Touch target dimensions, button hit-boxes, mobile thumb zones | `interaction-ergonomics` |
| Menus, breadcrumbs, search, back button, mental models | `navigation-wayfinding` |
| Loading spinners, skeletons, Doherty latency, success toasts | `system-feedback` |
| Form validation, inline errors, input masking, destructive safeguards | `error-resilience` |
| Color contrast, font size, viewport zoom, senior ergonomics | `accessibility-inclusion` |
| Jargon vs plain language, icon labels, empty states, tooltips | `content-clarity` |
