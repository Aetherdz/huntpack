---
name: bb-methodology
description: >
  Use at the start of any bug bounty session, when switching targets, or when unsure what to do next. Master router combining the 5-phase workflow with the critical-thinking mindset framework.
  Also use for "what should I do next" or "where am I in the process."
---

# BUG BOUNTY METHODOLOGY — master router

This file routes, it doesn't duplicate. Load the referenced part for depth; use this table only to decide which one.

| Part | Load when... |
|---|---|
| 0 — Knowledge Base Auto-Load (`reference/phase0-knowledge-base.md`) | Always first, every session, before any recon/test |
| 1 — Mindset (`reference/part1-mindset.md`) | Need the thinking framework — goal selection, trust-boundary questioning, anti-patterns |
| 2 — Workflow (`reference/part2-workflow.md`) | Need the concrete phase-by-phase actions (recon → mapping → discovery → prove → report) |
| 3 — Navigation & Timing (`reference/part3-navigation-timing.md`) | Stuck, rotating targets, or need the tool-order table |
| 4 — Analysis Methodology (`reference/part4-analysis-methodology.md`) | Need root-cause/inconsistency-hunting depth instead of named-vuln-class hunting |

Default session order: 0 → 1 (once, sets the mindset) → 2 (drives the loop) → 3 (whenever stuck) → 4 (whenever Part 2's discovery phase needs deeper root-cause thinking, not just a vuln-class checklist).

## RESPONSE-DRIVEN NEXT ACTIONS

| You See | You Are In | Next Move |
|---------|-----------|-----------|
| 403 on all requests to endpoint | Recon/Discovery | Run 403 bypass checklist (headers, method swap, path variation). 5 min → skip. |
| 200 but body is SPA catch-all | Recon | Not a real endpoint. Try `.json`, `/api` prefix, format param. |
| Error stack trace on bad input | Discovery → Prove | Deepen error probe, chain to info disclosure, look for debug endpoints. |
| Timing diff on user-exists | Discovery → Prove | Automate enumeration → password spray or ATO chain. |
| WAF block page (403/406/429) | Discovery | Try Content-Type switch, HTTP/2→1.1, IP rotation. 5 min → kill path. |
| IDOR-confirmed (A reads B data) | Prove → Chain | Check if same IDOR affects PUT/DELETE → chain to data mod or ATO. |
| Race condition success (2x200, 2x change) | Prove | Verify ledger — both changes persisted? → financial impact chain. |
| 401 without token, 200 with any token | Mapping | Auth exists but weak ACL. Focus on IDOR, BOLA, mass assignment. |
| JWT in response with `role` field | Mapping → Prove | None-alg, weak secret, role tamper → chain to admin access. |
| GraphQL introspection on | Mapping → Discovery | Schema leak → field auth bypass → batching for mass PII. |
| Sibling endpoint found mid-session | Mapping | Re-score, add to model, generate new hypotheses. |

## WEAK PATH CANCELLATION (Stop Early, Save Time)

Kill the current path immediately when:
- 3 consecutive 403s with no bypass → STOP (auth gated)
- 5 min of recon on a host → SKIP (5-minute rule)
- 20 min on an endpoint with no signal → ROTATE (20-minute rule)
- A vs B sessions return identical data → STOP (no IDOR)
- `unique constraint` on race test → STOP (serialized)
- Confirmed intended behavior → STOP
- Score < 40 after 2 clean tests → STOP
- WAF blocking 3 different payload approaches → STOP

DEFER (don't kill) when:
- New technology detected mid-session → re-evaluate
- Score jumps 15+ points from new evidence → re-prioritize
- Chain opportunity appears for a low-sev finding
- Target just deployed an update

## EVIDENCE SCHEMA INTEGRATION

Every phase output must use the shared evidence schema below:
```yaml
evidence_id: "OBS-NNN" | phase: "recon"|"model"|"hunt"|"chain"|"validate"
type: "request"|"response"|"diff"|"observation"
source: "header"|"JS"|"API"|"curl"|"diff" | actor: "guest"|"user_a"|"user_b"|"admin"
signal: "sequential_id"|"missing_403"|"role_field"|"error_stack"|"timing_diff"
action: "exact curl/request" | expected: "what should happen" | actual: "what happened"
confidence: 0.3-1.0 | impact: "real" | reproducible: true|false
chain_candidate: false
```

No evidence → no claim → kill it.
