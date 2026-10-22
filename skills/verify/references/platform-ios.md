# iOS 도구 명령과 함정

## 차례
- 테스트와 커버리지 (Swift Testing · XCTest · XCUITest 접근성 감사 · xccov)
- 성능 (XCTest metrics · xctrace 시나리오 · xcprof)
- 안전 (ASan · TSan)
- 품질 (SwiftLint)
- CI 레시피 (잡 구성·시뮬레이터 선택·결과 보존)
- iOS 고유 함정

빌드 산출물(`-derivedDataPath`)·결과 번들(`-resultBundlePath`)·로그는 저장소 밖 빌드 폴더에 둔다. 기기 식별자·서명 팀은 gitignore된 로컬 env 파일에서 읽는다. 모든 도구는 Xcode에 들어 있으며 설치 확인은 `xcodebuild -version`, `swift --version`.

## 테스트와 커버리지

### Swift Testing
**설치 확인**: `swift --version`. 패키지는 `swift-tools-version: 6.0` 이상.
```sh
xcodebuild test -scheme <패키지>-Package -skip-testing:<벤치마크 타깃> \
  -parallel-testing-enabled NO \
  -destination 'platform=iOS Simulator,name=<기기>,OS=<iOS>' \
  -resultBundlePath <빌드 폴더>/package.xcresult -enableCodeCoverage YES
xcodebuild test -scheme <패키지>-Package -only-testing:<테스트 타깃>   # 일부만
TEST_RUNNER_<변수>=<값> xcodebuild test ...                            # 환경 변수 전달
```
**결과**: 로그의 `Test run with N tests in M suites`(번들마다 1줄), `<함수> with N test cases`(매개변수), `** TEST SUCCEEDED **`. 집계는 `xcrun xcresulttool get test-results summary --path <xcresult>`.
**함정**: 환경 변수는 `TEST_RUNNER_` 접두사가 있어야 시뮬레이터의 테스트 프로세스에 전달된다. 매개변수 케이스 수는 로그 줄이 아니라 xcresult로 센다(인자에 줄바꿈이 있으면 줄 수로는 빠진다). 반복문 테스트는 결과가 1개이고 입력별 재실행이 안 되므로 메시지에 입력 번호를 넣는다. UIKit 의존 타깃은 `swift test`(macOS 호스트)로 검증하지 않는다. 스위트 안 테스트는 기본 병렬이라 시간 측정 스위트에는 `.serialized`를 붙인다.

### XCTest · xcresulttool
**설치 확인**: `xcrun xcresulttool version`.
```sh
xcodebuild test -project <앱>.xcodeproj -scheme <scheme> -testPlan <플랜> \
  -destination 'platform=iOS Simulator,name=<기기>,OS=<iOS>' -resultBundlePath <빌드 폴더>/app.xcresult
xcrun xcresulttool get test-results summary --path <xcresult>
xcrun xcresulttool get test-results tests --path <xcresult>
xcrun xcresulttool get test-results metrics --path <xcresult>
xcrun xcresulttool export attachments --path <xcresult> --output-path <폴더>
```
**결과**: summary의 `totalTestCount`·`passedTests`·`skippedTests`·`failedTests`와 `N tests ran with dynamic parameters · M test runs`.
**함정**: 번들마다 XCTest 실행기가 `Executed 0 tests`를 먼저 출력해도 Swift Testing만 있는 번들이면 정상이다. 건너뜀(`XCTSkip`·스냅샷 기기 불일치)은 통과가 아니다. `get object`는 사용 중단이라 `get test-results` 계열을 쓴다. 번들에는 기기 이름·로컬 경로가 있어 공유 전에 확인한다.

