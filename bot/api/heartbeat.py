import asyncio
from py_clob_client.client import ClobClient
from bot.utils.logger import setup_logger

logger = setup_logger("Heartbeat")

async def start_heartbeat(client: ClobClient, interval_seconds: int = 50):
    """
    Background task to keep the active session window open.
    Polymarket requires a heartbeat every 60 seconds (or less) to prevent
    automatic cancellation of resting limit orders when the connection drops.
    """
    logger.info(f"Starting heartbeat loop (interval: {interval_seconds}s)")
    
    while True:
        try:
            # Polymarket API heartbeat
            responseMsg = client.post_heartbeat(None)
            logger.debug(f"Heartbeat Sent. Response: {responseMsg}")
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
            
        await asyncio.sleep(interval_seconds)
