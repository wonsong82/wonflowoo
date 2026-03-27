---
name: s4-01-generation-project-scaffold
description: Use when starting code generation phase, creating initial Spring Boot project structure, or setting up Gradle multi-module build configuration (project)
---

# Project Scaffold

> **Skill ID**: S4-01
> **Skill Type**: Generation (Singleton - 1회성)
> **Stage**: 4 - Generation
> **Phase**: 4.1 - Project Scaffold

## 1. Overview

### 1.1 Purpose

승인된 아키텍처 설계와 생성 템플릿을 기반으로 **Spring Boot 3.2 프로젝트 초기 구조**를 생성합니다. Wave 1에서 1회만 실행되며, 이후 Wave에서는 기존 프로젝트에 추가합니다.

**생성 대상:**
- Gradle 빌드 설정 (build.gradle.kts)
- 공통 모듈 구조 (common package)
- Configuration 파일 (application.yml)
- 기본 인프라 코드 (ApiResponse, Exception handling)

**사용 용도:**
- S4-02 Mini-Pilot 실행 전 프로젝트 기반 제공
- S4-03/04 대량 코드 생성의 target 프로젝트

### 1.2 Scope

**In Scope:**
- Gradle Kotlin DSL 빌드 설정
- Spring Boot 3.2 + Java 17 설정
- MyBatis + HikariCP + Oracle 설정
- Common 모듈 (ApiResponse, GlobalExceptionHandler)
- Swagger/OpenAPI 설정

**Out of Scope:**
- 도메인별 Feature 코드 (→ S4-02, S4-03)
- 테스트 코드 (→ S4-04)
- 도메인별 패키지 구조 (→ S4-02에서 생성)

### 1.3 Core Principles

| Principle | Description | Rationale |
|-----------|-------------|-----------|
| **Reference Aligned** | next-hallain-sample 패턴 준수 | 검증된 프로젝트 구조 |
| **Convention over Configuration** | Spring Boot 규약 준수 | 유지보수성 |
| **Build First** | 빌드 가능한 상태 보장 | 즉시 검증 가능 |
| **Minimal Viable** | 필수 요소만 포함 | 복잡도 최소화 |

### 1.4 QUERY-FIRST 원칙

> **SQL 보존 100% 필수** (REHOSTING/REPLATFORMING 범위)
> - 참조: migration-strategy.md Section 2.3
> - S4-01은 프로젝트 구조를 생성하며, **MyBatis Mapper 리소스 구조가 SQL 보존의 기반**

### 1.5 Relationships

**Predecessors:**
| Skill | Reason |
|-------|--------|
| `s3-04-preparation-architecture-design` | 승인된 아키텍처 설계 필요 |
| `s3-05-preparation-generation-spec` | 생성 템플릿 및 규칙 필요 |

**Successors:**
| Skill | Reason |
|-------|--------|
| `s4-02-generation-mini-pilot` | Scaffold 프로젝트 위에 파일럿 생성 |
| `s4-03-generation-domain-batch` | Scaffold 프로젝트 위에 배치 생성 |

---

## 2. Prerequisites

### 2.1 Skill Dependencies

```yaml
skill_dependencies:
  - skill_id: "S3-04"
    skill_name: "s3-04-preparation-architecture-design"
    status: "APPROVED"
    artifacts:
      - "architecture-design.yaml"

  - skill_id: "S3-05"
    skill_name: "s3-05-preparation-generation-spec"
    status: "completed"
    artifacts:
      - "generation-templates/"
      - "generation-rules.yaml"
```

### 2.2 Input Requirements

| Name | Type | Location | Format | Required |
|------|------|----------|--------|----------|
| architecture_design | file | `work/specs/stage3-outputs/phase4/architecture-design.yaml` | YAML | Yes |
| generation_templates | directory | `work/specs/stage3-outputs/phase5/generation-templates/` | YAML | Yes |
| reference_project | directory | `next-hallain-sample/` | Java/Gradle | Yes |

### 2.3 Environment