### XCUITest · 접근성 감사
**설치 확인**: 감사 API는 iOS 17 이상(그 미만은 `XCTSkip`).
```sh
xcodebuild test -project <앱>.xcodeproj -scheme <scheme> -testPlan <플랜> \
  -destination 'platform=iOS Simulator,name=<기기>,OS=<iOS>' \
  -only-testing:<UI 테스트 타깃>/<감사 클래스> -resultBundlePath <빌드 폴더>/ui.xcresult
```
**결과**: 로그의 `제외: …`(적용된 감사 예외), `Test Case … passed`, `Executed N tests, with K tests skipped and 0 failures`. 감사 3구성 = 라이트 · 다크(실행 인자) · 최대 글자(`-UIPreferredContentSizeCategoryName UICTContentSizeCategoryAccessibilityXXXL`).
**함정**: `continueAfterFailure = true`로 화면 하나의 실패가 나머지를 막지 않게 한다. 예외는 감사 종류·문구·요소를 좁혀 걸고 근거를 주석에 남긴다(종류 단위는 `.all.subtracting([.dynamicType, .textClipped])`). 화면에 보이는 요소만 검사하며 VoiceOver 실사용을 대신하지 못한다. UI 테스트가 켠 접근성 모드는 성능 측정값에 비용을 더한다. 공유 CI 러너에서는 WebView 초기화·감사 시간 초과로 흔들려 수동 잡으로 분리한다.

### xccov
**설치 확인**: `xcrun --find xccov`, `xcrun xcresulttool get content-availability --path <xcresult>`에서 `hasCoverage`.
```sh
xcrun xccov view --report --only-targets <xcresult>
xcrun xccov view --report --files-for-target <타깃> <xcresult>
xcrun xccov view --report --functions-for-file <파일>.swift <xcresult>
xcrun xccov view --archive --file-list <xcresult>
xcrun xccov view --archive --file <소스 절대 경로> <xcresult>      # 줄별 실행 횟수, 0이 미실행
xcrun xccov view --report --json <xcresult> > coverage.json
python3 scripts/coverage_gate.py coverage.json --module <핵심 모듈>=0.90 --total 0.80   # 스킬 폴더 기준 경로
```
**결과**: 타깃별 `비율 (실행/전체)`, JSON은 파일 단위 항목. `coverage_gate.py`의 종료 코드는 0 통과·1 미달(지정한 모듈이 보고서에 없을 때 포함)·2 입력 오류(파일 없음, 깨진 보고서, 모듈을 하나도 찾지 못함)이다. 기준값은 비율(0.80)로 쓴다.
**함정**: 테스트 실행에 `-enableCodeCoverage YES`가 필요하다. 정적 링크 때문에 같은 파일이 여러 타깃에 중복되고 핵심 모듈 행이 없을 수 있어 커버리지 게이트 스크립트는 `/Sources/` 파일만 고르고 파일별 최댓값으로 모듈 값을 다시 계산한다. `-skip-testing`한 타깃도 비율이 찍힌다(테스트 파일이 0%이면 미실행). 줄 커버리지는 분기·비Swift 자산을 보지 않는다. 로컬 래퍼의 기준이 CI와 다르지 않은지 확인한다.

## 성능

### XCTest metrics
**설치 확인**: 실기기는 개발자 모드·`DEVELOPMENT_TEAM`. SwiftPM 테스트 타깃은 기기에서 직접 못 돌므로 호스트 앱 프로젝트를 생성한다(`xcodegen`).
```sh
xcodebuild test -project <호스트>.xcodeproj -scheme <벤치마크 scheme> -configuration Release \
  -destination "id=<기기 식별자>" -derivedDataPath <빌드 폴더>/DerivedData \
  -resultBundlePath <빌드 폴더>/micro.xcresult -allowProvisioningUpdates DEVELOPMENT_TEAM=<팀>
python3 scripts/bench_collect.py <로그> --label "<기기>" --out results.json --table   # 테스트가 BENCH 줄을 찍을 때
xcrun xcresulttool get test-results metrics --path <빌드 폴더>/micro.xcresult      # BENCH 줄이 없으면 측정값을 직접 꺼낸다
```
**결과**: 로그의 `measured [Clock Monotonic Time, s] average … values: [...]`, `bench_collect.py`는 반복마다 출력한 `BENCH <지표> <값> <단위>` 줄을 모아 중앙값·p90·최소·최대를 낸다. 앱 실행은 `Duration (AppLaunch)`.
**함정**: `iterationCount + 1`번 실행하고 첫 값은 버린다. CPU·메모리는 기본이 프로세스 전체 값이다(`XCTCPUMetric(limitingToCurrentThread: true)`로 제한). 절댓값은 실기기 Release만 인용하고 시뮬레이터 Debug는 상대 비교용이다. 기준값을 안 두면 회귀를 자동으로 실패시키지 않는다. 새니타이저 실행에서는 시간 게이트를 건너뛴다(`dlsym`으로 `__asan_init`·`__tsan_init` 확인).

