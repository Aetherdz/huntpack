## 8. OAUTH / OIDC BUGS

### Missing PKCE (Coinbase pattern)
```
Test: GET /oauth2/auth?...&client_id=X (without code_challenge parameter)
Result: If 302 redirect (not error) = PKCE not enforced
Impact: Auth code interception → ATO
```

### State Parameter Bypass (CSRF on OAuth)
```
Start OAuth → don't authorize → capture URL → send to victim
Victim authorizes → their auth code tied to YOUR session → ATO
```

### Open Redirect Bypass Techniques (for OAuth chaining, 11 techniques)

| Technique | Example | Why it works |
|---|---|---|
| @ symbol | `https://legit.com@evil.com` | Browser navigates to evil.com |
| Subdomain abuse | `https://legit.com.evil.com` | evil.com controls subdomain |
| Protocol tricks | `javascript:alert(1)` | XSS via redirect |
| Double encoding | `%252f%252fevil.com` | Decodes to `//evil.com` |
| Backslash | `https://legit.com\@evil.com` | Parsers normalize `\` to `/` |
| Protocol-relative | `//evil.com` | Uses current page's protocol |
| Null byte | `https://legit.com%00.evil.com` | Some parsers truncate at null |
| Unicode IDN | `https://legіt.com` (Cyrillic і) | Visually identical, different domain |
| Data URL | `data:text/html,<script>...` | Direct payload |
| Fragment abuse | `https://legit.com#@evil.com` | Inconsistent parsing |
| Redirect + OAuth | `target.com/callback?redirect_uri=..` | Redirect endpoint |

### redirect_uri Validation Bypass (steal the code)
The whole flow's security rests on the AS matching `redirect_uri` exactly. Weak matching leaks the `code`/token to an attacker origin. Test each against the *registered* URI `https://app.com/cb`:
```
https://app.com/cb/../oob            # path traversal normalizes away the path
https://app.com/cb%2f@evil.com       # encoded slash + @ confusion
https://app.com.evil.com/cb          # suffix match if AS uses startsWith
https://app.com/cb?x=.evil.com       # AS checks prefix only
https://evil.com/cb                  # AS validates path not host (or subdomain wildcard)
https://app.com/cb#.evil.com         # fragment smuggling
```
Then chain with an **open redirect on the allow-listed host** (table above): `redirect_uri=https://app.com/openredirect?to=evil.com` — the AS trusts `app.com`, the app bounces the code out. Also test `response_mode=fragment` vs `query` and `response_type=token` (implicit) where the token lands in the URL.
- **Confirm:** you receive the victim's `code`/`access_token` on your host, then exchange it. A redirect that keeps the code on `app.com` is not exploitable.

### Auth Code Reuse / Replay
Codes must be single-use and short-lived. Test: complete a login, **capture the `code`, then replay** `POST /token` with it a second time. If a new `access_token` is issued twice → replay = ATO when combined with a code leak. Also try using an old/expired code and a code issued for a **different client_id**.
- **FP-kill:** a second exchange returning `invalid_grant` is correct behavior — not a bug.

### PKCE Downgrade
Beyond "missing PKCE": if the app *starts* with `code_challenge`, try **dropping `code_challenge` at /authorize** and **omitting `code_verifier` at /token**, or sending `code_challenge_method=plain` with `code_verifier == code_challenge`. If the token endpoint still issues a token, PKCE is bypassable → intercepted codes become usable.

### Account-Linking / sub-vs-email Confusion
Apps that link a social login to an existing account **by email** (not by immutable `sub`) let an attacker pre-register the victim's email, or use an IdP that lets them set an unverified `email` claim → login merges into the victim's account. Test: IdP where you control the `email` claim, or `email_verified:false` accepted as verified. High-value ATO.
- id_token `alg:none` / RS256→HS256 confusion on the OIDC ID token: see `reference/12-api-security.md` (same JWT attacks apply to the id_token).

