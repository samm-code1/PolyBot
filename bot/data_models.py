from enum import Enum
from dataclasses import dataclass

class StrategyType(Enum):
    NEGATIVE_RISK = "negative_risk"
    SPREAD_SNIPE = "spread_snipe"
    MAKER_REBATE = "maker_rebate"
    CTF_MERGE = "ctf_merge"

class OrderStatus(Enum):
    OPEN = "open"
    MATCHED = "matched"
    CANCELLED = "cancelled"
    SCORING = "scoring"

@dataclass
class WalletState:
    current_balance: float
    high_water_mark: float
    weekly_pnl: float
    is_halted: bool = False
