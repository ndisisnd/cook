---
last_reviewed: 2026-10-23
---
# React Component Patterns

Targets React 19.x. The patterns below are known; only decision rules and React 19 changes are kept.

## React 19 Changes

- `ref` is a regular prop on function components. Do not use `forwardRef` in new code.
- Render `<Context value={x}>` directly. Do not use `<Context.Provider>` in new code.
- Ref callbacks may return a cleanup function. Do not mutate DOM from an implicit-return arrow that returns a value.

```tsx
function Input({ ref, ...props }: React.ComponentProps<'input'>) {
  return <input ref={ref} {...props} />;
}
```

## Choosing a Pattern

| Need | Use |
|---|---|
| Caller controls what renders in fixed regions | Slots: `ReactNode` props, not drilled data |
| Related parts share hidden state (tabs, accordion, menu) | Compound components over one context |
| Caller decides how each item renders | Render prop (`renderItem`) with a `getKey` prop |
| Reusable logic | Custom hook. HOCs only to wrap a tree or interop with classes |
| Caller changes the element | Polymorphic `as` prop typed with `React.ElementType` and `ComponentPropsWithoutRef<T>` |

## Rules

- Compound components: throw from the context hook when used outside the parent; compose with `Object.assign` or named exports.
- Context `value` that is an object, array, or function must be stable: memoize it or split contexts. With React Compiler enabled it memoizes inline values; without, wrap manually.
- Custom widgets must meet the accessibility contract: expanded state and labelled regions for accordions; focus trap, `Escape`, title label, and focus return for dialogs; roving keyboard navigation and ARIA roles for menus and tabs. Prefer proven accessible primitives over hand-rolled ones.
- Prefer controlled inputs for forms that need validation, disabled states, or reset. Use uncontrolled (`ref`/`FormData`) for file inputs and submit-time-only values.
- Boolean props use shorthand for `true` (`<Modal isOpen />`). Replace several booleans that allow impossible states with one `variant` prop or a discriminated union.
- Use a ternary or explicit `null` instead of `cond && <X />` when `cond` can be `0`, because React renders `0`.
