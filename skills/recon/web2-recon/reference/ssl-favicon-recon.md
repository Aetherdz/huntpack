## SSL + FAVICON RECON — تقنيات تمديدية

### tlsx (SSL/TLS Analysis)

يكشف دومينات إضافية من شهادات SSL.

```bash
# استخراج Subject Alternative Names (SAN)
echo "target.com" | tlsx -san -cn -silent | tee /tmp/san-domains.txt

# فحص SSL مع تفاصيل
tlsx -u target.com -expired -san -cn -ss -subject -issuer -silent

# تثبيت
go install github.com/projectdiscovery/tlsx/cmd/tlsx@latest
```

### Favicon Hash (لتوسيع البحث)

كل موقع غالباً له favicon فريد. تقدر تبحث عنه في Shodan أو ZoomEye وتلقى خوادم أخرى لنفس الشركة.

```bash
# حساب hash (استخدم python أو mmh3)
curl -s "https://target.com/favicon.ico" -o /tmp/fav.ico
python3 -c "
import mmh3, codecs
data = open('/tmp/fav.ico', 'rb').read()
hash = mmh3.hash(codecs.encode(data, 'base64'))
print(f'http.favicon.hash:{hash}')
"

# ابحث في Shodan
# https://www.shodan.io/search?query=http.favicon.hash:XXXXX

# أو curl
curl -s "https://internetdb.shodan.io/$(dig +short target.com | head -1)" | jq
```

### Historical IP (SecurityTrails)

```bash
# شوف IPs القديمة (قبل ما يحطونه وراء CDN)
curl -s "https://api.securitytrails.com/v1/history/target.com/dns/a" \
  -H "APIKEY: $SECURITYTRAILS_KEY" | jq -r '.records[] | .values[].ip' 2>/dev/null

# بدون API key — جرب Crt.sh
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sort -u
```
