"""Shared helpers, constants, and evaluation formulas for ux-auditor.
Standard library only, Python 3.8+.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_ROOT / "data"

CATEGORIES = [
    "visual-hierarchy",
    "interaction-ergonomics",
    "navigation-wayfinding",
    "system-feedback",
    "error-resilience",
    "accessibility-inclusion",
    "content-clarity",
]

CATEGORY_TITLES = {
    "visual-hierarchy": "Visual Hierarchy & Cognitive Load",
    "interaction-ergonomics": "Touch, Motor & Interaction Ergonomics",
    "navigation-wayfinding": "Navigation, Wayfinding & Consistency",
    "system-feedback": "Feedback, Status & Performance",
    "error-resilience": "Error Prevention & Recovery",
    "accessibility-inclusion": "Accessibility & Age Inclusivity",
    "content-clarity": "Content Clarity & Real-World Match",
}

# Category weights sum to 100
CATEGORY_WEIGHTS = {
    "visual-hierarchy": 15,
    "interaction-ergonomics": 20,
    "navigation-wayfinding": 15,
    "system-feedback": 15,
    "error-resilience": 15,
    "accessibility-inclusion": 10,
    "content-clarity": 10,
}

PREFIX = {
    "visual-hierarchy": "VIS",
    "interaction-ergonomics": "ERG",
    "navigation-wayfinding": "NAV",
    "system-feedback": "FDB",
    "error-resilience": "ERR",
    "accessibility-inclusion": "ACC",
    "content-clarity": "CLR",
}

STATUSES = ("fail", "warn", "unverified", "pass")
SEVERITIES = ("critical", "high", "medium", "low", "info")
CONFIDENCES = ("confirmed", "likely", "possible")
TIERS = ("static", "runtime", "questionnaire")
VIEWPORTS = ("desktop", "mobile", "both")
AGE_PERSONAS = ("young", "adult", "senior", "all")
EFFORTS = ("S", "M", "L")

SEV_POINTS = {"critical": 35, "high": 20, "medium": 10, "low": 4, "info": 0}
CONF_MULT = {"confirmed": 1.0, "likely": 0.8, "possible": 0.5}
STATUS_MULT = {"fail": 1.0, "warn": 0.5}
SEV_RANK = {s: i for i, s in enumerate(SEVERITIES)}
STATUS_RANK = {s: i for i, s in enumerate(STATUSES)}
EFFORT_RANK = {"S": 0, "M": 1, "L": 2}
SEV_ICON = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}

# Viewport device dimensions
DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
MOBILE_VIEWPORT = {"width": 390, "height": 844}  # Modern mobile flagship (iPhone/Android standard)


def load_json(name: str) -> dict:
    """Load JSON from data/ directory."""
    with open(DATA_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


def get_laws_index() -> Dict[str, dict]:
    """Map law ID to law data dict."""
    return {law["id"]: law for law in load_json("laws_of_ux.json")["laws"]}


def get_heuristics_index() -> Dict[str, dict]:
    """Map heuristic ID to heuristic data dict."""
    return {h["id"]: h for h in load_json("heuristics.json")["heuristics"]}


def get_personas_index() -> Dict[str, dict]:
    """Map persona ID to persona data dict."""
    return {p["id"]: p for p in load_json("personas.json")["personas"]}


# --------------------------------------------------------------------------- #
# Rating & Usability Score Calculations
# --------------------------------------------------------------------------- #

def rating(score: Optional[float]) -> str:
    """Return UX rating label from score 0-100."""
    if score is None:
        return "Not assessed"
    if score >= 90:
        return "Optimal (Excellent UX)"
    if score >= 75:
        return "Good, with minor friction"
    if score >= 50:
        return "Needs improvement (Noticeable friction)"
    return "High friction (Severe UX defects)"


def rating_color(score: Optional[float]) -> str:
    """Return CSS hex color for score."""
    if score is None:
        return "#9ca3af"
    if score >= 90:
        return "#10b981"  # Emerald green
    if score >= 75:
        return "#3b82f6"  # Blue
    if score >= 50:
        return "#f59e0b"  # Amber
    return "#ef4444"      # Red


# --------------------------------------------------------------------------- #
# WCAG Color Contrast Mathematics
# --------------------------------------------------------------------------- #

def parse_css_color(color_str: str) -> Optional[Tuple[int, int, int]]:
    """Parse hex, rgb(), or rgba() string to (r, g, b) tuple 0-255."""
    if not color_str or not isinstance(color_str, str):
        return None
    s = color_str.strip().lower()

    # Hex: #rgb or #rrggbb
    if s.startswith("#"):
        hex_val = s[1:]
        if len(hex_val) == 3:
            return tuple(int(c * 2, 16) for c in hex_val)  # type: ignore
        elif len(hex_val) in (6, 8):
            return (int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16))

    # rgb(r, g, b) or rgba(r, g, b, a)
    m = re.match(r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", s)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # Named basic colors fallback
    NAMED_COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "transparent": (255, 255, 255),
        "gray": (128, 128, 128),
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "green": (0, 128, 0),
    }
    return NAMED_COLORS.get(s)


def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance according to WCAG 2.1 specification."""
    def channel_lum(val: int) -> float:
        s = val / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    rs = channel_lum(r)
    gs = channel_lum(g)
    bs = channel_lum(b)
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs


def calculate_contrast_ratio(fg: Tuple[int, int, int], bg: Tuple[int, int, int]) -> float:
    """Calculate WCAG contrast ratio between foreground and background (1.0 to 21.0)."""
    l1 = relative_luminance(*fg)
    l2 = relative_luminance(*bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    ratio = (lighter + 0.05) / (darker + 0.05)
    return round(ratio, 2)


# --------------------------------------------------------------------------- #
# Fitts's Law & Touch Target Dimensions
# --------------------------------------------------------------------------- #

def evaluate_touch_target(width: float, height: float, spacing: float = 8.0, persona: str = "adult") -> Dict[str, any]:
    """Evaluate touch target against platform guidelines and age personas."""
    # Base thresholds:
    # Young: min 44x44, spacing >= 6
    # Adult: min 44x44 (Apple) / 48x48 (Material), spacing >= 8
    # Senior: min 48x48 (rec 56x56), spacing >= 12
    min_size = 48.0 if persona == "senior" else 44.0
    rec_size = 56.0 if persona == "senior" else 48.0
    min_space = 12.0 if persona == "senior" else (6.0 if persona == "young" else 8.0)

    is_compliant = (width >= min_size) and (height >= min_size)
    is_optimal = (width >= rec_size) and (height >= rec_size)
    spacing_compliant = spacing >= min_space

    status = "pass" if is_optimal else ("warn" if is_compliant else "fail")

    return {
        "width": width,
        "height": height,
        "spacing": spacing,
        "is_compliant": is_compliant,
        "is_optimal": is_optimal,
        "spacing_compliant": spacing_compliant,
        "status": status,
        "required_min_px": min_size,
        "required_spacing_px": min_space,
    }


# --------------------------------------------------------------------------- #
# Code Sanitization & Evidence Helpers
# --------------------------------------------------------------------------- #

_SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key|secret|token|password|auth|bearer)[\"'\s:=]+([a-zA-Z0-9_\-\.]{12,})", re.I),
]


def mask_sensitive(text: str) -> str:
    """Mask any accidental tokens or passwords from source snippets."""
    res = text
    for pat in _SECRET_PATTERNS:
        res = pat.sub(r"\1: [REDACTED]", res)
    return res
