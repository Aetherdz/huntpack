## HTTP SMUGGLING CHECK — في مرحلة الـ Recon

ما تنتظر لبعدين. اكتشفه من البداية.

### سريع (ثلاثة طلبات)

```bash
# CL.TE
curl -ks "https://target.com/" -H "Transfer-Encoding: chunked" \
  -d "0\r\n\r\nG" -w "\n%{http_code}" 2>/dev/null \
  | grep -q "403\|502\|400" && echo "⚠️ Possibly vulnerable to CL.TE"

# TE.CL  
curl -ks "https://target.com/" -H "Transfer-Encoding: chunked" \
  -H "Content-Length: 4" -d "123" -w "\n%{http_code}" 2>/dev/null

# TE.TE (obfuscated)
curl -ks "https://target.com/" -H "Transfer-Encoding: xchunked" \
  -d "0\r\n\r\n" -w "\n%{http_code}" 2>/dev/null
```

### باستخدام Burp (أدق)

```
استخدم BCheck:
- اذهب إلى Extensions → BChecks
- شغّل "HTTP Request Smuggling" (موجود مع Burp Pro)
- شيل كل الـ تلقائيات اللي يفحصون smuggling
```

### متى يكون مفيد؟

- وراء reverse proxy (nginx, haproxy, AWS ALB, Cloudflare)
- في برامج CDN (Fastly, Akamai, CloudFront) كثير توجد ثغرات smuggling
- لو شفت `Transfer-Encoding` أو `Content-Length` مختلف بين request و response
