---

### 3. `ROADMAP.md`
```markdown
# 🗺 ROADMAP & STRATEGY PHASES

## 🔹 Phase 1: MVP (The $10 Setup)
- [ ] Connect `py_clob_client` with L1 (Wallet) and L2 (API keys) credentials.
- [ ] Implement `python-dotenv` for secure private key management.
- [ ] Establish WebSocket connection to `Market Channel` for a specific high-volume market.
- [ ] Write basic execution functions: `post_new_order`, `cancel_single_order`.
- [ ] Implement Risk Module: Hard stop-loss at $8.00 (protecting the initial $10).

## 🔹 Phase 2: Arbitrage Logic (The "Edgy" Stuff)
- [ ] **Strategy A (Spread Sniping):** Detect markets with massive spreads. Place a bid slightly above the best bid, and an ask slightly below best ask.
- [ ] **Strategy B (Negative Risk Arb):** Monitor multi-outcome markets. If the combined price of all exhaustive outcomes drops below $0.98, buy all outcomes, use the `Merge Tokens` CTF contract to convert back to $1.00 instantly.
- [ ] **Heartbeat System:** Implement the ping system to prevent stranded orders.

## 🔹 Phase 3: Scaling & Auto-Banking (The $1000 Loop)
- [ ] Implement state tracker for the $1000/week goal.
- [ ] Build the `Safety Net` module: Once balance hits $1000, use Polymarket `Withdraw` bridge API to send $900 USDC.e to a cold wallet.
- [ ] Restart bot state with the remaining $100.
- [ ] Implement Trailing Stop-Losses (e.g., if balance reaches $500, new stop loss is $450).