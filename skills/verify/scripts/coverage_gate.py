#!/usr/bin/env python3
# Author: JunyoungJung
# Date: 2026-10-22
"""줄 커버리지 보고서에서 모듈별·전체 비율을 계산하고 기준 미달이면 종료 코드 1로 끝난다.

입력 형식 두 가지를 확장자로 구분한다.
  *.json  xccov JSON (`xcrun xccov view --report --json <xcresult>`): targets[].files[].{path, coveredLines, executableLines}
          모듈 = 경로에서 `--source-root`(기본 Sources) 바로 다음 폴더 이름. 같은 소스가 여러 테스트 번들에 정적 링크되어
          중복으로 나타나므로 파일별 최대값을 쓴다. `/checkouts/`(의존성) 경로는 제외.
  *.xml   JaCoCo/Kover XML (`koverXmlReport`, `jacocoTestReport`): report > package > sourcefile > counter[type=LINE]
          모듈 = report 의 name 속성(Gradle 모듈마다 보고서가 따로 나온다). 여러 XML을 넘기면 모듈이 여러 개가 된다.

    coverage_gate.py <report>... [--module NAME=RATIO]... [--total RATIO] [--source-root Sources] [--json out.json]
    coverage_gate.py --self-test

종료 코드: 0 통과, 1 기준 미달(지정한 모듈이 보고서에 없을 때 포함), 2 입력 오류(파일 없음, 깨진 보고서, 모듈을 하나도 찾지 못함).
기준값은 비율로 쓴다(80%는 0.80). 1보다 큰 값은 거부한다.

기준값에는 근거를 적어 둔다: 핵심 모듈(모든 입력이 지나가는 파서·코어)은 호스트에서 빠르게 테스트할 수 있어 높은 기준을
유지하기 쉬우므로 90%, 전체는 UI·플랫폼 글루를 포함해 80%가 흔한 출발점이다. 커버리지는 "테스트가 닿지 않은 곳"을
찾는 지표이지 결과가 맞다는 근거가 아니다.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict


def modules_from_xccov(path: pathlib.Path, source_root: str) -> dict[str, list[int]]:
    report = json.loads(path.read_text(encoding="utf-8"))
    marker = f"/{source_root}/"
    best: dict[str, tuple[int, int, str]] = {}
    for target in report.get("targets", []):
        for entry in target.get("files", []):
            file_path = entry.get("path", "")
            if marker not in file_path or "/checkouts/" in file_path:
                continue
            covered, executable = entry.get("coveredLines", 0), entry.get("executableLines", 0)
            module = file_path.split(marker, 1)[1].split("/", 1)[0]
            if file_path not in best or covered > best[file_path][0]:
                best[file_path] = (covered, executable, module)
    modules: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for covered, executable, module in best.values():
        modules[module][0] += covered
        modules[module][1] += executable
    return dict(modules)


def modules_from_jacoco(path: pathlib.Path) -> dict[str, list[int]]:
    root = ET.parse(path).getroot()  # nosemgrep: python.lang.security.use-defused-xml-parse.use-defused-xml-parse — 로컬 빌드 산출물만 읽는다
    name = root.get("name") or path.stem
    covered = missed = 0
    for sourcefile in root.iter("sourcefile"):
        for counter in sourcefile.findall("counter"):
            if counter.get("type") == "LINE":
                covered += int(counter.get("covered", 0))
                missed += int(counter.get("missed", 0))
    return {name: [covered, covered + missed]}


def collect(reports: list[pathlib.Path], source_root: str) -> dict[str, list[int]]:
    modules: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for report in reports:
        found = modules_from_xccov(report, source_root) if report.suffix == ".json" else modules_from_jacoco(report)
        for module, (covered, executable) in found.items():
            modules[module][0] += covered
            modules[module][1] += executable
    return dict(modules)


def evaluate(modules: dict[str, list[int]], gates: dict[str, float], total_gate: float | None) -> tuple[dict, list[str]]:
    rows = {m: {"covered": c, "executable": e, "ratio": c / e if e else 0.0} for m, (c, e) in sorted(modules.items())}
    total_c = sum(c for c, _ in modules.values())
    total_e = sum(e for _, e in modules.values())
    rows["TOTAL"] = {"covered": total_c, "executable": total_e, "ratio": total_c / total_e if total_e else 0.0}
    failures = []
    for module, gate in gates.items():
        if module not in modules:
            failures.append(f"{module}: 보고서에 없음")
        elif rows[module]["ratio"] < gate:
            failures.append(f"{module} {rows[module]['ratio']:.1%} < {gate:.0%}")
    if total_gate is not None and rows["TOTAL"]["ratio"] < total_gate:
        failures.append(f"TOTAL {rows['TOTAL']['ratio']:.1%} < {total_gate:.0%}")
    return rows, failures


def ratio_arg(text: str) -> float:
    ratio = float(text)
    if not 0 < ratio <= 1:
        raise argparse.ArgumentTypeError(f"기준값은 0보다 크고 1 이하인 비율이다(80%는 0.80): {text}")
    return ratio


def parse_gate(text: str) -> tuple[str, float]:
    name, _, value = text.partition("=")
    if not value:
        raise argparse.ArgumentTypeError(f"--module 은 NAME=RATIO 형식이다: {text}")
    ratio = float(value)
    if not 0 < ratio <= 1:
        raise argparse.ArgumentTypeError(f"기준값은 0보다 크고 1 이하인 비율이다(80%는 0.80): {text}")
    return name, ratio


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        base = pathlib.Path(tmp)
        xccov = {"targets": [
            {"files": [{"path": "/r/Sources/Core/A.swift", "coveredLines": 90, "executableLines": 100},
                       {"path": "/r/Sources/UI/B.swift", "coveredLines": 50, "executableLines": 100},
                       {"path": "/r/.build/checkouts/dep/Sources/Dep/C.swift", "coveredLines": 0, "executableLines": 100}]},
            {"files": [{"path": "/r/Sources/Core/A.swift", "coveredLines": 95, "executableLines": 100}]},
        ]}
        (base / "cov.json").write_text(json.dumps(xccov), encoding="utf-8")
        (base / "core.xml").write_text(
            '<report name="core"><package name="x"><sourcefile name="A.kt">'
            '<counter type="LINE" missed="10" covered="90"/></sourcefile></package></report>', encoding="utf-8")
        modules = collect([base / "cov.json"], "Sources")
        assert modules == {"Core": [95, 100], "UI": [50, 100]}, modules  # 파일별 최대값, checkouts 제외
        rows, failures = evaluate(modules, {"Core": 0.9}, 0.8)
        assert not [f for f in failures if f.startswith("Core")], failures
        assert any(f.startswith("TOTAL") for f in failures), failures  # 145/200 = 72.5% < 80%
        modules = collect([base / "core.xml"], "Sources")
        assert modules == {"core": [90, 100]}, modules
        _, failures = evaluate(modules, {"core": 0.95}, None)
        assert failures == ["core 90.0% < 95%"], failures
        _, failures = evaluate(modules, {"missing": 0.5}, None)
        assert failures == ["missing: 보고서에 없음"], failures
        (base / "broken.json").write_text("{not json", encoding="utf-8")
        assert main([str(base / "broken.json")]) == 2
        (base / "empty.json").write_text('{"targets": []}', encoding="utf-8")
        assert main([str(base / "empty.json"), "--total", "0.8"]) == 2
        try:
            parse_gate("core=80")
        except argparse.ArgumentTypeError:
            pass
        else:
            raise AssertionError("80 같은 퍼센트 값을 거부해야 한다")
    print("self-test: OK")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reports", nargs="*", type=pathlib.Path)
    ap.add_argument("--module", action="append", type=parse_gate, default=[], metavar="NAME=RATIO")
    ap.add_argument("--total", type=ratio_arg)
    ap.add_argument("--source-root", default="Sources")
    ap.add_argument("--json")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.reports:
        ap.error("커버리지 보고서 경로가 필요하다")
    missing = [str(r) for r in args.reports if not r.is_file()]
    if missing:
        print("not found: " + ", ".join(missing), file=sys.stderr)
        return 2
    try:
        modules = collect(args.reports, args.source_root)
    except (json.JSONDecodeError, ET.ParseError, UnicodeDecodeError, AttributeError, TypeError) as error:
        print(f"커버리지 보고서를 읽을 수 없다: {error}", file=sys.stderr)
        return 2
    if not modules:
        print(f"보고서에서 모듈을 찾지 못했다(xccov는 경로에 /{args.source_root}/ 가 있어야 한다)", file=sys.stderr)
        return 2
    rows, failures = evaluate(modules, dict(args.module), args.total)
    for name, r in rows.items():
        print(f"{name:28} {r['covered']:7}/{r['executable']:7}  {r['ratio']:6.1%}")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print("coverage gate:", "FAIL — " + ", ".join(failures) if failures else "OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
