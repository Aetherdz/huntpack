## 6. SUBSCRIPTION / MEMBERSHIP

### Signature Assets
- Subscription plans, billing
- Premium content, features
- Member profiles, payment methods
- Gift subscriptions, promo codes
- Usage analytics

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| Free User | Limited content | Trial abuse |
| Subscriber | Premium content | Downgrade access |
| Creator | Publish (Patreon/Substack) | Payout abuse |

### Priority Attack Surface

```
1. TRIAL ABUSE ← #1 SUBSCRIPTION BUG
   POST /api/subscriptions/trial           → race (unlimited trials)
   POST /api/subscriptions/trial/start    → repeat with same card
   POST /api/subscriptions/trial/convert  → skip payment
   Test: create trial → cancel → create trial → repeat

2. DOWNGRADE / FEATURE PERSISTENCE
   PUT  /api/subscriptions/{id}/plan       → downgrade but keep features
   GET  /api/content/premium               → access after downgrade
   Test: subscribe → download → cancel → check access still works

3. GIFT CODE / PROMO ABUSE
   POST /api/gifts/redeem                  → redeem same code multiple times
   POST /api/promos/apply                  → apply unlimited promos
   GET  /api/promos/{code}                 → enumerate valid promo codes
   Test: try to stack gift subscriptions

4. CANCELLATION BYPASS
   POST /api/subscriptions/{id}/cancel     → cancel but service continues
   POST /api/subscriptions/{id}/pause      → pause but content still accessible
   Test: check feature flags and content access after cancellation

5. BILLING MANIPULATION
   POST /api/billing/invoice               → modify invoice amount
   PUT  /api/billing/card                  → use stolen/expired card
   POST /api/billing/upgrade               → proration miscalculation
   Test: intercept billing flow, modify amounts
```

### Top Attack Chains
```
1. [High] Trial Abuse → Cancel → Retrial → Loop → Years of Free Premium
2. [High] Downgrade → Keep Premium → Download All Content → Cancel Account
3. [Medium] Gift Stack → 100 Gift Codes → 8+ Years Free → Share Account
4. [Medium] Cancel → Service Active → Continue Accessing → Never Pay
```

### Real H1 Examples
- Dropbox: Referral exploit (classic, unlimited free space)
- Chaturbate: Billing manipulation (#394329)
- Netflix/Spotify: Trial abuse (well-known pattern)

---

