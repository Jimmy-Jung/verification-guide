# Author: JunyoungJung
# Date: 2026-10-22
"""매니페스트·스킬·문서가 서로 어긋나지 않는지 검사한다.

- 이름·버전이 plugin.json, marketplace.json, .codex-plugin, .agents, VERSION, CHANGELOG, SKILL.md에서 같다
- SKILL.md 는 500줄 미만, 링크한 파일이 모두 스킬 폴더 안에 있고 1단계 깊이다
- 스킬 폴더의 references·templates 는 전부 SKILL.md 에서 링크된다
- 에이전트용 파일은 docs/ 를 링크하지 않는다 (Codex 패키징에서 docs 가 빠진다)
- 사람용 도구 문서 5편이 도구마다 7개 하위 절 양식을 따르고, references/tools.md 에 같은 도구가 있다
- 공개 사본 금지 문자열이 docs/·skills/ 에 없다
- 모든 eval 케이스에 prompt.md 와 grader 가 있다
"""
import json
import re

import pytest

TOOL_GROUPS = {  # docs/tools/<묶음>.md → {도구 절 제목의 앞부분: references/tools.md 에 나타나야 하는 이름 조각}
    "ios-testing": {"Swift Testing": "Swift Testing", "XCTest": "XCTest", "XCUITest": "XCUITest", "xccov": "xccov",
                    "SwiftLint": "SwiftLint"},
    "ios-performance": {"XCTest 성능 지표": "XCTest metrics", "Instruments": "xctrace", "xcprof": "xcprof",
                        "AddressSanitizer": "AddressSanitizer", "ThreadSanitizer": "ThreadSanitizer"},
    "android-testing": {"JUnit": "JUnit", "AndroidX Test": "Espresso", "Accessibility Test Framework": "ATF",
                        "Kover": "Kover", "JaCoCo": "JaCoCo", "Android lint": "Android lint"},
    "android-performance": {"Jetpack Microbenchmark": "Microbenchmark", "Jetpack Macrobenchmark": "Macrobenchmark",
                            "dumpsys gfxinfo": "gfxinfo", "Perfetto": "Perfetto"},
    "common-security-quality": {"semgrep": "semgrep", "osv-scanner": "osv-scanner", "npm audit": "npm audit",
                                "cdxgen": "cdxgen", "lizard": "lizard", "scc": "scc"},
}
TOOL_SECTIONS = ["한눈에 보기", "무엇을 하는 도구인가", "왜 이 도구를 썼나", "준비", "사용 방법", "결과 읽는 법", "주의할 점·한계"]
FORBIDDEN = ["/Users/", "/Volumes/", "990EVO", "메가스터디", "@gmail", "megastudy"]
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def frontmatter(text: str) -> dict:
    assert text.startswith("---\n"), "frontmatter 없음"
    body = text.split("\n---\n", 1)[0][4:]
    out = {}
    for line in body.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            out[key.strip()] = value.strip().strip('"')
    return out


