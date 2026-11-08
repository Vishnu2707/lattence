#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"

command -v uv >/dev/null 2>&1 || {
  echo "uv is required" >&2
  exit 2
}

work=$(mktemp -d "${TMPDIR:-/tmp}/lattence-verify.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM

expected_tests=390
expected_coverage=92

echo "==> Synchronizing the workspace"
uv sync --all-packages --dev

echo "==> Reproducing the vulnerable-agent report"
uv run lattence scan examples/vulnerable-agent \
  --offline --no-color --fail-on none --out "$work/report" \
  >"$work/scan.log"
cat "$work/scan.log"

echo "==> Reproducing cross-layer correlations"
uv run lattence graph chain examples/vulnerable-agent \
  --offline --no-color --out "$work/chain" \
  >"$work/chain.log"
cat "$work/chain.log"

uv run python - "$work/report/lattence-report.json" \
  "$work/report/lattence-report.html" "$work/scan.log" "$work/chain.log" <<'PY'
import json
import sys
from pathlib import Path

json_path, html_path, scan_path, chain_path = map(Path, sys.argv[1:])
report = json.loads(json_path.read_text(encoding="utf-8"))
scan = scan_path.read_text(encoding="utf-8")
chain = chain_path.read_text(encoding="utf-8")

actual = {
    "nodes": len(report["graph"]["nodes"]),
    "edges": len(report["graph"]["edges"]),
    "findings": len(report["findings"]),
    "pqc_readiness": report["summary"]["pqc_readiness"],
}
expected = {"nodes": 24, "edges": 92, "findings": 13, "pqc_readiness": 21.0}
if actual != expected:
    raise SystemExit(f"report mismatch: expected {expected}, got {actual}")
if "Attack paths           92" not in scan:
    raise SystemExit("scan output did not contain 92 attack paths")
if "32 finding correlations across 9 distinct structural paths" not in chain:
    raise SystemExit("cross-layer output did not contain 32 correlations and 9 paths")

json_size = json_path.stat().st_size
html_size = html_path.stat().st_size
size_ceiling = 1_000_000
if json_size >= size_ceiling or html_size >= size_ceiling:
    raise SystemExit(
        f"report size ceiling exceeded: JSON={json_size}, HTML={html_size}"
    )

print("Verified findings: 13")
print("Verified attack paths: 92")
print("Verified cross-layer correlations: 32")
print("Verified distinct structural paths: 9")
print("Verified PQC readiness: 21%")
print(f"Measured JSON report size: {json_size} bytes")
print(f"Measured HTML report size: {html_size} bytes")
print(f"Verified report size ceiling: both files below {size_ceiling} bytes")
PY

echo "==> Running the full test and coverage suite"
uv run pytest --cov --cov-report=term >"$work/pytest.log" 2>&1
cat "$work/pytest.log"

test_count=$(sed -n 's/.*= \([0-9][0-9]*\) passed.*/\1/p' "$work/pytest.log" | tail -n 1)
coverage=$(awk '/^TOTAL / {value=$NF; gsub(/%/, "", value); print value}' "$work/pytest.log")

if [ "$test_count" != "$expected_tests" ]; then
  echo "test count mismatch: expected $expected_tests, got ${test_count:-missing}" >&2
  exit 1
fi
if [ "$coverage" != "$expected_coverage" ]; then
  echo "coverage mismatch: expected $expected_coverage%, got ${coverage:-missing}%" >&2
  exit 1
fi

echo "Verified tests: $test_count passed"
echo "Verified coverage: $coverage%"
echo "Release verification passed"
