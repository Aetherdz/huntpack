## 2. SAAS / CLOUD PLATFORM

### Signature Assets
- User accounts, profiles
- Files, documents, projects, workspaces
- API keys, tokens, webhooks
- Organizations, teams, billing
- Subscription plans, feature flags
- Notification settings, email preferences

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| Free User | Limited features | Trial abuse |
| Premium User | Full features | Downgrade access persistence |
| Org Admin | Manage members, billing | Mass assignment → Super Admin |
| Super Admin | Full system | Cross-tenant access |

### Priority Attack Surface

```
1. TRIAL/SUBSCRIPTION BYPASS ← BEST ROI
   POST /api/subscriptions/trial    → race condition (unlimited trials)
   GET  /api/features/premium       → access premium without paying
   PUT  /api/account/plan           → downgrade but keep features
   POST /api/account/cancel         → cancel but service not revoked
   Test: check feature flags after downgrade

2. CROSS-TENANT IDOR ← CRITICAL
   GET  /api/org/{id}/documents     → change org id
   GET  /api/workspace/{id}         → access other workspace
   GET  /api/team/{id}/members      → list other team members
   Test: Org A creates, Org B reads — compare IDs

3. API KEY / TOKEN ABUSE
   GET  /api/tokens                 → list all tokens (including others')
   POST /api/tokens                 → create token with higher scope
   PUT  /api/tokens/{id}/scopes     → escalate token permissions
   Test: check if API key inherits creator's permissions

4. SEAT/MEMBER ABUSE
   POST /api/org/{id}/members       → add unlimited members
   POST /api/org/{id}/invite        → invite self to other org
   PUT  /api/team/{id}/role         → escalate own role
   Test: add member beyond plan limit

5. FILE/STORAGE IDOR
   GET  /api/files/{id}             → access others' files
   GET  /api/files/{id}/download    → download without permission
   POST /api/files/share            → share with unauthorized users
   Test: sequential file IDs, UUID in URL parameter
```

### Top Attack Chains
```
1. [Critical] Cross-Tenant IDOR → Read Org B's API Keys → Access Org B's Cloud → Full Compromise
2. [High]      Trial Abuse → Unlimited Trials → Create 1000 Accounts → Scrape Data
3. [High]      Seat Abuse → Add Unlimited Members → Bypass Per-Seat Billing
4. [Critical]  Privilege Escalation → Free User → Admin → Export All Organizations' Data
5. [Medium]    API Key Escalation → Create Token with admin scopes → Persistent Backdoor
```

### Real H1 Examples
- Nextcloud: IDOR on files (#3382343, #153905)
- Nextcloud: Privilege escalation (#166581)
- GitHub: OAuth app token theft (#3522254)
- GitHub: Private repo access via PAT (#3506183)
- Stripo Inc: Cross-tenant access (CVSS 9.9, #3459285)
- SingleStore: Seat abuse (#3295500)
- Chaturbate: Billing manipulation (#394329)

---

