---
name: part4-analysis-methodology
description: Root-cause analysis method — hunt inconsistencies (parsing/state/trust/encoding/boundary) instead of named vuln classes, plus hypothesis ranking and confidence scoring.
---

# ANALYSIS METHODOLOGY — root cause focus

**Core shift**: don't search for "XSS" — search for data reaching an unexpected context. Don't search for "IDOR" — search for broken trust. Don't search for "SSRF" — search for unexpected network trust. Every named vulnerability is evidence of a deeper inconsistency; find the inconsistency and the vuln class follows.

## 6-phase process

1. **Business purpose** — before any technical look: why does this feature exist, what problem does it solve, what is the developer incentivized to protect, and — just as important — what are they *not* incentivized to protect (that's usually where the gap is)?
2. **Technology stack** — identify frontend, backend, database, infra, auth, cache layers fully before proceeding. Each layer has its own attack surface; skipping this means guessing blind later.
3. **Architecture** — trace the request path (user → frontend → CDN → WAF → proxy → app → API gateway → microservices → DB, plus any queue/worker/external-API leg). For every hop ask: where's the trust boundary, what assumption crosses it, where is validation actually performed vs assumed, and do any two components parse the same input differently?
4. **Developer assumptions** — what did the developer assume is impossible? which inputs were treated as trusted by default? what edge cases were (intentionally or not) ignored? what shortcuts were taken under deadline pressure? Assume a vulnerability exists wherever confidence replaced verification.
5. **Hunt inconsistencies** — five categories, check all five, not just the obvious one: **parsing** (do frontend/backend/gateway/DB interpret the same input identically — if not, that gap is the vuln) · **state** (can a request land while the system is in an unexpected state — race conditions, desync, TOCTOU) · **trust** (does one component trust another's data without verifying it — SSRF, CSRF, OAuth misconfig) · **encoding** (does encoding change between components — Unicode normalization, URL encoding, Base64 variants) · **boundary** (what happens at limits — max values, empty, negative, null).
6. **Build and rank hypotheses** — for each inconsistency found, write a specific testable hypothesis ("if I change parameter X to Y, the system responds with Z"), score it on Impact/Likelihood/Exploitability (0-10 each), test the highest combined score first, and update the knowledge base after — not just the finding log.

## Cross-layer check
Every request crosses layers that may disagree on the same input: browser (URL/HTML/JS encoding, normalization) · CDN (cache keys, Vary headers) · WAF (content-type, encoding variants) · reverse proxy (path normalization) · framework (routing, middleware order) · application (validation assumptions) · ORM (type coercion) · database (Unicode, collation). Any two layers disagreeing on the same input is worth investigating — that disagreement is often the exploit primitive itself.

## "What must be true?" — replaces "can I exploit this?"
Before attempting exploitation: list every condition that must hold for the attack to succeed, verify each independently, and recognize the attack fails if any single one is false. This catches false leads before they waste testing time, not after.

## Self-critique before concluding
Did I actually understand the architecture and business logic, not just poke at inputs? Did I identify all trust boundaries and test the developer's assumptions, not just the obvious one? Can I explain *why* something is secure, not just that my attempt failed? Did I only search where everyone else searches? What would a more experienced researcher check next, given unlimited time?

## Confidence assessment — record per finding
Confidence (0-100%) · evidence tier (A = direct proof, B = strong inference, C = weak inference, D = theoretical) · what information is missing that would change the assessment · what alternative explanation could account for the same observation · how this specific finding could be a false positive.
