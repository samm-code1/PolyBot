from bot.api.client import get_clob_client
from py_clob_client.clob_types import BalanceAllowanceParams, AssetType

def approve_usdc():
    print("Approving Polymarket Exchange to spend USDC.e...")
    try:
        client = get_clob_client()
        # Create parameters using the exact AssetType Enum
        params = BalanceAllowanceParams(asset_type=AssetType.COLLATERAL, signature_type=1) 
        res = client.update_balance_allowance(params)
        print("✅ Allowance approved successfully!")
        print(f"Transaction Hash / Response: {res}")
    except Exception as e:
        print(f"❌ Failed to approve allowance. Error: {e}")

if __name__ == "__main__":
    approve_usdc()
