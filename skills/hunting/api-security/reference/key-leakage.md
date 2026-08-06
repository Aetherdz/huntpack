# KEY LEAKAGE — EXECUTION

| Signal | Source | Test | Impact |
|--------|--------|------|--------|
| `api_key`, `API_KEY` | JS bundle | `grep -oP 'api[_-]?key["\s:=]+["'"'"']?([A-Za-z0-9]{20,})' target.js` | Access paid API |
| `client_secret` | APK strings.xml | `apktool d app.apk && grep -r "client_secret" .` | OAuth token theft |
| `password`, `secret` | Source maps | `curl /static/js/app.js.map` → beautify → grep | Backend access |
| `Bearer` token | LocalStorage/JS | `grep -r "Bearer" target.js` | Auth bypass |
| AWS `AKIA` | JS/commits | `grep -r "AKIA" target.js` | Cloud resources |
| Firebase URL | google-services.json | `curl project.firebaseio.com/.json` | Open DB access |

**Key verification:** `curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $KEY" /api/limited`
