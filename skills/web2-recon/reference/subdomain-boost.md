## SUBDOMAIN BOOST — اكتشاف اللي فاتك

بعد تشغيل subfinder/assetfinder، استخدم هذي التقنيات لزيادة عدد الـ subdomains.

### Alterx (توليد permutations)

```bash
# توليد احتمالات من subdomains موجودة
cat /tmp/subs.txt | alterx -silent | tee /tmp/permuted.txt

# دمج مع القائمة الأصلية وحل DNS
cat /tmp/subs.txt /tmp/permuted.txt | sort -u | dnsx -silent | tee /tmp/all-subs.txt

# تثبيت
go install github.com/projectdiscovery/alterx/cmd/alterx@latest
```

### Puredns (تصفية Wildcard DNS)

```bash
# لو الموقع يستخدم wildcard (*.target.com كلشي يresolve)
# puredns يصفيهم ويكشف الحقيقي
puredns resolve /tmp/all-subs.txt -r ~/wordlists/resolvers.txt -w /tmp/real-subs.txt

# تثبيت
go install github.com/d3mondev/puredns/v2@latest
```

### شو نضيف؟

| الأداة | الاستخدام |
|--------|-----------|
| `alterx` | توليد احتمالات (api-dev.target.com من dev.target.com) |
| `puredns` | حل DNS مع مقاومة wildcard |
| `dnsx -wd` | تصفية wildcard DNS |
| `tlsx` | استخراج SAN من الشهادات (دومينات إضافية) |

### سير كامل

```bash
# 1. Subdomains أساسية
subfinder -d target.com -silent > /tmp/base.txt

# 2. Permutations
cat /tmp/base.txt | alterx -silent > /tmp/perm.txt

# 3. DNS resolution مع تصفية wildcard
cat /tmp/base.txt /tmp/perm.txt | sort -u | puredns resolve -w /tmp/verified.txt

# 4. SAN من الشهادات (تغفل عنها كل الأدوات)
echo "target.com" | tlsx -san -cn -silent | anew /tmp/from-certs.txt

# 5. ادمج الكل
cat /tmp/verified.txt /tmp/from-certs.txt | sort -u > /tmp/final-subs.txt
```
