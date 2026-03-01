import os
import requests
from bot.utils.logger import setup_logger

logger = setup_logger("Telegram")

def send_telegram_message(message: str) -> bool:
    """
    Sends a message to the configured Telegram bot chat.
    Validates that the required environment variables are set before sending.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        # Silently fail if the user hasn't configured Telegram yet
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False
