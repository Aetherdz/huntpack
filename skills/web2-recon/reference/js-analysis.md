## JS ANALYSIS

> **⚙️ Tool note:** `tools/SecretFinder/SecretFinder.py` and `tools/LinkFinder/linkfinder.py` are optional local clones. If absent, use standard equivalents:
> ```bash
> # endpoints/links from JS (LinkFinder equivalent)
> katana -u https://target -jc -d 3 | anew urls.txt        # or: cat app.js | jsluice urls
> # secrets/keys in JS (SecretFinder equivalent)
> cat app.js | jsluice secrets                             # or: trufflehog filesystem app.js
> # quick grep fallback
> grep -oE '(api[_-]?key|secret|token|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35})[^"'\'' ]*' app.js
> ```

### SecretFinder (API keys, tokens in JS bundles)

```bash
# Activate venv
source ~/tools/SecretFinder/.venv/bin/activate

# Scan a single JS file
python3 ~/tools/SecretFinder/SecretFinder.py -i "https://target.com/static/js/main.js" -o cli

# Scan all JS URLs found in recon
cat /tmp/urls.txt | grep "\.js$" | head -50 | while read url; do
  echo "=== $url ==="
  python3 ~/tools/SecretFinder/SecretFinder.py -i "$url" -o cli 2>/dev/null
done

deactivate
```

### LinkFinder (Endpoints hidden in JS)

```bash
source ~/tools/LinkFinder/.venv/bin/activate

# Single JS file
python3 ~/tools/LinkFinder/linkfinder.py -i "https://target.com/app.js" -o cli

# All pages (crawls JS from HTML)
python3 ~/tools/LinkFinder/linkfinder.py -i "https://target.com" -d -o cli

deactivate
```
