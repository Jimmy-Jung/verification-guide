# 그림 다시 만들기

이 폴더의 도식 11장과 그래프 2장은 모두 [build_figures.py](build_figures.py) 한 파일이 만듭니다. 그림을 고칠 때는 SVG나 PNG에 직접 손대지 않고, 스크립트의 좌표·라벨이나 CSV 데이터를 고친 뒤 다시 빌드합니다. 손으로 고친 파일은 다음 빌드가 덮어씁니다.

## 1. 필요한 도구

*표 1. 그림 빌드에 필요한 도구*

| 도구 | 쓰는 곳 |
|---|---|
| Python 3, matplotlib 3.10 이상, numpy | 그래프 2장과 가상 데이터 생성 |
| Node.js `npx` | Excalidraw 원본을 SVG로 내보내는 도구(익스포터) 실행. 첫 실행 때 npm에서 고정 버전을 내려받음 |
| `rsvg-convert` (librsvg) | 검수용 PNG 생성 |
| paper-figures 스킬의 헬퍼 `paper_kit`·`chart_style` | 상자·선·색·글꼴 같은 그림 스타일 |

헬퍼 위치는 `PAPER_FIGURES_SCRIPTS` 환경 변수로 지정합니다. 지정하지 않으면 `~/.claude/skills/paper-figures/scripts`에서 찾습니다. `paper_kit`은 같은 스킬 폴더에 나란히 있는 excalidraw-concept-diagrams 스킬과 technical-document-writing 스킬도 불러 씁니다.

## 2. 다시 만드는 순서

저장소 루트에서 다음 명령을 실행합니다. `<빌드 폴더>`는 저장소 밖의 작업 폴더입니다.

```bash
export PAPER_FIGURES_SCRIPTS="$HOME/.claude/skills/paper-figures/scripts"   # 기본 위치라면 생략합니다

# 가상 데이터를 바꿀 때만: CSV 3개를 시드 고정으로 다시 씁니다
python3 docs/assets/build_figures.py --make-data

# 도식 11장과 그래프 2장을 만듭니다
MPLCONFIGDIR="<빌드 폴더>/mpl" npm_config_cache="<빌드 폴더>/npm-cache" TMPDIR="<빌드 폴더>/tmp/" \
  python3 docs/assets/build_figures.py --renders "<빌드 폴더>/renders"
```

`MPLCONFIGDIR`·`npm_config_cache`·`TMPDIR`는 matplotlib 글꼴 캐시, npm 캐시, 익스포터 임시 파일을 저장소 밖에 두려고 지정합니다. 빠뜨려도 빌드는 되지만 캐시가 기본 위치에 쌓입니다.

빌드가 끝나면 마지막 줄에 `OK · 도식 11장 · 그래프 2장`이 나옵니다. 한 장이라도 만들어지지 않으면 스크립트가 실패합니다.

그다음 도식 검수 PNG(`<빌드 폴더>/renders`)와 그래프 PNG(`docs/assets/figures/`)를 한 장씩 직접 봅니다. 화살표가 상자나 글자를 지나가지 않는지, 글자가 상자 밖으로 나오지 않는지, 값 라벨이 기준선과 겹치지 않는지 확인합니다. 문제가 있으면 스크립트의 좌표를 고쳐 다시 빌드합니다.

## 3. 산출물 위치

*표 2. 빌드 산출물과 위치*

| 산출물 | 위치 | 저장소에 넣는가 |
|---|---|---|
| 도식 편집 원본 | `figures/src/<이름>.excalidraw.md` | 넣습니다 |
| 도식 SVG(문서에 넣는 파일) | `figures/<이름>.svg` | 넣습니다 |
| 그래프 PNG(220 dpi, 폭 6.4 in) | `figures/vg-chart-0N-*.png` | 넣습니다 |
| 그래프 데이터 | `data/*.csv` | 넣습니다 |
| 도식 검수 PNG | `<빌드 폴더>/renders/<이름>.png` | 넣지 않습니다 |

SVG에는 빌드 스크립트가 흰 바탕 사각형을 넣습니다. 익스포터가 내보내는 SVG는 배경이 투명해서, GitHub 다크 테마에서는 검은 글자가 어두운 바탕에 묻혀 보이지 않기 때문입니다.

## 4. 가상 데이터

그래프 2장은 실제 측정값이 아니라, 해석 원칙을 보여 주려고 만든 **가상 데이터**로 그렸습니다. 그래프 안 오른쪽 아래에도 "가상 데이터"라고 적었습니다.

*표 3. 데이터 파일*

