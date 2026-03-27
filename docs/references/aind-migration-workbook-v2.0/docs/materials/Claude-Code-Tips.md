# Claude Code Tips - CLAUDE.md에 추가하면 좋은 규칙들

> **출처**: [X/Twitter @svpino](https://x.com/svpino/status/2018682144361734368)
> **작성자**: Santiago (@svpino) - AI/ML 엔지니어, 43만+ 팔로워

---

## 핵심 요약

Santiago가 Claude Code 사용 시 CLAUDE.md 파일에 추가해서 효과를 본 5가지 규칙. 코드 작성 전 승인 받기, 작은 단위로 나누기, 테스트 중심 개발 등 실용적인 프롬프트 엔지니어링 팁.

---

## 영문 원본 (Original English)

> **Claude Code tips that have made my life easier:**
> 
> (Add these to your CLAUDE.md file)
> 
> 1. "Before writing any code, describe your approach and wait for approval. Always ask clarifying questions before writing any code if requirements are ambiguous."
> 
> 2. "If a task requires changes to more than 3 files, stop and break it into smaller tasks first."
> 
> 3. "After writing code, list what could break and suggest tests to cover it."
> 
> 4. "When there's a bug, start by writing a test that reproduces it, then fix it until the test passes."
> 
> 5. "Every time I correct you, add a new rule to the CLAUDE.md file so it never happens again."
> 
> The wording in the file is much more detailed than what I wrote above, but hopefully these show the spirit.

---

## 한국어 번역

### Claude Code 사용을 편하게 만들어준 팁들

(CLAUDE.md 파일에 이 내용들을 추가하세요)

### 1. 코드 작성 전 승인 받기
> "코드를 작성하기 전에 먼저 접근 방식을 설명하고 승인을 기다려라. 요구사항이 모호하면 코드 작성 전에 항상 명확히 하는 질문을 해라."

**왜 중요한가**: AI가 잘못된 방향으로 코드를 대량 생성하는 것을 방지

### 2. 큰 작업은 나누기
> "3개 이상의 파일을 변경해야 하는 작업이면, 멈추고 먼저 더 작은 작업들로 나눠라."

**왜 중요한가**: 변경 범위 제한으로 디버깅과 리뷰 용이

### 3. 코드 작성 후 취약점과 테스트 제안
> "코드를 작성한 후, 무엇이 깨질 수 있는지 나열하고 그것을 커버할 테스트를 제안해라."

**왜 중요한가**: 선제적 품질 관리와 테스트 커버리지 향상

### 4. 버그 수정 시 테스트 우선
> "버그가 있으면, 먼저 그 버그를 재현하는 테스트를 작성하고, 테스트가 통과할 때까지 수정해라."

**왜 중요한가**: TDD 방식으로 회귀 버그 방지

### 5. 자가 학습 규칙
> "내가 너를 교정할 때마다, CLAUDE.md 파일에 새로운 규칙을 추가해서 다시는 같은 실수를 하지 않도록 해라."

**왜 중요한가**: 점진적으로 더 나은 AI 어시스턴트로 진화

---

## 적용 예시

```markdown
# CLAUDE.md

## 코드 작성 규칙

1. 코드 작성 전에 접근 방식을 설명하고 승인을 기다릴 것
2. 요구사항이 불명확하면 먼저 질문할 것
3. 3개 이상 파일 변경 시 작업을 분할할 것
4. 코드 작성 후 취약점과 테스트 제안할 것
5. 버그 수정 시 재현 테스트부터 작성할 것

## 학습된 규칙 (자동 추가됨)
- [날짜] ...
```

---

## 통계

- 💬 조회수: 139,294
- ❤️ 좋아요: 2,045
- 🔖 북마크: 4,040
- 🔄 리트윗: 183
- 📅 작성일: 2026-02-03

---

