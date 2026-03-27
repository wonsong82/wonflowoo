# Glossary

**Version**: 1.0.0
**Last Updated**: 2025-12-15

---

## A

### ADR (Architecture Decision Record)
아키텍처 결정 기록. 중요한 아키텍처 결정과 그 배경, 결과를 문서화한 기록.

### API Endpoint
클라이언트가 서버의 특정 기능에 접근하기 위한 URL과 HTTP 메서드 조합.

### Assessment
마이그레이션 프로젝트 시작 전 레거시 시스템의 규모, 복잡도, 실현 가능성을 평가하는 단계.

### Auto-to-Max
Choisor 옵션. 한 Feature의 현재 Phase 완료 후 자동으로 다음 Phase로 진행하여 최대 Phase까지 연속 처리.

---

## B

### Backward Validation
Ground Truth(소스 코드)에서 출발하여 생성된 스펙/코드의 완전성을 검증하는 방식.

### Batch Processing
여러 Feature를 그룹으로 묶어 일괄 처리하는 실행 방식.

### Bidirectional Validation
Forward Extraction과 Backward Validation을 모두 수행하여 완전성을 보장하는 검증 방식.

### Blocker
배포를 불가능하게 만드는 가장 심각한 수준의 이슈. 즉시 수정 필수.

### Business Logic
데이터 처리의 비즈니스 규칙과 계산 로직. 검증, 계산, 워크플로우 포함.

---

## C

### Checkpoint
작업의 중간 상태를 저장하여 실패 시 재개할 수 있게 하는 지점.

### Choisor
세션 기반 작업 오케스트레이션 도구. Feature 단위 상태 관리와 Phase 연속 처리 지원.

### Complexity Score
Feature의 복잡도를 0-100 점으로 정량화한 점수. 모델 선택과 작업 시간 추정에 사용.

### Context Budget
LLM이 한번에 처리할 수 있는 토큰 수 제한. 일반적으로 200K 토큰.

### Coverage Rate
전체 대상 중 처리/검증이 완료된 비율. 목표: 99%+.

### Critical Issue
심각한 기능 오류를 나타내는 이슈 수준. SQL 불일치, 필수 로직 누락 등.

### Cross-Domain Dependency
한 도메인의 Feature가 다른 도메인의 컴포넌트에 의존하는 관계.

---

## D

### Dataset
MiPlatform 프로토콜에서 사용하는 데이터 전송 단위. ds_search, ds_list 등.

### Deep Analysis
Feature의 모든 레이어(Controller → Service → MyBatis → VO)를 추적 분석하는 상세 분석.

### Domain
비즈니스 기능 영역. PA(구매), MM(자재), SC(공급망) 등.

### Domain Batch
동일 도메인의 모든 Feature를 그룹으로 묶어 처리하는 배치 전략.

### Dynamic SQL
MyBatis에서 조건에 따라 동적으로 생성되는 SQL. `<if>`, `<choose>`, `<foreach>` 태그 사용.

---

## E

### Endpoint Equivalence
레거시와 생성된 코드의 API 엔드포인트가 동등한지 검증하는 항목.

### Entity Service
4-Layer 아키텍처의 3번째 레이어. MyBatis 호출 담당.

### Escalation
해결되지 않는 문제를 상위 레벨로 전달하는 절차.

---

## F

### Feature
Screen ID를 기반으로 그룹핑된 API 엔드포인트 묶음. 마이그레이션의 기본 작업 단위.

### Feature Inventory
모든 Feature 목록과 메타데이터를 정리한 인벤토리.

### First Pass Success Rate
첫 번째 시도에서 검증을 통과한 Feature 비율. 목표: 85%+.

### Forward Extraction
레거시 코드에서 시작하여 스펙을 추출하는 방식.

### Functional Validation
생성된 코드가 레거시와 기능적으로 동등한지 검증하는 Phase.

---

## G

### Gap Analysis
Stage 1 스펙에서 누락된 항목을 식별하고 분석하는 Phase.

### Ground Truth
검증의 기준이 되는 소스 데이터. 일반적으로 레거시 소스 코드.

---

## H

### Haiku
Anthropic의 경량 AI 모델. 단순한 작업에 사용. 빠르고 비용 효율적.

### Hub Domain
다른 도메인들이 공통으로 의존하는 중앙 도메인. 예: CM(Common).

---

## I

