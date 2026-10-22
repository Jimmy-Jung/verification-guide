#!/usr/bin/env python3
# Author: JunyoungJung
# Date: 2026-10-22
"""공용 입력 코퍼스의 파일·바이트·SHA-256 목록(manifest)을 만들거나 검증한다.

정본 저장소에서 manifest를 만들고, 사본을 가진 저장소는 --check로 같은 파일인지 대조한다.
사본을 각자 고치면 결과 차이가 코드 때문인지 입력 때문인지 구분할 수 없으므로 CI에서 커밋마다 돌린다.

    fixtures_manifest.py <dir> [--out <dir>/manifest.json]      # 생성 (경로 기준 정렬)
    fixtures_manifest.py --check <dir> [--manifest <path>]      # 검증: 누락·추가·불일치가 있으면 종료 코드 1
    fixtures_manifest.py --self-test

종료 코드: 0 일치, 1 누락·추가·불일치, 2 입력 오류(폴더·manifest 없음, 깨진 manifest).

manifest 형식: [{"path": "spec/001.md", "bytes": 12, "sha256": "..."}] — path는 <dir> 기준 POSIX 상대경로.
건너뛰는 파일: manifest.json, README.md, .DS_Store, 숨김 폴더(.git 등).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import tempfile

SKIP_FILES = {"manifest.json", "README.md", ".DS_Store"}


def entries(base: pathlib.Path) -> list[dict]:
    out = []
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.name in SKIP_FILES:
            continue
        if any(part.startswith(".") for part in p.relative_to(base).parts):
            continue
        data = p.read_bytes()
        out.append({"path": p.relative_to(base).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return out


def generate(base: pathlib.Path, out: pathlib.Path) -> int:
    rows = entries(base)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{out}: {len(rows)} files")
    return 0


def check(base: pathlib.Path, manifest: pathlib.Path) -> int:
    if not manifest.is_file():
        print(f"manifest not found: {manifest}", file=sys.stderr)
        return 2
    try:
        expected = {row["path"]: row for row in json.loads(manifest.read_text(encoding="utf-8"))}
        if any("sha256" not in row for row in expected.values()):
            raise KeyError("sha256")
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"manifest를 읽을 수 없다: {manifest}: {error!r}", file=sys.stderr)
        return 2
    actual = {row["path"]: row for row in entries(base)}
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    mismatch = sorted(p for p in set(expected) & set(actual) if expected[p]["sha256"] != actual[p]["sha256"])
    for p in missing:
        print(f"missing   {p}")
    for p in extra:
        print(f"extra     {p}")
    for p in mismatch:
        print(f"mismatch  {p}")
    ok = not (missing or extra or mismatch)
    print(f"manifest check: {'OK' if ok else 'FAIL'} ({len(actual)} files, missing {len(missing)}, extra {len(extra)}, mismatch {len(mismatch)})")
    return 0 if ok else 1


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        base = pathlib.Path(tmp) / "fixtures"
        (base / "spec").mkdir(parents=True)
        (base / "spec" / "001.md").write_text("# a\n", encoding="utf-8")
        (base / "README.md").write_text("skip me", encoding="utf-8")
        manifest = base / "manifest.json"
        assert generate(base, manifest) == 0
        rows = json.loads(manifest.read_text(encoding="utf-8"))
        assert [r["path"] for r in rows] == ["spec/001.md"], rows
        assert check(base, manifest) == 0
        (base / "spec" / "001.md").write_text("# changed\n", encoding="utf-8")
        assert check(base, manifest) == 1
        (base / "spec" / "001.md").write_text("# a\n", encoding="utf-8")
        (base / "spec" / "002.md").write_text("extra", encoding="utf-8")
        assert check(base, manifest) == 1
        broken = base / "broken.json"
        broken.write_text('[{"path": "x"}]', encoding="utf-8")
        assert check(base, broken) == 2
        broken.write_text("not json", encoding="utf-8")
        assert check(base, broken) == 2
    print("self-test: OK")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", help="코퍼스 폴더")
    ap.add_argument("--out", help="생성할 manifest 경로 (기본 <dir>/manifest.json)")
    ap.add_argument("--check", metavar="DIR", help="검증할 코퍼스 폴더")
    ap.add_argument("--manifest", help="검증 기준 manifest (기본 <DIR>/manifest.json)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.check:
        base = pathlib.Path(args.check)
        return check(base, pathlib.Path(args.manifest) if args.manifest else base / "manifest.json")
    if not args.dir:
        ap.error("<dir> 또는 --check <dir> 가 필요하다")
    base = pathlib.Path(args.dir)
    if not base.is_dir():
        print(f"not a directory: {base}", file=sys.stderr)
        return 2
    return generate(base, pathlib.Path(args.out) if args.out else base / "manifest.json")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