**Tools:**
| Tool | Version | Purpose |
|------|---------|---------|
| Write | - | 파일 생성 |
| Read | - | Reference 프로젝트 분석 |
| Bash | - | Gradle 빌드 검증 |

**Access:**
- `next-hallain/` 디렉토리 쓰기 권한
- Reference 프로젝트 읽기 권한

---

## 3. Methodology

### 3.1 Execution Model

```yaml
execution_model:
  type: singleton
  execution: once_per_project  # Wave 1에서만 실행
  parallelization:
    enabled: false
    max_sessions: 1
  lifecycle:
    timeout_minutes: 120
    retry_on_failure: 2
```

### 3.2 Generation Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Analyze    │────▶│    Create    │────▶│    Setup     │────▶│   Validate   │
│  Reference   │     │    Gradle    │     │   Packages   │     │    Build     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 3.3 Process Steps

#### Step 1: Analyze Reference Project

**Description:** next-hallain-sample 프로젝트 구조 분석

**Sub-steps:**
1. build.gradle.kts 의존성 목록 확인
2. application.yml 설정 구조 확인
3. common 패키지 구조 확인
4. 설정 클래스 목록 확인

**Validation:** Reference 프로젝트 구조 파악 완료

**Outputs:**
- Reference 패턴 목록

---

#### Step 2: Create Gradle Build Configuration

**Description:** build.gradle.kts 및 settings.gradle.kts 생성

**Sub-steps:**
1. 프로젝트 루트 디렉토리 생성 (`next-hallain/`)
2. settings.gradle.kts 생성
3. build.gradle.kts 생성 (의존성 포함)
4. gradle/wrapper 설정

**Key Dependencies:**
```kotlin
dependencies {
    // Spring Boot
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-validation")

    // MyBatis
    implementation("org.mybatis.spring.boot:mybatis-spring-boot-starter:3.0.3")

    // Database
    implementation("com.oracle.database.jdbc:ojdbc11:23.3.0.23.09")
    implementation("com.zaxxer:HikariCP:5.1.0")

    // Swagger
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0")

    // Lombok
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")

    // Test
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.mybatis.spring.boot:mybatis-spring-boot-starter-test:3.0.3")
}
```

**Validation:** gradle 파일 생성 완료

---

#### Step 3: Create Configuration Files

**Description:** application.yml 및 설정 파일 생성

**Sub-steps:**
1. `src/main/resources/application.yml` 생성
2. `src/main/resources/application-local.yml` 생성
3. `src/main/resources/application-dev.yml` 생성
4. MyBatis config 생성

**application.yml Structure:**
```yaml
spring:
  application:
    name: hallain-backend
  profiles:
    active: local

server:
  port: 8080
  servlet:
    context-path: /api

mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.hallain
  configuration:
    map-underscore-to-camel-case: true
    default-fetch-size: 100

springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
```

**Validation:** 설정 파일 생성 완료

---

#### Step 4: Create Common Module

**Description:** 공통 모듈 패키지 및 클래스 생성

**Sub-steps:**
1. Package 구조 생성
2. ApiResponse 클래스 생성
3. GlobalExceptionHandler 생성
4. BaseEntity 클래스 생성
5. RowStatus enum 생성

**Package Structure:**
```
com.hallain/
├── HallainApplication.java
└── common/
    ├── config/
    │   ├── WebMvcConfig.java
    │   └── MyBatisConfig.java
    ├── response/
    │   ├── ApiResponse.java
    │   └── PageResponse.java
    ├── exception/
    │   ├── GlobalExceptionHandler.java
    │   ├── BusinessException.java
    │   └── ErrorCode.java
    └── entity/
        ├── BaseEntity.java
        └── RowStatus.java
```

**Validation:** Common 모듈 컴파일 가능

---

#### Step 5: Validate Build

**Description:** Gradle 빌드 검증

**Sub-steps:**
1. `./gradlew build --dry-run` 실행
2. 빌드 성공 확인
3. 컴파일 오류 없음 확인

**Validation:** 빌드 성공

---

#### Step 6: Schema Validation

**Description:** 생성된 프로젝트 구조가 표준 스키마를 준수하는지 검증

