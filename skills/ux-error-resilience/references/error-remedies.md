# Error Resilience Code Remedies

Concrete ❌ / ✅ patterns for resolving form errors, forgiving formatting, and destructive safeguards.

---

## 1. Unguarded Destructive Delete Action (Error Prevention)

❌ **Problem:** Clicking a delete button immediately destroys data without confirmation.

```jsx
<button onClick={() => deleteProject(project.id)}>
  Delete Project
</button>
```

✅ **Remedy:** Guard with confirmation dialog and clear consequence explanation:

```jsx
function DeleteButton({ project, onDelete }) {
  const [showConfirm, setShowConfirm] = useState(false);

  return (
    <>
      <button
        onClick={() => setShowConfirm(true)}
        className="px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md font-medium"
      >
        Delete Project
      </button>

      {showConfirm && (
        <ConfirmDialog
          title="Delete Project?"
          message={`Are you sure you want to permanently delete "${project.name}"? This action cannot be undone.`}
          confirmLabel="Yes, Delete Permanently"
          isDestructive
          onConfirm={() => {
            onDelete(project.id);
            setShowConfirm(false);
          }}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </>
  );
}
```

---

## 2. Inflexible Phone Formatting (Postel's Law)

❌ **Problem:** Rejecting phone numbers that contain spaces or parentheses with a strict error.

```js
// Rejects "(555) 123-4567" or "+1 555 123 4567"
if (!/^\d{10}$/.test(phone)) {
  showError("Must be exactly 10 digits");
}
```

✅ **Remedy:** Sanitize and strip formatting automatically before validating:

```js
// Be liberal in what you accept
const cleanPhone = phone.replace(/[\s\-\(\)\.]/g, "");
if (!/^\+?\d{10,15}$/.test(cleanPhone)) {
  showError("Please enter a valid phone number (e.g. +1 555 123 4567)");
}
```
