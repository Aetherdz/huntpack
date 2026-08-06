## CVSS 4.0

### Key Differences from 3.1
| Metric | CVSS 3.1 | CVSS 4.0 |
|--------|----------|----------|
| Attack Vector (AV) | N/A/L/P | N/A/L/P (expanded definitions) |
| Complexity (AC) | L/H | L/H (removed "Medium") |
| Privileges (PR) | N/L/H | N/L/H (expanded for cloud) |
| User Interaction (UI) | N/R | N/R (clarified) |
| Scope (S) | U/C | U/C (no change) |
| Confidentiality/Integrity/Availability | H/L/N | H/L/N (added "Safety" impact) |
| Exploit Maturity (E) | Not in Base | New: X/U/P/F/H |
| Environmental | Modified Base | Modified Base (expanded) |

### CVSS 4.0 Score Ranges

| Severity | 3.1 Range | 4.0 Range |
|----------|-----------|-----------|
| NONE | 0.0 | 0.0 |
| LOW | 0.1–3.9 | 0.1–3.9 |
| MEDIUM | 4.0–6.9 | 4.0–6.9 |
| HIGH | 7.0–8.9 | 7.0–8.9 |
| CRITICAL | 9.0–10.0 | 9.0–10.0 |

### CVSS 4.0 Common Vectors
```yaml
IDOR (user data, no auth needed):
  Vector: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N
  Score: 8.7 (HIGH)
  
SQLi with data exfil:
  Vector: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N
  Score: 10.0 (CRITICAL)

Stored XSS:
  Vector: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N
  Score: 5.1 (MEDIUM)
```

### Threat Metric — Exploit Maturity (E) mapped to YOUR evidence
CVSS 4.0 folds the old Temporal group into a single **Threat** metric, `E`. It moves score and it maps directly to how solid your PoC is — set it honestly, it *raises* credibility (and often the payout tier):

| E value | Meaning | Set it when your PoC is… |
|---|---|---|
| `E:A` (Attacked) | in-the-wild exploitation exists | a public exploit / active abuse is known |
| `E:P` (Proof-of-Concept) | a PoC exists but isn't weaponized | you have a working, repeatable PoC (the normal bug-bounty case) |
| `E:U` (Unreported) | no known exploit | purely theoretical — usually means *don't submit yet* |
| `E:X` (Not Defined) | omitted | you don't want E to affect the score |

**Reproducibility → E → how many times to prove it:**
```
Deterministic bug (IDOR, authz, SQLi, XSS): reproduce 3× clean-state → E:P (or E:A if public)
Timing/race/heisenbug:                       reproduce ≥1× with the ordered packet log + success rate (e.g. "7/50 races won") → E:P
Only worked once, can't re-trigger:          E:U → DO NOT SUBMIT (fails Reproducibility Gate)
```
(See `.quality-gates.md` → Reproducibility Gate. "Once" is only acceptable for genuine races, and only with the concurrency evidence attached.)

