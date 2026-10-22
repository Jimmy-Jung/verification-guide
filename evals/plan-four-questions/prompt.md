---
max_turns: 12
timeout_seconds: 420
allowed_tools: [Skill, Read, Glob, Grep]
runs: 2
tags: [plan]
---
우리 팀이 만든 iOS·Android Markdown 렌더링 라이브러리를 다음 분기 서비스에 넣으려고 해. 팀장이 "AI 도구로 짠 코드라 오류·성능·보안이 걱정된다"고 해서 근거를 만들어야 해. 어떻게 검증할지 계획을 세워줘. 두 플랫폼 코드는 같은 설계를 Swift와 Kotlin으로 따로 구현했고, 테스트는 단위 테스트 300개쯤 있고 CI는 없어.
