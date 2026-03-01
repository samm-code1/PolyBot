import os
from py_clob_client.client import ClobClient
from dotenv import load_dotenv
from bot.utils.logger import setup_logger

logger = setup_logger("API_Client")
load_dotenv()

def get_clob_client() -> ClobClient:
    host = os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com")
    chain_id = int(os.getenv("POLYMARKET_CHAIN_ID", "137"))
    private_key = os.getenv("PRIVATE_KEY")
    
    if not private_key:
        logger.error("PRIVATE_KEY missing in .env")
        raise ValueError("PRIVATE_KEY environment variable is not set")

    try:
        client = ClobClient(host, key=private_key, chain_id=chain_id)
        client.set_api_creds(client.create_or_derive_api_creds())
        logger.info("py_clob_client initialized successfully with L1/L2 credentials.")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize py_clob_client: {e}")
        raise
