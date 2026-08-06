## 5. BUSINESS LOGIC
> Transferred from web3's "incomplete code path" pattern.

### Pattern 1: Fast Path Skips State Update
```python
def redeem_coupon(coupon_code, user_id):
    coupon = get_coupon(coupon_code)
    if coupon.balance >= amount:
        transfer(user_id, amount)
        return  # MISSING: never marks coupon as used!
    coupon.mark_used()
    transfer(user_id, amount)
```

### Pattern 2: Workflow Step Skip
```
Normal: select plan → add payment → confirm → activate
Attack: skip to /confirm?plan=premium&skip_payment=true
```

### Pattern 3: Negative / Zero Bypass
```
POST /api/transfer {"amount": -100}  → credits attacker, debits victim
POST /api/cart {"quantity": 0}       → adds item free
POST /api/refund {"amount": 99999}   → refunds more than purchased
```

### Pattern 4: Race Condition (TOCTOU)
```
Thread 1: checks balance (10 credits) → PASS
Thread 2: checks balance (10 credits) → PASS
Thread 1: deducts → 0 remaining
Thread 2: deducts → -10 remaining (DOUBLE SPEND)
```

