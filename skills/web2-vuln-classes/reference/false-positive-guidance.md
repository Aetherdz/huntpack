## FALSE POSITIVE GUIDANCE PER CLASS

| Class | Common False Positive | Why It's FP | How to Verify |
|-------|---------------------|-------------|---------------|
| **IDOR** | 200 OK with empty body | Endpoint returns 200 for all IDs, just empty for unauthorized | Compare response body size between your ID and another's — must contain actual data |
| **IDOR** | UUID in URL, changing UUID returns 404 | UUID is random, 404 means doesn't exist, not unauthorized | Test with KNOWN valid UUIDs from other users (found in JS, emails, support tickets) |
| **SSRF** | DNS callback received | Server may have pre-fetched your URL during rendering | Disable URL in baseline request — if callback still comes, it's pre-fetch, not SSRF |
| **SSRF** | 200 OK + response contains public data | URL fetcher may work but only allow-listed domains | Test internal IPs (127.0.0.1, 169.254.169.254) — if blocked, it's not SSRF |
| **XSS** | Alert fires on YOUR browser only | Self-XSS — only you can trigger it on your own session | Test from incognito/another browser — if it needs your session cookies, it's self-XSS |
| **XSS** | CSP blocks execution but input is reflected | CSP is working as intended, not a bypass | Check CSP policy — `script-src 'self'` blocks inline scripts. Need CSP bypass first |
| **SQLi** | `' OR 1=1--` returns different page | Could be WAF block, not SQL injection | Test `' OR 1=2--` — if SAME response as `OR 1=1`, it's not SQLi (WAF blocks both) |
| **SQLi** | Sleep(5) causes 5s delay | Database connection latency, not time-based SQLi | Test baseline response time first. Sleep(0) vs Sleep(5) — if both slow, it's network |
| **Race Condition** | Parallel requests both succeed | Endpoint may be idempotent (same result both times) | Check if resource state ACTUALLY changed (balance deducted twice, discount applied 2x) |
| **Race Condition** | Turbo Intruder shows 2x success | Server may process sequentially despite parallel sends | Check database state after — if only 1 change recorded, it's not a race condition |
| **JWT alg:none** | Server returns 200 with modified token | Server may accept token but fall back to session cookie auth | Remove ALL auth (cookie + header) and test again — if still 200, auth is not JWT-based |
| **File Upload** | PHP file uploads but doesn't execute | Server stores but doesn't execute PHP (runs as static file) | Access uploaded file URL — if PHP code is displayed as text, not executed, it's not RCE |
| **Business Logic** | Can skip steps but final action fails | Step skipping detected and blocked at commit | Check if the FINAL state change actually happened (DB change, email sent, balance moved) |
| **GraphQL** | Introspection returns schema | Many GraphQL servers leave introspection on in production | Check if AUTHENTICATED queries are also unprotected. Introspection alone is informational |
| **Rate Limit** | 100 requests all return 200 | Rate limit may be per-IP and you're using unique IPs | Test from single IP with consistent headers — if still 200, no rate limit |
| **Cache Poisoning** | Response contains your injected header | Cache may not be storing the poisoned response | Check `X-Cache: hit` header on SECOND request — if miss, cache not poisoned |
| **IDOR** | Cross-account request returns "victim" data | May be a CDN/edge cache serving YOUR earlier copy | Add a cache-buster query, use a fresh session/IP; confirm a field that is provably the victim's (their email/audit id) |
| **SSRF (gopher/dict)** | `gopher://` returns 200 / no error | Scheme silently dropped by fetcher, nothing executed | Prove the side effect with a second read (key set, cron fired, OOB hit) — 200 alone ≠ execution |
| **SSRF (blind)** | Interactsh DNS-only ping | App resolved the host but may not have fetched it | Wait for an **HTTP** callback from the target's egress, or a timing delta on open vs closed port — DNS-only stays Info |
| **OAuth** | `redirect_uri` bypass "works" | The code still lands on the legitimate origin | Confirm the `code`/token arrives on **your** host and exchanges — code kept on app.com is not exploitable |
| **JWT (jwk/jku/kid)** | Forged-key token returns 200 | Endpoint may not require JWT at all | Send the request with **no token** — if still 200, auth isn't JWT-based (not a forgery bug) |
| **CORS** | `Access-Control-Allow-Origin: *` on sensitive data | Browsers refuse `*` + credentials, so no cross-origin cred read | Only a bug if ACAO **reflects your origin** (or `null`) AND `Allow-Credentials: true`; `*` alone = informational |
| **NoSQLi** | `{"$ne":null}` returns 200 | 200 with empty/error body isn't injection | Confirm it authenticates you or returns **another user's** document |
| **MFA (response manip.)** | Flipping `{"success":true}` shows dashboard | Client-side render only; backend session still unauthenticated | Perform a **server-side** authenticated action afterward — if it 401s, the MFA is still enforced |
| **Rate limit** | Brute force returns all 200s | Cloudflare/WAF may be silently tar-pitting or serving cached 200s, not the app | Confirm the guessed value actually **worked** (login succeeded / OTP accepted); check for `cf-mitigated`, challenge, or identical timing on every response |

