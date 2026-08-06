## 9. DEVELOPER PLATFORM / API

### Signature Assets
- API keys, tokens, PATs (Personal Access Tokens)
- Source code, repositories
- CI/CD pipelines, workflows
- Cloud resources, deployments
- Developer accounts, orgs
- Issues, PRs, code reviews
- Infrastructure configs (Docker, K8s, Terraform)

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| Developer | Push code, manage repos | CI/CD injection |
| Org Admin | Manage org, billing | OAuth abuse |
| Machine/CI | Automated actions | Token persistence |
| Owner | Full org control | Permission escalation |

### Priority Attack Surface

```
1. CI/CD PIPELINE INJECTION ← CRITICAL, $$$
   PR with malicious workflow                 → trigger on pull_request_target
   POST /.github/workflows/{id}/dispatch      → inject commands
   PUT  /api/repos/{owner}/{repo}/actions/secrets → steal secrets
   Test: workflow_run, pull_request_target, issue_comment triggers

2. PAT / TOKEN ABUSE
   GET  /api/tokens/{id}                       → list others' tokens
   POST /api/tokens                            → create token with elevated scopes
   PUT  /api/tokens/{id}/scopes                → escalate token permissions
   Test: create token with repo:admin, delete repo

3. WORKFLOW INJECTION (pull_request_target)
   PR from fork: malicious .github/workflows/*.yml → runs on base repo
   Script injection in issue/PR body               → context: github.token
   Test: create PR with malicious workflow, check if it runs

4. SECRET LEAKAGE (BUILD LOGS)
   POST /api/repos/{owner}/{repo}/dispatches   → trigger build
   GET  /api/repos/{owner}/{repo}/actions/runs/{id}/logs → check logs for secrets
   Test: workflows that echo environment variables

5. OAuth APP ABUSE
   GET  /api/apps/{id}/installations            → list all installations
   POST /api/apps/{app}/installations/{id}/access_tokens → create access token
   Test: create OAuth app → trick user → steal tokens → access org

6. DEPENDENCY CONFUSION
   npm install @company/internal-package       → published on public npm?
   pip install company-internal                → published on PyPI?
   Test: check if internal package names exist publicly
```

### Top Attack Chains
```
1. [Critical] CI/CD Injection → Steal AWS_ACCESS_KEY_ID from Build → Cloud Account Takeover
2. [Critical] OAuth App → User Installs → Steal Token → Access Private Repos → Extract Secrets
3. [Critical] PAT Leak → Full Repo Access → Clone All Code → Find More API Keys in Code
4. [High]      Dependency Confusion → Publish Malicious Package → Infect 10K+ Builds
5. [High]      Workflow Injection → PR Opens → Workflow Runs → RCE on Runner → Pivot
```

### Real H1 Examples
- DuckDuckGo: CI/CD pipeline injection (Critical, #3619288)
- GitHub: PAT abuse (#3522254, #3506183)
- Cloudflare: OAuth app token theft (#3423950)

---

