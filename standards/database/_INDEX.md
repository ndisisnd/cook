<!-- Hand-maintained routing index. Keep in sync with SKILL.md frontmatter. -->
# database Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **database** | `**/*.entity.ts`, `prisma/schema.prisma`, `prisma/migrations/*/migration.sql`, `**/migrations/*.sql`, `drizzle.config.ts`, `drizzle/**/*.sql`, `**/redis.config.ts` | postgres, postgresql, prisma, TypeOrmModule, PrismaService, PostgresModule, redis, ttl, eviction |
| database → PostgreSQL refs | `**/*.entity.ts`, `prisma/schema.prisma`, `prisma/migrations/*/migration.sql`, `**/migrations/*.sql`, `drizzle/**/*.sql` | index, RLS, transaction, query plan, explain, sql |
| database → Redis refs | `**/redis.config.ts` | redis, ttl, eviction, scan |

> Load `<SKILLS>/database/SKILL.md` for PostgreSQL schema work, migrations, query tuning, and Redis/Valkey configuration or caching changes.
> Load `<SKILLS>/database/refs/postgresql-implementation.md` for the expand-contract migration recipe (rename/reshape on a live table).
> Load `<SKILLS>/database/refs/postgresql-checklist.md` when reviewing a migration (locks, `CONCURRENTLY`, `NOT VALID`) or a complex query.
> Load `<SKILLS>/database/refs/postgresql-best-practices.md`, `postgresql-anti-patterns.md`, or `sql-gotchas.md` when reviewing PostgreSQL schema, SQL, indexing, pooling, RLS, or PG17/18 features.
> Load `<SKILLS>/database/refs/redis-best-practices.md` or `redis-checklist.md` when reviewing cache behavior, TTL strategy, command safety, client setup, or Redis/Valkey operations.