def test_names_and_versions_agree(root, skill):
    plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    codex = json.loads((root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    agents = json.loads((root / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    skill_meta = frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
    assert plugin["name"] == market["plugins"][0]["name"] == codex["name"] == agents["plugins"][0]["name"]
    assert skill_meta["name"] == skill.name
    assert plugin["displayName"] == codex["interface"]["displayName"] == agents["interface"]["displayName"]
    assert plugin["version"] == codex["version"] == agents["plugins"][0]["version"] == version
    assert f"## {version}" in (root / "CHANGELOG.md").read_text(encoding="utf-8")
    assert market["plugins"][0]["source"] == "./"
    for name in (plugin["name"], skill_meta["name"]):
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name)
    assert 0 < len(skill_meta["description"]) <= 1024


def test_skill_md_size_and_links(skill):
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 500
    linked = set()
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://")):
            continue
        path = (skill / target).resolve()
        assert path.is_file(), f"SKILL.md 링크 대상 없음: {target}"
        assert skill.resolve() in path.parents, f"스킬 폴더 밖 링크: {target}"
        assert len(path.relative_to(skill.resolve()).parts) == 2, f"1단계보다 깊은 링크: {target}"
        linked.add(path)
    for folder in ("references", "templates"):
        for file in (skill / folder).iterdir():
            assert file.resolve() in linked, f"SKILL.md 에서 링크되지 않음: {file.relative_to(skill)}"


def test_agent_files_do_not_link_docs(skill):
    for file in [skill / "SKILL.md", *(skill / "references").glob("*.md")]:
        for target in LINK.findall(file.read_text(encoding="utf-8")):
            assert not target.startswith(("docs/", "../docs", "../../docs")), f"{file.name}: docs/ 링크 {target}"


def test_long_references_have_toc(skill):
    for file in (skill / "references").glob("*.md"):
        text = file.read_text(encoding="utf-8")
        if len(text.splitlines()) > 100:
            assert "## 차례" in text, f"{file.name}: 100줄 넘는데 차례 없음"


def tool_sections(text: str) -> dict[str, tuple[str, str]]:
    """`## N. 도구 — 설명` 절마다 (번호, 본문)."""
    out = {}
    text = re.sub(r"^```.*?^```", "", text, flags=re.M | re.S)  # 코드 블록 안의 `## …` 줄은 제목이 아니다
    for match in re.finditer(r"^## (\d+)\. (.+?)\n(.*?)(?=^## |\Z)", text, re.M | re.S):
        out[match.group(2)] = (match.group(1), match.group(3))
    return out


@pytest.mark.parametrize("group", sorted(TOOL_GROUPS))
def test_tool_group_follows_template(root, group):
    path = root / "docs" / "tools" / f"{group}.md"
    assert path.is_file(), f"도구 문서 없음: {path.relative_to(root)}"
    text = path.read_text(encoding="utf-8")
    meta = frontmatter(text)
    assert meta.get("author") and meta.get("created")
    assert "## 1. 들어가며" in text and "## 참고문헌" in text
    assert "<!--" not in text, f"{group}: 채우지 않은 자리표시 주석이 남음"
    sections = tool_sections(text)
    for prefix in TOOL_GROUPS[group]:
        found = [(title, body) for title, body in sections.items() if title.startswith(prefix)]
        assert found, f"{group}: '{prefix}' 도구 절 없음"
        number, body = sections[found[0][0]]
        for k, name in enumerate(TOOL_SECTIONS, start=1):
            assert re.search(rf"^### {number}\.{k} {re.escape(name)}$", body, re.M), f"{group}/{prefix}: {number}.{k} {name} 없음"


def test_tool_groups_match_reference_table(root, skill):
    table = (skill / "references" / "tools.md").read_text(encoding="utf-8")
    for group, tools in TOOL_GROUPS.items():
        for prefix, name in tools.items():
            assert name in table, f"references/tools.md 에 {name}({group}/{prefix}) 없음"
    files = {p.stem for p in (root / "docs" / "tools").glob("*.md")}
    assert files == set(TOOL_GROUPS), f"도구 문서 목록이 다름: {sorted(files ^ set(TOOL_GROUPS))}"


PUBLIC_EMAIL_FILES = {".claude-plugin/plugin.json", ".codex-plugin/plugin.json"}  # 작성자 공개 주소는 매니페스트에만 둔다


def test_no_private_strings(root):
    offenders = []
    skip_dirs = {".git", "results", "__pycache__", ".pytest_cache"}
    for file in root.rglob("*"):
        rel = file.relative_to(root).as_posix()
        if not file.is_file() or skip_dirs & set(file.relative_to(root).parts) or rel == "tests/test_plugin_consistency.py":
            continue
        if file.suffix not in {".md", ".csv", ".py", ".json", ".yaml", ".yml", ".txt", ".ini"} and file.name != ".gitignore":
            continue
        text = file.read_text(encoding="utf-8", errors="replace")
        for word in FORBIDDEN:
            if word in text and not (word == "@gmail" and rel in PUBLIC_EMAIL_FILES):
                offenders.append(f"{rel}: {word}")
    assert not offenders, "\n".join(offenders)


def test_eval_cases_have_prompt_and_grader(root):
    cases = [p for p in (root / "evals").iterdir() if p.is_dir() and p.name not in {"results", "mocks"}]
    assert cases, "eval 케이스 없음"
    for case in cases:
        assert (case / "prompt.md").is_file(), f"{case.name}: prompt.md 없음"
        graders = list((case / "graders").glob("*.md"))
        assert graders, f"{case.name}: grader 없음"
        for grader in graders:
            assert "type:" in frontmatter(grader.read_text(encoding="utf-8")) or "type:" in grader.read_text(encoding="utf-8")


@pytest.mark.parametrize("doc", ["README.md", "evals/README.md"])
def test_relative_links_resolve(root, doc):
    path = root / doc
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        assert (path.parent / target).exists(), f"{doc}: 깨진 링크 {target}"


def test_docs_relative_links_resolve(root):
    broken = []
    for file in (root / "docs").rglob("*.md"):
        for target in LINK.findall(file.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (file.parent / target).exists():
                broken.append(f"{file.relative_to(root)} → {target}")
    assert not broken, "\n".join(broken)


def github_slug(heading: str) -> str:
    """GitHub 제목 앵커 규칙: 소문자, 글자·숫자·밑줄·하이픈·공백 외 제거, 공백은 하이픈."""
    text = re.sub(r"`([^`]*)`", r"\1", heading.strip().lower())
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def anchors_of(path) -> set[str]:
    found, seen, fence = set(), {}, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        found.update(re.findall(r'<a id="([^"]+)"', line))
        match = re.match(r"^#{1,6} (.+?)\s*#*$", line)
        if match:
            slug = github_slug(match.group(1))
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            found.add(slug if count == 0 else f"{slug}-{count}")
    return found


def test_anchor_links_resolve(root):
    docs = [root / "README.md", *(p for p in (root / "docs").rglob("*.md") if not p.name.endswith(".excalidraw.md"))]
    broken = []
    for file in docs:
        for target in re.findall(r"\]\(([^)\s]*#[^)\s]+)\)", file.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://")):
                continue
            path_part, anchor = target.split("#", 1)
            dest = (file.parent / path_part) if path_part else file
            if dest.suffix == ".md" and dest.exists() and anchor not in anchors_of(dest):
                broken.append(f"{file.relative_to(root)} → {target}")
    assert not broken, "\n".join(broken)


def test_screenshots_are_referenced(root):
    """docs/assets/screenshots 의 그림은 모두 어느 문서에서 쓰이고, 문서가 가리키는 그림은 모두 있다."""
    folder = root / "docs" / "assets" / "screenshots"
    text = "\n".join(p.read_text(encoding="utf-8") for p in (root / "docs").rglob("*.md"))
    files = {p.name for p in folder.glob("*.png")}
    referenced = set(re.findall(r"assets/screenshots/([\w.-]+\.png)", text))
    assert files == referenced, f"쓰지 않는 그림 {sorted(files - referenced)}, 없는 그림 {sorted(referenced - files)}"

