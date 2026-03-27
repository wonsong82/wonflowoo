# Legacy Analysis Checklist

## Overview

이 문서는 Legacy 시스템 분석을 위한 체계적인 체크리스트를 제공합니다. 마이그레이션 프로젝트 시작 전 반드시 수행해야 할 평가 항목들을 정의합니다.

---

## Assessment Critical Path (Human Checklist)

> **이 10개 항목은 반드시 Human이 직접 확인해야 합니다.**

| # | 항목 | 미확인 시 결과 |
|---|------|---------------|
| 1 | 총 Controller/Endpoint 수 파악 | Stage 2에서 누락 발견, 전체 재작업 |
| 2 | 도메인 경계 식별 | Wave 분할 실패, Context 초과 |
| 3 | SP(Stored Procedure) 목록 완성 | Stage 4 코드 생성 실패 |
| 4 | Dynamic SQL 패턴 분류 | iBatis→MyBatis 변환 오류 |
| 5 | 외부 시스템 연동 목록 | 통합 테스트 누락 |
| 6 | 커스텀 프레임워크 식별 | 예상치 못한 의존성 문제 |
| 7 | 인증/인가 패턴 확인 | Security 마이그레이션 실패 |
| 8 | 트랜잭션 경계 확인 | 데이터 정합성 문제 |
| 9 | 배치 처리 로직 식별 | 스케줄러 마이그레이션 누락 |
| 10 | 코드 복잡도 측정 | 잘못된 공수 산정 |

---

## 1. Codebase Profiling

### 1.1 Basic Statistics

**Task ID**: `ASSESS-001`

**WHY 필요한가?**
> 코드 규모가 파악되지 않으면 적절한 Wave 분할이 불가능합니다.
> 8,000+ 파일 프로젝트를 단일 Wave로 처리하면 Context 초과로 실패합니다.

**이 단계를 놓치면?**
> - Stage 4 코드 생성 시 Context 초과 오류 빈발
> - Wave 분할 기준 없이 임의 진행 → 재작업 발생
> - 프로젝트 일정 산정 불가

```bash
# 실행 명령어 예시
cloc --yaml --out=codebase-stats.yaml <legacy-source-path>
find <legacy-source-path> -name "*.java" | wc -l
find <legacy-source-path> -type d | wc -l
```

**수집 항목**:

| 항목 | 측정 방법 | 예시 값 |
|------|----------|---------|
| 총 파일 수 | `find -name "*.java" \| wc -l` | 8,377 |
| 총 코드 라인 | `cloc` | 1,200,000 |
| 디렉토리 수 | `find -type d \| wc -l` | 450 |
| 패키지 수 | 고유 패키지 경로 | 120 |

**체크리스트**:

- [ ] 총 소스 파일 수 확인
- [ ] 언어별 파일 분포 확인 (Java, XML, SQL 등)
- [ ] 코드 라인 수 (LOC) 측정
- [ ] 빈 파일 / 주석 비율 확인
- [ ] 빌드 스크립트 위치 확인 (Maven, Gradle, Ant)

### 1.2 Architecture Pattern Identification

**Task ID**: `ASSESS-002`

**WHY 필요한가?**
> 아키텍처 패턴에 따라 마이그레이션 전략이 완전히 달라집니다.
> Layered vs SOA vs Custom Framework에 따라 Skill 선택과 변환 규칙이 다릅니다.

**이 단계를 놓치면?**
> - 커스텀 프레임워크 미식별 → Stage 3 아키텍처 설계 오류
> - 레이어 구조 오해 → 잘못된 패키지 매핑

**식별 대상 패턴**:

```yaml
architecture_patterns:
  layered:
    indicators:
      - "controller/, service/, dao/, vo/ 디렉토리 구조"
      - "패키지명에 controller, service, repository 포함"
    example: "Spring MVC 3-tier"

  mvc:
    indicators:
      - "Controller 클래스 존재"
      - "View 템플릿 (JSP, Thymeleaf) 존재"
    example: "Spring MVC, Struts"

  soa:
    indicators:
      - "WSDL 파일 존재"
      - "WebService 어노테이션"
    example: "JAX-WS, CXF"

  custom_framework:
    indicators:
      - "자체 프레임워크 패키지 (com.company.framework)"
      - "비표준 base 클래스"
    example: "benitware.framework.*"
```