**Schema Reference:** `output.schema.yaml` (이 skill 디렉토리 내)

**Validation Rules:**

| Rule ID | Target | Check | On Fail | Blocking |
|---------|--------|-------|---------|----------|
| V001 | gradle files | build.gradle.kts, settings.gradle.kts 존재 | ERROR | Yes |
| V002 | main class | HallainApplication.java 존재 | ERROR | Yes |
| V003 | config files | application.yml 존재 | ERROR | Yes |
| V004 | common module | ApiResponse.java, GlobalExceptionHandler.java 존재 | ERROR | Yes |
| V005 | build.gradle.kts | Spring Boot 플러그인 포함 | ERROR | Yes |
| V006 | build.gradle.kts | Java 17 설정 | ERROR | Yes |
| V007 | build.gradle.kts | MyBatis 의존성 포함 | ERROR | Yes |
| V008 | build.gradle.kts | Oracle Driver 의존성 포함 | ERROR | Yes |
| V009 | gradle | ./gradlew build --dry-run 성공 | ERROR | Yes |
| V010 | gradle | ./gradlew compileJava 성공 | ERROR | Yes |

**Sub-steps:**
1. 필수 파일 존재 검증
2. 디렉토리 구조 검증
3. build.gradle.kts 내용 검증
4. Gradle 빌드 실행 검증

**On Validation Failure:**
- blocking=true 오류: Gate 실패, 구조 재생성 필요
- blocking=false 오류: WARNING 로그, 계속 진행

---

### 3.4 Decision Points

| ID | Condition | True Action | False Action |
|----|-----------|-------------|--------------|
| DP-1 | Wave > 1 | Skip (기존 프로젝트 사용) | 신규 생성 |
| DP-2 | next-hallain/ 존재 | 백업 후 진행 | 신규 생성 |
| DP-3 | Gradle 설치됨 | 로컬 빌드 | Wrapper만 생성 |

---

## 4. Outputs

### 4.1 Directory Structure

```yaml
outputs:
  directory:
    base: "next-hallain/"

  structure:
    - "build.gradle.kts"
    - "settings.gradle.kts"
    - "gradle/"
    - "src/main/java/com/hallain/"
    - "src/main/resources/"
    - "src/test/java/com/hallain/"
```

### 4.2 Output Files

| File | Type | Purpose | Required |
|------|------|---------|----------|
| build.gradle.kts | Kotlin | Gradle 빌드 설정 | Yes |
| settings.gradle.kts | Kotlin | 프로젝트 설정 | Yes |
| HallainApplication.java | Java | Spring Boot 진입점 | Yes |
| application.yml | YAML | 애플리케이션 설정 | Yes |
| ApiResponse.java | Java | 공통 응답 래퍼 | Yes |
| GlobalExceptionHandler.java | Java | 전역 예외 처리 | Yes |

### 4.3 File Header

```java
/**
 * Generated by: s4-01-generation-project-scaffold
 * Stage: 4 - Generation
 * Phase: 4.1 - Project Scaffold
 * Generated: ${TIMESTAMP}
 * Model: ${MODEL_NAME}
 */
```

### 4.4 Key Generated Files

#### build.gradle.kts

```kotlin
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    java
    id("org.springframework.boot") version "3.2.1"
    id("io.spring.dependency-management") version "1.1.4"
}

group = "com.hallain"
version = "1.0.0-SNAPSHOT"

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    // Spring Boot
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-validation")

    // MyBatis
    implementation("org.mybatis.spring.boot:mybatis-spring-boot-starter:3.0.3")

    // Database
    implementation("com.oracle.database.jdbc:ojdbc11:23.3.0.23.09")

    // Swagger
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0")

    // Lombok
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")

    // Test
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.withType<Test> {
    useJUnitPlatform()
}
```

#### ApiResponse.java

```java
package com.hallain.common.response;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class ApiResponse<T> {
    private boolean success;
    private T data;
    private String message;
    private String errorCode;

    private ApiResponse(boolean success, T data, String message, String errorCode) {
        this.success = success;
        this.data = data;
        this.message = message;
        this.errorCode = errorCode;
    }

    public static <T> ApiResponse<T> success() {
        return new ApiResponse<>(true, null, null, null);
    }

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, data, null, null);
    }

    public static <T> ApiResponse<T> error(String message, String errorCode) {
        return new ApiResponse<>(false, null, message, errorCode);
    }
}
```

