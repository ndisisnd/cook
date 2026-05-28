---
description: Prevent SQL injection by parameterizing all queries — never concatenate user input into SQL strings
alwaysApply: false
---

# Query Parameterization

## NEVER
- Concatenate user input directly into SQL query strings
- Perform SQL injection prevention via input validation alone — parameterize first
- Use client-side-only parameterization libraries that still build unsafe queries server-side
- Construct dynamic SQL in stored procedures without bind variables

## ALWAYS
- Use parameterized queries / prepared statements for all database interactions
- Use bind variables for any dynamic SQL within stored procedures
- Validate input for business logic requirements separately from SQL injection prevention
- Ensure parameterization occurs server-side

## Language Patterns

| Language | Safe API |
| -------- | -------- |
| Java | `PreparedStatement` with `?` placeholders; Hibernate named params |
| .NET | `SqlCommand` with `@param`; `OleDbCommand` with `?` |
| Ruby | ActiveRecord `where("col = ?", val)` or `prepare`/`execute` |
| PHP | PDO `prepare` + `bindParam` |
| Perl | DBI `prepare` + `execute` |
| Rust | `sqlx::query!` macro or `.bind()` |
| Cold Fusion | `<cfqueryparam>` |

## Stored Procedure Examples

```sql
-- Oracle dynamic SQL: bind variable prevents injection
EXECUTE IMMEDIATE 'SELECT balance FROM accounts WHERE user_ID = :1'
  INTO result USING UserID;

-- SQL Server dynamic SQL: sp_executesql with typed params
EXEC sp_executesql @sql, '@UID VARCHAR(20)', @UID=@UserID
```

## Checklist
- [ ] Every query uses `?` / named placeholders, no string concatenation
- [ ] Prepared statements created server-side
- [ ] Stored procedure dynamic SQL uses bind variables
- [ ] ORM/framework queries pass data as parameters, not interpolated strings
- [ ] Input validation handles business rules, not SQL escaping