**체크리스트**:

- [ ] 주요 디렉토리 구조 분석
- [ ] 레이어 수 및 명칭 확인
- [ ] 프레임워크 버전 확인
- [ ] 커스텀 프레임워크 존재 여부
- [ ] 외부 라이브러리 목록 (pom.xml, build.gradle)

### 1.3 Framework & Library Inventory

**Task ID**: `ASSESS-003`

**분류 기준**:

| 카테고리 | 항목 | 마이그레이션 영향 |
|----------|------|-----------------|
| **Web Framework** | Spring MVC, Struts | 높음 |
| **Persistence** | MyBatis, Hibernate, JPA | 높음 |
| **Database** | Oracle, MySQL, PostgreSQL | 중간 |
| **Security** | Spring Security, Custom | 높음 |
| **Logging** | Log4j, SLF4J | 낮음 |
| **Utility** | Apache Commons, Guava | 낮음 |
| **Custom** | 자체 프레임워크 | 매우 높음 |

**체크리스트**:

- [ ] 빌드 파일에서 의존성 목록 추출
- [ ] 버전 정보 확인
- [ ] Deprecated 라이브러리 식별
- [ ] 보안 취약 라이브러리 확인
- [ ] 라이선스 호환성 검토

---

## 2. Domain Decomposition

### 2.1 Domain Boundary Identification

**Task ID**: `ASSESS-004`

**분석 방법**:

```python
# 도메인 식별 알고리즘 (의사 코드)
def identify_domains(source_path):
    # 1. 패키지 구조 분석
    packages = extract_packages(source_path)

    # 2. 도메인 후보 추출 (2-3 레벨 패키지)
    domain_candidates = []
    for pkg in packages:
        levels = pkg.split('.')
        if len(levels) >= 3:
            domain = levels[2]  # com.company.{domain}
            domain_candidates.append(domain)

    # 3. 도메인별 파일 수 집계
    domain_stats = count_files_per_domain(domain_candidates)

    # 4. 유의미한 도메인 필터링
    domains = [d for d in domain_stats if d.file_count > threshold]

    return domains
```

**체크리스트**:

- [ ] 패키지 구조에서 도메인 후보 추출
- [ ] 도메인별 파일 수 집계
- [ ] 도메인 경계 명확성 검토
- [ ] Cross-cutting concerns 식별 (common, util, framework)
- [ ] 도메인 네이밍 규칙 파악

### 2.2 Inter-Domain Dependency Analysis

**Task ID**: `ASSESS-005`

**분석 매트릭스**:

```
            | Domain A | Domain B | Domain C | Common |
------------|----------|----------|----------|--------|
Domain A    |    -     |    5     |    0     |   12   |
Domain B    |    3     |    -     |    8     |   15   |
Domain C    |    0     |    2     |    -     |   10   |
Common      |    0     |    0     |    0     |    -   |
```

**분석 명령어**:

```bash
# Import 의존성 분석 (예시)
grep -r "import com.company.domainA" --include="*.java" domainB/ | wc -l
```

**체크리스트**:

- [ ] 도메인 간 import 의존성 측정
- [ ] 순환 의존성(Circular Dependency) 탐지
- [ ] 공통 모듈 의존도 분석
- [ ] 고립된 도메인 식별
- [ ] 의존성 방향성 검증 (하위 → 상위)

### 2.3 Priority Classification

**Task ID**: `ASSESS-006`

**우선순위 기준**:

