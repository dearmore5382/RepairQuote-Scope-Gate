"""Read-only deployed-source parity gate for RepairQuote Scope Gate."""
import base64, hashlib, json, os
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RPC = "https://studio.genlayer.com/api"
ADDRESS = os.environ.get("REPAIRQUOTE_CONTRACT", "")

def rpc(method, params):
    response = requests.post(RPC, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=45)
    response.raise_for_status(); data = response.json()
    if "error" in data: raise RuntimeError(data["error"].get("message"))
    return data["result"]

def main():
    if not ADDRESS.startswith("0x") or len(ADDRESS) != 42: raise RuntimeError("SET_REPAIRQUOTE_CONTRACT")
    local = (ROOT / "contracts" / "RepairQuoteScopeGate.py").read_bytes()
    deployed = base64.b64decode(rpc("gen_getContractCode", [ADDRESS]))
    result = {"contract":ADDRESS,"chain_id":int(rpc("eth_chainId",[]),16),"local_sha256":hashlib.sha256(local).hexdigest(),"deployed_sha256":hashlib.sha256(deployed).hexdigest(),"exact_source_parity":local==deployed}
    (ROOT/"verification"/("preflight-"+ADDRESS.lower()+".json")).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result))
    if not result["exact_source_parity"]: raise RuntimeError("SOURCE_MISMATCH")

if __name__ == "__main__": main()
