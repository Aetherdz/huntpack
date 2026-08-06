## POST-SUBMISSION PLAYBOOK — turn triager replies into action

The report isn't done at submit. Most lost bounties are recoverable if you read the triager's
reply as a **signal about what your report was missing** and respond with evidence, not argument.

### Triager reply → what it really means → your move

| Triager says | Real meaning | Your move |
|---|---|---|
| "Cannot reproduce" | Your PoC has an env dependency (session, region, rate-limit, timing, a header you set in Burp but omitted from the writeup) | Re-test from a **clean machine/incognito**, then reply with an **exact `curl`** (every header), a fresh account pair, and a screen recording with the clock visible. State prerequisites explicitly. |
| "Duplicate" | Same root cause already known — or a *different* bug they pattern-matched | Politely ask for the dup ID/date. If your **root cause or impact differs** (different endpoint, higher impact, bypasses their fix), show that delta — partial-dup or bonus is possible. If truly earlier, accept and move on. |
| "Informational / N/A" | No demonstrated impact, or it's on the always-rejected list | Add the **missing impact proof** (actual data pulled, actual money moved, actual admin action) or a **chain** that reaches real impact. If it's genuinely self-XSS / missing-header-only, don't argue — withdraw and save reputation. |
| "Out of scope" | Asset/finding outside the policy | Re-read scope; if you *were* in scope, quote the exact policy line. If not, concede immediately (arguing scope burns signal). |
| "Need more info" | They're interested but blocked | Answer fast and completely — momentum matters; a same-day, complete reply often converts. |
| Rated lower than you expect (e.g. Medium, you think High) | They scored a narrower impact than you demonstrated | **Severity negotiation**, evidence-first: show the concrete higher impact (CVSS 4.0 vector with justified Modified metrics — see `cvss-4-0.md`), the data at risk, or the chain. Never argue severity with adjectives. |
| Silence / stale (SLA passed) | Backlog, not rejection | One polite nudge after the platform's stated SLA. Escalate via the platform's mediation only after that, never publicly. |

### Appeal / re-open (N/A → paid) — worth it when:
- You can attach **new evidence** that answers the exact rejection reason (not a restatement).
- The impact was under-demonstrated and you can now **show** it, not assert it.
- A fix was deployed — verify it, and if it's **bypassable**, that's often a fresh, higher-value report.

### Tone rules (protect your signal/reputation)
- Evidence over debate. Every reply adds a request/response, a recording, or a number.
- Never threaten public disclosure or go public mid-triage — it forfeits the bounty and the account standing.
- Concede cleanly when you're wrong; a hunter who withdraws bad reports gets faster triage on good ones.
- Keep each finding in its own thread; don't bundle unrelated bugs into one report.

> Feeds back into hunting: a "cannot reproduce" almost always means your **evidence pipeline**
> was weak — tighten it next time (`.quality-gates.md` → Evidence + Reproducibility Gates).
