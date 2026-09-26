# Navigation & Wayfinding Code Remedies

Concrete ❌ / ✅ patterns for resolving navigation, mental models, and modal escape traps.

---

## 1. Logo Not Linking Home (Jakob's Law)

❌ **Problem:** Logo is a plain `<div>` or lacks an `href="/"`.

```jsx
<header>
  <div className="text-xl font-bold">Acme Corp</div>
</header>
```

✅ **Remedy:** Wrap in accessible link pointing to root:

```jsx
<header>
  <a href="/" aria-label="Acme Corp Home" className="flex items-center gap-2 font-bold text-xl text-gray-900">
    <LogoIcon className="h-6 w-6" />
    <span>Acme Corp</span>
  </a>
</header>
```

---

## 2. Modal Escape Trap (User Control & Freedom)

❌ **Problem:** Modal overlay has no close button and cannot be dismissed with Escape.

```jsx
function Modal({ children }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg">{children}</div>
    </div>
  );
}
```

✅ **Remedy:** Support Escape key, backdrop click, and visible close button:

```jsx
function Modal({ isOpen, onClose, children }) {
  useEffect(() => {
    const handleKey = (e) => e.key === "Escape" && onClose();
    if (isOpen) window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 relative" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={onClose}
          aria-label="Close dialog"
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
        >
          ✕
        </button>
        {children}
      </div>
    </div>
  );
}
```