```yaml
priority_levels:
  P0_Foundation:
    criteria:
      - "모든 도메인이 의존하는 공통 모듈"
      - "프레임워크 레벨 컴포넌트"
    examples:
      - "common, framework, security"
    order: "가장 먼저 마이그레이션"

  P1_Hub:
    criteria:
      - "많은 도메인에서 참조하는 중심 도메인"
      - "공통 데이터 관리 (코드, 사용자)"
    examples:
      - "CM (Common Master)"
    order: "P0 완료 후"

  P2_Core:
    criteria:
      - "핵심 비즈니스 로직"
      - "가장 많은 기능 포함"
    examples:
      - "PA (주요 업무), MM (자재), SC (영업)"
    order: "P1 완료 후, 순차 또는 병렬"

  P3_Supporting:
    criteria:
      - "보조 기능"
      - "다른 도메인 의존성 낮음"
    examples:
      - "BS (기초설정), QM (품질관리)"
    order: "P2 완료 후, 병렬"
```

**체크리스트**:

- [ ] 각 도메인을 P0-P3로 분류
- [ ] 분류 근거 문서화
- [ ] 도메인 간 실행 순서 정의
- [ ] 병렬 실행 가능 그룹 식별
- [ ] Critical Path 도출

---

## 3. Component Analysis

### 3.1 Controller/Endpoint Analysis

**Task ID**: `ASSESS-007`

**WHY 필요한가?**
> Controller/Endpoint 수는 전체 마이그레이션 규모를 결정합니다.
> 이 숫자가 Stage 1의 Feature Inventory와 일치해야 합니다.

**이 단계를 놓치면?**
> - Stage 2 Validation에서 대량 누락 발견 → Stage 1 전체 재작업
> - 912개 중 50개 누락 시: 5.5% 재작업 = 프로젝트 일정 1주 지연

**품질 기준**:
> - 모든 `@RequestMapping`, `@GetMapping`, `@PostMapping` 어노테이션 캡처
> - URL 패턴 중복 없음
> - HTTP 메서드 정확히 식별

**분석 스크립트**:

```bash
# @RequestMapping 패턴 추출
grep -rn "@RequestMapping" --include="*.java" <source-path> > endpoints.txt

# 엔드포인트 수 카운트
wc -l endpoints.txt
```

**수집 정보**:

| 항목 | 설명 | 예시 |
|------|------|------|
| URL 패턴 | 요청 경로 | `/api/user/*.mi` |
| HTTP 메서드 | GET, POST 등 | `POST` |
| 파라미터 | 입력 객체 | `UserVO` |
| 리턴 타입 | 출력 객체 | `List<UserVO>` |
| 컨트롤러 클래스 | 소스 위치 | `UserController.java:45` |

**체크리스트**:

- [ ] 전체 엔드포인트 수 파악
- [ ] URL 패턴 분석 (REST vs Custom)
- [ ] 컨트롤러별 엔드포인트 분포
- [ ] 중복 URL 패턴 확인
- [ ] 인증/인가 패턴 확인

### 3.2 Service Layer Analysis

**Task ID**: `ASSESS-008`

**분석 대상**:

```yaml
service_patterns:
  interface_based:
    pattern: "IXxxService / XxxServiceImpl"
    detection: "I로 시작하는 인터페이스 + Impl 접미사"

  annotation_based:
    pattern: "@Service annotation"
    detection: "grep @Service"

  transaction:
    pattern: "@Transactional"
    detection: "트랜잭션 경계 확인"
```

**체크리스트**:

- [ ] 서비스 인터페이스/구현체 수
- [ ] 서비스 네이밍 패턴 확인
- [ ] 트랜잭션 처리 방식
- [ ] 서비스 간 호출 관계
- [ ] 비즈니스 로직 복잡도 (조건문, 계산 로직)

### 3.3 Persistence Layer Analysis

**Task ID**: `ASSESS-009`

**WHY 필요한가?**
> Persistence Layer는 QUERY-FIRST 원칙의 핵심입니다.
> SQL 보존이 100% 되어야 비즈니스 로직 동등성이 보장됩니다.

**이 단계를 놓치면?**
> - Dynamic SQL 복잡도 과소평가 → Stage 4 변환 실패율 급증
> - SP 호출 누락 → 기능 동작 불가
> - 70%+ 쿼리가 동적 조건 포함 → 정적 분석만으로는 불충분

