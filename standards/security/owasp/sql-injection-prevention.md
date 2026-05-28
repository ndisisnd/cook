---
description: Prevent SQL injection via parameterized queries — never concatenate user input into SQL, use least-privilege accounts
alwaysApply: false
---

# SQL Injection Prevention

## NEVER
- Concatenate user input directly into SQL strings
- Use escaping as the primary injection defense — it is database-specific and error-prone
- Grant application database accounts DBA/admin privileges
- Treat validated input as safe for string concatenation
- Use client-side-only parameterization libraries that still build unsafe queries server-side
- Construct dynamic SQL in stored procedures without bind variables

## ALWAYS
- Use parameterized queries (prepared statements) as the primary defense
- Pass parameters separately after defining all SQL code; ensure parameterization occurs server-side
- Use least-privilege database accounts (read-only where possible)
- Apply input validation as a secondary, defense-in-depth layer only
- Use bind variables for any dynamic SQL within stored procedures
- Validate input for business logic requirements separately from SQL injection prevention

## Defense Options

| Option | When to use |
|--------|-------------|
| Prepared statements (parameterized) | Default — all dynamic queries |
| Stored procedures | Only if inputs are parameterized, no dynamic SQL inside |
| Allow-list input validation | Table/column names, sort indicators that cannot bind variables |
| Escaping | Avoid — use parameterized queries instead |

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

## Code Examples

Parameterized query (Java):
```java
String query = "SELECT balance FROM users WHERE name = ?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setString(1, custname);
```

Allow-list for non-bindable SQL elements (table name):
```java
switch(PARAM) {
  case "Value1": tableName = "fooTable"; break;
  default: throw new InputValidationException("unexpected value");
}
```

Stored procedure with bind variable (Oracle):
```sql
EXECUTE IMMEDIATE 'SELECT balance FROM accounts WHERE user_ID = :1'
  INTO result USING UserID;
```

Stored procedure with typed params (SQL Server):
```sql
EXEC sp_executesql @sql, '@UID VARCHAR(20)', @UID=@UserID
```

## Least Privilege
- Separate database users per application
- Grant only necessary read/write — never DDL rights
- Use database views to limit data exposure further

## Checklist
- [ ] All queries use parameterized statements, not string concatenation
- [ ] Prepared statements created server-side
- [ ] Stored procedures contain no dynamic SQL generation; bind variables used throughout
- [ ] ORM/framework queries pass data as parameters, not interpolated strings
- [ ] Table/column name inputs validated via allow-list switch/map
- [ ] Application DB account has no DBA/admin rights
- [ ] Input validation applied as secondary layer, not sole defense
- [ ] Escaping not relied upon as primary protection
