# System Feedback Code Remedies

Concrete ❌ / ✅ patterns for resolving feedback, loading latency, and progress indicators.

---

## 1. Async Submit Lacking Loading State (Doherty Threshold & Visibility)

❌ **Problem:** Button remains active with no indicator during 2-second API submission. User clicks repeatedly.

```jsx
<form onSubmit={handleSubmit}>
  <button type="submit" className="bg-blue-600 text-white px-4 py-2">
    Save Changes
  </button>
</form>
```

✅ **Remedy:** Disable button and show spinner immediately on submission:

```jsx
<button
  type="submit"
  disabled={isSubmitting}
  className="inline-flex items-center justify-center gap-2 min-h-[44px] px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-lg transition-colors"
>
  {isSubmitting ? (
    <>
      <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span>Saving changes...</span>
    </>
  ) : (
    <span>Save Changes</span>
  )}
</button>
```

---

## 2. Multi-Step Form Without Progress (Goal-Gradient Effect)

❌ **Problem:** Multi-step wizard has no indicator of current step or remaining steps.

```jsx
<div>
  <h2>Step Two: Shipping</h2>
  <ShippingFields />
</div>
```

✅ **Remedy:** Render a clear step indicator with completed checkpoints:

```jsx
<div className="mb-6">
  <div className="flex justify-between text-xs font-semibold text-gray-500 mb-2">
    <span className="text-indigo-600">1. Account</span>
    <span className="text-indigo-600">2. Shipping (Current)</span>
    <span>3. Payment</span>
    <span>4. Review</span>
  </div>
  <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
    <div className="bg-indigo-600 h-full rounded-full transition-all duration-300" style={{ width: "50%" }} />
  </div>
</div>
```
