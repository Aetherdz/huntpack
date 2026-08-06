## Platform-Specific Submission Formats

### HackerOne
```yaml
# HackerOne report structure
title: "[Severity]: [Vuln Type] in [Endpoint]"
summary: |
  One paragraph: what, where, impact. No filler.
  "IDOR in GET /api/v1/orders/{id} allows any authenticated user
   to view any other user's order details (PII + payment method)."
vulnerability_type: "Business Logic Errors > IDOR"
severity: "High"  # Auto-calculated from CVSS
scope: "https://target.com"
reproduction_steps: |
  1. Create account A and B
  2. Get JWT for each
  3. Request /api/v1/orders/5 with token B
  4. Response contains order 5 belonging to user A
impact: |
  - Unauthorized access to all orders (PII + payment info)
  - Violates GDPR data protection
  - Estimated 50K+ orders exposed
attachments:
  - proof.png (screenshot of response)
  - poc.py (Python exploit script)
```

### Bugcrowd
```markdown
# Bugcrowd requires:
# - Vulnerability Type (dropdown)
# - Target URL
# - Description (summary + impact)
# - Steps To Reproduce
# - Supporting Material (files/images)
# - Remediation Suggestion
# - CVSS Vector (auto-calculated from sliders)

**Important Bugcrowd rules:**
- Do NOT include hyperlinks in the report body (plain text only)
- Maximum 5 attachments per submission
- CVSS uses Bugcrowd's own calculator (match External sliders)
- "Vulnerability Discovered Date" must be within the program window
```

### Intigriti
```markdown
# Intigriti report structure:
# 1. Title
# 2. Summary (max 300 chars)
# 3. Steps to Reproduce (numbered, detailed)
# 4. Proof of Concept (curl, screenshots, video)
# 5. Impact (business, not technical)
# 6. Remediation
# 7. CVSS 3.1 Vector
# 8. Affected Users / Data Volume

**Intigriti tips:**
- Videos preferred over screenshots for complex chains
- CVSS Environmental metrics allowed (adjust for your scenario)
- Supports CVSS 4.0 — include the 4.0 vector with justified Threat/Environmental metrics (see `cvss-4-0.md`)
```

### Immunefi (Crypto/DeFi)
```markdown
# Immunefi report structure:
# 1. Smart Contract / Target
# 2. Vulnerability Class
# 3. Summary
# 4. Vulnerability Details (with code snippets)
# 5. Proof of Concept (forge test script preferred)
# 6. Impact (TVL at risk, funds at risk, user impact)
# 7. Severity (Critical/High/Medium/Low per Immunefi scale)
# 8. Recommended Fix (code diff)

**Immunefi rules:**
- Submit PoC as Forge test, not just curl
- TVL calculation must be included for Critical/High
- No public disclosure until 90 days post-fix
- Chain/combination findings get bonus multipliers
```

### Private Program (Email)
```markdown
Subject: [Critical] Security Vulnerability in [Product] - [Vuln Type]

Hi security team,

I identified [vulnerability] in [endpoint/feature].
Impact: [one-line business impact].
Attached: full report with PoC, reproduction steps, and CVSS.

Best,
[Name]
```

## Platform Reality — what actually gets rejected (aim before you fire)

| Platform | Severity philosophy | Auto-N/A / low-value here | Dup risk |
|----------|--------------------|---------------------------|----------|
| **HackerOne** | CVSS-driven, but triager can down/upgrade on real impact | self-XSS, missing headers, no-rate-limit alone, CSRF on non-state-changing, best-practice reports | **High** on popular public programs — check Hacktivity + report fast |
| **Bugcrowd** | Own **VRT** taxonomy (not pure CVSS) — look your bug up in the VRT first | anything marked "Won't Fix"/P5 in VRT, descriptive/informational, missing SPF/DMARC | Med–High; VRT priority sets the payout, argue VRT not CVSS |
| **Intigriti** | CVSS + business context; researcher-friendly triage | out-of-scope assets, theoretical impact, low-severity infoleak | Medium; smaller programs = fewer dups |
| **Immunefi** | Impact-in-funds only (TVL/funds at risk); PoC-or-it-didn't-happen | anything without a runnable PoC, gas-griefing, centralization "risks", best-practice | Low on code, but **must** prove fund impact |
| **Private/VDP** | Varies; often no bounty (VDP = recognition) | confirm bounty exists before deep work; VDP = report only high-impact | Low |

**Before submitting, match the bug to the platform:**
- Bugcrowd → find the exact **VRT** entry; it decides priority more than your CVSS.
- HackerOne → search **Hacktivity** for the same bug/endpoint to pre-empt "duplicate."
- Immunefi → no **funds-at-risk PoC** = don't submit; quantify TVL for Critical/High.
- Any → run the finding through `false-positive-killer` + the always-rejected list first; N/A ratio is your reputation.

> After you submit, drive triager responses with `post-submission-playbook.md`.

