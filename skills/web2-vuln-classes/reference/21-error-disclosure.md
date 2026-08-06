## 21. ERROR DISCLOSURE / DEBUG ENDPOINTS
> Stack traces and framework debug surfaces — chain into secret extraction → ATO. Single bug-bounty/SKILL.md already lists `/actuator/env`, `/.env`, `/server-status`, Laravel `/horizon` / `/telescope`, WordPress `/wp-json/wp/v2/users`, etc. This section covers the **detection signatures** and **triggering techniques** that turn those paths into payable chains.

### Framework Stack Trace Regex
Grep response bodies (4xx and 5xx) for these — each implies a known exploitation playbook.

```
Django           Traceback \(most recent call last\)              → check DEBUG=True page → DB creds, SECRET_KEY → forge sessions
Spring/Java      at \S+\(.*\.java:\d+\)|NestedServletException   → look for /actuator/* → /env → secrets / JWT key
Symfony (PHP)    Whoops\\Run|\\\\Symfony\\\\.*\\\\Exception        → check /_profiler/ → request tokens → replay/auth bypass
Rails            /app/controllers/|/gems/.*\.rb:\d+:in            → check dev mode → web-console RCE
ASP.NET (YSOD)   \[\w+Exception:|Server Error in '.+' Application  → check trace.axd, elmah.axd → request replay
PHP              (Warning|Fatal error|Notice):.*on line \d+        → path disclosure → LFI / config leak
Node.js          Error: .*\n\s+at \S+ \(.*:\d+:\d+\)               → look for /__debug__/, source maps
Go               goroutine \d+ \[running\]:|runtime/panic\.go      → expvar at /debug/vars, /debug/pprof
```

### Framework Debug Surfaces — Not Yet Listed Elsewhere
> `/.env` / `/.env.local` / `/.env.production` / `/actuator/*` / `/server-status` / `/server-info` / `elmah.axd` / `trace.axd` / `/.git/config` / Laravel `/horizon` / `/telescope` / WordPress `/wp-json/wp/v2/users` — **already covered** in bug-bounty/SKILL.md and wordlists/sensitive-files.txt. Don't re-probe.

```
Symfony          /_profiler/             → list every request + tokens → replay user requests
Symfony          /_profiler/phpinfo      → environment dump
Django           /__debug__/             → django-debug-toolbar panels (SQL, settings)
Django           /admin/                 → defaults to /admin/ if not renamed
Next.js          /_next/data/            → SSR payload leak (server-rendered JSON exposed)
Next.js          /_next/static/chunks/   → JS chunks with hardcoded secrets
Go expvar        /debug/vars             → leaks memstats, cmdline, env vars
Go pprof         /debug/pprof/           → goroutine stacks (memory layout, secrets in flight)
Spring Boot      /actuator/heapdump      → full JVM heap → grep secrets out
Spring Boot      /actuator/mappings      → endpoint list including hidden internal routes
Spring Boot      /actuator/loggers       → modify log level to leak more data
GraphQL          ?debug=1 / ?debug=true  → some servers expand errors with debug flag
Java             /META-INF/MANIFEST.MF   → dependency versions → CVE chain
```

### Triggering Stack Traces (when no debug endpoint exposed)
Inject malformed input on existing parameters — many apps still leak traces on unexpected types.

```
Numeric ID → string         /api/user/abc                       → ORM error with column names
Numeric ID → negative       /api/user/-1                        → unhandled signed overflow
Numeric ID → boundary       /api/user/9999999999999999999       → int overflow / type cast error
JSON null where object      {"user": null}                      → NullPointerException
JSON array where object     {"user": []}                        → ClassCastException
Truncated/malformed JSON    {"user":                            → parser stack trace
%00 in path                 /api/user/1%00.json                 → path normalisation difference
Oversized page param        ?page=99999999                      → OOM or query timeout trace
Wrong content-type          POST JSON as Content-Type: text/xml → XML parser dump
Empty multipart boundary    Content-Type: multipart/form-data;  → Busboy / Undici stack trace
Unicode normalisation       /api/user/admin​               → diff path between sanitiser and DB
```

### Chains That Pay
```
Stack trace -> framework version -> public CVE -> RCE             High–Critical
/actuator/env -> spring.datasource.password -> DB access           Critical
/actuator/env -> JWT signing key -> forge admin token              Critical (ATO)
/actuator/heapdump -> grep secrets -> AWS access keys              Critical
/_profiler/ -> capture victim session token -> account takeover    Critical
/_next/data/ -> SSR-rendered API responses -> IDOR without auth    High
DEBUG=True (Django) -> SECRET_KEY leak -> session forgery          Critical
PHP path disclosure -> LFI parameter discovered earlier -> RCE     Critical
Stack trace alone (no chain)                                       Low → likely N/A
```

### Triage
```
Secrets visible (DB creds, JWT key, API keys)        = Critical (chain to ATO/data)
Framework version + public CVE matching              = High–Critical (verify with PoC)
PII / internal IP / hostname in stack trace          = Medium (information disclosure)
Path disclosure only (no secrets)                    = Low/Info (chain to LFI to upgrade)
"Yellow page" / "Internal Server Error" generic      = N/A — no signal
```

