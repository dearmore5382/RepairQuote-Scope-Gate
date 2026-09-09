import ast
from pathlib import Path
SOURCE = (Path(__file__).resolve().parents[1] / "contracts" / "RepairQuoteScopeGate.py").read_text(encoding="utf-8")

def test_contract_shape_and_non_payable_profile():
    ast.parse(SOURCE)
    assert "class RepairQuoteScopeGate(gl.Contract):" in SOURCE
    assert "payable" not in SOURCE and "emit_transfer" not in SOURCE

def test_sources_are_fetched_exactly_and_digest_bound():
    assert SOURCE.count("gl.eq_principle.strict_eq(") == 2
    assert "hashlib.sha256(approved.encode" in SOURCE
    assert "hashlib.sha256(quote.encode" in SOURCE
    assert "_validate_package(approved, quote)" in SOURCE

def test_ai_surface_is_one_bounded_verdict():
    block = SOURCE.split("def _classify_quote", 1)[1].split("class RepairQuoteScopeGate", 1)[0]
    for value in ("QUOTE_ACCEPTABLE", "REVIEW_REQUIRED", "SCOPE_VIOLATION"): assert value in block
    assert "Do not judge price, workmanship, urgency, legal liability, or payment" in block
    assert "json.dumps" not in block

def test_source_failures_precede_storage_mutation():
    block = SOURCE.split("def capture_sources", 1)[1].split("@gl.public.write", 1)[0]
    mutation = block.index('self.approved_bodies[review_id] = approved')
    for marker in ("SOURCE_UNAVAILABLE", "APPROVED_SCOPE_HASH_MISMATCH", "QUOTE_HASH_MISMATCH", "INVALID_PACKAGE_SCHEMA"):
        assert block.index(marker) < mutation
