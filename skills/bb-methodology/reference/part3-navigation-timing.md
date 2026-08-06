---
name: part3-navigation-timing
description: Quick unstuck-navigation table, rotation timing rules, and the phase-by-phase tool routing order (with the reasoning for each order).
---

# NAVIGATION & TIMING

## When stuck, go here
| Stuck because... | Go to |
|---|---|
| Can't find subdomains | Recon — try different sources, Google dorks |
| Found a subdomain, don't know what to test | Mapping — download JS, understand auth |
| Testing but nothing works | Discovery — switch vuln class (20-min rule) |
| Found a bug but impact is low | Escalation paths or gadget chaining |
| WAF/CSP/403 blocking the payload | Fingerprint the WAF → try encoded variants → kill after 5 min total if still blocked |
| Stuck 45+ min on one parameter | Stop. Rabbit hole. Move to the next endpoint. |
| New endpoint discovered mid-test | Return to Mapping — map it before attacking it |
| Found one bug | Hunt 20 min for sibling bugs — same developer, same mistake pattern |

## Rotation clock
Every 20 minutes, ask "am I making progress?" No → rotate: endpoint → subdomain → vuln class → target, in that order of increasing scope change. Stuck on the same target 2+ weeks with nothing? Consider switching programs.

## Tool routing — order matters, not just tool choice
| Task | Order | Why this order |
|---|---|---|
| Subdomains | `subfinder`/`amass -passive`/`assetfinder` + `crt.sh` (CT logs) + `github-subdomains` (org token, dork leaked hostnames) → merge+dedupe (`anew`) → `puredns` (resolve, public resolver list) → `httpx` (probe+tech+screenshot) | Passive/CT/GitHub sources surface assets DNS brute-force never finds (forgotten CT-logged hosts, hostnames leaked in repos); merge before resolving so nothing's tested twice; resolve before probing wastes no requests on dead hosts |
| New assets (cloud/decommissioned) | `httpx` output → check each host's CNAME against `subjack`/`nuclei -tags takeover` (dangling CNAME to GitHub Pages/Heroku/Azure/S3) → `s3scanner` on any bucket-shaped hostname | Decommissioned third-party services pointed to by a live CNAME are the highest-yield asset-class bug; check this on every new host, not just once |
| Continuous recon (re-run, not one-off) | Re-run the full subdomain pipeline weekly per active target → diff against last run's saved list → `httpx` only the new/changed hosts → alert on new CT log entries via `certstream`/`github-subdomains` on a cron | A target's attack surface grows between sessions (new deploys, new subdomains, new CT certs); recon is a standing process during an active engagement, not a one-time Phase-1 step |
| URLs | `gau`/`waymore` (archive) → `katana` (active crawl) → `uro` (dedupe) | Archive surfaces what active crawling can't see; dedupe last so nothing's lost mid-pipeline |
| JS | `jsluice` (extract) → `mantra` (find keys) → `trufflehog --only-verified` | No point flagging a key before confirming it's live |
| Ports | `naabu` (fast top-1000) → `rustscan` (full 65535 on interesting targets) | Full scan on everything wastes time; narrow first |
| Vuln scan | `nuclei -tags cve` → `nuclei -tags takeover` | CVEs are highest-confidence hits; takeover needs immediate action once found, so it's checked right after |
| Params | `arjun` + `paramspider` + ParamMiner, in parallel | Different discovery angles, no dependency order between them |
| XSS | `kxss` (filter reflective params) → `dalfox` (scan only those) | Scanning every param wastes time; only reflective ones matter |
| 403 bypass | fingerprint the block (`wafw00f`) → `byp4xx`/`nomore403` | Blind bypass attempts without fingerprinting waste the 5-minute budget |
| Cloud (S3 etc.) | `s3scanner` (permissions) → `aws` CLI (extract exposed metadata/creds) | Permission scan tells you if extraction is even possible first |
| Secrets | `trufflehog --only-verified` | Unverified secret hits are mostly noise — verification is what makes a finding real |

## Session end
Save proxy project state · record "weird but not yet exploitable" behavior as future gadget candidates · log failed attempts explicitly (so they aren't retested blindly next session) · log confirmed findings for recall.
