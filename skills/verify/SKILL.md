---
name: verify
description: 소프트웨어 검증을 오류·성능·보안·유지보수 네 질문으로 계획하고, 실행하고, 측정값을 해석하고, 보고서로 만든다. 검증 계획, 테스트 전략, 벤치마크 설계, 성능 측정 해석, 보안 검증, CI 게이트, 결함 대장, 검증 보고서, 도입 검토 보고서 요청에 사용한다. 공용 입력 모음(코퍼스), 차등 테스트, 시드 고정 퍼징(fuzz 테스트), 극단 입력(pathological input), 실기기 반복 측정, 위협 모델, 커버리지·복잡도 게이트, 수치 파이프라인을 다루며 iOS·Android 도구 명령과 측정 함정을 둔다. 단위 테스트 한 개 작성, UI 자동화 조작, 그래프 렌더링 자체에는 쓰지 않는다.
license: MIT
metadata:
  author: JunyoungJung
  version: "0.1.0"
  created: "2026-10-22"
  updated: "2026-10-22"
---

# 검증 가이드 (Verification Guide)

검증을 네 질문으로 묶고 계획·실행·해석·보고 네 모드로 진행한다. 결과는 다시 실행할 수 있는 스크립트와 수치의 단일 출처로 남긴다.

## 언제 쓰나

- 라이브러리·앱·서비스의 검증 계획, 테스트 전략, 벤치마크 설계, 보안 검증, CI 게이트 설계
- 측정값이나 도구 출력의 해석 요청("이 숫자를 믿어도 되나", "0건이면 안전한가", "왜 회차마다 다르나")
- 검증 보고서, 관리자용 도입 검토 보고서, 결함 대장 작성

## 언제 쓰지 않나

- 단위 테스트 한 개를 쓰는 일(TDD 스킬), 기기 UI 자동 조작(기기 QA 스킬), 그래프·도식 렌더링(그림 스킬), 아키텍처 판정

## 네 질문

| ID | 질문 | 확인하는 위험 | 주된 방법 | 보완 방법 |
|---|---|---|---|---|
| Q1 오류 | 다양한·악의적·중간 상태 입력에서 크래시·멈춤·오표시가 없는가, 구현들이 같은 결과를 내는가 | 크래시, 멈춤, 데이터 손실, 구현 간 차이 | 공용 입력 모음(코퍼스), 차등 테스트, 시드 고정 퍼징(fuzz 테스트), 극단 입력 | 스트리밍 동등성, 렌더 스냅샷, 접근성 감사, 최소·최신 OS 실행 |
| Q2 성능 | 실제 사용 조건에서 지연·끊김·메모리·크기가 기준 안인가, 저사양에서도 그런가 | 지연, 프레임 끊김, 메모리 증가, 크기 | 실기기 Release 반복 측정, 외부 기준 | 회귀 방지 기준, 원리가 다른 도구의 교차 확인 |
| Q3 보안 | 신뢰할 수 없는 입력이 코드 실행·외부 요청·자원 고갈·메모리 오류로 이어지지 않는가, 공급망은 고정되는가 | 스크립트 실행, 외부 통신, 자원 고갈, 메모리 오류, 취약 의존성 | 위협 모델 → 공격 입력 동적 검증 | 정적 분석, 의존성 감사, SBOM, 새니타이저 |
| Q4 유지보수 | 검증이 자동으로 반복되는가, 코드가 사람이 관리할 수준인가 | 검증 미반복, 복잡한 코드 | CI 게이트, 커버리지 기준 | 복잡도 분포, 결함 대장 |

## 원칙 (모든 모드)

