# Content Clarity Code Remedies

Concrete ❌ / ✅ patterns for resolving icon labelling, technical jargon, and empty states.

---

## 1. Icon-Only Button Without Accessible Name (Mystery-Meat Icon)

❌ **Problem:** Button has only an SVG icon with no text or `aria-label`.

```jsx
<button onClick={handleFilter} className="p-2 border rounded">
  <FilterIcon />
</button>
```

✅ **Remedy:** Add explicit `aria-label` or visible label:

```jsx
<button
  onClick={handleFilter}
  aria-label="Filter items by category"
  className="inline-flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
>
  <FilterIcon className="h-4 w-4" />
  <span className="hidden sm:inline">Filter</span>
</button>
```

---

## 2. Empty State Dead End (Help & Guidance)

❌ **Problem:** An empty table or list shows a blank screen or plain "No data".

```jsx
{items.length === 0 ? (
  <div>No items found</div>
) : (
  <ItemList items={items} />
)}
```

✅ **Remedy:** Provide an encouraging empty state with guidance and primary CTA:

```jsx
{items.length === 0 ? (
  <div className="text-center py-12 px-4 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 max-w-md mx-auto">
    <FolderPlusIcon className="mx-auto h-12 w-12 text-gray-400 mb-3" />
    <h3 className="text-base font-semibold text-gray-900 mb-1">No projects created yet</h3>
    <p className="text-sm text-gray-500 mb-6">
      Get started by creating your first project workspace. It takes less than a minute.
    </p>
    <button
      onClick={handleCreate}
      className="inline-flex items-center px-4 py-2.5 bg-indigo-600 text-white font-medium text-sm rounded-lg hover:bg-indigo-700 shadow-sm"
    >
      + Create First Project
    </button>
  </div>
) : (
  <ItemList items={items} />
)}
```
