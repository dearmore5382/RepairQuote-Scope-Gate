"""Checkpointed Studionet happy path; submitted hashes are never resent."""
import base64,getpass,hashlib,json,os,sys,time
from pathlib import Path
import requests
from dotenv import dotenv_values
from genlayer_py import create_account,create_client
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.chains import studionet
R=Path(__file__).resolve().parents[1]; A=os.environ.get("REPAIRQUOTE_CONTRACT",""); RPC="https://studio.genlayer.com/api"; C="b379644f492cd730e9f7655052b3138250dc65b8"; B=f"https://raw.githubusercontent.com/dearmore5382/RepairQuote-Scope-Gate/{C}/test-fixtures"; SH="9a97bf34b6c01d93662823951d555c44f7000f10c2d12872f796fa20cb02425b"; S=(f"{B}/approved-scope.json","fcea0a746395b8f1c9b7499da54c9adc21eda9de420302cfd01ae32ebcf266b8"); Q=(f"{B}/quote-happy.json","1606137ebec9f9e347a43aef3abff85bb0e9be06503e6b158b4466e3dad2be56"); V=(f"{B}/quote-violation.json","175f74afc96e9d38aa2f25a62cb18cab2bb5d9ea8350e462aa8a8141d3f282c1"); M=(f"{B}/quote-ambiguous.json","43653d9424fd7314b1526f221c9a8dccfc31b4343e767fae18e968b7788fffda"); P=R/".private"/("quote-"+A.lower()+".json"); O=R/"verification"/("live-"+A.lower()+".json")
def rpc(m,p):
 x=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":m,"params":p},timeout=45);x.raise_for_status();d=x.json()
 if "error" in d:raise RuntimeError(d["error"])
 return d["result"]
def view(m,args=[]):
 d=serialize([calldata.encode({"method":m,"args":args}),b"\0"]);r=rpc("gen_call",[{"type":"read","to":A,"from":"0x0000000000000000000000000000000000000001","value":"0x0","data":d,"transaction_hash_variant":"latest-final"}]);return str(calldata.decode(bytes.fromhex(r.removeprefix("0x"))))
def ret(t):
 r=t["consensus_data"]["leader_receipt"];r=[r]if isinstance(r,dict)else r;r=[x for x in r if x.get("mode")=="leader"][-1];v=r["result"];z=base64.b64decode(v["raw"]if isinstance(v,dict)else v)
 if r["execution_result"]!="SUCCESS"or z[0]!=0:raise RuntimeError("EXECUTION_FAILED")
 return str(calldata.decode(z[1:]))
def save(j):
 P.parent.mkdir(exist_ok=True);P.write_text(json.dumps(j,indent=2));q=json.loads(json.dumps(j));[x.pop("receipt",None)for x in q["steps"]];O.write_text(json.dumps(q,indent=2)+"\n")
