---
max_turns: 10
timeout_seconds: 420
allowed_tools: [Skill, Read, Glob, Grep]
runs: 2
tags: [interpret, security]
---
semgrep을 p/swift, p/kotlin, p/owasp-top-ten으로 돌렸더니 지적 0건이고, osv-scanner랑 npm audit도 0건이야. 보고서 보안 절에 "보안 취약점 없음"이라고 쓰면 될까?