### xctrace
**설치 확인**: `xcrun xctrace version`, `xcrun xctrace list instruments`, `xcrun devicectl list devices`. 기기는 잠금 해제·충전·열 상태 정상.
```sh
xcrun xctrace record --device <하드웨어 UDID> --instrument "Time Profiler" --instrument Hitches \
  --time-limit 20s --no-prompt --output <폴더>/<시나리오>.hitches.trace --attach <앱>
xcrun xctrace record ... --launch -- <번들 ID> <앱 인자>           # 콜드 런치·자동 재생
xcrun xctrace export --input <트레이스> --toc   # 표 목록
xcrun xctrace export --input <트레이스> --xpath '/trace-toc/run[@number="1"]/data/table[@schema="hitches"]'
```
**결과**: 표 이름 `hitches`·`hitches-frame-lifetimes`·`time-profile`·`os-signpost-interval`. 끊김 시간 비율(hitch time ratio) = hitch 시간 합 ÷ 측정 구간 초(ms/s). 외부 기준은 Tech Talk 10855(5/10)와 Organizer(10/25/50)를 섞지 않는다.
**함정**: `--device`는 CoreDevice 식별자가 아니라 하드웨어 UDID. CPU Profiler는 Hitches·Activity Monitor와 한 녹화에 못 넣는다(묶음별 별도 실행). 기기가 잠기면 빈 트레이스. 같은 기기에 측정 둘을 겹쳐 돌리지 않는다(잠금 폴더). `xctrace export`는 segfault(종료 139)가 잦아 재시도, record가 멈추면 제한 시간 + 여유 뒤 SIGTERM. "device to boot" 시간 초과는 `devicectl`로 깨우고 재시도. Allocations는 export 불가. 요약 표는 트레이스 전체 범위이므로 측정 구간 기준 값과 구분한다. 고정 시간 구간보다 앱이 남긴 signpost 구간을 측정 구간으로 쓴다. hitch 수는 시작 위상(vsync 기준)과 화면의 다른 움직임에 따라 회차마다 크게 갈리므로 한 회차로 결론 내지 않는다. 트레이스 목차에 기기 이름이 있어 공유 전에 가린다.

### xcprof
**설치 확인**: `xcprof doctor --human`(Axiom 플러그인 안 `tools/xcprof`, 서드파티 `0.1.0-dev`).
```sh
xcprof analyze <트레이스> --json --dsym <dSYM> --start-ms <A> --end-ms <B>
xcprof compare <기준.trace> <현재.trace> --fail-on-regression --threshold-pct 5   # 회귀면 종료 3
```
**결과**: JSON `hot_frames[].inclusive_pct`·`self_pct`, `main_thread`, `notes`.
**함정**: `inclusive_ms`·`self_ms`는 표본 비율 × 측정 구간 길이의 추정치라 시간으로 인용하지 않는다(비율만 읽고 시간은 Time Profiler). `analyze`는 CPU Profiler만 읽는다(Time Profiler 트레이스는 표본 0). Release는 맞는 dSYM이 필요하며 빌드 직후 보존한다. 내부 export segfault는 재시도. 메인 스레드 후보 정지는 근삿값.

## 안전

### AddressSanitizer
```sh
xcodebuild test -scheme <패키지>-Package -destination "platform=iOS Simulator,id=<ID>" \
  -parallel-testing-enabled NO -skip-testing:<벤치마크 타깃> \
  -derivedDataPath <빌드 폴더>/DerivedData-address -resultBundlePath <빌드 폴더>/address.xcresult \
  -enableAddressSanitizer YES
grep -c "ERROR: AddressSanitizer" address.log
```
**결과**: `ERROR: AddressSanitizer <오류 종류> on address …` + 호출 스택, 보고 0줄이면 미탐지.
**함정**: 크래시가 나도 보고가 0줄이면 ASan이 키운 스택 프레임에 의한 스택 넘침일 수 있다. 누수·미초기화 읽기·정수 넘침은 찾지 않는다. 2–5배 느려져 시간 게이트는 건너뛴다. 계측되지 않은 XCFramework·시스템 프레임워크 내부는 못 본다. TSan과 한 빌드에 못 켜며 산출물 폴더를 나눈다.

