# FLOW MAPPING — EXECUTION

## CAPTURE FLOW
```bash
# Use Burp proxy or curl chain to map every step
# 1. Start capture
burp_session="target_flow.log"
# 2. Perform each business action:
#    signup → login → browse → add to cart → checkout → pay → refund
# 3. Export all requests/response pairs

# Or use curl to manually trace:
curl -v -X POST /api/auth/signup -d '{"email":"test@x.com","pass":"X"}' 2>&1 | tee 01-signup.log
curl -v -X POST /api/auth/login -d '{"email":"test@x.com","pass":"X"}' 2>&1 | tee 02-login.log
curl -v -X GET  /api/products -b "session=A" 2>&1 | tee 03-products.log
curl -v -X POST /api/cart/add -d '{"product":1,"qty":1}' -b "session=A" 2>&1 | tee 04-cart.log
curl -v -X POST /api/checkout -d '{"payment":"card"}' -b "session=A" 2>&1 | tee 05-checkout.log
```

## FLOW ANALYSIS
For each step, ask:
```
[ ] State: Does server validate state before this step?
[ ] Auth: Does this step re-verify identity or trust previous step?
[ ] ID: Is the resource ID predictable? (sequential, UUID, email)
[ ] Race: Can this step execute in parallel with itself?
[ ] Skip: Can you POST directly to this step without previous ones?
[ ] Param: Which parameters came from client vs server?
[ ] Side: What side effects does this step trigger? (email, charge, notification)
```

## COMPARE: AUTH vs UNAUTH
```bash
# Auth check: try each step without session
for step in $(cat flow_steps.txt); do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$step" -b "session=INVALID")
  echo "$step without auth → $code"
done
```

## STATE MACHINE MAP
```bash
# Map all transitions
curl -s /api/order/123 -b "session=A" | jq '.status'
# Try setting different states
for status in draft pending confirmed shipped delivered cancelled refunded; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH /api/order/123 \
    -d "{\"status\":\"$status\"}" -b "session=A")
  echo "→ $status: $code"
done
```
