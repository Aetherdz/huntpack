## 4. BANKING / FINTECH

### Signature Assets
- Account balances, transactions
- Cards, payment methods
- KYC documents, identity verification
- Webhooks, API integrations
- Transaction history, statements
- Notifications, alerts

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| Customer | Send/receive, view | Transaction IDOR |
| Business | API keys, webhooks | Webhook replay |
| Admin | Review suspicious | KYC bypass |
| Compliance | KYC/AML review | Document forgery |

### Priority Attack Surface

```
1. TRANSACTION IDOR ← CRITICAL, ALWAYS PAYS
   GET  /api/transactions/{id}          → sequential transaction IDs
   GET  /api/accounts/{id}/transactions → access others' statement
   GET  /api/cards/{id}/transactions    → access others' card history
   Test: create transaction with User A, access with User B

2. WEBHOOK REPLAY / DOUBLE PROCESSING
   POST /webhooks/stripe                → replay same webhook event
   POST /webhooks/paypal                → send duplicate IPN
   Test: capture webhook request, replay 5-10 times

3. KYC / IDENTITY BYPASS
   POST /api/kyc/upload                 → upload fake document
   POST /api/kyc/verify                 → skip verification step
   PUT  /api/kyc/status                 → mass assign verified=true
   Test: intercept KYC flow, check for step skipping

4. BALANCE / WALLET MANIPULATION
   POST /api/wallet/transfer            → negative amount
   POST /api/wallet/deposit             → race condition
   POST /api/wallet/withdraw            → negative balance
   Test: concurrent withdraw requests, negative amounts

5. OTP / MFA BYPASS
   POST /api/auth/verify-otp            → OTP reuse
   POST /api/auth/resend-otp            → multiple valid OTPs
   POST /api/auth/verify-2fa            → skip 2FA
   Test: race OTP verification, check if OTP expires after use
```

### Top Attack Chains
```
1. [Critical] Webhook Replay → Send 50 Duplicate Refund Webhooks → Extract 50x Refund
2. [Critical] Transaction IDOR → Read All Customer Transactions → Sell Financial Data
3. [High]      OTP Race → 100 Concurrent OTP Verifications → One Works → ATO
4. [High]      KYC Bypass → Create Anonymous Account → Launder Money
5. [Critical]  Balance Race → Deposit $100 → Send 50 Concurrent Withdrawals → $5000 Extracted
```

### Real H1 Examples
- PayPal: Transaction IDOR (#415081, $10,000)
- Monero: Wallet balance manipulation (#377592)
- Coinbase: Double spend (#106315)

---

