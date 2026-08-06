# BFF (Backend for Frontend) — EXECUTION

| Attack | Signal | Test | Confirm |
|--------|--------|------|---------|
| **Operation name mismatch** | x-operation-name header | Send query with `"operationName":"adminOp"` | BFF doesn't validate |
| **Unauthenticated mutations** | BFF proxy | `curl -X POST /bff/graphql -d '{"query":"mutation{deleteUser(id:1)}"}'` | Mutation without auth |
| **Internal URL leak** | Error on malformed | `curl -X POST /bff -d 'null'` | Error reveals internal K8s service name |
| **Legacy backend gap** | Old API version proxied | `curl /bff/v1/createUser -d '{"role":"admin"}'` | Old version missing auth |

**Key insight:** BFFs often delegate auth to a legacy backend and inherit its gaps
