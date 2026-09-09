import hashlib, json
from pathlib import Path
from unittest.mock import patch
from gltest.direct import VMContext, create_address, deploy_contract
ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "RepairQuoteScopeGate.py"
SCOPE = json.dumps({"schema_version":"1.0","project_ref":"RQS-204","approved_items":[{"scope_id":"S-01","area":"Kitchen","work":"Replace the sink P-trap"}]}, separators=(",", ":"))
QUOTE = json.dumps({"schema_version":"1.0","project_ref":"RQS-204","quote_items":[{"line_id":"Q-01","area":"Kitchen","work":"Supply and install one sink P-trap","scope_ref":"S-01"}]}, separators=(",", ":"))
def sha(v): return hashlib.sha256(v.encode()).hexdigest()

def deploy():
    owner, outsider = create_address("owner"), create_address("outsider"); vm = VMContext(owner)
    with patch("os.unlink", lambda _: None), vm.activate():
        contract = deploy_contract(CONTRACT, vm); gl = contract._instance.create_review.__globals__["gl"]; _ = gl.nondet
    return vm, contract, owner, outsider

def sync(vm, contract):
    gl = contract._instance.create_review.__globals__["gl"]; sender = vm.sender
    if isinstance(sender, bytes): sender = type(gl.message.sender_address)(sender)
    gl._cached_gl.message = gl.message._replace(sender_address=sender, origin_address=sender, value=type(gl.message.value)(vm.value))

def create(vm, contract):
    sync(vm, contract)
    return contract.create_review("Kitchen quote", "https://example.com/scope.json", sha(SCOPE), "https://example.com/quote.json", sha(QUOTE))

def test_create_guards_and_creator_authority():
    vm, contract, _, outsider = deploy()
    with vm.activate():
        sync(vm, contract); assert contract.create_review("", "https://a", "0"*64, "https://b", "0"*64) == "INVALID_TITLE"; rid = create(vm, contract)
    with vm.prank(outsider):
        sync(vm, contract); assert contract.capture_sources(rid) == "CREATOR_ONLY"

def test_package_schema_and_duplicate_ids():
    validate = deploy()[1]._instance.create_review.__globals__["_validate_package"]
    assert validate(SCOPE, QUOTE) and not validate("{}", QUOTE)
    duplicate = json.dumps({"schema_version":"1.0","project_ref":"RQS-204","quote_items":[{"line_id":"Q-01","area":"Kitchen","work":"One","scope_ref":"S-01"},{"line_id":"Q-01","area":"Kitchen","work":"Two","scope_ref":"S-01"}]},separators=(",",":"))
    assert not validate(SCOPE, duplicate)

def test_capture_failures_do_not_mutate_and_success_binds_bodies():
    vm, contract, _, _ = deploy()
    with vm.activate(): rid = create(vm, contract)
    module = contract._instance.create_review.__globals__
    with vm.activate(), patch.dict(module, {"_fetch_exact": lambda url: SCOPE if "scope" in url else QUOTE.replace("P-trap", "faucet")}):
        sync(vm, contract); assert contract.capture_sources(rid) == "QUOTE_HASH_MISMATCH"
    assert contract.get_review(rid).split("|")[0] == "DRAFT"
    with vm.activate(), patch.dict(module, {"_fetch_exact": lambda url: SCOPE if "scope" in url else QUOTE}):
        sync(vm, contract); assert contract.capture_sources(rid) == "SOURCES_CAPTURED"
    assert contract.get_review(rid).split("|")[0] == "CAPTURED"

def test_all_assessment_outcomes_and_replay_guard():
    for verdict in ("QUOTE_ACCEPTABLE", "REVIEW_REQUIRED", "SCOPE_VIOLATION"):
        vm, contract, _, _ = deploy(); module = contract._instance.create_review.__globals__
        with vm.activate(): rid = create(vm, contract)
        with vm.activate(), patch.dict(module, {"_fetch_exact": lambda url: SCOPE if "scope" in url else QUOTE}): sync(vm, contract); contract.capture_sources(rid)
        with vm.activate(), patch.dict(module, {"_classify_quote": lambda approved, quote: verdict}): sync(vm, contract); assert contract.assess_quote(rid) == verdict
        frozen = contract.get_review(rid)
        with vm.activate(): sync(vm, contract); assert contract.assess_quote(rid) == "ASSESSMENT_NOT_ALLOWED"
        assert contract.get_review(rid) == frozen

def test_close_requires_assessment_and_creator():
    vm, contract, _, outsider = deploy()
    with vm.activate(): rid = create(vm, contract); assert contract.close_review(rid) == "CLOSE_NOT_ALLOWED"
    with vm.prank(outsider): sync(vm, contract); assert contract.close_review(rid) == "CREATOR_ONLY"
