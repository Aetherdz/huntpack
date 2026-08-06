# Install & usage — per agent

This guide covers installing HuntPack skills into the major agent platforms that support the open **Agent Skills** standard.

## What "works on any agent" means

Every skill is a self-contained folder with a `SKILL.md` that uses only the standard frontmatter (`name`, `description`). The file format is identical across agents; only the **discovery path** differs. So a skill is fully portable — you just drop it in the right directory for your agent.

## Discovery paths

| Agent | Personal (global) skills | Project (repo) skills |
|---|---|---|
| **Claude Code** | `~/.claude/skills/` | `.claude/skills/` |
| **OpenCode** | `~/.config/opencode/skills/` | `.opencode/skills/` |
| **Codex CLI** | `~/.agents/skills/` | `.agents/skills/` |
| **Cursor** | — | `.cursor/skills/` |
| **Gemini CLI** | `~/.gemini/skills/` | — |
| **VS Code / Copilot** | — | `.copilot/skills/` |

> OpenCode *also* reads `~/.claude/skills/` and `~/.agents/skills/` for compatibility. So installing into `~/.claude/skills/` covers Claude Code **and** OpenCode at once.

## Quick install (all 12)

```bash
git clone https://github.com/<you>/HuntPack.git
cd HuntPack

# copy every skill into your agent (example: Claude Code + OpenCode)
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

## Symlink (single source, stays in sync)

```bash
cd HuntPack
mkdir -p ~/.claude/skills
for d in skills/*/; do ln -s "$(pwd)/$d" ~/.claude/skills/; done
```

> Symlinks avoid duplicating files if you update the repo. Some agents may not follow symlinks — if a skill doesn't load, copy instead of symlinking.

## Vercel skills CLI

```bash
npx @vercel/skills install --agent claude-code --scope personal --link ./skills
```

## Install a single skill

```bash
# the whole point: each skill is independent
mkdir -p ~/.claude/skills
cp -r skills/business-logic-hunter ~/.claude/skills/
```

## Suggested start order

Use them in pipeline order for a real session:

```
bb-methodology
  → application-archetypes → application-model-builder
  → web2-recon
  → domain-scoped-hunting (before any hunt)
    → web2-vuln-classes / business-logic-hunter / api-security
  → false-positive-killer → triage-validation
  → attack-path-builder → report-writing
```

## Troubleshooting

| Problem | Fix |
|---|---|
| Skill not loading | Restart your agent session; verify the folder is in the correct discovery path; confirm frontmatter `name` matches the folder name. |
| Skill ignored by model | The `description` is the trigger — make sure your task wording matches it. Weak triggers never fire. |
| Symlinked skill disappears | Some agents don't follow symlinks — use `cp -r` instead. |
| Content too big | The reference files load on demand. Keep `SKILL.md` lean. |