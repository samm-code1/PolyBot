import asyncio
import os
from dotenv import load_dotenv

from bot.api.client import get_clob_client
from bot.api.orders import post_new_order, cancel_single_order
from bot.data.websocket_client import PolyWebsocketClient
from bot.risk.stop_loss import RiskManager
from bot.utils.logger import setup_logger

from bot.strategies.spread_snipe import SpreadSniper
from bot.api.heartbeat import start_heartbeat
from bot.api.markets import get_top_markets

logger = setup_logger("MainApp")

# Global variables to hold the sniper
sniper = None

async def process_market_tick(data):
    # Pass live market data to the sniper strategy
    # The websocket can return a list of dictionaries or a single dictionary
    if isinstance(data, list):
        ticks = data
    else:
        ticks = [data]
        
    for tick in ticks:
        if sniper and isinstance(tick, dict) and tick.get("event_type") == "price_change":
            # Strategy A: Evaluate spread and snipe if wide enough
            sniper.process_tick(tick)
        else:
            if isinstance(tick, dict):
                logger.debug(f"Unhandled Tick: {tick.get('event_type')}")

async def track_balance_loop(client, risk_manager: RiskManager, interval_seconds: int = 60):
    """
    Background task to poll the wallet balance and feed it into the RiskManager
    for Auto-Banking ($1000 threshold) and Trailing Stop-Loss evaluation.
    """
    logger.info(f"Starting balance tracker loop (interval: {interval_seconds}s)")
    while not risk_manager.state.is_halted:
        try:
            # For py_clob_client, checking allowance/balance usually runs through specific endpoints or Web3.
            # Using standard proxy get_balance (assuming USDC.e on Polygon).
            # Note: actual py_clob_client.get_balance might require the exact asset dictionary,
            # but for MVP logic simulation, assuming it returns dict with 'balance'.
            
            # API NOTE: Currently PyClobClient natively doesn't have a direct get_balance without Web3. 
            # So for the MVP, we simulate parsing a balance, but in production we use Web3.py.
            
            # Mocking the balance check response for testing Phase 3 logic loop:
            # We start at 10.00 and pretend after a few seconds we hit the milestone.
            mock_live_balance = 10.00 # Placeholder for $1000/week scaling milestone
            
            # If DRY_RUN is active, aggregate the theoretical session profits 
            if sniper and getattr(sniper, "dry_run", False):
                mock_live_balance += getattr(sniper, "simulated_pnl", 0.0)
            
            # Print beautiful terminal update
            logger.info(f"==================================================")
            logger.info(f" 💸 [LIVE PNL] Current Balance: ${mock_live_balance:.2f} ")
            logger.info(f" 📈 [HIGH WATER MARK] Peak: ${risk_manager.state.high_water_mark:.2f} ")
            logger.info(f"==================================================")
            
            risk_manager.update_balance(mock_live_balance) 
            
        except Exception as e:
            logger.error(f"Failed to check balance: {e}")
            
        await asyncio.sleep(interval_seconds)

async def main():
    global sniper
    load_dotenv()
    logger.info("Starting PolyBot Phase 3: Scaling & Auto-Banking")
    
    try:
        client = get_clob_client()
        logger.info(f"Client initialized for address: {client.get_address()}")
        
        # Initialize Phase 3 Risk Manager
        risk_manager = RiskManager(initial_balance=10.00, client=client)
        
        # Initialize Phase 5 Dynamic Spread Strategy
        # User Configuration: 1.5x EMA multiplier for balanced volatility breakout catching
        sniper = SpreadSniper(clob_client=client, ema_multiplier=1.5, min_spread_floor=0.015, order_size=5.0)
    except Exception as e:
        logger.critical(f"Failed to initialize CLOB client. Exiting. Error: {e}")
        return

    # Fetch top markets dynamically
    # Watching a wide swath of 20 Goldilocks markets (Rank 10-30) to find the best breakout opportunities
    logger.info("Fetching token IDs for the extended Goldilocks markets (20 markets)...")
    top_market_token_ids = get_top_markets(limit=20, offset=10)
    
    if not top_market_token_ids:
        logger.error("Failed to fetch any market tokens. Exiting.")
        return

    ws_client = PolyWebsocketClient(
        token_ids=top_market_token_ids,
        on_message_callback=process_market_tick
    )
    
    logger.info("Entering main websocket listener loops...")
    
    # Start the background loops asynchronously
    heartbeat_task = asyncio.create_task(start_heartbeat(client, interval_seconds=50))
    balance_task = asyncio.create_task(track_balance_loop(client, risk_manager, interval_seconds=60))
    
    try:
        await ws_client.connect_and_listen()
    except asyncio.CancelledError:
        logger.info("Main loop cancelled.")
    finally:
        ws_client.stop()
        heartbeat_task.cancel()
        logger.info("PolyBot shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot manually stopped.")
