---
name: part2-workflow
description: 5-phase non-linear hunting workflow — recon, mapping, discovery, prove/escalate, validate/report — with decision tables per phase.
---

# WORKFLOW

**Non-linear.** Move freely between phases — stuck at any phase, go back. New API found while proving impact → return to Mapping. WAF blocks the payload → recheck origin IP from Recon.

Sequence: Recon → Mapping → Discovery → Prove → Report, with backward jumps whenever a phase surfaces something the prior phase should have caught.

**Tool note**: the wrapper scripts below are optional conveniences, not requirements — if a wrapper is missing, do the equivalent manually (hand-encode payloads, mutate multipart in Burp Repeater, use `X-Original-URL`/`..;/`/case-swap tricks for 403 bypass) rather than skipping the step.

## Phase 0: Session start (every time)
1. **Define**: target + feature + goal (C/I/A/ATO/RCE).
2. **Select**: 1-2 vuln classes only.
3. **Execute**: stay on the selected techniques.
4. **Identity**: decide anonymous vs authenticated. If the target bug class needs a session (IDOR, BOLA, privesc, auth bypass, mass assignment), load auth once at session start so every downstream tool inherits it automatically and logs are stamped with a stable session ID.

**Wide vs deep** — go wide (recon sweep) on: a new program's first day, a wildcard scope, a scope update adding a new domain. Go deep (focused testing) on: a main webapp you've worked >3 days, an interesting subdomain just found, or when hunting IDOR/BOLA/auth bugs specifically (these need an authenticated, focused pass, not a sweep).

## Phase 1: Recon
Goal: maximize attack surface, find what others missed.
**Wide**: subdomain enum (passive + CT logs + GitHub dorking, not brute-force alone) → DNS resolution → HTTP probing → port scan → tech detect → dangling-CNAME/takeover check on every new host.
**Deep**: Google dorks → JS file download → hidden param discovery → API mapping.
**Not one-off**: on any target you're actively hunting >1 session, re-run the passive sweep periodically and diff against the saved list — new subdomains/certs appear between sessions and are often untested by anyone else yet. See Part 3's tool-routing table for the exact pipeline and cadence.

| Found | Next |
|---|---|
| Live subdomains + tech stack | → Phase 2 |
| Known software (WordPress, Jira) | Check CVEs + default creds immediately |
| Cloud resources (S3, Firebase) | Test read/write/list permissions |
| 403, or 200 with a block-page body | Run the bypass check — verdict is bypassed/needs-review/blocked; if still blocked after 5 min, skip |
| Nothing after 5 min on a host | Skip to next host (5-minute rule) |

## Phase 2: Mapping & analysis
Goal: understand the app the way its developer does.
Map every endpoint · identify the auth model (cookie/JWT/OAuth/SAML) · find business-critical flows (payment, registration, password reset, data export) · download and analyze JS for hidden routes/secrets/logic · map roles and permissions · note naming/error/timing anomalies.

| Found | Next |
|---|---|
| Interesting JS logic | Taint analysis (sink → source) |
| OAuth/SAML | Run the OAuth/SAML checklist |
| API with ID parameters | → Phase 3, target IDOR |
| Complex business logic (payment, coupon) | → Phase 3, target business logic |
| postMessage listeners | DOM analysis |

## Phase 3: Vulnerability discovery
Goal: find the bug — error-based signals first, then blind.

Route by input type: ID parameter → IDOR checklist · search/filter/sort field → SQLi/NoSQLi · URL input/webhook/PDF generator → SSRF checklist · reflected text field → XSS (DOM or reflected) · file upload → SVG XSS/webshell/path traversal · price/quantity/coupon → business logic/race conditions · login/2FA/reset → auth bypass · profile update API → mass assignment · template/wiki editor → SSTI · nothing obvious → fuzz (ffuf) or error-based probing.

**Escalating signal strength**: error-based first (`'`, `"`, `{{7*7}}`, watch for 500s/stack traces) → no error, try time-based (`SLEEP(10)`, watch response time) → no time diff, try out-of-band (`curl attacker.com`, interactsh, watch for callback) → still nothing, try boolean diff (`AND 1=1` vs `AND 1=0`, watch content-length).

| Found | Next |
|---|---|
| Low-impact behavior (redirect, self-XSS, cookie injection) | Chain it — find a connector gadget |
| Confirmed vuln | → Phase 4 |
| Blocked by WAF/CSP/403 (or soft-block 200) | Run bypass check → check the verdict, not just the status code → encode variants → 5 min cap, then kill |
| Known-software CVE | Fast-path that CVE's exploit workflow |
| Nothing after 20 min on this endpoint | Rotate (20-minute rule) |

## Phase 4: Prove & escalate
Goal: prove maximum business impact — turn Low into Critical.

| Found | Escalation path |
|---|---|
| XSS | Can steal cookie/token? → session hijack → ATO. Cookie is HttpOnly? → force email change via XHR → ATO. Self-XSS only? → find a CSRF to trigger it. |
| IDOR | Can read PII? → automate + show scale. Can change password/email? → direct ATO. UUID-only? → find the UUID leak source, retry. |
| SSRF | DNS-only? Don't report yet — try cloud metadata. Reaches `169.254.169.254`? → extract keys → RCE. Internal port scan reachable? → find Redis/K8s → RCE. |
| SQLi | Error-based → extract data. Can `INTO OUTFILE`? → webshell → RCE. Blind → boolean/time extraction. |
| Open redirect | Inside an OAuth flow? → token theft → ATO. `javascript:` scheme? → XSS. |
| Blocked by a defense | Bypass it (WAF/CSP/proxy/sanitizer/2FA) before giving up. |
| Low-impact, can't escalate alone | Find a connector gadget to chain into. |

After proving impact, confirm: does it work with 0-1 clicks (minimize prerequisites)? does it affect all users or one role? what's the $ business impact?

## Phase 5: Validate & report
Pre-report gate: run the 7-question validation. All 7 pass → write the report. Any fail → kill the finding, don't waste time on it. Borderline → quick triage pass for go/no-go.

Report structure: platform-specific format (H1/Bugcrowd/Intigriti/Immunefi) · title = `[Bug Class] in [Endpoint] allows [role] to [impact]` · impact-first summary (sentence 1 = what the attacker can actually do) · exact HTTP requests in steps to reproduce · under 600 words · CVSS score that matches the actual proven impact, not the theoretical maximum.

After submission: keep trying to escalate further while triage is pending · if a fix deploys, retest for bypass (an incomplete patch is a new bug) · log the finding for future-session recall.