1. 작성 주체가 아니라 결과를 검증한다. "누가 썼나"를 "어떤 입력에서 깨지나"로 바꾼다.
2. 손으로 한 번 확인한 결과는 증거가 아니다. 스크립트로 고정하고 빠른 검사는 CI에 둔다.
3. 수치는 원시 결과 → 집계 스크립트 → CSV → 표·그래프 한 방향으로만 만든다. 본문 숫자를 직접 고치지 않는다.
4. 결함은 최소 재현 입력 → 수정 → 회귀 테스트 입력 → 전체 재실행 순서로 닫는다.
5. 대푯값은 중앙값이고 범위를 함께 적는다. 1회 값끼리 비교해 결론 내지 않는다.
6. 절대 성능은 실기기 Release 값만 인용한다. 시뮬레이터·Debug 값은 회귀 방지 기준에만 쓴다.
7. 판정 기준은 외부 기준(플랫폼 제작사·공식 문서)을 먼저 찾고, 직접 정한 값은 "회귀 방지 기준"이라고 부른다.
8. "0건"에는 도구의 시야를 붙인다. 예: "규칙이 아는 패턴 기준 0건".
9. 정의가 다른 지표를 한 축에 놓고 비교하지 않는다.
10. 확인하지 않은 범위와 남은 조건을 보고서에 적는다.

## 모드

요청을 아래 네 모드 중 하나로 분류하고, 해당 체크리스트를 복사해 진행 상황을 표시한다. 한 요청이 여러 모드에 걸치면 순서대로 진행한다.

### 1. 계획

```
계획 진행:
- [ ] 네 질문을 프로젝트 언어로 다시 쓴다 (templates/plan.md §2-1)
- [ ] 현재 상태 실측: 테스트 수·커버리지·성능 기록·보안 분석·CI·가용 환경(기기·런타임·도구)
- [ ] 질문마다 주된 방법·보완 방법·도구 선택 (references/correctness.md · performance.md · security.md · maintenance.md)
- [ ] 완료 기준이 있는 요구사항 표(FR 프로젝트 보강 · RR 보고서)
- [ ] 의사코드 수준 검증 설계, 작업 단계, 리스크와 대응
- [ ] 사용자 결정이 필요한 항목을 모아 한 번에 묻는다 (대상 범위·기기·도구 설치·결함 수정 범위·퍼징 규모·보고서 양식)
```

### 2. 실행

```
실행 진행:
- [ ] 공용 입력 모음 계약 → 해시 대조 → 러너 → 정규화 결과 → 비교 (references/correctness.md)
- [ ] 측정 전 함정 점검표 통과 (references/performance.md §측정 함정)
- [ ] 위협 모델 표 → 공격 입력 → 정적 분석·의존성 감사 (references/security.md)
- [ ] CI 게이트 기준과 검사 분할 (references/maintenance.md)
- [ ] 결함을 찾는 즉시 대장에 ID 부여 (references/defect-ledger.md)
- [ ] 측정마다 기기·OS·빌드 구성·날짜·커밋·원시 결과 경로 기록
```

플랫폼 명령은 [platform-ios.md](references/platform-ios.md), [platform-android.md](references/platform-android.md)를 연다. 둘 다 쓰는 프로젝트는 두 파일과 correctness.md의 차등 테스트 절을 함께 읽는다.

### 3. 해석

```
해석 진행:
- [ ] references/principles.md 해석 원칙 7개와 대조
- [ ] references/tools.md에서 해당 도구의 한 줄 해석과 함정 확인
- [ ] 반복 횟수·범위·환경이 결론을 지탱하는지 판단, 아니면 "잠정"으로 표시
- [ ] 측정 방법의 가정이 틀렸을 가능성을 references/performance.md §측정 함정과 대조
```

### 4. 보고

```
보고 진행:
- [ ] templates/report.md 목차로 구성 (references/report.md)
- [ ] 수치: 원시 결과 → scripts → CSV → 표·그래프. 본문 표는 CSV에서 옮기고 출처를 적는다
- [ ] 결함 대장을 부록으로, 재현 명령과 원시 데이터 위치를 부록으로
- [ ] "남은 조건·확인하지 않은 범위" 절 작성
- [ ] 공개 사본 규칙: 회사명·개인정보·내부 경로·볼륨 이름 제거
```

