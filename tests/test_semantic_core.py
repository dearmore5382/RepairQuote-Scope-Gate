import ast
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "contracts" / "RepairScope.py").read_text(encoding="utf-8")


def core():
    tree = ast.parse(SOURCE)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {"_unavailable", "_normalize", "_derive"}]
    class UserError(Exception): pass
    class VM: pass
    VM.UserError = UserError
    class GL: pass
    GL.vm = VM
    namespace = {"typing": __import__("typing"), "gl": GL}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "core", "exec"), namespace)
    return namespace


C = core()


def obs(**changes):
    value = {"analysis_status": "AVAILABLE", "baseline_relation": "NEW_DAMAGE", "damage_character": "NEGLECT", "duty_alignment": "TENANT", "account_consistency": "CONSISTENT"}
    value.update(changes)
    return value


def test_every_outcome_and_precedence():
    derive = C["_derive"]
    assert derive(C["_unavailable"]())["outcome"] == "RETRYABLE"
    assert derive(obs(account_consistency="CONFLICTING", baseline_relation="PRE_EXISTING"))["outcome"] == "INSUFFICIENT_EVIDENCE"
    assert derive(obs(baseline_relation="AMBIGUOUS"))["reason"] == "BASELINE_RELATION_UNCLEAR"
    assert derive(obs(baseline_relation="PRE_EXISTING", damage_character="MISUSE"))["outcome"] == "OWNER_RESPONSIBLE"
    assert derive(obs(damage_character="NORMAL_WEAR"))["outcome"] == "NORMAL_WEAR"
    assert derive(obs(damage_character="SYSTEM_FAILURE", duty_alignment="OWNER"))["outcome"] == "OWNER_RESPONSIBLE"
    assert derive(obs(damage_character="MISUSE", duty_alignment="TENANT"))["outcome"] == "TENANT_RESPONSIBLE"
    assert derive(obs(damage_character="ACCIDENT", duty_alignment="OWNER"))["outcome"] == "SHARED_RESPONSIBILITY"
    assert derive(obs(damage_character="NEGLECT", duty_alignment="OWNER"))["outcome"] == "OWNER_RESPONSIBLE"


def test_contradictions_fail_closed():
    derive = C["_derive"]
    assert derive(obs(damage_character="SYSTEM_FAILURE", duty_alignment="TENANT"))["outcome"] == "INSUFFICIENT_EVIDENCE"
    assert derive(obs(damage_character="MISUSE", duty_alignment="OWNER"))["outcome"] == "INSUFFICIENT_EVIDENCE"
    assert derive(obs(duty_alignment="CONFLICT"))["outcome"] == "INSUFFICIENT_EVIDENCE"


def test_schema_is_exact_and_closed():
    normalize = C["_normalize"]
    assert normalize(obs()) == obs()
    invalid = [dict(obs(), verdict="OWNER_RESPONSIBLE"), {key: value for key, value in obs().items() if key != "duty_alignment"}, obs(damage_character="BROKEN")]
    for item in invalid:
        try:
            normalize(item)
            raise AssertionError("invalid observation accepted")
        except Exception:
            pass
