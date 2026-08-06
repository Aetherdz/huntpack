# VERIFICATION — EXECUTION CHECKLIST

## PRE-REPORT: CONFIRM WITH CURL
```bash
# 1. Zero state test (fresh session, never seen before)
curl -s -X GET /api/resource -H "Cookie: FRESH_SESSION" > fresh_test.json

# 2. Cross-account test
curl -s -X GET /api/resource -H "Cookie: SESSION_B" > cross_account.json

# 3. Check production (if not already)
curl -s -X GET "https://production.com/api/resource" -H "Cookie: A" > prod_test.json

# 4. Verify impact: what did attacker actually get?
# IDOR: other user's real PII?
curl -s -X GET /api/user/OTHER_ID -H "Cookie: A" | jq '{email, phone, address}'
# Race: did balance actually change?
curl -s -X GET /api/wallet -H "Cookie: A" | jq '.balance'
# OTP bypass: account created without verification? Can login?
curl -s -X POST /api/auth/login -d '{"email":"new@x.com","pass":"X"}' | jq '.session'
```

## VERIFICATION GATES
- [ ] Reproducible from zero state (fresh session, no prior access)
- [ ] Works on production (not staging)
- [ ] Works with different accounts (A accessing B's data)
- [ ] Not in always-rejected list (security-arsenal/reference/always-rejected.md)
- [ ] Real impact proven: attacker walks away with something tangible
- [ ] Worst-case scenario documented: chained for maximum effect

## KILL SIGNALS
| Observation | Action |
|-------------|--------|
| 401/403 on all attempts | Auth present → move on |
| Same data both accounts | No IDOR → move on |
| UI-only "premium" with real charge on invoice | Intentional → move on |
| DB unique constraint error | Atomic → move on |
| "Cannot skip step" | State machine valid → move on |
| "Admin can do X" (non-admin can't) | Intentional → move on |
