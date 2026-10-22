#!/usr/bin/env python3
# Author: JunyoungJung
# Date: 2026-10-22
"""테스트 로그의 `BENCH <metric> <value> <unit>` 줄을 모아 metric별 통계를 results.json으로 쓴다.

벤치마크 테스트가 반복마다 한 줄씩 아래 형식으로 출력하면 플랫폼·언어와 무관하게 집계할 수 있다.
    BENCH parse.50KiB 11.52 ms
    BENCH parse.50KiB 11700000 ns
    BENCH footprint.peak 182000000 byte
단위 변환: ns → ms, us → ms, byte → kB(1000 byte). 같은 metric은 변환 뒤 같은 단위여야 한다.
통계: n, median, p90(최근접 순위), min, max, stdev(n ≥ 2). 대표값은 중앙값이고 범위(min–max)를 함께 싣는다.

    bench_collect.py <log>... --out results.json [--label "iPad Pro 11 (M5) · Release"] [--table]
    bench_collect.py --self-test

종료 코드: 0 성공, 1 BENCH 줄이 없음, 2 입력 오류(파일 없음, 같은 지표의 단위가 섞임).

xcresult·Gradle 보고서는 먼저 텍스트 로그로 내보낸다(예: `xcrun xcresulttool get log --type action`).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics
import sys
import tempfile

LINE = re.compile(r"^\s*BENCH\s+(\S+)\s+(-?\d+(?:\.\d+)?)\s+(\S+)\s*$")
CONVERT = {"ns": ("ms", 1e-6), "us": ("ms", 1e-3), "ms": ("ms", 1.0), "s": ("s", 1.0),
           "byte": ("kB", 1e-3), "bytes": ("kB", 1e-3), "kB": ("kB", 1.0), "MB": ("MB", 1.0)}


def parse_lines(text: str) -> dict[str, tuple[str, list[float]]]:
    metrics: dict[str, tuple[str, list[float]]] = {}
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        name, value, unit = m.group(1), float(m.group(2)), m.group(3)
        unit_out, factor = CONVERT.get(unit, (unit, 1.0))
        if name in metrics and metrics[name][0] != unit_out:
            raise ValueError(f"{name}: 단위가 섞였다 ({metrics[name][0]} vs {unit_out})")
        metrics.setdefault(name, (unit_out, []))[1].append(value * factor)
    return metrics


def p90(values: list[float]) -> float:
    ordered = sorted(values)
    index = -(-9 * len(ordered) // 10) - 1  # 최근접 순위: ceil(0.9·n)번째 값(1부터 셈). round()는 짝수 쪽으로 반올림해 n=10에서 한 칸 밀린다
    return ordered[index]


def summarize(metrics: dict[str, tuple[str, list[float]]]) -> dict[str, dict]:
    out = {}
    for name, (unit, values) in sorted(metrics.items()):
        out[name] = {
            "unit": unit, "n": len(values),
            "median": statistics.median(values), "p90": p90(values),
            "min": min(values), "max": max(values),
            "stdev": statistics.stdev(values) if len(values) >= 2 else 0.0,
        }
    return out


def table(results: dict[str, dict]) -> str:
    rows = ["| metric | unit | n | median | p90 | min | max |", "|---|---|---:|---:|---:|---:|---:|"]
    for name, r in results.items():
        rows.append(f"| {name} | {r['unit']} | {r['n']} | {r['median']:.3g} | {r['p90']:.3g} | {r['min']:.3g} | {r['max']:.3g} |")
    return "\n".join(rows)


def self_test() -> int:
    text = "noise\nBENCH parse.50KiB 10 ms\nBENCH parse.50KiB 12000000 ns\nBENCH parse.50KiB 30 ms\nBENCH mem.peak 1500 byte\n"
    results = summarize(parse_lines(text))
    r = results["parse.50KiB"]
    assert (r["unit"], r["n"], r["median"], r["min"], r["max"]) == ("ms", 3, 12.0, 10.0, 30.0), r
    assert r["p90"] == 30.0, r
    for n, rank in ((10, 9), (20, 18), (30, 27), (1, 1)):  # ceil(0.9·n)
        assert p90([float(i) for i in range(1, n + 1)]) == rank, (n, p90([float(i) for i in range(1, n + 1)]))
    assert results["mem.peak"]["unit"] == "kB" and results["mem.peak"]["median"] == 1.5, results["mem.peak"]
    try:
        parse_lines("BENCH x 1 ms\nBENCH x 1 byte\n")
    except ValueError:
        pass
    else:
        raise AssertionError("단위 혼용을 잡아야 한다")
    with tempfile.TemporaryDirectory() as tmp:
        log = pathlib.Path(tmp) / "a.log"
        log.write_text(text, encoding="utf-8")
        out = pathlib.Path(tmp) / "results.json"
        assert main([str(log), "--out", str(out), "--label", "test"]) == 0
        doc = json.loads(out.read_text(encoding="utf-8"))
        assert doc["label"] == "test" and "parse.50KiB" in doc["metrics"], doc
        mixed = pathlib.Path(tmp) / "mixed.log"
        mixed.write_text("BENCH x 1 ms\nBENCH x 1 byte\n", encoding="utf-8")
        assert main([str(mixed), "--out", str(out)]) == 2
    print("self-test: OK")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logs", nargs="*", type=pathlib.Path)
    ap.add_argument("--out")
    ap.add_argument("--label", default="")
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.logs:
        ap.error("로그 파일이 필요하다")
    missing = [str(p) for p in args.logs if not p.is_file()]
    if missing:
        print("not found: " + ", ".join(missing), file=sys.stderr)
        return 2
    merged: dict[str, tuple[str, list[float]]] = {}
    for log in args.logs:
        try:
            parsed = parse_lines(log.read_text(encoding="utf-8", errors="replace"))
        except ValueError as error:  # 한 로그 안에서 단위가 섞였다: 입력 오류(2)
            print(f"{log}: {error}", file=sys.stderr)
            return 2
        for name, (unit, values) in parsed.items():
            if name in merged and merged[name][0] != unit:
                print(f"{name}: 단위가 섞였다", file=sys.stderr)
                return 2
            merged.setdefault(name, (unit, []))[1].extend(values)
    if not merged:
        print("BENCH 줄이 없다", file=sys.stderr)
        return 1
    results = summarize(merged)
    doc = {"label": args.label, "sources": [str(p) for p in args.logs], "metrics": results}
    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{args.out}: {len(results)} metrics")
    if args.table or not args.out:
        print(table(results))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
