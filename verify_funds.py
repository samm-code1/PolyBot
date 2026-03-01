from web3 import Web3
from dotenv import load_dotenv
import os

def check_balances():
    load_dotenv()
    
    # Polygon RPC (Using official public RPC for stability)
    w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL", "https://polygon-rpc.com")))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon RPC.")
        return

    # Derive address from Private Key
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        print("❌ Wait! Your PRIVATE_KEY is missing from .env.")
        return
        
    try:
        account = w3.eth.account.from_key(private_key)
        address = account.address
        print(f"🔍 Checking Wallet: {address}\n")
    except Exception as e:
        print(f"❌ Invalid Private Key! Error: {e}")
        return

    # 1. Check Native MATIC Gas Balance
    matic_wei = w3.eth.get_balance(address)
    matic_balance = w3.from_wei(matic_wei, 'ether')

    if matic_balance > 0.1:
        print(f"✅ MATIC Gas Balance: {matic_balance:.4f} MATIC  (Ready for thousands of trades!)")
    else:
        print(f"⚠️ MATIC Gas Balance: {matic_balance:.4f} MATIC  (WARNING: You need more MATIC to pay gas fees.)")

    # 2. Check Bridged USDC.e Balance
    # Contract Address for Bridged USDC.e on Polygon: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
    usdc_contract_address = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
    
    # Standard ERC-20 balanceOf ABI
    erc20_abi = [
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}
    ]
    
    usdc_contract = w3.eth.contract(address=usdc_contract_address, abi=erc20_abi)
    usdc_balance_raw = usdc_contract.functions.balanceOf(address).call()
    
    # USDC.e has 6 decimal places on Polygon
    usdc_balance = usdc_balance_raw / (10 ** 6)

    if usdc_balance >= 5.0:
        print(f"✅ USDC.e Trading Balance: ${usdc_balance:.2f}  (Ready to trade!)")
    else:
        print(f"⚠️ USDC.e Trading Balance: ${usdc_balance:.2f}  (WARNING: You need at least $5.00 to place a minimum Polymarket order.)")

if __name__ == "__main__":
    check_balances()
