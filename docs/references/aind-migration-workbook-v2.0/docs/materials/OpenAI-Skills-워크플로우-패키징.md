# OpenAI API의 Skills - 재사용 가능한 워크플로우 패키징

> 출처: https://aisparkup.com/posts/9256  

## Skills란 무엇인가

**Skills**는 재사용 가능한 절차(instructions + scripts + assets)를 하나의 패키지로 묶은 것입니다. 마치 작은 CLI 도구처럼 동작합니다.

### 구성
- **SKILL.md**: 중심 파일 (마크다운 + YAML 메타데이터)
- **스크립트**: 실행 가능한 코드
- **리소스**: 관련 자산들
- **배포**: 폴더 하나로 패키징

### 동작 방식
모델이 필요할 때만 skill을 불러와 실행합니다.

## 역사와 배경

### 기원
- **2025년 10월**: Anthropic이 처음 소개
- **이후**: [Agent Skills](https://agentskills.io) 오픈 스탠다드로 공개
- **2025년 12월**: OpenAI가 채택 (2개월 만에)
- **핵심 설계**: "폴더 하나에 마크다운 파일과 스크립트"라는 극도로 단순한 구조

### Simon Willison의 평가
> "Agent Skills가 MCP보다 더 큰 변화일 수 있다"

**이유:**
- **MCP**: 복잡한 프로토콜 스펙 (hosts, clients, servers, transports 등)
- **Skills**: "마크다운에 YAML 메타데이터 몇 줄"이 전부

## OpenAI의 3층 구조

OpenAI는 프롬프트, 툴, Skills를 명확히 구분합니다:

### 1. 프롬프트
- **역할**: 항상 적용되는 전역 행동과 제약
- **예시**: 안전 정책, 톤

### 2. 툴
- **역할**: 외부 서비스 호출, 부수 효과 발생
- **예시**: 이메일 전송, 주문 취소

### 3. Skills
- **역할**: 필요할 때만 실행되는 패키징된 절차
- **적합한 상황**:
  - 반복 가능한 워크플로우를 여러 에이전트/팀에서 공유
  - 복잡한 분기 로직 필요
  - 버전 관리가 중요
- **예시**: 회사 표준 보고서 생성, 데이터 정제 파이프라인

## API에서 Skills 사용하기

### 사용 방식

**1. Upload 방식**
```
POST /v1/skills
```
- skill을 먼저 업로드
- `skill_id`로 참조
- zip 파일 또는 개별 파일 모두 가능

**2. Inline 방식**
- API 요청에 base64로 인코딩한 zip 파일 직접 포함
- 별도 업로드 없이 바로 사용
- 간단한 테스트나 일회성 작업에 유용

### Shell 환경

**1. Hosted Shell (container_auto)**
- OpenAI 제공 샌드박스 환경

**2. Local Shell**
- 로컬 머신에서 직접 실행

**공통점**: skill 선택과 프롬프트 동작은 동일

## OpenAI만의 차별점

### Anthropic vs OpenAI

**Anthropic (원조)**
- Claude Desktop/웹 UI에서 작동
- 클라이언트 중심

**OpenAI (채택)**
- **API 레벨로 확장**
- Shell Tool과 통합
- 프로그래밍 방식 호출 가능
- hosted/local 환경 모두 지원
- **명시적 버전 관리**: `default_version`, `latest_version`

### Inline Base64 방식의 편의성
- 별도 업로드 없이 API 요청에 포함
- 간단한 테스트에 최적
- 빠른 프로토타이핑 가능

### 공통 요구사항
- **필수**: 파일시스템 접근 + 코드 실행 환경
- **최적 환경**: ChatGPT Code Interpreter, Claude Code 등

## 실무 활용 포인트

### 베스트 프랙티스

**1. 작은 CLI처럼 설계**
- 커맨드라인에서 실행 가능
- 명확한 출력
- 실패 시 명확한 에러 메시지

**2. 버전 관리**
- 프로덕션: 특정 버전 고정 (최신 버전 ✗)
- 예측 가능한 동작 보장
- 모델 버전 + skill 버전 함께 고정 → 재현 가능한 배포

**3. 중복 방지**
- 시스템 프롬프트에 절차 중복 금지
- 전체 절차를 프롬프트에 반복 시:
  - 재사용성 ✗
  - 버전 관리 ✗
  - 조건부 호출 ✗

### 공식 예제

**CSV 분석 skill**
- SKILL.md
- Python 스크립트
- requirements.txt
- zip으로 업로드

[OpenAI Cookbook 예제](https://developers.openai.com/cookbook/examples/skills_in_api)에서 전체 과정 확인 가능

## 왜 중요한가

### 프롬프트 복잡도 문제 해결
AI 에이전트 개발 시 프롬프트가 점점 길어지고 복잡해지는 문제를 Skills가 해결합니다.

### 재사용과 공유
- 팀/조직 간 워크플로우 표준화
- 버전별 관리로 안정성 확보
- 오픈 스탠다드로 생태계 확장

### 생태계 영향
- **2개월 만에 OpenAI가 채택** → 빠른 확산 가능성
- 단순한 설계 → 낮은 진입장벽
- MCP보다 실용적일 가능성

## 참고자료

- [Skills | OpenAI API](https://developers.openai.com/api/docs/guides/tools-skills/) – OpenAI Developer Documentation
- [Skills in OpenAI API](https://simonwillison.net/2026/Feb/11/skills-in-openai-api/) – Simon Willison
- [Claude Skills are awesome, maybe a bigger deal than MCP](https://simonwillison.net/2025/Oct/16/claude-skills/) – Simon Willison
- [OpenAI are quietly adopting skills](https://simonwillison.net/2025/Dec/12/openai-skills/) – Simon Willison

---

**핵심 요약:**
- Skills = 재사용 가능한 워크플로우 패키지
- 단순한 설계 (마크다운 + 스크립트)
- OpenAI가 API 레벨로 확장
- 프롬프트 복잡도 문제 해결
- MCP보다 실용적일 가능성
