import ast
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "contracts" / "RepairScope.py").read_text(encoding="utf-8")


def test_contract_shape_and_no_custody_or_fetch():
    ast.parse(SOURCE)
    assert "class RepairScope(gl.Contract):" in SOURCE
    assert "payable" not in SOURCE and "emit_transfer" not in SOURCE and "web.get" not in SOURCE


def test_model_returns_observations_not_outcome():
    block = SOURCE.split("def _classify", 1)[1].split("class RepairScope", 1)[0]
    assert "Return no verdict, liability percentage, remedy, payment" in block
    assert "_derive" not in block


def test_validators_independently_repeat_and_compare_effect():
    block = SOURCE.split("def _consensus", 1)[1].split("@gl.public.write", 1)[0]
    assert block.count("_classify(*args)") >= 2
    assert "_derive(_normalize(result.calldata)) == _derive" in block


def test_retry_precedes_mutation_and_reports_are_bounded():
    block = SOURCE.split("def assess_report", 1)[1].split("@gl.public.write", 1)[0]
    assert block.index('result["outcome"] == "RETRYABLE"') < block.index('self.report_statuses[report_id] = "FINALIZED"')
    assert "MAX_REPORTS_PER_PROPERTY" in SOURCE and "PENDING_REPORT_EXISTS" in SOURCE


def test_two_party_baseline_and_report_authority_exist():
    for marker in ("TENANT_ONLY", "OWNER_ONLY", "COUNTERPARTY_ONLY", "REPORTER_ONLY", "STALE_REPORT_REVISION"):
        assert marker in SOURCE