**품질 기준**:
> - 모든 Mapper XML 파일 목록화
> - Statement 유형별 분류 (SELECT/INSERT/UPDATE/DELETE)
> - Dynamic SQL 태그 (`<if>`, `<choose>`, `<foreach>`) 사용 빈도 측정

**분석 대상 (MyBatis 예시)**:

```xml
<!-- Mapper XML 분석 항목 -->
<mapper namespace="com.company.domain.mapper.UserMapper">
  <select id="selectUser">...</select>  <!-- Statement 유형 -->
  <insert id="insertUser">...</insert>
  <update id="updateUser">...</update>
  <delete id="deleteUser">...</delete>
</mapper>
```

**수집 정보**:

| 항목 | 측정 방법 | 비고 |
|------|----------|------|
| Mapper XML 수 | `find -name "*Mapper.xml"` | - |
| Statement 수 | `grep -c "<select\|<insert\|<update\|<delete"` | - |
| 동적 SQL | `<if>`, `<choose>`, `<foreach>` 사용 | 복잡도 지표 |
| Stored Procedure | `{call ...}` 패턴 | 마이그레이션 난이도 |

**체크리스트**:

- [ ] Mapper/Repository 수 파악
- [ ] SQL Statement 유형별 분포
- [ ] 동적 SQL 복잡도 평가
- [ ] Stored Procedure 사용 현황
- [ ] 다중 테이블 조인 쿼리 식별

### 3.4 Data Model Analysis

**Task ID**: `ASSESS-010`

**분석 대상**:

```java
// VO/DTO/Entity 분석
public class UserVO extends BaseVO {
    private String userId;      // 필드
    private String userName;
    private Date createDate;
    // getter/setter
}
```

**수집 정보**:

| 항목 | 설명 |
|------|------|
| VO/DTO 클래스 수 | 데이터 모델 규모 |
| 평균 필드 수 | 복잡도 지표 |
| 상속 구조 | 공통 Base 클래스 |
| 어노테이션 | Validation, Serialization |

**체크리스트**:

- [ ] VO/DTO/Entity 클래스 수
- [ ] 네이밍 패턴 확인 (XxxVO, XxxDTO)
- [ ] 상속 구조 분석 (BaseVO, VOSupport)
- [ ] 필드-컬럼 매핑 규칙
- [ ] 중복 VO 식별

---

## 4. Technical Debt Identification

### 4.1 Dead Code Detection

**Task ID**: `ASSESS-011`

**탐지 방법**:

```yaml
dead_code_indicators:
  unused_classes:
    detection: "import 참조 없는 클래스"
    tool: "IDE 분석, grep"

  unused_methods:
    detection: "호출되지 않는 public 메서드"
    tool: "IDE 분석"

  commented_code:
    detection: "주석 처리된 코드 블록"
    pattern: "// or /* 로 시작하는 다중 라인"

  deprecated:
    detection: "@Deprecated 어노테이션"
    pattern: "grep @Deprecated"
```

**체크리스트**:

- [ ] 미사용 클래스 목록 작성
- [ ] 미사용 메서드 식별
- [ ] 주석 처리된 코드 블록 수
- [ ] Deprecated 코드 현황
- [ ] Dead code 비율 (%)

### 4.2 Code Quality Issues

**Task ID**: `ASSESS-012`

**검사 항목**:

| 카테고리 | 검사 내용 | 도구 |
|----------|----------|------|
| **복잡도** | Cyclomatic Complexity | PMD, SonarQube |
| **중복** | 코드 중복 비율 | CPD, SonarQube |
| **표준** | 코딩 표준 위반 | Checkstyle |
| **버그** | 잠재적 버그 패턴 | SpotBugs, FindBugs |
| **보안** | 보안 취약점 | OWASP, Fortify |

**체크리스트**:

- [ ] 정적 분석 도구 실행
- [ ] 고위험 이슈 목록화
- [ ] 복잡도 높은 클래스/메서드 식별
- [ ] 코드 중복 핫스팟
- [ ] 보안 취약점 목록

---

## 5. External Dependencies

