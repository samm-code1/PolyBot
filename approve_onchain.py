from web3 import Web3
import os
from dotenv import load_dotenv

def approve_onchain():
    load_dotenv()
    
    # Polygon RPC
    w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL", "https://polygon-rpc.com")))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon RPC.")
        return

    private_key = os.getenv("PRIVATE_KEY")
    account = w3.eth.account.from_key(private_key)
    address = account.address
    
    # USDC.e Address on Polygon
    usdc_address = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
    # Polymarket CTF Exchange Address (from py_clob_client)
    exchange_address = Web3.to_checksum_address("0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E")

    # ERC20 Approve ABI
    erc20_abi = [
        {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
    ]
    
    usdc_contract = w3.eth.contract(address=usdc_address, abi=erc20_abi)
    
    # Check current allowance
    current_allowance = usdc_contract.functions.allowance(address, exchange_address).call()
    print(f"Current Allowance: {current_allowance} wei")
    
    if current_allowance > 0:
        print("✅ You already have some allowance approved.")
        return

    # Approve MAX_UINT256
    max_amount = 2**256 - 1
    
    print(f"Building approve transaction for {address} to allow Exchange {exchange_address}...")
    txn = usdc_contract.functions.approve(exchange_address, max_amount).build_transaction({
        'from': address,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(address),
    })

    print("Signing transaction...")
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    
    print("Broadcasting to Polygon...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"✅ Transaction broadcasted! Hash: {w3.to_hex(tx_hash)}")
    print("Wait ~15 seconds for it to confirm, then deploy PolyBot again.")

if __name__ == "__main__":
    approve_onchain()
