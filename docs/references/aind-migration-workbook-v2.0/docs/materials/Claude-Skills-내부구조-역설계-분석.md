# Claude Skills 해부: 프롬프트부터 실전까지, 개발자가 분석한 AI 워크플로우

> **출처**: [AI Sparkup](https://aisparkup.com/posts/7032) / 원글: [leehanchung.github.io](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

---

## 핵심 요약

개발자 Han-chung Lee가 Claude Skills의 내부 구조를 역설계(reverse engineering)한 심층 분석. Skills는 코드가 아니라 **대화 맥락에 주입되는 특수한 프롬프트 템플릿**이며, 메타-툴 아키텍처, 이중 메시지 구조, contextModifier를 통해 도구 권한과 모델까지 동적으로 변경한다.

---

## Skills는 코드가 아니라 프롬프트다

한 줄 요약: **"Skills는 실행 가능한 코드가 아니라 대화 맥락에 주입되는 특수한 프롬프트 템플릿이다."**

- Python/JavaScript를 실행하지 않고, HTTP 서버를 띄우지도 않음
- 도메인 특화 지시사항을 대화 맥락에 주입 → Claude의 행동 방식 변경

**일반 툴 vs Skills 비교**

| 구분 | 일반 툴 (Read, Write, Bash) | Skills |
|------|---------------------------|--------|
| 동작 방식 | 즉각적인 동작 실행 후 결과 반환 | Claude를 특정 문제에 "준비"시킴 |
| 예시 | 파일 읽기, 명령 실행 | "PDF 전문가로서 작동하라" 지시 주입 |

---

## 메타-툴 아키텍처: Skill 안에 skills가 있다

Skills 시스템의 핵심 설계:
- **대문자 `Skill` 툴** → 개별 skills(pdf, skill-creator, internal-comms 등)을 관리하는 컨테이너
- Claude는 세 가지를 받음: 사용자 메시지 + 일반 도구들 + Skill 툴

**라우팅 방식**: 알고리즘 없음. 임베딩도, 분류기도, 패턴 매칭도 없음.
- **순수하게 LLM 추론만으로** Skill 툴 설명의 리스트를 읽고 사용자 의도와 매칭
- "로그 작성 skill을 만들어줘" → Claude가 internal-comms skill이 맞다고 판단해서 호출

---

## 두 개의 메시지: 보이는 것과 보이지 않는 것

Skill 실행 시 대화 기록에 두 개의 사용자 메시지가 주입됨:

**메시지 1** (`isMeta: false` → UI에 표시)
```xml
<command-message>The "pdf" skill is loading</command-message>
<command-name>pdf</command-name>
<command-args>report.pdf</command-args>
```
- 사용자는 "PDF skill이 로딩 중"이라는 상태만 봄 (50~200자)

**메시지 2** (`isMeta: true` → API에는 전송, UI에는 숨김)
- SKILL.md 파일의 전체 내용 로드
- 500~5,000단어에 달하는 상세 가이드: 작업 맥락, 워크플로우, 도구, 출력 형식, 환경별 경로 등

> **이 설계의 이유**: 하나로 통합하면 수천 단어의 AI 지시사항이 사용자 채팅창에 쏟아지거나, 어떤 skill이 실행되는지 전혀 알 수 없는 두 가지 문제 중 하나를 선택해야 하기 때문

---

## SKILL.md 구조

```
---                          ← 프론트매터 (YAML): "어떻게" 실행할지
name: skill-name
description: "..."           ← 가장 중요! Claude가 skill 선택 시 주요 신호
allowed-tools: "Read,Write,Bash(git status:*),Bash(git diff:*)"
model: claude-opus-4-20250514  ← 선택사항, 복잡한 작업용
---

# 마크다운 콘텐츠             ← "무엇을" 할지 Claude에게 전달하는 실제 프롬프트
```

**프론트매터 필드 설명**

| 필드 | 설명 |
|------|------|
| `description` | Claude가 skill 선택 시 주요 신호. 명확하고 행동 지향적 언어 권장 |
| `allowed-tools` | 사용자 승인 없이 쓸 수 있는 도구. 넓게 줄 수도, 특정 명령만 허용할 수도 있음 |
| `model` | 기본값은 현재 세션 모델 상속. 복잡한 작업엔 강력한 모델 지정 가능 |

**마크다운 콘텐츠 작성 팁**
- 5,000단어 이내 유지
- 명령형 언어 사용
- 상세 내용은 외부 파일 참조
- `{baseDir}` 변수로 skill 설치 디렉토리 동적 참조

---

## 실행 맥락 수정: contextModifier

Skill 호출 시 프롬프트 주입 + **도구 권한 변경 + 모델 전환**까지 수행:

```javascript
contextModifier(context) {
  let modified = context;

  if (allowedTools.length > 0) {
    modified = {
      ...modified,
      async getAppState() {
        const state = await context.getAppState();
        return {
          ...state,
          toolPermissionContext: {
            ...state.toolPermissionContext,
            alwaysAllowRules: {
              ...state.toolPermissionContext.alwaysAllowRules,
              command: [
                ...state.toolPermissionContext.alwaysAllowRules.command || [],
                ...allowedTools  // 이 도구들을 사전 승인
              ]
            }
          }
        };
      }
    };
  }

  return modified;
}
```

- 권한은 **skill 실행 기간에만 유효**, 작업 끝나면 정상 복귀

---

## 리소스 번들링: 3가지 디렉토리

| 디렉토리 | 용도 | 특징 |
|----------|------|------|
| `scripts/` | Python/Bash 실행 스크립트 | 자동화, 데이터 프로세서, 검증기 |
| `references/` | Claude가 맥락에 읽어들일 문서 | 마크다운, JSON 스키마 → 토큰 소비함 |
| `assets/` | Claude가 경로만 참조하는 파일 | HTML 템플릿, CSS, 이미지 → 토큰 소비 안 함 |

> **팁**: 10KB 마크다운을 `references/`에 두면 토큰 소비, 10KB HTML 템플릿을 `assets/`에 두면 토큰 소비 없음

---

## 실전 활용 패턴

| 패턴 | 설명 | 용도 |
|------|------|------|
| 스크립트 자동화 | Python/Bash 스크립트로 다단계 작업 처리 | 복잡한 자동화 |
| 읽기-처리-쓰기 | 입력 읽기 → 변환 → 출력 쓰기 | 형식 변환, 데이터 정리 |
| 검색-분석-보고 | Grep → 파일 읽기 → 구조화된 보고서 | 코드베이스 분석 |
| 마법사 다단계 | 각 단계마다 사용자 확인을 받으며 진행 | 복잡한 인터랙티브 프로세스 |

---

## 한계와 트레이드오프

**한계**
- 동시성 안전하지 않음
- 호출마다 1,500토큰 이상의 오버헤드
- 모든 걸 프롬프트로 표현해야 하는 제약

**장점**
- 유연성, 안전성, 조합 가능성
- 사용자 통제권 유지 + 복잡한 워크플로우 자동화

**의미**: "모든 걸 자동화하라"가 아니라 **"중요한 결정은 사람이, 반복 작업은 AI가"** 하는 협업 모델. 그걸 코드가 아니라 프롬프트로 구현.

---

## 참고자료

- [Introducing Agent Skills](https://www.anthropic.com/news/skills) – Anthropic
- [Equipping Agents for the Real World with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) – Anthropic Engineering Blog
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code/overview)
- [Skill Creator Skill](https://github.com/anthropics/skills/tree/main/skill-creator) – GitHub

---

