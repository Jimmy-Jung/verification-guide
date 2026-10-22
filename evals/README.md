# evals — 플러그인이 실제로 도움이 되는지 재는 평가 케이스

eval(평가)은 사용자가 칠 법한 요청을 모델에 그대로 넣고, 돌아온 답이 기대한 조건을 갖췄는지 자동으로 판정하는 시험입니다. 이 폴더의 케이스는 `claude plugin eval .`이 읽습니다.

스킬 문서를 잘 써도, 모델이 그 스킬을 실제로 불러 쓰는지, 불렀을 때 답이 나아지는지는 문서만 읽어서는 알 수 없습니다. 그래서 같은 요청을 플러그인이 있을 때와 없을 때 각각 돌려 점수를 비교합니다. 플러그인 없이도 똑같이 잘 답한다면, 그 케이스에서는 플러그인이 하는 일이 없는 셈입니다.

반대로 검증과 무관한 질문에 스킬이 끼어들면 오히려 방해가 됩니다. 그래서 스킬이 호출되지 않아야 하는 케이스도 함께 둡니다.

## 케이스 구성

케이스마다 폴더가 하나 있고, 그 안에 `prompt.md`(사용자가 칠 법한 요청)와 `graders/*.md`(판정 기준)가 있습니다. `prompt.md` 머리말(맨 위 `---` 사이의 설정 블록, 프런트매터)에는 최대 턴 수(`max_turns`), 제한 시간(`timeout_seconds`), 허용 도구(`allowed_tools`), 반복 횟수(`runs`), 태그(`tags`)가 적혀 있습니다. 지금 있는 케이스는 표 1과 같습니다.

*표 1. eval 케이스와 확인하는 것*

| 케이스 | 태그 | 확인하는 것 |
|---|---|---|
| `plan-four-questions` | `plan` | 검증 계획 요청에 스킬이 호출되고, 네 질문·재실행·남은 조건·사용자 결정 항목을 갖춘 계획을 낸다 |
| `interpret-single-run-hitch` | `interpret`, `performance` | 1회 측정·고정 측정 구간·접근성 모드·기준 출처를 짚고 판정을 "잠정"으로 돌린다 |
| `zero-findings-scope` | `interpret`, `security` | "취약점 없음" 대신 도구별 0건의 범위를 붙인 문구를 낸다 |
| `ignores-unrelated-request` | `negative` | 검증과 무관한 SwiftUI 질문에는 스킬이 호출되지 않는다 |

판정 파일은 머리말의 `type`에 따라 세 종류로 나뉩니다(표 2). `llm` 판정 가운데 답의 내용을 깊이 보는 세 개(`plan-quality.md`, `measurement-critique.md`, `scoped-zero.md`)에는 가중치 `weight: 2`를 주어 다른 판정보다 크게 반영합니다.

*표 2. 판정 파일의 종류*

| `type` | 판정 방법 | 이 폴더의 예 |
|---|---|---|
| `tool_used` | 정해진 도구(여기서는 `Skill`)가 불린 횟수로 판정 | `skill-fired.md`, `skill-not-fired.md` |
| `regex` | 마지막 답변에 정규식이 맞는지로 판정 | `four-questions-and-remaining.md` |
| `llm` | 판정용 모델이 마지막 답변을 기준 문장과 대조해 PASS·FAIL로 판정 | `plan-quality.md`, `measurement-critique.md`, `scoped-zero.md`, `answers-directly.md` |

## 실행 방법

저장소 루트에서 실행합니다. 모델을 실제로 호출하므로 비용이 듭니다.

```sh
claude plugin eval . --trust-plugin                     # 전체, no-plugin baseline 포함
claude plugin eval . --trust-plugin --tag interpret     # 일부
claude plugin eval . --trust-plugin --json results.json --model <id> --judge-model <id>   # CI
```

첫 줄은 모든 케이스를 실행하고, 플러그인을 뺀 기준 실행(no-plugin baseline)도 함께 돌립니다. 둘째 줄은 태그가 `interpret`인 케이스(표 1의 두 개)만 돌립니다. 셋째 줄은 CI용으로, 전체 결과를 JSON 파일로 남기고 답변 모델과 판정 모델을 고정합니다.

`--trust-plugin`은 처음 실행할 때 나오는 신뢰 확인 질문을 건너뛰는 옵션입니다. 플러그인 코드와 eval 케이스를 믿을 수 있을 때만 붙입니다.

## 비용 주의

실행(run) 하나마다 실제 Claude 세션이 하나씩 열리고, 실행한 사람의 인증으로 모델을 호출합니다. 케이스마다 `runs: 2`이고 플러그인 있음·없음 두 갈래를 돌리므로, 전체를 실행하면 답변 세션 16번에 `llm` 판정 호출이 더해집니다. 판정 모델은 따로 지정하지 않으면 haiku입니다.

비용을 줄이려면 `--tag`로 필요한 케이스만 돌립니다. 비용을 확실히 묶어 두려면 `--max-cost-usd`로 상한을 둡니다. 상한에 닿으면 실행을 멈추고 그때까지의 결과만 보고합니다.

## 결과 읽는 법

`results/`는 실행할 때 생기며 `.gitignore`에 들어 있습니다. 실행마다 시각을 이름으로 한 폴더가 생기고, 그 안에 `aggregate-result.json`(점수 집계)과 `report.html`(사람이 읽는 보고서)이 있습니다. 보고서는 계정이 지원하면 claude.ai에도 게시되므로, 로컬에만 두려면 `--no-publish`를 붙입니다.

먼저 볼 값은 케이스별 점수(`score`)와 통과율(`passRate`), 전체 점수(`overallScore`)입니다. 케이스 점수가 기준(`--threshold`, 기본 1.0)보다 낮으면 명령이 종료 코드 1로 끝나므로, CI에서 그대로 실패로 처리할 수 있습니다.

비교 실행에서 핵심은 플러그인 있음·없음 두 갈래의 점수 차이입니다. 차이가 크면 플러그인이 답을 바꾼 것이고, 차이가 없으면 그 케이스에서는 플러그인이 하는 일이 없는 것입니다. 스킬 호출 판정(`tool_used: Skill`)은 플러그인이 없는 쪽에서는 성립할 수 없으므로, 비교 실행에서는 점수에 넣지 않고 "스킬이 호출됐는가"를 보여 주는 표시로만 씁니다.

케이스마다 두 번만 돌리고 모델의 답은 실행마다 달라지므로, 점수 하나로 단정하지 않습니다. 실패한 실행이 있으면 `report.html`에서 그 실행의 답변과 판정 이유를 먼저 읽습니다.
