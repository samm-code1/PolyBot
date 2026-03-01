import os
from bot.data_models import WalletState
from bot.utils.logger import setup_logger
from bot.api.bridge import execute_profit_sweep

logger = setup_logger("RiskManager")

MIN_BALANCE = 5.00  # Hard stop-loss floor
TRAILING_DISTANCE = 50.00 # The distance the stop-loss trails behind the peak
MILESTONE_TARGET = 1000.00
SWEEP_AMOUNT = 900.00

class RiskManager:
    def __init__(self, initial_balance: float, client=None):
        self.state = WalletState(
            current_balance=initial_balance,
            high_water_mark=initial_balance,
            weekly_pnl=0.0,
            is_halted=False
        )
        self.client = client
        self.cold_wallet = os.getenv("COLD_WALLET_ADDRESS", "")

    def update_balance(self, new_balance: float):
        if self.state.is_halted:
            return
            
        self.state.current_balance = new_balance
        
        # Check for Auto-Banking Milestone ($1000)
        if new_balance >= MILESTONE_TARGET:
            self._execute_safety_net()
            return
            
        # Update High Water Mark for Trailing Stop
        if new_balance > self.state.high_water_mark:
            self.state.high_water_mark = new_balance
            logger.debug(f"New High Water Mark: ${self.state.high_water_mark:.2f}")
            
        self._check_stop_loss()

    def _check_stop_loss(self):
        # Calculate trailing stop loss
        trailing_stop = max(MIN_BALANCE, self.state.high_water_mark - TRAILING_DISTANCE)
        
        if self.state.current_balance <= trailing_stop:
            self.state.is_halted = True
            logger.error(f"TRAILING STOP-LOSS TRIGGERED! Balance: ${self.state.current_balance:.2f} hit the ${trailing_stop:.2f} stop boundary.")

    def _execute_safety_net(self):
        logger.info(f"*** $1000 MILESTONE REACHED! Balance: ${self.state.current_balance:.2f} ***")
        logger.info("Halting trading and executing Profit Sweep...")
        self.state.is_halted = True
        
        # Execute proxy withdraw
        success = execute_profit_sweep(self.client, SWEEP_AMOUNT, self.cold_wallet)
        
        if success:
            logger.info("Sweep successful. Resetting state with remaining $100.00 collateral.")
            # Reset bot state to continue with the remaining $100
            self.state.current_balance -= SWEEP_AMOUNT
            self.state.high_water_mark = self.state.current_balance
            self.state.is_halted = False
        else:
            logger.critical("Sweep failed. Bot remains halted for manual intervention.")
            
    def can_trade(self) -> bool:
        return not self.state.is_halted