### 5.1 Database Dependencies

**Task ID**: `ASSESS-013`

**WHY 필요한가?**
> DB 특성(Vendor, SP, Trigger)에 따라 마이그레이션 전략이 달라집니다.
> Oracle → PostgreSQL 전환이면 SQL 방언 변환이 추가됩니다.

**이 단계를 놓치면?**
> - Stored Procedure 200개 미식별 → Stage 4 완료 후 발견 시 전체 재작업
> - Trigger 존재 미파악 → 데이터 정합성 문제
> - Sequence 전략 미확인 → ID 생성 오류

**품질 기준**:
> - SP 목록 100% 완성 (이름, 파라미터, 용도)
> - DB-specific SQL 문법 목록화 (Oracle: ROWNUM, DECODE 등)
> - Trigger/Function 존재 여부 확인

**분석 항목**:

```yaml
database_analysis:
  vendor:
    options: ["Oracle", "MySQL", "PostgreSQL", "SQL Server"]
    impact: "SQL 방언, 함수 호환성"

  features:
    stored_procedures:
      detection: "{call ...}"
      migration_effort: "높음"
    functions:
      detection: "사용자 정의 함수"
      migration_effort: "중간"
    triggers:
      detection: "DB 트리거"
      migration_effort: "높음"
    sequences:
      detection: "시퀀스 사용"
      migration_effort: "낮음"

  schema:
    tables: "테이블 수"
    views: "뷰 수"
    indexes: "인덱스 수"
```

**체크리스트**:

- [ ] 데이터베이스 벤더 및 버전
- [ ] Stored Procedure 목록
- [ ] User-defined Function 목록
- [ ] 트리거 존재 여부
- [ ] DB-specific SQL 문법 사용 현황

### 5.2 External System Integration

**Task ID**: `ASSESS-014`

**통합 유형**:

| 유형 | 예시 | 마이그레이션 고려사항 |
|------|------|---------------------|
| REST API | 외부 서비스 호출 | 엔드포인트 변경 영향 |
| SOAP/WSDL | 레거시 웹서비스 | 프로토콜 전환 필요성 |
| Message Queue | MQ, Kafka | 메시지 포맷 호환성 |
| File Transfer | FTP, SFTP | 파일 형식 유지 |
| Batch | Quartz, Spring Batch | 스케줄 및 로직 보존 |

**체크리스트**:

- [ ] 외부 시스템 연동 목록
- [ ] 연동 프로토콜 확인
- [ ] 인터페이스 명세서 수집
- [ ] 연동 테스트 환경 확인
- [ ] 연동 장애 시 대응 방안

---

## 6. Extended Analysis (Phase 6)

### 6.1 Test Coverage Analysis

**Task ID**: `ASSESS-015`

**분석 명령어**:

```bash
# 테스트 파일 수
find <legacy-source-path> -name "*Test.java" | wc -l
find <legacy-source-path> -name "*Spec.java" | wc -l

# JUnit 사용 현황
grep -r "import org.junit" --include="*.java" <legacy-source-path> | wc -l
grep -r "import org.mockito" --include="*.java" <legacy-source-path> | wc -l
```

**수집 항목**:

| 항목 | 측정 방법 | 비고 |
|------|----------|------|
| 단위 테스트 파일 | `*Test.java`, `*Spec.java` | JUnit, TestNG |
| 통합 테스트 파일 | `*IT.java`, `*IntegrationTest.java` | - |
| 테스트 프레임워크 | import 문 분석 | JUnit 4/5, Mockito |
| 테스트 실행 설정 | Maven Surefire/Failsafe | pom.xml 확인 |

**체크리스트**:

- [ ] 단위 테스트 파일 수 파악
- [ ] 통합 테스트 파일 수 파악
- [ ] 테스트 프레임워크 버전 확인
- [ ] 테스트 실행 설정 확인 (Maven/Gradle)
- [ ] 테스트 커버리지 도구 존재 여부 (JaCoCo 등)

### 6.2 Build & Deployment Analysis

**Task ID**: `ASSESS-016`

**분석 명령어**:

