# Contributing to HuntPack

Thanks for helping make this library better. Keep a few rules in mind.

## Golden rules for every skill

1. **PoC or nothing.** Every claim must be reproducible. No theory, no "could potentially."
2. **Works on any agent.** Use only the open Agent Skills frontmatter — `name` + `description`. No agent-specific tool calls in `SKILL.md`.
3. **Progressive disclosure.** Keep `SKILL.md` short (< ~500 lines). Push heavy content into `references/`.
4. **The discipline layer survives.** Adding a payload dump is not a contribution — strengthening `domain-scoped-hunting`, `false-positive-killer`, or `triage-validation` *is*.
5. **No secrets, ever.** No absolute paths, API keys, tokens, or private target data.

## Frontmatter standard

```yaml
---
name: your-skill    # lowercase kebab-case, must match folder name
description: >      # English, 1–1024 chars: WHAT it does + WHEN to use it
  ...this is the trigger the agent reads to decide to load the skill...
---
```

## Validation before you submit

```bash
# every skill folder must have a SKILL.md with valid name+description
for s in skills/*/; do
  echo "$s: name=$(grep -c '^name:' "$s/SKILL.md") desc=$(grep -c '^description:' "$s/SKILL.md")"
done

# no internal / personal references may escape
grep -rn "/home/\|/root/\|BEGIN.*PRIVATE" skills/ || echo "clean"
```

## Process

1. Fork, create a branch.
2. Add or improve a skill in `skills/<name>/`.
3. Run the validation above.
4. Open a PR. Describe *what* and *why*, and show the `description` you wrote for the trigger.