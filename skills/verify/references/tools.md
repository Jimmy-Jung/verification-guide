# 도구 지도 — 질문 → 도구 → 한 줄 해석 → 함정

명령·설치·CI 레시피는 platform-ios.md · platform-android.md. 사람용 상세 설명은 플러그인 저장소 `docs/tools/`의 도구 문서 5편에 있다(에이전트 필수 아님).

## 차례
- 테스트
- 성능
- 보안
- 품질
- 보고
- 검증 방법에 속하는 스크립트

## 테스트

| 도구 | 답하는 질문 | 통과·0건의 뜻 | 함정 |
|---|---|---|---|
| Swift Testing · XCTest · XCUITest(iOS) | 코드가 기대 결과를 내는가, 화면이 접근성 감사를 통과하는가 | 해당 테스트가 명시한 조건과 맞는다 | 명세 예제는 기대 HTML과 대조하지 않고 무크래시·시간·정규화 출력만 검사할 수 있다. 테스트 개수는 플랫폼마다 세는 방식이 달라 비교하지 않는다 |
| JUnit · AndroidX Test · Espresso · ATF(Android) | 같은 질문 | 같음 | ATF는 Compose 글자 대비를 읽지 못한다. 접근성 0건은 보조 기술 실사용을 말하지 않는다 |

## 성능

| 도구 | 답하는 질문 | 값의 뜻 | 함정 |
|---|---|---|---|
| XCTest metrics(`measure`) | 함수 하나가 실기기에서 얼마나 걸리나 | 예열된 함수의 시간·CPU·메모리 | 화면 끊김·첫 실행 비용은 모른다 |
| Instruments · xctrace: Time Profiler | 시간이 어디로 갔나 | 1 ms 표본, 표본 수 = CPU 실행 ms(대기 제외) | 이름 문자열로 넓게 모은 합계는 믿지 않는다 |
| Instruments: Animation Hitches | 늦게 표시된 시간 | 끊김 시간 비율(hitch ms/s), 외부 기준과 직접 비교 | 측정 구간 길이·접근성 모드·시작 위상·목격자 규칙에 따라 회차마다 흔들린다. 빌드 비교는 메인 스레드 점유 시간(busy ms/s)·지연 초과 시간(late excess ms/s)과 함께 본다 |
| Instruments: Activity Monitor | 메모리가 느나 | physical footprint 시계열 | 늘지 않았다고 누수가 없다는 뜻은 아니다 |
| os_signpost | 구간이 몇 번, 얼마나 | 앱이 표시한 구간 합 | 측정 구간의 정본으로 쓴다 |
| xcprof | 트레이스 자동 요약 | 상위 프레임 inclusive | `inclusive_ms`는 시간이 아니라 추정치. 측정 구간 길이에 가까운 값이 나오면 그 신호다 |
| Jetpack Microbenchmark | 함수 지연(Android) | 중앙값·p99·할당 | `cpuLocked`는 라이브러리 판정값일 수 있다 |
| Jetpack Macrobenchmark | 앱 실행·프레임 시간 | 반복 합산 백분위 | 이상 반복 하나가 P90을 끌어올린다. 공식 문서가 끊김과 직접 연결하는 지표는 `frameOverrunMs`다 |
| `dumpsys gfxinfo` | 스크롤 프레임 분포 | 히스토그램 백분위 | 5 ms 이하는 구분하지 못한다. Macrobenchmark 값과 같은 축이 아니다 |
| Perfetto | 느린 프레임이 왜 느린가 | 스레드·프레임 타임라인 | 교차 확인 계획에 있었는데 안 했으면 그 사실을 적는다 |

## 보안

| 도구 | 답하는 질문 | 0건의 뜻 | 함정 |
|---|---|---|---|
| semgrep | 알려진 위험 패턴이 있는가 | 규칙이 아는 모양이 없다 | Swift·Kotlin 전용 공개 규칙이 적다 → 보조 근거. 로그의 언어별 규칙 수를 적는다 |
| osv-scanner · npm audit | 의존성에 공개 취약점이 있는가 | 검사 시점 DB 기준으로 없다 | 커밋마다 검사와 수동 1회 검사를 구분한다 |
| cdxgen · CycloneDX SBOM | 무엇이 들어 있는가 | 목록일 뿐이다 | 안전 판정이 아니다 |
| AddressSanitizer · ThreadSanitizer | 실행 중 메모리 오류·경합 | 계측한 코드·실행 경로에서 탐지가 없다 | 미리 빌드된 바이너리·시스템 내부·누수 범위 밖. Debug 스택 넘침을 부수적으로 찾을 수 있다 |

## 품질

| 도구 | 답하는 질문 | 값의 뜻 | 함정 |
|---|---|---|---|
| xccov · Kover · JaCoCo | 테스트가 어느 줄을 실행했나 | 줄 커버리지 | 결과가 맞는지는 모른다. 중복 링크는 파일별 최댓값을 쓴다 |
| lizard | 함수가 얼마나 복잡한가 | 순환 복잡도 분포 | 평균을 쓰지 않는다. 분포와 상위 함수를 설명한다 |
| scc | 규모 | 줄 수 | 관리 부담의 경향만 보여 준다 |
| SwiftLint · Android lint | 스타일·플랫폼 위반 | 위반 수 | 결함 수가 아니다 |

## 보고

| 도구 | 답하는 질문 | 함정 |
|---|---|---|
| collect.py · charts.py · 문서 변환기 | 사람이 숫자를 옮겨 적지 않았나 | 재실행 동일성을 확인한다. 측정 정의가 맞는지는 따로 검증한다 |

## 검증 방법에 속하는 스크립트

플랫폼 간 비교(`fixtures-parity`), 퍼징 잔여 차이 분류(`fuzz-residual`), 공용 입력 모음(코퍼스) 해시(`fixtures_manifest`), 커버리지 게이트(`coverage_gate`), 벤치 집계(`bench_collect`)는 도구라기보다 방법의 일부다. correctness.md·maintenance.md에서 다룬다.
