import os
from py_clob_client.client import ClobClient
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("POLYMARKET_HOST")
chain_id = int(os.getenv("POLYMARKET_CHAIN_ID"))
key = os.getenv("PRIVATE_KEY")

try:
    print("Testing ClobClient INIT...")
    client = ClobClient(host, key=key, chain_id=chain_id)
    print("SUCCESS INIT")
    
    print("Testing create_or_derive_api_creds...")
    creds = client.create_or_derive_api_creds()
    print("SUCCESS CREDS")
except Exception as e:
    import traceback
    traceback.print_exc()

