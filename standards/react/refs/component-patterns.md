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
const SelectContext = createContext<{ val: string; setVal: (v: string) => void } | null>(null);

function Select({ children }: { children: ReactNode }) {
  const [val, setVal] = useState('');
  return (
    <SelectContext.Provider value={{ val, setVal }}>
      <select value={val} onChange={(e) => setVal(e.target.value)}>
        {children}
      </select>
    </SelectContext.Provider>
  );
}

Select.Option = function Option({ value, children }: { value: string; children: ReactNode }) {
  return <option value={value}>{children}</option>;
};

// Usage
<Select>
  <Select.Option value="a">Alpha</Select.Option>
  <Select.Option value="b">Beta</Select.Option>
</Select>
```

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
    <form onSubmit={() => onSubmit(ref.current?.value ?? '')}>
      <input ref={ref} />
    </form>
  );
}
```

Prefer controlled for forms that need validation, disabled states, or reset behaviour. Uncontrolled is appropriate for file inputs and cases where you only need the value at submit time.

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
