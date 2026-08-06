---
name: part1-mindset
description: Core hunting mindset — goal-first thinking, 4 thinking domains, amateur-vs-pro discipline, anti-patterns to avoid.
---

# MINDSET

Hunting is proving an attack scenario, not pattern-scanning. Before touching a tool: **Define** ("today I target X to achieve [C/I/A/ATO/RCE]") → **Select** (1-2 vuln classes only) → **Execute** (no wandering outside the selection).

## 5 goals — pick exactly one per session
Confidentiality (steal data) · Integrity (modify data) · Availability (app-level DoS only) · Account Takeover · RCE.

## 4 thinking domains

**Critical thinking** — question every trust boundary: is a check client-side only (bypass via proxy)? does a role/price field trust client input? Reverse-engineer developer psychology: a new similar feature probably repeats an old feature's auth gap; complex flows (coupon+points+refund) hide edge-case bugs; an old API version (`/v1/`) may still work with weaker auth than `/v2/`. Run "what-if" experiments: skip a step and hit the endpoint directly; fire the same request 10x concurrently (race?); swap a UUID for a sibling endpoint's sequential ID (IDOR?).

**Multi-perspective** — same role, different user (horizontal IDOR) · different role entirely (vertical, e.g. user→admin route) · full request/response data flow, not just the rendered page (hidden JSON params) · time/state (race conditions, session reuse post-delete) · client environment (mobile UA → legacy weaker API) · business impact ("what's the $ damage if this breaks?").

**Tactical thinking (pattern detection)** — naming inconsistency (`userId` everywhere, one `user_id` = different dev, likely weaker) · error response structure differs for the same status code = different backend · a 200 with a tiny body or "just a moment" text is a WAF soft-block, not a real response — verify before treating it as success · prod vs dev/staging config diffs (debug headers, disabled CSP) · JS diffed across versions reveals removed params/new routes · check framework/library versions against known CVEs · third-party integrations (Stripe/Auth0) missing webhook signature verification.

**Strategic thinking** — asymmetry: the defender must close every hole, you need one. Log the "feels wrong" intuition immediately and verify later — don't lose the signal. Can't resolve something now? Park it explicitly as "investigate later," don't let it stall the session.

**AI-assisted thinking** — use the model to expand hypotheses, never to declare a verdict. It's an adversarial-idea generator; the proxy and live requests are the only proof layer. Ask it to: decompose the feature (actors, assets, entry points, trust boundaries) · generate sibling paths (versioned/mobile/legacy endpoints, alternate roles) · build a role matrix (anon, user A, user B, stale session, admin, service account) · name likely developer shortcuts · predict adjacent bugs B/C if bug A is real. Every AI suggestion must become one reproducible HTTP request — if it can't point to a concrete request/response delta, it stays an unverified hypothesis, not a finding.

## Amateur vs pro
| Phase | Amateur | Pro |
|---|---|---|
| Recon | Main domain only | Shadow IT, dev environments, full asset set |
| Discovery | Looks for errors | Looks for design contradictions, logic flaws |
| Exploit | Gives up when blocked | Builds filter-bypass payloads |
| Escalation | Reports the phenomenon | Chains to real harm (session theft, ATO) |
| Feasibility | Includes unrealistic conditions | Minimizes attack prerequisites |
| Reporting | States facts only | Quantifies business risk |
| Retest | Checks if the old PoC still fails | Analyzes the fix, hunts incomplete patches |

## Two entry routes
**Feature-based**: pick a complex feature → deep-dive its input handling → find the bug. **Vuln-based**: pick a vuln class (e.g. IDOR) → find endpoints with sequential/guessable IDs → test access control.

## Anti-patterns — stop doing these
Program-hopping before 2 weeks / 30 hours on one target · relying on automation alone (it finds duplicates; manual testing finds unique bugs) · rabbit-holing past 45 minutes on one parameter (set a timer, move on if stuck) · testing without a defined goal ("just looking around" wastes the session).
