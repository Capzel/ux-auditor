# Findings JSON Schema Contract

Every specialist agent produces a findings fragment at `<audit-dir>/findings/<category>.json`. The orchestrator merges these into `<audit-dir>/audit-data.json`.

---

## Category Fragment Schema (`findings/<category>.json`)

```json
{
  "category": "interaction-ergonomics",
  "summary": "Evaluation of touch targets, button hit areas, and mobile thumb zone ergonomics.",
  "findings": [
    {
      "title": "Mobile primary checkout CTA smaller than 44px minimum touch target",
      "status": "fail",
      "severity": "high",
      "confidence": "confirmed",
      "evidence_tier": "runtime",
      "viewport": "mobile",
      "personas_affected": ["senior", "young", "adult"],
      "laws": ["fitts-law"],
      "heuristics": ["consistency-and-standards", "flexibility-and-efficiency-of-use"],
      "impact": "On mobile devices, users must tap with extreme precision. Older adults with tremors or reduced motor control experience frequent missed taps and frustration.",
      "evidence": [
        {
          "selector": "button.checkout-btn",
          "url": "http://localhost:3000/cart",
          "note": "Measured 32px height x 110px width with 4px margin to cancel button"
        },
        {
          "file": "components/CartDrawer.tsx",
          "line": 48,
          "snippet": "<button className=\"h-8 px-2 text-sm bg-indigo-600\">Checkout</button>"
        }
      ],
      "remedy": {
        "summary": "Increase button height to at least 48px on mobile and provide 12px vertical spacing to adjacent buttons.",
        "effort": "S",
        "code": "<button className=\"min-h-[48px] px-4 py-3 text-base bg-indigo-600 rounded-lg\">Checkout</button>"
      }
    }
  ]
}
```

---

## Required Fields by Status

| Field | Type | Allowed Values / Constraints | Required For |
|---|---|---|---|
| `title` | string | Non-empty summary | All statuses |
| `status` | string | `"fail"`, `"warn"`, `"unverified"`, `"pass"` | All statuses |
| `severity` | string | `"critical"`, `"high"`, `"medium"`, `"low"`, `"info"` | All statuses |
| `confidence` | string | `"confirmed"`, `"likely"`, `"possible"` | All statuses |
| `evidence_tier` | string | `"static"`, `"runtime"`, `"questionnaire"` | All statuses |
| `viewport` | string | `"desktop"`, `"mobile"`, `"both"` | All statuses |
| `personas_affected`| array | `["young"]`, `["adult"]`, `["senior"]`, `["all"]` | All statuses |
| `laws` | array | Valid IDs from `data/laws_of_ux.json` (e.g. `fitts-law`) | Required for `fail`, `warn` |
| `heuristics` | array | Valid IDs from `data/heuristics.json` | Required for `fail`, `warn` |
| `impact` | string | Clear explanation of user harm and friction | Required for `fail`, `warn` |
| `evidence` | array | At least one item with `file`, `selector`, `url`, or `note` | Required for `fail`, `warn` |
| `remedy.summary` | string | Concrete actionable fix description | Required for `fail`, `warn` |
| `remedy.effort` | string | `"S"`, `"M"`, `"L"` | Required for `fail`, `warn` |

---

## Metadata Schema (`meta.json`)

Written by orchestrator during Phase 0:

```json
{
  "project": "my-web-app",
  "path": "/absolute/path/to/project",
  "url": "http://localhost:3000",
  "date": "2026-09-26",
  "stack": ["React", "Next.js", "Tailwind CSS"],
  "evidence_tiers": {
    "static": true,
    "runtime": true,
    "questionnaire": false
  },
  "executive_summary": "Overall UX score is 78/100 (Good, with minor friction). Primary friction occurs on mobile touch targets and low contrast text for seniors.",
  "target_personas": ["young", "adult", "senior"],
  "limitations": []
}
```
