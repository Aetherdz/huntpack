# Install & usage — per agent

HuntPack ships with the **Agent Skills** open standard: every skill is a self-contained folder with
a `SKILL.md` using only standard frontmatter (`name`, `description`). No agent-specific tooling.
It works on **any** standard-compliant agent — the only difference is where each agent looks for skills.

## The structure (why it's organized this way)

```
HuntPack/
├── router/                  ← the master dispatcher — load first, it routes to the right skill
├── skills/
│   ├── understand/          ← application-archetypes, application-model-builder
│   ├── recon/               ← web2-recon
│   ├── hunting/             ← web2-vuln-classes, business-logic-hunter, api-security
│   ├── discipline/          ← domain-scoped-hunting
│   ├── validation/          ← false-positive-killer, triage-validation
│   └── reporting/           ← attack-path-builder, report-writing
└── .claude-plugin/marketplace.json  ← one-command install for Claude Code
```

Skills are grouped by **pipeline stage**, mirroring the layout of the most-mature open-source skill
repositories (categories + a master `router`). The router reads which stage you're in and delegates
to the right specialized skill.

## Discovery paths

| Agent | Personal / global | Project |
|---|---|---|
| **Claude Code** | `~/.claude/skills/` | `.claude/skills/` |
| **OpenCode** | `~/.config/opencode/skills/` | `.opencode/skills/` |
| **Codex CLI** | `~/.agents/skills/` | `.agents/skills/` |
| **Cursor** | — | `.cursor/skills/` |
| **Gemini CLI** | `~/.gemini/skills/` | — |

## Option A — Marketplace (Claude Code, best UX)

```bash
claude install-plugin https://github.com/Aether-DZ/huntpack
claude plugin update huntpack
```

## Option B — Copy (works on any agent)

```bash
git clone https://github.com/Aether-DZ/huntpack.git
cd HuntPack

# install the router + every category (example: Claude Code)
mkdir -p ~/.claude/skills
cp -r router ~/.claude/skills/
cp -r skills/* ~/.claude/skills/
```

> Nested folders (`skills/hunting/web2-vuln-classes/`) are discovered by standard-compliant
> agents — the `name` field in each `SKILL.md` matches the leaf folder.

## Option C — Symlink (single source)

```bash
cd HuntPack
mkdir -p ~/.claude/skills
ln -s "$(pwd)/router" ~/.claude/skills/router
for d in skills/*/; do ln -s "$(pwd)/$d" ~/.claude/skills/; done
```

## Option D — Vercel skills CLI

```bash
npx @vercel/skills install --agent claude-code --scope personal --link ./skills
```

## Install a single skill

```bash
mkdir -p ~/.claude/skills
cp -r skills/hunting/business-logic-hunter ~/.claude/skills/
```

## Suggested start order

```
router
  → understand/ → recon/        (build the model, then the surface)
  → discipline/                  (load domain-scoped-hunting BEFORE any hunt)
  → hunting/                     (execute the bug-class skill)
  → validation/                  (prove: false-positive-proof → triage gate)
  → reporting/                   (chain & write the report)
```

## Troubleshooting

| Problem | Fix |
|---|---|
| Skill not loading | Restart the session; verify the folder is in the right discovery path; check `name` matches the folder name. |
| Router doesn't fire | Use "test", "hunt", "assessment", or name a bug class — the router's `description` is the trigger. |
| Symlinked skill gone | Some agents don't follow symlinks — use `cp -r` instead. |
| Reference not loading | Keep references one level deep under the skill folder. |
| Validate the whole pack | `python3 scripts/validate-skills.py` |