### Integration Validation
전체 시스템의 빌드 성공과 모듈 간 호환성을 검증하는 Phase.

---

## L

### Layer
4-Layer 아키텍처의 각 계층. Controller, TaskService, EntityService, MyBatis/VO.

### Layered Loading
컨텍스트 관리를 위해 레이어별로 점진적으로 코드를 로드하는 전략.

### Legacy System
마이그레이션 대상이 되는 기존 시스템.

### Lessons Learned
프로젝트 경험에서 도출된 교훈과 개선점.

---

## M

### Major Issue
중요하지만 Critical보다는 덜 심각한 이슈 수준.

### MiPlatform
TOBESOFT의 데스크톱 클라이언트 프레임워크. Dataset 기반 프로토콜 사용.

### Mini-Pilot
전체 실행 전 파이프라인을 검증하기 위한 소규모 파일럿. 복잡도별 6개 Feature 샘플링.

### Minor Issue
사소한 차이점. 코드 스타일, 주석 등.

### Modular Monolith
마이크로서비스의 모듈성과 모놀리스의 단순성을 결합한 아키텍처.

### Modular Spec
300 lines 미만의 작은 파일들로 구성된 모듈형 스펙 구조.

### MTTR (Mean Time To Remediate)
문제 발견부터 해결까지 걸리는 평균 시간.

### MyBatis
XML 기반 SQL 매핑 프레임워크. 레거시 시스템에서 주로 사용.

---

## O

### Opus
Anthropic의 최고급 AI 모델. 복잡한 분석과 아키텍처 설계에 사용.

### Orchestrator
여러 세션과 작업을 조율하는 관리 도구. Choisor가 대표적.

### Override
Phase Gate 실패에도 불구하고 예외적으로 진행을 승인하는 결정.

---

## P

### Parallel Execution
여러 Feature/Domain을 동시에 처리하는 실행 방식.

### Pass Threshold
검증 통과를 위한 최소 점수 기준.

### Phase
Stage 내의 세부 작업 단위. 순차적으로 진행.

### Phase Gate
Phase 완료 시 품질 기준 충족 여부를 검증하는 관문.

### Priority Group
의존성에 따라 분류된 도메인 그룹. P0(Foundation) → P1(Hub) → P2(Core) → P3(Supporting).

---

## Q

### Quality Gate
최종 품질 승인/반려를 결정하는 Stage 5 Phase 5.

### Quality Score
검증 결과를 0-100 점으로 정량화한 점수.

---

## R

### Remediation
검증 실패 시 문제를 해결하는 수정 절차.

### Remediation Report
수정 내용과 결과를 문서화한 보고서.

### Resume
중단된 작업을 마지막 체크포인트에서 재개하는 기능.

### Root Cause Analysis
문제의 근본 원인을 분석하는 절차.

---

## S

### Screen ID
MiPlatform 화면 식별자. Feature 그룹핑의 기준. 예: PA0101010M.

### Skill
특정 작업을 위한 표준화된 지침 문서. SKILL.md 형식.

### Sonnet
Anthropic의 중급 AI 모델. 표준 Feature 분석과 코드 생성에 사용.

### Source Inventory
레거시 소스 코드에서 자동 추출한 Ground Truth 목록.

### Spec Validation
LLM을 사용하여 스펙의 정확성을 소스 코드와 비교 검증하는 프로세스.

### SQL Equivalence
레거시와 생성된 코드의 SQL이 동등한지 검증하는 핵심 항목.

### Stage
마이그레이션 워크플로우의 대분류 단계. 5개 Stage 존재.

### Structural Standardization
코드의 구조적 일관성(Naming, URL, Package, Import)을 표준화하는 Phase.

---

## T

### Task
Phase 내의 개별 작업 항목.

### Task Service
4-Layer 아키텍처의 2번째 레이어. 비즈니스 로직 담당.

### Threshold
검증 통과/실패를 결정하는 기준값.

### Traceability
모든 요소가 소스 코드까지 추적 가능한 특성.

---

## V

### Validation Framework
품질 검증을 위한 체계적인 프레임워크. 4-Layer Validation 구조.

### Value Object (VO)
데이터 전송 객체. 필드명, 타입, DB 매핑 정보 포함.

---

## W

### Weighted Score
가중치가 적용된 점수. 중요도에 따라 차등 배점.

### Workflow
Stage와 Phase로 구성된 전체 작업 흐름.

---

**Next**: [02-templates.md](02-templates.md)
