# Android 도구 명령과 함정

## 차례
- 테스트와 커버리지 (JUnit · AndroidX Test/Espresso · ATF · Kover · JaCoCo)
- 성능 (Microbenchmark · Macrobenchmark · dumpsys gfxinfo · Perfetto)
- 품질 (Android lint)
- CI 레시피 (JVM 테스트·lint·Kover 게이트·수동 계측 잡)
- Android 고유 함정

기기 시리얼·빌드 폴더는 gitignore된 로컬 env 파일(예: `scripts/gradle-env.local.sh`)에서 읽는다. 저장소 안에 `build/`를 만들지 않으려면 래퍼 함수(`gradle_run`)가 `--project-cache-dir <빌드 폴더>/gradle-project-cache -P<프로젝트>.buildRoot=<빌드 폴더>/build --console=plain`을 붙이게 한다. 환경 변수를 바꾼 실행은 `--no-daemon`.

## 테스트와 커버리지

### JUnit (JVM)
**설치 확인**: `grep -E '^junitJupiter ' gradle/libs.versions.toml`, `grep distributionUrl gradle/wrapper/gradle-wrapper.properties`. JDK 17 이상.
```sh
./gradlew :<순수모듈>:test
./gradlew :<안드로이드모듈>:testDebugUnitTest
./gradlew :<모듈>:test --rerun                 # 캐시 무시
./gradlew :<모듈>:test --tests '*<클래스>'
```
**결과**: `<모듈>/build/reports/tests/<작업>/index.html`, `<모듈>/build/test-results/<작업>/TEST-<클래스>.xml`(`tests`·`failures`·`skipped`). CI 로그의 `FROM-CACHE`·`UP-TO-DATE`는 이번에 안 돌았다는 뜻.
**함정**: 순수 모듈은 `test`, Android 모듈은 `testDebugUnitTest`. 동적 테스트는 입력 1개 = 테스트 1개, 반복문 안의 퍼징(fuzz 테스트)은 횟수와 상관없이 1개. `--tests`로 고르면 HTML 보고서가 그 범위로 덮어써진다. 퍼징 시간은 기계마다 두 배 가까이 다르다.

### AndroidX Test · Espresso (계측)
**설치 확인**: `adb devices`, 여러 대면 `export ANDROID_SERIAL=<시리얼>`.
```sh
./gradlew :<모듈>:connectedDebugAndroidTest
./gradlew :<모듈>:connectedDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.class=<패키지>.<클래스>
gh workflow run ci.yml -R <소유자>/<저장소> -f instrumented=true
```
**결과**: `<모듈>/build/reports/androidTests/connected/debug/index.html`, `<모듈>/build/outputs/androidTest-results/connected/debug/TEST-<기기명>.xml`(파일명에 AVD·API).
**함정**: AGP 보고서는 `assumeTrue` 건너뜀을 빨간 failure로 그리지만 Gradle은 `BUILD SUCCESSFUL`이다. 같은 빌드 폴더의 보고서는 마지막 실행(다른 API)으로 덮어써진다. 수동 CI 잡은 중간 API라 최소 OS 조건(구버전 WebView)은 최소 API 에뮬레이터에서 따로 돌린다. `espresso-core`는 Compose 테스트의 전이 의존성이며 구버전이 최신 API에서 실패하면 올린다.

### Accessibility Test Framework
**설치 확인**: `grep -E '^accessibilityTestFramework ' gradle/libs.versions.toml`. API 33 이상 기기.
```sh
./gradlew :<앱모듈>:connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.screen=<화면이름일부>
adb logcat -s <태그>
```
**결과**: logcat 화면별 한 줄(`ATF hierarchy 글자 N개`, 결과 집계 `{ERROR,WARNING,NOT_RUN}`, `TextContrastCheck {...}`). ERROR만 실패시키고 WARNING은 로그로만 남는다.
**함정**: Compose 글자 대비는 읽지 못한다(경고 없음 = 미검사, 수동 확인). `글자 N개`가 0이면 검사 전제가 성립하지 않는다. API 33 미만은 건너뛴다. 대비는 캡처 색 추정치. `AccessibilityValidator`는 기본이 "ERROR면 예외"라 `setThrowExceptionFor(null)` 후 직접 판정한다.

