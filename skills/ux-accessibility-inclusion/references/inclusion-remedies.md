# Accessibility & Age Inclusivity Code Remedies

Concrete ❌ / ✅ patterns for resolving contrast, viewport zooming, and keyboard focus outlines.

---

## 1. Viewport Zoom Disabled (Critical Senior Blocker)

❌ **Problem:** Meta tag prevents users with low vision or presbyopia from zooming.

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
```

✅ **Remedy:** Remove restrictive zoom limits:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

---

## 2. Low Contrast Text on Light Background (WCAG Failure)

❌ **Problem:** `text-gray-400` on white produces 2.1:1 contrast ratio, unreadable for older adults.

```html
<p class="text-gray-400 text-sm">
  Please enter your account billing number to proceed.
</p>
```

✅ **Remedy:** Use darker gray token satisfying WCAG 2.1 AA (≥4.5:1) and AAA (≥7:1 for seniors):

```html
<p class="text-gray-700 text-base leading-relaxed">
  Please enter your account billing number to proceed.
</p>
```

---

## 3. Focus Indicator Stripped Without Replacement

❌ **Problem:** `outline: none` leaves keyboard and screen magnifier users blind to focus.

```css
button:focus, input:focus {
  outline: none;
}
```

✅ **Remedy:** Use accessible `:focus-visible` ring with offset:

```css
button:focus-visible, input:focus-visible {
  outline: 2px solid #4f46e5;
  outline-offset: 2px;
}
```
In Tailwind CSS:
```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2">
  Continue
</button>
```