## 참고 파일

| 파일 | 내용 | 읽는 때 |
|---|---|---|
| [references/principles.md](references/principles.md) | 검증 원칙, 해석 원칙 7개, "0건" 문구 규칙, 판정 기준 출처, 반복 횟수 기본값 | 모든 모드 |
| [references/correctness.md](references/correctness.md) | 공용 입력 모음 계약, 차등 테스트, 속성 기반 퍼징, 극단 입력, 렌더 수준 검사, 최소·최신 OS | Q1 설계·실행 |
| [references/performance.md](references/performance.md) | 측정 원칙, 지표와 체감 대응, 판정 기준 출처, 교차 확인, 측정 함정 7종, 재측정 설계 | Q2 설계·실행·해석 |
| [references/security.md](references/security.md) | 위협 모델 양식, 공격 입력 동적 검증, 정적·의존성·SBOM 역할, 새니타이저 범위, 공급망 고정 | Q3 설계·실행 |
| [references/maintenance.md](references/maintenance.md) | 커버리지 게이트, 복잡도 분포, CI 분할 기준, 수동 잡, 브랜치 보호 확인 | Q4 설계·실행 |
| [references/defect-ledger.md](references/defect-ledger.md) | ID 체계, 표 열, 발견 경로, 수정 후 재실행과 출력 동일성 | 결함 첫 발견부터 |
| [references/report.md](references/report.md) | 계획·보고서 목차, 수치 파이프라인, 부록 구성, 독자별 파생본, 표기 규칙 | 계획·보고 |
| [references/tools.md](references/tools.md) | 질문 → 도구 → 한 줄 해석 → 함정 표 | 도구 선택·해석 |
| [references/platform-ios.md](references/platform-ios.md) | iOS 도구 명령, CI 레시피, iOS 고유 함정 | iOS 실행 |
| [references/platform-android.md](references/platform-android.md) | Android 도구 명령, CI 레시피, Android 고유 함정 | Android 실행 |

## 양식

| 파일 | 용도 |
|---|---|
| [templates/plan.md](templates/plan.md) | 검증 보강 계획 문서 |
| [templates/report.md](templates/report.md) | 검증 보고서 |
| [templates/defect-ledger.csv](templates/defect-ledger.csv) | 결함 대장 열 정의와 예시 행 |
| [templates/tool-card.md](templates/tool-card.md) | 도구 설명 문서 9절 |
| [templates/fixture-contract.md](templates/fixture-contract.md) | 공용 입력 모음 계약 README |

## 스크립트 (실행용, 읽지 않는다)

| 명령 | 하는 일 |
|---|---|
| `python3 scripts/fixtures_manifest.py <폴더>` / `--check <폴더>` | 공용 입력 모음의 파일·바이트·SHA-256 목록 생성, 다른 저장소 사본 대조 |
| `python3 scripts/coverage_gate.py <xccov.json\|kover.xml> --module <이름>=<기준> --total <기준>` | 모듈별 줄 커버리지 계산, 기준 미달이면 종료 코드 1 |
| `python3 scripts/bench_collect.py <로그...> --out results.json [--table]` | `BENCH <metric> <값> <단위>` 줄을 모아 중앙값·p90·최소·최대 집계 |

각 스크립트는 `--self-test`를 지원한다. 표준 라이브러리만 쓴다.

## 출력 규칙

- 기기는 모델·칩·출시 시기·OS 버전까지 적는다. "최신 기기" 같은 표현을 쓰지 않는다.
- 수치 옆에 환경(기기·OS·빌드 구성)·반복 횟수·날짜·커밋을 둔다. 추정값은 "추정"으로 표시한다.
- 측정 방법을 나중에 고쳤으면 고친 사실과 판정에 미친 영향 방향을 함께 적는다.
- 테스트 쪽 보정(기한 완화, 재측정 규칙)도 결함 대장에 남긴다. 결과가 좋아진 이유가 코드 수정인지 테스트 완화인지 구분되게 한다.
