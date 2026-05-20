# Architecture

## Component & State Structure

- One component per file. No cross-concern mixing in a single component.
- Keep state as local as possible. Lift only when two or more components need the same state.
- Extract business logic from components into hooks or services. Components describe UI, not decisions.
- No business logic leaked from backend services into frontend components — the UI renders results, it does not re-derive them.

## Detecting Structural Duplication

Search for split sources of truth before refactoring:

```bash
# Find versioned or legacy service duplicates
find . -name "*.ts" | grep -E "(Service|Repository)(New|V2|Legacy|Old)"
# Check for parallel directory trees
ls src/  # compare against any /v1, /v2, or /Refactor directories
```

Signs of duplication: `UserService.ts` and `UserServiceNew.ts` both exist; a `/v1` and `/v2` folder with overlapping entities; a "Refactor" folder with active usage.

## Detecting Logic Leakage

Business logic in the wrong layer is the most common structural finding.

**Web (React/Next.js)**
```bash
# If hook count in components/ is >20x the hooks/ folder, architecture is monolithic
grep -rE "useEffect|useState|useMemo" components --include="*.tsx" | wc -l
```

**Mobile (Flutter)**
```bash
# I/O or state mutation in build() is high debt
grep -rE "http\.|dio\.|socket\." lib/widgets --include="*.dart" | wc -l
```

**Backend (NestJS)**
```bash
# Controllers must only parse requests and format responses — not touch the DB
grep -rE "Repository\.|Query\.|db\." src/controllers --include="*.ts" | wc -l
```

## Identifying Monoliths

| Layer | Medium | Critical |
| --- | --- | --- |
| UI component | > 500 lines | > 1,000 lines |
| Backend service | > 1,000 lines | > 1,500 lines ("God Class") |
| Resource / constants file | > 1,000 lines | Requires granulation |

## Remediation Patterns

| Finding | Immediate action | Long-term fix |
| --- | --- | --- |
| Monolith file | Extract helpers to private methods or utilities | Break into smaller, atomic modules |
| Logic leakage (web) | Extract complex hooks into `useFeatureLogic` | Move all business decisions to hooks or services |
| Logic leakage (mobile) | Move logic to BLoC, Provider, or a Service class | Enforce layer boundaries in code review |
| God service (backend) | Identify the distinct sub-domains it handles | Split into `UserAuthService`, `UserProfileService`, etc. |
| DB leakage into domain | Wrap ORM calls in a repository | Keep domain entities agnostic of persistence drivers |
| Structural duplication | Mark legacy version `@deprecated` | Migrate all usage to the standard version, then delete |

## Layer Violation Scoring (for audits)

- Business logic in UI or controller layer: severe
- Structural fragmentation (parallel entity definitions): moderate
- Monolith unit > 1,000 lines: moderate
