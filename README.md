```
  invoking agent
       │
       │  file paths / code change
       ▼
  ┌───────────────────────────────────────┐
  │                 cook                  │
  │  derive signals from real sources     │
  │  (files, git, manifest, extensions)   │
  └──────────────────┬────────────────────┘
                     │
                     ▼
            check the route cache
                     │
         ┌───────────┴───────────┐
         │                       │
      cached                 not cached
         │                       │
         │               figure out what the
         │               task is trying to do
         │               (review? build? fix?)
         │                       │
         │               map signals to domains
         │               and concerns
         │                       │
         └───────────┬───────────┘
                     │
            ┌────────▼─────────┐
            │  reviewing code?  │
            │  → load review    │
            │    standards only │
            │  → save route,    │
            │    done           │
            └────────┬──────────┘
                     │ (building / fixing)
                     ▼
         always load universal rules   ← never skipped
                     │
                     ▼
         load matching cross-cutting
         concerns (security, API, auth…)
                     │
                     ▼
         load matching domain standards
         (React, Next.js, Postgres…)
                     │
                     ▼
            save route to cache
                     │
                     ▼
         compile into one payload
         (deduplicated, layered, clean)
                     │
                     ▼
         update cache with any
         files that failed to load
                     │
                     ▼
     standards payload → invoking agent
```
