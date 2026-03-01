from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from typing import Dict, Any, Optional
from bot.utils.logger import setup_logger
from bot.risk.stop_loss import RiskManager

logger = setup_logger("Orders")

def post_new_order(client: ClobClient, risk_manager: RiskManager, order_args: OrderArgs) -> Optional[Dict[str, Any]]:
    if not risk_manager.can_trade():
        logger.error("Trading halted by risk manager. Order not placed.")
        return None
        
    try:
        order = client.create_order(order_args)
        resp = client.post_order(order)
        
        # Typically the client returns a dictionary with 'errorMsg' or 'orderID'
        if isinstance(resp, dict) and resp.get("errorMsg"):
            logger.error(f"CLOB API Error posting order: {resp['errorMsg']}")
            return None
            
        order_id = resp.get("orderID") if isinstance(resp, dict) else getattr(resp, "orderID", "Unknown")
        logger.info(f"Order posted successfully: {order_id}")
        return resp
    except Exception as e:
        logger.error(f"Exception posting order: {e}")
        return None

def cancel_single_order(client: ClobClient, order_id: str) -> bool:
    try:
        # Note: cancel typically returns a string message or a dictionary
        resp = client.cancel(order_id)
        if isinstance(resp, dict) and resp.get("errorMsg"):
             logger.error(f"CLOB API Error cancelling order {order_id}: {resp['errorMsg']}")
             return False
             
        logger.info(f"Successfully cancelled order {order_id}: {resp}")
        return True
    except Exception as e:
        logger.error(f"Exception tracking cancelling order {order_id}: {e}")
        return False
