# HuntPack

> **Method-first bug bounty skills for AI agents.**
> *PoC or nothing — the discipline layer most security skill packs are missing.*

A compact, universal pack of **agent skills** that turns any AI coding agent — **Claude Code, OpenCode, Codex, Cursor, Gemini CLI, GitHub Copilot**, or any tool that supports the open [Agent Skills](https://agentskills.io) standard — into a disciplined bug bounty hunter.

**12 skills. 6 pipeline stages. Zero theory. Every finding must be proven.**

---

## Why HuntPack is different

Most "hacking skill" repos are **payload dumps** — hundreds of curl one-liners with no way to tell real from noise. HuntPack is the opposite. It is a **disciplined hunting pipeline** that:

| What others give you | What HuntPack gives you |
|---|---|
| A list of payloads | A full **pipeline**: understand → map → hunt → stay-honest → prove → deliver |
| "Could potentially be vulnerable" | **"PoC or nothing."** No proof → no claim → kill it. |
| A heap of files | 12 focused skills, each with evidence gates and exit rules |
| Breadth | The **business-logic + validation layers** that actually pay in bug bounties |

The core differentiator is the **discipline layer** — `domain-scoped-hunting`, `false-positive-killer`, and `triage-validation`. These force the agent to *prove* a finding before it ever reports it, which is exactly what separates a paid report from a triaged-as-won't-fix one.

---

## The pipeline

```
    ┌────────────┐   ┌───────────────┐   ┌───────────┐
  1 │  Understand │ → │ 2 Map surface │ → │ 3  Hunt   │
    └────────────┘   └───────────────┘   └─────┬─────┘
                                               │
    ┌────────────┐   ┌─────────────┐   ┌───────▼─────┐
 6  │  Deliver   │ ← │ 5  Prove     │ ← │ 4 Discipline │
    └────────────┘   └─────────────┘   └─────────────┘
```

| Stage | Skills | What it does |
|---|---|---|
| **0. Conduct** | `router` | Master dispatcher — tells the agent *where it is* and *what to run next*. |
| **1. Understand** | `application-archetypes` → `application-model-builder` | Recognize the target type, then build its model (assets, actors, trust boundaries) **before** any payload is sent. |
| **2. Map surface** | `web2-recon` | Subdomains, live hosts, URL crawling, JS analysis, fuzzing. |
| **3. Hunt** | `web2-vuln-classes` · `business-logic-hunter` · `api-security` | 24 bug classes + business-logic execution matrix + REST/OAuth/JWT patterns. |
| **4. Discipline** | `domain-scoped-hunting` | Loads *before* any hunt: domain declaration, boundaries, pivot hints, honest exit rules. **Anti-fabrication.** |
| **5. Prove** | `false-positive-killer` → `triage-validation` | Re-test from a clean state, kill false positives, run the 8-question acceptance gate. |
| **6. Deliver** | `attack-path-builder` → `report-writing` | Chain low/med findings into critical. Write structured reports. |

---

## Quick install

### Option A — marketplace (Claude Code)

```bash
claude install-plugin https://github.com/Aether-DZ/huntpack
```

### Option B — copy (works on any agent)

```bash
git clone https://github.com/Aether-DZ/huntpack.git
cd HuntPack

# example: install into Claude Code (personal)
mkdir -p ~/.claude/skills
cp -r router ~/.claude/skills/
cp -r skills/* ~/.claude/skills/
```

The standard discovery locations:

| Agent | Personal skills | Project skills |
|---|---|---|
| **Claude Code** | `~/.claude/skills/` | `.claude/skills/` |
| **OpenCode** | `~/.config/opencode/skills/` | `.opencode/skills/` |
| **Codex CLI** | `~/.agents/skills/` | `.agents/skills/` |
| **Cursor** | — | `.cursor/skills/` |
| **Gemini CLI** | `~/.gemini/skills/` | — |

### Option C — symlink (single source)

```bash
# keep the repo as single source, symlink into your agent
ln -s "$(pwd)/router" ~/.claude/skills/router
for d in skills/*/; do ln -s "$(pwd)/$d" ~/.claude/skills/; done
```

### Option D — Vercel skills CLI

```bash
npx @vercel/skills install --agent claude-code --scope personal --link ./skills
```

Restart your agent session. The skills auto-load when a task matches their description.

### Just want one skill?

Each folder is self-contained. Copy a single `skills/<category>/<name>/` into your agent and it works alone.

---

## Safety & scope — required reading

HuntPack is for **authorized** testing — your own applications, contractual pentests, or a target's official **bug-bounty scope**. Every skill assumes:

1. **Read the scope** and confirm the target is authorized before running. 
2. **No theory.** A fingerprint or CVE is *never* evidence of exploitability. Proof-of-concept or nothing.
3. Harmless, non-destructive requests only. No credential brute-forcing or DoS by default.

By using these skills you agree you are responsible for acting within the legal authorization of the targets you test and applicable bot-bounty-program rules.

---

## Repo layout

```
HuntPack/
├── router/               ← master dispatcher — tells the agent where it is & what to run next
├── skills/               ← organized by pipeline stage
│   ├── understand/       ← application-archetypes · application-model-builder
│   ├── recon/            ← web2-recon
│   ├── hunting/          ← web2-vuln-classes · business-logic-hunter · api-security
│   ├── discipline/       ← domain-scoped-hunting
│   ├── validation/       ← false-positive-killer · triage-validation
│   └── reporting/        ← attack-path-builder · report-writing
├── scripts/validate-skills.py   ← CI + local lint (frontmatter, leaks)
├── .claude-plugin/marketplace.json
├── docs/                 ← INSTALL · PIPELINE · SKILL-FORMAT
├── .github/workflows/validate.yml
├── LICENSE · CONTRIBUTING · CHANGELOG · SECURITY
└── README.md
```

This mirrors the layout of the most mature open-source skill repositories: a **master router** at
the top, and skills grouped by **discipline category**, each with an index table
(`skills/README.md`). Every `SKILL.md` uses only the open Agent Skills frontmatter standard
(`name` + `description`) so it runs on **any** standard-compliant agent with zero porting.

## How it works

```
         ┌───────────┐
         │   router   │  ← where are you? what's next?
         └─────┬─────┘
   ┌───────────┼───────────┐
   ▼           ▼           ▼
understand   recon      discipline
   │           │           │
   └───────┐   │           ▼
           ▼   ▼         hunting
        model → surface    │
                           ▼
                       validation
                           │
                           ▼
                       reporting
```

Start with the `router`. It reads the stage and delegates. Discipline loads *before* hunting.
Validation gates *every* finding before it reaches reporting.

---

## License

MIT — see [LICENSE](LICENSE). Use it, modify it, share it.

> **Disclaimer:** These skills are methodology and educational material. You are solely responsible for how you use them and for complying with applicable laws and authorization requirements.