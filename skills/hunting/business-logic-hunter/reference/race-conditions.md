# RACE CONDITIONS — execution notes

Race conditions are a top-paying business-logic class: two requests racing for the same resource state, and the server fails to serialize them.

## Signal
- Money/credit/stock/redeem endpoints with a decrement-then-check flow
- `balance` or `stock` read, then subtract, then write — without a transaction or lock
- OTP/session endpoints where "consume once" is enforced only after response

## Test
1. Capture the vulnerable request (e.g., redeem coupon, withdraw, add credit).
2. Fire N parallel copies in the same instant:
   ```bash
   # turbo intruder style — 20 parallel identical requests
   seq 1 20 | xargs -P20 -I{} curl -s -o /dev/null -w "%{http_code}\n" \
     -X POST https://target/api/redeem \
     -H "Cookie: <session>" -d '{"code":"TEST2026"}'
   ```
3. Check the response count vs expected (server should reject 19 of 20).

## Confirm (not false positive)
- Count **successful** responses, not total. 20×200 but 1 credit applied = timing window closed, not a bug.
- Repeat 3×. Consistent over-application = race condition.
- Verify the state afterwards (balance grew by >1) from a second request.

## Kill
- Server returns the same balance after retry
- Only the first request mutates state; others hit a DB unique constraint
- Requests are serialized by a lock or transaction (response order = request order)

## Chaining
Race on coupon/reward redemption → free premium / free stock → privilege or financial impact. Pair with `chain-construction.md`.