def main():
 key_file=os.environ.get("REPAIRQUOTE_KEY_FILE","")
 if key_file:
  env=dotenv_values(key_file);ks=[str(env["WALLET_A_PRIVATE_KEY"]),str(env["WALLET_B_PRIVATE_KEY"])]
 else:
  if not sys.stdin.isatty():raise RuntimeError("TTY_REQUIRED")
  ks=json.loads(getpass.getpass("KEY_INPUT_REQUIRED_NO_ECHO: "))
 ac=[create_account(account_private_key="0x"+x.removeprefix("0x"))for x in ks];del ks
 if len(ac)!=2:raise RuntimeError("TWO_KEYS")
 if hashlib.sha256((R/"contracts/RepairQuoteScopeGate.py").read_bytes()).hexdigest()!=SH or base64.b64decode(rpc("gen_getContractCode",[A]))!=(R/"contracts/RepairQuoteScopeGate.py").read_bytes():raise RuntimeError("SOURCE_MISMATCH")
 c={x.address.lower():create_client(chain=studionet,account=x)for x in ac};u,o=ac
 plan=[("F1-invalid-title",u,"create_review",["",S[0],S[1],Q[0],Q[1]],"INVALID_TITLE"),("H1-create",u,"create_review",["Kitchen sink quote",S[0],S[1],Q[0],Q[1]],"0"),("F2-assess-before-capture",u,"assess_quote",[0],"ASSESSMENT_NOT_ALLOWED"),("H2-outsider-capture",o,"capture_sources",[0],"SOURCES_CAPTURED"),("H3-assess",o,"assess_quote",[0],"QUOTE_ACCEPTABLE"),("F3-outsider-close",o,"close_review",[0],"CREATOR_ONLY"),("F4-replay",u,"assess_quote",[0],"ASSESSMENT_NOT_ALLOWED"),("H4-close",u,"close_review",[0],"REVIEW_CLOSED"),("A1-create-violation",u,"create_review",["Out-of-scope quote",S[0],S[1],V[0],V[1]],"1"),("A2-capture-violation",o,"capture_sources",[1],"SOURCES_CAPTURED"),("A3-assess-violation",o,"assess_quote",[1],"SCOPE_VIOLATION"),("A4-create-ambiguous",u,"create_review",["Ambiguous quote",S[0],S[1],M[0],M[1]],"2"),("A5-capture-ambiguous",o,"capture_sources",[2],"SOURCES_CAPTURED"),("A6-assess-ambiguous",o,"assess_quote",[2],"REVIEW_REQUIRED"),("F5-create-wrong-digest",u,"create_review",["Wrong digest",S[0],"0000000000000000000000000000000000000000000000000000000000000000",Q[0],Q[1]],"3"),("F6-reject-wrong-digest",o,"capture_sources",[3],"APPROVED_SCOPE_HASH_MISMATCH")]
 j=json.loads(P.read_text())if P.exists()else{"contract":A,"source_sha256":SH,"fixture_commit":C,"wallets":[x.address for x in ac],"steps":[],"complete":False}
 if not P.exists()and view("get_review_count")!="0":raise RuntimeError("EXPECTED_EMPTY")
 save(j);print(json.dumps({"ready":True,"completed":len(j["steps"]),"total":len(plan)}),flush=True)
 for i,(name,a,m,args,want)in enumerate(plan):
  if i<len(j["steps"]):it=j["steps"][i]
  else:
   it={"id":name,"actor":a.address,"method":m,"args":args,"expected":want,"status":"INTENT"};j["steps"].append(it);save(j)
  if it.get("status")=="INTENT":
   it["hash"]=str(c[a.address.lower()].write_contract(address=A,function_name=m,args=args,value=0,leader_only=False));it["status"]="SUBMITTED";save(j);print(json.dumps({"step":name,"hash":it["hash"]}),flush=True)
  if it.get("status")=="VERIFIED":continue
  for _ in range(150):
   t=rpc("eth_getTransactionByHash",[it["hash"]])
   if t and t.get("status")=="FINALIZED":
    if t.get("result_name")!="MAJORITY_AGREE":raise RuntimeError("CONSENSUS_FAILED:"+name)
    got=ret(t)
    if got!=want:raise RuntimeError(f"UNEXPECTED:{name}:{got}")
    rb={"count":view("get_review_count")};
    for rid in range(int(rb["count"])):rb[f"review{rid}"]=view("get_review",[rid])
    if name=="H3-assess":j["frozen"]=rb["review0"]
    if name=="F4-replay"and rb["review0"]!=j["frozen"]:raise RuntimeError("REPLAY_MUTATED")
    it.update({"actual":got,"readback":rb,"receipt":t,"status":"VERIFIED"});save(j);print(json.dumps({"step":name,"actual":got,"readback":rb}),flush=True);break
   time.sleep(8)
  else:raise RuntimeError("POLL_TIMEOUT_KEEP_HASH")
 j["complete"]=True;save(j);print(json.dumps({"complete":True,"steps":len(plan)}))
if __name__=="__main__":main()
