# SKILL-FORMAT — authoring standard

Every skill in HuntPack must conform to the open **Agent Skills** standard
([agentskills.io](https://agentskills.io)) so it runs on **any** compliant agent —
Claude Code, OpenCode, Codex, Cursor, Gemini, Copilot — without porting.

## Folder layout

```
skills/<category>/<skill-name>/
├── SKILL.md            # REQUIRED — frontmatter + instructions
├── references/         # OPTIONAL — loaded on demand (progressive disclosure)
├── scripts/            # OPTIONAL — executable helpers
└── assets/             # OPTIONAL — templates / fixtures
```

- The folder name is the canonical skill ID.
- The frontmatter `name` **must equal** the folder name, lowercase kebab-case.

## Frontmatter (only `name` + `description` are required)

```markdown
---
name: <kebab-case>
description: >          # English, 1–1024 chars. WHAT it does + WHEN to use it.
  <the trigger — write this for the agent's router, not for humans.>
license: MIT            # optional but recommended
compatibility: ...      # optional — env/CLI requirements
metadata:               # optional — author, version, category
  category: <stage>
---
```

Rules:
- `name`: lowercase `a-z0-9` + hyphens only, ≤ 64 chars, must match folder.
- `description`: **third person**, 1–1024 chars, says **both** what and when.
  This is the only text the agent sees before deciding to load the skill — make it count.
- No XML angle brackets (`<` `>`) in frontmatter — they can inject into the system prompt.

## Body rules

- Keep `SKILL.md` under **500 lines**. Push heavy content into `references/`.
- **Default assumption:** the agent already knows security fundamentals. Only add context it
  doesn't have. Dead content costs tokens.
- Use **imperative steps, real commands, explicit rules, named anti-patterns**.
- Prefer `references/*.md` for checklists, tables, long examples — loaded only when referenced.

## The discipline requirement

Security skills carry a non-negotiable rule: **PoC or nothing.**

1. Every claim must be reproducible — a fingerprint or CVE is **never** evidence.
2. Read the target's scope; authorize before testing.
3. Harmless, non-destructive requests only. No brute-force or DoS by default.

## Validate your skill

```bash
python3 scripts/validate-skills.py skills/<category>/<skill-name>
# ✅ All skills valid.
```

CI runs this on every PR. See `CONTRIBUTING.md` for the submission process.