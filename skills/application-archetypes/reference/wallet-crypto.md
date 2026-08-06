## 5. WALLET / CRYPTO

### Signature Assets
- Cryptocurrency balances (BTC, ETH, SOL, etc.)
- Private keys, seed phrases
- Transaction history
- Smart contract interactions
- Withdrawal addresses
- Bridge/swap quotes

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| User | Send/receive, view | Withdraw race |
| Verified User | Higher limits | KYC bypass |
| Admin | Freeze, review | Balance manipulation |

### Priority Attack Surface

```
1. RACE CONDITION ON WITHDRAW ← MOST CRITICAL
   POST /api/wallet/withdraw            → 50 concurrent withdraws
   POST /api/wallet/transfer            → race transfer same funds twice
   Test: Burp Intruder, 50+ parallel threads, same nonce

2. REFERRAL BONUS ABUSE
   POST /api/referrals/claim            → create 1000 accounts, claim bonus
   POST /api/referrals/verify           → skip verification
   Test: automation with temp wallets/emails

3. SWAP QUOTE MANIPULATION
   GET  /api/swap/quote?from=ETH&to=USDC&amount=100 → manipulate quote
   POST /api/swap/execute               → execute stale quote
   Test: capture quote, delay execution, check price change

4. SIGNATURE REPLAY
   Capture valid signed transaction     → replay on different chain
   Capture valid signed message         → reuse for different action
   Test: same signature, different chain_id/nonce

5. BALANCE MANIPULATION
   GET  /api/wallet/balance             → manipulate response
   POST /api/wallet/deposit             → fake deposit confirmation
   Test: intercept API response, modify balance field
```

### Top Attack Chains
```
1. [Critical] Withdraw Race → 100 Concurrent Withdrawals → Empty Wallet → Sell ETH
2. [Critical] Signature Replay → Capture Swap → Replay on Polygon/Arbitrum → Double Swap
3. [High]      Referral Bonus → 10,000 Virtual Accounts → Collect All Bonuses → Real Value
4. [Critical]  Oracle Manipulation → Manipulate Swap Price → Buy Cheap → Sell Real
5. [Medium]    Quote Stale → Capture Low Price → Execute When Market Moves → Arbitrage
```

### Real H1 Examples
- Monero: Balance manipulation (#501585)
- MetaMask: Signature replay across chains (#3507241)

---

