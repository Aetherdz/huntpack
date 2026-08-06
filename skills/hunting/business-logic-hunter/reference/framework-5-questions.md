# 5-QUESTION FRAMEWORK — WITH TECHNIQUE MAPPING

Ask these BEFORE starting any assessment:

| # | Question | Technique | Command/Check |
|---|----------|-----------|---------------|
| Q1 | **What are Assets?** | Map revenue-critical features | `grep -oP '"price"|"plan"|"wallet"|"balance"|"premium"' target.js` |
| Q2 | **What are Roles?** | AuthZ matrix | `for r in guest user admin; do curl /api/admin -b "role=$r"; done` |
| Q3 | **What Constraints?** | Rate limits, ownership, state | `curl -X POST /api/checkout -d '{"qty":999}'` — is there a limit? |
| Q4 | **What Assumptions?** | Developer trust boundaries | "UUID is safe", "frontend hides it", "users won't race" |
| Q5 | **How to Break?** | Violate each assumption | Predict UUID, curl directly, parallel requests |

## DEVELOPER ASSUMPTIONS → ATTACK MAPPING
| Assumption | Violation | Attack Type | Example Command |
|------------|-----------|-------------|----------------|
| "UUIDs are unguessable" | Predictable or leaked | IDOR | `curl /api/resource/$UUID` from another session |
| "Frontend hides admin routes" | Direct HTTP to hidden routes | PrivEsc | `curl /api/admin/users` with user session |
| "Users follow steps 1→2→3" | Skip/reverse steps | Workflow Bypass | `curl POST /order/confirm` before /order/pay |
| "Users submit once" | Parallel requests | Race Condition | `for i in {1..N}; do curl ... &; done` |
| "Only our JS calls our API" | Replay/modify requests | Mass Assignment | `curl PATCH /profile -d '{"role":"admin"}'` |
| "Payment succeeded = user paid" | Cancel after grant | Premium Abuse | Upgrade → cancel before charge → check features |
| "Email verified = real user" | Tempmail + OTP bypass | Signup Abuse | `mail.tm` + skip OTP step |

## QUICK START: For any target
```bash
# 1. Map assets: what's paid/protected?
curl -s /api/user/me -H "Cookie: A" | jq '.'
# 2. Map roles: what can different users do?
# 3. Find assumptions: what did the developer trust?
# 4. Break each assumption with the techniques above
```
