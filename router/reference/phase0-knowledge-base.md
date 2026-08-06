---
name: phase0-knowledge-base
description: Mandatory pre-session step — gather target intelligence from public sources, build a local knowledge base of known patterns for the target's stack, then bootstrap the methodology before any active testing.
---

# PHASE 0: KNOWLEDGE BASE — mandatory first step

Before any recon, mapping, or test — in this order:

## 0.1 Build a local knowledge base
Maintain a local, per-target knowledge base that captures known weaknesses. A simple approach:
- `KNOWLEDGE.md` — system overview, target scope, key tech stack
- `root-causes/` — the recurring root cause categories you have seen pay (broken auth, state desync, broken assumptions, etc.)
- `attack-patterns/` — attack-surface map per technology
- `technologies/` — known weaknesses per detected stack
- `exploit-chains/` — proven A→B→C chain patterns
- `confidence/` — how you score evidence confidence

## 0.2 Gather target-specific intelligence
Before touching the target, research publicly disclosed reports:
- HackerOne **Hacktivity** and Bugcrowd **CrowdStream** for the same target/stack
- GitHub for disclosed reports / PoCs matching the detected technology
- Prior assessments you or your team recorded for this target
Build from **known patterns — not guesswork.**

## 0.3 Apply knowledge to the target
1. Identify the target's technology stack.
2. Cross-reference it against your `technologies/` index for known weaknesses.
3. Map root-cause → attack-surface relationships.
4. Check attack patterns relevant to the detected surfaces.
5. Search hacktivity for report patterns seen in the same stack.
6. Form hypotheses from these patterns — never from speculation.

## 0.4 Update the knowledge base
Record any genuinely new pattern observed during the session back into the local knowledge base so it compounds for future targets.

## Mandatory session bootstrap (after Phase 0, before any active recon/test)
Follow the methodology in order: `application-model-builder` → `application-archetypes` → `web2-recon` → hunt skills → `false-positive-killer` → `triage-validation` → `attack-path-builder` → `report-writing`.

The session must produce a versioned plan and a ranked task graph before execution begins. New evidence during testing triggers a replanning cycle — it does not silently expand scope on its own.