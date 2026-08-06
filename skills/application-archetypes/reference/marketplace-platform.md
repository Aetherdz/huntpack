## 3. MARKETPLACE / PLATFORM

### Signature Assets
- Transactions, fees, escrow
- Buyers, sellers, drivers, riders
- Ratings, reviews, reputation scores
- Listings, services, availability
- Orders, bookings, trips
- Payment methods, payouts

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| Buyer/Rider | Browse, purchase, rate | Fee manipulation |
| Seller/Driver | List, fulfill, earn | Payout tampering |
| Admin | Dispute resolution, refunds | Escrow release |

### Priority Attack Surface

```
1. REFERRAL ABUSE ← MOST HUNTED
   POST /api/referrals/code         → generate referral code
   POST /api/referrals/claim        → claim with temp email
   POST /api/referrals/redeem       → race condition (redeem same code N times)
   Test: self-referral, race condition on bonus, temp emails

2. ESCROW / PAYOUT MANIPULATION ← HIGH IMPACT
   POST /api/orders/{id}/complete   → mark complete before delivery
   POST /api/orders/{id}/dispute    → reject valid order
   GET  /api/payouts/{id}           → IDOR on seller payouts
   PUT  /api/payouts/{id}/bank      → redirect payout to own account
   Test: intercept escrow release, manipulate payout destination

3. RATING/REVIEW FRAUD
   POST /api/listings/{id}/review   → review without purchase
   PUT  /api/reviews/{id}           → edit others' reviews
   POST /api/reviews/{id}/like      → mass like/dislike own review
   Test: check authorization on review submission

4. PRICING MANIPULATION
   POST /api/bookings               → modify price in booking request
   PUT  /api/listings/{id}/price    → change price after booking
   POST /api/services/quote         → manipulate fee calculation
   Test: intercept booking, modify price/fee fields

5. ACCOUNT TAKEOVER VIA MARKETPLACE ROLE
   POST /api/auth/reset-password    → reset seller password
   POST /api/auth/email/change      → hijack high-reputation account
   Test: check if seller account can be taken over → scam buyers
```

### Top Attack Chains
```
1. [Critical] Referral Race → Create 1000 Fake Users → Claim All Referral Bonuses → Cash Out
2. [Critical] Escrow Bypass → Mark Delivered Without Shipping → Receive Payment → Withdraw
3. [High]      Payout IDOR → Read All Sellers' Earnings → Extract Banking Details
4. [High]      ATO Top Seller → Take Over High-Rep Account → Scam All Active Buyers
5. [Medium]    Fake Reviews → 500 Five-Star Reviews → Unfair Advantage → Drive Real Sales
```

### Real H1 Examples
- Uber: Driver mass assignment (#99424)
- Uber: Driver IDOR (#194594) 
- Uber: Account takeover (#136885)

---