---

## 5. Quality Checks

### 5.1 Automated Checks

| Check | Type | Criteria | On Fail | Blocking |
|-------|------|----------|---------|----------|
| gradle_build_succeeds | structural | `./gradlew build --dry-run` 성공 | ERROR | Yes |
| common_module_exists | structural | `com.hallain.common` 패키지 존재 | ERROR | Yes |
| config_files_present | structural | `application.yml` 존재 | ERROR | Yes |
| main_class_exists | structural | `HallainApplication.java` 존재 | ERROR | Yes |

### 5.2 Gate Criteria

```yaml
gate_criteria:
  id: "G4.1"
  name: "Scaffold Gate"
  threshold: 70
  metrics:
    - metric: "gradle_build_succeeds"
      weight: 0.4
      target: "true"
      command: "cd backend && ./gradlew build --dry-run"
    - metric: "common_module_exists"
      weight: 0.3
      target: "true"
      check: "com.hallain.common package created"
    - metric: "config_files_present"
      weight: 0.3
      target: "true"
      check: "application.yml exists"
  on_pass:
    auto_commit: true
    message: "feat(S4-P4.1): Project scaffold created"
```

---

## 6. Error Handling

### 6.1 Known Issues

| Issue | Symptom | Cause | Resolution | Retry |
|-------|---------|-------|------------|-------|
| Gradle not found | 빌드 명령 실패 | Gradle 미설치 | Wrapper 사용 | Yes |
| Java version mismatch | 컴파일 오류 | Java < 17 | JAVA_HOME 설정 | No |
| Directory exists | 덮어쓰기 충돌 | 기존 프로젝트 | 백업 후 진행 | Yes |

### 6.2 Escalation

| Condition | Severity | Action | Notify |
|-----------|----------|--------|--------|
| Build failure | critical | 로그 분석 후 수정 | Developer |
| Config error | major | 설정 검토 | Developer |

### 6.3 Recovery

| Scenario | Procedure | Rollback Level |
|----------|-----------|----------------|
| 빌드 실패 | 오류 수정 후 재시도 | Phase |
| 구조 오류 | next-hallain/ 삭제 후 재생성 | Phase |

---

## 7. Examples

### 7.1 Sample Input

**architecture-design.yaml (excerpt):**
```yaml
architecture:
  base_package: "com.hallain"
  modules:
    - name: "common"
      purpose: "Shared utilities and base classes"
    - name: "domain"
      purpose: "Domain-specific features"
  layers:
    - controller
    - service
    - repository
    - entity
    - dto
```

### 7.2 Sample Output

**Generated Directory Structure:**
```
next-hallain/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew
├── gradlew.bat
└── src/
    ├── main/
    │   ├── java/
    │   │   └── com/
    │   │       └── hallain/
    │   │           ├── HallainApplication.java
    │   │           └── common/
    │   │               ├── config/
    │   │               ├── response/
    │   │               ├── exception/
    │   │               └── entity/
    │   └── resources/
    │       ├── application.yml
    │       ├── application-local.yml
    │       └── mapper/
    └── test/
        └── java/
            └── com/
                └── hallain/
```

### 7.3 Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| Wave 1 | 신규 프로젝트 | 전체 Scaffold 생성 |
| Wave > 1 | 기존 프로젝트 | Skip (no action) |
| next-hallain/ 존재 | 기존 디렉토리 | 백업 후 재생성 |

---

## Version History

### v1.1.0 (2026-01-08)
- Step 6: Schema Validation 추가
- s4-01-project-scaffold.schema.yaml 스키마 참조
- 10개 검증 규칙 적용 (V001-V010)

### v1.0.0 (2026-01-07)
- Initial version
- Spring Boot 3.2 + Java 17
- MyBatis 3.0 + Oracle 설정
- Common 모듈 구조