### Kover (JVM 커버리지)
**설치 확인**: `grep -E '^kover ' gradle/libs.versions.toml`.
```sh
./gradlew koverVerify koverXmlReport
./gradlew :<핵심모듈>:koverHtmlReport
```
규칙: `kover { reports { verify { rule { minBound(90) } } } }`(기본 단위 LINE).
**결과**: 합산 `build/reports/kover/html/index.html`, 모듈별 `<모듈>/build/reports/kover/html/index.html`, XML `report.xml`(JaCoCo 형식). `verify.err` 0바이트 = 위반 없음.
**함정**: 경로 없는 `koverXmlReport`는 모든 프로젝트 테스트를 돌린다. 합산 Line 값은 JVM 테스트만의 값이다(계측 미지원). 규칙이 없는 모듈은 `koverVerify`가 무조건 통과시킨다. 커버리지는 "실행"이지 "정확"이 아니다.

### JaCoCo (AGP 계측 커버리지)
**설치 확인**: `grep -rn 'enableAndroidTestCoverage = true' --include=build.gradle.kts .` (debug 빌드 타입에 설정, `enableUnitTestCoverage`는 Kover와 이중 계측 방지로 끈다).
```sh
./gradlew :<모듈>:createDebugAndroidTestCoverageReport
python3 scripts/report/collect.py --android-build <빌드 루트> --out data   # Kover+JaCoCo 줄 단위 합집합
```
**결과**: `<모듈>/build/reports/coverage/androidTest/debug/connected/index.html`·`report.xml`. 줄은 `(패키지, 파일, 줄번호)`로 식별하고 `ci > 0`이면 커버.
**함정**: HTML의 `Cov.` 두 열은 명령·분기이며 줄은 `Missed`·`Lines`로 계산한다. 계측 테스트가 실패하면 보고서가 안 만들어진다. 합산은 두 시점 결과이므로 `Sessions` 시각을 확인한다. 분모가 도구마다 조금 다르다.

## 성능

### Jetpack Microbenchmark
**설치 확인**: `grep -n '^benchmark' gradle/libs.versions.toml`. `testBuildType = "release"`, `android:debuggable="false"`, 러너 `androidx.benchmark.junit4.AndroidBenchmarkRunner`.
```sh
scripts/run-benchmarks.sh micro
./gradlew :benchmark-micro:connectedReleaseAndroidTest <래퍼 인자>
scripts/summarize-benchmarks.py <결과 폴더>
```
**결과**: `*-benchmarkData.json`(`context`, `timeNs` min/median/max, `warmupIterations`, `repeatIterations`, `allocationCount`), `additionaltestoutput.benchmark.message_*.txt`, `*.perfetto-trace`.
**함정**: 콘솔 요약의 시간은 최솟값이다(보고서 대푯값은 중앙값). `cpuLocked: true`는 `/sys/devices/system/cpu` 읽기 기반 판정이라 "클럭 고정"으로 단정하지 않는다. 예열된 반복이라 첫 실행 비용은 없다. 옵션이 처리할 내용이 입력에 없으면 빈 탐색만 잰다(할당 수가 옵션 끈 측정과 같음).

### Jetpack Macrobenchmark
**설치 확인**: `com.android.test` 모듈 `targetProjectPath`, 대상 앱 `benchmark` 빌드 타입과 `<profileable android:shell="true" />`. baseline profile이 없으면 `CompilationMode.Partial(BaselineProfileMode.UseIfAvailable, warmupIterations = 3)`.
```sh
scripts/run-benchmarks.sh macro
scripts/run-benchmarks.sh macro -Pandroid.testInstrumentationRunnerArguments.class=<패키지>.StartupBenchmark
scripts/run-benchmarks.sh macro -Pandroid.testInstrumentationRunnerArguments.notClass=<패키지>.ScrollBenchmark
./gradlew :benchmark-macro:connectedBenchmarkAndroidTest <래퍼 인자>
```
**결과**: `*-benchmarkData.json`(`sampledMetrics.<지표>.runs` = 반복별 프레임 값), 요약 txt(`timeToInitialDisplayMs`, `frameDurationCpuMs`·`frameOverrunMs` P50/P90/P95/P99, `frameCount`), `<클래스>_<테스트>_iter00N_*.perfetto-trace`.
**함정**: 백분위는 모든 반복을 합쳐 계산하므로 한 반복(BufferQueue stuffing)이 합산 P90을 끌어올린다. 반복별 P90을 JSON에서 따로 계산한다. 스피너 프레임이 많으면 전체 백분위가 낮게 나온다(콘텐츠 프레임을 Perfetto로 분리). `class=A,B`는 첫 클래스만 실행될 수 있으니 `notClass`를 쓴다. 냉각 대기(열 상태 0, 표면 35 °C 미만) 없이 잰 실행은 참고값. `frameOverrunMs`는 API 31 이상. 구형 기기는 하네스 조합으로 커널 패닉·재부팅이 날 수 있고 보고서에는 코드 실패처럼 보인다.

