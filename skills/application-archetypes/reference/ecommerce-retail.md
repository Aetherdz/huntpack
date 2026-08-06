## 1. E-COMMERCE / RETAIL

### Signature Assets
- Product catalog, prices, inventory
- Coupons, discount codes, gift cards
- Orders, shipments, returns
- Customer profiles, addresses, payment methods
- Reviews, ratings, wishlists
- Vendor/seller dashboards

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| Guest | Browse | No auth needed |
| Customer | Purchase, review | IDOR on orders |
| Seller | List products | Price manipulation |
| Admin | Refunds, moderation | Privilege escalation |

### Priority Attack Surface (Test In Order)

```
1. COUPON/DISCOUNT ENDPOINTS ← PAYS MOST
   POST /api/coupons/redeem          → race condition (apply same coupon N times)
   POST /api/coupons/apply           → stacking (apply unlimited coupons)
   POST /api/gift-cards/redeem       → balance manipulation
   GET  /api/coupons/{code}          → coupon enumeration
   PUT  /api/cart/{id}/coupon        → modify coupon after apply
   Test: quantity=-1, price=0, coupon=STACK_MULTIPLE

2. ORDER IDOR ← HIGH PAYOUT, EASY
   GET  /api/orders/{id}             → change id (123→124)
   GET  /api/orders/{id}/items       → view others' purchases
   POST /api/orders/{id}/cancel      → cancel others' orders
   POST /api/orders/{id}/refund      → refund others' orders
   Test: compare two accounts (User A order, User B access)

3. CHECKOUT RACE CONDITION
   POST /api/checkout                → send 50 identical requests
   POST /api/orders                  → race add/remove items
   PUT  /api/cart                    → modify cart after payment
   Test: Burp Intruder, 50 parallel threads

4. PRICE MANIPULATION
   POST /api/cart/add?product=X&price=0      → set your own price
   POST /api/cart/add?product=X&quantity=-1   → negative quantity (credit instead of charge)
   PUT  /api/cart/item/{id}?price=1          → modify price in cart
   POST /api/checkout?currency=X             → currency conversion abuse
   Test: intercept cart add, modify price field

5. REVIEW/RATING IDOR
   DELETE /api/reviews/{id}          → delete others' reviews
   PUT    /api/reviews/{id}          → edit others' reviews
   POST   /api/products/{id}/rate    → rate without purchase
   Test: check authorization on review CRUD

6. SHIPPING ABUSE
   POST /api/orders/{id}/address     → modify shipping after order
   POST /api/orders/{id}/cancel      → cancel after shipped
   POST /api/shipping/estimate       → manipulate zip code for pricing
```

### Top Attack Chains
```
1. [Critical] Coupon Race → Apply Same Coupon 100x → 100% Discount → Free Items → Resell
2. [High]      IDOR on Orders → Read All Orders → Extract PII (addresses, emails, phone)
3. [High]      Negative Quantity → Add item with qty=-50 → Credit on Account → Buy Real Items
4. [Medium]    Review IDOR → Delete Competitor Reviews → Manipulate Product Rating
5. [Low→High]  Coupon Enumeration → Find Valid 90%-off Codes → Stack With Other Coupons
```

### Real H1 Examples
- Instacart: IDOR on batch deliveries (#157996)
- Instacart: Dropping Earning from batch (#3426839)  
- Shopify: Race condition in cart (#413759)
- Shopify: IDOR on order transactions (#243943)
- Zomato: IDOR on order details (#269937)
- WooCommerce: Price manipulation (qty=-1) — common pattern

---

