#!/usr/bin/env python3
"""검증 가이드 그림 빌드: 도식 11장(Excalidraw 원본 → SVG + 검수 PNG)과 그래프 2장(PNG).

Author: JunyoungJung
Date: 2026-10-22

paper-figures 스킬의 헬퍼(paper_kit · chart_style)를 쓴다. 헬퍼 위치는 PAPER_FIGURES_SCRIPTS 환경 변수,
없으면 ~/.claude/skills/paper-figures/scripts 순으로 찾는다.

    python3 docs/assets/build_figures.py --make-data                 # 가상 데이터 CSV를 시드 고정으로 다시 쓴다
    python3 docs/assets/build_figures.py --renders <검수 PNG 폴더>   # 도식 11장 + 그래프 2장

산출물: figures/src/<slug>.excalidraw.md(원본) · figures/<slug>.svg · figures/vg-chart-*.png,
검수 PNG는 --renders 폴더(저장소 밖)에 둔다. 한 장이라도 없으면 실패한다.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, os.environ.get("PAPER_FIGURES_SCRIPTS", str(Path.home() / ".claude" / "skills" / "paper-figures" / "scripts")))

from chart_style import (BLUE, INK, INK_2, MUTED, NEUTRAL, ORANGE, ORANGE_RAMP, WIDTH_IN, bar_axis, column_axis,  # noqa: E402
                         hline_ref, plt, read_csv, save, setup_style, top_label, vline_ref)
from paper_kit import (BLACK, CHIP, NAVY, NOTE, REGION_STROKE, WEAK, Diagram, brief, build_all, decision, ellipse, flow,  # noqa: E402
                       lane, legend_rows, marker, new_diagram, node, note, region, render_png, rule, task)

ASSETS = Path(__file__).resolve().parent
FIGURES = ASSETS / "figures"
SOURCES = FIGURES / "src"
DATA = ASSETS / "data"
SEED = 20261022
WHITE_RECT = '<rect width="100%" height="100%" fill="#ffffff"/>'


# ================================================================ 도식

def modes(out: Path) -> Diagram:
    d = new_diagram("vg-01-modes", "검증의 네 단계",
                    brief(claim="검증은 계획→실행→해석→보고 순서로 진행하고, 해석에서 측정 방법이 의심되면 실행으로 돌아가며, "
                                "보고의 남은 조건은 다음 계획의 입력이 된다.",
                          span="계획에서 보고까지, 다시 다음 계획으로", flow="왼쪽에서 오른쪽, 되돌아감은 아래 파선",
                          change="질문 → 측정값 → 판단 → 보고서", actors="계획 · 실행 · 해석 · 보고", caption="검증 단계"), out)
    xs = [40, 340, 640, 940]
    labels = ["계획", "실행", "해석", "보고"]
    memos = ["네 질문 · 요구사항 · 결정", "입력 모음 · 측정 · 결함 대장", "해석 원칙 · 측정 함정", "보고서 · 부록 · 남은 조건"]
    for i, (x, label, memo) in enumerate(zip(xs, labels, memos)):
        node(d, f"m{i}", x, 60, 240, 80, label, emph=(label == "해석"), size=17)
        note(d, memo, x + 120, 152, size=13, align="center")
        if i < 3:
            flow(d, f"a{i}", x + 240, 100, [[0, 0], [60, 0]])
    # 되돌아감은 상자 밑변 가장자리에서 출발·도착해 아래 메모를 피한다(끝점은 상자 밑변 y=140).
    flow(d, "back", 655, 140, [[0, 0], [0, 70], [-90, 70], [-90, 0]], style="dashed")
    note(d, "측정 방법이 의심되면 다시 측정", 610, 218, size=13, align="center")
    flow(d, "next", 1165, 140, [[0, 0], [0, 130], [-1110, 130], [-1110, 0]], style="dashed")
    note(d, "남은 조건 → 다음 계획", 610, 278, size=13, align="center")
    note(d, "실선: 진행 순서 · 파선: 되돌아감", 40, 320, size=13, color=WEAK)
    return d


def number_pipeline(out: Path) -> Diagram:
    d = new_diagram("vg-02-number-pipeline", "수치의 단일 출처",
                    brief(claim="원시 결과는 집계 스크립트를 거쳐 CSV 한 벌로 모이고, 그래프·표·파생본은 모두 그 CSV에서만 나온다. "
                                "본문 숫자를 직접 고치는 경로는 없다.",
                          span="원시 결과 파일에서 보고서 3종까지", flow="왼쪽에서 오른쪽, 팬인 뒤 팬아웃",
                          change="JSON·보고서·대장 → CSV → 그래프·표 → 문서", actors="집계 스크립트 · 그래프 스크립트 · 표",
                          caption="수치 파이프라인"), out)
    region(d, "in", 40, 40, 260, 440, "입력 (원시 결과)")
    inputs = ["벤치마크 결과 JSON", "커버리지 보고서", "정적 분석 결과", "결함 대장", "트레이스"]
    agg_y = 267
    for i, label in enumerate(inputs):
        y = 95 + i * 72
        node(d, f"in{i}", 60, y, 220, 56, label, size=14)
        flow(d, f"fi{i}", 280, y + 28, [[0, 0], [40, 0], [40, agg_y - y - 28], [80, agg_y - y - 28]])
    region(d, "tx", 340, 40, 560, 440, "변환 (스크립트)")
    node(d, "agg", 360, 232, 140, 70, "집계 스크립트", size=14)
    node(d, "csv", 540, 232, 140, 70, "CSV 한 벌", emph=True, size=16)
    note(d, "수치의 단일 출처", 610, 312, size=13, align="center")
    flow(d, "f1", 500, agg_y, [[0, 0], [40, 0]])
    node(d, "chart", 730, 92, 150, 70, "그래프 스크립트", size=14)
    node(d, "table", 730, 342, 150, 90, "표\nCSV에서 옮기고\n출처 표기", size=14)
    flow(d, "f2", 680, agg_y, [[0, 0], [25, 0], [25, 127 - agg_y], [50, 127 - agg_y]])
    flow(d, "f3", 680, agg_y, [[0, 0], [25, 0], [25, 387 - agg_y], [50, 387 - agg_y]])
    rule(d, "bus", 880, 127, [[0, 0], [30, 0], [30, 260]])
    rule(d, "bus2", 880, 387, [[0, 0], [30, 0]])
    region(d, "outr", 920, 40, 300, 440, "산출")
    for i, label in enumerate(["검증 보고서", "발표 자료", "관리자용 보고서"]):
        node(d, f"o{i}", 940, 95 + i * 130, 260, 64, label, size=14)
        flow(d, f"fo{i}", 910, 127 + i * 130, [[0, 0], [30, 0]])
    node(d, "manual", 940, 530, 260, 56, "본문 숫자를 직접 고치기", fill=CHIP, dashed=True, size=14)
    flow(d, "fm", 1070, 530, [[0, 0], [0, -50]], style="dashed", color=WEAK)
    note(d, "이 경로는 쓰지 않는다", 790, 549, size=13)
    return d


def differential(out: Path) -> Diagram:
    d = new_diagram("vg-03-differential", "같은 입력, 두 구현, 하나의 비교",
                    brief(claim="같은 입력을 두 구현이 처리해 정규화 결과를 비교하고, 차이는 일치·승인 예외·미해결로 나뉘며 "
                                "미해결은 고친 뒤 같은 입력으로 다시 돌린다.",
                          span="공용 입력 하나에서 판정까지", flow="왼쪽에서 오른쪽, 결함은 아래 파선으로 되돌아감",
                          change="입력 → 구현별 결과 → 정규화 결과 → 판정", actors="구현 A · 구현 B · 비교",
                          caption="차등 테스트"), out)
    node(d, "in", 40, 230, 170, 90, "공용 입력\n(같은 파일)", size=15)
    for k, (y, name) in enumerate([(70, "구현 A"), (400, "구현 B")]):
        note(d, name, 260, y - 30, size=16, color=BLACK)
        node(d, f"p{k}", 260, y, 200, 80, "파싱", size=15)
        node(d, f"n{k}", 510, y, 200, 80, "정규화 결과", size=15)
        flow(d, f"pn{k}", 460, y + 40, [[0, 0], [50, 0]])
        flow(d, f"in{k}", 210, 275, [[0, 0], [25, 0], [25, y + 40 - 275], [50, y + 40 - 275]])
        target = 255 if k == 0 else 295
        flow(d, f"nc{k}", 710, y + 40, [[0, 0], [35, 0], [35, target - y - 40], [70, target - y - 40]])
    note(d, "정규화 결과: 비교하기 쉽게 같은 형식(JSON)으로 바꾼 결과", 260, 500, size=13)
    node(d, "cmp", 780, 230, 160, 90, "비교", emph=True, size=16)
    results = [("일치", 90, {}), ("승인 예외\n이유를 기록", 240, {}), ("미해결\n→ 결함 수정", 390, {"fill": CHIP})]
    for i, (label, y, style) in enumerate(results):
        node(d, f"r{i}", 1020, y, 190, 70, label, size=15, **style)
        dy = y + 35 - 275
        flow(d, f"cr{i}", 940, 275, [[0, 0], [40, 0], [40, dy], [80, dy]])
    flow(d, "loop", 1115, 460, [[0, 0], [0, 100], [-990, 100], [-990, -140]], style="dashed")  # 입력 상자 밑변(y=320)에서 멈춘다
    note(d, "고친 뒤 같은 입력으로 다시 실행", 620, 568, size=13, align="center")
    return d


def fuzz_loop(out: Path) -> Diagram:
    d = new_diagram("vg-04-fuzz-loop", "퍼징 반복과 회귀 테스트 입력",
                    brief(claim="시드로 만든 변형 입력이 성질 검사를 통과하지 못하면 최소화해 회귀 테스트 입력으로 저장하고, "
                                "그 입력은 커밋마다 CI에서 다시 검사된다.",
                          span="시드에서 CI 재검사까지", flow="왼쪽에서 오른쪽, 실패 가지는 아래",
                          change="시드 → 변형 입력 → 최소 재현 입력 → 회귀 테스트 입력", actors="생성기 · 성질 검사 · 최소화 · CI",
                          caption="퍼징 흐름"), out)
    node(d, "seed", 40, 120, 120, 60, "시드", size=15)
    node(d, "gen", 210, 120, 180, 60, "생성기", size=15)
    note(d, "입력 모음에서 고르고\n1~8회 변형", 300, 190, size=13, align="center")
    flow(d, "f0", 160, 150, [[0, 0], [50, 0]])
    decision(d, "prop", 440, 85, 230, 130, "성질을 모두\n지키나?", size=14, emph=True)
    flow(d, "f1", 390, 150, [[0, 0], [50, 0]])
    node(d, "next", 730, 120, 160, 60, "다음 반복", size=15)
    flow(d, "yes", 670, 150, [[0, 0], [60, 0]])
    note(d, "예", 682, 126, size=12)
    flow(d, "loop", 810, 120, [[0, 0], [0, -70], [-510, -70], [-510, 0]], style="dashed")  # 생성기 윗변(y=120)에서 멈춘다
    note(d, "반복 번호 + 1", 555, 28, size=13, align="center")
    flow(d, "no", 555, 215, [[0, 0], [0, 85]])
    note(d, "아니오", 565, 245, size=12)
    node(d, "min", 465, 300, 180, 60, "자동 최소화", size=15)
    node(d, "save", 705, 300, 220, 60, "회귀 테스트 입력으로\n저장", size=14)
    node(d, "ci", 985, 300, 200, 60, "커밋마다 CI에서\n다시 검사", size=14)
    flow(d, "f2", 645, 330, [[0, 0], [60, 0]])
    flow(d, "f3", 925, 330, [[0, 0], [60, 0]])
    note(d, "성질 예: 무크래시 · 시간 상한 · 왕복 동일 · 상한 준수", 40, 400, size=13)
    note(d, "시드 + 반복 번호 = 같은 입력 재현", 40, 426, size=13)
    return d


def measurement(out: Path) -> Diagram:
    d = new_diagram("vg-05-measurement", "실기기 측정 구성",
                    brief(claim="실기기의 Release 앱은 구간 표시를 남기고, 조작은 UI 자동화 또는 자동 재생이 맡으며, 프로파일러는 밖에서 "
                                "관찰만 하고, 호스트는 빌드·설치·결과 회수·커밋 기록을 맡는다.",
                          span="빌드에서 결과 기록까지", flow="호스트 → 기기(명령), 기기 → 호스트(회수)",
                          change="소스 → 설치된 앱 → 트레이스 → 기록", actors="앱 · 조작 · 프로파일러 · 호스트",
                          caption="측정 구성"), out)
    region(d, "dev", 40, 40, 780, 290, "실기기")
    node(d, "app", 70, 95, 360, 200, "")
    note(d, "앱 (Release 빌드)", 90, 108, size=16, color=BLACK)
    node(d, "sign", 100, 150, 300, 110, "구간 표시(signpost)\n측정 구간의 시작 · 끝 기록", emph=True, size=14)
    node(d, "drive", 530, 95, 260, 80, "조작\nUI 자동화 또는 자동 재생", size=14)
    flow(d, "input", 530, 135, [[0, 0], [-100, 0]])
    note(d, "입력 이벤트", 444, 143, size=12)
    node(d, "prof", 900, 215, 300, 80, "프로파일러\nInstruments · Perfetto", size=15)
    flow(d, "observe", 900, 255, [[0, 0], [-470, 0]], style="dotted")
    note(d, "관찰만", 640, 232, size=12)
    region(d, "host", 40, 400, 1160, 200, "호스트(Mac)")
    node(d, "build", 70, 460, 260, 80, "빌드 · 설치", size=15)
    flow(d, "cmd", 200, 460, [[0, 0], [0, -130]])
    note(d, "명령", 210, 365, size=12)
    node(d, "pull", 420, 460, 260, 80, "결과 회수\n트레이스 · 결과 파일", size=14)
    flow(d, "ret", 550, 330, [[0, 0], [0, 130]], style="dashed")
    node(d, "rec", 770, 460, 300, 80, "커밋 · 앱 UUID 기록\n어느 빌드를 쟀는지 남김", size=14)
    flow(d, "f1", 680, 500, [[0, 0], [90, 0]])
    note(d, "실선: 명령 · 파선: 결과 회수 · 점선: 관찰 (프로파일러는 앱 밖에서 관찰만 한다)", 60, 562, size=13, color=WEAK)
    return d


def threat_model(out: Path) -> Diagram:
    d = new_diagram("vg-06-threat-model", "믿을 수 없는 입력의 경로",
                    brief(claim="믿을 수 없는 입력은 신뢰 경계에서 입력 제한을 먼저 지나고, 링크·스크립트·외부 요청·네이티브 엔진 경로마다 "
                                "방어와 검증이 따로 붙는다.",
                          span="입력 원천에서 출력 경로 4개까지", flow="왼쪽에서 오른쪽, 경계를 지나 팬아웃",
                          change="원문 → 제한된 입력 → 경로별 처리", actors="입력 원천 · 입력 제한 · 출력 경로 4개",
                          caption="위협 모델"), out)
    rule(d, "boundary", 300, 50, [[0, 0], [0, 550]], style="dashed", color=NAVY)
    note(d, "신뢰 경계", 312, 26, size=14, color=NAVY)
    node(d, "src", 40, 230, 220, 140, "")
    note(d, "믿을 수 없는 입력", 60, 250, size=16, color=BLACK)
    note(d, "LLM 답변\n사용자 콘텐츠\n네트워크 응답", 60, 285, size=13)
    flow(d, "f0", 260, 300, [[0, 0], [80, 0]])
    node(d, "limit", 340, 220, 220, 160, "입력 제한\n\n크기 · 중첩 · 개수 상한", emph=True, size=15)
    note(d, "T2", 450, 392, size=15, color=NAVY, align="center")
    note(d, "막는 위협", 1136, 14, size=13, color=WEAK)
    paths = [("링크", "허용한 스킴만 연다 (https · http · mailto)", "T1"),
             ("화면 표시 · 스크립트", "HTML은 글자로 표시 · WebView는 CSP · HTML 새니타이저", "T3"),
             ("외부 요청", "번들에 든 로컬 파일만 읽고 외부 연결은 막는다", "T4"),
             ("네이티브 엔진 (FFI)", "엔진 입력 상한 · ASan·TSan으로 호출 경로 검사", "T5")]
    for i, (name, control, tag) in enumerate(paths):
        y = 40 + i * 140
        node(d, f"p{i}", 640, y, 480, 110, "")
        note(d, name, 664, y + 22, size=16, color=BLACK)
        note(d, control, 664, y + 62, size=13)
        note(d, tag, 1150, y + 45, size=15, color=NAVY)
        dy = y + 55 - 300
        flow(d, f"fp{i}", 560, 300, [[0, 0], [40, 0], [40, dy], [80, dy]])
    region(d, "legend", 40, 620, 1160, 110, "위협")
    legend_rows(d, ["T1 링크 스킴 악용 (javascript: · file: 등)", "T2 자원 고갈 (깊은 중첩 · 거대 입력)",
                    "T3 스크립트 실행 (HTML · WebView)", "T4 외부 요청 (추적 · 정보 유출)", "T5 네이티브 메모리 오류 (FFI 경계)"],
                60, 660, cols=3, col_w=380)
    return d


def ci_split(out: Path) -> Diagram:
    d = new_diagram("vg-07-ci-split", "자동 검사와 릴리스 전 검사",
                    brief(claim="빠르고 결과가 안정적인 검사는 커밋마다 자동으로 돌아 실패하면 막고, 실기기·계측·대규모 퍼징은 "
                                "릴리스 전에 사람이 돌린다.",
                          span="커밋에서 릴리스까지", flow="위 구역은 왼쪽에서 오른쪽, 아래 구역은 나열",
                          change="커밋 → 병합 / 릴리스 후보 → 릴리스", actors="CI · 사람", caption="CI 분할"), out)
    region(d, "auto", 40, 40, 1160, 280, "커밋·PR마다 (자동)")
    gates = ["빌드", "입력 모음\n해시 확인", "테스트\n퍼징 1만 회 포함", "커버리지 기준", "정적 분석 ·\n의존성 감사"]
    for i, label in enumerate(gates):
        x = 60 + i * 231
        node(d, f"g{i}", x, 100, 196, 80, label, size=15)
        flow(d, f"gd{i}", x + 98, 180, [[0, 0], [0, 50]], style="dashed")
        if i < len(gates) - 1:
            flow(d, f"ga{i}", x + 196, 140, [[0, 0], [35, 0]])
    node(d, "block", 60, 230, 1120, 56, "하나라도 실패하면 병합을 막는다 (브랜치 보호 설정이 있을 때)", fill=CHIP, size=15)
    node(d, "rule", 360, 345, 520, 50, "나누는 기준: 빠르고 결과가 안정적인가", emph=True, size=15)
    region(d, "manual", 40, 420, 1160, 170, "릴리스 전 (수동)")
    for i, label in enumerate(["실기기 성능", "퍼징 10만 회", "에뮬레이터\n계측 테스트", "UI · 접근성 테스트"]):
        node(d, f"m{i}", 60 + i * 290, 480, 260, 80, label, size=15)
    return d


def defect_flow(out: Path) -> Diagram:
    d = new_diagram("vg-08-defect-flow", "결함이 닫히는 순서",
                    brief(claim="결함은 발견 경로와 함께 번호를 받고, 최소 재현 → 수정 → 회귀 테스트 → 전체 재실행으로 닫히며, "
                                "상위 라이브러리 차이는 기록만 한다.",
                          span="발견에서 닫힘까지", flow="왼쪽에서 오른쪽, 기록만 하는 가지는 아래",
                          change="발견 → 번호 → 수정 → 닫힘", actors="결함 대장", caption="결함 처리 흐름"), out)
    node(d, "found", 40, 100, 100, 64, "발견", size=15)
    note(d, "발견 경로 기록", 90, 176, size=13, align="center")
    node(d, "id", 166, 100, 110, 64, "번호 부여", size=15)
    note(d, "머리글자\nF·E·R·S·P·T·M·D", 221, 176, size=13, align="center")
    decision(d, "ours", 302, 62, 220, 140, "우리 코드가 원인이거나\n사용자에게 보이나?", size=13)
    steps = [("repro", 548, 110, "최소 재현\n입력", False), ("fix", 684, 80, "수정", False),
             ("reg", 790, 120, "회귀 테스트\n추가", False), ("rerun", 936, 120, "전체 재실행", True)]
    for name, x, w, label, emph in steps:
        node(d, name, x, 100, w, 64, label, emph=emph, size=15 if "\n" not in label else 14)
    note(d, "출력이 바뀌면 안 되는\n수정은 바이트 비교", 996, 176, size=13, align="center")
    ellipse(d, "closed", 1082, 107, 90, 50, "닫힘", size=15)
    for i, x in enumerate([140, 276, 522, 658, 764, 910, 1056]):
        flow(d, f"f{i}", x, 132, [[0, 0], [26, 0]])
    note(d, "예", 526, 108, size=12)
    flow(d, "no", 412, 202, [[0, 0], [0, 78]])
    note(d, "아니오", 422, 228, size=12)
    node(d, "record", 262, 280, 300, 60, "기록만\nD: 상위 라이브러리 차이", fill=CHIP, size=14)
    return d


def fixed_window(out: Path) -> Diagram:
    d = new_diagram("vg-09-fixed-window", "고정 측정 구간과 구간 표시",
                    brief(claim="고정 10초 측정 구간은 작업이 일찍 끝나면 유휴 시간을 분모에 넣어 비율을 희석하고, "
                                "구간 표시로 잡은 구간은 실제 작업만 담는다.",
                          span="탭부터 10초까지", flow="왼쪽에서 오른쪽 (시간)", change="작업 중 → 유휴",
                          actors="고정 구간 · 실제 작업 · 구간 표시", caption="측정 구간 함정"), out)

    def tx(seconds: float) -> float:
        return 300 + 80 * seconds

    y1 = lane(d, "fixed", 100, "고정 측정 구간", label_w=220, x1=1180, size=14)
    y2 = lane(d, "work", 200, "실제 작업", label_w=220, x1=1180, size=14)
    y3 = lane(d, "sign", 300, "구간 표시로 잡은 구간", label_w=220, x1=1180, size=14)
    marker(d, "end", tx(7.6), "7.6 s 작업 끝", y_text=50, y_from=74, y_to=96, y_rule_to=350)
    task(d, "t-fixed", tx(0), y1, tx(10) - tx(0), "탭 + 10초")
    task(d, "t-work", tx(0.3), y2, tx(7.6) - tx(0.3), "스트림", emph=True)
    task(d, "t-idle", tx(7.6), y2, tx(10) - tx(7.6), "유휴 — 분모만 늘림", fill=CHIP, size=13)
    task(d, "t-sign", tx(0), y3, tx(7.9) - tx(0), "signpost 시작~끝 ±여유")
    rule(d, "axis", tx(0), 390, [[0, 0], [tx(10) - tx(0), 0]])
    for t in (0, 2.5, 5, 7.5, 10):
        rule(d, f"tick{t:g}", tx(t), 390, [[0, 0], [0, 6]])
        note(d, f"{t:g} s" if t in (0, 10) else f"{t:g}", tx(t), 402, size=13, align="center")
    note(d, "끊김 시간 비율 = 늦게 표시된 시간의 합 ÷ 측정 구간 길이 — 구간이 실제 작업보다 길면 비율이 희석된다", 40, 444, size=13)
    return d


def schedule(out: Path) -> Diagram:
    d = new_diagram("vg-10-schedule", "부하 일정의 두 방식",
                    brief(claim="'처리 후 50 ms 쉬기'는 처리가 느린 빌드일수록 간격이 늘어 부하가 줄고, 절대 시각 일정은 빌드 속도와 "
                                "상관없이 같은 간격을 유지한다.",
                          span="0~300 ms", flow="왼쪽에서 오른쪽 (시간)", change="청크 간격 50 → 60 → 100 ms",
                          actors="절대 시각 일정 · 빠른 빌드 · 느린 빌드", caption="부하 일정 함정"), out)

    def tx(ms: float) -> float:
        return 270 + 3 * ms

    for t in range(0, 301, 50):  # 50 ms 격자를 먼저 그려 상자 아래에 깐다
        rule(d, f"grid{t}", tx(t), 78, [[0, 0], [0, 282]], style="dashed", color=REGION_STROKE)
    y1 = lane(d, "abs", 80, "절대 시각 일정", label_w=200, x1=1190, size=14)
    y2 = lane(d, "fast", 190, "처리 후 50 ms 쉬기\n빠른 빌드", label_w=200, x1=1190, size=14)
    y3 = lane(d, "slow", 300, "처리 후 50 ms 쉬기\n느린 빌드", label_w=200, x1=1190, size=14)
    for k in range(6):
        task(d, f"abs{k}", tx(k * 50), y1, 30, str(k + 1), emph=True, size=13)
    for lane_y, yc, proc, label in [(190, y2, 10, "{}"), (300, y3, 50, "처리 {}")]:
        starts = list(range(0, 300, proc + 50))
        for k, start in enumerate(starts):
            task(d, f"p{proc}-{k}", tx(start), yc, 3 * proc, label.format(k + 1), size=13)
            task(d, f"s{proc}-{k}", tx(start + proc), yc, 150, "쉼 50 ms", faded=True, dashed=True, size=12)
        note(d, f"300 ms 동안 {len(starts)}개", 1060, lane_y - 22, size=13)
    note(d, "300 ms 동안 6개", 1060, 58, size=13)
    rule(d, "axis", tx(0), 370, [[0, 0], [tx(300) - tx(0), 0]])
    for t in range(0, 301, 50):
        rule(d, f"tick{t}", tx(t), 370, [[0, 0], [0, 6]])
        note(d, f"{t} ms" if t == 300 else str(t), tx(t), 382, size=13, align="center")
    note(d, "느린 빌드일수록 부하가 줄어 측정값이 좋아 보인다", 40, 424, size=14, color=BLACK)
    note(d, "절대 시각 일정은 k번째 청크를 '시작 시각 + k × 50 ms'에 보내므로 처리 속도와 상관없이 간격이 같다", 40, 450, size=13)
    return d


def witness_rule(out: Path) -> Diagram:
    d = new_diagram("vg-11-witness-rule", "hitch로 세어지는 조건",
                    brief(claim="늦은 프레임이 화면에 머무는 동안 다른 프레임이 표시되어야 계측기가 hitch로 세므로, "
                                "같은 지연도 시작 위상에 따라 세어지거나 빠진다.",
                          span="vsync 다섯 주기", flow="왼쪽에서 오른쪽 (시간), 위아래 두 경우 비교",
                          change="같은 지연 → 셈 / 세지 않음", actors="앱 프레임 · 다른 프레임(스피너) · 계측기",
                          caption="hitch 판정 조건"), out)
    vsync = [300 + 120 * k for k in range(6)]
    cases = [(20, "경우 1. 늦은 프레임이 머무는 동안 스피너 프레임이 표시됨", True),
             (270, "경우 2. 늦은 프레임이 머무는 동안 다른 프레임이 없음", False)]
    for k, (base, title, witnessed) in enumerate(cases):
        note(d, title, 40, base, size=15, color=BLACK)
        tick_y = base + 40
        for i, x in enumerate(vsync):
            rule(d, f"g{k}-{i}", x, tick_y + 12, [[0, 0], [0, 176]], style="dashed", color=REGION_STROKE)
            rule(d, f"v{k}-{i}", x, tick_y, [[0, 0], [0, 12]])
        note(d, "vsync", 60, tick_y - 2, size=13)
        ya = lane(d, f"app{k}", base + 70, "앱 프레임", label_w=200, x1=940, size=14)
        yb = lane(d, f"other{k}", base + 140, "다른 프레임 (스피너)", label_w=200, x1=940, size=14, faded=not witnessed)
        task(d, f"prev{k}", vsync[0], ya, 120, "이전 프레임", size=13)
        task(d, f"late{k}", vsync[1], ya, 360, "늦은 프레임 — 3 vsync 동안 화면에 머묾", size=13)
        task(d, f"next{k}", vsync[4], ya, 120, "다음 프레임", size=13)
        if witnessed:
            for i in (1, 2, 3):
                task(d, f"spin{k}-{i}", vsync[i] + 10, yb, 100, "스피너", size=13)
            node(d, f"res{k}", 980, base + 95, 200, 64, "hitch로 셈", emph=True, size=16)
        else:
            task(d, f"none{k}", vsync[1], yb, 360, "표시된 프레임 없음", faded=True, dashed=True, size=13)
            node(d, f"res{k}", 980, base + 95, 200, 64, "세지 않음", fill=CHIP, size=16)
    note(d, "같은 지연도 시작 위상에 따라 세어지거나 빠진다", 40, 500, size=14, color=BLACK)
    note(d, "→ 빌드 비교에는 메인 스레드 점유 시간과 지연 초과 시간을 함께 본다", 40, 526, size=13)
    return d


DIAGRAMS = {
    "vg-01-modes": modes,
    "vg-02-number-pipeline": number_pipeline,
    "vg-03-differential": differential,
    "vg-04-fuzz-loop": fuzz_loop,
    "vg-05-measurement": measurement,
    "vg-06-threat-model": threat_model,
    "vg-07-ci-split": ci_split,
    "vg-08-defect-flow": defect_flow,
    "vg-09-fixed-window": fixed_window,
    "vg-10-schedule": schedule,
    "vg-11-witness-rule": witness_rule,
}


def add_white_background(svg: Path) -> None:
    """투명 SVG는 GitHub 다크 테마에서 검은 글자가 안 보인다. 여는 <svg> 바로 뒤에 흰 바탕을 깐다."""
    text = svg.read_text(encoding="utf-8")
    if WHITE_RECT in text:
        return
    opening = re.search(r"<svg\b[^>]*>", text)
    assert opening, f"<svg> 태그 없음: {svg}"
    view_box = re.search(r'viewBox="([^"]+)"', opening.group(0))
    assert view_box and view_box.group(1).split()[:2] == ["0", "0"], f"viewBox 원점이 0 0이 아니다: {svg}"
    svg.write_text(text[:opening.end()] + WHITE_RECT + text[opening.end():], encoding="utf-8")


def build_diagrams(renders: Path) -> list[Path]:
    svgs = build_all(DIAGRAMS, source_dir=SOURCES, svg_dir=FIGURES)
    for svg in svgs:
        add_white_background(svg)
        render_png(svg, renders / f"{svg.stem}.png")
    return svgs


# ================================================================ 그래프 (가상 데이터)

def write_csv(path: Path, header: list[str], rows: list[tuple]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"wrote {path.name} ({len(rows)}행)")


def make_data(data: Path) -> None:
    """가상 데이터. 실제 측정값이 아니며 그림의 주장을 보여 주려고 만든 값이다."""
    data.mkdir(parents=True, exist_ok=True)
    runs = {"A": [3.1, 4.2, 4.6, 4.8, 9.7, 12.4], "B": [1.2, 1.5, 1.6, 1.8, 2.0, 2.3]}
    write_csv(data / "median_range.csv", ["build", "run", "hitch_ms_s"],
              [(build, i + 1, value) for build, values in runs.items() for i, value in enumerate(values)])
    rng = np.random.default_rng(SEED)
    frames = []
    for run in range(1, 6):
        mean = 14.0 if run == 4 else 5.0  # 반복 4만 느리다
        frames += [(run, f"{value:.2f}") for value in rng.normal(mean, 1.0, 120).clip(0.5)]
    write_csv(data / "pooled_frames.csv", ["run", "frame_ms"], frames)
    write_csv(data / "reference_lines.csv", ["chart", "label", "value"],
              [("median-range", "외부 기준 5", 5), ("median-range", "10", 10),
               ("pooled-p90", "프레임 예산 8.33 ms (120 Hz)", f"{1000 / 120:.2f}")])


def references(data: Path, chart: str) -> list[tuple[str, float]]:
    return [(r["label"], float(r["value"])) for r in read_csv(data, "reference_lines") if r["chart"] == chart]


def synthetic_mark(ax, y: float) -> None:
    ax.text(1.0, y, "가상 데이터", transform=ax.transAxes, ha="right", va="top", fontsize=7, color=MUTED)


def median_range_chart(data: Path, out: Path) -> Path:
    rows = read_csv(data, "median_range")
    builds = list(dict.fromkeys(r["build"] for r in rows))
    colors = dict(zip(builds, [BLUE, ORANGE]))
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 2.2))
    ys = list(range(len(builds)))[::-1]
    top = 0.0
    for y, build in zip(ys, builds):
        values = [float(r["hitch_ms_s"]) for r in rows if r["build"] == build]
        median = statistics.median(values)
        top = max(top, max(values))
        ax.hlines(y, min(values), max(values), color=colors[build], linewidth=1, zorder=2)
        ax.scatter(values, [y] * len(values), s=28, color=colors[build], alpha=0.7, linewidths=0, zorder=3)
        ax.plot([median, median], [y - 0.22, y + 0.22], color=INK, linewidth=2.2, zorder=4)
        # 라벨은 중앙값 눈금의 왼쪽 위에 둔다. 가운데 정렬이면 바로 오른쪽의 기준선과 겹친다.
        ax.annotate(f"중앙값 {median:.1f}", (median, y + 0.22), xytext=(-3, 1), textcoords="offset points", ha="right",
                    fontsize=8, color=INK)
    for label, value in references(data, "median-range"):
        vline_ref(ax, value, label, -0.75)
    ax.set_ylim(-0.9, len(builds) - 0.4)
    ax.set_yticks(ys, [f"빌드 {b}" for b in builds], fontsize=8)
    ax.set_xlim(0, top * 1.12)
    ax.set_xlabel("끊김 시간 비율 (ms/s) · 점 = 회차(6회), 굵은 세로선 = 중앙값, 가는 선 = 최소~최대")
    bar_axis(ax)
    synthetic_mark(ax, -0.32)
    return save(fig, out, "vg-chart-01-median-range")


def pooled_p90_chart(data: Path, out: Path) -> Path:
    rows = read_csv(data, "pooled_frames")
    runs = sorted({int(r["run"]) for r in rows})
    frames = {run: [float(r["frame_ms"]) for r in rows if int(r["run"]) == run] for run in runs}
    p90 = {run: float(np.percentile(values, 90)) for run, values in frames.items()}
    pooled = float(np.percentile([v for values in frames.values() for v in values], 90))
    slowest = max(p90, key=p90.get)
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 3.0))
    xs = list(range(len(runs)))
    ax.bar(xs, [p90[r] for r in runs], width=0.6, color=[ORANGE if r == slowest else NEUTRAL for r in runs], zorder=3)
    for x, run in zip(xs, runs):
        top_label(ax, x, p90[run], f"{p90[run]:.1f}", size=8, color=INK)
    pooled_color = ORANGE_RAMP[3]
    ax.axhline(pooled, color=pooled_color, linewidth=1.3, linestyle=(0, (6, 2)), zorder=4)
    ax.annotate(f"반복 합산 P90 {pooled:.1f} ms", (-0.55, pooled), xytext=(0, 4), textcoords="offset points", ha="left",
                fontsize=7.5, color=pooled_color)
    for label, value in references(data, "pooled-p90"):
        hline_ref(ax, value, label, -0.55)
    ax.set_xticks(xs, [f"반복 {r}" for r in runs], fontsize=8)
    ax.set_xlim(-0.6, len(runs) - 0.4)
    ax.set_ylim(0, max(max(p90.values()), pooled) * 1.25)
    ax.set_ylabel("프레임 시간 P90 (ms)")
    ax.set_xlabel(f"반복(각 {len(frames[runs[0]])}프레임) · 막대 = 반복별 P90, 주황 파선 = 모든 반복의 프레임을 합쳐 낸 P90")
    column_axis(ax)
    synthetic_mark(ax, -0.2)
    return save(fig, out, "vg-chart-02-pooled-p90")


# ================================================================ main

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--renders", type=Path, help="검수 PNG를 둘 폴더(저장소 밖)")
    parser.add_argument("--make-data", action="store_true", help="가상 데이터 CSV를 시드 고정으로 다시 쓴다")
    args = parser.parse_args()
    if not (args.make_data or args.renders):
        parser.error("--make-data 또는 --renders 중 하나는 필요하다")
    if args.make_data:
        make_data(DATA)
    if not args.renders:
        return
    renders = args.renders.resolve()
    svgs = build_diagrams(renders)
    family = setup_style()
    charts = [median_range_chart(DATA, FIGURES), pooled_p90_chart(DATA, FIGURES)]
    outputs = svgs + [renders / f"{svg.stem}.png" for svg in svgs] + charts
    for path in outputs:
        assert path.exists() and path.stat().st_size > 1000, f"산출물 없음: {path}"
    for svg in svgs:
        assert WHITE_RECT in svg.read_text(encoding="utf-8"), f"흰 바탕 없음: {svg}"
    assert len(svgs) == 11 and len(charts) == 2
    print(f"OK · 도식 {len(svgs)}장 · 그래프 {len(charts)}장 · 글꼴 {family}")


if __name__ == "__main__":
    main()