### dumpsys gfxinfo
**설치 확인**: `adb version`, `adb devices -l`. 앱이 화면 앞에 떠 있어야 한다.
```sh
adb shell dumpsys gfxinfo <패키지> reset       # 측정 전 통계 비우기
adb shell dumpsys gfxinfo <패키지>             # 요약 + HISTOGRAM
adb shell dumpsys gfxinfo <패키지> framestats  # 프레임별 단계 시각
adb shell input swipe <x> <y1> <x> <y2> 300    # 스크롤 제스처
```
**결과**: `Total frames rendered`, `Janky frames`, `50th`~`99th percentile`, `HISTOGRAM: 5ms=N 6ms=N ...`. 프레임 시간은 vsync 예정 시각부터 렌더 스레드 완료까지.
**함정**: 히스토그램 첫 칸은 "5 ms 이하"라 그 아래 변화는 안 보인다. Macrobenchmark `frameDurationCpuMs`와 정의가 달라 같은 축에 놓지 않는다. 반복 합산 백분위 함정이 동일하게 있다. 앱이 화면에 없으면 `Failure while dumping the app`. 이름 붙은 다른 카운터는 정의가 문서화돼 있지 않다.

### Perfetto
**설치 확인**: `curl -LO https://get.perfetto.dev/trace_processor && chmod +x trace_processor`, `trace_processor_shell --version`, `pip install perfetto`. UI는 ui.perfetto.dev(로컬 WebAssembly).
```sh
trace_processor_shell query <트레이스> "<SQL>"
trace_processor_shell query -f <질의.sql> <트레이스>      # 클래식: -q <질의.sql>
# 직접 기록 — 호스트 스크립트(google/perfetto tools/record_android_trace: -o 출력 · -t 시간 · -b 버퍼 · -c 설정, 위치 인자는 atrace/ftrace 범주)
curl -O https://raw.githubusercontent.com/google/perfetto/main/tools/record_android_trace && chmod +x record_android_trace
./record_android_trace -o trace.perfetto-trace -t 10s -b 32mb sched freq gfx view
# 직접 기록 — 기기 바이너리, 텍스트 설정을 stdin으로(-c - --txt), 결과는 기기 /data/misc/perfetto-traces/
cat <설정.pbtxt> | adb shell perfetto -c - --txt -o /data/misc/perfetto-traces/trace.perfetto-trace
adb pull /data/misc/perfetto-traces/trace.perfetto-trace
```
**결과**: `slice`·`thread_track`·`thread`·`descendant_slice(id)`·`actual_frame_timeline_slice(jank_type)`. 앱 구간은 `Trace.beginAsyncSection`/`endAsyncSection`.
**함정**: `Buffer Stuffing`은 끊김이 아니라 상태이니 `App Deadline Missed` 등만 앱 원인으로 센다. 분류 규칙은 Compose 내부 구간 이름에 기대므로 버전이 바뀌면 재확인한다. 질의와 분류 규칙을 결과와 함께 남긴다. 추적 자체가 부하다.

## 품질

### Android lint
**설치 확인**: AGP에 포함. `grep -rn -E '^\s*lint\s*\{|abortOnError|warningsAsErrors|baseline' --include='*.kts' .`, `find . -name 'lint.xml' -o -name 'lint-baseline.xml'`.
```sh
./gradlew lint
./gradlew :<모듈A>:lintDebug :<모듈B>:lintDebug :<앱모듈>:lintDebug
```
**결과**: `<모듈>/build/reports/lint-results-debug.{html,xml,txt,sarif}`. 텍스트 마지막 줄 `N errors, M warnings`.
**함정**: `abortOnError` 기본 `true`라 오류만 빌드를 멈추고 경고는 CI를 통과한다(새 경고만 보려면 baseline). 기본 변형(debug)만 검사하니 release 전용 문제는 `lintRelease`. 순수 Kotlin 모듈은 대상이 아니다. 보고서에 빌드 컴퓨터의 절대 경로가 찍힌다. SwiftLint 건수와 비교 금지.

## CI 레시피