| 파일 | 내용 |
|---|---|
| `data/median_range.csv` | 빌드 A·B를 각각 6회 측정한 끊김 시간 비율(ms/s) |
| `data/pooled_frames.csv` | 반복 5회의 프레임별 원시 시간(ms). 반복마다 120프레임, 반복 4만 느림 |
| `data/reference_lines.csv` | 그래프에 긋는 기준선 값과 라벨 |

`pooled_frames.csv`는 난수로 만들고, 시드는 `20261022`로 고정했습니다. 그래서 `--make-data`를 다시 실행해도 같은 파일이 나옵니다. 그래프의 P90은 이 원시 프레임 값에서 빌드할 때마다 계산하고, 그림 코드에는 숫자를 직접 적지 않습니다.

## 5. 그림 목록

*표 4. 그림과 넣는 문서*

| ID | 파일 | 넣는 문서 | 그림이 말하는 것 |
|---|---|---|---|
| F1 | `vg-01-modes.svg` | README.md | 계획→실행→해석→보고 순서와 되돌아가는 두 경로 |
| F2 | `vg-02-number-pipeline.svg` | 06-records-and-reports.md | 모든 수치가 CSV 한 벌에서만 나오는 구조 |
| F3 | `vg-03-differential.svg` | 02-correctness.md | 두 구현의 정규화 결과 비교와 세 갈래 판정 |
| F4 | `vg-04-fuzz-loop.svg` | 02-correctness.md | 실패한 변형 입력이 회귀 테스트 입력이 되는 과정 |
| F5 | `vg-05-measurement.svg` | 03-performance.md | 실기기·조작·프로파일러·호스트의 역할 분리 |
| F6 | `vg-06-threat-model.svg` | 04-security.md | 신뢰 경계, 입력 제한, 경로별 방어 |
| F7 | `vg-07-ci-split.svg` | 05-maintenance.md | 커밋마다 자동 검사와 릴리스 전 수동 검사의 구분 |
| F8 | `vg-08-defect-flow.svg` | 06-records-and-reports.md | 결함이 번호를 받고 닫히기까지의 순서 |
| F9 | `vg-09-fixed-window.svg` | 03-performance.md 함정 1 | 고정 10초 측정 구간이 비율을 희석하는 이유 |
| F10 | `vg-10-schedule.svg` | 03-performance.md 함정 2 | "처리 후 쉬기" 일정이 느린 빌드의 부하를 줄이는 이유 |
| F11 | `vg-11-witness-rule.svg` | 03-performance.md 함정 6 | 같은 지연도 hitch로 세어지거나 빠지는 조건 |
| C1 | `vg-chart-01-median-range.png` | 01-principles.md | 중앙값이 기준 안이어도 범위가 여러 판정 구간에 걸치는 경우(가상 예시) |
| C2 | `vg-chart-02-pooled-p90.png` | 03-performance.md 함정 5 | 한 번만 느린 반복이 합산 P90을 프레임 예산 위로 올리는 현상(가상 예시) |

## 6. 도구 문서의 스크린샷

`screenshots/rmv-tool-*.png` 66장은 도식과 달리 다시 만들 수 없는 그림입니다. 2026년 10월 RichMarkdown(iOS·Android Markdown 렌더러)을 검증할 때 찍은 화면이고, 도구 문서 5편에서 "결과 읽는 법" 같은 절에 붙어 있습니다. 화면 속 숫자는 그 검증에서 나온 값이라, 다른 프로젝트에서는 출력의 모양만 참고합니다.

공개 저장소에 넣기 전에 두 가지를 확인했습니다.

- **개인 정보.** 모든 장의 글자를 OCR(이미지 속 글자를 읽어 내는 기능)로 읽고 눈으로도 한 장씩 봤습니다. 로컬 경로가 찍힌 6장은 그 부분만 `<빌드 폴더>`나 `~/…/RichMarkdown/`처럼 바꿔 그렸습니다. Android 패키지 이름, 공개 저장소 이름, 기기 모델명은 이미 공개된 정보라 그대로 두었습니다.
- **저작권.** 원래 자료에 있던 Apple 개발자 문서의 도판 3장(렌더 파이프라인, 커밋 hitch, Hitches 템플릿 화면)은 넣지 않고 원문 링크로 대신했습니다. Perfetto 문서의 도판 1장(`rmv-tool-perfetto-02.png`)은 Perfetto 문서의 라이선스(Apache License 2.0)에 따라 출처를 밝혀 넣었습니다.

원래 자료에서 내용이 같은 화면 1장은 한 장만 남겼습니다.

스크린샷을 새로 더할 때도 같은 순서로 확인합니다. 화면에 사용자 이름, 홈 폴더나 외장 볼륨 경로, 기기 일련번호, 이메일, 토큰이 없는지 보고, 남의 문서에서 가져온 그림이면 라이선스를 확인합니다.

