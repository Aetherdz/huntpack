# skills/

The skill collection, organized by pipeline stage:

| Category | Folder | Scope |
|----------|--------|-------|
| Understand | [`understand/`](understand/) | Target recognition & application modeling |
| Map surface | [`recon/`](recon/) | Attack-surface discovery |
| Hunt | [`hunting/`](hunting/) | Bug-class execution matrices (web2, business logic, API) |
| Discipline | [`discipline/`](discipline/) | Anti-fabrication discipline — load before any hunt |
| Prove | [`validation/`](validation/) | False-positive elimination & acceptance gates |
| Deliver | [`reporting/`](reporting/) | Attack-path chaining & report writing |

| Skill | Category | What it does |
|-------|----------|--------------|
| [`application-archetypes`](understand/application-archetypes/) | Understand | Classify the target type and get its ready-made asset/role/workflow map + top logic bugs |
| [`application-model-builder`](understand/application-model-builder/) | Understand | Build the app model (assets, actors, permissions, trust boundaries) before any payload |
| [`web2-recon`](recon/web2-recon/) | Map surface | Subdomains, live hosts, crawling, JS analysis, fuzzing |
| [`web2-vuln-classes`](hunting/web2-vuln-classes/) | Hunt | 24 web2 bug classes — root cause, detection, bypass tables, paid examples |
| [`business-logic-hunter`](hunting/business-logic-hunter/) | Hunt | Business-logic execution matrix — SIGNAL → TEST → CONFIRM → KILL |
| [`api-security`](hunting/api-security/) | Hunt | REST / OAuth / JWT attack patterns |
| [`domain-scoped-hunting`](discipline/domain-scoped-hunting/) | Discipline | Domain declaration, boundaries, pivot hints, honest exit rules |
| [`false-positive-killer`](validation/false-positive-killer/) | Prove | Re-test from clean state, eliminate theoretical bugs |
| [`triage-validation`](validation/triage-validation/) | Prove | 8-question acceptance gate before any report |
| [`attack-path-builder`](reporting/attack-path-builder/) | Deliver | Chain low/med findings into critical paths |
| [`report-writing`](reporting/report-writing/) | Deliver | Structured reports with PoC, impact, remediation |

Each skill is a folder with a `SKILL.md`. The folder name must equal the skill's
`name` frontmatter field. The master router lives in [`../router/`](../router/).

See [`../docs/SKILL-FORMAT.md`](../docs/SKILL-FORMAT.md) for the authoring standard and
[`../CONTRIBUTING.md`](../CONTRIBUTING.md) for how to add a skill.