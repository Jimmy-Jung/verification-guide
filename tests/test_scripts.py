# Author: JunyoungJung
# Date: 2026-10-22
"""스크립트 3종의 self-test와 종료 코드 계약."""
import json
import subprocess
import sys

import pytest

SCRIPTS = ["fixtures_manifest.py", "coverage_gate.py", "bench_collect.py"]


def run(skill, script, *args, **kw):
    return subprocess.run([sys.executable, "-B", "-I", str(skill / "scripts" / script), *args],
                          capture_output=True, text=True, **kw)


@pytest.mark.parametrize("script", SCRIPTS)
def test_self_test_passes(skill, script):
    result = run(skill, script, "--self-test")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "self-test: OK" in result.stdout


def test_manifest_generate_then_check(skill, tmp_path):
    corpus = tmp_path / "fixtures"
    (corpus / "spec").mkdir(parents=True)
    (corpus / "spec" / "a.md").write_text("# a\n", encoding="utf-8")
    assert run(skill, "fixtures_manifest.py", str(corpus)).returncode == 0
    rows = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    assert rows[0]["path"] == "spec/a.md" and rows[0]["bytes"] == 4
    assert run(skill, "fixtures_manifest.py", "--check", str(corpus)).returncode == 0
    (corpus / "spec" / "a.md").write_text("# b\n", encoding="utf-8")
    result = run(skill, "fixtures_manifest.py", "--check", str(corpus))
    assert result.returncode == 1 and "mismatch  spec/a.md" in result.stdout


def test_coverage_gate_exit_codes(skill, tmp_path):
    report = tmp_path / "cov.json"
    report.write_text(json.dumps({"targets": [{"files": [
        {"path": "/r/Sources/Core/A.swift", "coveredLines": 85, "executableLines": 100}]}]}), encoding="utf-8")
    assert run(skill, "coverage_gate.py", str(report), "--module", "Core=0.8").returncode == 0
    failed = run(skill, "coverage_gate.py", str(report), "--module", "Core=0.9")
    assert failed.returncode == 1 and "FAIL" in failed.stdout
    assert run(skill, "coverage_gate.py", str(tmp_path / "missing.json")).returncode == 2


def test_bench_collect_table(skill, tmp_path):
    log = tmp_path / "bench.log"
    log.write_text("BENCH parse.1KiB 1.0 ms\nBENCH parse.1KiB 3.0 ms\n", encoding="utf-8")
    result = run(skill, "bench_collect.py", str(log), "--table")
    assert result.returncode == 0 and "| parse.1KiB | ms | 2 | 2 |" in result.stdout
    assert run(skill, "bench_collect.py", str(tmp_path / "none.log")).returncode == 2
