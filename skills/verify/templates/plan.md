---
title: "<프로젝트> 검증 보강 — 요구사항과 계획"
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: <작성자>
status: draft
---

# <프로젝트> 검증 보강 — 요구사항과 계획

## 0. 배경과 목표

<무엇이 결정되었고 어떤 우려가 제기되었나. 목표: 우려에 재현 가능한 근거로 답한다.>

원칙:
1. 보고서의 모든 수치는 실제 실행 결과만 쓴다. 환경·날짜·커밋·원시 데이터 경로를 함께 적는다. 추정값은 "추정"으로 표기한다.
2. 핵심 지표는 원리가 다른 도구 두 가지로 교차 확인한다.
3. 확인하지 않은 범위와 미해결 결함은 "남은 조건" 절에 적는다.
4. 모든 검증은 스크립트와 CI로 다시 실행할 수 있어야 한다.

## 1. 현재 상태 (YYYY-MM-DD 실측)

*표 1. 현재 상태 실측*

| 항목 | <플랫폼 A> (커밋) | <플랫폼 B> (커밋) |
|---|---|---|
| 소스 규모 | | |
| 테스트 수 | | |
| 커버리지 | | |
| 성능 기록 | | |
| 보안 분석 | | |
| CI | | |
| 알려진 미해결 | | |

*표 2. 가용 환경*

| 구분 | 있음 | 없음(설치·준비 필요) |
|---|---|---|
| 측정 도구 | | |
| 시뮬레이터·에뮬레이터 런타임 | | |
| 실기기 | | |
| 문서 도구 | | |

## 2. 요구사항

### 2-1. 보고서가 답해야 하는 질문

| ID | 질문 | 답의 형태 |
|---|---|---|
| Q1 오류 | | 테스트 매트릭스, 퍼징(fuzz 테스트) 결과, 플랫폼 간 비교(패리티) diff, 결함 대장 |
| Q2 성능 | | 도구별 측정표·그래프, CI 게이트 기준과 통과 여부, 기기별 비교 |
| Q3 보안 | | 위협 모델, 정적·의존성 결과, 공격 입력 차단 결과, 설정 체크리스트 |
| Q4 유지보수 | | 복잡도·커버리지·경고 수, CI 게이트 흐름 |

### 2-2. 프로젝트 보강 요구사항 (FR)

| ID | 요구사항 | 완료 기준 |
|---|---|---|
| FR-1 | 공용 입력 모음(코퍼스) | 범주별 파일 수 표, 저장소 간 해시 일치 |
| FR-2 | 속성 기반 테스트·퍼징 | CI N회·수동 M회 무크래시, 실패 시 최소화한 입력 자동 저장 |
| FR-3 | 렌더 수준 검사 | |
| FR-4 | 성능 하네스 | 시나리오 × 도구 원시 JSON, CI 게이트 기준표 |
| FR-5 | 보안 분석 | critical·high 0건 또는 수정·예외 사유, 공격 입력 전부 차단 |
| FR-6 | 품질 지표 | 모듈별 표 |
| FR-7 | CI | 커밋 게이트·수동 잡 구분 |
| FR-8 | 결함 처리 규칙 | 결함 대장(발견 경로·수정 커밋·회귀 테스트) |

### 2-3. 보고서 요구사항 (RR)

| ID | 요구사항 |
|---|---|
| RR-1 | 형식 |
| RR-2 | 모든 수치에 환경·날짜·커밋·원시 데이터 경로 |
| RR-3 | 도식·그래프·스크린샷 목록. 캡션은 표 위 `*표 N. …*`, 그림 아래 `*그림 N. …*` |
| RR-4 | 요약: 서술형 초록 3~5문장(결론·조건부 권고·남은 리스크). 리스크 표는 결론 절 |
| RR-5 | "확인하지 않은 범위·남은 조건" 절 필수 |
| RR-6 | 공개 사본 규칙 |
| RR-7 | 번호식 참고문헌(`[1] 저자·기관, "제목", 출처, URL`), 본문에서 [1]로 인용 |

### 2-4. 제약

<빌드 산출물 위치, 커밋 분리, 승인 범위, 세션 한도 대비>

## 3. 검증 설계 (의사코드)

### 3-1. 공용 입력 모음 러너 + 플랫폼 간 비교
```
for fixture in fixtures/**:
    doc = parse(fixture, limits); assert no_throw and elapsed < budget[category]
    norm = normalize(doc); write out/<platform>/<name>.json
parity = diff(out/A, out/B)  # 일치 / 승인 예외 / 미해결
```

### 3-2. 퍼징·속성 기반 테스트
```
rng = Seeded(seed)
repeat N: mutated = mutate(pick(corpus)); assert properties(mutated)
on failure: save minimize(mutated) → fixtures/regressions/<seed>-<n>
```

### 3-3. 성능
```
micro: measure(iterations) for inputs; gate on simulator; record on device Release
scenarios: trace(scroll, stream, launch, …) × N on device; window = app signpost
cross-check: two tools on one interval
```

### 3-4. 보안
```
static: analyzer rulesets → JSON; dependency audit; SBOM
dynamic: for payload in corpus: assert no_exec, no_nav, no_external, limits
sanitizers: full test suite under ASan, TSan
```

### 3-5. 보고서 파이프라인
```
raw → collect.py → data/*.csv → charts.py → assets/ → report.md → 사본·변환 → 검수
```

## 4. 작업 단계

| 단계 | 내용 | 산출물 |
|---|---|---|
| P0 | 환경·공용 입력 모음 | |
| P1 | 테스트 보강·결함 수정 | |
| P2 | 성능 하네스·측정 | |
| P3 | 보안 | |
| P4 | CI | |
| P5 | 보고서 | |

## 5. 보고서 목차 초안

<templates/report.md 참고>

## 6. 확정된 결정 (YYYY-MM-DD)

| # | 항목 | 결정 |
|---|---|---|
| 1 | 양식 | |
| 2 | 결함 수정 범위 | |
| 3 | 저장소 변경(커밋·태그) | |
| 4 | 도구 설치 | |
| 5 | 실기기 | |
| 6 | 퍼징 규모 | |

## 7. 리스크

| 리스크 | 대응 |
|---|---|
| 최소 OS 런타임 확보 실패 | "선언값 미검증"으로 기록 |
| 결함 다수 발견으로 기간 초과 | 전부 수정하되 단계 기간 조정, 진행 기록 |
| 세션 한도 | 파일 기반 체크리스트, 단계별 커밋 분리 |

## 8. 도구 설명

<도구마다 무엇·왜·설치. templates/tool-card.md>

## 9. 진행 체크리스트

- [ ] P0
- [ ] P1
- [ ] P2
- [ ] P3
- [ ] P4
- [ ] P5
