# ux-auditor

**A comprehensive UX & usability audit for web apps and codebases, based on the [21 Laws of UX](https://lawsofux.com/) and the [NN/g 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).**

Runs as a plugin in [Claude Code](https://claude.com/claude-code) and [Google Antigravity](https://github.com/google), installs into Gemini CLI, OpenAI Codex, and Cursor via standard `SKILL.md`, and executes standalone in Python and CI/CD pipelines without any AI agent.

---

> [!NOTE]
> Evaluates interfaces across **both Desktop (1440×900) and Mobile (390×844 touch) viewports**, and simulates age-specific friction across **Digital Natives (Gen Z/Alpha), Working Adults, and Older Adults (60+ Seniors)**.

---

## What It Does

- **Fitts's Law & Touch Targets:** Inspects real rendered bounding boxes via Playwright. Flags touch targets `<44px` (iOS) or `<48px` (Android/WCAG), detects tight spacing (`<8px`) causing accidental taps, and tests mobile thumb zone reachability.
- **Cognitive Load & Chunking:** Evaluates Miller's Law, Hick's Law, and Gestalt proximity. Flags forms with >10 unchunked fields, un-grouped select dropdowns, and ambiguous label-to-input associations.
- **Dual-Viewport Responsiveness:** Tests Desktop (1440×900) and Mobile (390×844) independently. Flags horizontal scroll blowouts (`scrollWidth > innerWidth`) and disabled viewport zooming (`user-scalable=no`).
- **Age Cohort Ergonomic Simulation:**
  - **Gen Z & Alpha (13–24):** Low patience thresholds (<300ms feedback latency), gesture ergonomics, visual scannability.
  - **Working Adults (25–59):** Task efficiency, keyboard navigation (`:focus-visible`), autofill compliance (Parkinson's Law), multi-step wizard state retention.
  - **Older Adults & Seniors (60+):** High contrast ratios (WCAG AAA ≥7:1), minimum body font size (≥16px), touch targets ≥48px with 12px margins, explicit text labels on all icons (no mystery-meat icons).
- **Feedback & Doherty Threshold (<400ms):** Flags async submit buttons missing loading spinners or disabled states, missing skeleton loaders, and uncelebrated success states.
- **Error Resilience (Postel's Law):** Verifies forgiving input handling (phone numbers, cards, dates), inline error guidance, and confirmation guards on destructive actions.
- **Scored Deliverables:** Generates `UX-AUDIT-REPORT.md`, a phased `ACTION-PLAN.md` (P0 Quick Wins, P1 Mobile & Ergonomics, P2 Polish), `personas-analysis.md`, and an interactive standalone `ux-audit-report.html` with 1-click print-to-PDF styles.

---

## Deliverables Generated

```
ux-audit/<project>-<date>/
├── UX-AUDIT-REPORT.md        full report: executive summary, usability score (0-100), heuristic breakdown, findings, laws cited, remedies
├── ACTION-PLAN.md            action plan in phases (P0 Quick Wins, P1 High Impact, P2 Polish) tagged by persona and viewport
├── personas-analysis.md      detailed friction and accessibility analysis across Young, Adult, and Senior age cohorts
├── ux-audit-report.html      standalone interactive HTML report with mobile/desktop filter and print-to-PDF styles
├── audit-data.json           machine-readable audit data with deterministic finding IDs (e.g. ERG-001, VIS-001)
├── findings/                 per-category findings JSON from each specialist agent
└── evidence/                 static scan signals, desktop & mobile runtime DOM metrics, and full-page screenshots
```

---

## Quick Start

### 1. Prerequisites

| Requirement | Purpose |
|---|---|
| Python 3.8 or newer | Core scanners and report pipeline (standard library only) |
| *Optional:* Playwright + Chromium | Runtime DOM inspection, contrast calculation, and mobile/desktop screenshots |

To enable headless browser inspection:

```bash
pip install playwright
python -m playwright install chromium
```

### 2. Install the Plugin

Inside Claude Code:

```bash
/plugin marketplace add Capzel/ux-auditor
/plugin install ux-auditor@ux-auditor
```

Inside Google Antigravity or Gemini CLI:

```bash
python3 scripts/install_skills.py --agent antigravity --scope user
```

For OpenAI Codex or other agents:

```bash
python3 scripts/install_skills.py --agent codex --scope project
```

*(See [docs/other-agents.md](docs/other-agents.md) for full agent installation guide).*

### 3. Run Your First Audit

Open your agent in the project you want to audit and run:

```
/ux audit . --url http://localhost:3000
```

---

## Commands

| Command | What it does |
|---|---|
| `/ux audit [path] [--url URL]` | Full audit: static code scan, desktop & mobile runtime checks, 7 parallel agents, cohort simulation, and scored report |
| `/ux scan [path]` | Fast static codebase scan in the terminal without browser or agents |
| `/ux runtime --url URL [--pages ...]` | Playwright runtime audit of Desktop & Mobile viewports with screenshots |
| `/ux mobile <url>` | Quick mobile viewport inspection (tap targets, overflow, thumb zone) |
| `/ux desktop <url>` | Quick desktop viewport inspection (focus rings, hover, density) |
| `/ux simulate [url] --persona senior\|young\|adult` | Simulate interface experience through a specific age cohort lens |
| `/ux report [audit-dir]` | Re-merge findings and re-render Markdown & HTML reports after edits |
| `/ux fix <FINDING-ID> [audit-dir]` | Plan and implement the remedy for one finding in code, then verify |
| `/ux laws [law-id]` | Browse the 21 Laws of UX with guidelines, violations, and remedies |
| `/ux heuristics [heuristic-id]` | Browse the NN/g 10 Usability Heuristics checklist |

---

## The 7 UX Audit Categories

| Category | Pillar Title | Laws of UX Covered | NN/g Heuristics |
|---|---|---|---|
| `visual-hierarchy` | Visual Hierarchy & Cognitive Load | Hick's Law, Miller's Law, Law of Proximity, Common Region, Prägnanz, Aesthetic-Usability Effect | #8 Aesthetic & minimalist, #6 Recognition vs recall |
| `interaction-ergonomics` | Touch, Motor & Interaction Ergonomics | Fitts's Law, Parkinson's Law, Tesler's Law | #7 Flexibility & efficiency, #4 Consistency |
| `navigation-wayfinding` | Navigation, Wayfinding & Consistency | Jakob's Law, Uniform Connectedness, Serial Position Effect, Pareto Principle | #3 User control & freedom, #4 Consistency |
| `system-feedback` | Feedback, Status & Performance | Doherty Threshold (<400ms), Goal-Gradient Effect, Peak-End Rule, Zeigarnik Effect | #1 Visibility of system status |
| `error-resilience` | Error Prevention & Recovery | Postel's Law, Peak-End Rule | #5 Error prevention, #9 Error recovery |
| `accessibility-inclusion` | Accessibility & Age Inclusivity | Aesthetic-Usability Effect, Senior Ergonomics | #7 Flexibility, #4 Standards |
| `content-clarity` | Content Clarity & Real-World Match | Jakob's Law, Occam's Razor | #2 Match system & real world, #10 Help & documentation |

---

## Example Finding

```markdown
### 🔴 [ERG-001] Mobile primary checkout CTA smaller than 44px minimum touch target

- **Severity:** `HIGH` | **Status:** `fail` | **Confidence:** `confirmed`
- **Category:** Touch, Motor & Interaction Ergonomics | **Viewport:** `mobile`
- **Personas Impacted:** senior, young, adult
- **Laws of UX Cited:** [Fitts's Law](https://lawsofux.com/fitts-s-law/)
- **NN/g Heuristic:** #7 Flexibility and efficiency of use, #4 Consistency and standards

**Why it matters:** On mobile screens, targets smaller than 44×44px cause high error rates. Older adults with tremors experience frequent missed taps and checkout abandonment.

**Evidence:**
- File: `components/CartDrawer.tsx:48`
  ```tsx
  <button className="h-8 px-2 text-sm bg-indigo-600">Checkout</button>
  ```
- DOM Selector: `button.checkout-btn` (Measured 32px height x 110px width with 4px margin)

**Remedy (Effort: `S`):** Increase button height to at least 48px on mobile and provide 12px vertical spacing to adjacent buttons.
```tsx
<button className="min-h-[48px] px-4 py-3 text-base bg-indigo-600 rounded-lg">Checkout</button>
```
```

---

## Running the Test Suite

```bash
python3 -m unittest discover -s tests -v
```

All scanners, mathematical contrast formulas, and report pipelines run with zero external dependencies on Python standard library.

---

## License

MIT © [Capzel](https://github.com/Capzel)