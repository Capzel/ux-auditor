# Visual Hierarchy Code Remedies

Concrete ❌ / ✅ patterns for resolving cognitive load, chunking, and Gestalt layout violations.

---

## 1. Massive Unchunked Form (Miller's Law / Hick's Law)

❌ **Problem:** 15 form fields stacked continuously on a single screen without visual breaks.

```jsx
<form onSubmit={handleSave}>
  <input name="first_name" />
  <input name="last_name" />
  <input name="email" />
  <input name="company" />
  <input name="address" />
  {/* 10 more fields */}
  <button type="submit">Submit</button>
</form>
```

✅ **Remedy:** Chunk into visual cards or a multi-step stepper wizard with progress indication.

```jsx
<form onSubmit={handleSave} className="space-y-6 max-w-xl">
  {/* Card 1: Identity */}
  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
    <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">1. Personal Identity</h3>
    <div className="grid grid-cols-2 gap-4">
      <FormField label="First Name" name="first_name" />
      <FormField label="Last Name" name="last_name" />
    </div>
    <FormField label="Email" name="email" type="email" />
  </div>

  {/* Card 2: Billing & Shipping */}
  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
    <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">2. Billing Details</h3>
    <FormField label="Street Address" name="address" />
  </div>
  <button type="submit" className="w-full py-3 bg-indigo-600 text-white font-medium rounded-lg">Save & Continue</button>
</form>
```

---

## 2. Label Proximity Ambiguity (Law of Proximity)

❌ **Problem:** Label is equidistant from the preceding input and its own input.

```html
<!-- Ambiguous spacing: user cannot tell which label belongs to which input -->
<input class="mb-4">
<label class="mb-4">Billing City</label>
<input class="mb-4">
```

✅ **Remedy:** Ensure label-to-input gap (4–8px) is significantly smaller than field-to-field gap (20–24px).

```html
<div class="space-y-5">
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1.5">First Name</label>
    <input class="w-full rounded-md border-gray-300 px-3 py-2" />
  </div>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1.5">Last Name</label>
    <input class="w-full rounded-md border-gray-300 px-3 py-2" />
  </div>
</div>
```

---

## 3. Competing CTAs (Von Restorff Effect & Occam's Razor)

❌ **Problem:** Primary action blends in with secondary actions.

```html
<button class="bg-blue-600 text-white px-4 py-2">Save</button>
<button class="bg-blue-600 text-white px-4 py-2">Preview</button>
<button class="bg-blue-600 text-white px-4 py-2">Share</button>
```

✅ **Remedy:** Distinct visual hierarchy: one primary filled button, secondary outlined, tertiary ghost.

```html
<div class="flex items-center gap-3">
  <button class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-5 py-2.5 rounded-lg shadow-sm">
    Publish Now
  </button>
  <button class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium px-4 py-2.5 rounded-lg">
    Save Draft
  </button>
  <button class="text-gray-500 hover:text-gray-700 px-3 py-2 font-medium">
    Cancel
  </button>
</div>
```