### Environmental / Modified metrics — score for THIS asset's context
Don't ship a generic base score when context changes impact. Override the base with Modified metrics when the target's reality differs:
- **`MAV`** — internal-only admin panel reachable only from VPN → `MAV:A`/`MAV:L` lowers a network score (be honest; triagers respect it).
- **`MVC/MVI/MVA`** — a bug in a subsystem holding crown-jewel data → raise; a bug touching only public/non-sensitive data → lower `MVC:L/N`.
- **`CR/IR/AR`** (security requirements) — payment/PII systems justify `CR:H`, nudging the score up with a documented reason.
- **Rule:** every non-default metric needs a one-line justification in the report, or it reads as inflation (the #1 "Overclaiming" rejection). A *defensible lower* score builds trust and speeds triage.

## Detection Heuristics Per Vuln Class

Use these patterns during testing to IDENTIFY vulnerabilities before you write the report. Each heuristic tells you WHAT to look for in the response.

### IDOR / BOLA
| Heuristic | What to Check | Confidence |
|-----------|---------------|------------|
| Sequential ID in URL/body | Change user_id/order_id by ±1, check if different user's data returns | High |
| UUID in URL | Replace with another user's UUID from registration/debug response | High |
| Array/collection endpoint | Access /api/users instead of /api/users/me — does it return all users? | High |
| HTTP method variation | Does DELETE /api/resource/123 work without ownership check? | Medium |
| Batch operations | Does POST /api/batch accept IDs from other users? | Medium |
| Response size comparison | Same endpoint, different IDs — if response sizes vary, data is user-specific | Low |

**Key pattern**: 200 OK ≠ authorized. Always test with another account's ID.

### SSRF
| Heuristic | What to Check | Confidence |
|-----------|---------------|------------|
| URL parameter | Replace with `http://169.254.169.254/` — check response or timing | High |
| Webhook/import feature | Point to internal service (`http://localhost:6379` for Redis) | High |
| File/image fetch | Replace URL with `file:///etc/passwd` — check for file contents | High |
| DNS interaction | Use collaborator.interactsh.com — check for DNS callback | High |
| Redirect following | Set up redirect from your server → internal IP — does it follow? | Medium |

**Key pattern**: Any feature that takes a URL is a potential SSRF. Test ALL of them.

### SQLi
| Heuristic | What to Check | Confidence |
|-----------|---------------|------------|
| Parameter reflection | `'` causes error? String reflected in response? | High |
| Time-based | `' OR SLEEP(5)--` causes 5s delay vs normal? | High |
| Boolean blind | `' AND 1=1--` vs `' AND 1=2--` — different responses? | High |
| Union select | `' UNION SELECT 1,2,3--` — numbers reflected in output? | High |
| Error-based | `' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT @@version)))--` | Medium |

**Key pattern**: The response CHANGES based on SQL injection. If it doesn't change, it's not exploitable SQLi.

### XSS (Reflected)
| Heuristic | What to Check | Confidence |
|-----------|---------------|------------|
| Input reflection | `<script>alert(1)</script>` appears in response HTML unencoded? | High |
| Context escaping | Value reflected inside `"...."` vs `'...'` vs `<...>` — each needs different payload | High |
| CSP headers | Check `Content-Security-Policy` — if `unsafe-inline` present, XSS is possible | Medium |
| WAF detection | `alert(1)` blocked but `alert(1)` with different casing works? WAF bypass needed | Low |

**Key pattern**: Input must be reflected UNENCODED/UNESCAPED in the response for reflected XSS.

### Business Logic
| Heuristic | What to Check | Confidence |
|-----------|---------------|------------|
| Step skipping | POST step 3 directly without steps 1-2 — does it work? | High |
| Negative values | Set quantity/price to -1, 0, or overflow — accepted? | High |
| Race window | Send 20 parallel requests to same discount endpoint — all succeed? | High |
| State manipulation | Do action, then undo, then redo — does state get corrupted? | High |
| Role boundary | User does admin action — accepted? | High |

**Key pattern**: The server trusts the CLIENT to follow the intended flow. Break that trust.

### JWT Issues
| Heuristic | What to Check | Confidence |
|-----------|---------------|------------|
| alg:none | Change alg to "none", remove signature — token accepted? | High |
| Weak secret | Crack with hashcat — `hashcat -m 16500 jwt.txt rockyou.txt` | High |
| RS256→HS256 | Use public key as HMAC secret — token accepted? | High |
| Missing verification | Modify payload claims, keep same signature — still valid? | High |
| Expired token | Use expired token — still accepted? | Medium |

**Key pattern**: If you can modify the JWT payload and the server still accepts it, there's NO signature verification.

### Race Conditions
| Heuristic | What to Check | Confidence |
|-----------|---------------|------------|
| Discount/gift code | Apply same code 20x in parallel — applied multiple times? | High |
| Withdrawal/transfer | Send parallel withdraw requests — balance goes negative? | High |
| Account registration | Register same email 10x in parallel — 10 accounts created? | Medium |
| Like/vote/follow | Send parallel like requests — count exceeds 1 per user? | Medium |

**Key pattern**: Use Turbo Intruder's single-packet attack. Send all requests SIMULTANEOUSLY (not sequentially).

### GraphQL
| Heuristic | What to Check | Confidence |
|-----------|---------------|------------|
| Introspection | `{__schema{types{name}}}` — schema returned? | High |
| Field suggestions | Typo in field name — error message leaks valid field names? | High |
| Alias bombing | 1000 aliases in one query — server processes all? | Medium |
| Batching | 100 identical queries in one POST — 100 results returned? | Medium |
| Mutation auth | Delete mutation without auth — still works? | High |

**Key pattern**: GraphQL is a single endpoint — auth must be checked per FIELD, not per endpoint.

---

## Common Report Rejection Reasons

| Rejection | Why | Fix |
|-----------|-----|-----|
| "Out of Scope" | Target/asset not in program scope | Always verify scope before testing |
| "Duplicate" | Same bug reported earlier | Check hacktivity before submitting |
| "Insufficient Impact" | Bug is real but impact is theoretical | Always demonstrate actual data access/loss |
| "N/A" | Not a vulnerability (expected behavior) | Run through 7-Question Gate before writing |
| "Missing PoC" | Steps not reproducible | Include curl + full request/response |
| "Informational" | Missing header, self-XSS, etc. | Only submit if chainable to higher impact |
| "Overclaiming" | CVSS inflated without justification | Use actual impact, not hypothetical worst case |

## Report Title Formulas

```text
[Vuln Type] in [Endpoint] — [Impact Summary]

Examples:
• IDOR in GET /api/v1/orders — Unauthorized Access to All User Orders
• SSRF in /api/import — Internal Network Scanning via URL Parameter
• Race Condition in POST /api/withdraw — Double Spending by Concurrent Requests
• SQLi in /api/search — Authentication Bypass + Full Database Read
• Stored XSS in /profile/bio — Cross-Site Scripting on User Profile Pages
• Auth Bypass in /admin/* — Privilege Escalation via Token Manipulation
```

## Evidence Attachment Guide

| Evidence Type | When to Use | Format | Max Size |
|--------------|-------------|--------|----------|
| Screenshot | UI-based bugs, visual proof | PNG/JPG | 5MB |
| curl log | API-based bugs | Text | 1MB |
| Full HTTP request/response | Auth/IDOR/SSRF | Text (headers + body) | 1MB |
| Video PoC | Complex chains, race conditions | MP4/GIF | 25MB |
| Exploit script | SQLi, RCE, SSRF | Python/bash | 500KB |
| Code diff | Source review, insecure code | Text | 500KB |

### Naming Convention
```
poc_2026-07-23_idor_orders.png
poc_2026-07-23_injection_exploit.py
request_response_2026-07-23.txt
```

## Chain Report Format

When reporting chained findings, use combined format:

```markdown
# Attack Chain: [Chain Name] — [Final Impact]

## Chain Summary
[Step 1] → [Step 2] → [Step 3] = [Final Impact]

## Individual Findings

### Finding 1: [Vuln Type] in [Endpoint] — [Severity]
(CVSS + PoC + Impact)
→ Enables Finding 2 by [mechanism]

### Finding 2: [Vuln Type] in [Endpoint] — [Severity]  
(CVSS + PoC + Impact)
→ Enables Finding 3 by [mechanism]

### Finding 3: [Vuln Type] — [Critical/Combined Severity]
(CVSS + PoC + Final Impact)

## Combined Impact
What the attacker can achieve by exploiting all three:

## Why Chain Matters
Individual findings are Low/Medium separately.
Together they enable [Critical impact].

