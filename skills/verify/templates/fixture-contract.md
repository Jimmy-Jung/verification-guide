# 공용 입력 모음(코퍼스) 계약

정본 저장소: <저장소>. 다른 저장소는 `fixtures_manifest.py --check`로 대조한 뒤 쓴다.

## 1. 디렉터리

| 폴더 | 범주 | 검사 |
|---|---|---|
| `spec/` | 공개 명세 예제 | 무크래시, 시간 상한, 플랫폼 간 비교(패리티) 입력 |
| `domain/` | 도메인 경계 사례 | 기대 조건 |
| `unicode/` | 결합 문자·RTL·ZWJ·BOM·CRLF·zero-width | 기대 조건 |
| `streaming/` | 중간 상태(닫히지 않은 구조) | 조각 누적 == 전체 |
| `security/` | 링크 스킴·HTML·공격 입력 | 정책 준수 |
| `pathological/` | 극단 입력 생성 규칙(`*.gen.json`) | 시간 예산 |
| `regressions/` | 결함별 최소 재현(`<seed>-<n>` 또는 `<id>`) | 기대 결과 |
| `manifest.json` | 파일·바이트·SHA-256 | CI 해시 검사 |

## 2. 사이드카 `.meta.json` (선택)

```json
{ "category": "unicode", "expect": { "blocks": 3, "text_preserved": true }, "budget_ms": 500, "note": "..." }
```

## 3. 정규화 결과 (플랫폼 중립 JSON)

블록 종류·순서, 글자, 강조 범위, 링크 주소(정규화 규칙 명시), 특수 구간, 표 크기만 남긴다. 픽셀·레이아웃은 제외.

```json
{ "blocks": [ { "type": "paragraph", "text": "...", "spans": [ ... ] } ], "limits_hit": [] }
```

## 4. 러너 동작

- 모든 테스트 입력을 읽어 `<out>/<platform>/<상대경로>.json`을 쓴다.
- 시간 상한 초과 시 같은 입력을 3회 재측정, 최솟값으로 판정.
- 환경 변수로 출력 폴더·퍼징(fuzz 테스트) 규모·시드·덤프 여부를 받는다.

## 5. 극단 입력 생성 규칙 (`pathological/*.gen.json`)

```json
{ "kind": "nested_list", "depth": 500, "budget_ms": 3000 }
```

## 6. 퍼징 생성기 (두 플랫폼 동일 결과)

SplitMix64, 기본 시드 <값>. 변형 6종: 기호 삽입(풀 N개), 글자 삭제, 구간 복제(≤64), 구분자 삭제, 줄바꿈 변형, prefix 자르기. 1~8회 적용. 덤프 형식 `fuzz-<seed>.jsonl`: `{ "n": 1, "input": "...", "norm": { ... } }`.

## 7. 렌더 수준 스트리밍 검사 (코어 밖)

조각 크기 {1, 7, 64, 1024, (긴 입력) 4096}. 플랫폼 뷰 종류별로.

## 8. 보안 페이로드 (`security/`)

페이로드마다 기대 판정: 실행 없음 · 설정 변경 거부 · 외부 요청 0건 · 상한 거부.
