import requests
from typing import List
from bot.utils.logger import setup_logger
import json

logger = setup_logger("API_Markets")

def get_top_markets(limit: int = 1, offset: int = 0) -> List[str]:
    """
    Fetches the top active markets by volume from Polymarket.
    Returns a list of token IDs.
    """
    url = f"https://gamma-api.polymarket.com/events?active=true&closed=false&limit={limit}&offset={offset}"
    
    try:
        logger.info(f"Fetching {limit} markets by volume (offset {offset}) from {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        events = response.json()
        
        token_ids = []
        for event in events:
            # Events contain a list of 'markets'
            markets = event.get("markets", [])
            for market in markets:
                clob_token_ids_str = market.get("clobTokenIds")
                if clob_token_ids_str:
                    try:
                        parsed_ids = json.loads(clob_token_ids_str)
                        token_ids.extend(parsed_ids)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse clobTokenIds for market {market.get('id')}")
                    
        # Return unique token IDs
        unique_token_ids = list(set(token_ids))
        logger.info(f"Successfully retrieved {len(unique_token_ids)} token IDs from top {limit} markets.")
        return unique_token_ids
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching top markets: {e}")
        return []

if __name__ == "__main__":
    # Test
    print(get_top_markets(1))
