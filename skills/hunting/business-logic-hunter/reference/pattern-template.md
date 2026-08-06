# PATTERN TEMPLATE — For new business logic bugs

## Copy this to create a new pattern file
```markdown
# PATTERN NAME — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| Attack variant | What to look for | `curl exact command` | Expected success condition | When to stop |

## CURL COMMANDS
\`\`\`bash
# exact commands
\`\`\`

## DECISION TREE
\`\`\`
Found [signal]?
├─ Try [test]?
│  ├─ Success → [attack type]
│  └─ Fail → [what to try next]
└─ [else]
\`\`\`

## CHAIN
[Attack] + [Another] = [Impact]
```
