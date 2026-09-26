# UX Audit Coverage Matrix

Comprehensive mapping of the **21 Laws of UX**, the **NN/g 10 Usability Heuristics**, and **Age Cohort Ergonomics** across the 7 audit categories.

---

## 1. Laws of UX to Category Mapping

| Law of UX ID | Official Name | Category | Primary Category Owner | Evaluation Focus |
|---|---|---|---|---|
| `fitts-law` | Fitts's Law | Heuristic | `interaction-ergonomics` | Touch targets (≥44/48px), target spacing, mobile thumb zones |
| `hicks-law` | Hick's Law | Heuristic | `visual-hierarchy` | Limiting choices, menu complexity, progressive disclosure |
| `jakobs-law` | Jakob's Law | Heuristic | `navigation-wayfinding` | Common web conventions, logo home link, standard search |
| `millers-law` | Miller's Law | Heuristic | `visual-hierarchy` | Chunking content, form lengths, top-level nav item counts (5–7) |
| `parkinsons-law` | Parkinson's Law | Heuristic | `interaction-ergonomics` | Reducing input time via autofill, smart defaults, address lookup |
| `postels-law` | Postel's Law | Heuristic | `error-resilience` | Forgiving input formatting (phones, cards, dates) |
| `teslers-law` | Tesler's Law | Heuristic | `interaction-ergonomics` | Absorbing system complexity (automatic timezones, currency, tax) |
| `proximity-law` | Law of Proximity | Gestalt | `visual-hierarchy` | Label-to-input margins vs inter-field gaps, card clustering |
| `common-region-law` | Law of Common Region | Gestalt | `visual-hierarchy` | Card borders, distinct background regions, modal overlays |
| `similarity-law` | Law of Similarity | Gestalt | `navigation-wayfinding` | Consistent button variants, primary vs secondary vs destructive |
| `uniform-connectedness-law` | Law of Uniform Connectedness | Gestalt | `navigation-wayfinding` | Stepper lines, breadcrumb arrows, tab anchor indicators |
| `pragnanz-law` | Law of Prägnanz | Gestalt | `visual-hierarchy` | Geometric simplicity, recognizable iconography |
| `aesthetic-usability-effect` | Aesthetic-Usability Effect | Cognitive | `visual-hierarchy` | Visual polish, baseline alignment, typography harmony |
| `doherty-threshold` | Doherty Threshold | Cognitive | `system-feedback` | Response times <400ms, optimistic UI, skeleton loaders |
| `goal-gradient-effect` | Goal-Gradient Effect | Cognitive | `system-feedback` | Progress bars, percentage indicators, endowed progress |
| `occams-razor` | Occam's Razor | Principle | `visual-hierarchy` | Removing redundant controls, clutter elimination |
| `pareto-principle` | Pareto Principle | Principle | `navigation-wayfinding` | Prioritizing the core 20% critical user journeys |
| `peak-end-rule` | Peak-End Rule | Cognitive | `system-feedback` | Celebratory success states, helpful 404/500 error pages |
| `serial-position-effect` | Serial Position Effect | Cognitive | `navigation-wayfinding` | Placing key items at start/end of nav bars and pricing tables |
| `von-restorff-effect` | Von Restorff Effect | Cognitive | `visual-hierarchy` | Isolated primary CTA styling, 'Recommended' plan badges |
| `zeigarnik-effect` | Zeigarnik Effect | Cognitive | `system-feedback` | Draft saving reminders, profile completion indicators |

---

## 2. NN/g 10 Usability Heuristics Mapping

| Heuristic # | Name | Category Owner | Key Checks |
|---|---|---|---|
| **#1** | Visibility of system status | `system-feedback` | Spinners, skeletons, disabled submit buttons, progress bars |
| **#2** | Match between system and real world | `content-clarity` | User language, real-world metaphors, no raw database errors |
| **#3** | User control and freedom | `navigation-wayfinding` | Escape closes modals, Undo support, back button retains state |
| **#4** | Consistency and standards | `navigation-wayfinding` | Design system tokens, uniform button terminology, platform standards |
| **#5** | Error prevention | `error-resilience` | Destructive action confirmation dialogs, input constraints, client masks |
| **#6** | Recognition rather than recall | `visual-hierarchy` | Persistent form labels, visible options, contextual hints |
| **#7** | Flexibility and efficiency of use | `interaction-ergonomics` | Keyboard shortcuts, command palettes, filters, paste support |
| **#8** | Aesthetic and minimalist design | `visual-hierarchy` | Generous whitespace, scannable copy, zero visual noise |
| **#9** | Help users recognize & recover from errors | `error-resilience` | Plain-language error messages, inline placement, constructive fix |
| **#10**| Help and documentation | `content-clarity` | Contextual tooltips, informative empty states, searchable help |

---

## 3. Age Cohort Evaluation Matrix

| Criterion | Digital Natives (Gen Z/Alpha, 13–24) | Working Adults (25–59) | Older Adults & Seniors (60+) |
|---|---|---|---|
| **Primary Device** | Mobile Touchscreen First | Cross-Device (Desktop & Mobile) | Tablets, Desktop, Large Mobile |
| **Touch Target Size** | Min 44×44px | Min 44×44px (rec 48px) | Min 48×48px (rec 56px) |
| **Target Spacing** | Min 6px | Min 8px | Min 12px (prevents tremors/mistaps) |
| **Minimum Font Size**| 14px body | 15–16px body | 16–18px body (WCAG AAA) |
| **Contrast Ratio** | 4.5:1 | 4.5:1 | 7.0:1 (high contrast for presbyopia) |
| **Patience / Doherty**| < 300ms feedback | < 400ms feedback | < 600ms feedback |
| **Memory Load** | Rapid visual scanning, cards | Tab switching, search/filters | Heavy recognition over recall, explicit labels |
| **Zoom Requirement**| App standard | Responsive scale | Viewport zoom mandatory (no `user-scalable=no`) |