```bash
# 빌드 설정 파일 탐지
find <legacy-source-path> -name "pom.xml" -o -name "build.xml" -o -name "build.gradle"

# Maven 플러그인 현황
grep -A 5 "<plugin>" pom.xml

# Ant 타겟 확인
grep "<target" build.xml
```

**수집 항목**:

| 항목 | 설명 | 마이그레이션 영향 |
|------|------|-----------------|
| 빌드 도구 | Maven, Ant, Gradle | 전환 복잡도 |
| Java 버전 | source/target 설정 | 호환성 |
| 패키징 유형 | WAR, EAR, JAR | 배포 방식 |
| CI/CD 설정 | Jenkins, GitLab CI | 파이프라인 재구성 |
| WAS 환경 | Tomcat, WebLogic, JBoss | 전환 가능성 |

**체크리스트**:

- [ ] 빌드 도구 종류 및 버전
- [ ] 빌드 스크립트 구조 분석
- [ ] CI/CD 파이프라인 현황
- [ ] 배포 환경 (WAS 종류, 버전)
- [ ] 환경별 설정 관리 방식 (dev/staging/prod)

### 6.3 Performance Bottleneck Analysis

**Task ID**: `ASSESS-017`

**분석 명령어**:

```bash
# N+1 쿼리 패턴 탐지 (루프 내 쿼리 호출)
grep -rn "for.*{" --include="*.java" -A 10 | grep -E "queryFor|selectList|select"

# 캐싱 현황
grep -r "@Cacheable\|@Cache\|CacheManager" --include="*.java" <legacy-source-path>

# 비동기 처리
grep -r "@Async\|ExecutorService\|ThreadPool" --include="*.java" <legacy-source-path>

# 대용량 데이터 처리
grep -r "LIMIT\|OFFSET\|ROWNUM\|fetchSize" --include="*.java" --include="*.xml" <legacy-source-path>
```

**분석 항목**:

| 항목 | 설명 | 영향도 |
|------|------|--------|
| N+1 쿼리 | 루프 내 반복 쿼리 | HIGH |
| 대용량 처리 | 페이징, 배치 처리 | MEDIUM |
| 캐싱 | 캐시 적용 현황 | MEDIUM |
| 비동기 처리 | Thread Pool 활용 | MEDIUM |
| 느린 쿼리 | 복잡한 JOIN, 서브쿼리 | HIGH |

**체크리스트**:

- [ ] N+1 쿼리 패턴 탐지
- [ ] 대용량 데이터 처리 로직 확인
- [ ] 캐싱 현황 (Redis, Ehcache 등)
- [ ] 비동기 처리 패턴 확인
- [ ] 복잡한 SQL 쿼리 목록

### 6.4 Documentation Status

**Task ID**: `ASSESS-018`

**분석 명령어**:

```bash
# Markdown 문서
find <legacy-source-path> -name "*.md" | wc -l

# JavaDoc 현황
grep -r "/\*\*" --include="*.java" <legacy-source-path> | wc -l

# API 문서 (Swagger)
grep -r "@Api\|@ApiOperation\|springdoc\|swagger" --include="*.java" --include="*.xml" <legacy-source-path>
```

**수집 항목**:

| 항목 | 설명 | 현황 |
|------|------|------|
| README | 프로젝트 설명서 | 있음/없음 |
| JavaDoc | 코드 문서화 | 비율 (%) |
| API 문서 | Swagger/OpenAPI | 있음/없음 |
| Wiki | 업무 문서 | 있음/없음 |
| ERD | DB 설계 문서 | 있음/없음 |

**체크리스트**:

- [ ] README 파일 존재 여부
- [ ] JavaDoc 커버리지 비율
- [ ] API 문서화 현황 (Swagger 등)
- [ ] 업무 Wiki/Confluence 현황
- [ ] ERD/설계 문서 존재 여부

### 6.5 Operations & Monitoring

**Task ID**: `ASSESS-019`

**분석 명령어**:

