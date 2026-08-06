## CVSS 3.1 Quick Reference

### Base Score Formula

```
Score = round_to_1_decimal(
  if Impact ≤ 0: 0
  else if Scope_Changed: min(Impact + Exploitability, 10) × 1.08
  else: min(Impact + Exploitability, 10)
)
```

### Metrics Table

| Metric | Value | Score |
|--------|-------|-------|
| **AV** (Attack Vector) | N=0.85, A=0.62, L=0.55, P=0.2 |
| **AC** (Complexity) | L=0.77, H=0.44 |
| **PR** (Privileges) | N=0.85, L=0.62(0.68), H=0.27(0.50) |
| **UI** (User Interaction) | N=0.85, R=0.62 |
| **S** (Scope) | U=unchanged, C=changed |
| **C/I/A** | H=0.56, L=0.22, N=0 |

### Common Vectors

| Vulnerability | CVSS Vector | Score |
|---------------|-------------|-------|
| IDOR (user data) | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N | 6.5 (Medium) |
| IDOR (admin data) | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 7.5 (High) |
| IDOR (tenant-wide) | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N | 8.5 (High) |
| SSRF (internal) | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N | 7.7 (High) |
| SSRF (metadata) | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N | 8.6 (High) |
| ATO via IDOR chain | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H | 10.0 (Critical) |
| SQLi (auth bypass) | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H | 10.0 (Critical) |
| Race Condition (payment) | AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N | 6.3 (Medium) |
| Business Logic (bypass) | AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N | 7.7 (High) |
| XSS (stored) | AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N | 5.4 (Medium) |

---

