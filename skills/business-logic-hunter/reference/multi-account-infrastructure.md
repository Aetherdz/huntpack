# MULTI-ACCOUNT INFRASTRUCTURE — EXECUTION

## ACCOUNT MATRIX
| Account | Purpose | Setup Command |
|---------|---------|---------------|
| User A | Primary attacker | `curl -X POST /api/signup -d '{"email":"a@x.com","pass":"X"}'` |
| User B | Victim/IDOR target | `curl -X POST /api/signup -d '{"email":"b@x.com","pass":"X"}'` |
| User C | Extra comparison | `curl -X POST /api/signup -d '{"email":"c@x.com","pass":"X"}'` |
| Admin | Privilege reference | `admin@x.com` (use test account or escalate) |

## SESSION MANAGEMENT
```bash
# Save sessions to files for reuse
export A="session=token_a_here"
export B="session=token_b_here"
export ADMIN="session=token_admin_here"

# Or save to files
echo "token_a" > .session_a
echo "token_b" > .session_b

# Test IDOR with session compare
curl -s "/api/orders" -H "Cookie: $A" > orders_a.json
curl -s "/api/orders" -H "Cookie: $B" > orders_b.json
diff <(jq '.[].id' orders_a.json | sort) <(jq '.[].id' orders_b.json | sort)
# If A's orders appear in B's response → IDOR

# Authorization matrix
for session in a b admin; do
  echo "=== Session $session ==="
  for endpoint in /api/users /api/admin /api/orders /api/billing; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" \
      -H "Cookie: $(cat .session_$session)")
    echo "  $endpoint → $code"
  done
done
```

## COMPARE ACROSS SESSIONS
```bash
# Quick authz diff
curl -s /api/user/me -H "Cookie: A" | jq '{id, email, role, plan, permissions}' > a_me.json
curl -s /api/user/me -H "Cookie: B" | jq '{id, email, role, plan, permissions}' > b_me.json
diff a_me.json b_me.json

# Check if A can access B's resources
curl -s "/api/user/$(jq -r '.id' b_me.json)" -H "Cookie: A"
```
