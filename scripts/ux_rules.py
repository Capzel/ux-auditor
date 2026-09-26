"""Static UX code rules mapping source patterns to Laws of UX and NN/g Heuristics.
Standard library only, Python 3.8+.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional


class UXRule:
    def __init__(
        self,
        rule_id: str,
        category: str,
        title: str,
        severity: str,
        confidence: str,
        laws: List[str],
        heuristics: List[str],
        personas_affected: List[str],
        description: str,
        remedy: str,
        pattern: Optional[str] = None,
        compiled_regex: Optional[re.Pattern] = None,
        file_patterns: Optional[List[str]] = None,
    ):
        self.rule_id = rule_id
        self.category = category
        self.title = title
        self.severity = severity
        self.confidence = confidence
        self.laws = laws
        self.heuristics = heuristics
        self.personas_affected = personas_affected
        self.description = description
        self.remedy = remedy
        self.pattern = pattern
        self.compiled_regex = compiled_regex or (re.compile(pattern, re.IGNORECASE | re.DOTALL) if pattern else None)
        self.file_patterns = file_patterns or [".html", ".jsx", ".tsx", ".vue", ".svelte", ".js", ".ts", ".css", ".scss"]

    def to_dict(self) -> Dict:
        return {
            "id": self.rule_id,
            "category": self.category,
            "title": self.title,
            "severity": self.severity,
            "confidence": self.confidence,
            "laws": self.laws,
            "heuristics": self.heuristics,
            "personas_affected": self.personas_affected,
            "description": self.description,
            "remedy": self.remedy,
        }


# --------------------------------------------------------------------------- #
# Static Rules Collection
# --------------------------------------------------------------------------- #

RULES: List[UXRule] = [
    # 1. Fitts's Law / Touch Targets
    UXRule(
        rule_id="UX-FITTS-SMALL-BUTTON",
        category="interaction-ergonomics",
        title="Interactive target smaller than minimum 44px/48px touch guideline",
        severity="high",
        confidence="likely",
        laws=["fitts-law"],
        heuristics=["consistency-and-standards", "flexibility-and-efficiency-of-use"],
        personas_affected=["senior", "young", "adult"],
        description="Buttons or clickable controls are styled with heights below 36px (e.g., h-6, h-7, h-8, or height: 24px) without compensation padding. This causes frequent tap errors, particularly on mobile touchscreens and for older adults with reduced motor precision.",
        remedy="Increase button hit-area to at least 44x44px (iOS) or 48x48px (Android/WCAG 2.5.5). In Tailwind, use min-h-[44px] min-w-[44px] or add touch-target padding (p-3).",
        pattern=r"(class(?:Name)?=[\"'][^\"']*\b(h-[5-8]|w-[5-8]|py-0\.5|py-1)\b[^\"']*(?:btn|button|clickable)[\"']|style=[\"'][^\"']*(?:height|min-height)\s*:\s*(?:1[0-9]|2[0-9]|3[0-2])px)",
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".svelte", ".css", ".scss"],
    ),

    # 2. Viewport Zoom Disabled
    UXRule(
        rule_id="UX-RESP-ZOOM-DISABLED",
        category="accessibility-inclusion",
        title="Viewport zooming is disabled (user-scalable=no or maximum-scale=1)",
        severity="critical",
        confidence="confirmed",
        laws=["aesthetic-usability-effect"],
        heuristics=["user-control-and-freedom", "flexibility-and-efficiency-of-use"],
        personas_affected=["senior"],
        description="The meta viewport tag restricts zooming (user-scalable=no, user-scalable=0, or maximum-scale=1.0). This prevents seniors and users with visual impairments from magnifying text, violating WCAG 1.4.4.",
        remedy="Remove 'user-scalable=no' and 'maximum-scale=1.0' from your <meta name='viewport'> tag. Allow users to pinch-to-zoom freely up to at least 200%.",
        pattern=r"<meta\s+[^>]*name=[\"']viewport[\"'][^>]*content=[\"'][^\"']*(?:user-scalable\s*=\s*(?:no|0)|maximum-scale\s*=\s*1(?:\.0)?)",
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".php"],
    ),

    # 3. Focus Indicator Stripped
    UXRule(
        rule_id="UX-ACC-OUTLINE-NONE",
        category="accessibility-inclusion",
        title="Keyboard focus indicator stripped without custom focus ring",
        severity="high",
        confidence="likely",
        laws=["jakobs-law"],
        heuristics=["visibility-of-system-status", "flexibility-and-efficiency-of-use"],
        personas_affected=["adult", "senior"],
        description="CSS disables standard browser focus outlines (outline: none or outline: 0) without defining a visible replacement focus style. Keyboard navigation users cannot see where active focus is on the page.",
        remedy="Replace 'outline: none' with a prominent :focus-visible style: 'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary'.",
        pattern=r"(?:outline\s*:\s*(?:none|0)|focus:(?:outline-none|ring-0))\b",
        file_patterns=[".css", ".scss", ".jsx", ".tsx", ".vue", ".svelte", ".html"],
    ),

    # 4. Form Input Lacking Label
    UXRule(
        rule_id="UX-ERR-UNLABELED-INPUT",
        category="error-resilience",
        title="Form input field lacks persistent label or accessible name",
        severity="high",
        confidence="likely",
        laws=["recognition-rather-than-recall", "postels-law"],
        heuristics=["recognition-rather-than-recall", "error-prevention"],
        personas_affected=["senior", "adult"],
        description="Form inputs rely solely on placeholder attributes without an associated <label>, aria-label, or aria-labelledby. Placeholders disappear once text is typed, leaving users unable to verify what the field asks for.",
        remedy="Provide an explicit <label for='inputId'> above or next to the input. If visually hidden for minimal design, use an accessible aria-label or sr-only class.",
        pattern=r"<input\s+(?![^>]*\b(?:type=[\"'](?:hidden|submit|button|image|checkbox|radio)[\"']|aria-label|aria-labelledby|id=[\"'][^\"']+[\"']))[^>]*placeholder=[\"'][^\"']+[\"'][^>]*>",
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".svelte"],
    ),

    # 5. Missing Autocomplete Attributes
    UXRule(
        rule_id="UX-ERG-MISSING-AUTOCOMPLETE",
        category="interaction-ergonomics",
        title="Personal data input missing HTML5 autocomplete attribute",
        severity="medium",
        confidence="likely",
        laws=["parkinsons-law", "teslers-law"],
        heuristics=["flexibility-and-efficiency-of-use", "error-prevention"],
        personas_affected=["young", "adult", "senior"],
        description="Form fields requesting standard personal data (email, name, street-address, tel) lack the autocomplete attribute. Users must manually type information that their browser or password manager could populate instantly.",
        remedy="Add standard autocomplete attributes: autocomplete='email', autocomplete='name', autocomplete='tel', autocomplete='street-address'.",
        pattern=r"<input\s+[^>]*(?:type=[\"'](?:email|tel)[\"']|name=[\"'](?:email|phone|telephone|mobile|address|street|zip|postal)[\"'])(?![^>]*\bautocomplete=)[^>]*>",
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".svelte"],
    ),

    # 6. Submit Button Without Loading State
    UXRule(
        rule_id="UX-FDB-SUBMIT-NO-LOADING",
        category="system-feedback",
        title="Async form submit button lacks visual loading or disabled state",
        severity="medium",
        confidence="likely",
        laws=["doherty-threshold"],
        heuristics=["visibility-of-system-status", "error-prevention"],
        personas_affected=["young", "senior"],
        description="Form submit button is triggered by an async action but does not conditionally disable itself or render a spinner. This causes double-submissions and uncertainty when network latency exceeds 300ms.",
        remedy="Disable the submit button during submission (disabled={isSubmitting}) and display an inline spinner or 'Saving...' text.",
        pattern=r"(?:onSubmit|handleSubmit)\s*=\s*\{[^}]+\}[^>]*>\s*<button(?![^>]*\b(?:disabled|loading|isSubmitting|isLoading|spinner)\b)[^>]*type=[\"']submit[\"']",
        file_patterns=[".jsx", ".tsx", ".vue", ".svelte"],
    ),

    # 7. Unlabeled Icon Buttons
    UXRule(
        rule_id="UX-CLR-ICON-ONLY-BUTTON",
        category="content-clarity",
        title="Icon-only button has no text label or aria-label (mystery-meat icon)",
        severity="high",
        confidence="likely",
        laws=["jakobs-law", "pragnanz-law"],
        heuristics=["match-system-real-world", "recognition-rather-than-recall"],
        personas_affected=["senior", "adult"],
        description="Button contains only an SVG icon, FontAwesome icon, or graphical glyph with no accompanying text or aria-label. Screen readers cannot announce the action, and seniors or unfamiliar users cannot decipher its function.",
        remedy="Add aria-label='Description of action' to the button, or provide a visible text label adjacent to the icon.",
        pattern=r"<button(?![^>]*\baria-label=)[^>]*>\s*<(?:svg|i|span\s+class=[\"'][^\"']*(?:icon|fa-|lucide))[^>]*>.*?</(?:svg|i|span)>\s*</button>",
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".svelte"],
    ),

    # 8. Fixed Widths Causing Mobile Blowout
    UXRule(
        rule_id="UX-RESP-HARDCODED-WIDTH",
        category="visual-hierarchy",
        title="Fixed pixel width exceeds standard mobile screen bounds",
        severity="high",
        confidence="likely",
        laws=["aesthetic-usability-effect"],
        heuristics=["consistency-and-standards", "flexibility-and-efficiency-of-use"],
        personas_affected=["young", "senior"],
        description="Layout containers specify fixed pixel widths of 400px or greater (e.g. width: 600px, width: 800px) without max-width or responsive breakpoints. This triggers horizontal scrollbars and broken layouts on mobile screens.",
        remedy="Use max-w-full, percentage widths (w-full), or max-width: 100% with media queries (e.g. max-w-md w-full).",
        pattern=r"(?:style=[\"'][^\"']*width\s*:\s*[4-9]\d{2}px|class(?:Name)?=[\"'][^\"']*\bw-\[(?:[4-9]\d{2}|[1-9]\d{3})px\])",
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".svelte", ".css", ".scss"],
    ),

    # 9. Low Contrast Tailwind Utility Classes
    UXRule(
        rule_id="UX-ACC-LOW-CONTRAST-TEXT",
        category="accessibility-inclusion",
        title="Utility styling indicates low contrast text on light background",
        severity="medium",
        confidence="possible",
        laws=["aesthetic-usability-effect"],
        heuristics=["visibility-of-system-status", "help-users-recognize-errors"],
        personas_affected=["senior"],
        description="Text is styled with faint gray colors (text-gray-300, text-slate-300, text-zinc-300) without a dark background context. This falls below the WCAG 4.5:1 minimum contrast ratio, rendering it unreadable for older adults.",
        remedy="Use text-gray-700 or text-gray-600 for body copy on light backgrounds to ensure at least 4.5:1 (or 7:1 for seniors).",
        pattern=r"\btext-(?:gray|slate|zinc|neutral|stone)-(?:200|300|400)\b(?![^\"']*bg-(?:gray|slate|zinc|neutral|black|dark))",
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".svelte"],
    ),

    # 10. Massive Un-chunked Form
    UXRule(
        rule_id="UX-VIS-MASSIVE-FORM",
        category="visual-hierarchy",
        title="Extensive form fields on single screen without logical grouping or wizard",
        severity="medium",
        confidence="likely",
        laws=["millers-law", "hicks-law"],
        heuristics=["aesthetic-and-minimalist-design", "flexibility-and-efficiency-of-use"],
        personas_affected=["young", "adult", "senior"],
        description="A form contains more than 10 consecutive input fields without visual chunking (fieldsets, cards, accordions, or step wizards). This overwhelms working memory and triggers high abandonment rates.",
        remedy="Break extensive forms into logical 2-3 step wizards (e.g., Account -> Personal Details -> Payment) with a progress stepper, or group fields into labeled visual cards.",
        pattern=None,  # Handled by structure counter in ux_scan.py
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".svelte"],
    ),

    # 11. Destructive Action Without Confirmation
    UXRule(
        rule_id="UX-ERR-UNCONFIRMED-DESTRUCTIVE",
        category="error-resilience",
        title="Destructive action button (Delete/Remove) without confirmation guard",
        severity="high",
        confidence="likely",
        laws=["postels-law", "peak-end-rule"],
        heuristics=["error-prevention", "user-control-and-freedom"],
        personas_affected=["all"],
        description="A button triggering delete or destroy actions lacks an onClick confirmation dialog, modal prompt, or double-step safeguard. Accidental clicks result in permanent data loss.",
        remedy="Guard destructive actions with a modal dialog ('Are you sure you want to delete...?') or provide an immediate 'Undo' toast window.",
        pattern=r"<button\b[^>]*(?:delete|destroy|remove|purge)[^>]*onClick=\{(?:(?!(?:confirm|openModal|setShowModal|prompt))\w+)\}[^>]*>",
        file_patterns=[".jsx", ".tsx", ".vue", ".svelte"],
    ),

    # 12. Missing Image Alt Text
    UXRule(
        rule_id="UX-ACC-MISSING-IMG-ALT",
        category="accessibility-inclusion",
        title="Image element lacks an alt attribute",
        severity="low",
        confidence="confirmed",
        laws=["jakobs-law"],
        heuristics=["consistency-and-standards"],
        personas_affected=["senior"],
        description="An <img> tag has no alt attribute. Screen readers will read the raw image URL filename, causing confusion.",
        remedy="Add a meaningful alt='Description of image' attribute, or alt='' if the image is purely decorative.",
        pattern=r"<img\s+(?![^>]*\balt=)[^>]*>",
        file_patterns=[".html", ".jsx", ".tsx", ".vue", ".svelte"],
    ),
]


def get_rules_by_category(category: str) -> List[UXRule]:
    """Retrieve all static rules for a specific category."""
    return [r for r in RULES if r.category == category]


def get_rules_index() -> Dict[str, UXRule]:
    """Map rule ID to rule instance."""
    return {r.rule_id: r for r in RULES}
