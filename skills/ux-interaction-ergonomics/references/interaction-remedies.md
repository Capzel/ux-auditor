# Touch & Motor Ergonomics Code Remedies

Concrete ❌ / ✅ patterns for resolving touch target sizing, spacing, and autofill efficiency.

---

## 1. Undersized Mobile Touch Target (Fitts's Law)

❌ **Problem:** Button is styled with `h-8` (32px), failing mobile touch criteria and causing mistaps.

```jsx
<button className="h-8 px-2 text-xs bg-blue-600 text-white rounded">
  Add to Cart
</button>
```

✅ **Remedy:** Ensure minimum 44px (or 48px) hit box using padding or min-h:

```jsx
<button className="min-h-[44px] min-w-[44px] sm:min-h-[48px] px-4 py-2.5 text-sm font-medium bg-blue-600 text-white rounded-lg active:scale-95 transition-transform">
  Add to Cart
</button>
```

---

## 2. Tight Target-to-Target Spacing (Accidental Mistaps)

❌ **Problem:** Edit and Delete icons placed 2px apart. Seniors and mobile users frequently hit Delete by mistake.

```html
<div class="flex gap-0.5">
  <button class="p-1"><EditIcon /></button>
  <button class="p-1"><DeleteIcon /></button>
</div>
```

✅ **Remedy:** Separate interactive targets with at least 8–12px margin.

```html
<div class="flex items-center gap-3">
  <button class="p-2.5 rounded-md hover:bg-gray-100" aria-label="Edit item">
    <EditIcon />
  </button>
  <button class="p-2.5 rounded-md hover:bg-red-50 text-red-600" aria-label="Delete item">
    <DeleteIcon />
  </button>
</div>
```

---

## 3. Missing Autocomplete Attributes (Parkinson's Law)

❌ **Problem:** User must manually type their name, email, and address.

```html
<input type="text" name="email" />
<input type="text" name="phone" />
<input type="text" name="shipping_address" />
```

✅ **Remedy:** Add standard HTML5 autocomplete tokens for browser and password manager integration.

```html
<input type="email" name="email" autocomplete="email" />
<input type="tel" name="phone" autocomplete="tel" />
<input type="text" name="shipping_address" autocomplete="shipping street-address" />
<input type="text" name="postal_code" autocomplete="shipping postal-code" />
```
