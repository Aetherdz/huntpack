## CDN/WAF DETECTION — قبل ما تبدأ الاختبار

معرفة إذا الموقع وراء CDN أو WAF يغير طريقة هجومك بشكل كامل.

### cdncheck (أداة ProjectDiscovery)

```bash
# فحص دومين واحد
cdncheck -d target.com

#批量 من قائمة
cat /tmp/live.txt | cdncheck -resp | tee /tmp/cdn-check.txt

# عرض التفاصيل كاملة
cat /tmp/live.txt | cdncheck -resp -v

# تثبيت
go install github.com/projectdiscovery/cdncheck/cmd/cdncheck@latest
```

### يدوي — من الرؤوس

```bash
# Cloudflare
curl -sI https://target.com | grep -i "cf-ray\|server: cloudflare\|cf-cache-status"

# Akamai
curl -sI https://target.com | grep -i "x-akamai\|x-akamai-transformed"

# CloudFront
curl -sI https://target.com | grep -i "x-amz-cf-id\|x-amz-cf-pop"

# Fastly
curl -sI https://target.com | grep -i "x-fastly\|x-served-by"
```

### كشف الـ Origin IP (أهم خطوة)

إذا الموقع وراء CDN، لازم تلاقي IP الأصلي:

```bash
# 1. شوف تاريخ الـ DNS
curl -s "https://api.securitytrails.com/v1/history/target.com/dns/a" \
  -H "APIKEY: $SECURITYTRAILS_KEY" | jq '.records[].values[].ip' 2>/dev/null

# 2. شوف الـ subdomains اللي تشير IP مشهور
host -t a admin.target.com
host -t a mail.target.com
host -t a ftp.target.com
host -t a direct.target.com
host -t a origin.target.com

# 3. CERT Transparency — شوف السيرتيفيكيت القديم (فيه IP حقيقي)
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u

# 4. Shodan — ابحث بـ IP من تاريخ DNS
shodan search "ssl.cert.subject.cn:target.com" 2>/dev/null || \
curl -s "https://internetdb.shodan.io/$(host target.com | awk '/has address/ {print $4}')"

# 5. Favicon hash — لو الموقع له favicon ثابت
curl -s "https://target.com/favicon.ico" | python3 -c "
import mmh3, requests, sys, codecs
data = sys.stdin.buffer.read()
hash = mmh3.hash(codecs.encode(data, 'base64'))
print(f'favicon hash: {hash}')
# بعدها ابحث في Shodan: https://www.shodan.io/search?query=http.favicon.hash:HASH
"
```

### WAF Fingerprinting

```bash
# wafw00f
wafw00f https://target.com -a  # -a = جميع الاختبارات

# يدوي من الاستجابة
curl -s -o /dev/null -w "%{http_code}" -X POST https://target.com/login \
  -d "user=<script>alert(1)</script>"  # لو 403/406/999 → WAF موجود
```

### إشارات القتل السريع

| الإشارة | ماذا يعني |
|---------|-----------|
| `cf-ray` في الرد | Cloudflare |
| `x-amz-cf-id` | CloudFront |
| `x-akamai-transformed` | Akamai |
| `server: cloudflare` | Cloudflare |
| كل الطلبات عائدة 403 مع HTML | WAF يمنع |
| الـ SSL issuer = Google Trust | GCP/CDN |