```bash
# 로깅 설정 파일
find <legacy-source-path> -name "log4j*.xml" -o -name "log4j*.properties" -o -name "logback*.xml"

# Health Check
grep -r "HealthCheck\|actuator\|/health" --include="*.java" --include="*.xml" <legacy-source-path>

# 모니터링 (APM)
grep -r "newrelic\|datadog\|prometheus\|micrometer" --include="*.java" --include="*.xml" <legacy-source-path>
```

**수집 항목**:

| 항목 | 설명 | 현황 |
|------|------|------|
| 로깅 프레임워크 | Log4j, Logback | 버전 |
| 로그 레벨 설정 | DEBUG, INFO, ERROR | 환경별 |
| Health Check | /health 엔드포인트 | 있음/없음 |
| APM | NewRelic, Datadog | 있음/없음 |
| 알림 설정 | Email, Slack | 있음/없음 |

**체크리스트**:

- [ ] 로깅 프레임워크 및 설정
- [ ] 로그 레벨 정책
- [ ] Health Check 엔드포인트 존재 여부
- [ ] APM/모니터링 도구 현황
- [ ] 장애 알림 체계

### 6.6 Migration Cost Estimation

**Task ID**: `ASSESS-020`

**산정 기준**:

```yaml
cost_estimation:
  factors:
    - name: "도메인 규모"
      metric: "파일 수, LOC"
      weight: 0.3

    - name: "복잡도"
      metric: "SP, 동적SQL, 외부연동"
      weight: 0.3

    - name: "기술부채"
      metric: "보안취약점, 레거시 의존성"
      weight: 0.2

    - name: "테스트 현황"
      metric: "기존 테스트 커버리지"
      weight: 0.2

  effort_formula:
    base_hours_per_endpoint: 2-4
    complexity_multiplier:
      LOW: 1.0
      MEDIUM: 1.5
      HIGH: 2.5
    buffer_percentage: 20-30%
```

**수집 항목**:

| 항목 | 산정 방법 | 비고 |
|------|----------|------|
| 도메인별 예상 인시 | 엔드포인트 × 복잡도 계수 | - |
| 리스크 버퍼 | 기본 20-30% | 불확실성 반영 |
| 총 예상 인시 | 합계 + 버퍼 | - |
| 예상 기간 | 인시 / 팀원수 | FTE 기준 |

**체크리스트**:

- [ ] 도메인별 예상 인시 산정
- [ ] 복잡도별 가중치 적용
- [ ] 리스크 버퍼 산정
- [ ] 총 비용 추정 (인력, 인프라)
- [ ] 마이그레이션 일정 산출

---

## 7. Assessment Output Template

### 7.1 Summary Report

```yaml
# legacy-assessment-report.yaml

project:
  name: "{PROJECT_NAME}"
  assessment_date: "YYYY-MM-DD"
  assessor: "{ASSESSOR_NAME}"

codebase_summary:
  total_files: 0
  total_loc: 0
  languages:
    java: 0
    xml: 0
    sql: 0

architecture:
  pattern: "{PATTERN}"
  layers: []
  frameworks: []

domains:
  count: 0
  list:
    - name: "{DOMAIN}"
      priority: "P{N}"
      files: 0
      endpoints: 0

complexity:
  overall: "HIGH|MEDIUM|LOW"
  stored_procedures: 0
  dynamic_sql_ratio: 0%

technical_debt:
  dead_code_ratio: 0%
  high_complexity_classes: 0
  security_issues: 0

external_dependencies:
  databases: []
  external_systems: []

migration_recommendation:
  strategy: "REPLATFORMING|REFACTORING|REWRITING"
  estimated_effort: "{EFFORT}"
  risk_level: "HIGH|MEDIUM|LOW"
  priority_order: []
```

---

## Next Steps

Assessment 완료 후:

1. **Complexity Estimation** → [02-complexity-estimation.md](02-complexity-estimation.md)
2. **Feasibility Matrix** → [03-feasibility-matrix.md](03-feasibility-matrix.md)
3. **Workflow Design** → [../02-WORKFLOW-DESIGN/](../02-WORKFLOW-DESIGN/)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-15
