import asyncio
import json
import websockets
from typing import Callable, Coroutine, Any, List
from bot.utils.logger import setup_logger

logger = setup_logger("WebSocketClient")

WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

class PolyWebsocketClient:
    def __init__(self, token_ids: List[str], on_message_callback: Callable[[dict], Coroutine[Any, Any, None]]):
        self.token_ids = token_ids
        self.on_message_callback = on_message_callback
        self.ws = None
        self._running = False

    async def connect_and_listen(self):
        self._running = True
        retry_delay = 1
        
        while self._running:
            try:
                logger.info(f"Connecting to {WS_URL}...")
                async with websockets.connect(WS_URL) as ws:
                    self.ws = ws
                    logger.info("Connected to Market Channel.")
                    retry_delay = 1 # Reset delay on successful connection
                    
                    # Subscribe to markets
                    subscribe_msg = {
                        "assets_ids": self.token_ids,
                        "type": "market"
                    }
                    await self.ws.send(json.dumps(subscribe_msg))
                    logger.info(f"Sent subscribe message for tokens: {self.token_ids}")
                    
                    # Listen for messages
                    async for message in self.ws:
                        if not self._running:
                            break
                        try:
                            data = json.loads(message)
                            await self.on_message_callback(data)
                        except json.JSONDecodeError:
                            logger.error(f"Failed to decode message: {message}")
                        except Exception as e:
                            logger.error(f"Error in message callback: {e}")
                            
            except (websockets.ConnectionClosed, Exception) as e:
                if not self._running:
                    break
                logger.error(f"WebSocket disconnected: {e}. Reconnecting in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60) # Exponential backoff max 60s
                
    def stop(self):
        self._running = False
        if self.ws:
            asyncio.create_task(self.ws.close())
