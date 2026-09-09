"""Checkpointed RepairScope Studionet audit. Never auto-resubmits a transaction."""
import base64,getpass,hashlib,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
import requests
from genlayer_py import create_account,create_client
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.chains import studionet

ROOT=Path(__file__).resolve().parents[1]; ADDRESS="0x789c96431699b1e280E36A57102A0842Bae17aE5"; RPC="https://studio.genlayer.com/api"; SOURCE_HASH="e55e7e8f75881d62abfad04315f2414fe64921f98ae313d9191bccc83d3db334"
BASELINE="At handover, the kitchen sink, tap, cabinet base, drain and visible supply lines were dry, intact and operating normally. No water staining or swelling was recorded."
POLICY="The owner maintains concealed plumbing, supply lines and building systems. The tenant is responsible for misuse, avoidable overflow and reasonable day-to-day care. Ordinary wear is not tenant damage. Accidental damage with shared maintenance contribution is shared responsibility."
PRIVATE=ROOT/".private"/("live-"+ADDRESS.lower()+".json"); PUBLIC=ROOT/"verification"/("live-"+ADDRESS.lower()+".json")
def rpc(method,params):
 response=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=45); response.raise_for_status(); data=response.json()
 if "error" in data: raise RuntimeError("RPC_ERROR:"+str(data["error"].get("message")))
 return data["result"]
def view(method,args=None,sender="0x0000000000000000000000000000000000000001"):
 data=serialize([calldata.encode({"method":method,"args":args or []}),b"\x00"]); raw=rpc("gen_call",[{"type":"read","to":ADDRESS,"from":sender,"value":"0x0","data":data,"transaction_hash_variant":"latest-final"}]); return str(calldata.decode(bytes.fromhex(raw.removeprefix("0x"))))
def parity():
 deployed=base64.b64decode(rpc("gen_getContractCode",[ADDRESS])); local=(ROOT/"contracts"/"RepairScope.py").read_bytes()
 if deployed!=local or hashlib.sha256(deployed).hexdigest()!=SOURCE_HASH: raise RuntimeError("SOURCE_MISMATCH")
def tx_return(tx):
 receipts=(tx.get("consensus_data") or {}).get("leader_receipt") or []; receipts=[receipts] if isinstance(receipts,dict) else receipts; leaders=[x for x in receipts if x.get("mode")=="leader"]
 if not leaders or leaders[-1].get("execution_result")!="SUCCESS": raise RuntimeError("LEADER_EXECUTION_FAILED")
 value=leaders[-1].get("result"); raw=base64.b64decode(value["raw"] if isinstance(value,dict) else value)
 if not raw or raw[0]!=0: raise RuntimeError("CONTRACT_EXECUTION_ERROR")
 return str(calldata.decode(raw[1:]))
def save(j):
 PRIVATE.parent.mkdir(exist_ok=True); PRIVATE.write_text(json.dumps(j,indent=2),encoding="utf-8"); public=json.loads(json.dumps(j)); public.pop("balances",None)
 for x in public["steps"]: x.pop("receipt",None)
 PUBLIC.write_text(json.dumps(public,indent=2)+"\n",encoding="utf-8")
