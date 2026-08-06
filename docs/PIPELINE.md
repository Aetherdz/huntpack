# The HuntPack methodology — pipeline walkthrough

HuntPack is built on one idea: **a bug bounty hunt is a pipeline, and most failures happen in the discipline stages, not the payload stages.** This document walks through each stage and why it exists.

## Stage 0 — Conduct (`bb-methodology`)

The master router. When you start a hunt, run this first. It tells the agent:
- **Where am I in the 5-phase workflow?**
- **What should I run next?**
- **Should I continue or stop?**

Every phase output feeds a shared evidence schema so findings stay comparable.

## Stage 1 — Understand (`application-archetypes` → `application-model-builder`)

Most hunters fire payloads at a target they don't understand. This stage forces the opposite:

- **`application-archetypes`** — instantly classify the target (e-commerce, SaaS, fintech, marketplace, admin, CMS) and get ready-made asset/role/workflow maps plus the **top logic bugs per type**.
- **`application-model-builder`** — the mandatory step *before* any payload. Build the model: assets, actors, permissions, workflows, trust boundaries, state machines — then *break assumptions*. Unknowns are marked **unknown**, never guessed.

**Why it matters:** the highest-bounty bugs (business logic, IDOR, privilege escalation) only appear once you know who the actors are and what they're *supposed* to do.

## Stage 2 — Map surface (`web2-recon`)

- Subdomain enumeration (passive + active)
- Live host discovery
- URL crawling + wayback
- Directory fuzzing, JS analysis, GitHub dorking, ASN/cloud discovery

Output: a ranked attack surface — where authorization boundaries and hidden endpoints are.

## Stage 3 — Hunt (`web2-vuln-classes` · `business-logic-hunter` · `api-security`)

The knowledge layer:
- **`web2-vuln-classes`** — 24 bug classes with root cause, detection pattern, bypass tables, and real paid examples.
- **`business-logic-hunter`** — the highest-bounty category. An execution matrix: **SIGNAL → TEST → CONFIRM → KILL** per pattern (workflow bypass, race conditions, discount manipulation, subscription abuse, OTP gaps, wallet manipulation…), plus response-driven next actions.
- **`api-security`** — REST / OAuth / JWT patterns with the same killable-test discipline.

## Stage 4 — Discipline (`domain-scoped-hunting`)

**Load this before every hunt.** It is the anti-fabrication layer most tools lack:
- You must **declare the domain** you're testing.
- Set **boundaries** (what's in / out of scope).
- Given **pivot hints** — where to go when blocked.
- Have **exit evidence** — a positive requires verified proof; a negative requires honest *"not found under current evidence"*, never a claim.

> **Anti-fabrication rule:** a fingerprint or CVE is **never** evidence of exploitability. Only a reproducible PoC is.

## Stage 5 — Prove (`false-positive-killer` → `triage-validation`)

The difference between a valid report and a `won't-fix`:
- **`false-positive-killer`** — re-test from a clean state, compare responses, eliminate theoretical bugs, assign confidence.
- **`triage-validation`** — the final **8-question acceptance gate** before any report leaves. One wrong answer = kill.

## Stage 6 — Deliver (`attack-path-builder` → `report-writing`)

- **`attack-path-builder`** — chain scattered low/med findings into one critical path (account takeover, privesc, data breach). A verified chain beats ten standalone lows — but every link must be independently verified.
- **`report-writing`** — structured, reproducible reports with PoC, impact, and remediation.

---

## Why this ordering wins

1. **Understand before firing** → higher hit rate, fewer burnt targets.
2. **Discipline gate** → the false-positive rate drops, protecting your reputation and your report/`N/A` ratio.
3. **Chain-first reporting** → one critical, verified finding usually outranks many unverified lows.
4. **Every stage produces evidence** → nothing is "claimed," everything is reproducible.