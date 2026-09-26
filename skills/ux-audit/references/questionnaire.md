# UX Audit Scope Questionnaire

Used in **Phase 0** by the orchestrator. If the interactive `ask_question` tool is available, ask these questions in a single modal. Otherwise, present them in a single clear message.

---

## 1. Running Application URL
- **Question:** Is there a running local or staging web application URL available for live browser inspection?
- **Options:**
  - `http://localhost:3000` (or detected local dev server)
  - `Staging / Preview URL` (provide URL)
  - `Codebase only` (skip live browser inspection and run static analysis only)

## 2. Key Viewports to Prioritize
- **Question:** Which viewports should the audit inspect and report on?
- **Options:**
  - `Both Desktop (1440x900) and Mobile (390x844)` (Recommended)
  - `Mobile only (Smartphones)`
  - `Desktop only (Laptops & Desktops)`

## 3. Target Demographics & Age Simulation
- **Question:** Which age cohorts should be explicitly simulated for ergonomic and cognitive friction?
- **Options:**
  - `All cohorts: Gen Z (13-24), Adults (25-59), and Seniors (60+)` (Recommended)
  - `Seniors / Older Adults (focus on high contrast, large touch targets, motor ease)`
  - `Digital Natives / Youth (focus on mobile speed, gesture navigation, <300ms feedback)`
  - `General Working Adults (focus on keyboard shortcuts, efficiency, multi-tasking)`

## 4. Priority User Journeys
- **Question:** Are there specific critical user journeys or paths to test?
- **Options:**
  - `Standard public routes: Home, Onboarding/Signup, Login, Forms` (Recommended)
  - `E-commerce: Product catalog, Cart drawer, Checkout flow`
  - `SaaS / Dashboard: App layout, Data tables, Settings, Modals`
