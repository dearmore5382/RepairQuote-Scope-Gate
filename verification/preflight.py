"""Read-only deployed-source parity and initial-state verification."""
import base64, hashlib, json
from pathlib import Path
import requests
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize

ROOT=Path(__file__).resolve().parents[1]
ADDRESS="0x789c96431699b1e280E36A57102A0842Bae17aE5"
RPC="https://studio.genlayer.com/api"
EXPECTED="e55e7e8f75881d62abfad04315f2414fe64921f98ae313d9191bccc83d3db334"
SENDER="0x0000000000000000000000000000000000000001"

def rpc(method,params):
 response=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=45); response.raise_for_status(); data=response.json()
 if "error" in data: raise RuntimeError(json.dumps(data["error"]))
 return data["result"]
def view(method,args=None):
 data=serialize([calldata.encode({"method":method,"args":args or []}),b"\x00"]); raw=rpc("gen_call",[{"type":"read","to":ADDRESS,"from":SENDER,"value":"0x0","data":data,"transaction_hash_variant":"latest-final"}]); return str(calldata.decode(bytes.fromhex(raw.removeprefix("0x"))))
def main():
 deployed=base64.b64decode(rpc("gen_getContractCode",[ADDRESS])); local=(ROOT/"contracts"/"RepairScope.py").read_bytes()
 report={"network":"Studionet","chain_id":int(rpc("eth_chainId",[]),16),"contract":ADDRESS,"source_sha256":hashlib.sha256(deployed).hexdigest(),"exact_source_parity":deployed==local,"initial_counts":view("get_counts"),"schema":rpc("gen_getContractSchema",[ADDRESS])}
 if report["chain_id"]!=61999: raise RuntimeError("WRONG_CHAIN")
 if report["source_sha256"]!=EXPECTED or not report["exact_source_parity"]: raise RuntimeError("SOURCE_PARITY_FAILED")
 if report["initial_counts"]!="0|0": raise RuntimeError("INITIAL_STATE_NOT_EMPTY")
 out=ROOT/"verification"/("preflight-"+ADDRESS.lower()+".json"); out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8"); print(json.dumps({k:v for k,v in report.items() if k!="schema"},indent=2))
if __name__=="__main__": main()
