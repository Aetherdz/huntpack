## ASN DISCOVERY — وسّع سطح الهجوم

لما تلاقي IP تابع لـ ASN معين، تقدر تكتشف كل الدومينات المرتبطة بنفس infrastructure.

### asnmap (ProjectDiscovery)

```bash
# 1. من دومين → ASN
asnmap -d target.com -silent

# 2. من IP → CIDR
asnmap -i 1.2.3.4 -silent

# 3. من اسم الشركة → كل CIDR ranges
asnmap -org "Target Corp" -silent

# 4. من ASN → كل CIDR blocks
asnmap -a AS12345 -silent

# تثبيت
go install github.com/projectdiscovery/asnmap/cmd/asnmap@latest
```

### سير العمل الكامل

```bash
# الخطوة 1: IP → ASN → كل CIDR
IP=$(dig +short target.com | head -1)
ASN=$(whois -h whois.cymru.com $IP | tail -1 | awk '{print $1}')
CIDRS=$(asnmap -a $ASN -silent)

# الخطوة 2: CIDR → IPs → PTR records (دومينات إضافية)
echo "$CIDRS" | mapcidr -silent | dnsx -ptr -resp-only -silent | tee /tmp/ptr-names.txt

# الخطوة 3: تأكد إنها نفس الشركة
cat /tmp/ptr-names.txt | grep -i "target\|corp\|company"

# الخطوة 4: ضيفهم للـ scope
cat /tmp/ptr-names.txt | anew /tmp/scope-domains.txt
```