### ThreadSanitizer
```sh
xcodebuild test -scheme <패키지>-Package -destination "platform=iOS Simulator,id=<ID>" \
  -parallel-testing-enabled NO -skip-testing:<벤치마크 타깃> \
  -derivedDataPath <빌드 폴더>/DerivedData-thread -resultBundlePath <빌드 폴더>/thread.xcresult \
  -enableThreadSanitizer YES
grep -c "WARNING: ThreadSanitizer" thread.log
```
**결과**: `WARNING: ThreadSanitizer: Swift access race` + 두 접근의 호출 스택·`SUMMARY:`.
**함정**: iOS 실기기에서는 못 쓴다(시뮬레이터·macOS만). `@unchecked Sendable`·`nonisolated(unsafe)` 면제 지점은 컴파일러가 안 보므로 TSan 대상이다(`grep`으로 먼저 센다). 실행 중 함께 일어난 접근만 비교하고 2–20배 느리다. `TEST FAILED`와 경합 보고는 별개이므로 종료 코드가 아니라 보고 줄 수로 판단한다.

## 품질

### SwiftLint
**설치 확인**: `swiftlint version`(`brew install swiftlint`).
```sh
swiftlint lint --quiet --reporter json Sources > swiftlint.json
jq -r '.[].rule_id' swiftlint.json | sort | uniq -c | sort -rn
swiftlint rules <규칙 이름>
swiftlint lint --write-baseline <파일>      # 이후 --baseline으로 새 위반만
```
**결과**: JSON `file`·`line`·`character`·`rule_id`·`severity`·`reason`, 종료 코드 2는 오류 있음.
**함정**: 설정 파일(`.swiftlint.yml`) 없이 돌린 건수는 기본 기준의 값이며 결함 개수가 아니다(한 글자 이름이 오류). 강제 캐스트는 건별로 판단한다(`layerClass` 대응 `layer as!`는 안전). 범위·커밋을 함께 기록한다.

## CI 레시피

- macOS 러너에서 `xcode-select`로 Xcode 버전을 고정한다. 패키지 테스트 잡은 설치된 iPhone 시뮬레이터 중 최신 iOS를 골라 `-destination "platform=iOS Simulator,id=<ID>"`로 넘긴다(`xcrun simctl list devices available -j`를 파싱).
- 커밋마다: 패키지 테스트(`-enableCodeCoverage YES` + 커버리지 게이트), 앱 단위 테스트(`-only-testing:<단위 타깃>`), 호스트 빌드(`swift build --target <Foundation 전용 모듈>`).
- 수동 입력(`workflow_dispatch`) 잡: UI·접근성 테스트(성능 전용 클래스는 `-skip-testing`), 새니타이저. 실기기 성능·xctrace는 CI 러너에 기기가 없어 릴리스 전 로컬에서 실행한다.
- 결과 보존: 잡마다 `.xcresult`와 로그를 `actions/upload-artifact`로 올리고 보관 기간(예: 14일)을 지정한다. 실패해도 올리도록 `if: always()`.
- 시간 게이트는 p50처럼 안정된 지표에 두고 새니타이저 런타임이 로드되면 건너뛴다.

## iOS 고유 함정

- `xcodebuild`로만 UIKit 의존 타깃을 검증한다. 호스트 `swift test` 통과는 근거가 아니다.
- 라이브러리 제품과 같은 이름의 스킴은 테스트 동작이 없을 수 있다. 패키지 전체는 `<패키지>-Package`.
- 시뮬레이터 Debug 값(CI 게이트·새니타이저)과 실기기 Release 값은 섞지 않는다. 스냅샷 기준 이미지는 특정 기기·OS 전용이므로 다른 환경에서는 건너뛴다.
- 결과 번들·트레이스·요약 JSON에는 기기 이름(소유자 이름 포함 가능)과 로컬 경로가 들어 있다. 공유 전에 가린다.
- 같은 빌드 슬롯을 다시 빌드해도 트레이스와 맞는 dSYM·git SHA를 결과 폴더에 남긴다.
