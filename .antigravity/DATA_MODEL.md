---

### 2. `DATA_MODEL.md`
```markdown
# 🧠 DATA MODEL & STATE

## 1. Core State Management
The bot must track a continuous `WalletState` in memory to manage the $10 -> $1000 compounding loop.
- `current_balance`: USDC.e balance on Polygon.
- `high_water_mark`: Highest balance achieved (used for trailing stop-losses).
- `weekly_pnl`: Tracked to trigger the $1000 withdrawal milestone.

## 2. Standard Enums
Standardize all data flows using Python `Enum` classes.

```python
from enum import Enum

class StrategyType(Enum):
    NEGATIVE_RISK = "negative_risk" # Exploiting multi-outcome > 100% logic
    SPREAD_SNIPE = "spread_snipe"   # Front-running large spread differences
    MAKER_REBATE = "maker_rebate"   # Providing liquidity for polymarket rewards
    CTF_MERGE = "ctf_merge"         # Buying outcome tokens and merging to USDC

class OrderStatus(Enum):
    OPEN = "open"
    MATCHED = "matched"
    CANCELLED = "cancelled"
    SCORING = "scoring" # Eligible for maker rewards