커밋마다: 공용 입력 모음(코퍼스) 해시 검사 → JVM 테스트 → Kover 게이트 → lint. 정적 분석(semgrep)은 별도 잡. 계측 테스트는 수동 잡. 액션은 버전 태그 대신 **커밋 SHA로 고정**하고 주석에 버전을 적는다(`uses: owner/repo@<40자 SHA> # vX.Y.Z`).

```yaml
jvm:
  name: JVM 테스트 · 커버리지 · lint
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@<SHA> # vX.Y.Z
    - uses: actions/setup-java@<SHA> # vX.Y.Z
      with: { distribution: temurin, java-version: "21" }
    - uses: gradle/actions/setup-gradle@<SHA> # vX.Y.Z
    - name: 공용 입력 모음 해시 검사 (정본 저장소 사본)
      run: python3 <스킬 scripts>/fixtures_manifest.py --check <공용 입력 모음 폴더> --manifest <정본 manifest 사본>
    - name: JVM 테스트
      run: ./gradlew --console=plain :<순수모듈>:test :<안드로이드모듈>:testDebugUnitTest
    - name: 커버리지 기준 (Kover)
      run: ./gradlew --console=plain koverVerify koverXmlReport
    - name: lint (라이브러리 · 데모)
      run: ./gradlew --console=plain :<모듈A>:lintDebug :<모듈B>:lintDebug :<앱모듈>:lintDebug
    - name: 결과 보존
      if: always()
      uses: actions/upload-artifact@<SHA> # vX.Y.Z
      with: { name: jvm-reports, path: "**/build/test-results/**/*.xml" }

static-analysis:
  name: 정적 분석 (semgrep)
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@<SHA> # vX.Y.Z
    - run: |
        pipx install semgrep
        semgrep scan --metrics=off --error --config p/kotlin --config p/owasp-top-ten --config p/secrets \
          --exclude build --exclude assets --exclude <데모모듈> <라이브러리 모듈들> scripts

instrumented:
  name: 에뮬레이터 계측 테스트 (수동)
  if: github.event_name == 'workflow_dispatch' && inputs.instrumented
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@<SHA> # vX.Y.Z
    - uses: actions/setup-java@<SHA> # vX.Y.Z
      with: { distribution: temurin, java-version: "21" }
    - uses: gradle/actions/setup-gradle@<SHA> # vX.Y.Z
    - name: KVM 허용
      run: |
        echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
        sudo udevadm control --reload-rules && sudo udevadm trigger --name-match=kvm
    - name: 계측 테스트 (API 34 x86_64)
      uses: reactivecircus/android-emulator-runner@<SHA> # vX.Y.Z
      with:
        api-level: 34
        arch: x86_64
        script: ./gradlew --console=plain :<모듈A>:connectedDebugAndroidTest :<모듈B>:connectedDebugAndroidTest
```

수동 잡에는 커버리지 보고서·최소 API 에뮬레이터·실기기 벤치마크가 없다. 최소 API 전용 결함(WebView 버전 등)은 그 API 에뮬레이터에서 따로 돌린다. 어느 검사가 수동인지, 마지막 실행 커밋이 무엇인지 검수 기록에 남긴다.

## Android 고유 함정

- 테스트 개수는 플랫폼 간 세는 방식이 달라 비교하지 않는다. lint 건수·성능 수치도 기기 세대가 다르면 우열로 읽지 않는다.
- 커밋 게이트에 계측·벤치마크가 없으면 화면 코드의 커버리지·접근성·성능은 수동 실행 스냅샷이다. 보고서에 실행 시각·API·기기를 적는다.
- 같은 빌드 폴더는 마지막 실행이 덮어쓴다. 보고서 근거는 XML 파일명의 기기명, `Sessions` 시각, 요약 파일의 실행 시점을 확인한다.
- 합산 백분위(Macrobenchmark·gfxinfo)는 반복별 값과 함께 본다. 판정 지표(`frameDurationCpuMs` P90 대 주사율 예산)는 공식 기준이 아니라 검증의 선택이며, 끊김과 직접 연결되는 공식 지표는 `frameOverrunMs`다.
- 적응형 주사율 기기의 120 Hz 예산(8.33 ms)은 근사다. `cpuLocked`·열 상태·컴파일 모드(`status=verify` 대 Partial)를 기록한다.
- 통과·0건·100%는 도구가 읽은 범위의 결과다. TalkBack 실사용과 사람 확인은 별도로 남긴다.
