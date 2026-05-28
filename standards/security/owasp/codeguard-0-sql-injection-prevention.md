---
description: Prevent SQL injection by separating SQL code from data via parameterized queries
alwaysApply: false
---

# SQL Injection Prevention

## NEVER
- Concatenate user input directly into SQL strings
- Use escaping as the primary injection defense — it is database-specific and error-prone
- Grant application database accounts DBA/admin privileges
- Treat validated input as safe for string concatenation

## ALWAYS
- Use parameterized queries (prepared statements) as the primary defense
- Pass parameters separately after defining all SQL code
- Use least-privilege database accounts (read-only where possible)
- Apply input validation as a secondary, defense-in-depth layer only

## Defense Options

| Option | When to use |
|--------|-------------|
| Prepared statements (parameterized) | Default — all dynamic queries |
| Stored procedures | Only if inputs are parameterized, no dynamic SQL inside |
| Allow-list input validation | Table/column names, sort indicators that cannot bind variables |
| Escaping | Avoid — use parameterized queries instead |

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

## Least Privilege
- Separate database users per application
- Grant only necessary read/write — never DDL rights
- Use database views to limit data exposure further

## Checklist
- [ ] All queries use parameterized statements, not string concatenation
- [ ] Stored procedures contain no dynamic SQL generation
- [ ] Table/column name inputs validated via allow-list switch/map
- [ ] Application DB account has no DBA/admin rights
- [ ] Input validation applied as secondary layer, not sole defense
- [ ] Escaping not relied upon as primary protection
