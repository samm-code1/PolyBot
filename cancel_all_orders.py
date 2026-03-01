from bot.api.client import get_clob_client
import time

def cancel_all_open_orders():
    print("Fetching active orders on Polymarket...")
    try:
        client = get_clob_client()
        
        # 1. Fetch all currently open orders for this wallet
        open_orders = client.get_orders()
        
        if not open_orders:
            print("✅ No open orders found! All your capital is currently free.")
            return

        order_count = len(open_orders)
        print(f"⚠️ Found {order_count} open orders locking up capital. Canceling now...")

        # 2. Extract all IDs and batch cancel them
        order_ids = [order.get("id") for order in open_orders if order.get("id")]
        
        try:
            # Polymarket natively accepts an array of IDs to cancel in one API call
            client.cancel_orders(order_ids)
            print(f"\n✅ Successfully sent batch cancellation command for {len(order_ids)} orders.")
            print("Your USDC.e collateral has been refunded to your wallet!")
        except Exception as e:
            print(f"❌ Failed to batch cancel orders: {e}")

    except Exception as e:
        print(f"❌ Error communicating with Polymarket: {e}")

if __name__ == "__main__":
    cancel_all_open_orders()
