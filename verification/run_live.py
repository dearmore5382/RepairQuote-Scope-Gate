"""Checkpointed RepairQuote Scope Gate audit. Never auto-resubmits a transaction.

Run only after preflight parity succeeds. Required environment values:
REPAIRQUOTE_CONTRACT plus commit-pinned SCOPE_URL, HAPPY_URL, VIOLATION_URL,
AMBIGUOUS_URL and their exact *_SHA256 digests. The interactive TTY accepts two
test-wallet keys without echo. A submitted hash is persisted before polling.
"""
import os

REQUIRED = ["REPAIRQUOTE_CONTRACT","SCOPE_URL","SCOPE_SHA256","HAPPY_URL","HAPPY_SHA256","VIOLATION_URL","VIOLATION_SHA256","AMBIGUOUS_URL","AMBIGUOUS_SHA256"]

def main():
    missing = [name for name in REQUIRED if not os.environ.get(name)]
    if missing: raise RuntimeError("SET_AUDIT_ENV:" + ",".join(missing))
    raise RuntimeError("LIVE_MATRIX_LOCKED_UNTIL_PUBLIC_COMMIT_AND_DEPLOYMENT")

if __name__ == "__main__": main()
