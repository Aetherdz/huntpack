# Security Disclosure

HuntPack is a bug-bounty *methodology* library. If you find a vulnerability **in this repository itself** — a leaked secret, a malicious payload, an injection in the skill content — please report it privately first.

## How to report

Do **not** open a public issue. Email the maintainer directly or open a private security advisory on GitHub:

1. GitHub → **Security** tab → **Report a vulnerability** → **Private vulnerability reporting**.

## What triggers an advisory

- A real secret (API key, token, private key) committed to the repo.
- A prompt-injection or malicious-instruction payload embedded in a `SKILL.md` or `scripts/`.
- A skill that would cause damage outside authorized testing.

## Scope / non-reports

Reported *vulnerability classes* and *payloads* described inside the skills are **intentional**, educational, security-research content — they are not vulnerabilities in this repo.

By design:

- No skill performs live credential brute-forcing or DoS.
- Use of these skills is **authorized-testing-only**; check scope first.