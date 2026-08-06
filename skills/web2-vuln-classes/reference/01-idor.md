## 1. IDOR — INSECURE DIRECT OBJECT REFERENCE  🔐
> #1 most paid web2 class — 30% of all submissions that get paid.
> **Needs two sessions** (A=attacker, B=victim) — load both via `--auth-file`
> and diff audit-log `session_id` hashes to confirm cross-tenant access.

### Root Cause
```python
# VULNERABLE — no ownership check
@app.route('/api/orders/<order_id>')
def get_order(order_id):
    order = db.query("SELECT * FROM orders WHERE id = ?", order_id)
    return jsonify(order)  # Never checks if order belongs to current user!

# SECURE
@app.route('/api/orders/<order_id>')
def get_order(order_id):
    order = db.query("SELECT * FROM orders WHERE id = ? AND user_id = ?",
                     order_id, current_user.id)
```

### Variants
- **V1:** Numeric ID swap — `/api/user/123/profile` → change to 124
- **V2:** UUID swap — enumerate UUID via email invite or other endpoint
- **V3:** Indirect IDOR — `POST /api/export?report_id=456` exports another user's report
- **V4:** Parameter add — `?user_id=other` makes backend use it
- **V5:** HTTP method swap — PUT protected, DELETE not
- **V6:** Old API version — `/v1/users/123` lacks auth that `/v2/` has
- **V7:** GraphQL node — `{ node(id: "base64(User:456)") { email } }`
- **V8:** WebSocket — WS sends `{"action":"get_history","userId":"client-generated-UUID"}`

### Testing Checklist
```
[ ] Two accounts (A=attacker, B=victim)
[ ] Log in as A, perform all actions, note all IDs
[ ] Replay A's requests with A's token but B's IDs
[ ] Test EVERY HTTP method (GET, PUT, DELETE, PATCH)
[ ] Check API v1 vs v2
[ ] Check GraphQL node() queries
[ ] Check WebSocket messages for client-supplied IDs
```

### Modern Variants (2024–2026 paid)
- **V9 — Encrypted/encoded ID reuse:** ID looks opaque (`?id=8f3a...`, base64, `hashid`). Don't crack it — **copy B's opaque blob** from any endpoint that leaks it (share link, invite email, export, notification) and paste into A's request. Encryption without ownership check is still IDOR.
- **V10 — UUIDv1 prediction:** `uuidv1` encodes timestamp + MAC → **not random**. Harvest 2–3 UUIDs, feed to `uuidtools`/`sandwich` to predict adjacent ones (invite tokens, reset IDs, object IDs). `uuidv4` is safe; check version nibble (13th hex char = `1`).
- **V11 — BOPLA (broken object *property* level auth, OWASP API #3):** object is yours but you read/write **fields you shouldn't**. Probe `?fields=`, `?expand=`, GraphQL field selection, sparse-fieldset params → pull `role`, `is_admin`, `balance`, `ssn`, internal flags. Write side = mass assignment (see `reference/12-api-security.md`).
- **V12 — Blind / second-order IDOR:** the swapped ID returns nothing useful *in-band*, but the action fires on a **side channel** — victim's data lands in an emailed export, generated PDF, webhook, CSV, or admin panel. Confirm out-of-band; a boring 200 can still be Critical.
- **V13 — Array / batch widening:** single-item authz doesn't cover bulk. Turn `id=1` into `id[]=1&id[]=2`, `id=1,2,3`, JSON `{"ids":[victim,you]}`, or GraphQL aliased batch — server authorizes the request, not each item.

### Automated Detection (role-diff)
- **Burp Autorize / Auth Analyzer:** load A's session as "low-priv", browse as B, auto-replays every request with A's cookies → flags `Bypassed!` where A gets B's data. Highest signal-per-minute for IDOR at scale.
- **Scripted A/B replay:** capture B's traffic → resend with A's token, diff status **and body length**. Same length + 200 = access; 200 + different length = compare content before claiming.
- **Confirm cross-tenant** by diffing an owned field (email/audit `session_id` hash) so you prove it's *B's* record, not A's cached copy.

### IDOR Chain Escalation
- IDOR + Read PII = Medium
- IDOR + Write (modify other's data) = High
- IDOR + Admin endpoint = Critical (privilege escalation)
- IDOR + Account takeover path = Critical
- IDOR + Chatbot reads other user's data = High