def main():
 if not sys.stdin.isatty(): raise RuntimeError("TTY_REQUIRED")
 keys=json.loads(getpass.getpass("KEY_INPUT_REQUIRED_NO_ECHO: ")); accounts=[create_account(account_private_key="0x"+k.removeprefix("0x")) for k in keys]; del keys
 if len(accounts)!=2: raise RuntimeError("TWO_WALLETS_REQUIRED")
 owner,tenant=accounts; clients={a.address.lower():create_client(chain=studionet,account=a) for a in accounts}; parity(); balances={a.address:int(rpc("eth_getBalance",[a.address,"latest"]),16) for a in accounts}
 misuse="After handover, the tenant left the tap running with the drain stopper closed for about twenty minutes. Water overflowed onto the previously dry cabinet base, causing new swelling."
 misuse_reply="I inspected after the reported overflow. The cabinet shows fresh overflow staining from above; the visible supply and drain connections were dry and operating, with no system leak."
 conflict="New water damage appeared in the cabinet, but I do not know when it began or whether the tap, drain, or a concealed line caused it."
 conflict_reply="I cannot confirm the timing or cause. The accounts disagree about whether staining existed before handover and no shared observation resolves that point."
 plan=[
  {"id":"F1-invalid-create","actor":owner.address,"method":"create_property","args":["","Kitchen","Sink",BASELINE,POLICY,tenant.address],"allowed":["INVALID_PROPERTY_REFERENCE"]},
  {"id":"H1-create","actor":owner.address,"method":"create_property","args":["LEASE-204-KITCHEN","Kitchen","Sink and supply lines",BASELINE,POLICY,tenant.address],"allowed":["0"]},
  {"id":"F2-owner-accept","actor":owner.address,"method":"accept_baseline","args":[0],"allowed":["TENANT_ONLY"]},
  {"id":"H2-tenant-accept","actor":tenant.address,"method":"accept_baseline","args":[0],"allowed":["BASELINE_ACCEPTED"]},
  {"id":"F3-tenant-seal-property","actor":tenant.address,"method":"seal_property","args":[0],"allowed":["OWNER_ONLY"]},
  {"id":"H3-owner-seal-property","actor":owner.address,"method":"seal_property","args":[0],"allowed":["PROPERTY_SEALED"]},
  {"id":"H4-open-misuse","actor":tenant.address,"method":"open_report","args":[0,misuse],"allowed":["0"]},
  {"id":"F4-duplicate-pending","actor":owner.address,"method":"open_report","args":[0,"A second report must not replace the pending report."],"allowed":["PENDING_REPORT_EXISTS"]},
  {"id":"H5-owner-response","actor":owner.address,"method":"respond_report","args":[0,misuse_reply],"allowed":["REPORT_RESPONDED"]},
  {"id":"F5-owner-seal-report","actor":owner.address,"method":"seal_report","args":[0],"allowed":["REPORTER_ONLY"]},
  {"id":"H6-tenant-seal-report","actor":tenant.address,"method":"seal_report","args":[0],"allowed":["REPORT_SEALED"]},
  {"id":"H7-assess-misuse","actor":owner.address,"method":"assess_report","args":[0],"allowed":["TENANT_RESPONSIBLE","ASSESSMENT_RETRYABLE"]},
  {"id":"H7b-explicit-retry","actor":tenant.address,"method":"assess_report","args":[0],"allowed":["TENANT_RESPONSIBLE"]},
  {"id":"A1-replay","actor":tenant.address,"method":"assess_report","args":[0],"allowed":["REPORT_NOT_ASSESSABLE"]},
  {"id":"H8-open-conflict","actor":owner.address,"method":"open_report","args":[0,conflict],"allowed":["1"]},
  {"id":"H9-tenant-response","actor":tenant.address,"method":"respond_report","args":[1,conflict_reply],"allowed":["REPORT_RESPONDED"]},
  {"id":"H10-owner-seal-report","actor":owner.address,"method":"seal_report","args":[1],"allowed":["REPORT_SEALED"]},
  {"id":"H11-assess-conflict","actor":tenant.address,"method":"assess_report","args":[1],"allowed":["INSUFFICIENT_EVIDENCE"]},
  {"id":"H12-close","actor":owner.address,"method":"close_property","args":[0],"allowed":["PROPERTY_CLOSED"]},
  {"id":"F6-open-closed","actor":tenant.address,"method":"open_report","args":[0,"No report can be opened after closure."],"allowed":["PROPERTY_NOT_ACTIVE"]},
 ]
 if PRIVATE.exists(): j=json.loads(PRIVATE.read_text(encoding="utf-8"))
 else:
  if view("get_counts",sender=owner.address)!="0|0": raise RuntimeError("EXPECTED_EMPTY")
  j={"contract":ADDRESS,"source_sha256":SOURCE_HASH,"started_at":datetime.now(timezone.utc).isoformat(),"wallets":[a.address for a in accounts],"balances":balances,"steps":[],"complete":False}; save(j)
 print(json.dumps({"ready":True,"balances":balances,"completed":len(j["steps"]),"total":len(plan)}),flush=True)
 for index,want in enumerate(plan):
  parity()
  if index<len(j["steps"]):
   item=j["steps"][index]
   if item["id"]!=want["id"]: raise RuntimeError("PLAN_MISMATCH")
   item["allowed"]=want["allowed"]
   if item.get("status")=="VERIFIED": continue
   if item.get("status")!="SUBMITTED": raise RuntimeError("UNKNOWN_INTENT")
  else:
   item=dict(want); item["status"]="INTENT_SAVED"; j["steps"].append(item); save(j); item["hash"]=str(clients[item["actor"].lower()].write_contract(address=ADDRESS,function_name=item["method"],args=item["args"],value=0,leader_only=False)); item["status"]="SUBMITTED"; save(j); print(json.dumps({"step":item["id"],"hash":item["hash"]}),flush=True)
  deadline=time.monotonic()+1200
  while time.monotonic()<deadline:
   tx=rpc("eth_getTransactionByHash",[item["hash"]])
   if tx and tx.get("status")=="FINALIZED":
    if tx.get("result_name")!="MAJORITY_AGREE": raise RuntimeError("CONSENSUS_FAILED")
    actual=tx_return(tx)
    if actual=="ASSESSMENT_RETRYABLE" and item["id"]!="H7-assess-misuse": raise RuntimeError("RETRYABLE_STOP_NO_RESUBMIT")
    if actual not in item["allowed"]: raise RuntimeError("UNEXPECTED:"+actual)
    counts=view("get_counts",sender=owner.address); readback={"counts":counts}
    if counts!="0|0": readback["property0"]=view("get_property",[0],owner.address)
    if item["id"] in ("H7-assess-misuse","H7b-explicit-retry","A1-replay","H11-assess-conflict","H12-close","F6-open-closed"):
     readback["report0"]=view("get_report",[0],owner.address)
     if int(counts.split("|")[1])>1: readback["report1"]=view("get_report",[1],owner.address)
    if item["id"]=="H7-assess-misuse" and actual=="ASSESSMENT_RETRYABLE" and not readback["report0"].startswith("SEALED|"): raise RuntimeError("RETRY_MUTATED_STATE")
    if item["id"] in ("H7-assess-misuse","H7b-explicit-retry") and actual=="TENANT_RESPONSIBLE": j["frozen_report0"]=readback["report0"]
    if item["id"] in ("A1-replay","H11-assess-conflict","H12-close","F6-open-closed") and readback["report0"]!=j.get("frozen_report0"): raise RuntimeError("HISTORY_MUTATED")
    item.update({"actual":actual,"receipt":tx,"readback":readback,"status":"VERIFIED"}); save(j); print(json.dumps({"step":item["id"],"actual":actual,"readback":readback}),flush=True); break
   time.sleep(8)
  else: raise RuntimeError("POLL_TIMEOUT_KEEP_HASH")
 j["complete"]=True; j["completed_at"]=datetime.now(timezone.utc).isoformat(); save(j); print(json.dumps({"complete":True,"steps":len(plan)}))
if __name__=="__main__": main()
