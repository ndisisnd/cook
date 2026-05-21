# React Component Patterns

## Composition — Slot Pattern

Avoid prop drilling by accepting `ReactNode` slots. Callers control what renders inside each slot.

```tsx
function Layout({ children, aside }: { children: ReactNode; aside: ReactNode }) {
  return (
    <div className="grid">
      <aside>{aside}</aside>
      <main>{children}</main>
    </div>
  );
}
```

## Compound Components

Share implicit state between tightly related components without exposing it to callers.

```tsx
type AccordionContextValue = {
  activeIndex: number | null;
  setActiveIndex: (index: number | null) => void;
};

const AccordionContext = createContext<AccordionContextValue | null>(null);

function useAccordionContext() {
  const ctx = useContext(AccordionContext);
  if (!ctx) throw new Error('Accordion components must be used inside <Accordion>');
  return ctx;
}

function Accordion({ children }: { children: ReactNode }) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const value = useMemo(() => ({ activeIndex, setActiveIndex }), [activeIndex]);

  return (
    <AccordionContext.Provider value={value}>
      <div>{children}</div>
    </AccordionContext.Provider>
  );
}

Accordion.Item = function Item({ index, children }: { index: number; children: ReactNode }) {
  return <section data-open={useAccordionContext().activeIndex === index}>{children}</section>;
};

Accordion.Header = function Header({ index, children }: { index: number; children: ReactNode }) {
  const { activeIndex, setActiveIndex } = useAccordionContext();
  const isOpen = activeIndex === index;
  return (
    <button
      aria-controls={`accordion-panel-${index}`}
      aria-expanded={isOpen}
      onClick={() => setActiveIndex(isOpen ? null : index)}
    >
      {children}
    </button>
  );
};

Accordion.Body = function Body({ index, children }: { index: number; children: ReactNode }) {
  const isOpen = useAccordionContext().activeIndex === index;
  return isOpen ? <div id={`accordion-panel-${index}`} role="region">{children}</div> : null;
};

// Usage
<Accordion>
  <Accordion.Item index={0}>
    <Accordion.Header index={0}>Shipping</Accordion.Header>
    <Accordion.Body index={0}>Ships in 2-3 days.</Accordion.Body>
  </Accordion.Item>
</Accordion>
```

Provider values that are objects, arrays, or functions must be memoized or split into separate contexts. Otherwise every consumer re-renders on every provider render even when the meaningful data is unchanged.

Custom compound widgets must meet the platform accessibility contract. Accordions need expanded state and labelled regions; dialogs need focus trap, escape dismissal, labelled title, and focus return; menus and tabs need roving keyboard navigation and correct ARIA roles. Prefer proven accessible primitives when you cannot fully implement the keyboard and focus behavior.

## Render Props

Invert control of rendering so callers decide how items are displayed.

```tsx
function List<T>({
  items,
  getKey,
  renderItem,
}: {
  items: T[];
  getKey: (item: T) => string | number;
  renderItem: (item: T) => ReactNode;
}) {
  return <ul>{items.map((item) => <li key={getKey(item)}>{renderItem(item)}</li>)}</ul>;
}

// Usage
<List items={users} getKey={(u) => u.id} renderItem={(u) => <UserCard user={u} />} />
```

## Higher-Order Components (HOC)

Use for cross-cutting concerns (auth guard, analytics, feature flags). Prefer hooks for new code — HOCs suit cases where you need to wrap a component tree or interop with class-based APIs.

```tsx
function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthGuard(props: P) {
    const { user, loading } = useAuth();
    if (loading) return <Spinner />;
    if (!user) return <Navigate to="/login" />;
    return <Component {...props} />;
  };
}

const ProtectedDashboard = withAuth(Dashboard);
```

## Controlled vs Uncontrolled

Controlled — state lives in the parent, component is a pure view of that state:

```tsx
function ControlledInput({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return <input value={value} onChange={(e) => onChange(e.target.value)} />;
}
```

Uncontrolled — component owns its state; parent reads it imperatively via ref:

```tsx
function UncontrolledInput({ onSubmit }: { onSubmit: (v: string) => void }) {
  const ref = useRef<HTMLInputElement>(null);
  return (
    <form onSubmit={(event) => { event.preventDefault(); onSubmit(ref.current?.value ?? ''); }}>
      <input ref={ref} />
    </form>
  );
}
```

Prefer controlled for forms that need validation, disabled states, or reset behaviour. Uncontrolled is appropriate for file inputs and cases where you only need the value at submit time.

## Boolean Props and Conditional Rendering

Boolean props should read clearly at the call site and use shorthand for `true`:

```tsx
<Modal isOpen />
```

Avoid multiple boolean flags that can create impossible states. Prefer a single `variant` prop or a discriminated union. Prefer ternaries or explicit `null` over `&&` when the left side might be `0`, because React renders `0`.

## Polymorphic `as` Prop

Lets callers change the rendered element without breaking the component's prop contract.

```tsx
type BoxProps<T extends React.ElementType = 'div'> = {
  as?: T;
} & React.ComponentPropsWithoutRef<T>;

function Box<T extends React.ElementType = 'div'>({ as, ...props }: BoxProps<T>) {
  const Component = as ?? 'div';
  return <Component {...props} />;
}

// <Box as="section" className="wrapper" />
// <Box as="button" onClick={handler} />
```
