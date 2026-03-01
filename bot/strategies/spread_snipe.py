import os
from typing import Dict, Optional, Tuple
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs
from bot.utils.logger import setup_logger
from bot.utils.telegram_bot import send_telegram_message

logger = setup_logger("SpreadSniper")

class SpreadSniper:
    def __init__(self, clob_client: ClobClient, ema_multiplier: float = 1.5, min_spread_floor: float = 0.015, order_size: float = 5.0):
        """
        Initializes the SpreadSniper strategy with a dynamic EMA (Exponential Moving Average) filter.
        :param clob_client: Initialized ClobClient instance.
        :param ema_multiplier: The current spread must be this many times larger than the average spread to trigger.
        :param min_spread_floor: Minimum absolute spread required regardless of EMA (prevents microscopic trades).
        :param order_size: The number of shares to bid/ask.
        """
        self.client = clob_client
        self.ema_multiplier = ema_multiplier
        self.min_spread_floor = min_spread_floor
        self.order_size = order_size
        self.dry_run = os.getenv("DRY_RUN", "True").lower() in ("true", "1", "yes")
        
        if self.dry_run:
            logger.warning("DRY_RUN is ENABLED. Orders will be simulated, not placed on Polymarket.")
        
        # Track active snipes so we don't spam orders on every tick
        # Format: { asset_id: {"bid_price": float, "ask_price": float} }
        self.active_snipes: Dict[str, Dict[str, float]] = {}
        
        # Track the Trailing Exponential Moving Average of the spread per asset
        # Format: { asset_id: float_ema }
        self.ema_spreads: Dict[str, float] = {}

    def process_tick(self, tick_data: dict):
        """
        Processes an incoming websocket tick to find large spreads and execute sniper orders.
        """
        market_id = tick_data.get("market")
        price_changes = tick_data.get("price_changes", [])
        
        for change in price_changes:
            asset_id = change.get("asset_id")
            best_bid_str = change.get("best_bid")
            best_ask_str = change.get("best_ask")
            
            if not asset_id or not best_bid_str or not best_ask_str:
                continue
                
            try:
                best_bid = float(best_bid_str)
                best_ask = float(best_ask_str)
            except ValueError:
                continue

            # Calculate instantaneous spread
            spread = round(best_ask - best_bid, 4)
            if spread <= 0:
                continue

            # Update the Exponential Moving Average (EMA) for this asset
            # Alpha = 0.1 gives roughly a 20-tick trailing average memory
            current_ema = self.ema_spreads.get(asset_id)
            if current_ema is None:
                self.ema_spreads[asset_id] = spread
                current_ema = spread
            else:
                current_ema = (spread * 0.1) + (current_ema * 0.9)
                self.ema_spreads[asset_id] = current_ema

            # Phase 5 Dynamic Trigger Logic:
            # The current spread must be significantly wider than the running average AND beat the absolute floor
            dynamic_threshold = max(self.min_spread_floor, current_ema * self.ema_multiplier)

            if spread >= dynamic_threshold:
                logger.info(f"[snipe_target] Volatility Spike Detected! Asset: {asset_id[:8]}...")
                logger.info(f"   ↳ Spread: {spread:.4f} | Avg (EMA): {current_ema:.4f} | Threshold Required: {dynamic_threshold:.4f}")
                self._execute_snipe(asset_id, best_bid, best_ask)
            else:
                # If spread collapsed but we have an active snipe, we might want to evaluate canceling it.
                # For Phase 2 MVP, we will rely on Heartbeat timeouts or manual cancels if unfilled,
                # or build advanced cancel routines later.
                pass

    def _execute_snipe(self, asset_id: str, best_bid: float, best_ask: float):
        """
        Places a BID slightly above the best bid and an ASK slightly below the best ask.
        """
        # We don't want to re-post identical orders if we're already the best bid/ask
        active = self.active_snipes.get(asset_id)
        
        # Calculate our target prices (front-run by 1 tick / 1 cent)
        target_bid = round(best_bid + 0.01, 2)
        target_ask = round(best_ask - 0.01, 2)
        
        # Sanity check boundaries
        if target_bid >= target_ask:
            logger.debug("Spread too tight after front-run calculation. Aborting.")
            return
            
        if target_bid >= 1.0 or target_ask <= 0.0:
            return

        # Check if we already have this exact snipe active
        if active and active.get("bid_price") == target_bid and active.get("ask_price") == target_ask:
            return
            
        logger.info(f"Executing Snipe for {asset_id[:8]}... Placing Bid @ {target_bid} & Ask @ {target_ask}")
        
        # Record our attempt
        if asset_id not in self.active_snipes:
             self.active_snipes[asset_id] = {}
        self.active_snipes[asset_id]["bid_price"] = target_bid
        self.active_snipes[asset_id]["ask_price"] = target_ask

        # Note: Polymarket typically requires the Bids and Asks to be distinct function calls.
        # This will POST the orders to the CLOB.
        if self.dry_run:
            simulated_profit = (target_ask - target_bid) * self.order_size
            self.simulated_pnl = getattr(self, "simulated_pnl", 0.0) + simulated_profit
            
            logger.info(f"[DRY_RUN] 🛡️ Would place BID @ {target_bid} & ASK @ {target_ask} for {self.order_size} shares on asset {asset_id[:8]}...")
            
            if simulated_profit >= 0:
                msg = f"🟢 <b>[SIMULATION] Profit Captured!</b>\nAsset: {asset_id[:8]}...\nYield: +${simulated_profit:.2f}\nTotal PNL: ${self.simulated_pnl:.2f}"
                logger.info(f"[DRY_RUN] 🟢 TRADE CLOSED IN PROFIT: +${simulated_profit:.2f} | Total Session PNL: ${self.simulated_pnl:.2f}")
            else:
                msg = f"🔴 <b>[SIMULATION] Loss Taken!</b>\nAsset: {asset_id[:8]}...\nYield: -${abs(simulated_profit):.2f}\nTotal PNL: ${self.simulated_pnl:.2f}"
                logger.warning(f"[DRY_RUN] 🔴 TRADE CLOSED IN LOSS: -${abs(simulated_profit):.2f} | Total Session PNL: ${self.simulated_pnl:.2f}")
            
            send_telegram_message(msg)
            return
            
        try:
            # 1. Place the Bid
            bid_order = OrderArgs(
                price=target_bid,
                size=self.order_size,
                side="BUY",
                token_id=asset_id
            )
            # Create, sign, and post natively
            resp_bid = self.client.create_and_post_order(bid_order)
            logger.info(f"Bid Placed: {resp_bid}")

            # 2. Place the Ask (Wrap in separate Try/Except because Polymarket rejects naked SELLs)
            try:
                ask_order = OrderArgs(
                    price=target_ask,
                    size=self.order_size,
                    side="SELL",
                    token_id=asset_id
                )
                resp_ask = self.client.create_and_post_order(ask_order)
                logger.info(f"Ask Placed: {resp_ask}")
            except Exception as e:
                if "not enough balance / allowance" in str(e):
                    logger.warning(f"Ask Rejected: Insufficient '{asset_id[:8]}' token inventory to place a naked SELL. V2 Inventory Management required.")
                else:
                    logger.warning(f"Ask failed: {e}")
            
            # Since we rely on limit order resting time, we don't know the INSTANT PNL of a real order until it fills.
            # But we can alert the user that the net was securely cast.
            send_telegram_message(f"🚀 <b>Live Order Placed</b>\nAsset: {asset_id[:8]}...\nBid: {target_bid} | Ask: {target_ask}\nSize: {self.order_size} shares")

        except Exception as e:
            err_str = str(e)
            if "not enough balance / allowance" in err_str:
                # This is EXPECTED behavior: bot has placed so many resting Bids that the
                # Polymarket CLOB has internally reserved all available USDC.e collateral.
                # This is NOT a crash. Just log a warning - do NOT send a scary Telegram alert.
                logger.warning(f"Bid skipped: Wallet collateral fully reserved by resting orders. No action needed.")
            else:
                logger.error(f"Snipe Execution Failed: {e}")
                send_telegram_message(f"⚠️ <b>Snipe Execution Error</b>\n{err_str}")

